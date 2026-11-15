/**
 * Time-sensitive facts (src/data/registry/facts.json): valid, versions never overlap, the date
 * lookup picks the right version, and nothing is past its review date. Freshness is checked against
 * an injected date so CI is deterministic; the real-date check runs only in the scheduled job
 * (CHECK_FRESHNESS=1), because 06-critique §1 item 21 says stale facts must not block erratum deploys.
 */
import { describe, expect, it } from 'vitest';
import { FactDef } from '../../src/data/schema';
import { buildRegistry, factValueOn, FACTS, getFact, overdueReviews, registryProblems, validFromIsLowerBound, type RegistryFiles } from '../../src/data/registry';

const AS_OF = '2026-11-15';
const EXAM_DAY = '2027-01-22';

const fact = (id: string) => {
  const f = getFact(id);
  if (!f) throw new Error(`fact ${id} missing`);
  return f;
};
/** the numeric value on a date, or undefined (for facts stored as { n, unit }) */
const n = (id: string, date: string) => {
  const v = factValueOn(fact(id), date)?.value;
  return v && 'n' in v ? v.n : undefined;
};

/** Taiwan's calendar date today, so the freshness job agrees with the site's audience. */
function taipeiToday(): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}

describe('facts.json', () => {
  it('has every seeded fact', () => {
    expect([...FACTS.keys()].sort()).toEqual(
      [
        'civics.age-of-majority',
        'civics.referendum-age',
        'civics.voting-age',
        'civics.min-wage-monthly',
        'civics.min-wage-hourly',
        'exam.gsat-116-dates',
        'exam.multi-select-scoring',
        'exam.level-scale',
        'exam.five-standards',
        'exam.calculators',
      ].sort(),
    );
  });

  it('validates every entry against the schema', () => {
    for (const f of FACTS.values()) expect(FactDef.safeParse(f).success).toBe(true);
  });

  it('never lets two versions of one fact overlap', () => {
    for (const f of FACTS.values()) {
      const vs = [...f.versions].sort((a, b) => a.validFrom.localeCompare(b.validFrom));
      vs.forEach((v, i) => {
        if (v.validTo) expect(v.validTo > v.validFrom).toBe(true);
        const next = vs[i + 1];
        if (next) expect({ id: f.id, endsBeforeNext: v.validTo !== undefined && v.validTo <= next.validFrom }).toEqual({ id: f.id, endsBeforeNext: true });
      });
    }
  });

  it('records the research date as asOf on every fact', () => {
    for (const f of FACTS.values()) expect([f.id, f.asOf]).toEqual([f.id, AS_OF]);
  });

  it('sets the review dates by family: exam rules after the sitting, law before the 117 brochure, wages after the yearly review', () => {
    for (const f of FACTS.values()) {
      const expected = f.id.startsWith('exam.') ? '2027-01-25' : f.id.startsWith('civics.min-wage') ? '2027-10-31' : '2027-08-01';
      expect([f.id, f.reviewBy]).toEqual([f.id, expected]);
    }
  });
});

describe('factValueOn', () => {
  it('keeps the three ages apart on exam day', () => {
    expect(n('civics.age-of-majority', EXAM_DAY)).toBe(18);
    expect(n('civics.referendum-age', EXAM_DAY)).toBe(18);
    expect(n('civics.voting-age', EXAM_DAY)).toBe(20);
  });

  it('switches the minimum wage on 2027-01-01 (validTo is exclusive)', () => {
    expect(n('civics.min-wage-monthly', '2026-12-31')).toBe(29500);
    expect(n('civics.min-wage-monthly', '2027-01-01')).toBe(30900);
    expect(n('civics.min-wage-hourly', '2026-12-31')).toBe(196);
    expect(n('civics.min-wage-hourly', '2027-01-01')).toBe(205);
    expect(n('civics.min-wage-monthly', EXAM_DAY)).toBe(30900);
  });

  it('returns undefined before the first recorded version', () => {
    expect(factValueOn(fact('civics.age-of-majority'), '2022-12-31')).toBeUndefined();
    expect(factValueOn(fact('civics.min-wage-monthly'), '2025-12-31')).toBeUndefined();
    expect(n('civics.age-of-majority', '2023-01-01')).toBe(18);
  });

  it('marks the validFrom dates the research only bounds from below', () => {
    const lowerBound = [...FACTS.values()].filter((f) => f.versions.some(validFromIsLowerBound)).map((f) => f.id);
    expect(lowerBound.sort()).toEqual([
      'civics.referendum-age',
      'civics.voting-age',
      'exam.calculators',
      'exam.five-standards',
      'exam.gsat-116-dates',
      'exam.level-scale',
      'exam.multi-select-scoring',
    ]);
    // the age of majority and the wage dates are exact (民法 沿革: 自112-01-01施行; wage years start 1 January)
    expect(fact('civics.age-of-majority').versions.some(validFromIsLowerBound)).toBe(false);
  });

  it('returns the version object with its basis', () => {
    const v = factValueOn(fact('civics.min-wage-monthly'), EXAM_DAY);
    expect(v?.validFrom).toBe('2027-01-01');
    expect(v?.basis).toMatch(/2026-09-24/);
  });

  it('rejects anything but a YYYY-MM-DD date', () => {
    expect(() => factValueOn(fact('civics.voting-age'), '2027-1-22')).toThrow(/YYYY-MM-DD/);
    expect(() => factValueOn(fact('civics.voting-age'), '2027-01-22T09:20:00+08:00')).toThrow(/YYYY-MM-DD/);
  });

  it('states the multi-select rule as the brochure does', () => {
    const v = factValueOn(fact('exam.multi-select-scoring'), EXAM_DAY)?.value;
    expect(v && 'zh-tw' in v ? v['zh-tw'] : '').toContain('(n−2k)/n');
    expect(v && 'en' in v ? v.en : '').toMatch(/at least one of them correct/);
  });
});

describe('freshness (injected date)', () => {
  it('has nothing overdue on the research date', () => {
    expect(overdueReviews(AS_OF)).toEqual([]);
  });

  it('flags the exam facts the day after their review date, and not before', () => {
    expect(overdueReviews('2027-01-25').filter((d) => d.kind === 'fact')).toEqual([]);
    const due = overdueReviews('2027-01-26').filter((d) => d.kind === 'fact').map((d) => d.id);
    expect(due.sort()).toEqual(['exam.calculators', 'exam.five-standards', 'exam.gsat-116-dates', 'exam.level-scale', 'exam.multi-select-scoring']);
  });

  it('flags the law facts after 2027-08-01 and the wage facts after 2027-10-31', () => {
    const facts = (d: string) => overdueReviews(d).filter((x) => x.kind === 'fact').map((x) => x.id);
    expect(facts('2027-08-02')).toEqual(expect.arrayContaining(['civics.age-of-majority', 'civics.referendum-age', 'civics.voting-age']));
    expect(facts('2027-08-02')).not.toContain('civics.min-wage-monthly');
    expect(facts('2027-11-01')).toEqual(expect.arrayContaining(['civics.min-wage-monthly', 'civics.min-wage-hourly']));
  });

  it('covers sittings, papers and formula sheets too', () => {
    const kinds = new Set(overdueReviews('2027-01-26').map((d) => d.kind));
    expect([...kinds].sort()).toEqual(['fact', 'formula-sheet', 'paper', 'sitting']);
  });

  it('rejects a malformed date', () => {
    expect(() => overdueReviews('26-11-15')).toThrow(/YYYY-MM-DD/);
  });
});

describe.skipIf(process.env.CHECK_FRESHNESS !== '1')('freshness (real date, scheduled job only: CHECK_FRESHNESS=1)', () => {
  it('has nothing past its review date today in Taiwan', () => {
    const today = taipeiToday();
    expect(overdueReviews(today).map((d) => `${d.kind} ${d.id}: review by ${d.reviewBy}, today ${today}`)).toEqual([]);
  });
});

describe('registryProblems (facts)', () => {
  const files = (versions: object[]): RegistryFiles => ({
    sources: { 'sources.json': [{ id: 's', title: 'S', url: 'https://example.org/', publisher: 'P', kind: 'web', licence: 'l', accessed: AS_OF }] },
    licences: { 'licences.json': [{ id: 'l', name: 'L', mayQuote: 'yes', mayModify: true, mayRehost: true, attributionRequired: false, nonCommercialOnly: false }] },
    facts: {
      'facts.json': [
        { id: 'site.x', subject: 'site', label: { 'zh-tw': '甲', en: 'X' }, versions, asOf: AS_OF, reviewBy: '2027-01-25', sources: ['s'] },
      ],
    },
    misconceptions: {},
    sittings: { 'sittings.json': [] },
    papers: { 'papers.json': [] },
    formulaSheets: { 'formula-sheets.json': [] },
    examItems: {},
  });
  const v = (n: number, validFrom: string, validTo?: string) => ({ value: { n, unit: { 'zh-tw': '元', en: 'NT$' } }, validFrom, ...(validTo ? { validTo } : {}) });

  it('accepts back-to-back versions', () => {
    expect(registryProblems(buildRegistry(files([v(1, '2026-01-01', '2027-01-01'), v(2, '2027-01-01')])))).toEqual([]);
  });

  it('flags overlapping versions', () => {
    expect(registryProblems(buildRegistry(files([v(1, '2026-01-01', '2027-02-01'), v(2, '2027-01-01')])))).toEqual([
      'fact site.x: version from 2026-01-01 overlaps the one from 2027-01-01 (validTo is exclusive and must be <= the next validFrom)',
    ]);
  });

  it('flags an open-ended version followed by another', () => {
    expect(registryProblems(buildRegistry(files([v(1, '2026-01-01'), v(2, '2027-01-01')])))).toHaveLength(1);
  });

  it('flags a version that ends before it starts', () => {
    expect(registryProblems(buildRegistry(files([v(1, '2027-01-01', '2026-01-01')])))).toEqual([
      'fact site.x: version from 2027-01-01 ends on or before it starts (2026-01-01)',
    ]);
  });
});
