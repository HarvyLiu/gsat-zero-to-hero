/**
 * UI string parity (docs/design/05-platform.md §2, §6): every key of src/i18n/ui.ts exists in both
 * locales with a non-empty value and the same {placeholders}; t() refuses unknown keys; and every
 * co-located label set (a labels.ts module, or a module exporting LABELS) has the same shape in both.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { HTML_LANG, LANG_NAME, LOCALES, UI, t, type UiKey } from '../../src/i18n/ui';

const placeholders = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
const HAN = '\\p{Script=Han}';
const ASCII_PUNCT_NEXT_TO_HAN = new RegExp(`${HAN}\\s*[,;:?!]|[,;:?!]\\s*${HAN}`, 'u');

describe('src/i18n/ui.ts', () => {
  const zh = UI['zh-tw'] as Record<string, string>;
  const en = UI.en as Record<string, string>;

  it('has the same keys in zh-tw and en', () => {
    expect(Object.keys(en).sort()).toEqual(Object.keys(zh).sort());
  });

  it('has no empty strings', () => {
    const empty = LOCALES.flatMap((l) => Object.entries(UI[l] as Record<string, string>).filter(([, v]) => !v.trim()).map(([k]) => `${l}:${k}`));
    expect(empty).toEqual([]);
  });

  it('uses the same {placeholders} in both languages', () => {
    expect(Object.keys(zh).filter((k) => placeholders(zh[k]).join() !== placeholders(en[k]).join())).toEqual([]);
  });

  it('uses full-width punctuation next to Chinese text in zh-tw strings', () => {
    expect(Object.entries(zh).filter(([, v]) => ASCII_PUNCT_NEXT_TO_HAN.test(v) || /["“”]/.test(v)).map(([k, v]) => `${k}: ${v}`)).toEqual([]);
  });

  it('names both languages and their html lang', () => {
    expect(LOCALES).toEqual(['zh-tw', 'en']);
    expect(HTML_LANG).toEqual({ 'zh-tw': 'zh-TW', en: 'en' });
    expect(Object.keys(LANG_NAME).sort()).toEqual(['en', 'zh-tw']);
  });

  it('interpolates and throws on a missing key instead of falling back', () => {
    const key = Object.keys(zh).find((k) => placeholders(zh[k]).includes('n')) as UiKey | undefined;
    if (key) expect(t('en', key, { n: 7 })).toContain('7');
    expect(() => t('en', 'no.such.key' as UiKey)).toThrow(/Missing UI string/);
  });
});

/** Shape of a label tree: the sorted key paths of its string leaves; empty leaves are reported. */
function leaves(value: unknown, prefix = ''): { paths: string[]; empty: string[] } {
  if (typeof value === 'string') return { paths: [prefix], empty: value.trim() ? [] : [prefix] };
  if (Array.isArray(value)) return merge(value.map((v, i) => leaves(v, `${prefix}[${i}]`)));
  if (value && typeof value === 'object') return merge(Object.entries(value).map(([k, v]) => leaves(v, prefix ? `${prefix}.${k}` : k)));
  return { paths: [], empty: [] }; // functions and numbers are not translatable text
}
function merge(xs: Array<{ paths: string[]; empty: string[] }>) {
  return { paths: xs.flatMap((x) => x.paths).sort(), empty: xs.flatMap((x) => x.empty) };
}

// Lazy: only the modules that declare labels are imported.
const MODULES = import.meta.glob(['/src/**/*.ts', '/src/**/*.tsx', '!/src/**/*.d.ts']);
const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const LABEL_MODULES = Object.keys(MODULES).filter((p) => /\/labels\.tsx?$/.test(p) || /export const (?:LABELS|labels)\b/.test(readFileSync(ROOT + p.slice(1), 'utf8')));

describe('co-located widget labels', () => {
  it(`finds the label sets (${LABEL_MODULES.length}: ${LABEL_MODULES.join(', ') || 'none yet'})`, () => {
    expect(Array.isArray(LABEL_MODULES)).toBe(true);
  });
  for (const file of LABEL_MODULES) {
    it(`${file}: same keys in zh-tw and en, no empty strings`, async () => {
      const mod = (await MODULES[file]()) as Record<string, unknown>;
      const sets = Object.entries(mod).filter(([, v]) => v && typeof v === 'object' && 'zh-tw' in (v as object) && 'en' in (v as object)) as Array<[string, Record<string, unknown>]>;
      expect(sets.length, `${file} exports no { 'zh-tw', en } label set`).toBeGreaterThan(0);
      for (const [name, set] of sets) {
        const zh = leaves(set['zh-tw']);
        const en = leaves(set.en);
        expect(en.paths, `${file} ${name}: en keys`).toEqual(zh.paths);
        expect([...zh.empty, ...en.empty], `${file} ${name}: empty strings`).toEqual([]);
      }
    });
  }
});
