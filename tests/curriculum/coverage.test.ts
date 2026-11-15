/**
 * Code coverage of the official 學習內容 codes (plan: "Coverage test: every in_gsat code is reviewed,
 * in an order that respects verified depends_on"; critic §2: the dependsOn check is code-level with a
 * signed waiver file). Runs on every subject that has a course file, and on the fixture.
 */
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { CURRICULUM } from '../../src/data/curriculum';
import type { CodeEntry } from '../../src/data/schema';
import { build, chapterIn, fixtureCodes, fixtureCourses, missing, optionalModule } from './fixtures';
import { applyWaivers, beyondScopeOutsideExtensions, coverageOf, dependencyGaps, unknownCodeRefs, Waiver } from './rules';

const CODES_FILE = 'src/data/codes.ts';
const registry = await optionalModule<{ CODES: Map<string, CodeEntry>; getCode(key: string): CodeEntry | undefined }>(CODES_FILE, () => import('../../src/data/codes'));

const waiverJson: unknown = JSON.parse(readFileSync(new URL('../../src/data/course/waivers.json', import.meta.url), 'utf8'));
const subjectsWithCourses: string[] = CURRICULUM.courses.map((c) => c.subject).filter((s) => s !== 'site');

describe('waivers.json', () => {
  it('is a list of {from, to, reason, approvedBy}', () => {
    const r = Waiver.array().safeParse(waiverJson);
    expect(r.success, r.success ? '' : r.error.message).toBe(true);
  });
  it('lists each edge once', () => {
    const keys = (waiverJson as Waiver[]).map((w) => `${w.from}→${w.to}`);
    expect(keys.filter((k, i) => keys.indexOf(k) !== i)).toEqual([]);
  });
});

describe.skipIf(!registry)(`coverage of the real outlines${registry ? '' : ` ${missing(CODES_FILE)}`}`, () => {
  const codes = [...(registry?.CODES.values() ?? [])];
  const getCode = (k: string) => registry!.getCode(k);
  const waivers = Waiver.array().parse(waiverJson);

  it('refers only to codes that exist', () => {
    expect(unknownCodeRefs(CURRICULUM, getCode)).toEqual([]);
  });

  it('reports coverage (math, the pilot, always; other subjects once they have a course file)', () => {
    const report = ['math', ...subjectsWithCourses.filter((s) => s !== 'math')].map((s) => {
      const cov = coverageOf(CURRICULUM, s, codes);
      return `${s}: ${cov.covered}/${cov.total} in-scope codes covered${subjectsWithCourses.includes(s) ? '' : ' (no course file yet)'}`;
    });
    process.stdout.write(`${report.join('\n')}\n`);
    expect(report.length).toBeGreaterThan(0);
  });

  for (const subject of subjectsWithCourses) {
    it(`teaches or reviews every in-scope ${subject} code on the right path(s)`, () => {
      expect(coverageOf(CURRICULUM, subject, codes).missing).toEqual([]);
    });
  }

  it('keeps beyond-學測 codes in extension chapters', () => {
    expect(beyondScopeOutsideExtensions(CURRICULUM, getCode)).toEqual([]);
  });

  it('respects every official dependsOn edge, or has a signed waiver', () => {
    expect(applyWaivers(dependencyGaps(CURRICULUM, codes), waivers).open.map((g) => g.message)).toEqual([]);
  });

  it('has no stale waivers and none for unknown codes', () => {
    const { stale } = applyWaivers(dependencyGaps(CURRICULUM, codes), waivers);
    expect(stale.map((w) => `${w.from}→${w.to} no longer matches a gap`)).toEqual([]);
    expect(waivers.flatMap((w) => [w.from, w.to]).filter((k) => !getCode(k))).toEqual([]);
  });
});

describe('coverage on the passing fixture', () => {
  const cur = build(fixtureCourses());
  const codes = fixtureCodes();
  const getCode = (k: string) => codes.find((c) => c.key === k);

  it('covers math 4/4 (shared, 數A-only and 數B-only codes) and physics 1/1', () => {
    expect(coverageOf(cur, 'math', codes)).toEqual({ subject: 'math', total: 4, covered: 4, missing: [] });
    expect(coverageOf(cur, 'physics', codes)).toEqual({ subject: 'physics', total: 1, covered: 1, missing: [] });
  });
  it('knows every code it refers to', () => expect(unknownCodeRefs(cur, getCode)).toEqual([]));
  it('keeps the ※ code in its extension chapter', () => expect(beyondScopeOutsideExtensions(cur, getCode)).toEqual([]));
  it('respects dependsOn, including a cross-subject edge and a bridge code', () => expect(dependencyGaps(cur, codes)).toEqual([]));
});

describe('coverage rules fire on broken fixtures', () => {
  const move = (from: string, to: string, key: string) => (c: ReturnType<typeof fixtureCourses>) => {
    const a = chapterIn(c, from);
    a.codes = (a.codes as Array<{ key: string }>).filter((r) => r.key !== key);
    const b = chapterIn(c, to);
    b.codes = [...((b.codes as unknown[]) ?? []), { key }];
  };
  const missingFor = (mutate: (c: ReturnType<typeof fixtureCourses>) => void, subject = 'math') => {
    const courses = fixtureCourses();
    mutate(courses);
    return coverageOf(build(courses), subject, fixtureCodes()).missing.join('\n');
  };

  it('reports an in-scope code nobody teaches', () => {
    expect(missingFor((c) => (chapterIn(c, 'math/fx-b-only').codes = []))).toMatch(/math:FX-11B-1 \(FX-11B-1\) is not taught or reviewed on mathB/);
  });
  it('reports a 數A code taught only on the 數B path', () => {
    expect(missingFor(move('math/fx-a-only', 'math/fx-b-only', 'math:FX-11A-1'))).toMatch(/math:FX-11A-1 .* not taught or reviewed on mathA/);
  });
  it('reports a code for both papers taught on one path only', () => {
    expect(missingFor(move('math/fx-shared-11', 'math/fx-a-only', 'math:FX-11-1'))).toMatch(/math:FX-11-1 .* not taught or reviewed on mathB/);
  });
  it('does not count a code that is only bridged or used', () => {
    expect(missingFor((c) => (chapterIn(c, 'physics/fx-motion').codes = [{ key: 'nat:FX-PH-1', role: 'uses' }]), 'physics')).toMatch(/nat:FX-PH-1/);
  });
  it('reports a 數A/數B code in a subject without those paths', () => {
    const codes = fixtureCodes().map((c) => (c.key === 'nat:FX-PH-1' ? { ...c, gsatTrack: 'A' as const } : c));
    expect(coverageOf(build(fixtureCourses()), 'physics', codes).missing.join()).toMatch(/gsatTrack A, but physics has no path mathA/);
  });
  it('reports unknown code keys in codes and assumes', () => {
    const courses = fixtureCourses();
    chapterIn(courses, 'math/fx-real').codes = [{ key: 'math:FX-99-9' }];
    chapterIn(courses, 'math/fx-sprint-review').assumes = ['math:FX-98-1'];
    const codes = fixtureCodes();
    expect(unknownCodeRefs(build(courses), (k) => codes.find((c) => c.key === k))).toEqual([
      'math/fx-real refers to unknown code math:FX-99-9',
      'math/fx-sprint-review assumes unknown code math:FX-98-1',
    ]);
  });
  it('reports a beyond-學測 code taught in a core chapter, but allows role "beyond"', () => {
    const courses = fixtureCourses();
    chapterIn(courses, 'math/fx-real').codes = [{ key: 'math:FX-10-1' }, { key: 'math:FX-12-1' }];
    chapterIn(courses, 'math/fx-shared-11').codes = [{ key: 'math:FX-11-1' }, { key: 'math:FX-12-1', role: 'beyond' }];
    const codes = fixtureCodes();
    expect(beyondScopeOutsideExtensions(build(courses), (k) => codes.find((c) => c.key === k))).toEqual([
      'math/fx-real (core) teaches math:FX-12-1, which is beyond 學測; use an extension chapter or role "beyond"',
    ]);
  });

  describe('dependsOn', () => {
    // Make FX-10-1 depend on FX-11-1, which the outline teaches later: a gap.
    const codes = fixtureCodes().map((c) => (c.key === 'math:FX-10-1' ? { ...c, dependsOn: [...c.dependsOn, 'math:FX-11-1'] } : c));
    const cur = build(fixtureCourses());

    it('reports an edge no chapter order respects', () => {
      expect(dependencyGaps(cur, codes).map((g) => g.message)).toEqual([
        'math:FX-10-1 (in math/fx-real, math/fx-sprint-review) depends on math:FX-11-1 (in math/fx-shared-11), but no chapter with math:FX-10-1 has one with math:FX-11-1 behind it',
      ]);
    });
    it('accepts the gap once a waiver lists it, and reports the waiver as stale once the gap is gone', () => {
      const waiver: Waiver = { from: 'math:FX-10-1', to: 'math:FX-11-1', reason: 'fixture', approvedBy: 'fixture' };
      expect(applyWaivers(dependencyGaps(cur, codes), [waiver])).toEqual({ open: [], stale: [] });
      expect(applyWaivers(dependencyGaps(cur, fixtureCodes()), [waiver]).stale).toEqual([waiver]);
    });
    it('treats a code the chapter assumes (sprint entry level) as already behind it', () => {
      const courses = fixtureCourses();
      chapterIn(courses, 'math/fx-sprint-review').codes = [{ key: 'math:FX-11-1', role: 'reviews' }];
      chapterIn(courses, 'math/fx-sprint-review').assumes = ['math:FX-10-1'];
      expect(dependencyGaps(build(courses), fixtureCodes())).toEqual([]);
    });
    it('rejects a malformed waiver', () => {
      expect(Waiver.safeParse({ from: 'N-10-1', to: 'math:N-7-5', reason: '' }).success).toBe(false);
    });
  });
});
