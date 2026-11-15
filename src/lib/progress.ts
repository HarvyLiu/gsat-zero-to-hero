/**
 * Per-browser progress: finished chapters and practice-item results. Ported from the ASMC store
 * (KV abstraction, blocked-storage fallback, subscribe/reload, cross-tab `storage` events) and extended
 * for item scores (docs/design/05-platform.md §5).
 *
 * Keys never contain the locale: an item is '<chapter>/<itemId>', e.g. 'math/real-numbers/q3@2', so an
 * item solved on a zh-tw page shows as solved on the en page. The '@version' stays in the key on purpose:
 * revising an item (bumping its version) starts its progress afresh.
 *
 * Everything is wrapped so the site still works when storage is blocked (private windows, disabled
 * cookies, a full quota): progress then lives only in memory for this page.
 */
export interface KV {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem?(key: string): void;
}

export interface ChapterMark {
  done: true;
  at: string;
}

export interface Attempt {
  at: string;
  /** fraction of the item's points, 0..1 */
  score: number;
  /** self-assessed against a rubric (混合題), not machine-scored */
  self?: true;
}

export interface ItemRecord {
  firstAt: string;
  lastAt: string;
  /** best score over all attempts, 0..1 */
  best: number;
  /** the most recent attempts, oldest first, at most MAX_ATTEMPTS */
  attempts: Attempt[];
}

export interface ProgressData {
  v: 2;
  chapters: Record<string, ChapterMark>;
  items: Record<string, ItemRecord>;
}

export const PROGRESS_VERSION = 2;
export const MAX_ATTEMPTS = 5;
export const STORAGE_KEY = 'gsat:progress';
export const CHANGE_EVENT = 'gsat-progress';

/** The progress key of an item: locale-free, version included. */
export const itemKey = (chapter: string, itemId: string): string => `${chapter}/${itemId}`;

// Null-prototype dictionaries: a key such as '__proto__' or 'toString' is an ordinary key here.
function dict<T>(): Record<string, T> {
  return Object.create(null) as Record<string, T>;
}
const empty = (): ProgressData => ({ v: 2, chapters: dict(), items: dict() });

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === 'object' && x !== null && !Array.isArray(x);
}
const isScore = (x: unknown): x is number => typeof x === 'number' && Number.isFinite(x) && x >= 0 && x <= 1;

type Raw = Record<string, unknown>;

/**
 * v → v+1 upgrades, applied in order. v1 is the ASMC shape, where an item mark { done, at } meant
 * "answered correctly": it becomes a record with one full-score attempt.
 */
const MIGRATIONS: Record<number, (d: Raw) => Raw> = {
  1: (d) => {
    const items = dict<unknown>();
    if (isRecord(d.items)) {
      for (const [k, m] of Object.entries(d.items)) {
        if (isRecord(m) && typeof m.at === 'string') items[k] = { firstAt: m.at, lastAt: m.at, best: 1, attempts: [{ at: m.at, score: 1 }] };
      }
    }
    return { ...d, v: 2, items };
  },
};

function cleanChapters(x: unknown): Record<string, ChapterMark> {
  const out = dict<ChapterMark>();
  if (!isRecord(x)) return out;
  for (const [k, m] of Object.entries(x)) if (isRecord(m) && m.done === true && typeof m.at === 'string') out[k] = { done: true, at: m.at };
  return out;
}

function cleanAttempts(x: unknown): Attempt[] {
  if (!Array.isArray(x)) return [];
  const out: Attempt[] = [];
  for (const a of x) {
    if (!isRecord(a) || typeof a.at !== 'string' || !isScore(a.score)) continue;
    out.push(a.self === true ? { at: a.at, score: a.score, self: true } : { at: a.at, score: a.score });
  }
  return out.slice(-MAX_ATTEMPTS);
}

function cleanItems(x: unknown): Record<string, ItemRecord> {
  const out = dict<ItemRecord>();
  if (!isRecord(x)) return out;
  for (const [k, r] of Object.entries(x)) {
    if (!isRecord(r) || typeof r.firstAt !== 'string' || typeof r.lastAt !== 'string' || !isScore(r.best)) continue;
    out[k] = { firstAt: r.firstAt, lastAt: r.lastAt, best: r.best, attempts: cleanAttempts(r.attempts) };
  }
  return out;
}

/**
 * Parse stored or imported progress, migrating older versions. Missing, corrupt or unknown-version data
 * gives empty progress; malformed entries are dropped one by one, the rest is kept.
 * (Data from a NEWER version, e.g. after a rollback, also reads as empty: the trade-off ASMC made too.)
 */
export function parseProgress(raw: string | null): ProgressData {
  if (!raw) return empty();
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    return empty();
  }
  if (!isRecord(data) || typeof data.v !== 'number') return empty();
  let d: Raw = data;
  while (typeof d.v === 'number' && d.v < PROGRESS_VERSION) {
    const up = MIGRATIONS[d.v];
    if (!up) return empty();
    d = up(d);
  }
  if (d.v !== PROGRESS_VERSION || !isRecord(d.chapters) || !isRecord(d.items)) return empty();
  return { v: 2, chapters: cleanChapters(d.chapters), items: cleanItems(d.items) };
}

const earlier = (a: string, b: string) => (a <= b ? a : b);
const later = (a: string, b: string) => (a >= b ? a : b);

/** Merge two progress files (export/import): union, max best, earliest firstAt, latest lastAt. */
export function mergeProgress(a: ProgressData, b: ProgressData): ProgressData {
  const out = empty();
  for (const src of [a, b]) {
    for (const [k, m] of Object.entries(src.chapters)) out.chapters[k] = out.chapters[k] ? { done: true, at: earlier(out.chapters[k].at, m.at) } : { ...m };
  }
  for (const src of [a, b]) {
    for (const [k, r] of Object.entries(src.items)) {
      const prev = out.items[k];
      if (!prev) {
        out.items[k] = { ...r, attempts: [...r.attempts] };
        continue;
      }
      const seen = new Set<string>();
      const attempts = [...prev.attempts, ...r.attempts]
        .sort((x, y) => (x.at < y.at ? -1 : x.at > y.at ? 1 : 0))
        .filter((t) => {
          const id = `${t.at}|${t.score}|${t.self ? 1 : 0}`;
          return seen.has(id) ? false : (seen.add(id), true);
        })
        .slice(-MAX_ATTEMPTS);
      out.items[k] = { firstAt: earlier(prev.firstAt, r.firstAt), lastAt: later(prev.lastAt, r.lastAt), best: Math.max(prev.best, r.best), attempts };
    }
  }
  return out;
}

export interface ProgressStore {
  get(): ProgressData;
  isChapterDone(id: string): boolean;
  markChapter(id: string, done?: boolean): void;
  /** solved: best score is full marks */
  isItemDone(id: string): boolean;
  item(id: string): ItemRecord | undefined;
  bestScore(id: string): number | undefined;
  /** record a full-score attempt unless the item is already solved (simple widgets: Exercise, Predict) */
  markItem(id: string): void;
  /** record one scored attempt (0..1); keeps the best score and the last MAX_ATTEMPTS attempts */
  recordAttempt(id: string, score: number, opts?: { self?: boolean }): ItemRecord;
  /** solved items whose key starts with prefix, e.g. 'math/real-numbers/' */
  countItems(prefix: string): number;
  reset(): void;
  subscribe(cb: (data: ProgressData) => void): () => void;
  /** re-read from storage (another tab or island changed it) */
  reload(): void;
}

export function createProgressStore(storage: KV | null, notify: () => void = () => {}, now: () => Date = () => new Date()): ProgressStore {
  const read = (): ProgressData => {
    try {
      return parseProgress(storage ? storage.getItem(STORAGE_KEY) : null);
    } catch {
      return empty();
    }
  };
  let data = read();
  const listeners = new Set<(d: ProgressData) => void>();
  const emit = () => listeners.forEach((cb) => cb(data));

  const save = () => {
    try {
      storage?.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      /* storage full or blocked: keep the in-memory copy */
    }
    emit();
    notify();
  };
  const stamp = () => now().toISOString();
  const withItem = (id: string, rec: ItemRecord) => {
    const items = Object.assign(dict<ItemRecord>(), data.items);
    items[id] = rec;
    data = { ...data, items };
    save();
  };
  const own = <T,>(rec: Record<string, T>, id: string): T | undefined => (Object.hasOwn(rec, id) ? rec[id] : undefined);

  const recordAttempt = (id: string, score: number, opts?: { self?: boolean }): ItemRecord => {
    if (!Number.isFinite(score)) throw new RangeError(`recordAttempt: score must be a number in 0..1, got ${score}`);
    const s = Math.min(1, Math.max(0, score));
    const at = stamp();
    const attempt: Attempt = opts?.self ? { at, score: s, self: true } : { at, score: s };
    const prev = own(data.items, id);
    const rec: ItemRecord = prev
      ? { firstAt: prev.firstAt, lastAt: at, best: Math.max(prev.best, s), attempts: [...prev.attempts, attempt].slice(-MAX_ATTEMPTS) }
      : { firstAt: at, lastAt: at, best: s, attempts: [attempt] };
    withItem(id, rec);
    return rec;
  };
  const isItemDone = (id: string) => (own(data.items, id)?.best ?? 0) >= 1;

  return {
    get: () => data,
    isChapterDone: (id) => Boolean(own(data.chapters, id)),
    markChapter(id, done = true) {
      const chapters = Object.assign(dict<ChapterMark>(), data.chapters);
      if (done) chapters[id] = { done: true, at: stamp() };
      else delete chapters[id];
      data = { ...data, chapters };
      save();
    },
    isItemDone,
    item: (id) => own(data.items, id),
    bestScore: (id) => own(data.items, id)?.best,
    markItem(id) {
      if (isItemDone(id)) return;
      recordAttempt(id, 1);
    },
    recordAttempt,
    countItems: (prefix) => Object.entries(data.items).filter(([k, r]) => k.startsWith(prefix) && r.best >= 1).length,
    reset() {
      data = empty();
      save();
    },
    subscribe(cb) {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    reload() {
      data = read();
      emit();
    },
  };
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

let shared: ProgressStore | null = null;

/** The page-wide store. Islands and plain scripts all share it and stay in sync. */
export function progress(): ProgressStore {
  if (shared) return shared;
  if (typeof window === 'undefined') return createProgressStore(null);
  const store = createProgressStore(browserStorage(), () => window.dispatchEvent(new CustomEvent(CHANGE_EVENT, { detail: 'local' })));
  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEY) store.reload();
  });
  shared = store;
  return store;
}
