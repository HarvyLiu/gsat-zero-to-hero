import { describe, expect, it, vi } from 'vitest';
import { createProgressStore, itemKey, MAX_ATTEMPTS, mergeProgress, parseProgress, STORAGE_KEY, type KV, type ProgressData } from '../src/lib/progress';

function memoryKV(): KV & { raw: Map<string, string> } {
  const raw = new Map<string, string>();
  return { raw, getItem: (k) => raw.get(k) ?? null, setItem: (k, v) => void raw.set(k, v) };
}

/** a clock that ticks one minute per call, so attempt order is deterministic */
function clock(start = '2026-11-15T00:00:00.000Z') {
  let t = Date.parse(start);
  return () => {
    const d = new Date(t);
    t += 60_000;
    return d;
  };
}

const EMPTY = { v: 2, chapters: {}, items: {} };

describe('parseProgress', () => {
  it('returns empty data for missing, corrupt or unknown-version input', () => {
    for (const raw of [null, '', '{oops', '[]', '{"v":3,"chapters":{},"items":{}}', '{"v":0}', '{"v":2}', '{"chapters":{}}', '"text"']) {
      expect(parseProgress(raw)).toEqual(EMPTY);
    }
  });

  it('migrates the v1 shape: a v1 item mark means "solved", so it becomes one full-score attempt', () => {
    const v1 = { v: 1, chapters: { 'math/real-numbers': { done: true, at: '2026-11-01T00:00:00.000Z' } }, items: { 'math/real-numbers/q1': { done: true, at: '2026-11-02T00:00:00.000Z' }, bad: 3 } };
    const p = parseProgress(JSON.stringify(v1));
    expect(p.v).toBe(2);
    expect(p.chapters['math/real-numbers']).toEqual({ done: true, at: '2026-11-01T00:00:00.000Z' });
    expect(p.items['math/real-numbers/q1']).toEqual({
      firstAt: '2026-11-02T00:00:00.000Z',
      lastAt: '2026-11-02T00:00:00.000Z',
      best: 1,
      attempts: [{ at: '2026-11-02T00:00:00.000Z', score: 1 }],
    });
    expect(Object.keys(p.items)).toEqual(['math/real-numbers/q1']);
  });

  it('drops malformed v2 entries but keeps good ones, and trims long attempt lists', () => {
    const attempts = Array.from({ length: 8 }, (_, i) => ({ at: `2026-11-0${i + 1}`, score: 0.2 }));
    const raw = JSON.stringify({
      v: 2,
      chapters: { a: { done: true, at: 'x' }, b: { done: false, at: 'x' } },
      items: { good: { firstAt: 'x', lastAt: 'y', best: 0.6, attempts }, over: { firstAt: 'x', lastAt: 'y', best: 2, attempts: [] }, junk: 'no' },
    });
    const p = parseProgress(raw);
    expect(Object.keys(p.chapters)).toEqual(['a']);
    expect(Object.keys(p.items)).toEqual(['good']);
    expect(p.items.good.attempts).toHaveLength(MAX_ATTEMPTS);
    expect(p.items.good.attempts[0].at).toBe('2026-11-04');
  });

  it('keeps a key named __proto__ as data', () => {
    const raw = '{"v":2,"chapters":{},"items":{"__proto__":{"firstAt":"x","lastAt":"x","best":1,"attempts":[]}}}';
    const p = parseProgress(raw);
    expect(Object.keys(p.items)).toEqual(['__proto__']);
    expect(createProgressStore({ getItem: () => raw, setItem: () => {} }).isItemDone('__proto__')).toBe(true);
  });
});

describe('progress store', () => {
  it('marks and persists chapters and items', () => {
    const kv = memoryKV();
    const store = createProgressStore(kv);
    store.markChapter('math/real-numbers');
    store.markItem('math/real-numbers/q1');
    expect(store.isChapterDone('math/real-numbers')).toBe(true);
    expect(store.isItemDone('math/real-numbers/q1')).toBe(true);
    expect(store.countItems('math/real-numbers/')).toBe(1);

    const again = createProgressStore(kv);
    expect(again.isChapterDone('math/real-numbers')).toBe(true);
    expect(again.bestScore('math/real-numbers/q1')).toBe(1);
    expect(JSON.parse(kv.raw.get(STORAGE_KEY)!).v).toBe(2);
    expect(STORAGE_KEY).toBe('gsat:progress');
  });

  it('records scored attempts: best score, first/last time, the last five attempts', () => {
    const store = createProgressStore(memoryKV(), () => {}, clock());
    const id = 'math/real-numbers/q2';
    store.recordAttempt(id, 0.2);
    store.recordAttempt(id, 0.6);
    store.recordAttempt(id, 0);
    expect(store.bestScore(id)).toBe(0.6);
    expect(store.isItemDone(id)).toBe(false);
    expect(store.countItems('math/real-numbers/')).toBe(0);
    for (let i = 0; i < 5; i++) store.recordAttempt(id, 1);
    const rec = store.item(id)!;
    expect(rec.best).toBe(1);
    expect(rec.attempts).toHaveLength(MAX_ATTEMPTS);
    expect(rec.firstAt).toBe('2026-11-15T00:00:00.000Z');
    expect(rec.lastAt).toBe('2026-11-15T00:07:00.000Z');
    expect(store.isItemDone(id)).toBe(true);
  });

  it('marks self-scored attempts and clamps scores into 0..1', () => {
    const store = createProgressStore(memoryKV());
    const rec = store.recordAttempt('math/x/mixed', 0.75, { self: true });
    expect(rec.attempts[0]).toMatchObject({ score: 0.75, self: true });
    expect(store.recordAttempt('math/x/a', 1.4).best).toBe(1);
    expect(store.recordAttempt('math/x/b', -1).best).toBe(0);
    expect(() => store.recordAttempt('math/x/c', Number.NaN)).toThrow(RangeError);
  });

  it('uses locale-free keys that keep the item version', () => {
    expect(itemKey('math/real-numbers', 'q3@2')).toBe('math/real-numbers/q3@2');
    const store = createProgressStore(memoryKV());
    store.markItem(itemKey('math/real-numbers', 'q3@1'));
    // a revised item (new version) starts afresh; the zh and en pages share the same key
    expect(store.isItemDone(itemKey('math/real-numbers', 'q3@2'))).toBe(false);
    expect(store.isItemDone('math/real-numbers/q3@1')).toBe(true);
  });

  it('can un-mark a chapter and reset', () => {
    const store = createProgressStore(memoryKV());
    store.markChapter('a');
    store.markChapter('a', false);
    expect(store.isChapterDone('a')).toBe(false);
    store.markItem('x');
    store.reset();
    expect(store.isItemDone('x')).toBe(false);
    expect(store.get()).toEqual(EMPTY);
  });

  it('notifies subscribers and the page', () => {
    const notify = vi.fn();
    const store = createProgressStore(memoryKV(), notify);
    const cb = vi.fn();
    const off = store.subscribe(cb);
    store.markItem('q1');
    store.markItem('q1'); // second mark of a solved item is a no-op
    expect(cb).toHaveBeenCalledTimes(1);
    expect(notify).toHaveBeenCalledTimes(1);
    store.recordAttempt('q1', 1); // an explicit attempt is always recorded
    expect(cb).toHaveBeenCalledTimes(2);
    off();
    store.markItem('q2');
    expect(cb).toHaveBeenCalledTimes(2);
  });

  it('reload picks up changes another tab wrote', () => {
    const kv = memoryKV();
    const a = createProgressStore(kv);
    const b = createProgressStore(kv);
    const cb = vi.fn();
    b.subscribe(cb);
    a.markItem('math/x/q1');
    expect(b.isItemDone('math/x/q1')).toBe(false);
    b.reload();
    expect(b.isItemDone('math/x/q1')).toBe(true);
    expect(cb).toHaveBeenCalledTimes(1);
  });

  it('works with no storage at all', () => {
    const store = createProgressStore(null);
    store.markChapter('a');
    expect(store.isChapterDone('a')).toBe(true);
  });

  it('survives storage that throws', () => {
    const angry: KV = {
      getItem: () => {
        throw new Error('blocked');
      },
      setItem: () => {
        throw new Error('blocked');
      },
    };
    const store = createProgressStore(angry);
    expect(() => store.markItem('a')).not.toThrow();
    expect(store.isItemDone('a')).toBe(true);
    expect(() => store.recordAttempt('b', 0.6)).not.toThrow();
    expect(store.bestScore('b')).toBe(0.6);
  });
});

describe('mergeProgress (export/import)', () => {
  const rec = (firstAt: string, lastAt: string, best: number, scores: [string, number][]) => ({ firstAt, lastAt, best, attempts: scores.map(([at, score]) => ({ at, score })) });
  it('unions chapters and items, keeping max best, earliest firstAt and latest lastAt', () => {
    const a: ProgressData = parseProgress(
      JSON.stringify({ v: 2, chapters: { c1: { done: true, at: '2026-11-03' } }, items: { i1: rec('2026-11-01', '2026-11-02', 0.6, [['2026-11-01', 0.2], ['2026-11-02', 0.6]]) } }),
    );
    const b: ProgressData = parseProgress(
      JSON.stringify({
        v: 2,
        chapters: { c1: { done: true, at: '2026-11-01' }, c2: { done: true, at: '2026-11-05' } },
        items: { i1: rec('2026-10-30', '2026-11-01', 0.2, [['2026-10-30', 0], ['2026-11-01', 0.2]]), i2: rec('2026-11-04', '2026-11-04', 1, [['2026-11-04', 1]]) },
      }),
    );
    const m = mergeProgress(a, b);
    expect(m.chapters).toEqual({ c1: { done: true, at: '2026-11-01' }, c2: { done: true, at: '2026-11-05' } });
    expect(m.items.i1).toEqual(rec('2026-10-30', '2026-11-02', 0.6, [['2026-10-30', 0], ['2026-11-01', 0.2], ['2026-11-02', 0.6]]));
    expect(m.items.i2.best).toBe(1);
    // merging is idempotent
    expect(mergeProgress(m, m)).toEqual(m);
  });
});
