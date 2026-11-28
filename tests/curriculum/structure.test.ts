/**
 * Course structure (port of the ASMC structure checks, generalised): subjects.json, part numbering,
 * core before tracks, part-end checkpoints, minutes per kind, ※ only in extensions, known paths,
 * plus the typed views in src/data/curriculum.ts (neighbours, readiness, ancestors).
 */
import { existsSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { CURRICULUM, SUBJECTS, buildCurriculum, chapterIdFromUrl, isOnPath, lessonIdFromPath } from '../../src/data/curriculum';
import { SUBJECT_IDS, type CodeEntry } from '../../src/data/schema';
import subjectsJson from '../../src/data/subjects.json';
import { build, chapterIn, fixtureCodes, fixtureCourses, lookupsFor, missing, optionalModule, type CourseJson } from './fixtures';
import { STRUCTURE_RULES, type Lookups } from './rules';

type RuleName = keyof typeof STRUCTURE_RULES;
const RULES = Object.entries(STRUCTURE_RULES) as Array<[RuleName, (typeof STRUCTURE_RULES)[RuleName]]>;

const CODES_FILE = 'src/data/codes.ts';
const codes = await optionalModule<{ getCode(key: string): CodeEntry | undefined }>(CODES_FILE, () => import('../../src/data/codes'));

describe('subjects.json', () => {
  it('lists all 10 subjects once, in the schema order', () => {
    expect(SUBJECTS.map((s) => s.id)).toEqual([...SUBJECT_IDS]);
  });

  it('puts math on two paper paths, 數A and 數B, and makes it the pilot', () => {
    const math = SUBJECTS.find((s) => s.id === 'math')!;
    expect(math.status).toBe('pilot');
    expect(math.papers).toEqual(['mathA', 'mathB']);
    expect(math.paths.map((p) => [p.id, p.label['zh-tw']])).toEqual([
      ['mathA', '數A'],
      ['mathB', '數B'],
    ]);
  });

  it('maps every other subject to its paper and one path', () => {
    const paper = Object.fromEntries(SUBJECTS.map((s) => [s.id, s.papers.join(',')]));
    expect(paper).toMatchObject({
      physics: 'science',
      chemistry: 'science',
      biology: 'science',
      earth: 'science',
      inquiry: 'science',
      history: 'social',
      geography: 'social',
      civics: 'social',
      social: 'social',
      chinese: 'chinese',
    });
    for (const s of SUBJECTS.filter((x) => x.id !== 'math')) expect(s.paths, s.id).toHaveLength(1);
  });

  it('marks 國文 as beta, and a subject "active" only once every chapter of its outline is written and reviewed', () => {
    for (const s of SUBJECTS.filter((x) => x.id !== 'math')) {
      if (s.id === 'chinese') { expect(s.status).toBe('beta'); continue; }
      expect(['planned', 'active']).toContain(s.status);
      if (s.status !== 'active') continue;
      const chapters = CURRICULUM.chapters.filter((c) => c.subject === s.id);
      expect(chapters.length, `${s.id} is active but has no outline`).toBeGreaterThan(0);
      for (const c of chapters) {
        for (const loc of ['zh-tw', 'en']) {
          const f = `src/content/lessons/${loc}/${c.id}.mdx`;
          expect(existsSync(f), `${f} missing for active subject ${s.id}`).toBe(true);
          expect(readFileSync(f, 'utf8'), `${f} is not reviewed`).toMatch(/^status: *reviewed\s*$/m);
        }
      }
    }
  });

  it('names a 樂詞網 高中以下 term set only where one exists (no 歷史, 公民, 國文 or 探究 set)', () => {
    // research/verified-2026-11-15.json, exam-wide: sets exist for 數學, 物理學, 化學, 生命科學, 地球科學, 地理學.
    const withSet = SUBJECTS.filter((s) => s.termSource).map((s) => [s.id, s.termSource]);
    expect(withSet).toEqual(['math', 'physics', 'chemistry', 'biology', 'earth', 'geography'].map((id) => [id, `naer-terms-${id}`]));
  });

  it('keeps every learner-facing label non-empty in both languages', () => {
    const labels = SUBJECTS.flatMap((s) => [s.title, s.short, ...s.paths.map((p) => p.label)]);
    expect(labels.filter((l) => !l['zh-tw'].trim() || !l.en.trim())).toEqual([]);
  });

  it('uses unique path ids within a subject', () => {
    expect(SUBJECTS.filter((s) => new Set(s.paths.map((p) => p.id)).size !== s.paths.length).map((s) => s.id)).toEqual([]);
  });
});

describe('structure rules on the real outlines', () => {
  const lk: Lookups = codes ? { getCode: (k) => codes.getCode(k) } : {};
  for (const [name, rule] of RULES) {
    const note = name === 'notExaminedMarkOnlyInExtensions' && !codes ? ` (chapter marks only; code marks need codes.ts) ${missing(CODES_FILE)}` : '';
    it(`${name}${note}`, () => expect(rule(CURRICULUM, lk)).toEqual([]));
  }
  it.skipIf(!codes)(`notExaminedMarkOnlyInExtensions with the code registry${codes ? '' : ` ${missing(CODES_FILE)}`}`, () => {
    expect(STRUCTURE_RULES.notExaminedMarkOnlyInExtensions(CURRICULUM, lk)).toEqual([]);
  });
});

describe('structure rules on the passing fixture', () => {
  const cur = build(fixtureCourses());
  const lk = lookupsFor(fixtureCodes());
  for (const [name, rule] of RULES) it(name, () => expect(rule(cur, lk)).toEqual([]));
});

type Courses = Record<string, CourseJson>;
const CASES: Array<{ rule: RuleName; name: string; mutate: (c: Courses) => void; match: RegExp; also?: RuleName[] }> = [
  { rule: 'partsNumberedFromZero', name: 'a skipped part number', mutate: (c) => (c.math.parts[2].num = 7), match: /math: parts are numbered 0, 1, 7, 3, 4/ },
  {
    rule: 'corePartsBeforeTracks',
    name: 'a core part after a track',
    mutate: (c) => {
      const [core] = c.math.parts.splice(2, 1);
      c.math.parts.push(core);
      c.math.parts.forEach((p, i) => (p.num = i));
    },
    match: /math: core Part 4 \(fx-eleven\) comes after a track part/,
  },
  {
    rule: 'tracksAreWellFormed',
    name: 'a track that starts after a missing chapter',
    mutate: (c) => ((c.math.parts[3].track as { entry: { after: string[] } }).entry.after = ['math/fx-missing']),
    match: /track fx-extension starts after math\/fx-missing, which does not exist/,
  },
  {
    rule: 'tracksAreWellFormed',
    name: 'a track split by another track',
    mutate: (c) => {
      const again = structuredClone(c.math.parts[3]);
      again.chapters[0].slug = 'fx-extension-2';
      again.num = 5;
      c.math.parts.push(again);
    },
    match: /track fx-extension is split/,
  },
  {
    rule: 'corePartsEndWithACheckpoint',
    name: 'a core part that ends with a lesson',
    mutate: (c) => {
      const ch = c.math.parts[1].chapters;
      [ch[1], ch[2]] = [ch[2], ch[1]];
    },
    match: /math Part 1 \(fx-ten\) on mathA ends with fx-toolbox \(toolbox\)/,
  },
  {
    rule: 'corePartsEndWithACheckpoint',
    name: 'a branching part with no checkpoint on one path',
    mutate: (c) => c.math.parts[2].chapters.splice(3, 1),
    match: /math Part 2 \(fx-eleven\) on mathA ends with fx-a-only \(core\)/,
  },
  { rule: 'minutesWithinCap', name: 'a 20-minute toolbox', mutate: (c) => (chapterIn(c, 'math/fx-toolbox').minutes = 20), match: /math\/fx-toolbox \(toolbox\) runs 20 min; the cap is 15/ },
  { rule: 'minutesWithinCap', name: 'a 31-minute core chapter', mutate: (c) => (chapterIn(c, 'math/fx-real').minutes = 31), match: /math\/fx-real \(core\) runs 31 min; the cap is 30/ },
  { rule: 'notExaminedMarkOnlyInExtensions', name: 'a ※ mark on a core chapter', mutate: (c) => (chapterIn(c, 'math/fx-real').marks = ['※']), match: /math\/fx-real \(core\) is marked ※/ },
  {
    rule: 'notExaminedMarkOnlyInExtensions',
    name: 'a ※ code in a core chapter',
    mutate: (c) => (chapterIn(c, 'math/fx-real').codes = [{ key: 'math:FX-10-1' }, { key: 'math:FX-12-1', role: 'beyond' }]),
    match: /math\/fx-real \(core\) refers to ※ code math:FX-12-1/,
  },
  { rule: 'pathsAreKnown', name: 'an unknown path', mutate: (c) => (chapterIn(c, 'math/fx-a-only').paths = ['mathC']), match: /math\/fx-a-only is on unknown path mathC/ },
  { rule: 'pathsAreKnown', name: 'a site chapter with paths', mutate: (c) => (chapterIn(c, 'site/fx-scoring').paths = ['mathA']), match: /site\/fx-scoring: site chapters are on every path/ },
];

describe('structure rules fire on broken fixtures', () => {
  for (const k of CASES) {
    it(`${k.rule}: ${k.name}`, () => {
      const courses = fixtureCourses();
      k.mutate(courses);
      const cur = build(courses);
      const lk = lookupsFor(fixtureCodes());
      expect(STRUCTURE_RULES[k.rule](cur, lk).join('\n')).toMatch(k.match);
      const silent = new Set<RuleName>([k.rule, ...(k.also ?? [])]);
      expect(RULES.filter(([n]) => !silent.has(n)).flatMap(([n, r]) => r(cur, lk).map((v) => `${n}: ${v}`))).toEqual([]);
    });
  }
});

describe('curriculum views (fixture)', () => {
  const cur = build(fixtureCourses(), [
    '/src/content/lessons/zh-tw/math/fx-real.mdx',
    '/src/content/lessons/en/math/fx-real.mdx',
    '/src/content/lessons/zh-tw/math/fx-numbers.mdx',
  ]);
  const ids = (xs: Array<{ id: string } | undefined>) => xs.map((x) => x?.id);

  it('flattens chapters with global ids, parts and tracks', () => {
    const c = cur.chapterById('math/fx-a-only')!;
    expect([c.subject, c.partNum, c.partId, c.track, c.onPaths]).toEqual(['math', 2, 'fx-eleven', 'core', ['mathA']]);
    expect(cur.chapterById('math/fx-real')!.onPaths).toEqual(['mathA', 'mathB']);
    expect(cur.chapterById('math/fx-sprint-review')!.track).toBe('sprint-fx');
    expect(cur.chapters[0].id).toBe('site/welcome'); // site first, then subjects in schema order
  });

  it('applies schema defaults', () => {
    const c = cur.chapterById('math/fx-fractions')!;
    expect([c.codes, c.marks, c.reviews, c.examItems, c.activity]).toEqual([[], [], [], [], '']);
  });

  it('walks the core in order, across parts, without a path', () => {
    expect(ids([cur.neighbours('math/fx-numbers').prev, cur.neighbours('math/fx-numbers').next])).toEqual([undefined, 'math/fx-fractions']);
    expect(cur.neighbours('math/fx-check-1').next?.id).toBe('math/fx-shared-11');
  });

  it('skips chapters off the learner’s path (數B skips 數A chapters, and vice versa)', () => {
    expect(cur.neighbours('math/fx-shared-11', 'mathB').next?.id).toBe('math/fx-b-only');
    expect(cur.neighbours('math/fx-shared-11', 'mathA').next?.id).toBe('math/fx-a-only');
    expect(cur.neighbours('math/fx-check-2b', 'mathB').prev?.id).toBe('math/fx-b-only');
    expect(cur.neighbours('math/fx-a-only', 'mathB')).toEqual({});
  });

  it('never steps from the core into a track, between tracks, or across subjects', () => {
    expect(cur.neighbours('math/fx-check-2b').next).toBeUndefined();
    expect(cur.neighbours('math/fx-check-2a', 'mathA').next).toBeUndefined();
    expect(cur.neighbours('math/fx-extension').prev).toBeUndefined();
    expect(cur.neighbours('math/fx-extension').next).toBeUndefined();
    expect(cur.neighbours('math/fx-sprint-review').next?.id).toBe('math/fx-sprint-review-2');
    expect(cur.neighbours('physics/fx-arrows').prev).toBeUndefined();
    expect(cur.neighbours('site/fx-scoring').next).toBeUndefined();
  });

  it('puts site chapters on every path', () => {
    const welcome = cur.chapterById('site/welcome')!;
    expect(isOnPath(welcome, 'mathB') && isOnPath(welcome, 'science')).toBe(true);
    expect(cur.neighbours('site/welcome', 'mathA').next?.id).toBe('site/fx-scoring');
  });

  it('collects ancestors across subjects', () => {
    expect([...cur.ancestorsOf('physics/fx-motion')].sort()).toEqual(['math/fx-fractions', 'math/fx-numbers', 'math/fx-real', 'physics/fx-arrows', 'site/welcome']);
    expect(cur.ancestorsOf('site/welcome').size).toBe(0);
    expect(cur.ancestorsOf('math/nope').size).toBe(0);
  });

  it('terminates on a cyclic outline', () => {
    const courses = fixtureCourses();
    (chapterIn(courses, 'math/fx-numbers').prereqs as string[]).push('math/fx-fractions');
    expect(build(courses).ancestorsOf('math/fx-numbers').has('math/fx-numbers')).toBe(true);
  });

  it('marks a chapter ready only when both locales exist', () => {
    expect(cur.isReady('math/fx-real')).toBe(true);
    expect(cur.isReady('math/fx-numbers')).toBe(false);
    expect(cur.isReady('math/nope')).toBe(false);
  });

  it('names each concept’s owner chapter', () => {
    expect(cur.conceptOwner('math.fx-real-number')?.id).toBe('math/fx-real');
    expect(cur.conceptOwner('math.fx-nothing')).toBeUndefined();
  });

  it('turns lesson paths and URLs into ids', () => {
    expect(lessonIdFromPath('C:\\x\\src\\content\\lessons\\en\\math\\fx-real.mdx')).toBe('en/math/fx-real');
    expect(chapterIdFromUrl('/zh-tw/math/real-numbers/')).toBe('math/real-numbers');
    expect(chapterIdFromUrl('/repo/en/site/welcome/')).toBe('site/welcome');
    expect(chapterIdFromUrl('/zh-tw/')).toBeUndefined();
  });

  it('works with zero course files', () => {
    const empty = buildCurriculum([], subjectsJson);
    expect([empty.chapters, empty.courses, empty.neighbours('math/x'), empty.isReady('math/x')]).toEqual([[], [], {}, false]);
    expect(empty.pathsOf('math')).toEqual(['mathA', 'mathB']);
  });

  it('rejects malformed course data and a second file for one subject', () => {
    const courses = fixtureCourses();
    delete (chapterIn(courses, 'math/fx-real') as Record<string, unknown>).sources;
    expect(() => build(courses)).toThrow(/course file "math" is invalid: parts\.1\.chapters\.0\.sources/);
    const twice = fixtureCourses();
    expect(() => buildCurriculum([twice.math, structuredClone(twice.math)], subjectsJson)).toThrow(/two course files for subject "math"/);
  });
});
