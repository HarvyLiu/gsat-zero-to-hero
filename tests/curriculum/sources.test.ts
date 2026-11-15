/**
 * Every chapter is sourced (port of the ASMC sources checks, now against the id-based bibliography in
 * src/data/registry/, read through Builder B's src/data/registry.ts): cited ids exist, are https and
 * carry a known licence; exam-item and misconception references resolve; each subject's 樂詞網 term
 * set is in the bibliography; and every bibliography entry is cited somewhere (a warning until course
 * data exists, then an error).
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { CURRICULUM, SUBJECTS } from '../../src/data/curriculum';
import type { SourceDef } from '../../src/data/schema';
import { build, chapterIn, fixtureCourses, fixtureRegistry, missing, optionalModule } from './fixtures';
import { sourceProblems, uncited, type RegistryLookups } from './rules';

const REGISTRY_FILE = 'src/data/registry.ts';
type RegistryModule = {
  SOURCES: Map<string, SourceDef>;
  LICENCES: Map<string, unknown>;
  getSource(id: string): SourceDef | undefined;
  getExamItem(id: string): unknown;
  getMisconception(id: string): unknown;
};
const registry = await optionalModule<RegistryModule>(REGISTRY_FILE, () => import('../../src/data/registry'));

const SRC = fileURLToPath(new URL('../../src/', import.meta.url));
/** The bibliography itself does not count as citing its own entries. */
const NOT_CITATIONS = new Set(['data/registry/sources.json', 'data/registry/licences.json']);

/**
 * Every source file under src/ (data, components, pages, lessons) as one text. A source id written as a
 * quoted string anywhere ("katex" in an About page credit, a fact's sources list, a <Src id>) is a citation.
 */
function srcText(): string {
  const parts: string[] = [];
  const walk = (d: string) => {
    for (const n of readdirSync(d)) {
      const p = join(d, n);
      if (statSync(p).isDirectory()) walk(p);
      else if (/\.(ts|tsx|astro|mdx|json|ya?ml)$/.test(n) && !NOT_CITATIONS.has(relative(SRC, p).replace(/\\/g, '/'))) parts.push(readFileSync(p, 'utf8'));
    }
  };
  walk(SRC);
  return parts.join('\n');
}
const quotedIn = (text: string, id: string) => text.includes(`"${id}"`) || text.includes(`'${id}'`);

describe.skipIf(!registry)(`sources of the real outlines${registry ? '' : ` ${missing(REGISTRY_FILE)}`}`, () => {
  const reg: RegistryLookups = {
    getSource: (id) => registry!.getSource(id),
    hasLicence: (id) => registry!.LICENCES.has(id),
    hasExamItem: (id) => registry!.getExamItem(id) !== undefined,
    hasMisconception: (id) => registry!.getMisconception(id) !== undefined,
  };

  it('cites only known https sources with known licences, and only registered exam items and misconceptions', () => {
    expect(sourceProblems(CURRICULUM, reg)).toEqual([]);
  });

  it('lists only https sources in the bibliography', () => {
    expect([...registry!.SOURCES.values()].filter((s) => !/^https:\/\//.test(s.url)).map((s) => `${s.id}: ${s.url}`)).toEqual([]);
  });

  it('has a bibliography entry for each subject’s 樂詞網 term set', () => {
    expect(SUBJECTS.filter((s) => s.termSource && !registry!.getSource(s.termSource)).map((s) => `${s.id}: ${s.termSource}`)).toEqual([]);
  });

  it('cites every bibliography entry somewhere (a warning until every subject has an outline)', () => {
    const text = srcText();
    const cited = new Set(CURRICULUM.chapters.flatMap((c) => c.sources));
    for (const id of registry!.SOURCES.keys()) if (quotedIn(text, id)) cited.add(id);
    const never = uncited(registry!.SOURCES.keys(), cited);
    // the bibliography covers every subject, so it can only be fully cited once every subject has an outline
    const outlined = new Set(CURRICULUM.courses.map((c) => c.subject));
    if (!CURRICULUM.subjects.every((s) => outlined.has(s.id))) {
      if (never.length) process.stderr.write(`[sources] not cited anywhere yet (an error once every subject has an outline): ${never.join(', ')}\n`);
      return;
    }
    expect(never).toEqual([]);
  });
});

describe('sources rules on the fixture', () => {
  const reg = fixtureRegistry();

  it('pass on the good outline', () => {
    expect(sourceProblems(build(fixtureCourses()), reg)).toEqual([]);
  });

  it('report an unknown source, an http source, an unknown licence, exam item and misconception', () => {
    const courses = fixtureCourses();
    chapterIn(courses, 'math/fx-numbers').sources = ['fx-missing'];
    chapterIn(courses, 'site/fx-scoring').examItems = ['fx-missing-item'];
    chapterIn(courses, 'math/fx-real').misconceptions = ['math.fx-missing'];
    reg.sources.set('fx-http', { ...reg.sources.get('fx-source')!, id: 'fx-http', url: 'http://example.org/', licence: 'fx-unknown-licence' });
    chapterIn(courses, 'math/fx-fractions').sources = ['fx-http'];
    expect(sourceProblems(build(courses), reg)).toEqual([
      'site/fx-scoring links unknown exam item fx-missing-item',
      'math/fx-numbers cites unknown source fx-missing',
      'math/fx-fractions cites fx-http, whose URL is not https',
      'math/fx-fractions cites fx-http, whose licence fx-unknown-licence is not in licences.json',
      'math/fx-real lists unknown misconception math.fx-missing',
    ]);
  });

  it('finds bibliography entries nobody cites', () => {
    const cited = new Set(build(fixtureCourses()).chapters.flatMap((c) => c.sources));
    expect(uncited(fixtureRegistry().sources.keys(), cited)).toEqual(['fx-uncited']);
  });

  it('counts a quoted id anywhere in the source tree as a citation, but not a substring of another id', () => {
    expect(quotedIn(`credits: ['katex', "noto-sans-tc"]`, 'katex')).toBe(true);
    expect(quotedIn(`<Src id="phet-historical" />`, 'phet')).toBe(false);
  });
});
