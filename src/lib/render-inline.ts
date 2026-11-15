/**
 * Build-time renderer for the short texts in item banks (stems, options, hints, explanations).
 * It handles a deliberately small inline subset, so the output is predictable and pages ship no KaTeX JS:
 *   **bold**, *italic*, `code`, $inline math$, $$display math$$, a line break per newline,
 *   and the escapes \$ \* \` \\ for literal characters.
 * Math goes through katex.renderToString with throwOnError: a bad TeX string throws here, so the build
 * and tests/lib/render-inline.test.ts fail instead of shipping red error text. mhchem (\ce, \pu) is loaded
 * for chemistry. Everything outside math and code is HTML-escaped.
 * Server-only: never import this from an island (it would pull KaTeX into the client bundle).
 */
import katex from 'katex';
// Registers \ce and \pu on the same KaTeX instance (the contrib module imports ../katex.mjs).
import 'katex/contrib/mhchem';

const ESC: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ESC[c]);
}

// Private-use code points mark where rendered fragments go back in, after emphasis is applied to the text.
const OPEN = '';
const CLOSE = '';

function renderMath(tex: string, displayMode: boolean, source: string): string {
  try {
    return katex.renderToString(tex, {
      displayMode,
      throwOnError: true,
      output: 'htmlAndMathml',
      // CJK or other text in math mode must go inside \text{…}; everything else KaTeX merely warns about.
      strict: (code: string) => (code === 'unicodeTextInMathMode' ? 'error' : 'warn'),
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    throw new Error(`renderInline: bad TeX ${JSON.stringify(tex)} in ${JSON.stringify(source)}: ${msg}`);
  }
}

const cache = new Map<string, string>();

/** Inline markdown + $math$ → an HTML string (safe to set as innerHTML; contains no block elements). */
export function renderInline(markdown: string): string {
  const hit = cache.get(markdown);
  if (hit !== undefined) return hit;
  if (markdown.includes(OPEN) || markdown.includes(CLOSE)) throw new Error('renderInline: text contains reserved private-use characters U+E000/U+E001');

  const parts: string[] = [];
  const hold = (html: string) => `${OPEN}${parts.push(html) - 1}${CLOSE}`;
  const src = markdown.replace(/\r\n?/g, '\n').trim();
  let text = '';
  let i = 0;
  while (i < src.length) {
    const c = src[i];
    if (c === '\\' && i + 1 < src.length && '$*`\\'.includes(src[i + 1])) {
      text += hold(escapeHtml(src[i + 1]));
      i += 2;
    } else if (c === '`') {
      const end = src.indexOf('`', i + 1);
      if (end < 0) throw new Error(`renderInline: unclosed \` in ${JSON.stringify(markdown)}`);
      text += hold(`<code>${escapeHtml(src.slice(i + 1, end))}</code>`);
      i = end + 1;
    } else if (c === '$') {
      const display = src[i + 1] === '$';
      const open = display ? 2 : 1;
      const end = findMathEnd(src, i + open, display);
      if (end < 0) throw new Error(`renderInline: unclosed ${display ? '$$' : '$'} in ${JSON.stringify(markdown)} (write \\$ for a dollar sign)`);
      const tex = src.slice(i + open, end).trim();
      if (!tex) throw new Error(`renderInline: empty math in ${JSON.stringify(markdown)}`);
      text += hold(renderMath(tex, display, markdown));
      i = end + open;
    } else {
      text += c;
      i++;
    }
  }

  let html = escapeHtml(text)
    .replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(?=[^\s*])([^*]*?[^\s*])\*|\*([^\s*])\*/g, (_m, a: string | undefined, b: string | undefined) => `<em>${a ?? b}</em>`)
    .replace(/\n/g, '<br>');
  // Escaped and code/math asterisks are held as placeholders, so any '*' left over is unbalanced emphasis.
  if (html.includes('*')) {
    throw new Error(`renderInline: unmatched * in ${JSON.stringify(markdown)} (write \\* for an asterisk)`);
  }
  html = html.replace(new RegExp(`${OPEN}(\\d+)${CLOSE}`, 'g'), (_m, n: string) => parts[Number(n)]);
  cache.set(markdown, html);
  return html;
}

/** Index of the closing delimiter, skipping \$ inside the TeX. */
function findMathEnd(src: string, from: number, display: boolean): number {
  for (let j = from; j < src.length; j++) {
    if (src[j] === '\\') {
      j++;
      continue;
    }
    if (src[j] === '$') {
      if (!display) return j;
      if (src[j + 1] === '$') return j;
    }
  }
  return -1;
}
