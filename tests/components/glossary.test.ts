import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { describe, expect, it } from 'vitest';
import { TERMS, getTerm, mergeTerms } from '../../src/data/glossary';

const TERMS_DIR = join(__dirname, '..', '..', 'src', 'data', 'terms');
const LESSONS_DIR = join(__dirname, '..', '..', 'src', 'content', 'lessons');

/** placeholder entry; the values only exercise the merge logic */
const entry = (id: string, extra: Record<string, unknown> = {}) => ({
  id,
  zh: '測試詞',
  en: 'test term',
  def: { 'zh-tw': '測試用定義。', en: 'A definition used only by this test.' },
  source: { id: 'test-source' },
  ...extra,
});

function walk(dir: string, ext: string): string[] {
  let out: string[] = [];
  let names: string[] = [];
  try {
    names = readdirSync(dir);
  } catch {
    return out;
  }
  for (const name of names) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out = out.concat(walk(p, ext));
    else if (name.endsWith(ext)) out.push(p);
  }
  return out;
}

describe('mergeTerms', () => {
  it('merges entries from several chapter files and applies schema defaults', () => {
    const merged = mergeTerms({
      './terms/math/a.json': { terms: [entry('math.alpha')] },
      './terms/math/b.json': { terms: [entry('math.beta', { deepens: 'math.alpha' })] },
      './terms/site/c.json': { terms: [entry('site.gamma')] },
    });
    expect([...merged.keys()].sort()).toEqual(['math.alpha', 'math.beta', 'site.gamma']);
    expect(merged.get('math.alpha')?.kind).toBe('concept');
  });

  it('throws on a duplicate id across files and names both files', () => {
    expect(() =>
      mergeTerms({
        './terms/math/a.json': { terms: [entry('math.alpha')] },
        './terms/math/b.json': { terms: [entry('math.alpha')] },
      }),
    ).toThrow(/Duplicate term id "math\.alpha" in \.\/terms\/math\/b\.json \(already defined in \.\/terms\/math\/a\.json\)/);
  });

  it('throws on a duplicate id inside one file', () => {
    expect(() => mergeTerms({ './terms/math/a.json': { terms: [entry('math.alpha'), entry('math.alpha')] } })).toThrow(/Duplicate term id/);
  });

  it('rejects an entry that fails the TermEntry schema', () => {
    const bad = { ...entry('math.alpha'), def: { 'zh-tw': '', en: 'x' } };
    expect(() => mergeTerms({ './terms/math/a.json': { terms: [bad] } })).toThrow(/terms\[0\] is invalid/);
    expect(() => mergeTerms({ './terms/math/a.json': { terms: [{ ...entry('math.alpha'), extra: 1 }] } })).toThrow(/invalid/);
  });

  it('rejects an id owned by another subject folder', () => {
    expect(() => mergeTerms({ './terms/physics/a.json': { terms: [entry('math.alpha')] } })).toThrow(/must start with "physics\."/);
  });

  it('rejects files outside <subject>/<slug>.json and files without a terms array', () => {
    expect(() => mergeTerms({ './terms/a.json': { terms: [] } })).toThrow(/must be src\/data\/terms/);
    expect(() => mergeTerms({ './terms/music/a.json': { terms: [] } })).toThrow(/must be src\/data\/terms/);
    expect(() => mergeTerms({ './terms/math/a.json': { items: [] } })).toThrow(/must contain \{ "terms"/);
  });

  it('rejects a deepens link to a missing term', () => {
    expect(() => mergeTerms({ './terms/math/a.json': { terms: [entry('math.beta', { deepens: 'math.nowhere' })] } })).toThrow(
      /deepens "math\.nowhere"/,
    );
  });

  it('accepts Windows-style paths', () => {
    expect(mergeTerms({ '.\\terms\\math\\a.json': { terms: [entry('math.alpha')] } }).has('math.alpha')).toBe(true);
  });
});

describe('the real glossary', () => {
  it('loads every term file under src/data/terms (an empty folder is fine)', () => {
    const files = walk(TERMS_DIR, '.json');
    const count = files.reduce((n, f) => n + (JSON.parse(readFileSync(f, 'utf8')) as { terms: unknown[] }).terms.length, 0);
    expect(TERMS.size).toBe(count);
  });

  it('returns undefined for an unknown id', () => {
    expect(getTerm('math.this-term-does-not-exist')).toBeUndefined();
  });

  it('defines every <Term t> and [[id]] used in the lessons', () => {
    const missing: string[] = [];
    for (const f of walk(LESSONS_DIR, '.mdx')) {
      readFileSync(f, 'utf8')
        .split(/\r?\n/)
        .forEach((line, i) => {
          const ids = [...line.matchAll(/<Term\s+t=["']([^"']+)["']/g), ...line.matchAll(/\[\[([^\]|]+)(?:\|[^\]]*)?\]\]/g)].map((m) => m[1].trim());
          for (const id of ids) if (!TERMS.has(id)) missing.push(`${relative(LESSONS_DIR, f)}:${i + 1} "${id}"`);
        });
    }
    expect(missing).toEqual([]);
  });
});
