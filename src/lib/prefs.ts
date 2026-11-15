/**
 * Tiny per-browser preferences (theme, language, chosen papers). Separate from progress so the
 * inline head script can read it cheaply. Every access is wrapped: blocked storage just means
 * the preference lasts for this page only.
 */
export interface Prefs {
  v: 1;
  lang?: 'zh-tw' | 'en';
  theme?: 'light' | 'dark';
  mathPath?: 'A' | 'B' | 'both';
}

export const PREFS_KEY = 'gsat:prefs';

export function readPrefs(storage: Pick<Storage, 'getItem'> | null = safeStorage()): Prefs {
  try {
    const raw = storage?.getItem(PREFS_KEY);
    const data = raw ? (JSON.parse(raw) as Partial<Prefs>) : {};
    return { ...data, v: 1 };
  } catch {
    return { v: 1 };
  }
}

export function setPref<K extends Exclude<keyof Prefs, 'v'>>(key: K, value: Prefs[K], storage: Pick<Storage, 'getItem' | 'setItem'> | null = safeStorage()): void {
  try {
    const next = { ...readPrefs(storage), [key]: value };
    storage?.setItem(PREFS_KEY, JSON.stringify(next));
  } catch {
    /* storage blocked */
  }
}

function safeStorage(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.localStorage;
  } catch {
    return null;
  }
}
