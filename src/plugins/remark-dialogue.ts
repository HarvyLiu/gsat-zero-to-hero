/**
 * Turns fenced ```dialogue blocks into chat-bubble markup (ported from the ASMC reference, extended):
 *
 *   ```dialogue
 *   T: 為什麼 $\sqrt{2}$ 不能寫成分數？
 *   S[mc=math.some-misconception]: 因為小數點後面太長了？
 *   >> turn: q1
 *   T: 先別急，[[math.real-number|實數]]其實……
 *   （老師在黑板上畫了一條數線。）
 *   ```
 *
 * - Speaker tags come from src/data/characters.ts (T/S, TEACHER/STUDENT, 老師/學生); half- or full-width colon.
 * - `S[mc=<id>]:` marks a line where the student voices a documented misconception (registry id).
 * - `>> turn: <itemId>` is a "your turn" pause: it renders <DialogueTurn item>, and every later line is
 *   wrapped in .dlg-rest so a client script can hide it until the reader answers (all lines show without JS).
 *   DialogueTurn and Term are JSX, so dialogue blocks that use them must live in .mdx files.
 * - Lines in (…) or （…） are stage directions. Lines without a speaker continue the previous line.
 * - Inline: **bold**, *italic*, `code`, $math$ (rendered by rehype-katex), [[term-id]] / [[term-id|text]] → <Term>.
 */
import type { Code, Parent, PhrasingContent, Root, RootContent } from 'mdast';
import { visit } from 'unist-util-visit';
import { CHARACTERS, type CharacterId, type Locale } from '../data/characters.ts';

export type DialogueLine =
  | { kind: 'line'; speaker: CharacterId; text: string; mc?: string }
  | { kind: 'stage'; text: string }
  | { kind: 'turn'; item: string };

const TAGS = new Map<string, CharacterId>();
for (const c of Object.values(CHARACTERS)) for (const t of c.tags) TAGS.set(t.toUpperCase(), c.id);

const ID = '[A-Za-z0-9._/-]+';
const SPEAKER_RE = new RegExp(`^([A-Za-z]+|[\\u3400-\\u9fff]{1,8})(?:\\[mc=(${ID})\\])?\\s*[:：]\\s*(.*)$`);
const TURN_RE = new RegExp(`^>>\\s*turn\\s*[:：]\\s*(${ID})\\s*$`);

export function parseDialogue(src: string): DialogueLine[] {
  const out: DialogueLine[] = [];
  for (const raw of src.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    const turn = TURN_RE.exec(line);
    if (turn) {
      out.push({ kind: 'turn', item: turn[1] });
      continue;
    }
    if ((line.startsWith('(') && line.endsWith(')')) || (line.startsWith('（') && line.endsWith('）'))) {
      out.push({ kind: 'stage', text: line.slice(1, -1).trim() });
      continue;
    }
    const m = SPEAKER_RE.exec(line);
    const speaker = m ? TAGS.get(m[1].toUpperCase()) : undefined;
    if (m && speaker) {
      out.push({ kind: 'line', speaker, text: m[3], ...(m[2] ? { mc: m[2] } : {}) });
      continue;
    }
    const last = out[out.length - 1];
    if (last && last.kind !== 'turn') last.text = `${last.text} ${line}`.trim();
    else throw new Error(`Dialogue lines must start with a speaker tag (T: or S:), got "${line}"`);
  }
  if (!out.some((l) => l.kind === 'line')) throw new Error('A dialogue block needs at least one spoken line.');
  return out;
}

const INLINE_RE = /(\$[^$\n]+\$|\[\[[^\]\n]+\]\]|\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*|_[^_\s][^_]*_)/g;

/** Inline markdown for a dialogue line. Math nodes match the shape remark-math produces, so rehype-katex renders them. */
export function inlineMarkdown(text: string): PhrasingContent[] {
  const out: PhrasingContent[] = [];
  for (const part of text.split(INLINE_RE)) {
    if (!part) continue;
    if (part.length > 2 && part.startsWith('$') && part.endsWith('$')) {
      const value = part.slice(1, -1);
      out.push({
        type: 'inlineMath',
        value,
        data: { hName: 'code', hProperties: { className: ['language-math', 'math-inline'] }, hChildren: [{ type: 'text', value }] },
      } as unknown as PhrasingContent);
    } else if (part.startsWith('[[') && part.endsWith(']]')) {
      const [id, label] = part
        .slice(2, -2)
        .split('|')
        .map((s) => s.trim());
      out.push({
        type: 'mdxJsxTextElement',
        name: 'Term',
        attributes: [{ type: 'mdxJsxAttribute', name: 't', value: id }],
        children: label ? [{ type: 'text', value: label }] : [],
      } as unknown as PhrasingContent);
    } else if (part.startsWith('**') && part.endsWith('**') && part.length > 4) out.push({ type: 'strong', children: [{ type: 'text', value: part.slice(2, -2) }] });
    else if (part.startsWith('`') && part.endsWith('`') && part.length > 2) out.push({ type: 'inlineCode', value: part.slice(1, -1) });
    else if ((part.startsWith('*') && part.endsWith('*')) || (part.startsWith('_') && part.endsWith('_'))) {
      if (part.length > 2) out.push({ type: 'emphasis', children: [{ type: 'text', value: part.slice(1, -1) }] });
      else out.push({ type: 'text', value: part });
    } else out.push({ type: 'text', value: part });
  }
  return out;
}

type HNode = { type: string; data: { hName: string; hProperties?: Record<string, unknown> }; children?: unknown[] };
const el = (type: string, hName: string, hProperties: Record<string, unknown>, children?: unknown[]): HNode => ({
  type,
  data: { hName, hProperties },
  ...(children ? { children } : {}),
});

const LABEL: Record<Locale, string> = { 'zh-tw': '對話', en: 'Conversation' };

/** Lessons live in src/content/lessons/<locale>/…; anything else is treated as zh-tw. */
export function localeFromPath(path: string | undefined): Locale {
  return path && /[\\/]lessons[\\/]en[\\/]/.test(path) ? 'en' : 'zh-tw';
}

export function dialogueNode(lines: DialogueLine[], locale: Locale = 'zh-tw', base = '/'): RootContent {
  const root = base.endsWith('/') ? base : `${base}/`;
  const render = (from: number): unknown[] => {
    const nodes: unknown[] = [];
    for (let i = from; i < lines.length; i++) {
      const l = lines[i];
      if (l.kind === 'turn') {
        nodes.push({ type: 'mdxJsxFlowElement', name: 'DialogueTurn', attributes: [{ type: 'mdxJsxAttribute', name: 'item', value: l.item }], children: [] });
        nodes.push(el('dialogueRest', 'div', { className: ['dlg-rest'], dataAfter: l.item }, render(i + 1)));
        return nodes;
      }
      if (l.kind === 'stage') {
        nodes.push(el('paragraph', 'p', { className: ['dlg-stage'] }, inlineMarkdown(l.text)));
        continue;
      }
      nodes.push(
        el('dialogueLine', 'div', { className: ['dlg-line', `dlg-${l.speaker}`, ...(l.mc ? ['dlg-mc'] : [])], ...(l.mc ? { dataMc: l.mc } : {}) }, [
          el('dialogueAvatar', 'img', { className: ['dlg-avatar'], src: `${root}characters/${l.speaker}.svg`, alt: '', width: 52, height: 52, loading: 'lazy' }),
          el('dialogueBubble', 'div', { className: ['dlg-bubble'] }, [
            el('dialogueName', 'span', { className: ['dlg-name'], dataPagefindIgnore: '' }, [{ type: 'text', value: CHARACTERS[l.speaker].name[locale] }]),
            { type: 'paragraph', children: inlineMarkdown(l.text) },
          ]),
        ]),
      );
    }
    return nodes;
  };
  return el('dialogue', 'div', { className: ['dialogue'], role: 'group', ariaLabel: LABEL[locale] }, render(0)) as unknown as RootContent;
}

export default function remarkDialogue(options: { base?: string; locale?: Locale } = {}) {
  const base = options.base ?? '/';
  return (tree: Root, file?: { path?: string; history?: string[] }) => {
    const locale = options.locale ?? localeFromPath(file?.path ?? file?.history?.[0]);
    const hits: Array<{ parent: Parent; node: Code }> = [];
    visit(tree, 'code', (node: Code, _index, parent) => {
      if (node.lang === 'dialogue' && parent) hits.push({ parent: parent as Parent, node });
    });
    for (const { parent, node } of hits) {
      const i = parent.children.indexOf(node);
      if (i >= 0) parent.children.splice(i, 1, dialogueNode(parseDialogue(node.value), locale, base));
    }
  };
}
