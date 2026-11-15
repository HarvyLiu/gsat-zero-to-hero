/**
 * The curriculum code registry: every official 108課綱 code the course can cite, keyed
 * `<domain>:<ASCII code>` (docs/design/06-critique.md §1 item 8: bare codes collide across domains).
 *
 * The data is generated from the frozen research by scripts/import-codes.mjs into
 * src/data/registry/codes/<domain>.json. Never hand-edit those files: corrections go in
 * src/data/registry/codes/overrides.json and the script is re-run (npm run import:codes).
 *
 * Loading validates every entry against schema.CodeEntry and throws on:
 *  - a file that is not <domain>.json for a known domain, or an entry filed under the wrong domain;
 *  - a duplicate key;
 *  - a dependsOn key that is not in the registry.
 *
 * Works under Vite/Astro/Vitest (import.meta.glob) and under plain Node with type stripping
 * (scripts), where import.meta.glob does not exist and the files are read from disk.
 *
 * Build-time only: the registry is about 1.2 MB of JSON, so never import this from a client island;
 * pass the few entries a component needs as props instead.
 */
import { z } from 'astro/zod';
import { CodeEntry, DOMAINS, type Domain, type SubjectId } from './schema.ts';

export type { CodeEntry };

const FILE_RE = /(?:^|\/)registry\/codes\/([a-z-]+)\.json$/;
const DOMAIN_SET = new Set<string>(DOMAINS);

/** Merge registry files (path → parsed JSON). Throws with the file and index of the first bad entry. */
export function mergeCodes(files: Record<string, unknown>): Map<string, CodeEntry> {
  const out = new Map<string, CodeEntry>();
  const from = new Map<string, string>();
  for (const path of Object.keys(files).sort()) {
    const m = FILE_RE.exec(path.replace(/\\/g, '/'));
    if (!m || !DOMAIN_SET.has(m[1])) {
      throw new Error(`Code registry file ${path} must be src/data/registry/codes/<domain>.json (domain: ${DOMAINS.join(', ')}).`);
    }
    const domain = m[1] as Domain;
    const list = files[path];
    if (!Array.isArray(list)) throw new Error(`Code registry file ${path} must contain an array of CodeEntry.`);
    list.forEach((raw, i) => {
      const parsed = CodeEntry.safeParse(raw);
      if (!parsed.success) throw new Error(`Code registry file ${path}, [${i}] is invalid:\n${z.prettifyError(parsed.error)}`);
      const entry = parsed.data;
      if (entry.domain !== domain || !entry.key.startsWith(`${domain}:`)) {
        throw new Error(`Code "${entry.key}" (domain ${entry.domain}) is filed in ${path}; it belongs in ${entry.domain}.json with a "${entry.domain}:" key.`);
      }
      const earlier = from.get(entry.key);
      if (earlier) throw new Error(`Duplicate code key "${entry.key}" in ${path} (already defined in ${earlier}).`);
      out.set(entry.key, entry);
      from.set(entry.key, path);
    });
  }
  for (const entry of out.values()) {
    for (const dep of entry.dependsOn) {
      if (!out.has(dep)) throw new Error(`Code "${entry.key}" depends on "${dep}", which is not in the registry (defined in ${from.get(entry.key)}).`);
    }
  }
  return out;
}

/** Plain Node fallback: read the same files the glob would return. */
function readRegistryFiles(): Record<string, unknown> {
  const fs = process.getBuiltinModule('node:fs');
  const dir = new URL('./registry/codes/', import.meta.url);
  const files: Record<string, unknown> = {};
  for (const name of fs.readdirSync(dir).sort()) {
    if (!name.endsWith('.json') || name === 'overrides.json') continue;
    files[`./registry/codes/${name}`] = JSON.parse(fs.readFileSync(new URL(name, dir), 'utf8'));
  }
  return files;
}

function loadRegistryFiles(): Record<string, unknown> {
  try {
    // Vite rewrites this call at build time; overrides.json is input to the import script, not data.
    return import.meta.glob(['./registry/codes/*.json', '!./registry/codes/overrides.json'], { eager: true, import: 'default' });
  } catch {
    // import.meta.glob is not a function outside Vite.
    return readRegistryFiles();
  }
}

/** Every curriculum code, keyed `<domain>:<ASCII code>`, in file (domain) then key order. */
export const CODES: Map<string, CodeEntry> = mergeCodes(loadRegistryFiles());

const BY_SUBJECT = new Map<SubjectId, CodeEntry[]>();
for (const entry of CODES.values()) {
  for (const s of entry.subjects) {
    const list = BY_SUBJECT.get(s);
    if (list) list.push(entry);
    else BY_SUBJECT.set(s, [entry]);
  }
}

export function getCode(key: string): CodeEntry | undefined {
  return CODES.get(key);
}

/** Codes whose `subjects` include `subject` (codes a subject's syllabus lists, plus the background codes its bridges cite). */
export function codesFor(subject: SubjectId): CodeEntry[] {
  return [...(BY_SUBJECT.get(subject) ?? [])];
}
