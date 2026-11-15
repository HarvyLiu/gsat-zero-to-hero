/**
 * The paper grid stays exactly as the ASMC reference has it now (plan, Platform: "Paper grid: thin
 * lines only … There are no --grid-major or --scene-grid-major tokens. A token test fails if a
 * major/heavy grid layer is reintroduced."):
 *  - the page grid is one fixed body::before layer: two 1px var(--grid-minor) gradients at 24px 24px;
 *  - .scene-paper draws one var(--scene-grid) tile at 34.64px 20px;
 *  - no stylesheet defines or uses any other grid token or draws grid lines anywhere else.
 */
import { readdirSync, readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const DIR = new URL('../../src/styles/', import.meta.url);
const strip = (css: string) => css.replace(/\/\*[\s\S]*?\*\//g, '');
const FILES = readdirSync(DIR)
  .filter((f) => f.endsWith('.css'))
  .sort()
  .map((f) => ({ file: f, css: strip(readFileSync(new URL(f, DIR), 'utf8')) }));

/** The only grid tokens the site may have. */
const GRID_TOKENS = new Set(['--grid-minor', '--scene-grid']);

/** Declarations of the first rule whose selector is exactly `selector`. */
function rule(css: string, selector: string): Record<string, string> {
  const re = new RegExp(`(?:^|[}\\s])${selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*\\{([^}]*)\\}`);
  const m = re.exec(css);
  if (!m) throw new Error(`no rule for ${selector}`);
  const out: Record<string, string> = {};
  for (const d of m[1].matchAll(/([\w-]+)\s*:\s*([^;]+);?/g)) out[d[1]] = d[2].replace(/\s+/g, ' ').trim();
  return out;
}

/** Every value given to a custom property, per file. */
function definitions(name: string): Array<{ file: string; value: string }> {
  return FILES.flatMap(({ file, css }) => [...css.matchAll(new RegExp(`${name}\\s*:\\s*([^;]+);`, 'g'))].map((m) => ({ file, value: m[1].trim() })));
}

const paper = FILES.find((f) => f.file === 'paper.css')!.css;

describe('one thin, even grid', () => {
  it('has no major or heavier grid token anywhere', () => {
    const bad = FILES.flatMap(({ file, css }) => [...css.matchAll(/--[\w-]*(?:grid[\w-]*major|major[\w-]*grid)[\w-]*/gi)].map((m) => `${file}: ${m[0]}`));
    expect(bad).toEqual([]);
  });

  it('defines no grid token other than --grid-minor and --scene-grid', () => {
    const extra = FILES.flatMap(({ file, css }) => [...css.matchAll(/(--(?:scene-)?grid[\w-]*)\s*:/g)].map((m) => m[1]).filter((n) => !GRID_TOKENS.has(n)).map((n) => `${file}: ${n}`));
    expect(extra).toEqual([]);
  });

  it('draws the page grid on one fixed body::before layer: two 1px --grid-minor lines every 24px', () => {
    const r = rule(paper, 'body::before');
    expect(r['position']).toBe('fixed');
    expect(r['pointer-events']).toBe('none');
    expect(r['z-index']).toBe('-1');
    expect(r['background-image']).toBe('linear-gradient(var(--grid-minor) 1px, transparent 1px), linear-gradient(90deg, var(--grid-minor) 1px, transparent 1px)');
    expect(r['background-size']).toBe('24px 24px, 24px 24px');
    expect(r['background-position']).toBe('-1px -1px');
  });

  it('draws scenes on a single --scene-grid layer', () => {
    const r = rule(paper, '.scene-paper');
    expect(r['background-image']).toBe('var(--scene-grid)');
    expect(r['background-size']).toBe('34.64px 20px');
  });

  it('uses the grid tokens nowhere else', () => {
    const uses = FILES.flatMap(({ file, css }) =>
      [...css.matchAll(/var\((--(?:scene-)?grid[\w-]*)\)/g)].map((m) => `${file}: ${m[1]}`),
    );
    // paper.css: twice in body::before, once in .scene-paper; tokens.css only defines them.
    expect(uses.sort()).toEqual(['paper.css: --grid-minor', 'paper.css: --grid-minor', 'paper.css: --scene-grid']);
  });

  it('keeps every theme’s grid lines faint: --grid-minor alpha ≤ 0.1, one 1px stroke in --scene-grid', () => {
    const minor = definitions('--grid-minor');
    expect(minor.length).toBeGreaterThanOrEqual(2); // light and dark
    for (const { file, value } of minor) {
      const alpha = /rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*([\d.]+)\s*\)/.exec(value);
      expect(alpha, `${file}: --grid-minor must be an rgba() colour, got ${value}`).not.toBeNull();
      expect(Number(alpha![1]), `${file}: --grid-minor ${value}`).toBeLessThanOrEqual(0.1);
    }
    const scene = definitions('--scene-grid');
    expect(scene.length).toBeGreaterThanOrEqual(2);
    for (const { file, value } of scene) {
      expect(value.match(/url\(/g), `${file}: --scene-grid must be one image`).toHaveLength(1);
      expect([...value.matchAll(/stroke-width='([\d.]+)'/g)].map((m) => m[1]), `${file}: --scene-grid strokes`).toEqual(['1']);
      expect(value.match(/<path|%3Cpath/g), `${file}: --scene-grid paths`).toHaveLength(1);
      const op = /stroke-opacity='([\d.]+)'/.exec(value);
      expect(Number(op?.[1] ?? 1), `${file}: --scene-grid opacity`).toBeLessThanOrEqual(0.15);
    }
  });
});

describe('the grid lint fires', () => {
  // The same checks, applied to small broken stylesheets, so a regression cannot slip past a typo.
  const majorToken = (css: string) => /--[\w-]*(?:grid[\w-]*major|major[\w-]*grid)/i.test(strip(css));
  const extraToken = (css: string) => [...strip(css).matchAll(/(--(?:scene-)?grid[\w-]*)\s*:/g)].some((m) => !GRID_TOKENS.has(m[1]));

  it('on a reintroduced major grid', () => {
    expect(majorToken(':root { --grid-major: rgba(30, 102, 245, 0.16); }')).toBe(true);
    expect(majorToken(':root { --scene-grid-major: url(x.svg); }')).toBe(true);
    expect(majorToken(':root { --grid-minor: rgba(0,0,0,.07); /* --grid-major was removed */ }')).toBe(false);
  });

  it('on a second grid token under another name', () => {
    expect(extraToken(':root { --grid-strong: #000; }')).toBe(true);
    expect(extraToken(':root { --grid-minor: #000; --scene-grid: url(x); }')).toBe(false);
  });

  it('on an extra background layer in body::before', () => {
    const r = rule(
      'body::before { background-image: linear-gradient(var(--grid-minor) 1px, transparent 1px), linear-gradient(90deg, var(--grid-minor) 1px, transparent 1px), linear-gradient(var(--grid-minor) 2px, transparent 2px); }',
      'body::before',
    );
    expect(r['background-image']).not.toBe('linear-gradient(var(--grid-minor) 1px, transparent 1px), linear-gradient(90deg, var(--grid-minor) 1px, transparent 1px)');
  });
});
