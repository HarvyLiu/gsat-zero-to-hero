/**
 * remark-dialogue (ported from the ASMC reference test and extended for this site's syntax, plan
 * "Dialogue syntax"): T:/S: and 老師：/學生： tags, full-width colons, （）stage directions,
 * S[mc=…] misconception lines, '>> turn:' gating, inline $math$ reaching rehype-katex,
 * [[id|text]] terms, the localised aria-label and names, and the error on a speakerless first line.
 */
import type { Root } from 'mdast';
import rehypeKatex from 'rehype-katex';
import rehypeStringify from 'rehype-stringify';
import remarkMath from 'remark-math';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import { unified } from 'unified';
import { describe, expect, it } from 'vitest';
import remarkDialogue, { inlineMarkdown, localeFromPath, parseDialogue } from '../../src/plugins/remark-dialogue';

const ZH_FILE = '/site/src/content/lessons/zh-tw/math/real-numbers.mdx';
const EN_FILE = '/site/src/content/lessons/en/math/real-numbers.mdx';
const fence = (body: string) => '```dialogue\n' + body + '\n```\n';

async function html(md: string, path = ZH_FILE, base = '/'): Promise<string> {
  const file = { value: md, path }; // a VFile-compatible object (unified wraps it)
  return String(await unified().use(remarkParse).use(remarkMath).use(remarkDialogue, { base }).use(remarkRehype).use(rehypeKatex).use(rehypeStringify).process(file));
}

/** The mdast after the plugin, to inspect the JSX nodes it creates (DialogueTurn, Term). */
function mdast(md: string, path = ZH_FILE): Root {
  const processor = unified().use(remarkParse).use(remarkDialogue);
  const file = { value: md, path }; // a VFile-compatible object (unified wraps it)
  return processor.runSync(processor.parse(file), file) as Root;
}
type Node = { type: string; name?: string; value?: string; attributes?: Array<{ name: string; value: unknown }>; children?: Node[]; data?: { hProperties?: Record<string, unknown> } };
const all = (n: Node): Node[] => [n, ...(n.children ?? []).flatMap(all)];

describe('parseDialogue', () => {
  it('reads T:/S: role tags, continuations and stage directions', () => {
    expect(
      parseDialogue(`
T: Where does a number live?
S: ...on the number line?
  Maybe?
(The teacher draws a line.)
TEACHER: Close!
student: OK.
`),
    ).toEqual([
      { kind: 'line', speaker: 'teacher', text: 'Where does a number live?' },
      { kind: 'line', speaker: 'student', text: '...on the number line? Maybe?' },
      { kind: 'stage', text: 'The teacher draws a line.' },
      { kind: 'line', speaker: 'teacher', text: 'Close!' },
      { kind: 'line', speaker: 'student', text: 'OK.' },
    ]);
  });

  it('accepts the zh tags and the full-width colon', () => {
    expect(parseDialogue('老師：為什麼？\n學生: 因為……\nT：好。')).toEqual([
      { kind: 'line', speaker: 'teacher', text: '為什麼？' },
      { kind: 'line', speaker: 'student', text: '因為……' },
      { kind: 'line', speaker: 'teacher', text: '好。' },
    ]);
  });

  it('reads full-width （…） stage directions', () => {
    expect(parseDialogue('T: 看這裡。\n（老師在黑板上畫了一條數線。）')[1]).toEqual({ kind: 'stage', text: '老師在黑板上畫了一條數線。' });
  });

  it('marks a misconception line with S[mc=…]', () => {
    expect(parseDialogue('S[mc=math.root-two-is-a-fraction]: √2 是分數吧？')).toEqual([
      { kind: 'line', speaker: 'student', text: '√2 是分數吧？', mc: 'math.root-two-is-a-fraction' },
    ]);
    expect(parseDialogue('學生[mc=math.x]：嗯？')[0]).toMatchObject({ speaker: 'student', mc: 'math.x' });
  });

  it('reads a ">> turn:" pause, with either colon', () => {
    expect(parseDialogue('T: 換你。\n>> turn: q-turn1\n>> turn：q2\nT: 好。').map((l) => l.kind === 'turn' && l.item)).toEqual([false, 'q-turn1', 'q2', false]);
  });

  it('keeps colons that are not speaker tags', () => {
    expect(parseDialogue('S: Note: this has a colon')).toEqual([{ kind: 'line', speaker: 'student', text: 'Note: this has a colon' }]);
    expect(parseDialogue('T: 比例是 1:2。')[0]).toMatchObject({ text: '比例是 1:2。' });
  });

  it('refuses a speakerless first line, an unknown tag first, and a block with no spoken line', () => {
    expect(() => parseDialogue('hello there')).toThrow(/speaker tag/);
    expect(() => parseDialogue('路人：你好')).toThrow(/speaker tag/);
    expect(() => parseDialogue('(only a stage direction)')).toThrow(/at least one spoken line/);
    expect(() => parseDialogue('T: 好。\n>> turn: q1\nno speaker after a turn')).toThrow(/speaker tag/);
  });
});

describe('inlineMarkdown', () => {
  it('handles bold, italics and code', () => {
    expect(inlineMarkdown('a **big** *idea* with `code`').map((n) => n.type)).toEqual(['text', 'strong', 'text', 'emphasis', 'text', 'inlineCode']);
  });
  it('leaves lone asterisks alone', () => {
    expect(inlineMarkdown('2 * 3').every((n) => n.type === 'text')).toBe(true);
  });
  it('turns $…$ into the inlineMath node remark-math would make', () => {
    const [, math] = inlineMarkdown('看 $x^2$。') as unknown as Node[];
    expect(math).toMatchObject({ type: 'inlineMath', value: 'x^2', data: { hName: 'code', hProperties: { className: ['language-math', 'math-inline'] } } });
  });
  it('turns [[id]] and [[id|text]] into <Term t="id">', () => {
    const nodes = inlineMarkdown('這是[[math.real-number|實數]]與[[math.rational-number]]。') as unknown as Node[];
    const terms = nodes.filter((n) => n.type === 'mdxJsxTextElement');
    expect(terms.map((t) => [t.name, t.attributes?.[0], t.children?.map((c) => c.value)])).toEqual([
      ['Term', { type: 'mdxJsxAttribute', name: 't', value: 'math.real-number' }, ['實數']],
      ['Term', { type: 'mdxJsxAttribute', name: 't', value: 'math.rational-number' }, []],
    ]);
  });
});

describe('remarkDialogue', () => {
  it('renders bubbles with avatars and localised names and label (zh-tw)', async () => {
    const out = await html(fence('T: 你好，**同學**。\nS: 老師好！') + '\n之後。');
    expect(out).toContain('<div class="dialogue" role="group" aria-label="對話">');
    expect(out).toContain('class="dlg-line dlg-teacher"');
    expect(out).toContain('src="/characters/student.svg"');
    expect(out).toContain('<span class="dlg-name" data-pagefind-ignore="">老師</span>');
    expect(out).toContain('<strong>同學</strong>');
    expect(out).toContain('<p>之後。</p>');
    expect(out).not.toContain('<pre>');
  });

  it('localises by the lesson path: en files get "Conversation" and English names', async () => {
    const out = await html(fence('T: Hello.\nS: Hi!'), EN_FILE);
    expect(out).toContain('aria-label="Conversation"');
    expect(out).toContain('>Teacher</span>');
    expect(out).toContain('>Student</span>');
    expect(localeFromPath('C:\\site\\src\\content\\lessons\\en\\math\\x.mdx')).toBe('en');
    expect(localeFromPath(ZH_FILE)).toBe('zh-tw');
    expect(localeFromPath(undefined)).toBe('zh-tw');
  });

  it('prefixes avatars with the deploy base', async () => {
    expect(await html(fence('T: Hi.'), EN_FILE, '/repo/')).toContain('src="/repo/characters/teacher.svg"');
    expect(await html(fence('T: Hi.'), EN_FILE, '/repo')).toContain('src="/repo/characters/teacher.svg"');
  });

  it('renders $math$ in a dialogue line through rehype-katex', async () => {
    const out = await html(fence('T: 計算 $x^2 + 1$。'));
    expect(out).toContain('class="katex"');
    expect(out).toMatch(/<annotation encoding="application\/x-tex">x\^2 \+ 1<\/annotation>/);
    expect(out).not.toContain('$x^2');
  });

  it('renders stage directions and misconception lines', async () => {
    const out = await html(fence('S[mc=math.x]: 一定是分數吧？\n（老師搖搖頭。）'));
    expect(out).toContain('class="dlg-line dlg-student dlg-mc" data-mc="math.x"');
    expect(out).toContain('<p class="dlg-stage">老師搖搖頭。</p>');
  });

  it('turns ">> turn:" into <DialogueTurn item> and wraps every later line in .dlg-rest', () => {
    const tree = mdast(fence('T: 先想想看。\n>> turn: q1\nT: 答案是 2。\nS: 原來如此。'));
    const dialogue = tree.children[0] as unknown as Node;
    expect(dialogue.children!.map((c) => c.name ?? c.type)).toEqual(['dialogueLine', 'DialogueTurn', 'dialogueRest']);
    const [, turn, rest] = dialogue.children!;
    expect(turn).toMatchObject({ type: 'mdxJsxFlowElement', name: 'DialogueTurn', attributes: [{ name: 'item', value: 'q1' }] });
    expect(rest.data?.hProperties).toEqual({ className: ['dlg-rest'], dataAfter: 'q1' });
    expect(rest.children!.map((c) => c.type)).toEqual(['dialogueLine', 'dialogueLine']);
  });

  it('keeps the later lines inside .dlg-rest in the HTML', async () => {
    const out = await html(fence('T: 先想想看。\n>> turn: q1\nT: 答案是 2。'));
    expect(out).toMatch(/<div class="dlg-rest" data-after="q1">[\s\S]*答案是 2。/);
    expect(out.indexOf('先想想看')).toBeLessThan(out.indexOf('dlg-rest'));
  });

  it('turns [[id|text]] in a dialogue into a <Term> node', () => {
    const terms = all(mdast(fence('T: 今天談[[math.real-number|實數]]。')) as unknown as Node).filter((n) => n.name === 'Term');
    expect(terms).toHaveLength(1);
    expect(terms[0]).toMatchObject({ type: 'mdxJsxTextElement', attributes: [{ name: 't', value: 'math.real-number' }], children: [{ type: 'text', value: '實數' }] });
  });

  it('fails the build on a block whose first line has no speaker', async () => {
    await expect(html(fence('沒有說話的人。'))).rejects.toThrow(/speaker tag/);
  });

  it('ignores other code blocks', async () => {
    expect(await html('```c\nint x;\n```')).toContain('<pre><code class="language-c">');
  });
});
