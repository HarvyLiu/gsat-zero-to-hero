/**
 * Marks the first <Term t="…"> of each id in a document with `first`, in document order
 * (including Terms created from [[id]] inside dialogues). On English pages the first use renders
 * "real number（實數）"; later uses render the English only.
 */
import type { Root } from 'mdast';
import { visit } from 'unist-util-visit';

type JsxAttr = { type: string; name?: string; value?: unknown };
type JsxNode = { type: string; name?: string | null; attributes?: JsxAttr[] };

export default function remarkTermFirst() {
  return (tree: Root) => {
    const seen = new Set<string>();
    visit(tree, (node) => {
      const n = node as unknown as JsxNode;
      if ((n.type !== 'mdxJsxTextElement' && n.type !== 'mdxJsxFlowElement') || n.name !== 'Term' || !n.attributes) return;
      const t = n.attributes.find((a) => a.type === 'mdxJsxAttribute' && a.name === 't')?.value;
      if (typeof t !== 'string' || seen.has(t)) return;
      seen.add(t);
      n.attributes.push({ type: 'mdxJsxAttribute', name: 'first', value: null });
    });
  };
}
