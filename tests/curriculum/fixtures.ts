/**
 * Fixture data for the curriculum suites: the passing outline in tests/fixtures/course/*.json plus the
 * glossary, code and source lookups it refers to. Everything here is made up (ids are prefixed fx-) and
 * exists only to prove that each rule passes on a good outline and fires on a broken one.
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import type { CodeEntry, LicenceDef, SourceDef, TermEntry } from '../../src/data/schema';
import { buildCurriculum, type Curriculum } from '../../src/data/curriculum';
import subjects from '../../src/data/subjects.json';

const ROOT = new URL('../../', import.meta.url);
const FIXTURES = new URL('tests/fixtures/course/', ROOT);

/**
 * Import another builder's module only if its file exists. A missing file means "not written yet" and
 * the caller skips with a message; any other import error (bad data, syntax) still fails loudly.
 */
export async function optionalModule<T>(file: string, load: () => Promise<unknown>): Promise<T | undefined> {
  if (!existsSync(new URL(file, ROOT))) return undefined;
  return (await load()) as T;
}

export const missing = (file: string) => `(skipped: ${file} does not exist yet)`;

export type CourseJson = {
  subject: string;
  parts: Array<{ num: number; id: string; track?: unknown; chapters: Array<Record<string, unknown> & { slug: string }> }>;
};

/** Fresh, mutable copies of the fixture course files (site, math, physics). */
export function fixtureCourses(): Record<string, CourseJson> {
  const out: Record<string, CourseJson> = {};
  for (const f of readdirSync(FIXTURES).filter((n) => n.endsWith('.json'))) {
    const data = JSON.parse(readFileSync(new URL(f, FIXTURES), 'utf8')) as CourseJson;
    out[data.subject] = data;
  }
  return out;
}

export function build(courses: Record<string, CourseJson>, lessons: string[] = []): Curriculum {
  return buildCurriculum(Object.values(courses), subjects, lessons);
}

/** Find a chapter object inside fixture JSON, to mutate it. */
export function chapterIn(courses: Record<string, CourseJson>, id: string): Record<string, unknown> & { slug: string } {
  const [subject, slug] = id.split('/');
  for (const p of courses[subject]?.parts ?? []) for (const c of p.chapters) if (c.slug === slug) return c;
  throw new Error(`fixture has no chapter ${id}`);
}

const term = (id: string, kind: 'concept' | 'vocab' = 'concept', deepens?: string): TermEntry => ({
  id,
  zh: `測試${id}`,
  en: `fixture ${id}`,
  def: { 'zh-tw': '測試用詞條。', en: 'A fixture term.' },
  source: { id: 'fx-source' },
  kind,
  ...(deepens ? { deepens } : {}),
});

export const FIXTURE_TERMS = new Map<string, TermEntry>(
  [
    term('site.fx-route'),
    term('site.fx-score-band'),
    term('site.fx-multi-select'),
    term('math.fx-integer'),
    term('math.fx-fraction'),
    term('math.fx-real-number'),
    term('math.fx-tool'),
    term('math.fx-shared'),
    term('math.fx-a-idea'),
    term('math.fx-b-idea'),
    term('math.fx-extra'),
    term('math.fx-glossary-only'),
    term('math.fx-vocab', 'vocab'),
    term('physics.fx-force-arrow'),
    term('physics.fx-velocity'),
  ].map((t) => [t.id, t]),
);

const code = (key: string, over: Partial<CodeEntry> = {}): CodeEntry => ({
  key,
  code: key.split(':')[1],
  domain: key.split(':')[0] as CodeEntry['domain'],
  subjects: ['math'],
  level: '10',
  inGsat: 'yes',
  gsatTrack: 'both',
  marks: [],
  title: { 'zh-tw': '測試代碼' },
  keyConcepts: [],
  dependsOn: [],
  status: 'verified',
  source: 'fx-source',
  ...over,
});

/** Codes the fixture outline covers: 4 in-scope math codes (one shared, one per path), 1 physics code. */
export function fixtureCodes(): CodeEntry[] {
  return [
    code('math:FX-7-1', { level: '國中7', inGsat: 'background' }),
    code('math:FX-10-1', { dependsOn: ['math:FX-7-1'] }),
    code('math:FX-11-1', { level: '11A', dependsOn: ['math:FX-10-1'] }),
    code('math:FX-11A-1', { level: '11A', gsatTrack: 'A', dependsOn: ['math:FX-11-1'] }),
    code('math:FX-11B-1', { level: '11B', gsatTrack: 'B' }),
    code('math:FX-12-1', { level: '選修', inGsat: 'no', gsatTrack: 'none', marks: ['※'] }),
    code('nat:FX-PH-1', { subjects: ['physics'], dependsOn: ['math:FX-10-1'] }),
  ];
}

export const lookupsFor = (codes: CodeEntry[]) => {
  const map = new Map(codes.map((c) => [c.key, c]));
  return { getCode: (k: string) => map.get(k), getTerm: (id: string) => FIXTURE_TERMS.get(id) };
};

export function fixtureRegistry() {
  const sources = new Map<string, SourceDef>([
    ['fx-source', { id: 'fx-source', title: 'Fixture source', url: 'https://example.org/fx', publisher: 'Fixture', kind: 'web', licence: 'fx-licence', accessed: '2026-11-15' }],
    ['fx-uncited', { id: 'fx-uncited', title: 'Uncited source', url: 'https://example.org/uncited', publisher: 'Fixture', kind: 'web', licence: 'fx-licence', accessed: '2026-11-15' }],
  ]);
  const licences = new Map<string, LicenceDef>([
    ['fx-licence', { id: 'fx-licence', name: 'Fixture licence', mayQuote: 'short', mayModify: false, mayRehost: false, attributionRequired: true, nonCommercialOnly: false }],
  ]);
  const examItems = new Set(['fx-item']);
  const misconceptions = new Set(['math.fx-misconception']);
  return {
    sources,
    licences,
    getSource: (id: string) => sources.get(id),
    hasLicence: (id: string) => licences.has(id),
    hasExamItem: (id: string) => examItems.has(id),
    hasMisconception: (id: string) => misconceptions.has(id),
  };
}
