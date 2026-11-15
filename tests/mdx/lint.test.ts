/**
 * Lesson MDX lint (docs/design/05-platform.md §6 mdx + locale-parity; plan: "a short teacher–student
 * dialogue opens and closes every chapter"; EN is an adaptation that may not add or drop any item).
 * Runs over src/content/lessons (none may exist yet) and over tests/fixtures/mdx/{good,bad}, which
 * prove each rule passes and fires.
 */
import { existsSync, statSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { CURRICULUM, type Curriculum } from '../../src/data/curriculum';
import { MINUTES_CAP } from '../../src/data/schema';
import { build, fixtureCourses } from '../curriculum/fixtures';
import { attrValues, contentBlocks, dialogueLines, isDialogue, isJsx, lineOf, readCorpus, walk, type AnyNode, type Lesson } from './mdx-lib';

const REAL = fileURLToPath(new URL('../../src/content/lessons/', import.meta.url));
const GOOD = fileURLToPath(new URL('../fixtures/mdx/good/', import.meta.url));
const BAD = fileURLToPath(new URL('../fixtures/mdx/bad/', import.meta.url));

/** Components whose ids must match across locales, and the attribute that carries the id. */
const ID_ATTRS: Record<string, string> = {
  Quiz: 'items',
  DialogueTurn: 'item',
  Predict: 'id',
  PredictIsland: 'id',
  Fact: 'id',
  OnTheExam: 'item',
  Misconception: 'id',
  ExamItem: 'item',
  Exercise: 'id',
  WorkedExample: 'id',
};

const EXTS = ['', '.astro', '.tsx', '.ts', '.jsx', '.js', '.mdx', '.json', '.css'];

/** Relative imports that resolve to no file (ported from the ASMC mdx test; real lessons only). */
function brokenImports(l: Lesson): string[] {
  if (!l.tree || !l.file) return [];
  const out: string[] = [];
  for (const n of l.tree.children as unknown as AnyNode[]) {
    if (n.type !== 'mdxjsEsm') continue;
    for (const m of (n.value ?? '').matchAll(/\bfrom\s+['"]([^'"]+)['"]|^\s*import\s+['"]([^'"]+)['"]/gm)) {
      const spec = m[1] ?? m[2];
      if (!spec.startsWith('.')) continue;
      const base = resolve(dirname(l.file), spec);
      if (!EXTS.some((e) => existsSync(base + e) && statSync(base + e).isFile())) out.push(`${l.rel}:${lineOf(n)} cannot resolve import "${spec}"`);
    }
  }
  return out;
}

/** Per file: frontmatter shape, MDX syntax, dialogue blocks that parse, and the opening and closing dialogue. */
function lintFile(l: Lesson): string[] {
  const out = [...l.problems];
  if (!l.tree) return out;
  walk(l.tree as unknown as AnyNode, (n) => {
    if (!isDialogue(n)) return;
    const lines = dialogueLines(n);
    if (typeof lines === 'string') out.push(`${l.rel}:${lineOf(n)} dialogue block does not parse: ${lines}`);
  });
  const blocks = contentBlocks(l.tree) as unknown as AnyNode[];
  if (!blocks.length) out.push(`${l.rel}: the lesson is empty`);
  // '_name' files are internal pages (content.config.ts: e.g. the component style check), not lessons.
  else if (!l.slug.startsWith('_')) {
    if (!isDialogue(blocks[0])) out.push(`${l.rel}:${lineOf(blocks[0])} does not open with a \`\`\`dialogue block (found ${blocks[0].name ?? blocks[0].type})`);
    const last = blocks[blocks.length - 1];
    if (!isDialogue(last)) out.push(`${l.rel}:${lineOf(last)} does not close with a \`\`\`dialogue block (found ${last.name ?? last.type})`);
  }
  return out;
}

/** The ordered interactive ids of a lesson: component ids, dialogue turns and misconception lines. */
function interactiveIds(l: Lesson): string[] {
  const ids: string[] = [];
  if (!l.tree) return ids;
  walk(l.tree as unknown as AnyNode, (n) => {
    if (isDialogue(n)) {
      const lines = dialogueLines(n);
      if (typeof lines !== 'string')
        for (const d of lines) {
          if (d.kind === 'turn') ids.push(`DialogueTurn:${d.item}`);
          if (d.kind === 'line' && d.mc) ids.push(`mc:${d.mc}`);
        }
      return false;
    }
    if (isJsx(n) && n.name && ID_ATTRS[n.name]) for (const v of attrValues(n, ID_ATTRS[n.name])) ids.push(`${n.name === 'PredictIsland' ? 'Predict' : n.name}:${v}`);
  });
  return ids;
}

const dialogueCount = (l: Lesson) => {
  let n = 0;
  if (l.tree) walk(l.tree as unknown as AnyNode, (x) => void (isDialogue(x) && n++));
  return n;
};
const isDraft = (l: Lesson) => l.status === 'draft';

/** Across locales: mirrors exist for non-draft lessons; non-draft pairs match item for item. */
function lintPairs(lessons: Lesson[]): string[] {
  const out: string[] = [];
  const by = new Map(lessons.map((l) => [`${l.locale}/${l.chapter}`, l]));
  for (const l of lessons) {
    const other = l.locale === 'zh-tw' ? 'en' : 'zh-tw';
    const mirror = by.get(`${other}/${l.chapter}`);
    if (!mirror) {
      if (!isDraft(l)) out.push(`${l.rel} (${l.status}) has no ${other} mirror`);
      continue;
    }
    if (l.locale !== 'zh-tw' || isDraft(l) || isDraft(mirror)) continue; // compare each non-draft pair once
    const [a, b] = [interactiveIds(l), interactiveIds(mirror)];
    if (a.join('\n') !== b.join('\n')) out.push(`${l.chapter}: interactive ids differ between locales\n  zh-tw: ${a.join(', ')}\n  en:    ${b.join(', ')}`);
    const [da, db] = [dialogueCount(l), dialogueCount(mirror)];
    if (da !== db) out.push(`${l.chapter}: ${da} dialogue blocks in zh-tw but ${db} in en`);
    if (l.fm && mirror.fm && l.fm.minutes !== mirror.fm.minutes) out.push(`${l.chapter}: minutes differ (zh-tw ${l.fm.minutes}, en ${mirror.fm.minutes})`);
  }
  return out;
}

/** Against the outline: a non-draft lesson is a chapter of the outline; minutes stay within the kind's cap. */
function lintAgainstOutline(lessons: Lesson[], cur: Curriculum): string[] {
  const out = new Set<string>();
  for (const l of lessons) {
    const ch = cur.chapterById(l.chapter);
    if (!ch) {
      // '_name' files are internal pages (e.g. a style check), never chapters.
      if (!isDraft(l) && !l.slug.startsWith('_')) out.add(`${l.chapter}: a ${l.status} lesson that is not a chapter in the outline`);
      continue;
    }
    const cap = MINUTES_CAP[ch.kind];
    if (l.fm && cap !== null && l.fm.minutes > cap) out.add(`${l.rel} runs ${l.fm.minutes} min; a ${ch.kind} chapter is capped at ${cap}`);
  }
  return [...out];
}

const lintAll = (lessons: Lesson[], cur: Curriculum) => [...lessons.flatMap(lintFile), ...lintPairs(lessons), ...lintAgainstOutline(lessons, cur)];

describe('lesson MDX (src/content/lessons)', () => {
  const lessons = readCorpus(REAL);
  it(`reads ${lessons.length} lesson file(s)`, () => expect(lessons.length).toBeGreaterThanOrEqual(0));
  it('passes every lint rule', () => expect(lintAll(lessons, CURRICULUM)).toEqual([]));
  it('imports only files that exist', () => expect(lessons.flatMap(brokenImports)).toEqual([]));
});

describe('lesson MDX lint on fixtures', () => {
  const cur = build(fixtureCourses());

  it('passes the good fixtures', () => {
    const lessons = readCorpus(GOOD);
    expect(lessons.map((l) => l.rel)).toEqual(['en/math/fx-real.mdx', 'zh-tw/math/fx-real.mdx', 'zh-tw/site/_internal.mdx', 'zh-tw/site/welcome.mdx']);
    expect(lintAll(lessons, cur)).toEqual([]);
  });

  it('resolves relative imports, and reports one that points nowhere', () => {
    expect(readCorpus(GOOD).flatMap(brokenImports)).toEqual([]);
    expect(readCorpus(BAD).flatMap(brokenImports)).toEqual(['zh-tw/math/no-close.mdx:11 cannot resolve import "./does-not-exist.astro"']);
  });

  it('reads the interactive ids in document order, including dialogue turns and misconception lines', () => {
    const zh = readCorpus(GOOD).find((l) => l.rel === 'zh-tw/math/fx-real.mdx')!;
    expect(interactiveIds(zh)).toEqual([
      'mc:math.fx-misconception',
      'DialogueTurn:q-turn',
      'Predict:p1',
      'Misconception:math.fx-misconception',
      'Quiz:q1',
      'Quiz:q2',
      'Fact:site.fx-fact',
      'OnTheExam:115-mathA-q1',
    ]);
  });

  it('fires every rule on the bad fixtures, and nothing else', () => {
    const got = lintAll(readCorpus(BAD), cur);
    const expected: RegExp[] = [
      /^zh-tw\/math\/bad-frontmatter\.mdx frontmatter goals: /,
      /^zh-tw\/math\/bad-frontmatter\.mdx frontmatter aha: /,
      /^zh-tw\/math\/bad-frontmatter\.mdx frontmatter minutes: /,
      /^zh-tw\/math\/bad-frontmatter\.mdx frontmatter lastVerified: /,
      /^zh-tw\/math\/bad-frontmatter\.mdx frontmatter \(root\): .*author/,
      /^zh-tw\/math\/no-open\.mdx:\d+ does not open with a ```dialogue block \(found paragraph\)$/,
      /^zh-tw\/math\/no-close\.mdx:\d+ does not close with a ```dialogue block \(found Quiz\)$/,
      /^zh-tw\/math\/bad-dialogue\.mdx:\d+ dialogue block does not parse: Dialogue lines must start with a speaker tag/,
      /^zh-tw\/math\/no-mirror\.mdx \(reviewed\) has no en mirror$/,
      /^en\/math\/en-only\.mdx \(published\) has no zh-tw mirror$/,
      /^math\/mismatch: interactive ids differ between locales\n {2}zh-tw: DialogueTurn:t1, Quiz:q1, Quiz:q2, Fact:civics\.fx-fact\n {2}en: {4}DialogueTurn:t1, Quiz:q1, Quiz:q3$/,
      /^math\/mismatch: 3 dialogue blocks in zh-tw but 2 in en$/,
      /^math\/mismatch: minutes differ \(zh-tw 20, en 25\)$/,
      /^math\/(mismatch|no-mirror|en-only): a (reviewed|published) lesson that is not a chapter in the outline$/,
      /^zh-tw\/math\/fx-toolbox\.mdx runs 20 min; a toolbox chapter is capped at 15$/,
    ];
    const unmatched = expected.filter((re) => !got.some((g) => re.test(g))).map(String);
    const unexpected = got.filter((g) => !expected.some((re) => re.test(g)));
    expect({ unmatched, unexpected }).toEqual({ unmatched: [], unexpected: [] });
    expect(got.filter((g) => / not a chapter in the outline$/.test(g))).toHaveLength(3);
  });
});
