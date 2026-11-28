# Status and handoff (read this first after a context reset)

Updated 2026-11-28 (inquiry done: all five 自然 subjects are reviewed and active; 社會 116 outline and batch plan approved by the owner). Read these first:
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
- **Tests and checks** (2026-11-28): 587 tests passed and 1 skipped; the harness `--strict` passes on 1,078 items (1,077 recomputed; 133 of them inquiry; the one without a check is inquiry/s116-inq-question-plan q8, a written item, which the rule allows); the type check shows 0 errors; the build, the inquiry render scan (18 pages) and the inquiry control-character scan are clean. The build prints 203 KaTeX strict-mode warnings (Unicode such as ：and ① in math), unchanged; they don't change the rendering. Once, in a full run right after the build, `tests/curriculum/sources.test.ts` failed and then passed in two reruns and on its own: probably a timing flake; watch for it. The site-wide href check passed before the inquiry push (2026-11-28): 24,245 internal hrefs and srcs, 0 broken (hrefs.py in session 24cdd13f's inquiry-handoff).

- **Earth:** 13 sprint chapters, all `reviewed`, subject status `active` (2026-11-27, session 2f9c3a83).
  - 3 workflow batches: batch 1 (wf_b42bb6e0-bb8) universe-stars, sky-motion, earth-history, earth-layers-plates, plate-boundaries-taiwan; batch 2 (wf_7873df5f-e80) air-vapour-clouds, wind-weather-maps, ocean-currents-el-nino, waves-tides; batch 3 (wf_b6809cdd-3b2) typhoons, sustainability, climate-change, earth-data-items. Each batch: Opus writers, an Opus facts reviewer and teaching reviewer, 1 Opus fixer (2.0M, 1.8M and 1.8M subagent tokens), then 1 Sonnet visual reviewer + 1 Opus visual fixer (about 0.4M each; wf_73376318-449, wf_52375645-6e1, wf_5d78f6f7-4a6). Reviews found 1, 0 and 0 sev1; all sev1/sev2 fixed, none disputed.
  - The main session spot-checked the redrawn figures at 375 px after each visual fix.
  - `reviews` in `earth.json` are each chapter's linked glossary ids (zh + en), set by `earth_reviews.mjs`.
  - s116-sustainability reuses `chemistry.sustainable-development` instead of its own duplicate `earth.sustainable-development` (one term, one definition; the chemistry entry cites 樂詞網), so that chapter has no terms file.
  - The earth scripts are in session 2f9c3a83's scratchpad (`C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\2f9c3a83-a5c9-4282-9355-27d71c45acca\scratchpad\`): `earth-sprint-batch.js` (args `batch`, `date`, `lessons`), `earth-visual-review.js` (args `slugs`, `known`, `dark`), `earth_slices.py` and `earth-slices/` (per-chapter slices from `result[5]`), `earth-notes.md` (per-chapter `reviews` ids and the owner questions below), `pacing.py`, `render_scan.py`, `hrefs.py`, `collide.mjs`. A durable copy of the scripts and notes (not the slices) is in `C:\Users\spp_l\.claude\projects\C--Users-spp-l-Downloads-Claudechats-projects---\2f9c3a83-a5c9-4282-9355-27d71c45acca\earth-handoff\`. If the scratchpad was cleared, copy them into the new session's scratchpad, run `python -X utf8 earth_slices.py` there (it writes `earth-slices/` next to itself), and set `SP` in both workflow scripts to that scratchpad. The 23-item `lessons` string from the earth batches is in `earth-handoff/batch3-lessons.txt`; reuse it for inquiry.

- **Inquiry (探究與實作):** 9 chapters, all `reviewed`, subject status `active` (2026-11-28, session 24cdd13f).
  - 3 workflow batches: batch 1 (wf_bdc1a40f-11c, 2.02M subagent tokens) inq-question-plan, inq-argue-model, inq-share-reflect, s116x-one-context-four-subjects; batch 2 (wf_1abdc0a3-813, 2.08M) s116x-cross-subject-data, sci-plot-and-working, sci-short-explanations, sci-exam-toolkit; batch 3 (wf_32ff2006-7d7, 1.75M) the mock `s116-sci-mock`. Each: Opus writers, an Opus facts reviewer and teaching reviewer, 1 Opus fixer; then 1 Sonnet visual reviewer + 1 Opus visual fixer (0.33M, 0.34M, 0.28M; wf_9ef29b57-330, wf_1fb4969c-3b4, wf_c0af80d2-6fc). Reviews found 1, 1 and 0 sev1; all sev1/sev2 fixed (1 sev2 in batch 2 applied in part).
  - The main session DOM-scanned every page at 375 px after each visual fix (tables, display math, quiz options, SVG label clipping and overlap) and fixed what was left: 7 row-oriented data tables transposed to columns; the toolkit's ionic-equation options and the mock's q17 equation split so they fit.
  - **The mock** (130 min page, 110-min paper, 128 points): q1–q36 one 9-item block per subject (physics, chemistry, biology, earth), Part 2 sets 37–39 phys, 40–43 bio+chem, 44–46 chem, 47–49 bio, 50–53 earth+phys, 54–56 earth; 8 written items with four 1-point criteria each. Written by 4 subject part-writers plus an assembler; checks in `harness/checks/m_inquiry_s116_sci_mock_{phys,chem,bio,earth,cross}.py`. Item explanations name their review chapter in plain text (the inline renderer has no links); the page's review table has the links.
  - The exam toolkit is a cross-subject drill (owner, 2026-11-27): Lenz, dimensional checks and ionic-equation balancing are taught in physics/s116-induction, physics/s116-physics-reasoning and chemistry/s116-redox; the toolkit recaps them with links and mixes new practice.
  - Glossary: `src/data/terms/inquiry/` defines the four strand names, 跨科概念 and 操縱／控制／應變變因; `reviews` in inquiry.json set by `inquiry_reviews.mjs`.
  - Scripts and notes: session 24cdd13f's scratchpad, with a durable copy in `C:\Users\spp_l\.claude\projects\C--Users-spp-l-Downloads-Claudechats-projects---\24cdd13f-5e2a-4d46-85c1-42f31c7a5d7e\inquiry-handoff\`: `inquiry-sprint-batch.js` (args `batch`, `date`, `lessons`, `toolkit`; the mock path runs 4 part-writers + 1 assembler), `inquiry-visual-review.js` (args `slugs`, `known`, `dark`, `bankFix` to let the fixer edit a bank and its checks), `inquiry_slices.py` (slices from `result[5]` units 27–32 plus physics/chemistry extras for the toolkit), `inquiry_reviews.mjs`, `scan375.js` (the 375 px DOM scan), `inquiry-notes.md` (per-batch notes and owner answers). The last batch's 40-item `lessons` string is in the batch-3 workflow args (journal wf_32ff2006-7d7); reuse it for 社會.
- **Site changes this session:** table headers no longer upper-case (`.prose th` in `src/styles/global.css`, owner 2026-11-28; units like m/s and mL/min were shown as M/S, ML/MIN site-wide); the harness requires checks for inquiry items (`CHECKED_SUBJECTS`); `overrides.json` patches `nat:pe-Vc-1` with the 自變項／應變項 wording from the biology research (owner approved), regenerated by `npm run import:codes`.

- **社會 116 sprint outline (2026-11-28, session 426f99b5; outline and batch plan approved by the owner 2026-11-28):** 57 chapters in four files, all subjects still `planned`.
  - `src/data/course/geography.json` (20), `civics.json` (19), `history.json` (15) and the new shared `social.json` (社會綜合, 3: s116x-one-context-three-lenses, s116x-social-mixed-groups, the mock s116-soc-mock). Reading copies in `docs/curriculum/` (`npm run docs:curriculum`, which also refreshed the stale science copies).
  - Coverage: 歷史 51/51, 地理 80/80 (incl. 田野實察 ×3), 公民 78/78 in-GSAT codes; every official dependsOn edge respected; at most 5 content codes per chapter.
  - Contested chapters (design 03 §1.5 gate: claim-type audit, second reviewer, 爭議地圖 box, owner's full read, changelog): history s116-taiwan-status-documents (Da-Ⅴ-2), s116-228-white-terror-justice (Db-Ⅴ-2), s116-china-state-society (F-Ⅴ-1 section), s116-cold-war-and-after (Nb-Ⅴ-2 section); civics s116-state-and-government (Bd-Ⅴ-1), s116-law-constitution-rights (Bg-Ⅴ-2, live dispute TS-12), s116-multiculture-global (Dd-Ⅴ-2 section). Each chapter's `activity` says so.
  - Time-sensitive facts (design 03 §3.3 TS register) are named per chapter in `activity`; civics chapters take values only from `facts.json` through `<Fact>`; the TS checklist is the last section of civics/s116-civ-law-data-items.
  - Site change for the new subject: `social` added to `SUBJECT_IDS` and the chapter/term/lesson id regexes (`schema.ts`, `content.config.ts`), `PAPERS_OF_SUBJECT` (`registry.ts`), `subjects.json` (planned), and a neutral grey accent (Catppuccin overlay2, owner 2026-11-28) in `scripts/subject-tokens.mjs` → `src/styles/subjects.css`. Reviewed by 1 Sonnet reviewer (2026-11-28: 1 sev2, 3 sev3, all fixed: `social` added to `SUBJECT_ORDER` in `scripts/curriculum-doc.mjs`, `CHAPTER_RE` in `harness/verify_items.py`, the paper map in `tests/curriculum/structure.test.ts`, and the subject count in `src/data/curriculum.ts`). The build passes and makes `/<locale>/social/`.
  - Generator: `social_outline.py` in session 426f99b5's scratchpad (`C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\426f99b5-e436-4bf7-91f0-976c48cbff65\scratchpad\`); edit the JSON directly from now on.
  - Checks (2026-11-28): `npx vitest run` 601 passed, 1 skipped (curriculum 139).

**Committed and pushed:** the 社會 outline and the site change above, `docs/teaching-style.md` (社會 model chapters), the regenerated `docs/curriculum/` copies and this note. Committed (7147925) and pushed at the owner's request (2026-11-28) after the site-wide href check: 24,373 internal hrefs and srcs, 0 broken.

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
9. **Earth open questions for the owner** (details in the batch journals and `earth-notes.md`):
   - **Not in the sources:**
     - the history dates 1912, 1962 and 1968 and the name form 韋格納 (earth-layers-plates): keep them as standard facts, or show decades only?
     - 「最大震度4級」 in a StudentAsks (plate-boundaries-taiwan): the CWA scale's format isn't in the sources; keep it or reword without a number?
     - the Taiwan Strait tide model (waves-tides, EIc-Vc-4): the tide enters from both ends and meets near 臺中, the range is largest mid-strait, and flood currents run south in the north and north in the south. Quiz q8 depends on it; it is framed as 「課本常用的解釋」. Confirm or drop.
   - **Standard facts the writers used without a source:** magnitude rules (5 magnitudes = ×100, absolute magnitude at 10 pc); Wien's law qualitatively; atmospheric windows; axial tilt 23.5°; Polaris's altitude equals the latitude; the sky turns 15° per hour; block motion at normal and reverse faults; most of the nebula's mass went into the Sun; the atmosphere layer names and their heating; the dew-point cup and the wet- and dry-bulb thermometer; force directions (pressure gradient perpendicular to the isobars, Coriolis to the right in the Northern Hemisphere and zero at the equator); friction over land vs sea; the crest moving one wavelength per period. Also the name forms 哈伯 and 秒差距.
   - **Wording:** earth-history now says 「四十多億年」 instead of the unsourced 46 億. All numeric data in the earth chapters is labelled 示意數據 / illustrative. air-vapour-clouds gives cooling rates as question data without naming lapse rates; confirm that this stays inside 「不涉及乾、濕絕熱直減率」.
   - **Batch 3:**
     - nat.json gives ENb-Vc-1 to ENb-Vc-4 the same text, so which code covers glacial periods can't be checked; `earth.glacial-period` and the climate items cite ENb-Vc-2 (unverified).
     - unsourced standard facts in typhoons: a typhoon's energy comes from condensation heat; it weakens over cold sea and after landfall; windward mountain rain; the wind returns from the opposite direction after the eye; no calm lull at a buoy the eye misses; the Pacific High steers the track. In sustainability: renewable vs non-renewable resources (可再生資源 / 不可再生資源 also unsourced), the R/P ratio, groundwater over-pumping and subsidence; tidal range and intertidal width. In climate-change: solar activity doesn't match the recent warming (softened, points to an illustrative figure).
     - the earth-data-items ratio table: "about" cells were dropped and a note says some values are rounded.
     - typhoons cites 114學測第44～46題 (slice-verified) and the 考試說明 尼伯特 buoy sample (nat.json + slice tag).
10. **Site components found during the earth visual reviews (not fixed; site-code changes):**
    - `NumberLine` text scales down to about 7 px at phone width;
    - the fill-in answer sheet's digit row scrolls sideways at 375 px;
    - `Graph` has no way to set the tick step from MDX (a `tickStep` prop), and Mafs' own tick labels can't be moved;
    - `Graph`'s colour name `red` maps to the token `--teal`, which is vermilion (#c8402a). The name misled the batch-1 fixer. Consider renaming the token.
    - figure text across subjects says 黑色 / black for `ink` items, which show as cream in dark mode.
    Batch-2 lessons for the batch-3 writers: wide tick ranges crowd at phone width (pick ranges giving ticks every 5 or 10); a figure label must not answer the figure's own task; label the axes of every data graph; isobar values sit on their own rings.

    Update 2026-11-28: the upper-case table headers are fixed (owner). Inquiry avoided `NumberLine` entirely (drawn as `Graph` number lines instead). Also found in inquiry:
    - item stems have a 257 px box and quiz options a 200 px box at 375 px, and both hide their sideways scrollbar, so a too-wide table, equation or option is silently cut off. Writers must keep stem tables narrow (short headers, units in the text) and split long equations; a visible scroll cue in `exam.css` would make the failure obvious;
    - the item renderer (`src/lib/render-inline.ts`) has no markdown links, so `[text](url)` in an explanation shows raw; banks name review chapters in plain text.
11. **Inquiry open questions for the owner** (details in the batch journals and `inquiry-notes.md`):
    - **Answered 2026-11-27:** argue-model takes math/s116-data-analysis as a prereq; pe-Ⅴc-1 carries the 自變項／應變項 wording; batch-1 items 3–5 accepted.
    - **Standard facts not in the sources** (used softened or stated in the stem):
      - batch 2: Cu + Ag⁺; O₂ as the oxidant of Fe²⁺ (now only "the oxidant in the given equation"); the Fe³⁺ + I⁻ and Al + H⁺ equations (given to balance only); water evaporating from an open container; a switched-off field decays fast (the figure says its decay is drawn slower than real).
      - the mock: ethanol's ΔH = −1367 kJ/mol (q14) and Mg burning in CO₂, 2Mg + CO₂ → 2MgO + C (q18), both given in the stems; q11 uses ³⁴S (Z 16, A 34) though atomic-structure's isotope examples use only C and H (the item never calls it an isotope).
    - **Exam claims:** s116x-cross-subject-data says the 112–115 cross-subject sets were all two-subject and that 113 Q50–53 was chemistry with earth science; both come from the slice's research text and the earth confirmed list, not a separate verification entry.
    - **Depth:** plot-and-working q7 plots six stations' temperature against height and gets −6 ℃/km as a slope from data; it never names a lapse rate. Inside 「不涉及乾、濕絕熱直減率」?
    - **Course framing without a source:** three questions for judging a source; claim–evidence–reasoning–scope (claim–evidence–reasoning–limits in cross-subject-data); manipulated variable on the x axis; the term 外插; the romanised names Waisanding and Kinmen. en glossary terms for the strands and variables are not checked on 樂詞網.
    - **Overlaps kept:** mock q31 vs plot-and-working's ridge example; mock q52 vs plate-boundaries' Predict (different twist). short-explanations keeps its own draft 1→2→3 example and figure, opening with a link to earth-data-items' 限字說明 section.
    - **Wording:** the mock's opening calls itself the last chapter of the 116 science sprint; the toolkit's en title is now "Exam toolkit: tested skills beyond the required text" (inquiry.json, my decision; was "beyond the 必修 text").

## Next
- **Now:** start 地理 in a fresh session with the prep steps below. Still open for the owner: the Da-Ⅴ-2 document list, the 2027 minimum-wage approval (TS-13), the map point of view, and the harness rule for 社會 items.
- **社會 chapter batch plan** (approved by the owner 2026-11-28, modelled on inquiry; one subject per session; each batch runs as a workflow only when the owner asks):
  - **Prep in the main session before 地理 batch 1:** per-chapter research slices from `result[7]` (地理; `result[8]` 公民, `result[6]` 歷史 later) with a `geo_slices.py` like `inquiry_slices.py`; glossary ids assigned per chapter before writing (地理 has 樂詞網 `naer-terms-geography`; 歷史 and 公民 have no 樂詞網 set, design 03 §6); `social-sprint-batch.js` and `social-visual-review.js` adapted from the inquiry scripts, with the 40-item lessons string of inquiry batch 3 (journal wf_32ff2006-7d7) plus the 社會 rules (contested gate, time-sensitive facts, maps without national boundaries until the map point of view is decided); 1 Sonnet reviewer for the `social` site change; an owner decision on the harness rule for 社會 items: `--strict` requires a recomputed check for every item of a subject in `CHECKED_SUBJECTS`, but most 社會 items are conceptual, so I propose checks only for numeric items (inheritance shares, GDP, supply and demand, map scale, rank-size), which needs a small harness change.
  - **地理 20 = 4 batches of 5:** (inquiry-methods, maps-contours, geographic-information, climate-system, landform-system), (population, settlements-central-place, cities, industries, world-system), (taiwan-and-world, east-asia, southeast-south-asia, australia-new-zealand, islamic-world), (europe, united-states, global-south, globalisation, geo-map-items).
  - **公民 19 = 4 batches (5, 5, 5, 4):** (citizenship-legal-capacity, duties-sovereignty-identity, human-rights-norms, state-and-government, law-constitution-rights), (administrative-law, criminal-juvenile, civil-rights, governance-media, elections-referendums), (choices-incentives-trade, supply-demand, market-price-controls, competition-externalities, national-income-labour), (justice-social-security, multiculture-global, technology-trade, civ-law-data-items).
  - **歷史 15 = 4 batches (4, 4, 4, 3):** (how-we-know-the-past, indigenous-and-migrants, economy-and-cultures, modern-state-democracy), (taiwan-status-documents, 228-white-terror-justice, china-state-society, east-asia-migration), (tradition-meets-modern, war-and-peace-east-asia, europe-ancient-christian, individual-liberty-reason), (islam-west-and-world, cold-war-and-after, hist-sources-written).
  - **社會綜合 3 = 1 batch:** 2 writers + the mock as 3 subject part-writers and 1 assembler (as the 自然 mock).
  - **Each batch:** Opus writers (medium), 1 Opus facts-and-answers reviewer and 1 Opus teaching-and-wording reviewer (high; in contested chapters they also run the claim-type audit), 1 Opus fixer (high): 6–9 agents. Then 1 Sonnet visual reviewer (medium) and 1 Opus visual fixer (high) only if there are sev1/sev2 findings. Main session: harness, vitest on what changed, render and 375 px DOM scans.
  - **Cost:** about 2.4M subagent tokens per 5-chapter batch, 1.9M per 4, plus about 0.35M per visual pass: about 11M 地理, 10.5M 公民, 8.5M 歷史, 2.6M 社會綜合, so about 33M in all, over 13 batches.
  - **Owner reads in full** every contested, legal or time-sensitive chapter (plan.md S2 gate): the 4 contested history chapters and nearly all of 公民.
- Before 社會 chapters, the owner may also want to answer Pending 9 and 11 and decide Pending 10.
- **自然:** ~~chemistry (15)~~ → ~~biology (8)~~ → ~~earth (13)~~ → ~~inquiry (9)~~: all done (2026-11-28).
  - For earth: give the writers the biology lessons too (already in the batch `lessons` string). Biology's notable ones:
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
- **Then:** after 社會, 國文 beta.

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
- **Earth batches** (2026-11-23, my decisions; owner asked for a workflow):
  - 3 batches (5, 4, 4) in dependency order, each followed by 1 Sonnet visual reviewer and an Opus visual fixer only if there are sev1/sev2 findings;
  - model chapter `biology/s116-cell-division` for the content chapters (best pacing of the reviewed chapters: 3 predictions, 22 moments; and no single chapter models every subject); `physics/s116-physics-reasoning` for `s116-earth-data-items`;
  - glossary: the 29 research terms, plus 颱風, 永續發展 and 冰期 from the 領綱 titles (source naer-science-guidelines); reuse `physics.em-spectrum`, `physics.wavelength`, `chemistry.isotope`, `chemistry.greenhouse-effect`; `s116-earth-data-items` defines no ids;
  - data shown as real must come from the slice, otherwise it is labelled 示意數據; maps are schematic `Graph axes={false}` drawings; the agency is 中央氣象署; Taiwan tectonics only as the evidence-based convergent boundary.
- **Inquiry batches** (2026-11-27, owner asked for a workflow per batch):
  - 3 batches in dependency order: (question-plan, argue-model, share-reflect, one-context-four-subjects), (cross-subject-data, plot-and-working, short-explanations, exam-toolkit), (the mock);
  - model chapters (my decision): `chemistry/s116-laws-atomic-theory` for the inquiry and cross-subject chapters (inference from experiments and data); `earth/s116-earth-data-items` for the three exam-skills chapters instead of `physics/s116-physics-reasoning` (which misses the pacing targets: 14 moments, 180 words per moment); `math/s116-mock-a` for the mock;
  - the exam toolkit is a cross-subject drill, not a re-teach (owner);
  - the mock is split across 4 subject part-writers with fixed item numbers and their own check modules, plus 1 assembler (my decision), laid out like the 115 paper in papers.json;
  - glossary: strand names from the 領綱 (naer-science-guidelines); 操縱／控制／應變變因 cite `ceec-past-papers` (113 自然 非選擇題評分原則 第43題), because the research takes them from that scoring guide and the registry has no separate 113 rubric entry;
  - exam-skills chapters state the general 自然 rule, practise it on new contexts and link the subject exam-skills chapters instead of re-teaching them.
- **社會 outline** (2026-11-28):
  - **Owner:** about 57 chapters (歷史 15, 地理 20, 公民 19, 社會綜合 3) rather than the plan's ~44, so each 30-minute chapter reviews at most 5 codes as in the science sprint; a separate 社會綜合 course for the shared part, because 合科 items were about 56% of items in 114 and about 40% of the score in 115 (as inquiry holds the 自然 mock); writing order 地理 → 公民 → 歷史 → 社會綜合 (plan.md M5: fewest owner questions first, contested gate last); no new components (quoted source and statute blocks, Perspective, schematic Graph maps, Fact, rubric self-checks for drawing); a neutral grey accent for 社會綜合, because the four unused Catppuccin hues each sit near a subject or a role colour.
  - **My decisions** (owner may veto):
    - each subject ends with its own exam-skills chapter (地理 讀圖作圖非選; 公民 法條情境、圖表、非選 plus the TS checklist, which replaces the plan's separate "time-sensitive facts page"; 歷史 史料判讀 with 歷史考察 E/J/O, which have no content of their own and are tested through skills, 115 Q38);
    - history follows the 課綱 themes A→O only; the full design's 國中 chronological backbones are not repeated, and needed 國中 facts are recapped in place;
    - Da-Ⅴ-2 and Db-Ⅴ-2 get chapters of their own so the contested gate covers as little else as possible; F-Ⅴ-1, Nb-Ⅴ-2, Bd-Ⅴ-1, Bg-Ⅴ-2 and Dd-Ⅴ-2 sit in their themes' chapters, which are flagged contested as a whole;
    - both either/or geography regions are reviewed (東南亞 with 南亞 in parallel; 中南美洲 and 漠南非洲 side by side), because CEEC items 不偏版;
    - the 田野實察 codes are reviewed inside the chapter the 課綱 table puts them after (Bb, Cb, Ci);
    - 公民 Bk-Ⅴ-1 (juvenile procedure) is reviewed with criminal law, which it builds on; economics runs micro then macro with 勞動參與 after Ce, Cf and Cg;
    - geography s116-cities takes math/s116-logarithms as a prereq (official edge Be-Ⅴ → N-10-4, log axes); no civics → history prereqs, because history is written last (cross-links are added when the history chapters exist);
    - schematic maps show coastlines and regions without national boundaries until the owner decides the map point of view (design 03 §2.5);
    - model chapters (in teaching-style.md): `earth/s116-climate-change` for 地理 batch 1, then the best-paced reviewed geography chapter (also for 公民 and 歷史 until their own first batch is reviewed); `earth/s116-earth-data-items` for exam-skills chapters; `inquiry/s116x-one-context-four-subjects` for the cross-subject chapter; `inquiry/s116-sci-mock` for the 社會 mock.
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
