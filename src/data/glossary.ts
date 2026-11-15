/**
 * The glossary, which is also the concept registry: a chapter's `newConcepts`/`uses` ids are the
 * same ids <Term t="…"> uses, so the no-jump tests can check the outline and the MDX together.
 *
 * Terms live in src/data/terms/<subject>/<chapter-slug>.json as { "terms": TermEntry[] } (one file
 * per chapter, so chapters can be written in parallel) and are merged here. Merging validates every
 * entry against schema.TermEntry and throws on:
 *  - a duplicate id (one owner per concept: docs/design/06-critique.md §1 item 2);
 *  - an id whose prefix is not the folder's subject (the folder is the owner);
 *  - a `deepens` link to a term that does not exist.
 * The chapter that introduces a term is derived from course data (newConcepts), never stored here.
 *
 * Build-time only: never import this from a client island, or every term ships to the browser.
 */
import { z } from 'astro/zod';
import { SUBJECT_IDS, TermEntry } from './schema';

export type { TermEntry };

const OWNERS = new Set<string>(['site', ...SUBJECT_IDS]);
const FILE_RE = /(?:^|\/)terms\/([a-z]+)\/([a-z0-9-]+)\.json$/;

/** Merge glossary files (path → parsed JSON). Throws with the file and index of the first bad entry. */
export function mergeTerms(files: Record<string, unknown>): Map<string, TermEntry> {
  const out = new Map<string, TermEntry>();
  const from = new Map<string, string>();
  for (const path of Object.keys(files).sort()) {
    const m = FILE_RE.exec(path.replace(/\\/g, '/'));
    if (!m || !OWNERS.has(m[1])) {
      throw new Error(`Glossary file ${path} must be src/data/terms/<subject>/<chapter-slug>.json (subject: site or ${SUBJECT_IDS.join(', ')}).`);
    }
    const owner = m[1];
    const file = files[path] as { terms?: unknown } | null;
    if (!file || typeof file !== 'object' || !Array.isArray(file.terms)) {
      throw new Error(`Glossary file ${path} must contain { "terms": [ … ] }.`);
    }
    file.terms.forEach((raw, i) => {
      const parsed = TermEntry.safeParse(raw);
      if (!parsed.success) throw new Error(`Glossary file ${path}, terms[${i}] is invalid:\n${z.prettifyError(parsed.error)}`);
      const term = parsed.data;
      const prefix = term.id.slice(0, term.id.indexOf('.'));
      if (prefix !== owner) {
        throw new Error(`Term "${term.id}" in ${path} must start with "${owner}." (terms are owned by the subject folder they live in).`);
      }
      const earlier = from.get(term.id);
      if (earlier) throw new Error(`Duplicate term id "${term.id}" in ${path} (already defined in ${earlier}).`);
      out.set(term.id, term);
      from.set(term.id, path);
    });
  }
  for (const term of out.values()) {
    if (term.deepens && !out.has(term.deepens)) {
      throw new Error(`Term "${term.id}" deepens "${term.deepens}", which is not in the glossary (defined in ${from.get(term.id)}).`);
    }
  }
  return out;
}

/** Every term on the site, keyed by id. Empty until lessons add term files. */
export const TERMS: Map<string, TermEntry> = mergeTerms(import.meta.glob('./terms/**/*.json', { eager: true, import: 'default' }));

export function getTerm(id: string): TermEntry | undefined {
  return TERMS.get(id);
}
