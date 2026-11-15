/**
 * Practice item banks: YAML at src/data/items/<subject>/<slug>.yaml, `{ chapter, items }`, validated by
 * schema.ItemBank plus the cross-field rules below. YAML is the single source read by this loader and by
 * the SymPy harness (harness/verify_items.py), so answer keys exist exactly once for both locales.
 *
 * Item ids may carry '@<version>' (e.g. 'q3@2'). MDX may name an item by its base id ('q3'); progress keys
 * use the full id, so bumping the version of a revised item invalidates the old progress on purpose.
 *
 * Server-only (build time): it bundles every bank and KaTeX. Islands import only its types.
 */
import { parse as parseYaml } from 'yaml';
import { ChapterId, ItemBank, type Item, type Locale } from '../data/schema';
import { stripBase } from '../i18n/urls';
import { renderInline } from './render-inline';
import { keyValue, type NumericAccept } from './scoring';

export { renderInline };

const RAW = import.meta.glob<string>('/src/data/items/**/*.yaml', { query: '?raw', import: 'default', eager: true });

/** harness check ids: '<module>:<function>', module dotted for sub-packages (harness/checks/<module>.py) */
export const VERIFY_RE = /^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*:[a-z_][a-z0-9_]*$/;
const BANK_PATH_RE = /\/src\/data\/items\/([a-z]+)\/([a-z0-9-]+)\.ya?ml$/;

export class ItemBankError extends Error {
  constructor(
    readonly file: string,
    readonly problems: string[],
  ) {
    super(`Invalid item bank ${file}:\n  - ${problems.join('\n  - ')}`);
    this.name = 'ItemBankError';
  }
}

export const baseId = (id: string): string => id.replace(/@\d+$/, '');

/** Rules a Zod object schema cannot express: option parity across locales, key ranges, unique ids. */
export function itemProblems(item: Item): string[] {
  const out: string[] = [];
  const at = (msg: string) => out.push(`${item.id}: ${msg}`);
  const zh = item.text['zh-tw'];
  const en = item.text.en;
  if (Boolean(zh.hint) !== Boolean(en.hint)) at('hint must exist in both locales or in neither');
  if (item.verify !== undefined && !VERIFY_RE.test(item.verify)) at(`verify "${item.verify}" must look like "<module>:<function>"`);

  if (item.type === 'single' || item.type === 'multi') {
    const n = zh.options?.length ?? 0;
    if (!zh.options || !en.options) at('a choice item needs options in both locales');
    else if (zh.options.length !== en.options.length) at(`zh-tw has ${zh.options.length} options but en has ${en.options.length}`);
    if (n < 2) at('a choice item needs at least 2 options');
    for (const opt of [...(zh.options ?? []), ...(en.options ?? [])]) if (!opt.trim()) at('empty option text');
    const keys = item.type === 'single' ? [item.answer] : item.answer;
    for (const k of keys) if (k >= n) at(`answer index ${k} is outside the ${n} options (indices are 0-based)`);
    if (new Set(keys).size !== keys.length) at('answer lists an option twice');
  } else if (zh.options || en.options) {
    at(`a ${item.type} item has no options`);
  }

  if (item.type === 'numeric') {
    try {
      const v = keyValue(item.answer, item.accept);
      if (item.accept === 'int' && v.q !== 1n) at(`answer ${item.answer} is not an integer`);
    } catch (e) {
      at((e as Error).message);
    }
  }
  if (item.type === 'mixed') {
    const ids = item.rubric.criteria.map((c) => c.id);
    if (new Set(ids).size !== ids.length) at('rubric criteria ids must be unique');
  }
  return out;
}

function formatIssues(err: unknown): string[] {
  const issues = (err as { issues?: { path: PropertyKey[]; message: string }[] }).issues;
  if (!issues) return [String(err)];
  return issues.map((i) => `${i.path.map(String).join('.') || '(root)'}: ${i.message}`);
}

/** Parse and validate one bank's YAML source. Throws ItemBankError listing every problem found. */
export function parseItemBankSource(source: string, file: string): ItemBank {
  let data: unknown;
  try {
    data = parseYaml(source, { uniqueKeys: true, prettyErrors: true });
  } catch (e) {
    throw new ItemBankError(file, [`YAML: ${(e as Error).message}`]);
  }
  const parsed = ItemBank.safeParse(data);
  if (!parsed.success) throw new ItemBankError(file, formatIssues(parsed.error));
  const bank = parsed.data;
  const problems = bank.items.flatMap(itemProblems);
  const seen = new Set<string>();
  for (const it of bank.items) {
    const b = baseId(it.id);
    if (seen.has(b)) problems.push(`${it.id}: another item in this bank has the id "${b}" (ids are unique ignoring @version)`);
    seen.add(b);
  }
  const m = BANK_PATH_RE.exec(file.replace(/\\/g, '/'));
  if (m && bank.chapter !== `${m[1]}/${m[2]}`) problems.push(`chapter "${bank.chapter}" does not match the file path (expected "${m[1]}/${m[2]}")`);
  if (problems.length) throw new ItemBankError(file, problems);
  return bank;
}

/** Build the chapter → bank index from { path: yamlSource }; throws on invalid banks or a chapter defined twice. */
export function createItemIndex(files: Record<string, string>): Map<string, ItemBank> {
  const index = new Map<string, ItemBank>();
  const from = new Map<string, string>();
  for (const [file, source] of Object.entries(files).sort(([a], [b]) => a.localeCompare(b))) {
    const bank = parseItemBankSource(source, file);
    const prev = from.get(bank.chapter);
    if (prev) throw new ItemBankError(file, [`chapter "${bank.chapter}" already has a bank in ${prev}`]);
    index.set(bank.chapter, bank);
    from.set(bank.chapter, file);
  }
  return index;
}

let index: Map<string, ItemBank> | null = null;
const banks = (): Map<string, ItemBank> => (index ??= createItemIndex(RAW));

/** Every bank in src/data/items (for parity tests, the review queue and static item endpoints). */
export function itemBanks(): ItemBank[] {
  return [...banks().values()];
}

export function loadItemBank(chapterId: string): ItemBank | undefined {
  return banks().get(chapterId);
}

/** Resolve ids against a bank: an exact id, or a base id without '@version'. Throws on anything unknown. */
export function resolveItems(bank: ItemBank, ids: readonly string[]): Item[] {
  const seen = new Set<string>();
  return ids.map((id) => {
    const item = bank.items.find((it) => it.id === id) ?? bank.items.find((it) => baseId(it.id) === id);
    if (!item) throw new Error(`Unknown item "${id}" in ${bank.chapter}; the bank has: ${bank.items.map((it) => it.id).join(', ')}`);
    if (seen.has(item.id)) throw new Error(`Item "${id}" is listed twice for ${bank.chapter}`);
    seen.add(item.id);
    return item;
  });
}

export function itemsFor(chapterId: string, ids: string[]): Item[] {
  const bank = loadItemBank(chapterId);
  if (!bank) throw new Error(`No item bank for chapter "${chapterId}" (expected src/data/items/${chapterId}.yaml)`);
  return resolveItems(bank, ids);
}

// ---------- prepared items: what the ItemRunner island receives ----------

/** Pre-rendered HTML (renderInline) for one locale. */
export interface PreparedText {
  stem: string;
  options?: string[];
  explain: string;
  hint?: string;
  /** 混合題: rubric criterion texts, in rubric order */
  criteria?: string[];
  /** 混合題: model answer */
  model?: string;
}

interface PreparedCommon {
  /** full item id, '@version' included */
  id: string;
  html: PreparedText;
  /** the zh-tw text, on EN pages only ("顯示中文") */
  altHtml?: PreparedText;
}

export type PreparedItem = PreparedCommon &
  (
    | { type: 'single'; answer: number }
    | { type: 'multi'; answer: number[] }
    | { type: 'fill'; answer: string[] }
    | { type: 'numeric'; accept: NumericAccept; answer: number | string }
    | { type: 'mixed'; criteria: { id: string; points: number }[] }
  );

export function prepareText(item: Item, locale: Locale): PreparedText {
  const t = item.text[locale];
  const out: PreparedText = { stem: renderInline(t.stem), explain: renderInline(t.explain) };
  if (t.options) out.options = t.options.map(renderInline);
  if (t.hint) out.hint = renderInline(t.hint);
  if (item.type === 'mixed') {
    out.criteria = item.rubric.criteria.map((c) => renderInline(c.text[locale]));
    out.model = renderInline(item.model[locale]);
  }
  return out;
}

export function prepareItem(item: Item, locale: Locale): PreparedItem {
  const common: PreparedCommon = { id: item.id, html: prepareText(item, locale) };
  if (locale === 'en') common.altHtml = prepareText(item, 'zh-tw');
  switch (item.type) {
    case 'single':
      return { ...common, type: 'single', answer: item.answer };
    case 'multi':
      return { ...common, type: 'multi', answer: [...item.answer].sort((a, b) => a - b) };
    case 'fill':
      return { ...common, type: 'fill', answer: item.answer };
    case 'numeric':
      return { ...common, type: 'numeric', accept: item.accept, answer: item.answer };
    case 'mixed':
      return { ...common, type: 'mixed', criteria: item.rubric.criteria.map(({ id, points }) => ({ id, points })) };
  }
}

/** Load, resolve and pre-render items for a page in one locale (used by Quiz.astro at build time). */
export function prepareItems(chapterId: string, ids: string[], locale: Locale): PreparedItem[] {
  return itemsFor(chapterId, ids).map((it) => prepareItem(it, locale));
}

/** '/zh-tw/math/real-numbers/' → 'math/real-numbers' (deploy base stripped); undefined for other paths. */
export function chapterIdFromPath(pathname: string): string | undefined {
  const m = /^\/(?:zh-tw|en)\/([a-z]+)\/([a-z0-9-]+)\/?$/.exec(stripBase(pathname));
  if (!m) return undefined;
  const id = `${m[1]}/${m[2]}`;
  return ChapterId.safeParse(id).success ? id : undefined;
}
