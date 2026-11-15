/**
 * The licence registry (src/data/registry/licences.json): the seed set from the plan exists, the
 * permission flags are internally consistent, and the uncertain cases say so in their note.
 */
import { describe, expect, it } from 'vitest';
import { buildRegistry, LICENCES, registryProblems, SOURCES, type RegistryFiles } from '../../src/data/registry';

const SEED = [
  'ceec-nonprofit',
  'link-only',
  'naer-open',
  'ogdl-tw-1',
  'cc-by-nd-3.0-tw',
  'cc-by-4.0',
  'cc-by-nc',
  'geogebra-nc',
  'public-domain',
  'mit',
  'bsd-3',
  'isc',
  'ofl-1.1',
  'law-public',
];

const lic = (id: string) => {
  const l = LICENCES.get(id);
  if (!l) throw new Error(`licence ${id} missing`);
  return l;
};

describe('licences.json', () => {
  it('has every seed licence from the plan, and nothing unexpected', () => {
    expect([...LICENCES.keys()].sort()).toEqual([...SEED].sort());
  });

  it('keeps link-only and verbatim-only consistent with the modify/re-host flags', () => {
    for (const l of LICENCES.values()) {
      if (l.mayQuote === 'link-only') expect({ id: l.id, rehost: l.mayRehost, modify: l.mayModify }).toEqual({ id: l.id, rehost: false, modify: false });
      if (l.mayQuote === 'verbatim-only') expect({ id: l.id, modify: l.mayModify }).toEqual({ id: l.id, modify: false });
    }
  });

  it('marks the non-commercial licences as such', () => {
    for (const id of ['ceec-nonprofit', 'cc-by-nc', 'geogebra-nc']) expect([id, lic(id).nonCommercialOnly]).toEqual([id, true]);
    for (const id of ['naer-open', 'ogdl-tw-1', 'cc-by-nd-3.0-tw', 'cc-by-4.0', 'public-domain', 'mit', 'bsd-3', 'isc', 'ofl-1.1', 'law-public']) {
      expect([id, lic(id).nonCommercialOnly]).toEqual([id, false]);
    }
  });

  it('encodes the specific rules the research verified', () => {
    // CEEC past papers: never re-host, link by year, subject and number
    expect(lic('link-only').mayQuote).toBe('link-only');
    // MOE dictionaries: verbatim only, no edits, attribution
    expect(lic('cc-by-nd-3.0-tw')).toMatchObject({ mayQuote: 'verbatim-only', mayModify: false, attributionRequired: true });
    // Natural Earth: credit unnecessary
    expect(lic('public-domain').attributionRequired).toBe(false);
    // 政府資料開放授權條款: attribution is a condition of the grant
    expect(lic('ogdl-tw-1')).toMatchObject({ attributionRequired: true, url: 'https://data.gov.tw/license' });
    // NAER open-data declaration
    expect(lic('naer-open').url).toBe('https://www.naer.edu.tw/PageDoc?fid=324');
  });

  it('says where the research is unsure', () => {
    expect(lic('cc-by-nc').note).toMatch(/version is UNCONFIRMED/);
    expect(lic('cc-by-nc').note).toMatch(/2026-03-29/);
    expect(lic('law-public').note).toMatch(/§9\(1\)\(1\)/);
    expect(lic('law-public').note).toMatch(/§9\(1\)\(5\)/);
    expect(lic('link-only').note).toMatch(/1090203b/);
    expect(lic('geogebra-nc').note).toMatch(/could not confirm/);
  });

  it('gives any licence URL as https', () => {
    const bad = [...LICENCES.values()].filter((l) => l.url && !l.url.startsWith('https://')).map((l) => l.id);
    expect(bad).toEqual([]);
  });

  it('is used by the sources that need it', () => {
    const used = new Set([...SOURCES.values()].map((s) => s.licence));
    for (const id of ['ceec-nonprofit', 'link-only', 'naer-open', 'cc-by-nd-3.0-tw', 'cc-by-4.0', 'cc-by-nc', 'public-domain', 'mit', 'ofl-1.1', 'law-public']) {
      expect([id, used.has(id)]).toEqual([id, true]);
    }
  });
});

describe('registryProblems (licences)', () => {
  const files = (licence: object): RegistryFiles => ({
    sources: { 'sources.json': [] },
    licences: { 'licences.json': [licence] },
    facts: { 'facts.json': [] },
    misconceptions: {},
    sittings: { 'sittings.json': [] },
    papers: { 'papers.json': [] },
    formulaSheets: { 'formula-sheets.json': [] },
    examItems: {},
  });
  const ok = { id: 'x', name: 'X', mayQuote: 'link-only', mayModify: false, mayRehost: false, attributionRequired: true, nonCommercialOnly: false };

  it('accepts a consistent licence', () => {
    expect(registryProblems(buildRegistry(files(ok)))).toEqual([]);
  });

  it('flags a link-only licence that allows re-hosting', () => {
    expect(registryProblems(buildRegistry(files({ ...ok, mayRehost: true })))).toEqual(['licence x: link-only cannot allow re-hosting or modifying']);
  });

  it('flags a verbatim-only licence that allows modifying', () => {
    expect(registryProblems(buildRegistry(files({ ...ok, mayQuote: 'verbatim-only', mayModify: true })))).toEqual(['licence x: verbatim-only cannot allow modifying']);
  });
});
