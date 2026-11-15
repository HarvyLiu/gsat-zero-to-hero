/**
 * Named JSON saves (a widget's state, a program typed into an editor) kept in one
 * localStorage entry. Like progress.ts, it survives blocked or throwing storage
 * (private windows, full quota): saves then live only in memory for this page.
 */
import type { KV } from './progress';

export const SAVES_KEY = 'gsat:saves';

interface SaveItem {
  value: unknown;
  at: string;
}

export interface SavesData {
  v: 1;
  items: Record<string, SaveItem>;
}

export interface SavesStore {
  load<T>(key: string): T | null;
  save(key: string, value: unknown): void;
  remove(key: string): void;
  keys(): string[];
}

// Null-prototype dictionaries: keys such as 'toString' or '__proto__' are plain keys here.
const dict = (): Record<string, SaveItem> => Object.create(null) as Record<string, SaveItem>;
const empty = (): SavesData => ({ v: 1, items: dict() });

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === 'object' && x !== null && !Array.isArray(x);
}

export function parseSaves(raw: string | null): SavesData {
  if (!raw) return empty();
  try {
    const data: unknown = JSON.parse(raw);
    if (!isRecord(data) || data.v !== 1 || !isRecord(data.items)) return empty();
    const items = dict();
    for (const [k, it] of Object.entries(data.items)) {
      if (isRecord(it) && 'value' in it && typeof it.at === 'string') items[k] = { value: it.value, at: it.at };
    }
    return { v: 1, items };
  } catch {
    return empty();
  }
}

export function createSavesStore(storage: KV | null): SavesStore {
  // Re-read storage on every call so other tabs and islands see each other's saves.
  let memory = empty();
  // once a write fails, storage is stale: trust memory from then on
  let broken = storage === null;
  const read = (): SavesData => {
    if (broken || !storage) return memory;
    try {
      const raw = storage.getItem(SAVES_KEY);
      // nothing stored yet (or storage was cleared): fall back to whatever we hold in memory
      return raw === null ? memory : parseSaves(raw);
    } catch {
      broken = true;
      return memory;
    }
  };
  const write = (data: SavesData) => {
    memory = data;
    try {
      storage?.setItem(SAVES_KEY, JSON.stringify(data));
    } catch {
      broken = true; /* storage full or blocked: keep the in-memory copy */
    }
  };

  const load = <T,>(key: string): T | null => {
    const items = read().items;
    return Object.hasOwn(items, key) ? (items[key].value as T) : null;
  };
  const remove = (key: string): void => {
    const data = read();
    if (!Object.hasOwn(data.items, key)) return;
    const items = Object.assign(dict(), data.items);
    delete items[key];
    write({ v: 1, items });
  };
  const save = (key: string, value: unknown): void => {
    if (value === undefined) return remove(key);
    // round-trip through JSON so memory and storage hold the same thing
    let clean: unknown;
    try {
      clean = JSON.parse(JSON.stringify(value));
    } catch {
      return; // not serialisable (cycle, BigInt): ignore
    }
    const items = Object.assign(dict(), read().items);
    items[key] = { value: clean, at: new Date().toISOString() };
    write({ v: 1, items });
  };
  const keys = (): string[] => Object.keys(read().items).sort();

  // plain functions, no `this`: safe to destructure (`const { save } = saves()`)
  return { load, save, remove, keys };
}

function browserStorage(): KV | null {
  try {
    const s = window.localStorage;
    const probe = '__gsat_probe';
    s.setItem(probe, '1');
    s.removeItem(probe);
    return s;
  } catch {
    return null;
  }
}

let shared: SavesStore | null = null;

/** The page-wide saves store. */
export function saves(): SavesStore {
  if (shared) return shared;
  if (typeof window === 'undefined') return createSavesStore(null);
  shared = createSavesStore(browserStorage());
  return shared;
}
