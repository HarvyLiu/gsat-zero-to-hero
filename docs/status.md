# Status and handoff (read this first after a context reset)

Updated 2026-11-23. Read these first:
- the plan, `docs/plan.md`;
- the binding writing rules, `docs/authoring.md`, including the owner requirements added 2026-11-16;
- the cost rules and English spelling convention, `CLAUDE.md`;
- the pacing targets and model chapters, `docs/teaching-style.md`.

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
- **Chemistry:** 15 sprint chapters, all `reviewed`, subject status `active` (2026-11-22). They were written in 3 workflow batches of 5. Each batch had Opus writers, a facts reviewer and a teaching reviewer, and one fixer, followed by a Sonnet visual review and one cross-batch visual fixer. The batch script is `chemistry-sprint-batch-*.js` in the session workflows folder; reuse it for biology with a new chapter list, glossary map and slice paths. Per-chapter research slices were built in the session scratchpad from `result[3]` of the frozen research; rebuild them for the next subject the same way. The reviewer reports are in the workflow journals `wf_2e689952-f7d`, `wf_cb22dfd4-739` and `wf_88fff16e-5d1`.
- **Biology:** 8 sprint chapters, all `reviewed`, subject status `active` (2026-11-23).
  - Written in 2 workflow batches of 4 (Opus writers, a facts reviewer and a teaching reviewer, 1 fixer; 7 agents per batch, about 1.8M subagent tokens each), then 1 Sonnet visual reviewer and 1 Opus visual fixer (about 0.5M).
  - The batch script is `biology-sprint-batch-*.js` in this session's workflows folder (session 6bf4de06); it takes `args.batch`, `args.date` and `args.lessons`. Reuse it for earth with a new ORDER, TERMS map, model chapter and slice paths.
  - Research slices were built by `bio_slices.py` in that session's scratchpad from `result[4]` of the frozen research. Earth is in `result[5]` ("earth-inquiry").
  - Reviewer reports are in the workflow journals `wf_64c736ef-ff6`, `wf_2030d4c1-270` and `wf_5d89c654-58a` (visual).
  - The harness `--strict` now requires a check for every biology item too.
- **Graph tick labels (2026-11-23):** labels for ticks outside a figure's declared `x`/`y` range are now hidden. Mafs pads the view, and the bottom pad added more, so these labels used to show half-clipped (for example −10 on a count axis, or 26 above y = 25).
- **Checking figures in the hidden browser pane:** Graph islands are `client:visible` and Mafs measures its width on a rendered frame, so neither happens in a hidden pane. What works: load the pages in 375 px iframes, call each island's `hydrate()` after setting `Component` and `hydrator` from its `component-url` and `renderer-url`, take one tiny screenshot to force a frame, then scan the SVG `<text>` boxes for clipping and overlap.
- **Site fixes from the chemistry visual reviews (2026-11-22), which also improve math and physics:**
  - `Graph` gained `axes={false}` for schematic figures;
  - ticks are spaced automatically (≥18 px apart, `src/lib/ticks.ts`, tested), so wide axes no longer smear;
  - the view is padded below y = 0, so x-axis numbers aren't cut off;
  - mhchem `\ce{}` works in lesson prose;
  - display math, quiz options, stems and StudentAsks answers no longer widen the page on phones.

  Note: a one-line `$$…$$` renders INLINE. Display math needs `$$` on lines of their own.
- **Course entry points** (0bdb0ab):
  - the home page has a subject grid;
  - `/<locale>/subjects/` (the header link 科目);
  - `/<locale>/<subject>/` course pages with the full outline, a start/continue button and the 數A/數B chooser;
  - part numbers are shown from 1 (`partNo()` in `src/data/curriculum.ts`);
  - the phone nav text stays sr-only, so icon links keep their names.
- **Tests and checks** (2026-11-23): 587 tests passed and 1 skipped; the harness `--strict` passes on 818 items (80 of them biology); the type check shows 0 errors; the build and the biology render scan are clean. The site-wide href check passed before the biology push: 20,923 internal hrefs and srcs, 0 broken (scratchpad hrefs.py, session 6bf4de06).

**Uncommitted:** nothing. Chemistry and biology are pushed (biology in 1329e13, 2026-11-23); this status line is a later local commit.

**Pending (known, not fixed)**
1. **Outline vs frontmatter minutes.** In 35 of the 53 math chapters, the minutes in `src/data/course/math.json` differ from the lesson frontmatter. Example: s116-real-numbers is 25 in the outline and 30 in the frontmatter. The pages now show the frontmatter value everywhere. Decide whether to sync the outline to it.
2. **Physics review leftovers (sev3):**
   - In s116-physics-intro, the zh name forms 邁特納, 史特拉斯曼, 弗里施, 諾特 and 哈恩 are not yet checked against Taiwan textbooks.
   - Its scope section has a figure but no Perspective.
   - Phone-width label overlap in the physics figures hasn't been looked at.
   - The full reviewer reports are in the workflow journal `wf_33001870-054/journal.jsonl` (session subagents folder).
3. **Math polish:** the plane labels crowd in the three-planes figure (s116a-matrices).
4. **Physics and math figures found during the chemistry visual reviews:**
   - physics/s116-heat-energy-quality: the 冰的熔點 label overlaps the "(t, T)" label and the dashed line, and 水的沸點 is clipped at the right;
   - math/s116xb-models-and-tables: a "30" label is drawn twice.
   The new tick spacing may have moved the labels of other wide-axis math and physics figures. Give these figures a phone-width check during the next visual pass.
5. **Chemistry open questions for the owner:**
   - **Standard facts the writers used that are not in the frozen research.** The facts reviewer recomputed or confirmed them. Examples:
     - water's and CO₂'s triple points and CO₂'s sublimation point;
     - reaction heats (H₂ −286/−572, CH₄ −890, C₃H₈ −2220 kJ);
     - Iijima and carbon nanotubes (1991);
     - TiO₂ photocatalysis;
     - nanomaterial size, 1–100 nm;
     - lithium with water;
     - Lavoisier, Proust and Dalton history details;
     - silicon as a semiconductor.

     They are listed in the writer reports in the journals. Decide whether to accept them as standard textbook facts.
   - **Wording calls:**
     - 鋞離子 is marked 舊名 by NAER, but the slice gives no current form;
     - "this chapter works at 25℃" is used as a course convention;
     - written-items says "112年的跨科題目則以和生物的居多" (from the slice's statistic);
     - 皮耶（Pierre Curie）.
   - **Borderline spoilers left as they are:**
     - acids-bases q-turn: the goal states [H⁺][OH⁻]=10⁻¹⁴;
     - reaction-energy q-turn: the aha hints at the answer;
     - chemical-bonds q-mid: a section heading sits just above it.
6. Science and social chapters have no `<OnTheExam>` or `<Misconception>` entries yet: the registries hold only math. Physics mentions past items in plain text only.
7. **Biology open questions for the owner** (details in the batch journals):
   - **Names not in the frozen research:**
     - zh person names: 雷文霍克, 布朗, 許來登, 許旺, 魏修, 薩登, 史蒂文斯, 威爾遜, 摩根 and 麥克林托克;
     - the history dates in cell-theory and chromosomes;
     - Darwin's book title: both chapters use 《物種原始》; is 《物種起源》 preferred?
     - Whittaker and Woese are unnamed ("an American ecologist / microbiologist"): restore their names with Taiwan forms?
   - **Content to confirm:**
     - X-linked dominant inheritance is taught briefly in chromosomes-sex-linked, so a reason can fully rule out sex-linkage (112 Q50): confirm this scope.
     - the McClintock box in molecular-genetics: keep it or drop it?
     - standard facts the writers used without a source: the purposes of the kiwi DNA-extraction steps, insulin from bacteria, the archaea/eukaryote relationship, and the micrometer items in cell-theory (they scale against the eyepiece scale with no μm conversion, close to 「不涉及刻度換算」).
   - **Glossary:**
     - the English forms of nearly all biology glossary terms are "not yet checked on 樂詞網";
     - the source registry needs an entry for the 課程手冊 (biology.use-and-disuse cites p.19 under naer-curriculum);
     - nat.json titles `nat:Bc-IV-1` as inquiry basics, while the research puts 酵素 under Bc-Ⅳ-1, so the registry may be wrong (biology.enzyme cites it).
   - **Display:** the ABO labels use the Unicode glyphs Iᴬ and Iᴮ; check them on iOS and Android fonts.
   - **Figures:** about 10 biology figures now draw their own axes (`axes={false}`), so they have no grid lines.
8. **Older figures seen in the 375 px label scan (2026-11-23), not fixed:**
   - math/s116-linear-quadratic: origin tick labels crowd the point labels;
   - physics/s116-heat-energy-quality: several labels clipped or overlapping (already item 4);
   - chemistry/s116-solutions: figure 5's y labels are clipped.
   Run the iframe label scan over all subjects during the next visual pass.

## Next
- **自然:** one subject per session, in this order: ~~chemistry (15)~~ done → ~~biology (8)~~ done → earth (13) → inquiry (9, last; its cross-subject and mock chapters need the others).
  - For earth: add "earth" to `CHECKED_SUBJECTS` in `harness/verify_items.py`; give the writers the biology lessons too. Biology's notable ones:
    - CJK bold: a `**` that closes right after 。 and is followed by a Han character does not render;
    - predictions were given away by aha boxes and goals (they render above the opening dialogue), by headings and by StudentAsks;
    - quiz items reused worked examples;
    - claims about the GSAT need a source;
    - one long inline formula widened a phone page: put long formulas in display math;
    - Graph labels anchor at their start point ("ne"), not their centre.
  - Pipeline (as for chemistry): batches of up to 5 Opus writers → a facts reviewer and a teaching reviewer → 1 fixer → build and render scan → a Sonnet visual reviewer. That reviewer must scroll to hydrate the Graph islands (they render only when visible).
  - Give the writers the "lessons" list from the chemistry batches: options decided by code; predictions not given away by the text, goals, aha or glossary pop-ups; `axes={false}` on schematic figures; long equations as fenced display math; British spelling; no grade claims.
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

- **Teaching style** (2026-11-22): `docs/teaching-style.md` now exists, adapted from ASMC's. New 自然 and 社會 sprint chapters, starting with chemistry, use tighter pacing: ≥2 predictions, 3–4 StudentAsks, a task on every figure, ≤130 words per moment. Physics and math are not retrofitted (owner's choice).
- **Chemistry batches** (2026-11-22): run as a workflow, 3 batches of 5. Each batch is 5 Opus writers (medium), 2 Opus reviewers (high: facts and answers, teaching and wording) and 1 Opus fixer (high), so 8 agents per batch. Writers get a per-chapter research slice in the session scratchpad, rebuilt from `result[3]` of the frozen research.
- **Biology batches** (2026-11-23, my decisions):
  - 2 batches of 4, so each workflow stays at 7 agents;
  - model chapter `chemistry/s116-laws-atomic-theory`, added to teaching-style.md;
  - glossary ids assigned per chapter before writing; nucleic acid reuses `chemistry.nucleic-acid`;
  - glossary sources are the 領綱 or 考試說明 where 樂詞網 was not checked;
  - biology.json: s116-cell-division also lists s116-cell-energy as a prereq, because it uses ATP; the Mendel blurb says 複等位基因 (the 領綱 form), not 複對偶基因.
- **mhchem in lessons** (2026-11-22, my decision): `astro.config.mjs` imports `katex/contrib/mhchem`, so `\ce{…}` works in MDX prose as well as in item banks. Widget string props stay plain text, so use Unicode subscripts there.

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
