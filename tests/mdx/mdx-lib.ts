/**
 * Shared reader for the MDX lint suites: finds lessons under a root laid out like
 * src/content/lessons/<locale>/<subject>/<slug>.mdx, splits the YAML frontmatter, and parses the body
 * with remark-parse + remark-math + remark-mdx (the syntax layer of the real pipeline; no compile step,
 * so the suites stay fast and need no @mdx-js/mdx).
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { z } from 'astro/zod';
import type { Root, RootContent } from 'mdast';
import remarkMath from 'remark-math';
import remarkMdx from 'remark-mdx';
import remarkParse from 'remark-parse';
import { unified } from 'unified';
import { parse as parseYaml } from 'yaml';
import { parseDialogue, type DialogueLine } from '../../src/plugins/remark-dialogue';

export type Locale = 'zh-tw' | 'en';
export const LOCALES: Locale[] = ['zh-tw', 'en'];

/**
 * The lesson frontmatter schema. Mirrors src/content.config.ts (which imports the astro:content
 * virtual module and so cannot be loaded in Vitest); keep the two in step.
 */
const IsoDay = z.union([z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'use YYYY-MM-DD'), z.date()]);
export const Frontmatter = z
  .object({
    title: z.string().min(1),
    description: z.string().min(1),
    goals: z.array(z.string().min(1)).min(1).max(5),
    aha: z.string().min(1),
    minutes: z.number().int().positive(),
    status: z.enum(['draft', 'reviewed', 'published']),
    lastVerified: IsoDay.optional(),
    verifiedAgainst: z.array(z.string().min(1)).optional(),
  })
  .strict();
export type Frontmatter = z.infer<typeof Frontmatter>;

export interface Lesson {
  /** path relative to the corpus root, with forward slashes: 'zh-tw/math/real-numbers.mdx' */
  rel: string;
  locale: Locale;
  subject: string;
  slug: string;
  /** '<subject>/<slug>', the chapter id shared by both locales */
  chapter: string;
  /** parsed frontmatter, or undefined when missing or invalid (see `problems`) */
  fm?: Frontmatter;
  /** raw status, even when the rest of the frontmatter is invalid */
  status?: string;
  problems: string[];
  tree?: Root;
  /** absolute path, when read from disk */
  file?: string;
}

/** Split off YAML frontmatter, replacing it with blank lines so MDX line numbers stay true (from ASMC). */
export function splitFrontmatter(src: string): { yaml: string | null; body: string } {
  const m = /^---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/.exec(src);
  if (!m) return { yaml: null, body: src };
  const lines = m[0].split(/\r?\n/).length - 1;
  return { yaml: m[1], body: '\n'.repeat(lines) + src.slice(m[0].length) };
}

const parser = unified().use(remarkParse).use(remarkMath).use(remarkMdx);

export function parseLesson(rel: string, src: string, file?: string): Lesson {
  const [locale, subject, name, ...extra] = rel.split('/');
  const slug = (name ?? '').replace(/\.mdx$/, '');
  const lesson: Lesson = { rel, locale: locale as Locale, subject, slug, chapter: `${subject}/${slug}`, problems: [], ...(file ? { file } : {}) };
  if (!LOCALES.includes(lesson.locale) || !subject || !name || extra.length) lesson.problems.push(`${rel}: lessons live at <zh-tw|en>/<subject>/<slug>.mdx`);
  const { yaml, body } = splitFrontmatter(src);
  if (yaml === null) lesson.problems.push(`${rel}: no frontmatter block`);
  else {
    try {
      const data = (parseYaml(yaml) ?? {}) as Record<string, unknown>;
      if (typeof data.status === 'string') lesson.status = data.status;
      const r = Frontmatter.safeParse(data);
      if (r.success) lesson.fm = r.data;
      else lesson.problems.push(...r.error.issues.map((i) => `${rel} frontmatter ${i.path.join('.') || '(root)'}: ${i.message}`));
    } catch (e) {
      lesson.problems.push(`${rel}: frontmatter is not valid YAML: ${(e as Error).message}`);
    }
  }
  try {
    lesson.tree = parser.parse(body) as Root;
  } catch (e) {
    const err = e as { line?: number; reason?: string; message?: string };
    lesson.problems.push(`${rel}:${err.line ?? '?'} MDX syntax error: ${err.reason ?? err.message}`);
  }
  return lesson;
}

/** Every .mdx under a corpus root (missing root = no lessons). */
export function readCorpus(root: string): Lesson[] {
  const files: string[] = [];
  const walk = (d: string) => {
    let names: string[];
    try {
      names = readdirSync(d);
    } catch {
      return;
    }
    for (const n of names.sort()) {
      const p = join(d, n);
      if (statSync(p).isDirectory()) walk(p);
      else if (n.endsWith('.mdx')) files.push(p);
    }
  };
  walk(root);
  return files.map((f) => parseLesson(relative(root, f).replace(/\\/g, '/'), readFileSync(f, 'utf8'), f));
}

// ---------- tree helpers ----------

type AnyNode = { type: string; name?: string | null; lang?: string | null; value?: string; children?: AnyNode[]; attributes?: JsxAttr[]; position?: { start: { line: number } } };
type JsxAttr = { type: string; name?: string; value?: unknown };
export type { AnyNode };

export const lineOf = (n: { position?: { start: { line: number } } }) => n.position?.start.line ?? 0;
export const isJsx = (n: AnyNode) => n.type === 'mdxJsxFlowElement' || n.type === 'mdxJsxTextElement';
export const isDialogue = (n: AnyNode) => n.type === 'code' && n.lang === 'dialogue';

/** String value of a JSX attribute, or the string literals inside an expression value ({['q1','q2']}). */
export function attrValues(n: AnyNode, name: string): string[] {
  const a = n.attributes?.find((x) => x.type === 'mdxJsxAttribute' && x.name === name);
  if (!a) return [];
  if (typeof a.value === 'string') return [a.value];
  const expr = (a.value as { value?: string } | null)?.value;
  return expr ? [...expr.matchAll(/(['"`])((?:(?!\1).)*)\1/g)].map((m) => m[2]) : [];
}

/** Top-level blocks that carry content: imports/exports and {/* comments *\/} don't count. */
export function contentBlocks(tree: Root): RootContent[] {
  return tree.children.filter((c) => {
    const n = c as unknown as AnyNode;
    if (n.type === 'mdxjsEsm') return false;
    if (n.type === 'mdxFlowExpression' && /^\s*\/\*[\s\S]*\*\/\s*$/.test(n.value ?? '')) return false;
    return true;
  });
}

export function dialogueLines(n: AnyNode): DialogueLine[] | string {
  try {
    return parseDialogue(n.value ?? '');
  } catch (e) {
    return (e as Error).message;
  }
}

/** Depth-first walk; return false from `enter` to skip a node's children. */
export function walk(node: AnyNode, enter: (n: AnyNode) => boolean | void): void {
  if (enter(node) === false) return;
  for (const c of node.children ?? []) walk(c, enter);
}
