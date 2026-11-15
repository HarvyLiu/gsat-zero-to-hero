# 學測 Zero-to-Hero: bilingual course website plan

## Context

**Goal.** A free, professional, bilingual (繁體中文 zh-TW ⇄ English) course website for Taiwan's 學測 (GSAT). It covers:
- Math (數A and 數B);
- Science: 物理, 化學, 生物, plus **地球科學** and 探究與實作, which research shows are in 學測 at equal weight;
- Social Studies: 歷史, 地理, 公民與社會;
- 國文, as a beta.

**Requirements you set:**
- Zero to hero: no prerequisites are assumed.
- No jumps: no idea appears before it is taught.
- Professional and sourced: nothing is made up.
- Visual and engaging, with a professor–student dialogue in the style of OSTEP.
- The style of your ASMC project. ASMC was only ever **read**: no files there are written, built or run.

**Where we are now.** The working folder `C:\Users\spp_l\Downloads\Claudechats\projects\學測` is empty. Today is 2026-11-15. The **116學年度學測** runs 2027-01-22 → 24, which is 68 days away.

### Decisions already made (yours)

| Topic | Decision |
|---|---|
| English audience | Bilingual Taiwanese students who sit the exam in Chinese. English pages show the zh term beside each key term on first use, e.g. "real number（實數）". |
| Dialogue | Like ASMC, a short teacher–student dialogue opens and closes every chapter. The body is explanation, visuals and worked examples, with "student asks" callouts. There is a **new character pair** for this site. |
| Pilot subject | **Math**. |
| "And more" | Extra depth inside 學測 topics, **plus** clearly labelled optional tracks beyond 學測 (分科 加深加廣 previews), placed after the core. |
| Language default | The browser's language on the first visit, otherwise 中文; the learner's choice is remembered. |
| Look | **The same style as ASMC as it is now**, with a per-subject accent colour and icon, plus CJK fonts. The paper is white (Mocha in dark mode) with **one even, thin blue grid** and no thicker or darker major lines. Isometric scenes sit on a single-layer thin `--scene-grid`. Cards and the isometric style stay as they are. **Update 2026-11-15 (owner):** the colours are this site's own "answer sheet + red pen" theme (cream paper, navy ink, 朱紅 vermilion accent, indigo links, highlighter yellow; dark mode is deep navy), and the logo and heading markers are isometric open books, so the site doesn't resemble ASMC. |
| Out of scope | The 英文 paper. |
| Priority | **The 116 sitting comes first**: a verified exam-review sprint ships before 2027-01-22. The full zero-to-hero course follows for the 117 sitting. |
| Your review | You approve outlines and spot-check chapters. Contested History and Civics chapters get an extra AI "balance" pass plus your full read. Because your review is light, the automated verification is stricter (see Accuracy system). |
| Licence | Lessons: CC BY-NC-SA 4.0. Code: MIT. Third-party blocks keep their own licences. No ads and no paid tiers, ever. |

### How this plan was built

- **Research.** 12 researchers read primary Mandarin sources: the CEEC 116 簡章 and 考試說明, the 國教院 108課綱 PDFs, 全國法規資料庫, and 選才電子報. An independent adversarial fact-checker then re-checked each report. All 12 came back marked high reliability, after about 150 corrections in total.
- **Design.** 5 independent designers worked on the Math map, the Science map, the Social Studies + 國文 map, the accuracy pipeline and the platform. A critic then cross-checked all five.
- **Raw outputs** are in temp files. Step 1 of implementation copies them into the repo:
  - Research: `C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\a673455e-fcf2-49cf-bfaa-b16e3c4f2485\tasks\woe8teuu0.output`. A backup copy is in `C:\Users\spp_l\.claude\projects\C--Users-spp-l-Downloads-Claudechats-projects---\a673455e-fcf2-49cf-bfaa-b16e3c4f2485\subagents\workflows\wf_a050d5e0-6fd\journal.jsonl`.
  - Designs and critique: `...\tasks\we2og5m5y.output`. Backup in `...\workflows\wf_31eda925-1e2\journal.jsonl`.

---

## Verified ground truth (summary)

**Exam (116 簡章, 初版 115/8/4)**

| Day | Morning (09:20–11:00) | Afternoon |
|---|---|---|
| 1/22 | 數學A | 自然 12:50–14:40 |
| 1/23 | 英文 | 國綜 12:50–14:20; 國寫 15:20–16:50 |
| 1/24 | 數學B | 社會 12:50–14:40 |

- **Scope is 部定必修 only**:
  - 數A = 10年級必修 + 11A; 數B = 10年級必修 + 11B.
  - 自然 = 物理, 化學, 生物, 地科 + 探究與實作, at equal weight.
  - 社會 = 歷史, 地理, 公民, at equal weight.
  - 加深加廣 belongs to the 分科測驗 only.
- CEEC says 國中 content may appear as background knowledge. That justifies the bridge chapters.
- **Scoring:**
  - 單選: all or nothing.
  - 多選 (n options, at least one correct): (n−2k)/n of the points, where k is the number of wrong options, floored at 0.
  - 選填: every blank must be correct.
  - 混合題: written reasoning, graded by the 評分原則.
- **Score bands:** 15 級分, where L = (mean of the top 1%) / 15. The 五標 are the 88th, 75th, 50th, 25th and 12th percentiles.
- **Paper layouts:**

| Paper | Layout |
|---|---|
| 數A | 6 單選 + 6 多選 + 5 選填 (85 points) + one 15-point 混合題組 |
| 數B | 7 + 5 + 5 (85 points) + one 15-point 混合題組 |
| 自然 | 36 × 2 points + 6 題組 = 128. 地科 has 9 Part-1 items plus 2 題組. |
| 國綜 | Out of 100, with 18–20 points of written items |
| 國寫 | Out of 50: one 知性 task and one 情意 task |

- 國文 total = 國綜 × 0.5 + 國寫. Calculators are banned. The math paper prints a formula sheet.

**Syllabus (official 學習內容 codes in scope)**

| Subject | In scope |
|---|---|
| Math | 23 (10年級) + 23 (11A) + 12 (11B), plus 132 bridge codes |
| 物理 | 49 codes. Mostly qualitative and story-driven. |
| 化學 | 46 codes, with explicit depth limits |
| 生物 | 26 codes |
| 地科 | 42 codes |
| 探究與實作 | 4 strands / 14 sub-items |
| 歷史 | 51 codes in themes A–O, thematic rather than chronological |
| 地理 | 77 codes + 3 田野實察 |
| 公民 | 78 codes in 32 項目 |
| 國文 | A/B/C 學習內容 + 15 推薦文言選文 + 國寫 |

**Facts that shape the design**
- **Math curriculum marks:**
  - ★ = not a direct exam target.
  - ＃ = no standalone unit, so it becomes a ≤15-minute 工具箱 interlude.
  - ※ = suggested not in national exams (cot, sec, csc), so it goes to an extension track only.
- **Verified Math ordering fixes:**
  - 式的運算 comes right after 實數.
  - 邏輯 comes before 數列.
  - 矩陣應用 comes after 條件機率.
  - Σ appears only in grade 12, so earlier chapters write sums out.
- **Cross-subject gates:**
  - Chemistry's mole and pH need scientific-notation **arithmetic** (數學 N-10-1, which is not 國中 content) and 常用對數 (N-10-4).
  - Geography's log axes also need N-10-4.
- **Skills the exam tests beyond the 必修 text.** These go in a labelled "exam toolkit", each citing the past item that justifies it:
  - Lenz's-law reasoning;
  - dimensional analysis;
  - ion-equation balancing (111 Q57).
- **Social Studies:**
  - 歷史 needs a chronological backbone first.
  - 地理 has either/or regions (Cc, Ch): cover both options.
  - 公民 has time-sensitive facts, each keyed by exam cycle with an as-of date:
    - 成年 at 18 since 2023-01-01;
    - referendum age 18, voting age still 20;
    - 最低工資 NT$30,900 / NT$205 from 2027-01-01;
    - 憲法訴訟法 and 114年憲判字第1號.

**Copyright and licence rules**
- **CEEC past papers:** link by year, subject and question number; never re-host. Practice items are **original** and labelled as original. Your owner action: you may email CEEC to ask permission to embed; until then the site links only.
- **Terminology:** 樂詞網 term sets cover 數學, 物理, 化學, 生命科學, 地科 and 地理. There are **none for 歷史, 公民 or 國文**, so those use documented alternatives with recorded provenance.
- **Texts and dictionaries:**
  - MOE dictionaries are CC BY-ND: quote verbatim with attribution, never edit.
  - Classical texts: our own transcription from a cited base edition, with each author's death year sourced.
  - Modern 白話文: summaries, links and short quotes only.
- **Simulations and maps:**
  - PhET sims from before 2026-03-29 are CC BY 4.0; newer ones are CC BY-NC.
  - GeoGebra is non-commercial only. The Desmos API is not usable.
  - Build our own widgets with Mafs, JSXGraph (MIT option), Observable Plot/D3, 3Dmol.js and MapLibre.
  - Map data: Natural Earth (public domain) and 內政部 boundaries.
  - **Map point of view:** 內政部 boundaries for Taiwan, the Natural Earth TWN POV file for world maps, stated on the site.
- **OSTEP:** the format idea only, credited on the About page.

**Still unverified.** These are tracked as checks, never assumed:
- any 108課綱 微調 published in 2025–26;
- whether the 113-07-29 考試說明 update changed the math, science or social text;
- the 116 paper layouts (published after the exam);
- some misconception sources (Math M4, M5 and M7 are pending; M11 is a low-P note only);
- licences for the Barlow and JetBrains Mono fonts (checked in S0).

---


### Owner requirements added 2026-11-16 (binding; details in docs/authoring.md)
- Multiple perspectives for every major method (e.g. 3-variable systems by elimination AND as intersecting planes/lines), alternatives that need later knowledge go in a click-to-expand block.
- Visualizing and graphing in every chapter (interactive where possible).
- A cross-unit "solve it many ways" lesson after all units.
- A final optional part of 分科 material used as advanced tools for 學測, taught from zero and labelled 不考學測.
These apply to the 40 Math sprint chapters already written (a revision pass after batch 4) and to every subject after.

## Delivery plan

### Phase A: 116 Sprint (now → 2027-01-22)

**Who it is for.** Current 高三 students sitting 116, who already took 10th–11th grade in school.

**What a sprint chapter is.** A 重點複習 (exam review) chapter for one tight cluster of codes. It is labelled **「116衝刺」**, not zero-to-hero. Each one states its entry assumption: "studied in school; the full lesson arrives in the 117 course".

**Reuse.** Sprint chapters are built with the same framework, data and verification. In Phase B they become the **part-end review/checkpoint chapters** of the full course, so nothing is thrown away.

**Sprint chapter template.** Each chapter runs 20–30 minutes and has:
1. A short opening dialogue.
2. A 1–2 item pre-check.
3. Key ideas, with one diagram or widget each.
4. Original worked examples in 學測 style, with written-out steps.
5. "常見陷阱" traps drawn **only** from documented sources (CEEC 試題分析 or the research literature).
6. "On the exam": code badges, plus links to real 111–115 CEEC items by year and question number.
7. A self-check quiz using real 學測 scoring (單選, 多選 with (n−2k)/n, 選填 digit bubbles, a 混合題 self-check against a rubric).
8. A short closing dialogue.

**Sprint scope.** Estimated at **~130 chapters**; the S1 outline fixes the exact number. A coverage test proves every in-scope code is reviewed.

| Group | Est. | Basis |
|---|---|---|
| Site | 5 | Welcome; exam literacy (級分, scoring, 混合題); exam-day rules; formula-sheet guide; countdown and 68-day planner |
| Math | ~30 | CEEC 10年級 groups (數與式, 指數與對數, 數列與級數, 直線與圓, 三角比, 多項式與函數, 數據分析, 排列組合, 機率), 11 shared/A/B clusters, and exam skills (選填, 多選 strategy, 混合題 writing) |
| 自然 | ~45 | 物理 ~11, 化學 ~11, 生物 ~7, 地科 ~9, 探究與實作 and 自然 exam skills ~3, exam toolkit ~4 |
| 社會 | ~44 | 歷史 ~13 (A–O plus 史料判讀), 地理 ~17 (技能, 系統, 視野, both either/or cases, map and chart reading), 公民 ~14 (plus a time-sensitive facts page) |
| 國文 beta | ~10 | 15篇 grouped, 國綜 skills, 國寫 知性 and 情意 (original model answers at several levels, annotated against the official rubric) |

**Sprint milestones**

| ID | When | Delivers | Acceptance | Your gate |
|---|---|---|---|---|
| **S0 Framework (sprint subset)** | 11/16 → ~11/26 | Scaffold; i18n; dialogue; core components; registries imported from frozen research; tests; Python verification harness; Cloudflare preview deploy | All sprint tests green on Windows; preview URL works (language switch, scoring, KaTeX, dark/light, 375px) | Pick the character pair from 3 proposals; check look and feel on the preview |
| **S1 Sprint outline** | ~11/22 → 11/27, overlapping S0 | Every sprint chapter spec, with codes, objectives, concepts reviewed, CEEC items indexed and sources | Coverage test: every in_gsat code is reviewed, in an order that respects verified `depends_on` | **Approve the outline per subject** |
| **S2 Production** | ~11/27 → 1/10 | Math first (by ~12/08), then 自然 (by ~12/20), 社會 (by ~1/03), 國文 beta (by ~1/08). zh-TW publishes as soon as it is verified; EN follows within the same batch (`localeStatus`). | Every chapter passes the gates below | Spot-check about 2 chapters per part; read every contested, legal or time-sensitive chapter in full |
| **S3 Freeze** | 1/10 → 1/21 | Re-verify every fact and exam rule; a final mixed review set per paper; exam-day page | No fact past its review-by date; 0 open sev1/sev2 | Final look |

Post-exam (1/24 onward):
- index the 116 papers (link only);
- re-check the paper layouts;
- update facts (for example 最低工資 and §1223, which takes effect about 2027-02-17).

### Phase B: full zero-to-hero course for the 117 sitting (2027-02 → about 2028-01)

**Scale.** About 870 chapters, or about 1,740 bilingual lesson pages, after the critic's fixes:

| Subject | Chapters |
|---|---|
| Math | 215, in 34 parts |
| Science | ~236 + track previews |
| 歷史 | ~94 (+20–30 from splits) |
| 地理 | ~96 |
| 公民 | ~106 |
| 國文 | ~94 |

**Milestones**

| ID | Delivers | Acceptance | Your gate |
|---|---|---|---|
| **M0+** | Framework completion beyond the sprint: MasteryMap (cross-subject knowledge graph), PlacementCheck (test out of bridges), full spaced-review queue, draw items, band rubrics | Full test suite green | — |
| **M1 Full course data** | Every chapter of every subject: kind, namespaced codes, newConcepts (registry ids), uses, prereqs, sources, minutes. Includes the concept-ownership table and a signed waiver file. Overloaded chapters are split (history backbone, math bridges). 國中/國小 code titles are checked against the 課綱 text. | **Global** no-jump; code-level `depends_on` (waivers only); concept uniqueness; per-paper closure; either/or coverage; all 15 選文 present; generated `docs/curriculum/*.md` | **Approve each subject outline (Math first)**; approve the Math waivers (D2a/b/c); approve concept ownership |
| **M2 Math pilot** | Part 0 + Part 1 bridges, about 12 chapters, through all gates strictly in order | Token and time cost measured; template and prompts frozen as v1 | Read all ~12 pilot chapters (needed to lock voice and template) |
| **M3** | Math, in two halves: (a) bridges and 10年級, which unlocks the science gates; (b) grade 11 + 數A and 數B paths + capstone mocks | Published bilingual | Spot checks |
| **M4** | Science, in the round-robin order (all 4 sciences rotating, Math gates first) | 163 codes + 14 探究 sub-items covered | Spot checks; exam-toolkit list |
| **M5** | Social: 地理 → 公民 → 歷史, with the contested gate last | Claims typed (fact / attributed perspective / question); facts keyed by exam cycle | Every contested, legal or time-sensitive chapter, in full |
| **M6** | 國文 beta | 15篇 with base-edition provenance and death years | Base editions; the English approach for 國文 |

**Recurring checks:**
- each August: the new 簡章;
- each October: 最低工資;
- after each exam: index the papers.

---

## Course architecture (Phase B maps, already designed)

### Global structure

1. **Site Part 0**: welcome, how the site works, choose papers and route, placement.
2. **Exam literacy**: one owner for 級分, 多選 scoring, 混合題, the formula sheet and exam-day rules. Subjects only *use* these concepts.
3. **Per subject:**
   - bridge parts (國小/國中);
   - core parts;
   - exam-skills and exam-toolkit parts;
   - capstone mocks (original);
   - optional extension tracks (labelled 不考學測).

**Paths.** 數A, 數B, 自然, 社會 and 國文 are *paths*. Only extensions and the 116 sprint are *tracks*.

**Cross-subject edges** may only point into bridge chapters or whitelisted gate chapters:
- math `scientific-notation-arithmetic` (N-10-1);
- math `using-log-tables` (N-10-4), which also owns "reading a log axis";
- math probability basics, statistics charts, coordinate plane and similar figures.

Other cross-subject links are see-also only. For example, civics → history is see-also.

**Concept ownership.** Each concept has exactly one owner chapter, with `deepens` links for spiral revisits:

| Concept | Owner |
|---|---|
| unit conversion, order of magnitude, speed, significant digits | Math |
| latitude and longitude | 地理 bridge |
| 半衰期 | 地科 E2.6; Math `exponential-functions` deepens it |
| atmosphere and ocean circulation | ownership table settled in M1 |

### Math (pilot): 215 chapters, 34 parts, about 96 hours

| Parts | Content |
|---|---|
| 0 | Welcome |
| 1–7 | Bridges: 58 chapters. 國小 numbers, ratio and patterns, shapes, measurement and data; 國中 numbers and algebra, geometry, polynomials and functions, statistics and probability. |
| 8–16 | 10年級: 60 chapters. 數與式, 指數與對數, 數列與級數, 直線與圓, 三角比, 多項式與函數, 數據分析, 排列組合, 機率. |
| 17–22 | Shared grade 11: 26 chapters. Radian, vectors, space concepts, exponential and log graphs, probability, matrices. |
| 23–27 | 數A path: 27 chapters |
| 28–30 | 數B path: 11 chapters. Conics, proportion and perspective, periodic and growth models. |
| 31 | Exam skills + 2 capstone mocks |
| 32–33 | Extensions: ※ content, Σ, 12甲/乙 preview |

**Path rule.** A 數B-only learner never needs a 數A chapter.

**Prerequisite gaps found by the critic, to fix in M1:**
- `real-numbers` ← `absolute-value-distance`; its proof prerequisite is dropped by moving the √2 proof into a ★ box.
- `circle-equation` ← `quadratic-equations`.
- `polynomial-division` ← `cubic-identities`.
- `sets-toolbox` ← `lines-and-circles`.
- `vectors` ← `trig-any-angle`.
- `sum-difference-formulas` ← `law-of-cosines`.
- `conic-sections` ← `circle-equation`.

### Science: about 236 chapters

**Parts:**
- shared SCI-0 (common foundations);
- INQ-1 (探究與實作, short dedicated part);
- SCI-E (environment and sustainability);
- per subject: bridges + core;
- 物理 PHY-1…6, 化學 CHE-1…4, 生物 BIO-1…4, 地科 EAR-1…5;
- X (exam toolkit and skills), INQ-2 (inquiry projects), tracks.

**Global order.** Math bridges come first. The four sciences then rotate round-robin (interleaving). Math N-10-1 comes before CHE-2, and N-10-3/N-10-4 come before EAR-2 and CHE-3.

**Physics.** Physics bridge PB1.3 owns "force arrows / collinear net force", and 2D forces stay qualitative. Snell's law uses similar triangles, not sin.

### Social Studies and 國文: about 394 chapters

- **歷史**:
  - Backbone first: chronological bridges for 臺灣, 中國與東亞 and 世界.
  - Then themes A–O. E, J and O become 歷史考察 projects.
  - A recurring 史料判讀 strand runs throughout.
- **地理**:
  - 技能 → 系統 → 視野; maps (Ac) are taught before GIS (Ab).
  - Both either/or cases are covered.
  - 3 virtual 田野實察 projects use open data.
  - A recurring map and chart reading strand runs throughout.
- **公民**:
  - Order: A themes → law Bf→Bg→Bh→Bi→Bj→Bk → government and politics → economics Bl→Bm→Bn→Bo→Bq with markets Ce/Cf/Cg → ideals D.
  - Bridges cover the 國中-only Ba (family) and Bp (money) items.
  - A time-sensitive facts register keeps those facts current.
  - Law is quoted via `LawQuote` from 全國法規資料庫, with an as-of date.
- **國文 beta**:
  - Bridges: 注音, 部首/部件, 標點, 句型, 造字, 國中文言.
  - Skill strands.
  - The 15篇 in an aligned reader: 原文 | 注釋 | 語譯 (our own), plus MOE dictionary boxes kept verbatim.
  - 國綜 混合題 and 國寫 parts.
  - English pages are English explanation around Chinese text that is never translated away; learners always answer in Chinese.
- **Contested topics** (rules for 歷Da/Db/F/Nb and 公Bd/Dd/Bg):
  - Open with the 課綱's own framing questions, using 課綱 wording by default.
  - Every sentence is one of three types: a documented fact, an attributed interpretation, or the course's own question.
  - At least two cited perspectives are shown in equal-size cards.
  - The teacher character stays neutral.
  - 228 content uses archival sources and carries a content note.
  - Live legal disputes are dated, not settled.

---

## Accuracy system (strict, because your review is light)

**Canonical language.** zh-TW is written first and verified against zh sources. EN is an **adaptation** of the verified zh. It may not add, drop or change any claim, item, fact, example or widget. EN-only language help lives inside `<ExamChinese>`.

**Gates.** Every chapter is tracked in `production/state/<subject>/<slug>.json`, and any change to an input hash sends it back to `needs-reverify`.

| Gate | What happens |
|---|---|
| G0 Spec | Course-data entry; tests pass |
| G1 Source pack | Every objective and fact has a source id, a locator, an access date and a cached copy with sha256. An independent checker marks each claim supported or unsupported; unsupported objectives are dropped. |
| G2 zh draft | Template, lints and jump scanner |
| G3 Verification | Math, physics and chemistry: a **Python/SymPy harness** recomputes every item, step and answer key. All subjects: a claim verifier checks that no sentence says more than its source. |
| G4 Refute | Adversarial refuter. 0 open sev1/sev2 findings are allowed. A **second, independent refuter** must confirm every sev1 fix (two-key rule). |
| G5 Student read | A fresh reader sees only this chapter and its prerequisites, flags undefined terms and leaps, and must be able to solve every quiz item. |
| G6 EN adaptation + G7 EN verification | Parity and meaning-drift checks |
| G8 Language review | Taiwan usage (no Mainland terms), full-width punctuation, polite 你 register |
| G9 CI | Tests, build and link checks |
| G10 Owner check | Sampled |
| G11 Published | Shows 「最後查證」 with `verifiedAgainst` |

**Extra safeguards for light review:**
- Every answer key and every time-sensitive fact is confirmed by **two independent agents**.
- Contested chapters get an additional **balance pass**: perspective symmetry, claim typing, no unattributed evaluative words.
- Every page has a visible **「回報錯誤 / Report an error」** link (GitHub Issue Form + mailto) and a per-chapter changelog. A sev1 report takes the chapter down within one day.

**Severity.**
- sev1: a wrong fact, key, law or date; a jump; a licence breach; unlabelled beyond-學測 content.
- sev2: misleading, or out of scope.
- sev3: style.

**Registries.** All are validated by Zod schemas in `src/data/schema.ts`.

| Registry | Contents |
|---|---|
| codes | Key `<domain>:<ASCII code>`. Domains: math, nat, soc-elem, hist, geo, civ, chi. Stores the official display glyph, in_gsat and ★/＃/※ marks. Imported from the frozen research by `scripts/import-codes.mjs`. |
| code refs | `{key, part?, case?, role}` |
| concepts / terms | zh, en, definition, term source (樂詞網 or a documented alternative), owner chapter, `deepens`, aliases, forbidden variants |
| items (YAML, single source) | Item text, steps, `verify` path, `@version` in the id, skills tags. Read by both the SymPy harness and the TypeScript loader. |
| facts | Each value has `versions[]`, `examCycle`, an as-of date, a source and a `reviewBy` date |
| misconceptions | Statement, correction, documented source, status. Only verified ones may render. |
| exam index | CEEC year/subject/question → codes, as links |
| sources / licences | Bibliography with licence and access date |

**Production at scale.** Production runs as resumable Workflow batches, one part at a time, 3–4 parts in flight, zh first. Measured in M2. The estimate is about 0.8–1.5M tokens and 2–4 hours of wall time per chapter.

---

## Platform (new Astro project in `學測`, ported from ASMC patterns)

**Stack:**
- Astro 7 + MDX + React islands, using the explicit `unified()` markdown processor, as in ASMC.
- remark-dialogue, ported. remark-math + rehype-katex with KaTeX 0.16.47 + mhchem, rendered at build time.
- Pagefind 1.6 (lang zh-TW / en).
- Mafs, JSXGraph (MIT option), Observable Plot/D3, 3Dmol.js (Phase B) and MapLibre with Natural Earth and 內政部 data.
- Noto Sans TC as self-hosted woff2 slices via Fontsource, alongside a Barlow display font (licence checked in S0) and Catppuccin tokens with per-subject accents (AA contrast tested).
- **Paper grid: thin lines only, exactly as ASMC now has it.**
  - A fixed `body::before` layer (fixed this way so it also stays still on iOS) draws `linear-gradient(var(--grid-minor) 1px, transparent 1px)` in both directions at `24px 24px`, offset `-1px -1px`.
  - `.scene-paper` uses a single `--scene-grid` tile at `34.64px 20px`.
  - There are no `--grid-major` or `--scene-grid-major` tokens.
  - A token test fails if a major/heavy grid layer is reintroduced.
- **Porting style.** ASMC is still being worked on, so `tokens.css` and `paper.css` are re-read and ported from ASMC's *current* state when S0 starts, never from an older snapshot. ASMC itself is never written to.

**i18n:**
- `i18n: { locales: ['zh-tw','en'], defaultLocale: 'zh-tw', routing: { prefixDefaultLocale: true } }`.
- The root `/` is a bilingual chooser and the x-default target. It detects the browser language on the first visit and remembers the choice.
- `LangSwitch` keeps the same page. Pages carry hreflang and a sitemap.
- Lessons live in mirrored files: `src/content/lessons/{zh-tw,en}/<subject>/<slug>.mdx`.
- Quiz data is single-source, so progress is shared across languages.

**Project layout**

```
research/verified-2026-11-15.json         frozen research (read-only input)
docs/design/*.md                          frozen designs + critique; docs/curriculum/*.md (generated)
scripts/ import-codes.mjs curriculum-doc.mjs fonts.mjs katex-assets.mjs check-budgets.mjs shoot.mjs
harness/ (Python, pytest, SymPy)          recomputes math/science items; runs in CI
production/ state/ packs/ reports/        pipeline state (resumable)
src/data/ schema.ts subjects.json characters.ts course/<subject>.json terms/ items/ registry/{codes,facts,misconceptions,exam,sources,licences}
src/content/lessons/{zh-tw,en}/<subject>/<slug>.mdx
src/plugins/ remark-dialogue.ts remark-term-first.ts
src/lib/ progress.ts saves.ts scoring.ts review.ts mastery.ts
src/components/{dialogue,learning,exam,progress,site,scenes,widgets/<subject>}/
src/pages/{zh-tw,en}/…  (thin; delegate to src/views/)
tests/ tests-dist/ e2e/
```

**Dialogue syntax** (ported from ASMC):
- speaker lines `T:` (teacher) and `S:` (student);
- `S[mc=<id>]:`, where the student voices a documented misconception;
- `>> turn: <itemId>`, a "your turn" pause that the reader must answer before the dialogue continues;
- `(stage directions)`.

**Components:**

| Group | Components |
|---|---|
| Teaching | StudentAsks, Term (EN shows "English（中文）" on first use; zh shows English on hover), Predict, TryIt, WorkedExample (faded steps from items) |
| Corrections and scope | Misconception (refutation), Preview (a term used before it is taught), Beyond (beyond-學測 content) |
| Exam | OnTheExam (CEEC link + CodeBadge), Quiz/Exercise (單選, 多選 (n−2k)/n, 選填 bubbles, 混合題 rubric self-check), ExamToolkit, FormulaSheet, ExamCountdown |
| Sources | Fact (value + as-of date + source), Src, Quote, YouNeed (prerequisite reminders, generated) |
| Site and progress | CompleteChapter, ReviewQueue (simple spaced review; full version in M0+), Erratum, changelog, per-subject theming |

**Progress.** Ports `progress.ts`: a versioned schema, localStorage, no accounts, plus export and import.

**Tests (Vitest):**

| Area | Tests |
|---|---|
| Ported from ASMC | No-jump rule, made global and cross-subject; `contrast.test.ts` |
| Curriculum | Code-level `depends_on` with a waiver file; coverage (every in_gsat code); namespace checks; concept uniqueness; per-paper closure |
| Content | Locale parity (same sections, item ids, keys and widgets); glossary completeness (zh + en + source); sources and licences; MDX lint (dialogue opens and closes; minutes ≤ 30 core, ≤ 35 projects, ≤ 15 toolbox, capstones exempt) |
| Facts | Freshness: CI on pull requests warns, and the scheduled job fails and opens an issue |
| Scoring and language | Scoring rules; en-lint (no Han characters outside an allow-list of zh components) |
| Build | `dist` file count under 19,000 (Cloudflare limit 20,000); Pagefind zh-tw smoke test |
| Other suites | pytest harness; Playwright e2e on CI |

**Hosting.** Cloudflare Pages (free; needs your account), with GitHub for the repo, issues and CI. `.claude/launch.json` defines the local dev server (:4321) and preview (:4322).

**Ported from ASMC.** ASMC files are read only; new files are written in `學測`.

| From | To |
|---|---|
| `src/plugins/remark-dialogue.ts` | extended for the new syntax and characters |
| `tests/curriculum.test.ts` | made global and code-level |
| `src/lib/progress.ts`, `src/lib/saves.ts` | ported |
| `src/styles/tokens.css`, `paper.css` | Current version (thin even grid only), plus per-subject accents |
| `src/iso/*` | isometric scenes |
| `src/components/learning/{Quiz,Predict,Exercise,Term,TryIt,CompleteChapter}` | ported and extended |
| `HarvyAsks.astro` | becomes `StudentAsks` |
| `src/layouts/ChapterLayout.astro` | ported |
| `scripts/shoot.mjs`, `curriculum-doc.mjs` | ported |
| `tests/contrast.test.ts` | ported |

---

## Verification (how we know it works)

1. **Automated, on every change:**
   - `npm test`, `npm run typecheck`, `npm run build` (Astro + Pagefind), `npm run test:dist` (file budget, hreflang, Pagefind);
   - `pytest harness/` (every item and answer key recomputed);
   - Playwright `npm run e2e` on CI.
2. **Preview in the browser pane** via `.claude/launch.json`:
   - the language switch keeps the page; first-visit detection works;
   - an item answered in zh shows as answered in en;
   - 多選 scores by (n−2k)/n; 選填 uses bubbles;
   - KaTeX and mhchem render;
   - dark and light themes, 375px width and keyboard-only use all work;
   - the paper matches ASMC: one thin even grid that stays still while scrolling, with no heavy grid lines crossing text, compared side by side with ASMC screenshots;
   - search finds 實數 on zh pages and "real number" on en pages;
   - Fact shows its as-of date and source; the countdown shows the 116 dates in Taipei time.
3. **Content gates:** G1–G9 reports in `production/reports/`. 0 open sev1/sev2 before publishing. You approve outlines (S1, M1) and spot-check.
4. **Screenshots:** `scripts/shoot.mjs` captures key pages at 375px and desktop, light and dark, for the look-and-feel review.

## Your action items (outside the code)

- Pick the character pair in S0 (3 proposals will be given).
- Create the Cloudflare and GitHub accounts or repo, and choose a site name or domain.
- Optionally email CEEC to ask permission to embed past items. Until permission arrives, the site links only.
- Approve the outlines at S1 and M1, and read the contested chapters.
