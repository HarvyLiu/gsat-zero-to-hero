# Course outlines (`src/data/course/`)

One JSON file per subject, named after it: `math.json`, `physics.json`, … and `site.json` for the
site-level chapters (welcome, how the site works, exam literacy). No real outline is committed yet;
they are written and owner-approved at S1 (116 sprint) and M1 (full course).

Every file is validated against `CourseFile` in [`../schema.ts`](../schema.ts) when the site builds
(`src/data/curriculum.ts`), and the rules below are enforced by `tests/curriculum/`. The generated
reading copies live in `docs/curriculum/` (`npm run docs:curriculum`); edit the JSON, never the docs.

## File shape (`CourseFile`)

```jsonc
{
  "$comment": "optional free text",
  "subject": "math",              // a SubjectId from subjects.json, or "site"; must equal the file name
  "version": 1,
  "date": "2026-11-20",           // YYYY-MM-DD of this version
  "decisions": ["…"],             // owner decisions this outline relies on (docs only)
  "openQuestions": ["…"],
  "parts": [
    {
      "num": 0,                   // 0, 1, 2, … in file order
      "id": "welcome",
      "title": { "zh-tw": "…", "en": "…" },
      "question": { "zh-tw": "…", "en": "…" },   // the question the part opens with
      "whyHere": "internal rationale, docs only",
      "track": "core",            // or a track object, see below
      "chapters": [ /* ChapterDef, in reading order */ ]
    }
  ]
}
```

A **track** part (only extensions and the 116 sprint are tracks; 數A/數B are *paths*):

```jsonc
"track": {
  "id": "sprint-116",             // a track id starting with "sprint" is a review set (see rules)
  "title": { "zh-tw": "116衝刺", "en": "GSAT 116 sprint" },
  "entry": { "after": ["site/welcome"], "note": { "zh-tw": "…", "en": "…" } }
}
```

A **chapter** (`ChapterDef`; its global id is `<subject>/<slug>`):

| Field | Meaning |
|---|---|
| `slug` | ASCII kebab-case, the same in both locales |
| `title`, `blurb` | `{ "zh-tw", "en" }`, neither empty |
| `objectives` | 1–5 `{ "zh-tw", "en" }` |
| `kind` | `welcome`, `exam-literacy`, `bridge`, `core`, `toolbox`, `review`, `exam-skills`, `exam-toolkit`, `checkpoint`, `capstone`, `extension` |
| `paths` | optional, e.g. `["mathA"]`; omitted = every path of the subject. Site chapters never declare paths. |
| `codes` | code refs `{ "key": "math:N-10-1", "part"?, "case"?, "role" }`, role one of `teaches` (default), `reviews`, `bridges`, `toolkit`, `beyond`, `uses` |
| `marks` | `★`, `＃`, `※` |
| `newConcepts`, `uses`, `reviews` | glossary ids (`math.real-number`) from `src/data/terms/` |
| `prereqs` | chapter ids, may cross subjects (`math/scientific-notation-arithmetic`) |
| `assumes` | code keys a track with a stated entry level assumes already studied (the sprint) |
| `minutes` | integer |
| `sources` | ≥ 1 source id from `src/data/registry/sources.json` |
| `examItems`, `misconceptions` | registry ids |
| `activity` | internal note, docs only |

## Rules (enforced by `tests/curriculum/`)

**No jumps** (`no-jump.test.ts`):
- chapter ids are unique across all subjects; every prereq exists; a prereq in the same subject comes earlier in the file; the whole prereq graph (all subjects) has no cycle;
- every chapter has ≥ 1 prereq, except `welcome` and `exam-literacy` chapters and the first chapter of a track;
- each concept is introduced (`newConcepts`) exactly once in the whole site;
- every `uses`/`reviews` id is introduced by the chapter itself or one of its ancestors, across subjects (glossary `vocab` terms are exempt); sprint-style review chapters (`kind: review`, or a chapter with `assumes`) may instead use any concept that is in the glossary or introduced somewhere;
- `newConcepts` ≤ `NEW_CONCEPT_CAP[kind]` (schema.ts);
- paths: a chapter's same-subject prereqs and ancestors are on every path the chapter is on (a 數B chapter never needs a 數A-only chapter);
- a prereq in another subject must be a site chapter, or a `bridge`/`core` chapter on every path of its subject;
- `extension` chapters are never prereqs of other kinds.

**Structure** (`structure.test.ts`): parts numbered 0..n; core parts before track parts; track entries point at real chapters; every core part after Part 0 of a subject ends with a `checkpoint` or `capstone` chapter; `minutes` ≤ `MINUTES_CAP[kind]`; ※ material only in `extension` chapters.

**Coverage** (`coverage.test.ts`): every `inGsat: "yes"` code of a subject that has a course file is taught or reviewed on the right path(s); every code key exists; each official `dependsOn` edge X → Y is respected (a chapter teaching X has a chapter teaching Y as itself or an ancestor) unless waived.

**Sources** (`sources.test.ts`): every cited source exists, is https and has a known licence.

## Waivers (`waivers.json`)

A dependency edge the outline deliberately does not follow (for example the math D2a/b/c order
changes) is listed here and must be signed off by the owner:

```json
[{ "from": "math:A-11A-3", "to": "math:A-11A-2", "reason": "why the order differs", "approvedBy": "owner, YYYY-MM-DD" }]
```

`from` depends on `to` in the official data. Waivers that no longer match a real gap are reported
so the file stays honest. The file starts empty.
