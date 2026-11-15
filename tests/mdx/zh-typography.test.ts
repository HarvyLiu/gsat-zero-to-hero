/**
 * Typography lint (docs/design/05-platform.md §6 zh-typography and §7 authoring conventions; critic §1
 * item 18: the en-lint has an allow-list of zh components).
 *  - zh-tw prose (outside code, math, JSX attributes other than prose props, and frontmatter) must use
 *    full-width ，；：？！ next to Chinese text, and 「」 rather than "…" or “…”.
 *  - en prose must not contain Chinese characters outside <Term>, <Zh>, the allowed zh components,
 *    dialogue [[…]] terms, math and code.
 * Dialogue fences are prose too: their speaker tags are syntax and are stripped first.
 */
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { isDialogue, isJsx, lineOf, readCorpus, walk, type AnyNode, type Lesson } from './mdx-lib';

const REAL = fileURLToPath(new URL('../../src/content/lessons/', import.meta.url));
const GOOD = fileURLToPath(new URL('../fixtures/mdx/good/', import.meta.url));
const BAD = fileURLToPath(new URL('../fixtures/mdx/bad/', import.meta.url));

const HAN = '\\p{Script=Han}';
const ASCII_PUNCT = new RegExp(`(?<=${HAN}\\s*)[,;:?!]|[,;:?!](?=\\s*${HAN})`, 'gu');
const QUOTES = /["“”]/;
const HAN_RUN = new RegExp(`${HAN}+`, 'gu');

/** Attributes whose value is prose shown to the reader (StudentAsks q, Predict prompt, …). */
const PROSE_ATTRS = new Set(['q', 'title', 'prompt', 'caption', 'label', 'alt']);
/** Components that hold Chinese on purpose on EN pages: terms, quotes, exam Chinese, classical texts. */
const EN_ZH_ALLOWED = new Set(['Term', 'Zh', 'ExamChinese', 'Quote', 'LawQuote', 'SourceCard', 'ClassicalText', 'MoeDict']);
/** Never prose: code, math and MDX expressions. */
const SKIP = new Set(['code', 'inlineCode', 'math', 'inlineMath', 'mdxjsEsm', 'mdxFlowExpression', 'mdxTextExpression']);

const SPEAKER = /^\s*(?:[A-Za-z]+|[㐀-鿿]{1,8})(?:\[mc=[^\]]*\])?\s*[:：]\s*/;
const stripInline = (s: string, termText: 'keep' | 'drop') =>
  s
    .replace(/\$[^$\n]+\$/g, ' ')
    .replace(/`[^`]+`/g, ' ')
    .replace(/\[\[([^\]|]+)(?:\|([^\]]*))?\]\]/g, (_m, _id: string, label?: string) => (termText === 'keep' ? (label ?? '') : ' '));

interface Prose {
  text: string;
  line: number;
}

/** The reader-visible prose of a lesson, line by line where it matters. */
function proseOf(l: Lesson): Prose[] {
  const out: Prose[] = [];
  if (!l.tree) return out;
  const en = l.locale === 'en';
  const pushLines = (text: string, line: number) => text.split(/\r?\n/).forEach((t, i) => out.push({ text: t, line: line + i }));
  walk(l.tree as unknown as AnyNode, (n) => {
    if (isDialogue(n)) {
      (n.value ?? '').split(/\r?\n/).forEach((raw, i) => {
        if (/^\s*>>\s*turn/.test(raw)) return;
        out.push({ text: stripInline(raw.replace(SPEAKER, ''), en ? 'drop' : 'keep'), line: lineOf(n) + 1 + i });
      });
      return false;
    }
    if (SKIP.has(n.type)) return false;
    if (isJsx(n)) {
      if (en && n.name && EN_ZH_ALLOWED.has(n.name)) return false;
      for (const a of n.attributes ?? []) if (a.type === 'mdxJsxAttribute' && a.name && PROSE_ATTRS.has(a.name) && typeof a.value === 'string') out.push({ text: stripInline(a.value, 'keep'), line: lineOf(n) });
      return;
    }
    if (n.type === 'text' && n.value) pushLines(n.value, lineOf(n));
  });
  return out;
}

function zhTypography(l: Lesson): string[] {
  const out = new Set<string>();
  for (const p of proseOf(l)) {
    for (const m of p.text.matchAll(ASCII_PUNCT)) out.add(`${l.rel}:${p.line} ASCII "${m[0]}" next to Chinese text; use the full-width form`);
    if (QUOTES.test(p.text)) out.add(`${l.rel}:${p.line} quotation marks "…" or “…” in Chinese prose; use 「」`);
  }
  return [...out];
}

function enHan(l: Lesson): string[] {
  const out = new Set<string>();
  for (const p of proseOf(l)) for (const m of p.text.matchAll(HAN_RUN)) out.add(`${l.rel}:${p.line} Chinese "${m[0]}" outside <Term>, <Zh>, an allowed zh component, a dialogue [[term]] or math`);
  return [...out];
}

const lint = (lessons: Lesson[]) => lessons.flatMap((l) => (l.locale === 'en' ? enHan(l) : zhTypography(l)));

describe('typography of the real lessons', () => {
  const lessons = readCorpus(REAL);
  it(`zh-tw prose uses full-width punctuation and 「」; en prose keeps Chinese inside the allowed places (${lessons.length} file(s))`, () => {
    expect(lint(lessons)).toEqual([]);
  });
});

describe('typography lint on fixtures', () => {
  it('passes the good fixtures (code, math, frontmatter, ids and allowed components are exempt)', () => {
    expect(lint(readCorpus(GOOD))).toEqual([]);
  });

  it('flags ASCII punctuation and quotes in zh-tw prose, dialogue lines and prose attributes', () => {
    const zh = readCorpus(BAD).find((l) => l.rel === 'zh-tw/math/zh-punct.mdx')!;
    const f = 'zh-tw/math/zh-punct.mdx';
    expect(zhTypography(zh)).toEqual([
      `${f}:12 ASCII "," next to Chinese text; use the full-width form`,
      `${f}:16 ASCII "," next to Chinese text; use the full-width form`,
      `${f}:18 ASCII "?" next to Chinese text; use the full-width form`,
      `${f}:20 ASCII ":" next to Chinese text; use the full-width form`,
      `${f}:22 ASCII "!" next to Chinese text; use the full-width form`,
      `${f}:24 ASCII ";" next to Chinese text; use the full-width form`,
      `${f}:26 quotation marks "…" or “…” in Chinese prose; use 「」`,
      `${f}:28 quotation marks "…" or “…” in Chinese prose; use 「」`,
      `${f}:32 ASCII "?" next to Chinese text; use the full-width form`,
    ]);
  });

  it('flags Chinese in en prose, dialogue lines and prose attributes, but not in Term, Zh, ExamChinese, [[…]], math or code', () => {
    const en = readCorpus(BAD).find((l) => l.rel === 'en/math/en-han.mdx')!;
    const f = 'en/math/en-han.mdx';
    expect(enHan(en)).toEqual([
      `${f}:12 Chinese "實數" outside <Term>, <Zh>, an allowed zh component, a dialogue [[term]] or math`,
      `${f}:16 Chinese "實數" outside <Term>, <Zh>, an allowed zh component, a dialogue [[term]] or math`,
      `${f}:18 Chinese "什麼是實數" outside <Term>, <Zh>, an allowed zh component, a dialogue [[term]] or math`,
    ]);
  });

  it('finds nothing else in the bad fixtures', () => {
    const rest = readCorpus(BAD).filter((l) => l.rel !== 'zh-tw/math/zh-punct.mdx' && l.rel !== 'en/math/en-han.mdx');
    expect(lint(rest)).toEqual([]);
  });
});
