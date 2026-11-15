/**
 * The no-jump rule, global and cross-subject (port of the ASMC reference's tests/curriculum.test.ts).
 * Runs on the real outlines (src/data/course/*.json, possibly none yet) and on the fixture outline,
 * where each failing variant proves its rule fires, and fires alone (or with the rules it must drag along).
 */
import { describe, expect, it } from 'vitest';
import { CURRICULUM } from '../../src/data/curriculum';
import type { TermEntry } from '../../src/data/schema';
import { build, chapterIn, fixtureCodes, fixtureCourses, FIXTURE_TERMS, lookupsFor, missing, optionalModule, type CourseJson } from './fixtures';
import { NO_JUMP_RULES, type Lookups } from './rules';

type RuleName = keyof typeof NO_JUMP_RULES;
const RULES = Object.entries(NO_JUMP_RULES) as Array<[RuleName, (typeof NO_JUMP_RULES)[RuleName]]>;
const NEEDS_GLOSSARY = new Set<RuleName>(['conceptsAreInTheGlossary', 'deepenedConceptsAreIntroduced']);

const GLOSSARY_FILE = 'src/data/glossary.ts';
const glossary = await optionalModule<{ getTerm(id: string): TermEntry | undefined }>(GLOSSARY_FILE, () => import('../../src/data/glossary'));
const realLookups: Lookups = glossary ? { getTerm: (id) => glossary.getTerm(id) } : {};

describe('no-jump rules on the real outlines', () => {
  it(`loads ${CURRICULUM.courses.length} course file(s) with ${CURRICULUM.chapters.length} chapter(s)`, () => {
    expect(CURRICULUM.chapters.length).toBeGreaterThanOrEqual(0);
  });
  for (const [name, rule] of RULES) {
    const skip = NEEDS_GLOSSARY.has(name) && !glossary;
    const note = !glossary && name === 'usesAreTaughtEarlier' ? ' (without the glossary: no vocab exemption) ' + missing(GLOSSARY_FILE) : '';
    it.skipIf(skip)(`${name}${skip ? ` ${missing(GLOSSARY_FILE)}` : note}`, () => {
      expect(rule(CURRICULUM, realLookups)).toEqual([]);
    });
  }
});

describe('no-jump rules on the passing fixture', () => {
  const cur = build(fixtureCourses());
  const lk = lookupsFor(fixtureCodes());
  for (const [name, rule] of RULES) it(name, () => expect(rule(cur, lk)).toEqual([]));

  it('exempts welcome and exam-literacy chapters and the first chapter of each track from needing a prereq', () => {
    const noPrereq = cur.chapters.filter((c) => c.prereqs.length === 0).map((c) => c.id);
    expect(noPrereq).toEqual(['site/welcome', 'site/fx-scoring', 'math/fx-sprint-review']);
  });
});

type Courses = Record<string, CourseJson>;
interface Case {
  rule: RuleName;
  name: string;
  mutate?: (c: Courses) => void;
  terms?: (t: Map<string, TermEntry>) => void;
  /** a phrase the violation must contain */
  match: RegExp;
  /** rules that this break necessarily trips too; every other rule must stay silent */
  also?: RuleName[];
}

const push = (c: Courses, id: string, field: string, ...values: string[]) => {
  const ch = chapterIn(c, id);
  ch[field] = [...((ch[field] as string[] | undefined) ?? []), ...values];
};
const chapter = (slug: string, over: Record<string, unknown> = {}) => ({
  slug,
  title: { 'zh-tw': '測試', en: 'Fixture' },
  blurb: { 'zh-tw': '測試用章節。', en: 'A fixture chapter.' },
  objectives: [{ 'zh-tw': '測試', en: 'Fixture' }],
  kind: 'core',
  prereqs: ['site/welcome'],
  minutes: 20,
  sources: ['fx-source'],
  ...over,
});

const CASES: Case[] = [
  {
    rule: 'uniqueIds',
    name: 'a slug used twice in one subject',
    mutate: (c) => c.math.parts[1].chapters.splice(1, 0, chapter('fx-numbers', { prereqs: ['math/fx-real'] })),
    match: /math\/fx-numbers is used twice/,
  },
  { rule: 'prereqsExist', name: 'a prereq that does not exist', mutate: (c) => push(c, 'math/fx-fractions', 'prereqs', 'math/fx-missing'), match: /needs math\/fx-missing, which does not exist/ },
  {
    rule: 'sameSubjectPrereqsComeEarlier',
    name: 'a prereq later in the same subject',
    mutate: (c) => {
      c.math.parts[2].chapters.unshift(chapter('fx-late'));
      push(c, 'math/fx-real', 'prereqs', 'math/fx-late');
    },
    match: /math\/fx-real needs math\/fx-late, which comes later/,
  },
  { rule: 'acyclic', name: 'a cycle across subjects', mutate: (c) => push(c, 'math/fx-real', 'prereqs', 'physics/fx-motion'), match: /prereq cycle: .*physics\/fx-motion needs math\/fx-real/ },
  {
    rule: 'acyclic',
    name: 'a cycle inside one subject',
    mutate: (c) => push(c, 'math/fx-numbers', 'prereqs', 'math/fx-fractions'),
    match: /prereq cycle/,
    also: ['sameSubjectPrereqsComeEarlier'],
  },
  {
    rule: 'everyChapterHasAPrereq',
    name: 'a core chapter with no prereq',
    mutate: (c) => Object.assign(chapterIn(c, 'math/fx-fractions'), { prereqs: [], uses: [] }),
    match: /math\/fx-fractions \(bridge\) has no prerequisite/,
  },
  {
    rule: 'everyChapterHasAPrereq',
    name: 'a second track chapter with no prereq',
    mutate: (c) => Object.assign(chapterIn(c, 'math/fx-sprint-review-2'), { prereqs: [] }),
    match: /math\/fx-sprint-review-2 \(review\) has no prerequisite/,
  },
  { rule: 'conceptIntroducedOnce', name: 'a concept introduced twice in one subject', mutate: (c) => push(c, 'math/fx-toolbox', 'newConcepts', 'math.fx-real-number'), match: /math\.fx-real-number is introduced 2 times/ },
  { rule: 'conceptIntroducedOnce', name: 'a concept introduced again in another subject', mutate: (c) => push(c, 'physics/fx-arrows', 'newConcepts', 'math.fx-integer'), match: /math\.fx-integer is introduced 2 times: math\/fx-numbers, physics\/fx-arrows/ },
  { rule: 'usesAreTaughtEarlier', name: 'using a concept taught later', mutate: (c) => push(c, 'math/fx-numbers', 'uses', 'math.fx-real-number'), match: /math\/fx-numbers uses math\.fx-real-number from math\/fx-real, which it does not depend on/ },
  { rule: 'usesAreTaughtEarlier', name: 'using another subject’s concept without depending on it', mutate: (c) => push(c, 'physics/fx-arrows', 'uses', 'math.fx-real-number'), match: /physics\/fx-arrows uses math\.fx-real-number/ },
  { rule: 'usesAreTaughtEarlier', name: 'using a concept nobody teaches', mutate: (c) => push(c, 'math/fx-real', 'uses', 'math.fx-ghost'), match: /uses math\.fx-ghost, which no chapter introduces/, also: ['conceptsAreInTheGlossary'] },
  { rule: 'usesAreTaughtEarlier', name: 'a vocab-only exemption that no longer applies', terms: (t) => (t.get('math.fx-vocab')!.kind = 'concept'), match: /math\/fx-real uses math\.fx-vocab, which no chapter introduces/ },
  {
    rule: 'usesAreTaughtEarlier',
    name: 'a sprint review of a concept that exists nowhere',
    mutate: (c) => push(c, 'math/fx-sprint-review', 'reviews', 'math.fx-unknown'),
    match: /math\/fx-sprint-review reviews math\.fx-unknown, which is neither in the glossary nor introduced/,
    also: ['conceptsAreInTheGlossary'],
  },
  {
    rule: 'newConceptCap',
    name: 'a checkpoint introducing 3 concepts',
    mutate: (c) => push(c, 'math/fx-check-1', 'newConcepts', 'math.fx-c1', 'math.fx-c2', 'math.fx-c3'),
    match: /math\/fx-check-1 \(checkpoint\) introduces 3 concepts; the cap is 2/,
    also: ['conceptsAreInTheGlossary'],
  },
  {
    rule: 'prereqsOnEveryPathOfTheChapter',
    name: 'a mathB chapter needing a mathA-only chapter',
    mutate: (c) => push(c, 'math/fx-check-2b', 'prereqs', 'math/fx-a-only'),
    match: /math\/fx-check-2b \(on mathB\) needs math\/fx-a-only, which is not on mathB/,
    also: ['noOffPathAncestors'],
  },
  {
    rule: 'noOffPathAncestors',
    name: 'a mathB chapter behind a mathA-only chapter through another subject',
    mutate: (c) => {
      push(c, 'physics/fx-motion', 'prereqs', 'math/fx-a-only');
      push(c, 'math/fx-check-2b', 'prereqs', 'physics/fx-motion');
    },
    match: /math\/fx-check-2b \(on mathB\) has ancestor math\/fx-a-only, which is only on mathA/,
    also: ['crossSubjectPrereqsTargetSharedChapters'],
  },
  {
    rule: 'crossSubjectPrereqsTargetSharedChapters',
    name: 'a cross-subject prereq into a checkpoint',
    mutate: (c) => push(c, 'physics/fx-motion', 'prereqs', 'math/fx-check-1'),
    match: /physics\/fx-motion needs math\/fx-check-1 from another subject, which is a checkpoint chapter/,
  },
  {
    rule: 'crossSubjectPrereqsTargetSharedChapters',
    name: 'a cross-subject prereq into a single-path chapter',
    mutate: (c) => push(c, 'physics/fx-motion', 'prereqs', 'math/fx-a-only'),
    match: /physics\/fx-motion needs math\/fx-a-only from another subject, which is not on mathB/,
  },
  {
    rule: 'extensionsAreNeverPrereqsOfOtherKinds',
    name: 'a review chapter needing an extension chapter',
    mutate: (c) => push(c, 'math/fx-sprint-review-2', 'prereqs', 'math/fx-extension'),
    match: /math\/fx-sprint-review-2 \(review\) needs extension chapter math\/fx-extension/,
  },
  { rule: 'conceptsAreInTheGlossary', name: 'a concept missing from the glossary', mutate: (c) => push(c, 'math/fx-real', 'newConcepts', 'math.fx-not-in-glossary'), match: /math\/fx-real: math\.fx-not-in-glossary is not in the glossary/ },
  {
    rule: 'deepenedConceptsAreIntroduced',
    name: 'a spiral revisit of a concept nobody introduces',
    terms: (t) => (t.get('math.fx-shared')!.deepens = 'math.fx-a-idea-nowhere'),
    match: /math\/fx-shared-11 introduces math\.fx-shared, which deepens math\.fx-a-idea-nowhere, but no chapter introduces math\.fx-a-idea-nowhere/,
  },
];

describe('no-jump rules fire on broken fixtures', () => {
  for (const k of CASES) {
    it(`${k.rule}: ${k.name}`, () => {
      const courses = fixtureCourses();
      k.mutate?.(courses);
      const terms = new Map([...FIXTURE_TERMS].map(([id, t]) => [id, structuredClone(t)]));
      k.terms?.(terms);
      const lk: Lookups = { ...lookupsFor(fixtureCodes()), getTerm: (id) => terms.get(id) };
      const cur = build(courses);
      expect(NO_JUMP_RULES[k.rule](cur, lk).join('\n')).toMatch(k.match);
      const silent = new Set<RuleName>([k.rule, ...(k.also ?? [])]);
      const others = RULES.filter(([n]) => !silent.has(n)).flatMap(([n, r]) => r(cur, lk).map((v) => `${n}: ${v}`));
      expect(others).toEqual([]);
    });
  }
});
