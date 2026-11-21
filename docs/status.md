# Status and handoff (read this first after a context reset)

Updated 2026-11-21. Read these first:
- the plan, `docs/plan.md`;
- the binding writing rules, `docs/authoring.md`, including the owner requirements added 2026-11-16;
- the cost rules, `CLAUDE.md`.

## Current state

**Live and pushed**
- Repo: https://github.com/HarvyLiu/gsat-zero-to-hero (public). The owner approved making it public after a credential scan found nothing; the Vercel token stays in the git-ignored `.env.local`.
- Site: https://gsat-zero-to-hero.vercel.app, on Vercel project `viocity/gsat-zero-to-hero`. It is connected to GitHub, so every push to `main` redeploys. `SITE_URL` is set as a Vercel production environment variable, and `vercel.json` holds the build settings.

**Done (all committed)**
- **S0 framework:**
  - Astro 7 bilingual site with the "answer sheet + red pen" theme on ASMC's thin-grid layout.
  - Components: dialogue, Term (its pop-up definitions are rendered with KaTeX), Quiz with 學測 scoring (選填 rows ①②③ read left to right), Perspective, Graph, NumberLine, Space3D.
  - Registries, the SymPy harness and the test suites.
- **Math:** 53 chapters, all `reviewed`:
  - 116 sprint (40);
  - cross-unit 跨單元解題 (5);
  - optional 選修小技巧 track (8).
- **Physics:** 15 sprint chapters, all `reviewed`, subject status `active` (commits b86b2cd, 67ab0a2). The physics workflow script is `physics-sprint-write-*.js` in the session workflows folder; adapt it for the next subject, following the CLAUDE.md cost rules.
- **Course entry points** (0bdb0ab):
  - the home page has a subject grid;
  - `/<locale>/subjects/` (the header link 科目);
  - `/<locale>/<subject>/` course pages with the full outline, a start/continue button and the 數A/數B chooser;
  - part numbers are shown from 1 (`partNo()` in `src/data/curriculum.ts`);
  - the phone nav text stays sr-only, so icon links keep their names.
- **Tests and checks:** 582 tests passed and 1 skipped; the harness `--strict` passes; the type check shows 0 errors; all 14,828 internal hrefs resolve.

**Uncommitted:** nothing, apart from this handoff commit.

**Pending (known, not fixed)**
1. **Outline vs frontmatter minutes.** In 35 of the 53 math chapters, the minutes in `src/data/course/math.json` differ from the lesson frontmatter. Example: s116-real-numbers is 25 in the outline and 30 in the frontmatter. The pages now show the frontmatter value everywhere. Decide whether to sync the outline to it.
2. **Physics review leftovers (sev3):**
   - In s116-physics-intro, the zh name forms 邁特納, 史特拉斯曼, 弗里施, 諾特 and 哈恩 are not yet checked against Taiwan textbooks.
   - Its scope section has a figure but no Perspective.
   - Phone-width label overlap in the physics figures hasn't been looked at.
   - The full reviewer reports are in the workflow journal `wf_33001870-054/journal.jsonl` (session subagents folder).
3. **Math polish:** the plane labels crowd in the three-planes figure (s116a-matrices).
4. Science and social chapters have no `<OnTheExam>` or `<Misconception>` entries yet: the registries hold only math. Physics mentions past items in plain text only.

## Next
- **自然:** one subject per session, in this order: chemistry (15) → biology (8) → earth (13) → inquiry (9, last; its cross-subject and mock chapters need the others).
  - Pipeline: writer → reviewer per chapter, following CLAUDE.md.
  - Give writers a research slice, not the whole file.
  - SymPy checks go in `harness/checks/m_<subject>_<slug>.py`.
  - Assign glossary ids to chapters before parallel writing, so no id is defined twice.
  - For earth/s116-universe-stars: recap the EM spectrum in place and link to physics/s116-em-waves as the source.
- **After each subject:**
  - set each chapter's `reviews` to its `<Term>` ids;
  - run the control-character scan, harness `--strict`, vitest and the build;
  - run a text render scan over the built pages;
  - set the subject to `active` in `src/data/subjects.json` (a test checks that every chapter exists in both locales and is reviewed);
  - commit, then push only if the owner asks.
- **Then:** the 社會 (歷史, 地理, 公民) sprint outline → owner approval → chapters, following the contested-topic rules in docs/design/03-social-chinese-map.md §1.5. After that, 國文 beta.

## Decisions (and why)

These are owner decisions that are not already recorded in plan.md or authoring.md.

**Process**
- **One subject at a time** (2026-11-16), so rate limits don't cut a batch off.
- **Token economy** (2026-11-16, tightened 2026-11-21): agents run at medium effort and suitable models, never Fable. See CLAUDE.md.

**Site name, theme and design**
- **Site name:** zh 「從 0 開始的學測牲活」 (owner's choice, 2026-11-16, because it is more entertaining). The en name "GSAT from Zero" is a placeholder.
- **Theme:** "answer sheet + red pen", with an open-book logo and heading marker, so the site doesn't look too much like ASMC. The layout keeps ASMC's thin even grid only, with no major grid lines (from the owner's rejection of the first plan).
- **選填:** cells read left to right (rows ①②③), not top to bottom.

**Teaching rules**
- **Multiple perspectives** for every method, worked out in full.
- **Future knowledge** goes in collapsible `<Perspective later>` blocks.
- **Always visualize**, using graphing as a solving tool.
- **A cross-unit "many ways" lesson** comes after the units.
- **分科 material** only as optional "advanced tools that help 學測", taught from zero. The owner chose the label 選修小技巧 because it makes more sense than an AST/分科 label.
- **Math extensions proposal** approved as written, including x-linear-programming, kept and labelled.

**自然 outline** (approved 2026-11-16)
- Keep all 60 chapters.
- Biology uses the shared inquiry exam-skills part.
- A single shared 自然 mock paper.
- 環境汙染 stays one chapter.
- The earth chapter on stars links to physics/s116-em-waves.

**Publishing**
- Repo public and hosted on Vercel (2026-11-21), via the gh and vercel CLIs.
- Pushes only on the owner's request.

**Earlier decisions** (in plan.md): bilingual audience, open and close dialogues, a new character pair, Math as the pilot, depth plus tracks, auto-detected language, 116 first, light owner review, CC BY-NC-SA for lessons plus MIT for code, and no 英文 paper.

## Unresolved (owner to decide)
- The English site name (placeholder "GSAT from Zero").
- Character names (placeholders 老師/學生); the owner wanted a new pair.
- A custom domain. The site currently uses the vercel.app address, and `astro.config` still falls back to a pages.dev URL when `SITE_URL` is unset.
- Optional: email CEEC about embedding past items. Until then the site links only.
- Whether to sync the math outline minutes to the lesson frontmatter (Pending 1).
- The GitHub commit email is public. The owner can enable GitHub's private-email setting for future commits.
