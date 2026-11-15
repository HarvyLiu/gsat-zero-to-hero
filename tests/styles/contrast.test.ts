/**
 * Reads the real theme tokens from src/styles/tokens.css and src/styles/subjects.css and checks that
 * every text/background pair the site uses meets WCAG AA (4.5:1 for text, 3:1 for UI parts), in both
 * the light (Catppuccin Latte) and dark (Catppuccin Mocha) themes. Ported from the ASMC reference's
 * tests/contrast.test.ts; the subject accents are new (docs/design/05-platform.md §7 Tokens).
 */
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { SUBJECT_IDS } from '../../src/data/schema';
import { contrast } from '../../src/iso/palette';

const read = (f: string) => readFileSync(new URL(`../../src/styles/${f}`, import.meta.url), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
const TOKENS = read('tokens.css');
const SUBJECTS = read('subjects.css');

/** The 6-digit hex custom properties of the first block that opens with `selector`. */
function block(css: string, selector: string): Record<string, string> {
  const start = css.indexOf(selector);
  if (start < 0) throw new Error(`missing ${selector}`);
  const open = css.indexOf('{', start);
  const close = css.indexOf('}', open);
  const out: Record<string, string> = {};
  for (const m of css.slice(open + 1, close).matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;/g)) out[m[1]] = m[2].toLowerCase();
  return out;
}

const LIGHT_SEL = ':root {';
const DARK_SEL = ":root[data-theme='dark']";
const MEDIA_DARK_SEL = ":root:not([data-theme='light'])";

const light = { ...block(TOKENS, LIGHT_SEL), ...block(SUBJECTS, LIGHT_SEL) };
const dark = { ...light, ...block(TOKENS, DARK_SEL), ...block(SUBJECTS, DARK_SEL) };

const TEXT: Array<[string, string]> = [
  ['text', 'paper'],
  ['text', 'card'],
  ['text', 'inset'],
  ['muted', 'paper'],
  ['muted', 'card'],
  ['muted', 'inset'],
  ['accent', 'paper'],
  ['accent', 'card'],
  ['on-accent', 'accent'],
  ['teal-strong', 'paper'],
  ['teal-strong', 'teal-soft'],
  ['orange-text', 'paper'],
  ['orange-text', 'orange-soft'],
  ['text', 'orange-soft'],
  ['text', 'good-soft'],
  ['text', 'bad-soft'],
  ['text', 'teal-soft'],
  ['good-text', 'card'],
  ['bad', 'card'],
  ['aha-text', 'aha-bg'],
  ['aha-label', 'aha-bg'],
  // every subject accent (subjects.css): text in the subject colour on paper, cards and its tinted card
  ...SUBJECT_IDS.flatMap((s): Array<[string, string]> => [
    [`${s}-text`, 'paper'],
    [`${s}-text`, 'card'],
    [`${s}-text`, `${s}-soft`],
    ['text', `${s}-soft`],
  ]),
];
const UI: Array<[string, string]> = [
  ['card-border', 'paper'],
  ['card-border', 'card'],
  ['focus', 'paper'],
  // subject marks (icons, borders, chips)
  ...SUBJECT_IDS.map((s): [string, string] => [s, 'paper']),
];

for (const [name, theme] of [
  ['light (Latte)', light],
  ['dark (Mocha)', dark],
] as const) {
  describe(`contrast in ${name}`, () => {
    for (const [fg, bg] of TEXT) {
      it(`${fg} on ${bg} is at least 4.5:1`, () => {
        expect(theme[fg], `--${fg}`).toBeDefined();
        expect(theme[bg], `--${bg}`).toBeDefined();
        expect(contrast(theme[fg], theme[bg])).toBeGreaterThanOrEqual(4.5);
      });
    }
    for (const [fg, bg] of UI) {
      it(`${fg} on ${bg} is at least 3:1`, () => {
        expect(theme[fg], `--${fg}`).toBeDefined();
        expect(theme[bg], `--${bg}`).toBeDefined();
        expect(contrast(theme[fg], theme[bg])).toBeGreaterThanOrEqual(3);
      });
    }
  });
}

describe('theme blocks agree', () => {
  // The dark theme is written twice (prefers-color-scheme and the explicit toggle); they must not drift.
  for (const [file, css] of [
    ['tokens.css', TOKENS],
    ['subjects.css', SUBJECTS],
  ] as const) {
    it(`${file}: the prefers-color-scheme dark block equals the [data-theme='dark'] block`, () => {
      expect(block(css, MEDIA_DARK_SEL)).toEqual(block(css, DARK_SEL));
    });
  }

  it('defines every subject accent in both themes and maps each [data-subject]', () => {
    const want = SUBJECT_IDS.flatMap((s) => [s, `${s}-text`, `${s}-soft`]);
    expect(want.filter((k) => !block(SUBJECTS, LIGHT_SEL)[k])).toEqual([]);
    expect(want.filter((k) => !block(SUBJECTS, DARK_SEL)[k])).toEqual([]);
    expect(SUBJECT_IDS.filter((s) => !SUBJECTS.includes(`[data-subject='${s}'] { --subj: var(--${s}); --subj-text: var(--${s}-text); --subj-soft: var(--${s}-soft); }`))).toEqual([]);
  });
});
