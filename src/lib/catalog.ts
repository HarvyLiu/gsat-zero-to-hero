/**
 * The course catalogue the home, subjects and subject pages show: which subjects exist, how they group
 * by 學測 paper, and how much of each outline is online in a locale. "Online" means the chapter page is
 * built in that locale, using the same rule as src/pages/<locale>/[subject]/[slug].astro (drafts only in
 * dev or with DRAFTS=1), so a card never links to a page that does not exist.
 */
import { getCollection } from 'astro:content';
import { SUBJECTS, chaptersOf, type Chapter } from '../data/curriculum';
import type { SubjectDef } from '../data/schema';
import type { Locale } from '../i18n/ui';

export type GroupId = 'math' | 'science' | 'social' | 'chinese';
export const GROUPS: GroupId[] = ['math', 'science', 'social', 'chinese'];

/** the paper a subject is examined in decides its group */
export function groupOf(s: Pick<SubjectDef, 'papers'>): GroupId {
  const p = s.papers[0] ?? '';
  if (p.startsWith('math')) return 'math';
  if (p === 'science') return 'science';
  if (p === 'social') return 'social';
  return 'chinese';
}

/**
 * Chapters with a built page in this locale ('math/s116-lines' → its minutes). The minutes come from the
 * lesson's frontmatter, the number the chapter page itself shows, not from the outline's estimate.
 */
export async function builtChapters(locale: Locale): Promise<Map<string, number>> {
  const showDrafts = import.meta.env.DEV || process.env.DRAFTS === '1';
  const lessons = await getCollection('lessons', (e) => (showDrafts || e.data.status !== 'draft') && e.id.startsWith(`${locale}/`));
  return new Map(lessons.map((e) => [e.id.slice(locale.length + 1), e.data.minutes]));
}

export interface SubjectSummary {
  subject: SubjectDef;
  group: GroupId;
  /** every chapter in the outline, in reading order (core first, then tracks) */
  chapters: Chapter[];
  ready: Chapter[];
  /** minutes of the chapters that are online (or of the whole outline while none are) */
  minutes: number;
  /** the first chapter online, in reading order */
  first?: Chapter;
}

const trackRank = (c: Chapter) => (c.track === 'core' ? 0 : 1);
/** reading order: the core path first, then tracks, each in course order */
export const readingOrder = (cs: Chapter[]) => [...cs].sort((a, b) => trackRank(a) - trackRank(b) || a.index - b.index);

export function summarise(built: ReadonlyMap<string, number>): SubjectSummary[] {
  return SUBJECTS.map((subject) => {
    const chapters = readingOrder(chaptersOf(subject.id));
    const ready = chapters.filter((c) => built.has(c.id));
    const counted = ready.length ? ready : chapters;
    return {
      subject,
      group: groupOf(subject),
      chapters,
      ready,
      minutes: counted.reduce((n, c) => n + (built.get(c.id) ?? c.minutes), 0),
      first: ready[0],
    };
  });
}

/** hours to the nearest half hour, at least 0.5 */
export const hours = (minutes: number) => Math.max(0.5, Math.round(minutes / 30) / 2);
