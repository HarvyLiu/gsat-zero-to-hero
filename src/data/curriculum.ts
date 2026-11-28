/**
 * Typed views over the course outlines (ported from the ASMC reference's curriculum.ts, made
 * multi-subject, path-aware and cross-subject).
 *
 * Sources of truth:
 *   src/data/subjects.json          SubjectDef[]: the 11 subjects, their papers and learner paths
 *   src/data/course/<subject>.json  one CourseFile per subject ('site.json' for site-level chapters)
 * Both are validated with the Zod schemas in schema.ts, so a malformed outline fails the build.
 * The semantic rules (no jumps, path rules, coverage) live in tests/curriculum/, which run the same
 * buildCurriculum() on the real data and on fixtures.
 *
 * Course files are written later (S1/M1), so everything here must work with zero course files.
 *
 * Build-time only: never import this from a client:* island, or every outline ships to the browser.
 */
import { z } from 'astro/zod';
import { CourseFile, SUBJECT_IDS, SubjectDef, type ChapterDef, type ChapterId, type L10n, type Locale, type SubjectId } from './schema.ts';
import subjectsJson from './subjects.json';

export type CourseSubject = SubjectId | 'site';
type TrackShape = { id: string; title: L10n; entry: { after: ChapterId[]; note: L10n } };

export interface Chapter extends ChapterDef {
  /** global id: '<subject>/<slug>' */
  id: ChapterId;
  subject: CourseSubject;
  partNum: number;
  partId: string;
  partTitle: L10n;
  /** 'core', or the id of the track the chapter's part belongs to */
  track: string;
  /** the track definition, for chapters in a track part */
  trackDef?: TrackShape;
  /** position within its course file, from 0 (course order is reading order) */
  index: number;
  /**
   * The learner paths this chapter is on: `paths` when declared, else every path of its subject.
   * Site chapters are on every path of every subject; they get [] here and isOnPath() says true.
   */
  onPaths: string[];
}

export interface Curriculum {
  subjects: SubjectDef[];
  courses: CourseFile[];
  chapters: Chapter[];
  subjectById(id: string): SubjectDef | undefined;
  /** path ids of a subject ('site' and unknown subjects have none) */
  pathsOf(subject: string): string[];
  chapterById(id: string): Chapter | undefined;
  /** every chapter reachable backwards through prereqs, across subjects (unknown ids are skipped) */
  ancestorsOf(id: string): Set<string>;
  /** prev/next within the same course and track; with `path`, only chapters on that path */
  neighbours(id: string, path?: string): { prev?: Chapter; next?: Chapter };
  /** true when both locales of the lesson exist (src/content/lessons/{zh-tw,en}/<subject>/<slug>.mdx) */
  isReady(id: string): boolean;
  /** the chapter that introduces a concept (first one, if an outline wrongly introduces it twice) */
  conceptOwner(termId: string): Chapter | undefined;
}

const LOCALES: Locale[] = ['zh-tw', 'en'];
const COURSE_ORDER: CourseSubject[] = ['site', ...SUBJECT_IDS];

export function isOnPath(chapter: Pick<Chapter, 'subject' | 'onPaths'>, path: string): boolean {
  return chapter.subject === 'site' || chapter.onPaths.includes(path);
}

/** '/src/content/lessons/zh-tw/math/real-numbers.mdx' (or a bare 'zh-tw/math/real-numbers') → 'zh-tw/math/real-numbers' */
export function lessonIdFromPath(path: string): string {
  return path
    .replace(/\\/g, '/')
    .replace(/^.*?\/?lessons\//, '')
    .replace(/\.mdx$/, '');
}

function describeIssues(error: z.ZodError): string {
  return error.issues.map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ');
}

/**
 * Pure builder used by this module (real data) and by the tests (fixtures).
 * Throws only on data that cannot be read at all: schema violations and two files for one subject.
 */
export function buildCurriculum(courseInputs: readonly unknown[], subjectInput: readonly unknown[], lessonFiles: readonly string[] = []): Curriculum {
  const parsedSubjects = z.array(SubjectDef).safeParse(subjectInput);
  if (!parsedSubjects.success) throw new Error(`subjects.json is invalid: ${describeIssues(parsedSubjects.error)}`);
  const subjects = parsedSubjects.data;
  const subjectMap = new Map(subjects.map((s) => [s.id as string, s]));
  const pathsOf = (subject: string) => subjectMap.get(subject)?.paths.map((p) => p.id) ?? [];

  const courses = courseInputs.map((raw, i) => {
    const r = CourseFile.safeParse(raw);
    const label = (raw as { subject?: unknown } | null)?.subject ?? `#${i}`;
    if (!r.success) throw new Error(`course file "${String(label)}" is invalid: ${describeIssues(r.error)}`);
    return r.data;
  });
  const seenSubjects = new Set<string>();
  for (const c of courses) {
    if (seenSubjects.has(c.subject)) throw new Error(`two course files for subject "${c.subject}"`);
    seenSubjects.add(c.subject);
  }
  courses.sort((a, b) => COURSE_ORDER.indexOf(a.subject) - COURSE_ORDER.indexOf(b.subject));

  const chapters: Chapter[] = [];
  for (const course of courses) {
    let index = 0;
    for (const part of course.parts) {
      const trackDef = part.track === 'core' ? undefined : part.track;
      for (const def of part.chapters) {
        chapters.push({
          ...def,
          id: `${course.subject}/${def.slug}`,
          subject: course.subject,
          partNum: part.num,
          partId: part.id,
          partTitle: part.title,
          track: trackDef ? trackDef.id : 'core',
          ...(trackDef ? { trackDef } : {}),
          index: index++,
          onPaths: course.subject === 'site' ? [] : (def.paths ?? pathsOf(course.subject)),
        });
      }
    }
  }

  // Duplicate ids are a rule violation reported by tests/curriculum; lookups keep the first.
  const byId = new Map<string, Chapter>();
  for (const c of chapters) if (!byId.has(c.id)) byId.set(c.id, c);

  const owners = new Map<string, Chapter>();
  for (const c of chapters) for (const t of c.newConcepts) if (!owners.has(t)) owners.set(t, c);

  const ancestorCache = new Map<string, Set<string>>();
  const ancestorsOf = (id: string): Set<string> => {
    const known = ancestorCache.get(id);
    if (known) return known;
    // Iterative walk with a visited set: terminates even on a cyclic outline (the tests report cycles).
    const out = new Set<string>();
    const stack = [...(byId.get(id)?.prereqs ?? [])];
    while (stack.length) {
      const p = stack.pop()!;
      if (out.has(p) || !byId.has(p)) continue;
      out.add(p);
      stack.push(...byId.get(p)!.prereqs);
    }
    ancestorCache.set(id, out);
    return out;
  };

  const groupCache = new Map<string, Chapter[]>();
  const neighbours = (id: string, path?: string) => {
    const here = byId.get(id);
    if (!here || (path !== undefined && !isOnPath(here, path))) return {};
    const key = `${here.subject}|${here.track}|${path ?? ''}`;
    let group = groupCache.get(key);
    if (!group) {
      group = chapters.filter((c) => c.subject === here.subject && c.track === here.track && (path === undefined || isOnPath(c, path)));
      groupCache.set(key, group);
    }
    const i = group.indexOf(here);
    return { prev: group[i - 1], next: group[i + 1] };
  };

  const lessons = new Set(lessonFiles.map(lessonIdFromPath));
  const isReady = (id: string) => byId.has(id) && LOCALES.every((l) => lessons.has(`${l}/${id}`));

  return {
    subjects,
    courses,
    chapters,
    subjectById: (id) => subjectMap.get(id),
    pathsOf,
    chapterById: (id) => byId.get(id),
    ancestorsOf,
    neighbours,
    isReady,
    conceptOwner: (t) => owners.get(t),
  };
}

// ---------- the real data ----------

/** Course files; waivers.json lives in the same folder but is not a course. */
const COURSE_MODULES = import.meta.glob<{ default: unknown }>(['/src/data/course/*.json', '!/src/data/course/waivers.json'], { eager: true });
const COURSE_INPUTS = Object.entries(COURSE_MODULES).map(([file, mod]) => {
  const data = mod.default;
  const name = file.replace(/^.*\//, '').replace(/\.json$/, '');
  const subject = (data as { subject?: unknown } | null)?.subject;
  // One file per subject, named after it, so a reader can find an outline from its URL.
  if (subject !== name) throw new Error(`${file}: a course file must be named after its subject ("${String(subject)}.json")`);
  return data;
});
/** Lesson files, by name only (the glob is lazy: no lesson is imported here). */
const LESSON_FILES = Object.keys(import.meta.glob('/src/content/lessons/*/*/*.mdx'));

/** The whole site's curriculum; the named exports below are its parts. */
export const CURRICULUM: Curriculum = buildCurriculum(COURSE_INPUTS, subjectsJson, LESSON_FILES);

export const SUBJECTS: SubjectDef[] = CURRICULUM.subjects;
export const COURSES: CourseFile[] = CURRICULUM.courses;
export const CHAPTERS: Chapter[] = CURRICULUM.chapters;
export const subjectById = CURRICULUM.subjectById;
export const pathsOf = CURRICULUM.pathsOf;
export const chapterById = CURRICULUM.chapterById;
export const ancestorsOf = CURRICULUM.ancestorsOf;
export const neighbours = CURRICULUM.neighbours;
export const isReady = CURRICULUM.isReady;
export const conceptOwner = CURRICULUM.conceptOwner;

/** The chapters of one subject (or 'site'), in course order. */
/** Part numbers in course files start at 0; learners see them from 1 (第 1 部分, chapter 1.1). */
export const partNo = (num: number): number => num + 1;

export function chaptersOf(subject: CourseSubject): Chapter[] {
  return CHAPTERS.filter((c) => c.subject === subject);
}

/** The chapter id a lesson URL belongs to: '/zh-tw/math/real-numbers/' → 'math/real-numbers'. */
export function chapterIdFromUrl(pathname: string): string | undefined {
  const m = /\/(?:zh-tw|en)\/([a-z]+)\/([a-z0-9-]+)\/?$/.exec(pathname);
  return m ? `${m[1]}/${m[2]}` : undefined;
}
