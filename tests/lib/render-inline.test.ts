import { describe, expect, it } from 'vitest';
import { escapeHtml, renderInline } from '../../src/lib/render-inline';

describe('renderInline', () => {
  it('escapes HTML in plain text', () => {
    expect(renderInline('a < b & "c" > \'d\'')).toBe('a &lt; b &amp; &quot;c&quot; &gt; &#39;d&#39;');
    expect(renderInline('<script>alert(1)</script>')).not.toContain('<script>');
    expect(escapeHtml('<&>')).toBe('&lt;&amp;&gt;');
  });

  it('renders bold, italic and code', () => {
    expect(renderInline('**粗體**與*斜體*')).toBe('<strong>粗體</strong>與<em>斜體</em>');
    expect(renderInline('run `a<b`')).toBe('run <code>a&lt;b</code>');
    expect(renderInline('*x*')).toBe('<em>x</em>');
    expect(renderInline('`**not bold**`')).toBe('<code>**not bold**</code>');
  });

  it('renders inline math with KaTeX (a fraction)', () => {
    const html = renderInline('求 $\\frac{1}{2}+\\frac{1}{3}$ 的值。');
    expect(html.startsWith('求 <span class="katex">')).toBe(true);
    expect(html).toContain('mfrac'); // MathML fraction
    expect(html).toContain('frac-line'); // HTML fraction bar
    expect(html.endsWith(' 的值。')).toBe(true);
  });

  it('renders display math', () => {
    expect(renderInline('$$x^2 = 4$$')).toContain('katex-display');
  });

  it('has mhchem: \\ce{H2O}', () => {
    const html = renderInline('水是 $\\ce{H2O}$。');
    expect(html).toContain('class="katex"');
    // the subscript 2 is set as a lowered digit, not the literal text "H2O"
    expect(html).toContain('msub');
    expect(html).toContain('<mi mathvariant="normal">H</mi>'); // upright element symbol
    // the TeX source survives only in the MathML annotation, never as visible text
    expect(html.split('\\ce').length - 1).toBe(1);
    expect(html).toContain('<annotation encoding="application/x-tex">\\ce{H2O}</annotation>');
  });

  it('keeps emphasis around math and math inside emphasis', () => {
    const html = renderInline('**若 $x>0$**');
    expect(html.startsWith('<strong>若 <span class="katex">')).toBe(true);
    expect(html.endsWith('</strong>')).toBe(true);
  });

  it('turns newlines into line breaks and trims', () => {
    expect(renderInline('  一\n二\r\n三  ')).toBe('一<br>二<br>三');
  });

  it('supports escapes for literal $, * and `', () => {
    expect(renderInline('costs \\$5 and 2 \\* 3 \\`')).toBe('costs $5 and 2 * 3 `');
  });

  it('fails loudly on bad TeX, unclosed delimiters and stray asterisks', () => {
    expect(() => renderInline('$\\frac{1}{$')).toThrow(/bad TeX/);
    expect(() => renderInline('$\\notacommand$')).toThrow(/bad TeX/);
    expect(() => renderInline('price $5')).toThrow(/unclosed \$/);
    expect(() => renderInline('`open')).toThrow(/unclosed/);
    expect(() => renderInline('2 * 3')).toThrow(/unmatched \*/);
    expect(() => renderInline('$$ $$')).toThrow(/empty math/);
  });

  it('rejects CJK text in math mode unless it is inside \\text{}', () => {
    expect(() => renderInline('$面積=3$')).toThrow(/bad TeX/);
    expect(renderInline('$\\text{面積}=3$')).toContain('katex');
  });
});
