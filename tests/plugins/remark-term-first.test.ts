/**
 * remark-term-first marks the first <Term t> of each id with `first`, in document order, including
 * Terms that remark-dialogue creates from [[id]] (it runs after remark-dialogue, as in astro.config.mjs).
 */
import type { Root } from 'mdast';
import remarkMath from 'remark-math';
import remarkMdx from 'remark-mdx';
import remarkParse from 'remark-parse';
import { unified } from 'unified';
import { describe, expect, it } from 'vitest';
import remarkDialogue from '../../src/plugins/remark-dialogue';
import remarkTermFirst from '../../src/plugins/remark-term-first';

type Node = { type: string; name?: string; attributes?: Array<{ type: string; name: string; value: unknown }>; children?: Node[] };
const all = (n: Node): Node[] => [n, ...(n.children ?? []).flatMap(all)];

function terms(md: string): Array<[string, boolean]> {
  const p = unified().use(remarkParse).use(remarkMath).use(remarkMdx).use(remarkDialogue).use(remarkTermFirst);
  const tree = p.runSync(p.parse(md)) as Root;
  return all(tree as unknown as Node)
    .filter((n) => (n.type === 'mdxJsxTextElement' || n.type === 'mdxJsxFlowElement') && n.name === 'Term')
    .map((n) => {
      const t = n.attributes?.find((a) => a.name === 't')?.value;
      return [typeof t === 'string' ? t : '(expression)', !!n.attributes?.some((a) => a.name === 'first')];
    });
}

describe('remarkTermFirst', () => {
  it('marks only the first use of each id', () => {
    expect(terms('<Term t="math.a">a</Term> and <Term t="math.a">a</Term> and <Term t="math.b">b</Term>.')).toEqual([
      ['math.a', true],
      ['math.a', false],
      ['math.b', true],
    ]);
  });

  it('counts dialogue [[id]] terms in document order', () => {
    const md = '```dialogue\nT: 這是[[math.real-number|實數]]。\n```\n\n之後的 <Term t="math.real-number">實數</Term> 與 <Term t="math.other">其他</Term>。';
    expect(terms(md)).toEqual([
      ['math.real-number', true],
      ['math.real-number', false],
      ['math.other', true],
    ]);
  });

  it('handles flow (block) Terms and ignores non-string t', () => {
    expect(terms('<Term t="math.a">\nblock\n</Term>\n\n<Term t={x}>expr</Term> <Term t="math.a">again</Term>')).toEqual([
      ['math.a', true],
      ['(expression)', false],
      ['math.a', false],
    ]);
  });

  it('leaves other components alone', () => {
    const p = unified().use(remarkParse).use(remarkMdx).use(remarkTermFirst);
    const tree = p.runSync(p.parse('<Zh t="math.a">實數</Zh>')) as unknown as Node;
    expect(all(tree).find((n) => n.name === 'Zh')?.attributes?.map((a) => a.name)).toEqual(['t']);
  });
});
