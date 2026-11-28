/**
 * Lessons: one MDX file per chapter and locale, mirrored by path:
 *   src/content/lessons/<locale>/<subject>/<slug>.mdx   (subject may be 'site' for site-level chapters)
 * The entry id keeps that path without the extension ('zh-tw/math/real-numbers'), so the route,
 * the chapter id ('math/real-numbers') and the locale are all read from one place.
 * Course structure (part, prereqs, codes, sources) lives in src/data/course/*.json, not here,
 * so it is defined once for both locales.
 */
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

/** '<locale>/<subject|site>/<slug>'; a leading underscore marks internal pages such as the style check */
const LESSON_ID = /^(zh-tw|en)\/(site|math|physics|chemistry|biology|earth|inquiry|history|geography|civics|social|chinese)\/_?[a-z0-9-]+$/;

/**
 * YAML reads an unquoted 2026-11-15 as a Date, so accept both and normalise to 'YYYY-MM-DD'.
 * toISOString is safe here: YAML dates without a time are midnight UTC.
 */
const IsoDay = z.union([
  z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'use YYYY-MM-DD'),
  z.date().transform((d) => d.toISOString().slice(0, 10)),
]);

const lessons = defineCollection({
  loader: glob({
    pattern: '**/*.mdx',
    base: './src/content/lessons',
    generateId: ({ entry }) => {
      const id = entry.replace(/\\/g, '/').replace(/\.mdx$/, '');
      if (!LESSON_ID.test(id)) {
        throw new Error(`Lesson file "${entry}" must live at <zh-tw|en>/<subject>/<slug>.mdx with an ASCII kebab-case slug.`);
      }
      return id;
    },
  }),
  schema: z
    .object({
      title: z.string().min(1),
      description: z.string().min(1),
      goals: z.array(z.string().min(1)).min(1).max(5),
      aha: z.string().min(1),
      minutes: z.number().int().positive(),
      /** draft pages are built only in dev or with DRAFTS=1, and are never indexed for search */
      status: z.enum(['draft', 'reviewed', 'published']),
      /** the day the chapter's facts were last checked against its sources */
      lastVerified: IsoDay.optional(),
      /** bibliography ids (src/data/registry/sources.json) the chapter was checked against */
      verifiedAgainst: z.array(z.string().min(1)).optional(),
    })
    .strict(),
});

export const collections = { lessons };
