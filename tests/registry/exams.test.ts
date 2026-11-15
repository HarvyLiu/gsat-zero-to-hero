/**
 * Exam registries (src/data/registry/exam/): the 116 timetable exactly as the 簡章 prints it, paper
 * layouts whose numbers add up, formula sheets whose printed values round correctly, and an item index
 * that only links to CEEC and only uses real curriculum codes. Also lints every bilingual string in the
 * registries for Taiwan punctuation.
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse as parseYaml } from 'yaml';
import { describe, expect, it } from 'vitest';
import { CodeKey } from '../../src/data/schema';
import {
  buildRegistry,
  EXAM_ITEMS,
  expectedExamItemId,
  FORMULA_SHEETS,
  getPaper,
  getSitting,
  PAPER_IDS,
  PAPERS,
  REGISTRY_DATA,
  registryProblems,
  SOURCES,
  type PaperDef,
  type RegistryFiles,
} from '../../src/data/registry';

const SRC = fileURLToPath(new URL('../../src/', import.meta.url));

// Builder A's code registry may land after this file; check codes against it whenever it exists.
const CODES_FILE = join(SRC, 'data', 'codes.ts');
const CODES: Map<string, unknown> | undefined = existsSync(CODES_FILE) ? (await import('../../src/data/codes')).CODES : undefined;

const sitting116 = () => {
  const s = getSitting('116');
  if (!s) throw new Error('sitting 116 missing');
  return s;
};
const minutesBetween = (a: string, b: string) => (Date.parse(b) - Date.parse(a)) / 60000;

describe('exam/sittings.json: the 116 sitting', () => {
  it('lists the seven sessions exactly as the 116簡章 timetable gives them', () => {
    expect(sitting116().sessions.map((s) => [s.paper, s.start, s.end])).toEqual([
      ['mathA', '2027-01-22T09:20:00+08:00', '2027-01-22T11:00:00+08:00'],
      ['science', '2027-01-22T12:50:00+08:00', '2027-01-22T14:40:00+08:00'],
      ['english', '2027-01-23T09:20:00+08:00', '2027-01-23T11:00:00+08:00'],
      ['chinese-comp', '2027-01-23T12:50:00+08:00', '2027-01-23T14:20:00+08:00'],
      ['chinese-writing', '2027-01-23T15:20:00+08:00', '2027-01-23T16:50:00+08:00'],
      ['mathB', '2027-01-24T09:20:00+08:00', '2027-01-24T11:00:00+08:00'],
      ['social', '2027-01-24T12:50:00+08:00', '2027-01-24T14:40:00+08:00'],
    ]);
  });

  it('keeps every session in Taiwan time, in order and without overlap', () => {
    const sessions = sitting116().sessions;
    for (const s of sessions) {
      expect(s.start.endsWith('+08:00') && s.end.endsWith('+08:00')).toBe(true);
      expect(minutesBetween(s.start, s.end)).toBeGreaterThan(0);
    }
    for (let i = 1; i < sessions.length; i++) expect(Date.parse(sessions[i].start)).toBeGreaterThanOrEqual(Date.parse(sessions[i - 1].end));
  });

  it('gives each paper the session length papers.json records', () => {
    for (const s of sitting116().sessions) {
      const paper = getPaper(s.paper);
      if (paper) expect([s.paper, minutesBetween(s.start, s.end)]).toEqual([s.paper, paper.minutes]);
    }
    // English is a session of the sitting but not a paper this course teaches
    expect(sitting116().sessions.filter((s) => !getPaper(s.paper)).map((s) => s.paper)).toEqual(['english']);
  });

  it('has unique milestones in date order, from the brochure to the 60-level lookup', () => {
    const ms = sitting116().milestones;
    expect(new Set(ms.map((m) => m.id)).size).toBe(ms.length);
    for (let i = 1; i < ms.length; i++) expect(ms[i].date >= ms[i - 1].date).toBe(true);
    const byId = Object.fromEntries(ms.map((m) => [m.id, m.date]));
    expect(byId).toMatchObject({
      'registration-opens': '2026-10-27',
      'registration-closes': '2026-11-10',
      'registration-check-opens': '2026-11-13',
      'registration-check-closes': '2026-11-19',
      'exam-info-opens': '2027-01-05',
      'scores-released': '2027-02-25',
    });
  });

  it('is reviewed right after the sitting', () => {
    expect(sitting116().reviewBy).toBe('2027-01-25');
  });
});

describe('exam/papers.json', () => {
  it('describes every paper the course prepares for', () => {
    expect([...PAPERS.keys()].sort()).toEqual([...PAPER_IDS].sort());
  });

  it('says the layout is observed, not promised for 116', () => {
    for (const p of PAPERS.values()) {
      expect([p.id, p.layout.basis['zh-tw'].includes('116')]).toEqual([p.id, true]);
      expect([p.id, /116/.test(p.layout.basis.en) && /unconfirmed|not yet published/.test(p.layout.basis.en)]).toEqual([p.id, true]);
      expect(p.layout.observed).toEqual([111, 112, 113, 114, 115]);
    }
  });

  it('adds up: sections to parts, parts to the total, per-year splits to the total', () => {
    const problems: string[] = [];
    for (const p of PAPERS.values()) {
      for (const part of p.layout.parts) {
        for (const s of part.sections) {
          if (s.first !== undefined && s.last !== undefined && s.count !== undefined && s.last - s.first + 1 !== s.count) problems.push(`${p.id}/${part.id}: ${s.first}–${s.last} is not ${s.count} items`);
          if (s.count !== undefined && s.pointsEach !== undefined && s.points !== undefined && s.count * s.pointsEach !== s.points) problems.push(`${p.id}/${part.id}: ${s.count}×${s.pointsEach} ≠ ${s.points}`);
        }
        const sectionPoints = part.sections.map((s) => s.points);
        if (part.points !== undefined && sectionPoints.every((x) => x !== undefined) && sectionPoints.reduce((a, b) => a! + b!, 0) !== part.points) {
          problems.push(`${p.id}/${part.id}: sections do not add up to ${part.points}`);
        }
      }
      const partPoints = p.layout.parts.map((x) => x.points);
      if (partPoints.every((x) => x !== undefined) && partPoints.reduce((a, b) => a! + b!, 0) !== p.totalPoints.value) problems.push(`${p.id}: parts do not add up to ${p.totalPoints.value}`);
      for (const y of p.layout.byYear) {
        if (!p.layout.observed.includes(y.sitting)) problems.push(`${p.id}: byYear ${y.sitting} is not an observed sitting`);
        if (y.partPoints) {
          if (y.partPoints.length !== p.layout.parts.length) problems.push(`${p.id} ${y.sitting}: partPoints has ${y.partPoints.length} entries for ${p.layout.parts.length} parts`);
          if (y.partPoints.reduce((a, b) => a + b, 0) !== p.totalPoints.value) problems.push(`${p.id} ${y.sitting}: parts add up to ${y.partPoints.reduce((a, b) => a + b, 0)}, not ${p.totalPoints.value}`);
        }
      }
    }
    expect(problems).toEqual([]);
  });

  it('records the verified totals and session lengths', () => {
    const summary = Object.fromEntries([...PAPERS.values()].map((p) => [p.id, [p.minutes, p.totalPoints.value, p.totalPoints.basis]]));
    expect(summary).toEqual({
      mathA: [100, 100, 'observed'],
      mathB: [100, 100, 'observed'],
      science: [110, 128, 'observed'],
      social: [110, 144, 'observed'],
      'chinese-comp': [90, 100, 'rule'],
      'chinese-writing': [90, 50, 'rule'],
    });
  });

  it('keeps the 數A 6/6/5 and 數B 7/5/5 choice layouts', () => {
    const counts = (p: PaperDef | undefined) => p?.layout.parts[0].sections.map((s) => [s.type, s.first, s.last]);
    expect(counts(getPaper('mathA'))).toEqual([
      ['single', 1, 6],
      ['multi', 7, 12],
      ['fill', 13, 17],
    ]);
    expect(counts(getPaper('mathB'))).toEqual([
      ['single', 1, 7],
      ['multi', 8, 12],
      ['fill', 13, 17],
    ]);
  });

  it('states the multi-select rule in every paper that can have multi-select items', () => {
    for (const id of ['mathA', 'mathB', 'science', 'social', 'chinese-comp'] as const) {
      expect([id, getPaper(id)!.scoring.some((r) => r['zh-tw'].includes('(n−2k)/n'))]).toEqual([id, true]);
    }
  });
});

describe('exam/formula-sheets.json', () => {
  const a = FORMULA_SHEETS.get('mathA')!;
  const b = FORMULA_SHEETS.get('mathB')!;

  it('has a sheet for each math paper', () => {
    expect([...FORMULA_SHEETS.keys()].sort()).toEqual(['mathA', 'mathB']);
  });

  it('prints the same list for 數B minus the angle-sum formulas', () => {
    const ids = (s: typeof a) => s.formulas.map((f) => f.id);
    expect(ids(a)).toContain('angle-sum');
    expect(ids(b)).not.toContain('angle-sum');
    expect(ids(b)).toEqual(ids(a).filter((id) => id !== 'angle-sum'));
    expect(b.values).toEqual(a.values);
  });

  it('prints values that are the true values correctly rounded', () => {
    const exact: Record<string, number> = {
      sqrt2: Math.SQRT2,
      sqrt3: Math.sqrt(3),
      sqrt5: Math.sqrt(5),
      sqrt6: Math.sqrt(6),
      pi: Math.PI,
      log2: Math.log10(2),
      log3: Math.log10(3),
      log5: Math.log10(5),
      log7: Math.log10(7),
    };
    expect(a.values.map((v) => v.id).sort()).toEqual(Object.keys(exact).sort());
    for (const v of a.values) {
      const decimals = v.approx.split('.')[1].length;
      expect([v.id, exact[v.id].toFixed(decimals)]).toEqual([v.id, v.approx]);
    }
  });

  it('only claims content for a paper that was read', () => {
    for (const s of [a, b]) {
      expect(s.contentFrom.every((y) => s.present.includes(y))).toBe(true);
      expect(s.sources.some((id) => SOURCES.get(id)?.title.includes(`${s.contentFrom[0]}`))).toBe(true);
    }
  });
});

describe('exam/items/*.json', () => {
  const items = [...EXAM_ITEMS.values()];

  it('indexes the 115 數A/數B and 111 數B items the research cites', () => {
    expect(items.length).toBeGreaterThan(0);
    expect(new Set(items.map((i) => i.sitting))).toEqual(new Set([111, 115]));
  });

  it('derives every id from sitting, paper and question numbers', () => {
    expect(items.filter((i) => i.id !== expectedExamItemId(i)).map((i) => i.id)).toEqual([]);
  });

  it('links only to https CEEC pages that are in the bibliography', () => {
    const known = new Set([...SOURCES.values()].map((s) => s.url));
    for (const i of items) {
      for (const url of [i.paperUrl, i.answerUrl, i.rubricUrl].filter((u): u is string => !!u)) {
        expect(new URL(url).origin).toBe('https://www.ceec.edu.tw');
        expect([i.id, known.has(url)]).toEqual([i.id, true]);
      }
    }
  });

  it('never stores question text', () => {
    for (const i of items) expect(Object.keys(i).sort()).not.toContain('text');
  });

  it('uses curriculum codes that look like CodeKeys', () => {
    for (const i of items) for (const c of i.codes) expect([i.id, c, CodeKey.safeParse(c).success]).toEqual([i.id, c, true]);
  });

  it.skipIf(!CODES)('uses curriculum codes that exist in the code registry', () => {
    const unknown = items.flatMap((i) => i.codes.filter((c) => !CODES!.has(c)).map((c) => `${i.id}: ${c}`));
    expect(unknown).toEqual([]);
  });

  it('agrees with the paper layout on item type', () => {
    const problems: string[] = [];
    for (const i of items) {
      const paper = getPaper(i.paper);
      if (!paper || !paper.layout.observed.includes(i.sitting)) continue;
      for (const part of paper.layout.parts) {
        for (const s of part.sections) {
          if (s.first === undefined || s.last === undefined || !i.numbers.every((q) => q >= s.first! && q <= s.last!)) continue;
          const ok = s.type === 'mixed' || s.type === 'group' ? true : s.type === 'choice' ? i.type === 'single' || i.type === 'multi' : i.type === s.type;
          if (!ok) problems.push(`${i.id} is ${i.type}, but Q${s.first}–${s.last} of ${i.paper} are ${s.type}`);
        }
      }
    }
    expect(problems).toEqual([]);
  });

  it('marks only research-confirmed items as verified', () => {
    // every entry here was confirmed by the 2026-11-15 verification; unconfirmed ones are omitted, not added unverified
    expect(items.filter((i) => !i.verified).map((i) => i.id)).toEqual([]);
  });
});

describe('references into the item index from other data', () => {
  /** every `modelledOn` in the YAML item banks that looks like an official item id must exist */
  it('resolves modelledOn ids in src/data/items/**/*.yaml', () => {
    const root = join(SRC, 'data', 'items');
    if (!existsSync(root)) return;
    const files: string[] = [];
    const walk = (d: string) => readdirSync(d).forEach((n) => (statSync(join(d, n)).isDirectory() ? walk(join(d, n)) : /\.ya?ml$/.test(n) && files.push(join(d, n))));
    walk(root);
    const unknown: string[] = [];
    for (const f of files) {
      const bank = parseYaml(readFileSync(f, 'utf8')) as { items?: { id?: string; modelledOn?: string }[] } | null;
      for (const item of bank?.items ?? []) {
        if (item.modelledOn && /^\d{3}-[a-zA-Z]+-q[\d-]+$/.test(item.modelledOn) && !EXAM_ITEMS.has(item.modelledOn)) unknown.push(`${f}: ${item.id} → ${item.modelledOn}`);
      }
    }
    expect(unknown).toEqual([]);
  });
});

describe('registryProblems (exam items and sittings)', () => {
  const item = { id: '115-mathA-q1', sitting: 115, paper: 'mathA', numbers: [1], type: 'single', paperUrl: 'https://www.ceec.edu.tw/x.pdf', curriculum: '108', verified: true };
  const files = (over: Partial<RegistryFiles>): RegistryFiles => ({
    sources: { 'sources.json': [] },
    licences: { 'licences.json': [] },
    facts: { 'facts.json': [] },
    misconceptions: {},
    sittings: { 'sittings.json': [] },
    papers: { 'papers.json': [] },
    formulaSheets: { 'formula-sheets.json': [] },
    examItems: { 'src/data/registry/exam/items/math.json': [item] },
    ...over,
  });

  it('accepts a well-formed item', () => {
    expect(registryProblems(buildRegistry(files({})))).toEqual([]);
  });

  it('flags an id that does not match its numbers', () => {
    const bad = { ...item, numbers: [2] };
    expect(registryProblems(buildRegistry(files({ examItems: { 'items/math.json': [bad] } })))).toEqual(['exam item 115-mathA-q1: id should be 115-mathA-q2']);
  });

  it('flags a 108-curriculum tag on a pre-111 paper', () => {
    const bad = { ...item, id: '110-mathA-q1', sitting: 110 };
    expect(registryProblems(buildRegistry(files({ examItems: { 'items/math.json': [bad] } })))).toEqual(['exam item 110-mathA-q1: sitting 110 should be curriculum legacy']);
  });

  it('flags an item filed under the wrong subject', () => {
    expect(registryProblems(buildRegistry(files({ examItems: { 'items/civics.json': [item] } })))).toEqual(['exam item 115-mathA-q1: paper mathA does not belong in items/civics.json']);
  });

  it('rejects a non-CEEC link at load time', () => {
    expect(() => buildRegistry(files({ examItems: { 'items/math.json': [{ ...item, paperUrl: 'https://example.org/x.pdf' }] } }))).toThrow(/paperUrl/);
  });

  it('flags overlapping sessions', () => {
    const sitting = {
      id: '999',
      label: { 'zh-tw': '測', en: 'T' },
      sessions: [
        { paper: 'a', label: { 'zh-tw': '甲', en: 'A' }, start: '2027-01-22T09:00:00+08:00', end: '2027-01-22T11:00:00+08:00' },
        { paper: 'b', label: { 'zh-tw': '乙', en: 'B' }, start: '2027-01-22T10:00:00+08:00', end: '2027-01-22T12:00:00+08:00' },
      ],
      sources: ['s'],
      reviewBy: '2027-01-25',
    };
    const problems = registryProblems(buildRegistry(files({ sittings: { 'sittings.json': [sitting] }, examItems: {} })));
    expect(problems).toContain('sitting 999: b starts before the previous session ends');
    expect(problems).toContain('sitting 999 cites unknown source "s"');
  });
});

describe('bilingual strings in the registries', () => {
  /** every { 'zh-tw', en } pair anywhere in the parsed registries */
  function pairs(): { where: string; zh: string; en: string }[] {
    const out: { where: string; zh: string; en: string }[] = [];
    const walk = (v: unknown, where: string) => {
      if (Array.isArray(v)) v.forEach((x, i) => walk(x, `${where}[${i}]`));
      else if (v instanceof Map) v.forEach((x, k) => walk(x, `${where}.${k}`));
      else if (v && typeof v === 'object') {
        const o = v as Record<string, unknown>;
        if (typeof o['zh-tw'] === 'string' && typeof o.en === 'string') out.push({ where, zh: o['zh-tw'], en: o.en });
        else Object.entries(o).forEach(([k, x]) => walk(x, `${where}.${k}`));
      }
    };
    const { fileOf: _ignored, ...data } = REGISTRY_DATA;
    walk(data, 'registry');
    return out;
  }
  const HAN = '\\u3400-\\u9fff';
  const ASCII_NEXT_TO_HAN = new RegExp(`[${HAN}][,;:?!()]|[,;:?!()][${HAN}]`);
  const FULL_WIDTH = /[，。、；：「」？！（）]/;

  it('finds the strings it lints', () => {
    expect(pairs().length).toBeGreaterThan(100);
  });

  it('uses full-width punctuation next to Chinese in zh-tw', () => {
    expect(pairs().filter((p) => ASCII_NEXT_TO_HAN.test(p.zh)).map((p) => `${p.where}: ${p.zh}`)).toEqual([]);
  });

  it('keeps full-width punctuation out of en', () => {
    expect(pairs().filter((p) => FULL_WIDTH.test(p.en)).map((p) => `${p.where}: ${p.en}`)).toEqual([]);
  });

  it('avoids Mainland-only wording in zh-tw', () => {
    // common Mainland forms; Taiwan uses 資訊, 軟體, 影片, 網路, 預設
    expect(pairs().filter((p) => /信息|軟件|視頻|網絡|默認/.test(p.zh)).map((p) => `${p.where}: ${p.zh}`)).toEqual([]);
  });
});
