/**
 * Exam, fact, source and licence registries (docs/design/05-platform.md §1.3, with the
 * docs/design/06-critique.md fixes: facts carry dated versions plus a review-by date, misconceptions
 * are gated by status, official items are indexed by link only).
 *
 * Files (all JSON arrays, validated against src/data/schema.ts or the small schemas below):
 *   registry/sources.json            SourceDef[]       the bibliography every page cites by id
 *   registry/licences.json           LicenceDef[]      what each source's licence lets us do
 *   registry/facts.json              FactDef[]         time-sensitive values (law, wages, exam rules)
 *   registry/misconceptions/<s>.json MisconceptionDef[] documented errors, ids '<subject>.<kebab>'
 *   registry/exam/sittings.json      SittingDef[]      timetables and milestones (Taiwan time)
 *   registry/exam/papers.json        PaperDef[]        minutes, points, observed layout, scoring
 *   registry/exam/formula-sheets.json FormulaSheetDef[] what the 數A/數B papers print at the end
 *   registry/exam/items/<s>.json     ExamItemRef[]     official CEEC items, link only, never text
 *
 * Loading uses import.meta.glob (eager) so the same module works in Astro pages and in Vitest.
 * A schema error, a duplicate id or a broken internal reference throws at import time, so bad
 * data fails the build instead of rendering. Build-time only: do not import from a client island.
 *
 * Fact versions: validFrom <= date < validTo (validTo exclusive, open-ended when absent). Where the
 * research does not give the day a rule began, validFrom is the earliest date the research supports
 * and the version's `basis` says "validFrom 是下限"; components must not print such a date as "since".
 */
import { z } from 'astro/zod';
import {
  ExamItemRef,
  FactDef,
  ISODate,
  L10n,
  LicenceDef,
  MisconceptionDef,
  SittingDef as SittingSchema,
  SourceDef,
  SUBJECT_IDS,
  type SubjectId,
} from './schema.ts';

// ---------- schemas schema.ts does not have (papers, formula sheets) ----------

export const PAPER_IDS = ['mathA', 'mathB', 'science', 'social', 'chinese-comp', 'chinese-writing'] as const;
export const PaperId = z.enum(PAPER_IDS);
export type PaperId = z.infer<typeof PaperId>;

const Slug = z.string().regex(/^[a-z0-9-]+$/);
const Points = z.number().positive();
const QuestionNo = z.number().int().positive();
/** a sitting is named by its ROC academic year, e.g. 115 */
const SittingYear = z.number().int().min(83).max(999);

const PaperSection = z
  .object({
    /** 'choice' = single and multi-select mixed in one numbered block (自然 第壹部分) */
    type: z.enum(['single', 'multi', 'fill', 'choice', 'mixed', 'nonchoice', 'group']),
    label: L10n,
    /** first/last question number, only when the numbering was the same in every observed paper */
    first: QuestionNo.optional(),
    last: QuestionNo.optional(),
    count: z.number().int().positive().optional(),
    pointsEach: Points.optional(),
    points: Points.optional(),
    note: L10n.optional(),
  })
  .strict();

const PaperPart = z
  .object({
    id: Slug,
    label: L10n,
    /** omitted when the part's points changed between the observed papers */
    points: Points.optional(),
    sections: z.array(PaperSection).min(1),
    note: L10n.optional(),
  })
  .strict();

export const PaperDef = z
  .object({
    id: PaperId,
    label: L10n,
    /** the sitting whose brochure gives `minutes` (the session length) */
    sitting: z.string().regex(/^\d{3}$/),
    minutes: z.number().int().positive(),
    /** 'rule' = fixed by the brochure; 'observed' = what the past papers did (the brochure defers to each paper) */
    totalPoints: z.object({ value: Points, basis: z.enum(['rule', 'observed']) }).strict(),
    layout: z
      .object({
        /** sittings whose papers the layout was read from */
        observed: z.array(SittingYear).min(1),
        /** says the layout is observed, not promised (the next paper is unpublished until exam day) */
        basis: L10n,
        parts: z.array(PaperPart).min(1),
        /** per-sitting variation; partPoints follows the order of `parts` */
        byYear: z.array(z.object({ sitting: SittingYear, partPoints: z.array(Points).optional(), note: L10n }).strict()).default([]),
      })
      .strict(),
    /** what the 考試說明 sets as the frame (shares, item counts) */
    framework: L10n.optional(),
    scoring: z.array(L10n).min(1),
    note: L10n.optional(),
    sources: z.array(z.string()).min(1),
    reviewBy: ISODate,
  })
  .strict();
export type PaperDef = z.infer<typeof PaperDef>;

export const FormulaSheetDef = z
  .object({
    paper: z.enum(['mathA', 'mathB']),
    title: L10n,
    /** sittings whose paper ends with the sheet */
    present: z.array(SittingYear).min(1),
    /** sittings whose sheet content was actually read for this entry */
    contentFrom: z.array(SittingYear).min(1),
    basis: L10n,
    /** names only: how CEEC typesets each formula is not recorded, so we link the paper instead */
    formulas: z.array(z.object({ id: Slug, label: L10n }).strict()).min(1),
    /** printed reference values, kept as strings so trailing zeros (0.6990) survive */
    values: z.array(z.object({ id: Slug, tex: z.string().min(1), approx: z.string().regex(/^\d+\.\d+$/), label: L10n.optional() }).strict()).min(1),
    note: L10n.optional(),
    sources: z.array(z.string()).min(1),
    reviewBy: ISODate,
  })
  .strict();
export type FormulaSheetDef = z.infer<typeof FormulaSheetDef>;

// ---------- types ----------
// SourceDef, LicenceDef, FactDef, MisconceptionDef and ExamItemRef are both schemas and types in
// schema.ts; SittingDef is only a schema there, so its type is defined here.

export type SittingDef = z.infer<typeof SittingSchema>;
export type FactVersion = FactDef['versions'][number];

export interface Registry {
  sources: Map<string, SourceDef>;
  licences: Map<string, LicenceDef>;
  facts: Map<string, FactDef>;
  misconceptions: Map<string, MisconceptionDef>;
  examItems: Map<string, ExamItemRef>;
  sittings: Map<string, SittingDef>;
  papers: Map<PaperId, PaperDef>;
  formulaSheets: Map<FormulaSheetDef['paper'], FormulaSheetDef>;
  /**
   * which file each misconception / exam item came from (per-subject checks). One map is safe: a
   * misconception id always contains '.', an exam item id never does.
   */
  fileOf: Map<string, string>;
}

/** Raw JSON keyed by file path, exactly what import.meta.glob(..., { import: 'default' }) returns. */
export interface RegistryFiles {
  sources: Record<string, unknown>;
  licences: Record<string, unknown>;
  facts: Record<string, unknown>;
  misconceptions: Record<string, unknown>;
  sittings: Record<string, unknown>;
  papers: Record<string, unknown>;
  formulaSheets: Record<string, unknown>;
  examItems: Record<string, unknown>;
}

// ---------- building ----------

function describeIssues(error: z.ZodError): string {
  return error.issues.map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ');
}

/** Parse every file as an array of `schema` and merge into one map; throws on schema errors and duplicate keys. */
function mergeFiles<S extends z.ZodType>(
  label: string,
  files: Record<string, unknown>,
  schema: S,
  keyOf: (entry: z.infer<S>) => string,
  fileOf?: Map<string, string>,
): Map<string, z.infer<S>> {
  const out = new Map<string, z.infer<S>>();
  const from = new Map<string, string>();
  // sorted so the "already defined in" message is stable across platforms
  for (const path of Object.keys(files).sort()) {
    const parsed = z.array(schema).safeParse(files[path]);
    if (!parsed.success) throw new Error(`${label} ${path} is invalid: ${describeIssues(parsed.error)}`);
    for (const entry of parsed.data) {
      const key = keyOf(entry);
      if (out.has(key)) throw new Error(`Duplicate ${label} id "${key}" in ${path} (already defined in ${from.get(key)}).`);
      out.set(key, entry);
      from.set(key, path);
      fileOf?.set(key, path);
    }
  }
  return out;
}

export function buildRegistry(files: RegistryFiles): Registry {
  const fileOf = new Map<string, string>();
  return {
    sources: mergeFiles('source', files.sources, SourceDef, (s) => s.id),
    licences: mergeFiles('licence', files.licences, LicenceDef, (l) => l.id),
    facts: mergeFiles('fact', files.facts, FactDef, (f) => f.id),
    misconceptions: mergeFiles('misconception', files.misconceptions, MisconceptionDef, (m) => m.id, fileOf),
    examItems: mergeFiles('exam item', files.examItems, ExamItemRef, (i) => i.id, fileOf),
    sittings: mergeFiles('sitting', files.sittings, SittingSchema, (s) => s.id),
    papers: mergeFiles('paper', files.papers, PaperDef, (p) => p.id) as Map<PaperId, PaperDef>,
    formulaSheets: mergeFiles('formula sheet', files.formulaSheets, FormulaSheetDef, (f) => f.paper) as Map<FormulaSheetDef['paper'], FormulaSheetDef>,
    fileOf,
  };
}

/** 'src/data/registry/misconceptions/math.json' → 'math' */
export function subjectOfFile(path: string): string {
  return path.replace(/\\/g, '/').replace(/^.*\//, '').replace(/\.json$/, '');
}

/** The papers a subject's items may belong to (exam/items/<subject>.json). */
const PAPERS_OF_SUBJECT: Record<SubjectId, readonly PaperId[]> = {
  math: ['mathA', 'mathB'],
  physics: ['science'],
  chemistry: ['science'],
  biology: ['science'],
  earth: ['science'],
  inquiry: ['science'],
  history: ['social'],
  geography: ['social'],
  civics: ['social'],
  social: ['social'],
  chinese: ['chinese-comp', 'chinese-writing'],
};

/**
 * The id an exam item must have: '<sitting>-<paper>-q<first>' or '-q<first>-<last>' for a run.
 * Keeping the id derivable means a typo in `numbers` or `sitting` cannot hide behind a valid-looking id.
 */
export function expectedExamItemId(item: Pick<ExamItemRef, 'sitting' | 'paper' | 'numbers'>): string {
  const first = Math.min(...item.numbers);
  const last = Math.max(...item.numbers);
  return `${item.sitting}-${item.paper}-q${first === last ? first : `${first}-${last}`}`;
}

function versionProblems(fact: FactDef): string[] {
  const out: string[] = [];
  const versions = [...fact.versions].sort((a, b) => a.validFrom.localeCompare(b.validFrom));
  versions.forEach((v, i) => {
    if (v.validTo !== undefined && v.validTo <= v.validFrom) out.push(`fact ${fact.id}: version from ${v.validFrom} ends on or before it starts (${v.validTo})`);
    const next = versions[i + 1];
    if (next && (v.validTo === undefined || v.validTo > next.validFrom)) {
      out.push(`fact ${fact.id}: version from ${v.validFrom} overlaps the one from ${next.validFrom} (validTo is exclusive and must be <= the next validFrom)`);
    }
  });
  if (fact.asOf > fact.reviewBy) out.push(`fact ${fact.id}: asOf ${fact.asOf} is after reviewBy ${fact.reviewBy}`);
  return out;
}

/**
 * Referential and semantic checks across the registries. Returns human-readable problems (empty = OK).
 * Pure, so tests can run it on fixtures; the module below throws if the real data has any.
 */
export function registryProblems(reg: Registry): string[] {
  const out: string[] = [];
  const needSource = (owner: string, ids: readonly string[]) => {
    for (const id of ids) if (!reg.sources.has(id)) out.push(`${owner} cites unknown source "${id}"`);
  };

  for (const s of reg.sources.values()) {
    if (!reg.licences.has(s.licence)) out.push(`source ${s.id} has unknown licence "${s.licence}"`);
  }
  for (const l of reg.licences.values()) {
    if (l.mayQuote === 'link-only' && (l.mayRehost || l.mayModify)) out.push(`licence ${l.id}: link-only cannot allow re-hosting or modifying`);
    if (l.mayQuote === 'verbatim-only' && l.mayModify) out.push(`licence ${l.id}: verbatim-only cannot allow modifying`);
  }
  for (const f of reg.facts.values()) {
    needSource(`fact ${f.id}`, f.sources);
    out.push(...versionProblems(f));
  }
  for (const m of reg.misconceptions.values()) {
    needSource(`misconception ${m.id}`, m.sources);
    const subject = subjectOfFile(reg.fileOf.get(m.id) ?? '');
    if (!m.id.startsWith(`${subject}.`)) out.push(`misconception ${m.id} is in ${subject}.json but its id does not start with "${subject}."`);
  }
  for (const s of reg.sittings.values()) {
    needSource(`sitting ${s.id}`, s.sources);
    let prevEnd = '';
    for (const session of s.sessions) {
      const start = Date.parse(session.start);
      const end = Date.parse(session.end);
      if (Number.isNaN(start) || Number.isNaN(end)) out.push(`sitting ${s.id}: ${session.paper} has an unparseable time`);
      else if (end <= start) out.push(`sitting ${s.id}: ${session.paper} ends before it starts`);
      if (prevEnd && Date.parse(session.start) < Date.parse(prevEnd)) out.push(`sitting ${s.id}: ${session.paper} starts before the previous session ends`);
      prevEnd = session.end;
    }
  }
  for (const p of reg.papers.values()) {
    needSource(`paper ${p.id}`, p.sources);
    if (!reg.sittings.has(p.sitting)) out.push(`paper ${p.id} refers to unknown sitting ${p.sitting}`);
  }
  for (const f of reg.formulaSheets.values()) needSource(`formula sheet ${f.paper}`, f.sources);
  for (const item of reg.examItems.values()) {
    const expected = expectedExamItemId(item);
    if (item.id !== expected) out.push(`exam item ${item.id}: id should be ${expected}`);
    if ([...item.numbers].sort((a, b) => a - b).some((n, i, a) => i > 0 && n === a[i - 1])) out.push(`exam item ${item.id}: repeated question number`);
    // 111 was the first sitting under the 108課綱 (plan: earlier papers are 'legacy')
    if ((item.sitting >= 111) !== (item.curriculum === '108')) out.push(`exam item ${item.id}: sitting ${item.sitting} should be curriculum ${item.sitting >= 111 ? '108' : 'legacy'}`);
    const subject = subjectOfFile(reg.fileOf.get(item.id) ?? '');
    const allowed = (PAPERS_OF_SUBJECT as Record<string, readonly PaperId[] | undefined>)[subject];
    if (!allowed) out.push(`exam item ${item.id} is in items/${subject}.json, which is not a subject id (${SUBJECT_IDS.join(', ')})`);
    else if (!allowed.includes(item.paper)) out.push(`exam item ${item.id}: paper ${item.paper} does not belong in items/${subject}.json`);
  }
  return out;
}

// ---------- the real data ----------

// Vite needs each glob pattern as a literal, hence one call per file family.
const REGISTRY = buildRegistry({
  sources: import.meta.glob<unknown>('./registry/sources.json', { eager: true, import: 'default' }),
  licences: import.meta.glob<unknown>('./registry/licences.json', { eager: true, import: 'default' }),
  facts: import.meta.glob<unknown>('./registry/facts.json', { eager: true, import: 'default' }),
  misconceptions: import.meta.glob<unknown>('./registry/misconceptions/*.json', { eager: true, import: 'default' }),
  sittings: import.meta.glob<unknown>('./registry/exam/sittings.json', { eager: true, import: 'default' }),
  papers: import.meta.glob<unknown>('./registry/exam/papers.json', { eager: true, import: 'default' }),
  formulaSheets: import.meta.glob<unknown>('./registry/exam/formula-sheets.json', { eager: true, import: 'default' }),
  examItems: import.meta.glob<unknown>('./registry/exam/items/*.json', { eager: true, import: 'default' }),
});

const PROBLEMS = registryProblems(REGISTRY);
if (PROBLEMS.length) throw new Error(`Registry integrity check failed:\n- ${PROBLEMS.join('\n- ')}`);

export const SOURCES: Map<string, SourceDef> = REGISTRY.sources;
export const LICENCES: Map<string, LicenceDef> = REGISTRY.licences;
export const FACTS: Map<string, FactDef> = REGISTRY.facts;
export const MISCONCEPTIONS: Map<string, MisconceptionDef> = REGISTRY.misconceptions;
export const EXAM_ITEMS: Map<string, ExamItemRef> = REGISTRY.examItems;
export const SITTINGS: Map<string, SittingDef> = REGISTRY.sittings;
export const PAPERS: Map<PaperId, PaperDef> = REGISTRY.papers;
export const FORMULA_SHEETS: Map<FormulaSheetDef['paper'], FormulaSheetDef> = REGISTRY.formulaSheets;
/** the parsed registries as one object (tests and docs generators) */
export const REGISTRY_DATA: Readonly<Registry> = REGISTRY;

export const getSource = (id: string): SourceDef | undefined => SOURCES.get(id);
export const getLicence = (id: string): LicenceDef | undefined => LICENCES.get(id);
export const getFact = (id: string): FactDef | undefined => FACTS.get(id);
export const getMisconception = (id: string): MisconceptionDef | undefined => MISCONCEPTIONS.get(id);
export const getExamItem = (id: string): ExamItemRef | undefined => EXAM_ITEMS.get(id);
export const getSitting = (id: string): SittingDef | undefined => SITTINGS.get(id);
export const getPaper = (id: string): PaperDef | undefined => PAPERS.get(id as PaperId);
export const getFormulaSheet = (paper: string): FormulaSheetDef | undefined => FORMULA_SHEETS.get(paper as FormulaSheetDef['paper']);

/** The licence a source is published under (always defined for a known source: checked at load). */
export function licenceOf(sourceId: string): LicenceDef | undefined {
  const source = SOURCES.get(sourceId);
  return source ? LICENCES.get(source.licence) : undefined;
}

/**
 * The version of a fact that holds on `isoDate` (YYYY-MM-DD, Taiwan calendar date):
 * validFrom <= date < validTo, where validTo is exclusive and open-ended when absent.
 * Returns undefined before the first version, which callers must treat as "unknown", not "none".
 */
export function factValueOn(fact: FactDef, isoDate: string): FactVersion | undefined {
  if (!ISODate.safeParse(isoDate).success) throw new Error(`factValueOn: "${isoDate}" is not a YYYY-MM-DD date`);
  // ISO dates compare correctly as strings, which avoids time-zone shifts from Date parsing
  return fact.versions.find((v) => v.validFrom <= isoDate && (v.validTo === undefined || isoDate < v.validTo));
}

/**
 * True when a version's validFrom is only the earliest date the research supports (its basis says
 * "validFrom 是下限"), so a page may show the value but must not print the date as "since …".
 * A string marker because schema.ts has no field for it (reported to the integrator).
 */
export function validFromIsLowerBound(version: FactVersion): boolean {
  return version.basis?.includes('validFrom 是下限') ?? false;
}

export interface ReviewDue {
  kind: 'fact' | 'sitting' | 'paper' | 'formula-sheet';
  id: string;
  reviewBy: string;
}

/**
 * Everything whose reviewBy date has passed on `today` (YYYY-MM-DD). The date is a parameter so tests
 * stay deterministic; the scheduled freshness job passes the real date (06-critique §1 item 21:
 * PR CI only warns, the scheduled job fails).
 */
export function overdueReviews(today: string, reg: Pick<Registry, 'facts' | 'sittings' | 'papers' | 'formulaSheets'> = REGISTRY): ReviewDue[] {
  if (!ISODate.safeParse(today).success) throw new Error(`overdueReviews: "${today}" is not a YYYY-MM-DD date`);
  const due: ReviewDue[] = [];
  for (const f of reg.facts.values()) if (today > f.reviewBy) due.push({ kind: 'fact', id: f.id, reviewBy: f.reviewBy });
  for (const s of reg.sittings.values()) if (today > s.reviewBy) due.push({ kind: 'sitting', id: s.id, reviewBy: s.reviewBy });
  for (const p of reg.papers.values()) if (today > p.reviewBy) due.push({ kind: 'paper', id: p.id, reviewBy: p.reviewBy });
  for (const f of reg.formulaSheets.values()) if (today > f.reviewBy) due.push({ kind: 'formula-sheet', id: f.paper, reviewBy: f.reviewBy });
  return due;
}
