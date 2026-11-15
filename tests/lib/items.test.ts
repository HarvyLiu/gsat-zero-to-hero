import { createElement } from 'react';
import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import ItemRunner, { formatScore, LABELS, multiFormula } from '../../src/components/exam/ItemRunner';
import type { Item } from '../../src/data/schema';
import {
  baseId,
  chapterIdFromPath,
  createItemIndex,
  ItemBankError,
  itemBanks,
  itemsFor,
  loadItemBank,
  parseItemBankSource,
  prepareItem,
  prepareItems,
  renderInline,
  resolveItems,
} from '../../src/lib/items';
import { judgeMulti } from '../../src/lib/scoring';

const FIXTURES = import.meta.glob<string>('/tests/fixtures/items/*.yaml', { query: '?raw', import: 'default', eager: true });
const BAD = import.meta.glob<string>('/tests/fixtures/items/bad/*.yaml', { query: '?raw', import: 'default', eager: true });
const bad = (name: string) => BAD[`/tests/fixtures/items/bad/${name}.yaml`];

const fixtures = createItemIndex(FIXTURES);
const mathBank = fixtures.get('math/fixture-items')!;

/** a minimal valid bank in YAML, with one item patched */
function bankYaml(item: Record<string, unknown>, chapter = 'math/fixture-x'): string {
  const base = {
    id: 'q1',
    type: 'single',
    origin: 'original',
    text: {
      'zh-tw': { stem: '題目', options: ['甲', '乙'], explain: '說明' },
      en: { stem: 'Stem', options: ['A', 'B'], explain: 'Why' },
    },
    answer: 0,
  };
  return JSON.stringify({ chapter, items: [{ ...base, ...item }] }); // JSON is valid YAML
}
const problemsOf = (source: string, file = '/tests/x.yaml'): string[] => {
  try {
    parseItemBankSource(source, file);
    return [];
  } catch (e) {
    expect(e).toBeInstanceOf(ItemBankError);
    return (e as ItemBankError).problems;
  }
};

describe('fixture banks', () => {
  it('load and validate, and cover every item type', () => {
    expect([...fixtures.keys()].sort()).toEqual(['chemistry/fixture-items', 'math/fixture-items']);
    const types = new Set([...fixtures.values()].flatMap((b) => b.items.map((it) => it.type)));
    expect([...types].sort()).toEqual(['fill', 'mixed', 'multi', 'numeric', 'single']);
    // every fixture item is machine-checked by the harness
    for (const b of fixtures.values()) for (const it of b.items) expect(it.verify, it.id).toMatch(/^fixtures:/);
  });

  it('apply schema defaults', () => {
    const it = mathBank.items[0];
    expect(it.codes).toEqual([]);
    expect(it.review).toBe(true);
    expect(it.skills).toEqual([]);
  });

  it('the deliberately wrong key passes the schema: only the SymPy harness can catch it', () => {
    expect(() => parseItemBankSource(bad('wrong-key'), 'bad/wrong-key.yaml')).not.toThrow();
  });

  it('a bank without English text is rejected', () => {
    const problems = problemsOf(bad('missing-en'));
    expect(problems.some((p) => p.includes('text.en'))).toBe(true);
  });
});

describe('bank validation beyond the schema', () => {
  it('rejects option-count mismatches, out-of-range keys and duplicate keys', () => {
    expect(problemsOf(bankYaml({ text: { 'zh-tw': { stem: 's', options: ['a', 'b', 'c'], explain: 'e' }, en: { stem: 's', options: ['a', 'b'], explain: 'e' } } }))).toEqual([
      'q1: zh-tw has 3 options but en has 2',
    ]);
    expect(problemsOf(bankYaml({ answer: 2 }))[0]).toMatch(/answer index 2 is outside the 2 options/);
    expect(problemsOf(bankYaml({ type: 'multi', answer: [1, 1] }))).toEqual(['q1: answer lists an option twice']);
  });

  it('rejects options on non-choice items, one-sided hints and bad verify ids', () => {
    expect(problemsOf(bankYaml({ type: 'fill', answer: ['1'] }))).toEqual(['q1: a fill item has no options']);
    const hinted = { 'zh-tw': { stem: 's', options: ['a', 'b'], explain: 'e', hint: '提示' }, en: { stem: 's', options: ['a', 'b'], explain: 'e' } };
    expect(problemsOf(bankYaml({ text: hinted }))).toEqual(['q1: hint must exist in both locales or in neither']);
    expect(problemsOf(bankYaml({ verify: 'checks/fixtures.py::f' }))[0]).toMatch(/verify/);
    expect(problemsOf(bankYaml({ verify: 'math.real_numbers:ex_03' }))).toEqual([]);
  });

  it('rejects numeric keys that do not fit the accepted form', () => {
    const text = { 'zh-tw': { stem: 's', explain: 'e' }, en: { stem: 's', explain: 'e' } };
    expect(problemsOf(bankYaml({ type: 'numeric', accept: 'int', answer: 2.5, text }))[0]).toMatch(/not an integer/);
    expect(problemsOf(bankYaml({ type: 'numeric', accept: 'fraction', answer: '3/0', text }))[0]).toMatch(/not a valid fraction/);
    expect(problemsOf(bankYaml({ type: 'numeric', accept: 'fraction', answer: '−3/4', text }))).toEqual([]);
  });

  it('rejects fill cells outside 0–9 and U+2212, including the ASCII hyphen', () => {
    const text = { 'zh-tw': { stem: 's', explain: 'e' }, en: { stem: 's', explain: 'e' } };
    expect(problemsOf(bankYaml({ type: 'fill', answer: ['-', '1'], text })).length).toBeGreaterThan(0);
    expect(problemsOf(bankYaml({ type: 'fill', answer: ['−', '1'], text }))).toEqual([]);
  });

  it('rejects ids that repeat ignoring @version, and a chapter that does not match its path', () => {
    const doc = JSON.parse(bankYaml({ id: 'q1@1' }));
    doc.items.push({ ...doc.items[0], id: 'q1@2' });
    expect(problemsOf(JSON.stringify(doc))[0]).toMatch(/ids are unique ignoring @version/);
    expect(problemsOf(bankYaml({}, 'math/other'), 'C:\\repo\\src\\data\\items\\math\\fixture-x.yaml')[0]).toMatch(/does not match the file path/);
    expect(problemsOf(bankYaml({}, 'math/fixture-x'), '/src/data/items/math/fixture-x.yaml')).toEqual([]);
  });

  it('rejects duplicate YAML keys and broken YAML', () => {
    expect(problemsOf('chapter: math/a\nchapter: math/b\nitems: []')[0]).toMatch(/YAML/);
    expect(problemsOf('chapter: [unclosed')[0]).toMatch(/YAML/);
  });

  it('refuses a chapter with two banks', () => {
    expect(() => createItemIndex({ '/a.yaml': bankYaml({}), '/b.yaml': bankYaml({}) })).toThrow(/already has a bank/);
  });
});

describe('resolving item ids', () => {
  it('finds exact ids and base ids without @version', () => {
    expect(baseId('fx-sqrt@1')).toBe('fx-sqrt');
    expect(resolveItems(mathBank, ['fx-sqrt', 'fx-linear@1']).map((it) => it.id)).toEqual(['fx-sqrt@1', 'fx-linear@1']);
  });

  it('throws on unknown, stale-version and repeated ids', () => {
    expect(() => resolveItems(mathBank, ['nope'])).toThrow(/Unknown item "nope"/);
    expect(() => resolveItems(mathBank, ['fx-sqrt@2'])).toThrow(/Unknown item/);
    expect(() => resolveItems(mathBank, ['fx-sqrt', 'fx-sqrt@1'])).toThrow(/listed twice/);
  });

  it('itemsFor throws for a chapter without a bank; loadItemBank returns undefined', () => {
    expect(loadItemBank('math/no-such-chapter')).toBeUndefined();
    expect(() => itemsFor('math/no-such-chapter', ['q1'])).toThrow(/No item bank/);
  });
});

describe('real item banks in src/data/items', () => {
  it('all validate and pre-render in both locales (bad TeX fails here)', () => {
    for (const bank of itemBanks()) {
      const ids = bank.items.map((it) => it.id);
      expect(prepareItems(bank.chapter, ids, 'zh-tw')).toHaveLength(ids.length);
      expect(prepareItems(bank.chapter, ids, 'en')).toHaveLength(ids.length);
    }
  });
});

describe('prepared items', () => {
  const all: Item[] = [...fixtures.values()].flatMap((b) => b.items);

  it('pre-render every fixture text in both locales', () => {
    for (const it of all) {
      for (const locale of ['zh-tw', 'en'] as const) {
        const p = prepareItem(it, locale);
        expect(p.html.stem).toBe(renderInline(it.text[locale].stem));
        expect(p.html.explain.length).toBeGreaterThan(0);
        expect(Boolean(p.altHtml)).toBe(locale === 'en');
      }
    }
  });

  it('carry the zh-tw text on EN pages and the answer key once', () => {
    const p = prepareItem(mathBank.items[0], 'en');
    expect(p.html.stem).toContain('Compute');
    expect(p.altHtml?.stem).toContain('計算');
    expect(p).toMatchObject({ id: 'fx-sqrt@1', type: 'single', answer: 1 });
    const mixed = prepareItem(mathBank.items.find((it) => it.type === 'mixed')!, 'zh-tw');
    expect(mixed).toMatchObject({ type: 'mixed', criteria: [{ id: 'setup', points: 2 }, { id: 'simplify', points: 1 }, { id: 'conclude', points: 1 }] });
    expect(mixed.html.criteria).toHaveLength(3);
    expect(mixed.html.model).toContain('katex');
  });

  it('render mhchem formulas in options', () => {
    const chem = prepareItem(fixtures.get('chemistry/fixture-items')!.items[0], 'zh-tw');
    expect(chem.html.options).toHaveLength(4);
    for (const o of chem.html.options!) expect(o).toContain('class="katex"');
  });
});

describe('chapterIdFromPath', () => {
  it('derives the chapter id from a lesson URL', () => {
    expect(chapterIdFromPath('/zh-tw/math/real-numbers/')).toBe('math/real-numbers');
    expect(chapterIdFromPath('/en/chemistry/moles')).toBe('chemistry/moles');
    expect(chapterIdFromPath('/zh-tw/')).toBeUndefined();
    expect(chapterIdFromPath('/zh-tw/math/')).toBeUndefined();
    expect(chapterIdFromPath('/fr/math/x/')).toBeUndefined();
    expect(chapterIdFromPath('/zh-tw/music/x/')).toBeUndefined(); // not a subject
    expect(chapterIdFromPath('/zh-tw/math/x/extra/')).toBeUndefined();
  });
});

describe('ItemRunner (server render)', () => {
  const ids = mathBank.items.map((it) => it.id);
  const render = (locale: 'zh-tw' | 'en') =>
    renderToString(createElement(ItemRunner, { chapter: mathBank.chapter, locale, items: resolveItems(mathBank, ids).map((it) => prepareItem(it, locale)) }));

  it('renders every item type accessibly', () => {
    const html = render('zh-tw');
    expect(html.match(/<fieldset class="exam-fieldset"/g)).toHaveLength(ids.length);
    expect(html.match(/<legend class="quiz-prompt exam-stem"/g)).toHaveLength(ids.length);
    expect(html).toContain('aria-live="polite"');
    // 單選: five radios; 多選: five toggle buttons
    expect(html.match(/type="radio" name="[^"]*-single"/g)).toHaveLength(5);
    expect(html.match(/aria-pressed="false"/g)!.length).toBeGreaterThanOrEqual(5);
    // 選填: one radio column of 11 bubbles per cell (3 + 2 cells in the fixtures)
    expect(html.match(/class="fill-row"/g)).toHaveLength(5);
    expect(html.match(/class="fill-input"/g)).toHaveLength(5 * 11);
    expect(html).toContain('value="−"');
    expect(html).toContain('<textarea');
    expect(html).toContain('原創練習題（非大考中心試題）');
    expect(html).toContain('已答對0／8');
    expect(html).not.toContain('Show in Chinese');
    expect(html).toContain(`data-item="math/fixture-items/fx-sqrt@1"`);
  });

  it('offers the Chinese text on EN pages', () => {
    const html = render('en');
    expect(html.match(/顯示中文 \/ Show in Chinese/g)).toHaveLength(ids.length);
    expect(html).toContain('0 / 8 solved');
  });
});

describe('runner labels and formatting', () => {
  it('have the same keys in both locales and no empty strings', () => {
    const shape = (o: object): string[] =>
      Object.entries(o)
        .flatMap(([k, v]) => (typeof v === 'object' ? shape(v).map((s) => `${k}.${s}`) : [k]))
        .sort();
    expect(shape(LABELS.en)).toEqual(shape(LABELS['zh-tw']));
    const strings = (o: object): string[] => Object.values(o).flatMap((v) => (typeof v === 'object' ? strings(v) : [v as string]));
    for (const s of [...strings(LABELS.en), ...strings(LABELS['zh-tw'])]) expect(s.trim()).not.toBe('');
    // zh labels use full-width punctuation
    for (const s of strings(LABELS['zh-tw'])) expect(s, s).not.toMatch(/[\u4e00-\u9fff][,;:?!]|[,;:?!][\u4e00-\u9fff]/);
  });

  it('spells out the 多選 score', () => {
    expect(formatScore(2 / 3)).toBe('0.67');
    expect(multiFormula(judgeMulti([0], [0, 2], 5))).toBe('(5 − 2×1) / 5 = 0.6');
    expect(multiFormula(judgeMulti([1, 3, 4], [0, 2], 5))).toBe('(5 − 2×5) / 5 < 0 → 0');
    expect(multiFormula(judgeMulti([0, 2], [0, 2], 5))).toBe('(5 − 2×0) / 5 = 1');
  });
});
