/**
 * Documented misconceptions (src/data/registry/misconceptions/<subject>.json). Only documented errors
 * go in, each with a source; status gates what renders (06-critique §3 and §7 item 7):
 *   verified = documented and the source was re-opened by the verifier;
 *   pending  = the source page was not fetched, so no refutation box until it is (math M3/M4/M5/M7);
 *   low-p    = only a low success rate was reported, not a coded error (math M10/M11).
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { CodeKey, MisconceptionDef } from '../../src/data/schema';
import { buildRegistry, getMisconception, MISCONCEPTIONS, REGISTRY_DATA, registryProblems, SOURCES, subjectOfFile, type RegistryFiles } from '../../src/data/registry';

const SRC = fileURLToPath(new URL('../../src/', import.meta.url));
const CODES_FILE = join(SRC, 'data', 'codes.ts');
const CODES: Map<string, unknown> | undefined = existsSync(CODES_FILE) ? (await import('../../src/data/codes')).CODES : undefined;

/**
 * Pages the 2026-11-15 verification says it did NOT fetch (math.verification.unverifiable:
 * "Those 選才電子報 pages (sid=0N107367513929908281 and 0N107399949290380345) were not fetched").
 * A misconception resting only on them cannot be 'verified'.
 */
const UNFETCHED = new Set(['ceec-epaper-112-matha-rubric', 'ceec-epaper-112-mathb-rubric']);

const all = [...MISCONCEPTIONS.values()];

describe('misconceptions/*.json', () => {
  it('loads the documented math misconceptions', () => {
    expect(all.filter((m) => m.id.startsWith('math.')).length).toBe(12);
  });

  it('validates every entry and gives each at least one known source', () => {
    for (const m of all) {
      expect(MisconceptionDef.safeParse(m).success).toBe(true);
      expect(m.sources.length).toBeGreaterThan(0);
      expect([m.id, m.sources.filter((id) => !SOURCES.has(id))]).toEqual([m.id, []]);
    }
  });

  it('names every entry after the file it lives in', () => {
    for (const m of all) expect(m.id.startsWith(`${subjectOfFile(REGISTRY_DATA.fileOf.get(m.id) ?? '')}.`)).toBe(true);
  });

  it('never marks a misconception verified when its only error source was not opened', () => {
    const bad = all.filter((m) => m.status === 'verified' && m.sources.some((s) => UNFETCHED.has(s))).map((m) => m.id);
    expect(bad).toEqual([]);
    for (const m of all.filter((x) => x.sources.some((s) => UNFETCHED.has(s)))) expect([m.id, m.status]).toEqual([m.id, 'pending']);
  });

  it('keeps the statuses the verification gave (M3/M4/M5/M7 pending, M10/M11 low-p)', () => {
    const status = (id: string) => getMisconception(id)?.status;
    expect(status('math.unjustified-conclusion')).toBe('pending');
    expect(status('math.coordinate-sign')).toBe('pending');
    expect(status('math.trapezoid-area-half')).toBe('pending');
    expect(status('math.vanishing-point')).toBe('pending');
    expect(status('math.cone-section-shapes')).toBe('low-p');
    expect(status('math.low-p-115-matha')).toBe('low-p');
    expect(status('math.polar-coordinate-order')).toBe('verified');
    expect(status('math.product-always-bigger')).toBe('verified');
  });

  it('reports low-p entries as success rates, not as coded errors', () => {
    for (const m of all.filter((x) => x.status === 'low-p')) expect([m.id, /P\s?=\s?\d+%/.test(m.wrong['zh-tw'])]).toEqual([m.id, true]);
  });

  it('uses curriculum codes that look like CodeKeys', () => {
    for (const m of all) for (const c of m.codes) expect([m.id, c, CodeKey.safeParse(c).success]).toEqual([m.id, c, true]);
  });

  it.skipIf(!CODES)('uses curriculum codes that exist in the code registry', () => {
    expect(all.flatMap((m) => m.codes.filter((c) => !CODES!.has(c)).map((c) => `${m.id}: ${c}`))).toEqual([]);
  });

  it('gives both languages for the wrong and the right idea, and they differ', () => {
    for (const m of all) {
      expect(m.wrong['zh-tw']).not.toBe(m.right['zh-tw']);
      expect(m.wrong.en).not.toBe(m.right.en);
    }
  });
});

describe('registryProblems (misconceptions)', () => {
  const entry = {
    id: 'math.x',
    wrong: { 'zh-tw': '錯', en: 'wrong' },
    right: { 'zh-tw': '對', en: 'right' },
    sources: ['s'],
    status: 'verified',
  };
  const files = (path: string, sources: object[] = []): RegistryFiles => ({
    sources: { 'sources.json': sources },
    licences: { 'licences.json': [{ id: 'l', name: 'L', mayQuote: 'yes', mayModify: true, mayRehost: true, attributionRequired: false, nonCommercialOnly: false }] },
    facts: { 'facts.json': [] },
    misconceptions: { [path]: [entry] },
    sittings: { 'sittings.json': [] },
    papers: { 'papers.json': [] },
    formulaSheets: { 'formula-sheets.json': [] },
    examItems: {},
  });
  const source = { id: 's', title: 'S', url: 'https://example.org/', publisher: 'P', kind: 'web', licence: 'l', accessed: '2026-11-15' };

  it('accepts an entry with a known source in the right file', () => {
    expect(registryProblems(buildRegistry(files('misconceptions/math.json', [source])))).toEqual([]);
  });

  it('flags an unknown source', () => {
    expect(registryProblems(buildRegistry(files('misconceptions/math.json')))).toEqual(['misconception math.x cites unknown source "s"']);
  });

  it('flags an entry filed under another subject', () => {
    expect(registryProblems(buildRegistry(files('misconceptions/physics.json', [source])))).toEqual([
      'misconception math.x is in physics.json but its id does not start with "physics."',
    ]);
  });

  it('rejects an entry with no source at load time', () => {
    const bad: RegistryFiles = { ...files('misconceptions/math.json', [source]), misconceptions: { 'misconceptions/math.json': [{ ...entry, sources: [] }] } };
    expect(() => buildRegistry(bad)).toThrow(/misconception misconceptions\/math\.json is invalid/);
  });

  it('rejects a duplicate id across subject files', () => {
    const dup: RegistryFiles = { ...files('misconceptions/math.json', [source]), misconceptions: { 'a/math.json': [entry], 'b/math.json': [entry] } };
    expect(() => buildRegistry(dup)).toThrow(/Duplicate misconception id "math.x" in b\/math.json \(already defined in a\/math.json\)/);
  });
});
