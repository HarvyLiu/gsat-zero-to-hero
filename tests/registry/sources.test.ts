/**
 * The bibliography (src/data/registry/sources.json): https only, known licences, every id cited by
 * the other registries exists, and every URL is traceable to the frozen research (accuracy rule:
 * no URL may be invented). Chapter-level citations are checked by tests/curriculum/sources.test.ts.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { buildRegistry, LICENCES, registryProblems, REGISTRY_DATA, SOURCES, type RegistryFiles } from '../../src/data/registry';

const RESEARCH = fileURLToPath(new URL('../../research/verified-2026-11-15.json', import.meta.url));

/** Every string value in the frozen research, joined, so a URL can be looked up as a substring. */
function researchText(): string {
  const parts: string[] = [];
  const walk = (v: unknown) => {
    if (typeof v === 'string') parts.push(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === 'object') Object.values(v).forEach(walk);
  };
  walk(JSON.parse(readFileSync(RESEARCH, 'utf8')));
  return parts.join('\n');
}

/**
 * URLs that are not in the research but come from a file read in this repo. Each needs a reason.
 * The research did not cover the Barlow and JetBrains Mono fonts (06-critique §3), so their project
 * URLs and OFL status come from the LICENSE files bundled in their @fontsource packages.
 */
const NOT_FROM_RESEARCH: Record<string, string> = {
  'https://github.com/jpt/barlow': 'node_modules/@fontsource/barlow/LICENSE and barlow-condensed/LICENSE',
  'https://github.com/JetBrains/JetBrainsMono': 'node_modules/@fontsource/jetbrains-mono/LICENSE',
};

/** Every source id the registries themselves cite (facts, sittings, papers, formula sheets, misconceptions). */
function citedIds(): Map<string, string[]> {
  const cited = new Map<string, string[]>();
  const add = (owner: string, ids: readonly string[]) => ids.forEach((id) => cited.set(id, [...(cited.get(id) ?? []), owner]));
  for (const f of REGISTRY_DATA.facts.values()) add(`fact ${f.id}`, f.sources);
  for (const s of REGISTRY_DATA.sittings.values()) add(`sitting ${s.id}`, s.sources);
  for (const p of REGISTRY_DATA.papers.values()) add(`paper ${p.id}`, p.sources);
  for (const f of REGISTRY_DATA.formulaSheets.values()) add(`formula sheet ${f.paper}`, f.sources);
  for (const m of REGISTRY_DATA.misconceptions.values()) add(`misconception ${m.id}`, m.sources);
  return cited;
}

describe('sources.json', () => {
  it('loads a non-empty bibliography', () => {
    expect(SOURCES.size).toBeGreaterThan(50);
  });

  it('uses https URLs that parse', () => {
    const bad = [...SOURCES.values()].filter((s) => {
      try {
        return new URL(s.url).protocol !== 'https:';
      } catch {
        return true;
      }
    });
    expect(bad.map((s) => s.id)).toEqual([]);
  });

  it('gives every source a licence that exists in licences.json', () => {
    const bad = [...SOURCES.values()].filter((s) => !LICENCES.has(s.licence)).map((s) => `${s.id} → ${s.licence}`);
    expect(bad).toEqual([]);
  });

  it('resolves every source id cited by the other registries', () => {
    const unknown = [...citedIds()].filter(([id]) => !SOURCES.has(id)).map(([id, owners]) => `${id} (cited by ${owners.join(', ')})`);
    expect(unknown).toEqual([]);
  });

  it('takes every URL from the frozen research, or from a file listed with a reason', () => {
    const text = researchText();
    const urls = [
      ...[...SOURCES.values()].map((s) => ({ owner: `source ${s.id}`, url: s.url })),
      ...[...LICENCES.values()].filter((l) => l.url).map((l) => ({ owner: `licence ${l.id}`, url: l.url! })),
      ...[...REGISTRY_DATA.examItems.values()].flatMap((i) =>
        [i.paperUrl, i.answerUrl, i.rubricUrl].filter((u): u is string => !!u).map((url) => ({ owner: `exam item ${i.id}`, url })),
      ),
    ];
    const untraced = urls.filter(({ url }) => !text.includes(url) && !(url in NOT_FROM_RESEARCH)).map(({ owner, url }) => `${owner}: ${url}`);
    expect(untraced).toEqual([]);
    // the allow-list must not go stale either
    const allowListed = new Set(urls.map((u) => u.url));
    expect(Object.keys(NOT_FROM_RESEARCH).filter((u) => !allowListed.has(u))).toEqual([]);
  });

  it('stamps every source with a real access date no later than the research freeze', () => {
    const bad = [...SOURCES.values()].filter((s) => Number.isNaN(Date.parse(s.accessed)) || s.accessed > '2026-11-15').map((s) => s.id);
    expect(bad).toEqual([]);
  });

  it('keeps CEEC material on CEEC licences: the 考試說明 PDFs under ceec-nonprofit, everything else link-only', () => {
    // only the spec PDFs carry the non-profit notice in the research; papers, rubrics, brochures,
    // press releases and 選才電子報 state no reuse terms
    const SPECS = new Set(['ceec-spec-general', 'ceec-spec-math', 'ceec-spec-science', 'ceec-spec-social', 'ceec-spec-chinese']);
    const bad = [...SOURCES.values()]
      .filter((s) => new URL(s.url).hostname.endsWith('ceec.edu.tw'))
      .filter((s) => s.licence !== (SPECS.has(s.id) ? 'ceec-nonprofit' : 'link-only'))
      .map((s) => `${s.id} (${s.licence})`);
    expect(bad).toEqual([]);
    expect([...SPECS].filter((id) => !SOURCES.has(id))).toEqual([]);
  });

  it('files statutes as law under law-public, and dictionaries under the MOE licence', () => {
    const laws = [...SOURCES.values()].filter((s) => s.kind === 'law');
    expect(laws.length).toBeGreaterThan(0);
    expect(laws.filter((s) => s.licence !== 'law-public').map((s) => s.id)).toEqual([]);
    const dicts = [...SOURCES.values()].filter((s) => s.kind === 'dictionary');
    expect(dicts.filter((s) => s.licence !== 'cc-by-nd-3.0-tw').map((s) => s.id)).toEqual([]);
  });

  it('versions the 116 brochure as the first edition of 115/8/4', () => {
    expect(SOURCES.get('ceec-116-brochure')?.version).toBe('初版 115/8/4');
  });

  it('carries the exact attribution PhET requires for historical sims', () => {
    expect(SOURCES.get('phet-historical')?.attribution?.en).toBe(
      'Simulation by PhET Interactive Simulations, University of Colorado Boulder, licensed under CC BY 4.0 (https://phet.colorado.edu)',
    );
  });
});

describe('registryProblems (sources)', () => {
  const base: RegistryFiles = {
    sources: { 'sources.json': [{ id: 'a', title: 'A', url: 'https://example.org/a', publisher: 'P', kind: 'web', licence: 'nope', accessed: '2026-11-15' }] },
    licences: { 'licences.json': [] },
    facts: { 'facts.json': [] },
    misconceptions: {},
    sittings: { 'sittings.json': [] },
    papers: { 'papers.json': [] },
    formulaSheets: { 'formula-sheets.json': [] },
    examItems: {},
  };

  it('reports a source whose licence is missing', () => {
    expect(registryProblems(buildRegistry(base))).toEqual(['source a has unknown licence "nope"']);
  });

  it('rejects an http URL at load time', () => {
    const files = { ...base, sources: { 'sources.json': [{ ...(base.sources['sources.json'] as object[])[0], url: 'http://example.org/a' }] } };
    expect(() => buildRegistry(files)).toThrow(/sources must be https/);
  });

  it('rejects a duplicate id across entries', () => {
    const entry = (base.sources['sources.json'] as object[])[0];
    expect(() => buildRegistry({ ...base, sources: { 'sources.json': [entry, entry] } })).toThrow(/Duplicate source id "a"/);
  });
});
