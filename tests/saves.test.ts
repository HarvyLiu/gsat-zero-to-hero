import { describe, expect, it } from 'vitest';
import { createSavesStore, parseSaves, SAVES_KEY } from '../src/lib/saves';
import { createProgressStore, STORAGE_KEY, type KV } from '../src/lib/progress';

function memoryKV(): KV & { raw: Map<string, string> } {
  const raw = new Map<string, string>();
  return { raw, getItem: (k) => raw.get(k) ?? null, setItem: (k, v) => void raw.set(k, v) };
}

const throwing: KV = {
  getItem() {
    throw new Error('blocked');
  },
  setItem() {
    throw new Error('blocked');
  },
};

describe('parseSaves', () => {
  it('returns empty data for missing, corrupt or wrong-version input', () => {
    for (const raw of [null, '', '{oops', '[]', '{"v":2,"items":{}}', '{"v":1}', '{"v":1,"items":[]}']) {
      expect(parseSaves(raw)).toEqual({ v: 1, items: {} });
    }
  });
  it('drops malformed items but keeps good ones', () => {
    const raw = JSON.stringify({ v: 1, items: { a: { value: 3, at: 'x' }, b: 5, c: { at: 'x' } } });
    expect(parseSaves(raw)).toEqual({ v: 1, items: { a: { value: 3, at: 'x' } } });
  });
});

describe('saves store', () => {
  it('saves, loads, lists and removes values in one storage entry', () => {
    const kv = memoryKV();
    const s = createSavesStore(kv);
    expect(s.load('cpu')).toBeNull();
    s.save('cpu', { pc: 4, regs: [1, 2] });
    s.save('asm', 'MOV A, 1');
    expect(s.load<{ pc: number; regs: number[] }>('cpu')).toEqual({ pc: 4, regs: [1, 2] });
    expect(s.load<string>('asm')).toBe('MOV A, 1');
    expect(s.keys()).toEqual(['asm', 'cpu']);
    expect([...kv.raw.keys()]).toEqual([SAVES_KEY]);
    const stored = JSON.parse(kv.raw.get(SAVES_KEY)!);
    expect(stored.v).toBe(1);
    expect(typeof stored.items.cpu.at).toBe('string');
    s.remove('cpu');
    expect(s.load('cpu')).toBeNull();
    expect(s.keys()).toEqual(['asm']);
  });

  it('keeps falsy values distinct from missing ones', () => {
    const s = createSavesStore(memoryKV());
    s.save('zero', 0);
    s.save('nil', null);
    s.save('no', false);
    expect(s.load('zero')).toBe(0);
    expect(s.load('no')).toBe(false);
    expect(s.keys()).toContain('nil');
    s.save('zero', undefined);
    expect(s.keys()).not.toContain('zero');
  });

  it('stores a copy, not a live reference', () => {
    const s = createSavesStore(memoryKV());
    const v = { n: 1 };
    s.save('k', v);
    v.n = 2;
    expect(s.load('k')).toEqual({ n: 1 });
  });

  it('persists across stores sharing the same storage', () => {
    const kv = memoryKV();
    createSavesStore(kv).save('k', [1, 2, 3]);
    expect(createSavesStore(kv).load('k')).toEqual([1, 2, 3]);
  });

  it('sees writes made by another store (another island or tab)', () => {
    const kv = memoryKV();
    const a = createSavesStore(kv);
    const b = createSavesStore(kv);
    a.save('x', 1);
    expect(b.load('x')).toBe(1);
  });

  it('ignores a corrupt entry and starts fresh', () => {
    const kv = memoryKV();
    kv.raw.set(SAVES_KEY, '{not json');
    const s = createSavesStore(kv);
    expect(s.keys()).toEqual([]);
    s.save('k', 1);
    expect(s.load('k')).toBe(1);
  });

  it('falls back to memory when storage throws', () => {
    const s = createSavesStore(throwing);
    expect(s.load('k')).toBeNull();
    s.save('k', { a: 1 });
    expect(s.load('k')).toEqual({ a: 1 });
    expect(s.keys()).toEqual(['k']);
    s.remove('k');
    expect(s.keys()).toEqual([]);
  });

  it('keeps working in memory when writes start failing (quota full)', () => {
    const kv = memoryKV();
    const s = createSavesStore(kv);
    s.save('a', 1);
    kv.setItem = () => {
      throw new Error('quota');
    };
    s.save('b', 2);
    expect(s.load('a')).toBe(1);
    expect(s.load('b')).toBe(2);
  });

  it('works with no storage at all', () => {
    const s = createSavesStore(null);
    s.save('k', 'v');
    expect(s.load('k')).toBe('v');
  });

  it('shares one storage with the progress store without touching its entry', () => {
    const kv = memoryKV();
    const p = createProgressStore(kv);
    const s = createSavesStore(kv);
    expect(SAVES_KEY).not.toBe(STORAGE_KEY);
    p.recordAttempt('math/real-numbers/q1@1', 0.6);
    s.save('mixed-draft', 'my written answer');
    p.markChapter('math/real-numbers');
    expect(s.load('mixed-draft')).toBe('my written answer');
    expect(createProgressStore(kv).bestScore('math/real-numbers/q1@1')).toBe(0.6);
    expect([...kv.raw.keys()].sort()).toEqual([SAVES_KEY, STORAGE_KEY].sort());
  });

  it('ignores values that cannot be serialised', () => {
    const s = createSavesStore(memoryKV());
    const cyc: Record<string, unknown> = {};
    cyc.self = cyc;
    expect(() => s.save('c', cyc)).not.toThrow();
    expect(s.load('c')).toBeNull();
  });
});

describe('saves store edge cases', () => {
  it('can be destructured: methods do not depend on this', () => {
    const { load, save, remove, keys } = createSavesStore(memoryKV());
    save('k', 1);
    expect(load('k')).toBe(1);
    expect(() => save('k', undefined)).not.toThrow();
    expect(load('k')).toBeNull();
    save('j', 2);
    remove('j');
    expect(keys()).toEqual([]);
  });

  it('treats inherited names like toString as ordinary keys', () => {
    const kv = memoryKV();
    const s = createSavesStore(kv);
    expect(s.load('toString')).toBeNull();
    let writes = 0;
    const set = kv.setItem;
    kv.setItem = (k, v) => {
      writes++;
      set(k, v);
    };
    s.remove('toString');
    expect(writes).toBe(0);
    s.save('toString', 'x');
    expect(s.load('toString')).toBe('x');
    expect(s.keys()).toEqual(['toString']);
  });

  it('keeps a save under __proto__ across a re-parse', () => {
    const kv = memoryKV();
    const s = createSavesStore(kv);
    s.save('__proto__', { a: 1 });
    expect(s.keys()).toEqual(['__proto__']);
    expect(s.load('__proto__')).toEqual({ a: 1 });
    const again = createSavesStore(kv);
    expect(again.keys()).toEqual(['__proto__']);
    expect(again.load('__proto__')).toEqual({ a: 1 });
    expect(parseSaves(kv.raw.get(SAVES_KEY) ?? null).items.__proto__).toBeDefined();
    again.remove('__proto__');
    expect(again.keys()).toEqual([]);
    expect(again.load('__proto__')).toBeNull();
  });
});
