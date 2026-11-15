<!-- Frozen critic output, 2026-11-15. Its fixes are adopted by the approved plan. -->

# Cross-check and integration review of the five 學測 designs

**Method.** I read the reference test and the research JSON, querying only the parts I needed: `final_units`, corrections, unverifiable claims, the math bridges, the tech and pedagogy findings, and grep checks of specific claims. I also rebuilt the Math map's chapter graph (codes and prereqs for all chapters in Parts 0–30) and tested it mechanically against the verified math `depends_on`. Results are cited as "[scan]". All effort figures in §5 are my planning estimates, not facts.

---

## 1. Conflicts between designs, each with a fix

**A. Curriculum against curriculum**

1. **Exam-format concepts are introduced 4–6 times.**
   - 級分, 多選 scoring, 混合題/非選, calculator-free estimation and significant digits appear in:
     - math `what-is-gsat`, `multiple-select-strategy` and `calculator-free-arithmetic`;
     - science X.1 and X.2;
     - Z0.1 (級分, 混合題) and H0.1, G0.1, C0.1.
   - This breaks "each concept introduced exactly once" across subjects.
   - **Fix:** one site-level Part 0 plus a short "exam literacy" part that owns these concepts. Subject exam parts only *use* them. Math keeps the expected-value *strategy* for 多選 after Part 16.
2. **The same concept is introduced in two subjects.** Each needs one owner.

   | Concept | Introduced in | Fix |
   |---|---|---|
   | unit conversion | math `speed-and-units` and science S0.3 單位換算 | math owns |
   | order of magnitude | math `exponents-logs-project` and S0.3 數量級估計 | math owns |
   | speed | math `speed-and-units` and probably PB1.1 (Eb-Ⅳ-8) | math owns |
   | significant digits | math `scientific-notation-arithmetic` and X.2 有效位數 | math owns |
   | 半衰期 | math `exponential-functions` (grade 11) and E2.6 | see item 6 |
   | logarithmic scale | math `logarithmic-functions` (grade 11) and geography G4.6 對數刻度 | see item 4 |
   | meridian / parallel of latitude | math `globe-circles` and geography G1.1 經緯度 (owner: 地理 bridge) | geography owns |
   | 能量形式 | S0.7 and P5.1 | S0.7 owns |
   | 萬有引力 | PB1.6 and P1.4 | needs a "deepens" link |
   | pH | CB2.3 (國中 Jd) and C3.5 | needs a "deepens" link |
   | 牛頓定律 | 國中 version (PB1.5) and 高中 version (P2.3) | needs a "deepens" link |

   - Also unresolved: 地科 vs 地理 ownership of atmospheric circulation, surface currents, waves and coasts, and plates, and the overlap of SE.4 永續 with 地理.
   - **Fix:** a global registry with one owner per concept, plus a `deepens: <conceptId>` relation for spiral revisits.
3. **Civics has hard prereqs into history core chapters**: C2.2 ← H6.1, C2.5 ← H5.3, C6.3 ← H5.7, C10.3 ← H6.6.
   - This contradicts the design's own §5 table ("歷史 → 公民: none required").
   - C2.2 (civics Part 2) would wait behind the 32 history bridge chapters plus Parts 5–6.
   - **Fix:** turn all four into see-also links.
4. **Log axes for geography.**
   - The social design proposes 「對數刻度」 built on N-7-6~8 only. The verified geography `depends_on` for 地Be says "數學 N-10-4 常用對數 (log axes)" (corrected entry).
   - Math puts "logarithmic scale" in grade-11 `logarithmic-functions`, which also duplicates the concept.
   - 地科 E5.3 規模 is a log scale too, and E4.1 星等 may be one; the design leaves the magnitude formula as an open item.
   - **Fix:** move "logarithmic scale (reading a log axis)" into math `using-log-tables` (N-10-4, both paths). Then G4.6 and E5.3 depend on that chapter.
5. **The chain to Chemistry's mole gate is too long.**
   - `scientific-notation-arithmetic` (the N-10-1 gate for C2.2, C3.4, P5.6, P6.1 and E1.1) has 22 ancestors [scan].
   - The reason is that `real-numbers` depends on `constructions-and-proof`, only for the ★ √2 proof. That drags in congruent triangles and constructions.
   - **Fix:** move the √2 proof into `logic-toolbox` or a ★ "go deeper" box. Drop that prereq and add `absolute-value-distance` (see §2). That cuts the gate to 16 ancestors and `common-logarithms` from 30 to 25 [scan].
6. **Half-life.**
   - A 自然 learner meets 半衰期 in E2.6, a 10th-grade chapter in round-robin step 18, long before math Part 20.
   - The research says "only exponential decay / half-life still has no verified curriculum code."
   - **Fix:** E2.6 owns the concept (repeated halving, using the 國中 等比 bridge). Math `exponential-functions` declares `deepens` with its own self-contained definition, so 社會-only or math-only learners are not forced through 地科.
   - Close the science open item "Is 國中 等比數列 within N-8-3~6?": the verified bridge "數列：等差、等比；等差級數" (N-8-3~6) says yes.
7. **`globe-circles` is on the 數B path only**, but math §5 lists it as "needed by 地理".
   - The platform forbids cross-subject prereqs into chapters that are not on all paths.
   - **Fix:** see-also only. `globe-circles` *uses* `geo:geo-latlong`.

**B. Curriculum maps against the platform data shape**

8. **Codes cannot be expressed.**
   - The platform uses `codes: CodeKey[]` as `subject:ASCII`. This misses:
     - math's "(part)" annotations, such as N-10-1 main vs the 備註★ portion, and S-11A-1 split across shared Part 19 and 數A Part 26;
     - geography's either/or *cases* (Cc 東南亞 or 南亞; Ch 中南美洲 or 漠南非洲);
     - the pipeline's `role`.
   - Namespaces also collide. Bare codes repeat across curriculum domains, and the platform's subject prefix does not disambiguate 國中 codes shared by several subjects:
     - 國文 `Ab-Ⅴ-1`, 公`Ab-Ⅴ-1` and 地`Ab-Ⅴ-1`;
     - 國中 自然 `Ab-Ⅳ-1`, 國文 `Ab-Ⅳ-1` and 地`Ab-Ⅳ-1`;
     - 自然 `Ba-Ⅳ-1`, 公`Ba-Ⅳ`, 地`Ba-Ⅳ` and 國文 `Ba-Ⅳ`;
     - 國小 社會 `Cb-Ⅱ-1` and 國文 `Cb-Ⅴ`.
   - 國中 自然 codes are shared by physics, chemistry, biology and earth science, so a subject-based prefix would duplicate them.
   - **Fix:** key = `<domain>:<ASCII code>`, with domains math, nat (all 自然 incl. 國中), soc-elem (國小 社會), hist, geo, civ and chi. Store the official glyph form for display.
   - Ref shape: `{key, part?, case?, role}`.
9. **Glyph canon disagrees.**
   - Platform normalises Ⅴ to ASCII V. Pipeline makes U+2164 Ⅴ canonical and lints *against* ASCII V.
   - **Fix:** ASCII in keys, official glyph in a display field, and drop the pipeline's "no ASCII V" lint.
10. **探究 sub-items.**
    - The platform's `strands` enum has 4 values. Science requires 14 sub-items, each in at least 2 projects.
    - **Fix:** `inq:<strand>/<subitem>`.
11. **Kinds.**
    - The platform has no `exam-skills`, `capstone` or `review` kind; `exam-toolkit` wrongly requires a `justification` item.
    - Math uses slug regexes (`-project`/`-capstone`); science and social use the [PROJ] convention.
    - **Fix:** structure is driven by `kind` alone. 數A/數B are `paths`, and only extensions are `track`s; math's "track purity" becomes the platform's path rules (my scan found no purity violations).
12. **Missing item types.**
    - No drawing item: geography DrawIt and science X.3 作圖 need one.
    - No band rubric: 國寫 三等六級 and history 等級2/1/0 need one.
    - No `skills` tags (H1–H9, G1–G9, C1–C7, A/B) for review mixing.
    - No placement test-out: math and social both depend on it for the 68-day reality.
    - **Fix:** add `draw` (self-check against a model overlay), `rubric.type: 'criteria'|'bands'`, `skills[]` and a `PlacementCheck` mastery shortcut.

**C. Pipeline against platform**

13. **Three registries for the same data.**
    - Facts: pipeline `facts.json` (single value + effectiveFrom), platform `facts.json` (`versions[]`), social `time-sensitive.json` (TS-IDs).
    - Concepts and terms: pipeline `concepts/<subject>/<slug>.json`, platform `terms/<subject>/<chapter>.json`, social `terms/{subject}.json` with provenance.
    - **Fix:** one merged schema each. Facts use `versions[]` + `examCycle` + TS alias + volatility/reviewBy. Terms are one file per chapter with zhSource/enSource/status/alternatives/surface/forbiddenVariants; `introducedIn` is derived from course data, never stored.
14. **Two item formats.**
    - Pipeline: YAML with steps, `verify:` paths and `@version`, read by the Python harness. Platform: TS with String.raw; WorkedExample steps are authored in MDX.
    - **Fix:** YAML is the single source, read by both the SymPy harness and the TS loader. `<WorkedExample id>` renders steps from the item. Keep `@version` in ids so stale progress is invalidated.
15. **Dialogue syntax.**
    - Pipeline: `STUDENT[mc=…]:`, `PAUSE`. Platform: `T:`/`S:`, `>> turn: q1`.
    - **Fix:** `T:`/`S:`, `S[mc=id]:`, `>> turn:`.
16. **Jump detector.**
    - The platform checks only `<Term>` tags, so an untagged 「莫耳」 in prose passes. The pipeline's surface scan needs `<Later>`/`<Preview>`, which the platform lacks.
    - **Fix:** adopt the surface scan for multi-character terms only. Single-character terms (場, 功, 力, 熱, 波, 能) must be Term-tagged, or the false-positive rate will be unworkable. Add `<Preview until=chapterId>`.
17. **Gates and components the platform has not scoped.**
    - Infrastructure: the Python harness and pytest step in CI (platform CI is npm-only), `production/` state, the `.cache/sources` text cache.
    - Frontmatter and history: `lastVerified`/`verifiedAgainst`, the status enum mismatch (`draft|reviewed` vs `published`), per-chapter changelog plus `/changes/`, `Erratum` and "report a problem".
    - Components: Src, Beyond, ExamToolkit, Quote, LawQuote, Perspective, SourceCard, ClassicalText, MoeDict, ExamChinese.
    - **Fix:** M0 builds Src, Beyond, Preview, ExamToolkit, Quote, Erratum, the changelog and the harness. The rest arrive with their subject milestone.
18. **Parity and lint contradictions.**
    - The pipeline's "multiset of numbers in prose" parity breaks the platform's EN label "GSAT 115 (Jan 2026)".
    - en-lint (no Han outside 5 components) breaks EN 國文/社會 pages, which deliberately keep Chinese items, quotes, LawQuote and SourceCard.
    - The "zh-first publishing" switch breaks platform locale parity.
    - **Fix:**
      - numbers rendered by `<Year>`/`<Fact>`/registries are exempt from the numbers check;
      - en-lint gets an allow-list of zh components;
      - add `localeStatus` per chapter.
19. **Minutes limit.**
    - Platform mdx test: `minutes ≤ 30`. Math: projects 35, capstones 130. The pedagogy finding: "well under about 35 minutes", with effects non-significant beyond 35.
    - **Fix:** core ≤ 30, projects ≤ 35, toolbox ≤ 15, `capstone` exempt.
20. **＃ marks.**
    - Pipeline: "＃ codes never title a standalone chapter". Math and platform: standalone `-toolbox` chapters. The research says ＃ "needs no standalone teaching unit".
    - **Fix:** `kind: toolbox` interludes of ≤ 15 min, labelled 工具箱, never titled as a unit; the test checks kind and minutes. Owner sign-off (§6).
21. **Stale facts block deploys.**
    - `facts.test` fails CI when `today > reviewBy`. Exam-layout facts expire on 2027-01-25, which would block erratum deploys.
    - **Fix:** PR CI warns; the scheduled job fails and opens an issue.

## 2. Jump risks

**Code-level `depends_on` gaps in the Math map** [scan]. A gap here means no chapter teaching code X has a chapter teaching Y among its ancestors. Besides the declared D2a and D2b, 7 gaps are unflagged:

| Gap | Fix |
|---|---|
| N-10-1 needs N-7-5 | `real-numbers` ← `absolute-value-distance` |
| G-10-3 needs A-8-7 | `circle-equation` ← `quadratic-equations` |
| A-10-2 needs A-10-1 | `polynomial-division` ← `cubic-identities` |
| D-10-1 needs G-10-4 | `sets-toolbox` ← `lines-and-circles` |
| G-11A-1 and G-11B-1 need G-10-6 | `vectors` ← `trig-any-angle`. A real gap: components by angle/magnitude. |
| G-11A-5 needs G-10-7 | `sum-difference-formulas` ← `law-of-cosines`. The usual derivation needs it. |
| S-11B-2 needs G-10-3 | `conic-sections` ← `circle-equation` |

At chapter level there are 59 misses. Most are legitimately covered by another chapter of the same code (for example `lines-and-planes-in-space` lists S-11B-1, but only `globe-circles` needs radians). So the test must be code-level, with `part` annotations and a signed waiver file.

**Overloaded chapters, where "≤5 concepts" is met only by packing labels:**
- Math bridges:
  - `solids`: 7 shapes as 3 labels, plus volume and surface area;
  - `plane-figures-and-area` and `circles-and-sectors`: 5 concepts each, but several labels bundle multiple ideas;
  - `whole-numbers`: 6 codes in 20 minutes;
  - `decimals`: 7 codes in 20 minutes.
- Science:
  - BB3.4: 7 國中 codes;
  - BB3.5: 6 codes;
  - CB1.6: 5 codes;
  - CB2.3: 6 codes;
  - P1.4: field, gravitation, electric field and Coulomb in one chapter.
- History backbone:
  - H3.1 covers 商周至隋唐 in one chapter;
  - H4.1 covers Africa, West Asia, Greece and Rome;
  - H4.5 covers the American and French revolutions, industrialisation and nationalism.
  - Their concepts are unspecified, and they need splitting by 國中 條目 (roughly +20–30 chapters).
- **Fix:** a label-packing lint (flag labels joining 3 or more nouns) and a bridge code-load warning (more than 4 codes in a 20-minute chapter).

**Science needs that math schedules late:**
- Net force, free-body diagrams (P2.3, P2.5) and 三力與風 (E3.5) need 2D force addition, but vectors are grade-11 math. **Fix:** physics bridge PB1.3 owns "force arrows / collinear net force", and 2D stays qualitative.
- P3.3 Snell's law is 「以圖示法定量說明」. Using sin would pull in math Part 12 (about 40 ancestors), so keep it to similar triangles.

**Terms used before they are taught.** These need `<Preview>`:
- DNA in B2.1 and B2.3;
- 莫耳 in CB1.3;
- 發酵 and 光反應/固碳 in B1.7;
- the 國中 vs 高中 Newton and pH pairs listed in §1 item 2.

**Unscheduled cross-subject reads:**
- G4.6 log–log axes jump if geography skips N-10-4 (§1 item 4).
- C9.7 percentage change rests on a math concept whose code is unverified, as math itself notes.
- `multiple-select-strategy` jumps if "surfaced early" before Part 16.

**Outlines too thin to validate:**
- Roughly 250 social and 國文 chapters under "Later parts" list codes but no newConcepts or uses.
- Science bridge tables give only concept counts.
- M1 cannot pass until these are filled.

## 3. Accuracy and licence risks

| Design says | Research says | Action |
|---|---|---|
| Math D2: "None of these breaks a dependency" | Verified `depends_on`: A-11A-3 ← A-11A-2; G-11A-6 ← G-11A-4; F-11A-4 ← A-11A-4 | These are deviations from verified data, possibly safe ones. Log them as owner-signed waivers. Note the research calls some order fixes "dependency logic; the curriculum does not prescribe an order". |
| Math §3 implies the map is dependency-complete | 7 gaps (§2) | Fix before M1 |
| Math uses M4, M5 and M7 as documented misconceptions | Verification marks these unverifiable: "112 數A Q19/Q20 common errors… and 112 數B Q19 vanishing-point errors… pages … were not fetched" | No refutation box until G1 re-opens the pages |
| Math tags M11 as a misconception | "reported as low success rates rather than coded errors" | Low-P note only |
| Science I2.2 「隕石定年 地×化×物 115 Q54–56」; I2.3 「大氧化事件 地×化×生 113 Q50–53」 | CEEC classes 115 54–56 as 「地」 and 113 50–53 as 「化/地」 | Label per CEEC; the cross-subject framing is ours |
| Social: 「All 15 authors died long ago, far past §30」 | No death years in the research. 張李德和 (〈畫菊自序〉) is a 20th-century 臺灣古典散文 author. | Source each author's death year in `texts/*.json` before publishing full text |
| Social history total: "57 are core (P5–P11)" | The chapters listed add up to 56 | Trivial |
| Pipeline checklist: "國史館: 政府資料開放授權 with attribution" stated as settled | Only a research `resources` entry; the social design marks it open | Re-verify in G1 |
| Pipeline PhET: "no modification except translating the attribution" | Tech correction: that rule applies only to the attribution text | Reword |
| Platform scoring test: "blank → 0" | Research gives only (n−2k)/n with a floor of 0 | Source the blank rule from 簡章 成績計算 (which has worked tables) before encoding it |
| Platform: dist "should land in the low thousands" | 845 chapters × 2 locales ≈ 1,700 lesson pages, about as many Pagefind fragments, ≥232 Noto TC slices (464 if .woff leaks), plus KaTeX, JS and SVG ≈ 5–8k files (my estimate) | Under the 19k guard, but measure with a stub build in M0 |
| Social TS-11: pre-amendment §1223 "applies on exam day" | True for 116 only. The amendment takes effect 6 months after 115-08-17. | Key facts by `examCycle`; the answer flips for 117 |

The science open item about 國中 等比數列 can be closed (§1 item 6).

**Licence risks:**
- Wikisource CC BY-SA blocks impose share-alike on those blocks, so prefer our own transcription.
- NC assets (newer PhET, GeoGebra, 均一) bind the whole site to non-commercial use, so no ads or paid tiers.
- CEEC 例題 contain third-party historical sources. Do not paraphrase them closely in dialogues; write new sources.
- Barlow and JetBrains Mono licences are not in the research; Iansui is still beta.
- MOE ND entries stay verbatim. An EN gloss must be visibly ours and separate.

## 4. Gaps

- **Uncovered `in_gsat` items:**
  - 國文 學習表現 4-Ⅴ-2 (with Ab-Ⅴ-4 書法) is not mapped.
  - The "woven" codes PMc-Ⅴc-4 and CMb-Vc-1 pass coverage vacuously. A test should require a tagged 人物卡/科學史 block in every physics or chemistry part.
- **Missing parts:**
  - One site Part 0: welcome, how it works, choose papers/route, placement.
  - An exam-day logistics chapter built from verified facts:
    - devices: smart glasses mean a zero; a phone at the seat costs −3 級分;
    - entry and exit: bell 5 min before; no entry after 20 min; no leaving in the first 60 min;
    - materials: 2B pencil and black ink; correction tape for ink only; A3 卷卡合一 answer sheet; +30 min accommodation;
    - after the exam: answers 19:00 the next day; objections until 1/27; final answers 2/17; scores 2/25; re-check 2/26–3/4.
  - Registration status (closed 11/10; 檢核 11/13–19, in progress today; seat lists 116/1/05).
  - A cross-subject 68-day planner.
  - Full-length original mocks for 自然 (110 min), 社會 (SI.4 is only "a section") and 國綜+國寫.
  - Cross-subject interleaved review sets.
  - An 英文 out-of-scope notice (46.09% of 115 candidates took all six papers).
  - Credits/licences, privacy, `/changes/`, an accessibility statement.
- **Missing tests:**
  - code-level `depends_on` with a waiver file;
  - global concept uniqueness;
  - `deepens` and Preview resolution;
  - per-paper closure: a 社會-only path may pull only bridges and declared gate chapters from other papers;
  - a whitelist for cross-subject edges;
  - domain-namespace checks;
  - either/or case coverage;
  - 14 探究 sub-items, each in at least 2 projects;
  - all 15 選文 present;
  - fact value by examCycle;
  - misconception status gating;
  - minutes per kind;
  - label packing;
  - the en-lint allow-list.
- **Missing data:**
  - per-code content for 12甲/乙 and for the history and geography track codes;
  - checks of 國中/國小 per-code titles against the 課綱 text (math O1; social open item 2);
  - concepts for the thin outlines listed in §2.

## 5. Scale reality

- **Chapters as designed:**

  | Subject | Chapters |
  |---|---|
  | Math | 215 (195 core + 20 extension) |
  | Science | 236, plus 48–80 track previews (16 elective courses × 3–5) |
  | 社會 + 國文 | 394, plus 10 tracks of unspecified size |
  | **Total** | **845 core + extensions, about 925–975 with tracks** |

  - After merging the duplicate Part 0s (about −3) and splitting history and math bridges (about +25–40), that is roughly **870 chapters, or about 1,740 MDX lesson files** plus item banks.
  - Calibration: the reference outlined 239 chapters and wrote 52 (single language), so this is about 34× its written volume.
- **Learner time** for all five papers from zero is about 825 chapters × about 25 minutes ≈ 340 hours of lessons. That cannot fit 68 days, so the 116 sitting cannot be a zero-to-hero target.
- **Per-chapter pipeline effort (estimate; calibrate in M2):**
  - About 14 agent runs: pack + pack check, draft, computational and claim verification, refuter (+1 for sev1), beginner zh, about 2 integrator runs, EN adaptation, bilingual + EN beginner, 2 language reviews.
  - About 0.8–1.5M tokens and about 2–4 hours wall time serially.
  - Throughput is integrator-bound at about 8–12 chapters a day, with 3–4 parts in flight.
  - Whole programme: about 0.7–1.3B tokens and about 75–110 pipeline-days, before owner wait time.
  - Owner time:
    - pilot: about 30–45 minutes per chapter;
    - after that: first chapter of each part (about 140) + 20% sample (about 170) + 100% of contested, legal and time-sensitive chapters (about 120), about 400 reviews × 15–20 minutes ≈ 100–135 hours;
    - G0 outline sign-offs: about 25 hours.

**Milestones**

| M | Scope | Acceptance criteria | Owner reviews |
|---|---|---|---|
| M0 Framework | Platform §9 plus §1 fixes: domain-namespaced code import for all subjects from the frozen research (0 unmapped), merged schemas, YAML items, Python harness + pytest in CI, `production/` state, Src/Beyond/Preview/ExamToolkit/Quote/Erratum/changelog, PlacementCheck. Sample chapters are fixtures only. | All test suites green on Windows and CI. A stub build of about 900×2 pages reports the dist file count, largest file and build time. hreflang, chooser, switcher and shared progress pass e2e. | Preview URL (look, CJK, dark/light, 375px). Character pair + 2 voice samples. Brand/domain/accounts. Licence policy. |
| M1 Course data for all subjects | Every chapter in every subject has kind, codes (objects), newConcepts (registry ids), uses, prereqs, sources and minutes. Concept-ownership table. Waiver file. Term pass for math, science and geography against 樂詞網 datasets. | Coverage complete: math 58 + 132 bridge codes, 自然 163 + 14 sub-items, 歷 51, 地 77 + 3, 公 78, 國文 33 + A1–A6/B1–B5 + 15 篇. Global no-jump, code-level `depends_on` (waivers only), concept uniqueness, per-paper closure and case coverage all green. Generated curriculum, coverage, cross-subject and waivers docs. | G0 per subject (math first). The waivers (D2a/b/c). Concept ownership. Contested-topic policy. |
| M2 Pilot | Site Part 0 + exam literacy + math Part 1, about 12 chapters, run strictly serially G0→G11 | 0 sev1/sev2 open. Harness green. Measured tokens, time and beginner-reader pass rate recorded in `docs/ops.md`. Prompts and template frozen as v1. Schedule recalibrated. | Every chapter, in full |
| M3a Math through 10th grade | Bridges Parts 2–7, Parts 8–16, Part 31 skill chapters that need only 10th-grade content, widgets | Published bilingual. Unlocks the N-10-1 and N-10-4 science gates. | First chapter of each part + 20% |
| M3b Math grade 11 | Parts 17–30 and both capstones | Both mocks fully verified by the harness. Path navigation correct. | Both mocks in full + sample |
| M4 Science | SCI-0, INQ-1, SCI-E, bridges, round-robin core, X, INQ-2 | 163 codes published. TK chapters cite indexed items. Constants authority chosen. PhET/3Dmol entries complete. | TK list, licence exceptions, sample |
| M5 Social | Geography (map POV, datasets), civics (TS register, LawQuote), history (contested gate), integration | Claim-type audit on contested chapters. Every fact keyed by examCycle. | 100% of contested, legal and time-sensitive chapters |
| M6 國文 beta | Texts registry with base editions, MOE dataset, 國寫 rubric chapters | 15 篇 with sourced provenance and death years | Base editions; EN approach for 國文 |
| Ops gates | Recurring checks | After 2027-01-24: index the 116 papers and re-verify layouts. About 2027-02-17: §1223 in force. August: 117 簡章. October: 最低工資. | Any fact flips |

The 117 sitting (date unknown) is the realistic zero-to-hero target. An optional 116 slice (site Part 0, exam literacy, logistics, formula-sheet page, countdown) is feasible before 2027-01-22 only if M0 runs fast.

## 6. Decisions only the owner can make

1. **Launch target.** Recommended: Math zero-to-hero for 117, plus an optional thin 116 slice.
2. **Review capacity and sampling.** Recommended: the M2 pilot reviewed 100%, then the sampling in §5 (about 100–135 hours).
3. **A second human reviewer for contested history and civics** (228/轉型正義, 臺灣地位, 兩岸, 憲判). Recommended: recruit a volunteer Taiwanese teacher; without one, those chapters ship last.
4. **Map point of view.** Recommended: 內政部 boundaries for Taiwan and the Natural Earth TWN POV file for world maps, stated visibly on the site.
5. **Site content licence.** Recommended: CC BY-NC-SA 4.0 for prose and MIT for code. Third-party blocks keep their own licences. Never monetise, because of the NC assets.
6. **Publishing locales together or zh-first.** Recommended: together for Math and science; zh-first allowed for the 國文 beta.
7. **Math curriculum-handling deviations.** Approve D1 (shared grade-11 chapters), the D2a/b/c waivers and ＃ handled as ≤ 15-minute 工具箱 interludes. Recommended: approve all.
8. **Whether to write to CEEC for permission to embed past items.** Recommended: yes, sent by the owner. Until then, link only.
9. **Characters, brand, domain, accounts and error-report channel.** Recommended: GitHub Issue Forms + mailto at launch.

## 7. Top 12 changes for the merged plan

1. Create a site-level Part 0 + exam-literacy part (級分, 多選 scoring, 混合題, logistics, formula sheet). Delete the duplicates in math Part 31, science X.1/X.2 and the four subject P0s.
2. Codes become `<domain>:<ASCII>` keys with an official display glyph. Code refs become `{key, part, case, role}`.
3. Make the `depends_on` test code-level with a signed waiver file. Fix the 7 math gaps in §2.
4. One global concept registry with an owner table, `deepens` and `<Preview>`. Resolve every duplicate in §1 item 2.
5. Cross-subject edges only into bridges and whitelisted gate chapters. Civics → history becomes see-also. Add the per-paper closure test.
6. Shorten the chemistry gate (drop the proof prereq from `real-numbers`). Move "log scale" into `using-log-tables` (N-10-4) so 地Be keeps its verified dependency.
7. Merge the registry designs: YAML items (steps, `verify`, `@version`, `skills`); facts with `versions[]` and `examCycle`; terms with provenance; misconceptions with V/C gating (M4/M5/M7 pending, M11 low-P, H never refuted).
8. Unify kinds (welcome, bridge, core, toolbox, exam-skills, exam-toolkit, checkpoint, capstone, extension) and paths vs tracks. Ends-of-parts are detected by kind. Set the minutes limits per kind.
9. Unify dialogue syntax (`T:`/`S:`, `S[mc=]:`, `>> turn:`). Add the `draw` item type, band rubrics and PlacementCheck.
10. Add the pipeline infrastructure to M0: Python harness in CI, `production/` state, source cache, changelog and errata, the multi-character jump scanner, the en-lint allow-list and the parity number exemptions.
11. Require M1 to fill concepts for all thin outlines, split the overloaded bridge and backbone chapters, and check 國中/國小 per-code titles against the 課綱 text.
12. Adopt the M0–M6 sequence and acceptance gates in §5. Set 117 as the zero-to-hero target. Any 116 slice is exam literacy and logistics only.

### Critical Files for Implementation
- C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\a673455e-fcf2-49cf-bfaa-b16e3c4f2485\tasks\woe8teuu0.output (verified `final_units`, `depends_on` and corrections; freeze a copy into the repo in M0)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\curriculum.test.ts (read-only base for the global, code-level no-jump suite)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\src\plugins\remark-dialogue.ts (read-only base for the unified dialogue syntax)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\schema.ts (to create: merged contracts for codes, concepts, items, facts and kinds)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\course\math.json (to create: math outline with the §2 prereq fixes and the waiver file alongside)