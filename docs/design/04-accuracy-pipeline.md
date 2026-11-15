<!-- Frozen design output (Accuracy & content pipeline), 2026-11-15. Superseded where docs/design/06-critique.md or the approved plan says so. -->

# Accuracy and content-production system: design for 學測 Zero-to-Hero

This covers how several hundred bilingual chapters get written by agents with nothing invented, no jumps and nothing used without permission. It builds on the reference project's pattern: `course.json` is the single source of truth, a no-jump test runs in vitest, and glossary files are split per chapter so chapters can be written in parallel. The research JSON (`C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\a673455e-fcf2-49cf-bfaa-b16e3c4f2485\tasks\woe8teuu0.output`) seeds every registry. Where something needed is missing from it, section 8 lists it as an open item.

---

## 0. Design stance

1. **Closed-book drafting.** A drafter may state only three kinds of thing:
   - a claim from the chapter's source pack, cited by claim id;
   - an entry in a registry (a concept, fact, law, text or exam item);
   - math that the verification harness can derive.
   
   Anything else becomes a `PACK-REQUEST` note to the librarian, never prose. This carries over the reference rule from `docs/m2-design.md` §5: "If something can't be verified, leave it out."
2. **zh-TW is canonical; EN is a verified adaptation** (justified in 1.1).
3. **Data before prose.** These live once, in language-neutral data:
   - answer keys, worked-example steps and numeric values;
   - curriculum codes, facts, law text, classical texts and term pairs.
   
   MDX references them by id, so the two locales cannot drift on substance.
4. **Machines first, agents second, owner last.** Everything that can be a test is a test. Agents look for what tests cannot catch. The owner checks samples and decides policy.
5. **Verifiers are independent.** Verifiers, refuters and beginner-readers run in fresh contexts. They never see the drafter's notes, and the computational verifier never sees the answer key before it computes.
6. **Everything is resumable.** Each chapter-and-gate job is keyed by a hash of its inputs, and its outputs are files in the repo.

---

## 1. The chapter lifecycle

### 1.1 Canonical language: zh-TW first, then an EN adaptation

| Option | Verdict |
|---|---|
| Write both locales independently from the spec | **Rejected.** Verification work doubles. The two drafts end up with different examples and claims, so parity tests can only compare structure, not meaning. |
| Write EN canonical, then translate to zh | **Rejected.** The exam, 課綱, CEEC documents and 法規 are all in zh. Translating into zh invites translationese and Mainland or non-textbook terms, for example 正弦定律 where the CEEC formula sheet says 正弦定理. |
| **Write zh-TW canonical, verify it, then adapt to EN from the verified zh, the spec, the pack and the term registry** | **Chosen.** Verification runs natively against zh sources. EN learners sit the exam in Chinese, so EN must map one-to-one onto zh terms anyway. One verified claim set means EN verification is mostly mechanical. |

EN is an **adaptation, not a translation**:
- It may restructure sentences and add EN-only language aids inside one allow-listed component, `<ExamChinese>`, which explains exam phrasing such as 「下列敘述何者正確」.
- It may **not** add, drop or change any claim, item, fact, example or widget.
- zh-first publishing (EN page hidden and shown as "English version in progress") is an owner switch per part. The default is to publish both locales together. See open items.

### 1.2 Status machine and invalidation

Each chapter has a state file, `production/state/<subject>/<slug>.json`. Its `status` moves through:

`spec → packed → draft-zh → verified-zh → refuted → read-zh → draft-en → verified-en → language-ok → built → owner-ok → published`

There is also a `needs-reverify` status. A chapter is set to it automatically when any input hash changes:
- the spec entry;
- a source document's sha256;
- a registry entry it uses;
- the text of a prerequisite chapter, for concepts this chapter uses;
- the template or prompt version.

Invalidation re-runs only the gates whose inputs changed. A prerequisite's wording change re-runs the beginner-reader gate. A source hash change re-runs claim verification for the claims that cite that source.

### 1.3 Gates

| Gate | Role | Entry | Exit: machine checks | Exit: agent or human checks | Output |
|---|---|---|---|---|---|
| **G0 Spec** | Planner | Part outline approved by the owner | `curriculum.test`, `codes.test` and `concepts.test` pass. That covers no-jump, prereqs earlier, ≤5 new concepts (≤2 for projects), code coverage, and the depends_on rule (§3) | The owner approves the outline once per part (objectives, order, bridges) | `src/data/course/<subject>.json` entry: slug, zh and en titles, blurb, objectives, `newConcepts` (concept ids), `uses`, `prereqs` (may cross subjects, e.g. a chemistry mole chapter → math N-10-1 and N-10-4 chapters), `codes[{code, role: core\|partial\|bridge\|toolkit\|beyond}]`, `sources` (bibliography ids), planned `facts`, `misconceptions`, `examItems`, `activity` |
| **G1 Source pack** | Librarian, then an independent pack checker | G0 passed | Every objective, planned fact and planned claim has ≥1 claim with a source id, locator and access date. Every bibliography entry was fetched: it has an sha256 and a cached copy | The pack checker re-opens each cached document and marks every claim `supported`, `partial` or `unsupported`. If an objective has no supported claim, the objective is dropped or escalated, never kept | `production/packs/<subject>/<slug>.yaml`; new registry entries (facts, laws, texts, exam items, terms) |
| **G2 zh draft** | Drafter-zh | G1 passed, and every prerequisite is at least `verified-zh` | MDX compiles. The template is present: opening dialogue, crux, pre-question, body, a `Misconception` followed by a check item, "Check yourself", exercises, closing dialogue, "Go deeper". All items are in the items YAML. All lints pass: jump detector, notation detector, scope lint, unmarked-number lint, zh punctuation, simplified characters | — | `src/content/lessons/zh-tw/<subject>/<slug>.mdx`; `src/data/items/<subject>/<slug>.yaml` with zh stems, keys and steps |
| **G3 Verification (zh)** | Computational verifier (math and science); claim verifier (all subjects) | G2 passed | The harness is green for every item, step and prose identity. Every `<Src>` claim id exists and is `supported` | The claim verifier checks that each sentence carrying a `<Src>` says no more than its pack claim (paraphrase drift) | `production/reports/.../G3.json` |
| **G4 Refute** | Refuter, plus a second fresh refuter for sev1 fixes | G3 passed | — | 0 open sev1 or sev2 findings. Every fix is re-checked ("two-key" rule for sev1). At most 2 rounds, then escalate to the owner | `G4.json` with findings and their resolutions |
| **G5 Beginner read (zh)** | Fresh beginner agent | G4 passed | — | Every flag is fixed or rebutted with a pointer to the place the idea is taught. Every quiz item can be solved from the chapter alone | `G5.json` |
| **G6 EN adaptation** | EN adapter | G5 passed | `parity.test` passes (§5.4). Every newConcept appears as `<Term>` in EN. No Han characters outside zh components | — | EN MDX; `en` fields added to the items YAML (the key is untouched) |
| **G7 EN verification** | Bilingual checker; EN beginner-reader | G6 passed | Parity again. The harness re-runs automatically (keys are shared) | Meaning-drift review sentence by sentence. EN beginner flags | `G7.json` |
| **G8 Language review** | zh reviewer (Taiwan usage, polite 你 register, term consistency); EN reviewer | G7 passed | zh and EN lints | No sev ≥2 open | `G8.json` |
| **G9 Build and CI** | CI | G8 passed | Full vitest and pytest. MDX compile. KaTeX renders with `throwOnError`. Internal links resolve. External link check. hreflang. Pagefind. Number of files in `dist` < 20,000. Registry staleness | — | Build artefact |
| **G10 Owner check** | Owner | G9 passed | — | Sign-off on the review packet, or on a sample (§6.4) | `review: {by, date}` in state |
| **G11 Published** | Integrator | G10 passed | `lastVerified` ≥ the newest pack access date. `verifiedAgainst` lists source ids with document versions | — | Frontmatter `status: published`, `lastVerified`, `verifiedAgainst`. The layout renders: 「最後查證 2026-11-xx・依據 108課綱數學領綱；116學年度簡章（115/8/4 初版）」 |

**Severity scale**, adapted from the reference changelog's sev1/sev2:

- **sev1:** wrong fact, wrong answer key, wrong law or date; an untaught idea used (a jump); a licence breach; content beyond 學測 not labelled as such.
- **sev2:** a misleading analogy; an ambiguous item; a missing citation; a wrong or Mainland term; a depth limit exceeded inside a labelled box without evidence.
- **sev3:** style or clarity.

A chapter publishes only with 0 sev1 and 0 sev2 open.

---

## 2. Verification methods by content type

### 2.1 Rules shared by every subject

- **Numbers in prose.** Every digit, year or era pattern (年, 世紀, 民國, 西元, BC, AD) in prose, dialogue, callouts or items must be one of:
  - inside math checked by the harness;
  - a `<Fact id>`;
  - in a sentence that carries a `<Src c="…">`.
  
  This is the **unmarked-number lint**. Dialogue lines are not exempt.
- **Quotes are checked against the source text.** `<Quote src loc>` text must be a verbatim substring of the cached extracted text of that source (whitespace normalised). This catches invented quotations mechanically.
- **Exam-item references must come from the index.** "115學測數學A第18題" may appear only as `<PastPaper id="115-mathA-q18">`, from an index entry made by a librarian who opened the PDF and recorded the page.
- **Intentional errors are tagged.** A student's deliberate mistake in a dialogue is tagged `STUDENT[mc=<id>]:`, which needs a remark-dialogue extension. That way the refuter and the jump detector know it is intentional, and it must link to a documented misconception.

### 2.2 Math

**Items and worked examples are structured data**, in `src/data/items/math/<slug>.yaml`:

```yaml
- id: math/real-numbers/ex-03@1        # @version: bump when the key changes, so stale progress is cleared
  kind: worked | faded | single | multi | fill | written | group
  codes: [N-10-1]
  uses: [math.scientific-notation]      # must be in the chapter's allowed set
  stem: { zh: "…", en: "…" }
  options: [{ zh: "…", en: "…" }]
  key: …
  steps: [{ from: "…", to: "…", rule: math.rule.distributive, prompt: { zh: "…", en: "…" } }]
  verify: verify/math/real_numbers.py::ex_03
  original: true                        # renders as 「原創練習題（非大考中心試題）」
  modelledOn: 115-mathA-q07             # optional; link only
  targets: [math.mc.polar-order]
```

**Harness** (Python with SymPy, dev-only, run in CI; not part of the shipped site):
- The computational verifier writes `verify/...::ex_03` **from the stem alone**, then the harness compares its result with `key`.
- **單選:** exactly one option is true.
- **多選:** each option is evaluated as its own proposition. At least one must be true. Do not assume two or more (the 簡章 correction says at least one is correct).
- **選填:** every blank is computed. The answer must fit the bubble format (digits and '−'; a fraction in lowest terms if the form is a/b).
- **Steps:** `from ≡ to` is checked by `simplify(a−b)==0` plus a numeric test at random points. Equations and inequalities compare solution sets over the declared domain. Each `rule` must be a concept in the allowed set, so the self-explanation prompt never names an untaught rule.
- **Parameterised practice generators:** the verifier runs over N seeds.
- **Distractors:** each wrong option must actually be wrong, and ideally maps to a documented misconception.

**Prose math:**
- A test extracts every remark-math node containing `=`, `<` or `≤`.
- Expressions that parse get a random-point identity check.
- Expressions that don't parse are listed for the refuter.
- Math strings must be identical across locales once `\text{}` is stripped (a parity test).

**Exam realism:**
- Constants and approximations may come only from the formula-sheet list in `constants/math-sheet.json`. It is sourced from the 115 數A sheet: √2≈1.414, √3≈1.732, √5≈2.236, √6≈2.449, π≈3.142, log2=0.3010, log3=0.4771, log5=0.6990, log7=0.8451.
- A heuristic flags items that would need a calculator: very large intermediate integers, or logarithms not on the sheet.
- The practice engine's scoring follows the 簡章: 多選 earns (n−2k)/n, floored at 0; 選填 is all-or-nothing. The scoring function is unit-tested against the 簡章's own worked-example tables, copied into a fixture with page locators.
- Mocks show **raw scores only**. They never predict 級分, because L depends on the top 1% of each year's examinees, so any prediction would be invented.

**Curriculum marks:**
- **★** chapters get a "not a direct exam target" badge.
- **＃** content appears only as an integrated interlude, never as a standalone chapter title.
- **※** content (for example cot, sec and csc in F-11A-1, or the Cauchy-to-correlation note in G-11A-7) appears only inside `<Beyond>` boxes or in tracks.
- **Notation detector:** KaTeX macros map to notation concepts (for example `\sum` → `math.sigma-notation`, which is introduced only in a grade-12 preview or track). A core chapter that uses an untaught macro fails.

### 2.3 Science (物理, 化學, 生物, 地球科學, 探究與實作)

- **Constants register** (`constants/science.json`): symbol, value, unit, the precision the course uses, and source. *Open item: the research names no authority for constants.* Each subject declares one value per quantity (for example which g to use), and the same value is used everywhere unless an item states otherwise.
- **Units and dimensions:** worked-example quantities are `{value, unit}`. A units library (pint) checks that every step and the final answer are dimensionally consistent and numerically right. Significant-figure handling follows the N-10-1 備註.
- **Chemistry equations:** every `\ce{}` equation is parsed and checked for atom and charge balance. Unbalanced skeleton equations are allowed only when tagged `exercise: balance-me`.
- **Depth limits as data:** each code in the registry carries `limits[]`, each with text, a locator in the 學習內容說明, and forbidden concept ids and patterns. For 必修化學 these are:
  - valence electrons only for Z = 1–18;
  - no oxidation numbers;
  - no yield or gas-volume calculations;
  - pH without complex calculation;
  - surface area as the only reaction-rate factor;
  - Tyndall effect only for colloids.
  
  The **scope lint** fails a core chapter that uses a forbidden concept outside one of two boxes:
  - `<Beyond>` (超出學測);
  - `<ExamToolkit evidence="<exam-item-id>">`, which must cite an indexed CEEC item that rewarded the skill. Examples: Lenz's-law reasoning; dimensional analysis; ion-equation balancing by atom and charge conservation (111 自然 Q57).
- **Biology and earth-science prose:** every claim is pack-sourced and claim-verified. Ordering constraints become prereq edges that the curriculum test checks (for example surface currents before El Niño). The listed order of 地科 codes is not treated as a teaching order.
- **探究與實作:**
  - Inquiry tasks are tagged with a strand (發現問題, 規劃與研究, 論證與建模, 表達與分享).
  - A coverage test requires each strand in each science subject.
  - Mappings from strands to 學習表現 codes (ti, tr, tc, tm, po, pe, pa, pc, ah, an) carry `provenance: planner-mapping`, because the research marks them as inferred, not official.

### 2.4 Social studies

- **Claim markers:** every factual sentence carries `<Src c="h-a1-c07"/>`. It renders as a superscript footnote that links to the bibliography entry and its locator. The unmarked-number lint plus a **proper-noun lint** enforce this: names from the people, place and event registry need a marker in the same sentence.
- **Dates:**
  - `<Year ad="1895"/>` renders 西元, 民國 and 年號 forms. Conversions are computed by code, and the 年號 table is sourced.
  - Dates and names need one primary or authoritative source, plus a second source for anything contested.
  - The history part opens with a chronological backbone bridge from 國中 material. The three forward-reference primers the research requires are prereq edges: Cold War before Da-Ⅴ-2, communism before Ib-Ⅴ-2, Jesuit missions before Ia-Ⅴ-1.
- **Law:**
  - `<LawQuote id>` renders verbatim article text from `laws.json` (statutes are not copyrightable under §9(1)(1)), with 修正日期, retrieval date and URL.
  - Facts carry `effectiveFrom` so pages can state what is in force **on the exam date** as well as what is current. Example: the 民法§1223 amendment was promulgated 115-08-17 and takes effect six months later, after the 116學測.
  - Where 領綱 wording is outdated (公Fb-Ⅴ-3 says 基本工資; 公Ha-Ⅴ-1 says 聲請大法官解釋), the text uses the current terms (最低工資, 憲法法庭判決), with an alias and a note in the concept registry.
- **Contested topics** (`contested.json`): topic, codes, and ≥2 positions, each with its own sources.
  - A chapter touching a registered topic must present the positions with attribution ("according to X").
  - The refuter checks for loaded language.
  - Example from the research: 114年憲判字第1號 and the 憲法訴訟法 amendments must be presented as disputed.
- **Geography:**
  - Statistics are `<Fact>`s with an as-of date.
  - Map data provenance lives in the media registry.
  - Maps (Ac) are taught before GIS (Ab), enforced by a prereq edge.
  - A coverage test requires chapters for **both** options of each either/or region: Cc (東南亞 and 南亞) and Ch (中南美洲 and 漠南非洲).
  - Three 田野實察 checkpoints exist.
- **Civics bridges:** 國中-only Ba (family) and Bp (money) need bridge chapters. Code coverage enforces this through the depends_on rule (§3). 113 社會 non-choice Q49 tested 機會成本, a 國中 concept, which is the evidence.
- **Exam-item mappings** carry `provenance: ceec-stated | inferred`. Only the 考試說明 例題 state their codes; mapped items are shown as 「本站對應（非官方）」.

### 2.5 國文 (beta)

- **Classical texts** (`texts/<id>.json`):
  - title, author and dynasty;
  - **base edition** (bibliographic details, scan URL, page);
  - transcription source: our own from the scan, or a Wikisource revision id with its licence (CC BY-SA 4.0 or GFDL);
  - punctuation by (ours), and variants against common textbook readings, with sources.
  
  They render only through `<ClassicalText id>`, with a provenance line. A lint flags long runs of Han characters outside components. ctext.org is deep-linked only, because its terms forbid scraping.
- **MOE dictionaries** (CC BY-ND 3.0 TW):
  - `<MoeDict entry>` renders **verbatim** from the downloaded dataset (version recorded). A test checks the rendered text is byte-equal to the dataset.
  - No edits and no conversion to simplified characters.
  - Attribution includes 教育部, the dictionary title, version and URL.
  - **EN pages show the zh entry verbatim plus a separate English gloss labelled as ours.** A translation is an adaptation, which ND forbids.
- **Modern 白話文:** summaries in our own words, links, and short `<Quote>`s under the length cap (§4). Never text taken from CEEC item passages. 國寫 prompts and model essays are original and labelled.
- **Scope:** only the 必修 學習內容 A, B and C and the 15 推薦文言選文. The coverage test asserts all 15 are present. 國學常識 and other electives appear only as tracks.

### 2.6 Adversarial "refute this chapter" pass (G4)

- **Inputs:** zh chapter, spec, pack and registries. Not the drafter's notes.
- **Prompt:** find every way the chapter is wrong, misleading, out of scope, jumping ahead, unlabelled beyond 學測, using Mainland or wrong terms, misstating exam format, introducing a *new* misconception (for example a bad analogy), or infringing a licence.
- **Evidence rule:** every finding must carry evidence (a source locator, a counter-computation, or a registry reference). Suspicions without evidence are logged as sev3 "check" items.
- **Resolution:** the integrator fixes the finding or rebuts it with evidence. A fresh refuter instance re-checks every sev1 resolution.
- **Escaped errors:** any sev1 later found by learners adds a line to the refuter checklist and, where possible, a lint rule.

### 2.7 "Fresh beginner" pass (G5, repeated for EN at G7)

- **Inputs, and nothing else:**
  - the chapter;
  - the full text of its direct prereqs;
  - registry definitions of every ancestor concept;
  - the allowed-concept list.
- **Persona:** a learner who knows only this material. Bridge chapters use a "weak 國中" persona.
- **Tasks:**
  1. List every term or symbol not defined in the chapter or glossary.
  2. List every step where it cannot see why.
  3. Answer every "your turn" pause, quiz and exercise *using only the chapter*, recording answers and any "couldn't".
  4. Estimate the time against `minutes` (target: well under about 35 minutes).
- **Scoring:**
  - Wrong where the key is right → the item or the teaching is unclear (sev2).
  - "Couldn't" → teach-before-test violation (sev1).
  - Undefined term → sev1 if the mechanical jump detector also missed it, and then a registry surface form is added.

---

## 3. Data contracts and the tests that enforce them

All registries live under `src/data/`. Files are split per subject or per chapter so they can be written in parallel, and merged with duplicate checks, as the reference does with `glossary/*.ts`.

| Registry | Key fields |
|---|---|
| **Bibliography** `bibliography.json` | id, title, publisher or author, url (https), `docVersion` (e.g. 「115/8/4 初版」), `accessDate`, `sha256`, `licence` (enum: `gov-open-naer`, `ogdl-v1`, `cc-by-4.0`, `cc-by-nc`, `cc-by-sa-4.0`, `cc-by-nd-3.0-tw`, `cc-by-nc-sa`, `pd`, `statute-§9`, `ceec-nonprofit-attrib`, `arr-link-only`), `reuse` (link \| quote \| verbatim \| adapt \| embed), attribution template, tier (primary or secondary), kind, `watch` (bool) |
| **Curriculum codes** `codes/<subject>.json` | Canonical `code`, `aliases[]` (printed variants), subject prefix, type (學習內容 or 學習表現), stage and grade, track (數A, 數B, both, 自然, 社會…), `in_gsat` (yes \| partial \| no), `marks` (★, ＃, ※), title, `depends_on[]` (from the research), `limits[]`, source plus page locator, status (verified, corrected, added). Seeded from `final_units` and `final_bridging_prereqs` |
| **Concepts** `concepts/<subject>/<slug>.json` | id, `zh`, `en`, definitions in zh and en, `surface` (zh and en aliases), `forbiddenVariants.zh` (Mainland or outdated forms), `notation` (KaTeX macros), `everyday` (bool), `termSource.zh` and `termSource.en` (kind: `curriculum`, `ceec`, `naer-hs-<subject>` with dataset date, `naer-other:<category>`, `law-moj-en`, `proposed` with rationale and reviewer), `introducedIn`, `scope` (core \| bridge \| toolkit \| beyond), `codes` |
| **Facts** `facts.json` | id, domain (exam-rule, law, wage, election, stat, org), typed `value`, unit, template in zh and en with `{value}`, `asOf`, `effectiveFrom`, `effectiveUntil`, `appliesTo` (e.g. examCycle 116), source plus locator, `reviewBy`, volatility (annual, event, stable), `supersedes` |
| **Laws** `laws.json` | law name, pcode, article, verbatim text, 修正日期, effective date, retrieved date, URL, official English URL if one exists |
| **Misconceptions** `misconceptions/<subject>.json` | id, codes, wrong statement and correct idea in zh and en, contrast example, `evidence[{kind: ceec-rubric \| ceec-analysis \| peer-reviewed, source, locator}]` (e.g. 111 數A Q19–20 scanning-rod errors), linked exam items |
| **Exam items** `exam-items/<year>-<subject>.json` | id `115-mathA-q18`, year, subject, part, number, type, points, `paperUrl`, `keyUrl`, `rubricUrl`, `analysisUrl` (選才電子報), `codes[{code, provenance, by, date}]`, documented errors as misconception ids. **Link only** |
| **Contested topics, texts, media, constants** | As described in §2 and §4 |

**Code normalization (a real problem found in the research).** The research codes are written inconsistently:
- Chemistry and earth science use an ASCII `V` (`CCa-Vc-1`, `EEd-Vc-1`); physics, biology and the social subjects use `Ⅴ` (U+2164).
- Physics notes that the 課綱 itself printed one code as `PEa-Va-1`.
- Geography codes carry a spaced prefix (`地 Aa-Ⅴ-1`).
- Ranges appear (`公Ea-Ⅴ-1~4`), and some code fields contain prose ("related 學習表現 (planner mapping)…").

The registry therefore:
- stores one canonical form, proposed as U+2164 `Ⅴ` and U+2163 `Ⅳ`, with the subject prefix as a separate field;
- expands every range into individual codes;
- strips prose out of code fields;
- keeps printed variants as aliases.

### Tests

| Test (vitest unless noted) | Enforces |
|---|---|
| `curriculum.test.ts` (ported from `C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\curriculum.test.ts`, over a **global** graph across subjects) | Prereqs exist and come earlier; every chapter after 0 has a prereq; each concept is introduced once (by id); uses ⊆ the chapter itself plus its ancestors; ≤5 new concepts (≤2 for projects); ≥1 source per chapter; every source cited; all https; every part after Part 0 ends with a project; tracks come after the core |
| `codes.test.ts` | Canonical form only: no ranges, no prose, no look-alike characters (ASCII V, full-width hyphen). Every chapter code exists in the registry. **Coverage:** every `in_gsat: yes` code is covered by ≥1 core chapter. Count assertions match the verified totals (必修物理 49, 化學 46, 生物 26, 地科 42, 公民 32 項目, 歷史 themes A–O, the 15 選文). ＃ codes never title a standalone chapter. ※ and `in_gsat: no` codes appear only in `Beyond` boxes or tracks. **depends_on rule:** for every code a chapter covers, its research `depends_on` codes are covered by that chapter's ancestors, either bridges or earlier core chapters. This is the no-jump rule at the level of the curriculum |
| `concepts.test.ts` | Unique ids. zh, en and both definitions present. `termSource.zh` is never `proposed`. `introducedIn` matches the spec. **Jump detector:** longest-match scan of each concept's surface forms over MDX (both locales), item YAML, widget i18n strings and dialogue lines; any concept that is not allowed fails unless it sits inside `<Later part=N>`. **Notation detector** over math nodes |
| `scope.test.ts` | Forbidden concepts and patterns from `limits[]` appear only inside `Beyond` or `ExamToolkit`, and each `ExamToolkit` cites a valid exam-item id |
| `facts.test.ts` | Schema. **CI fails if any fact used by a published chapter is past `reviewBy`** (warning 30 days before). `reviewBy` stays within the maximum interval for its volatility class. Fact values (e.g. `29,500`, `30,900`) never appear as raw literals in MDX |
| `laws.test.ts` | `LawQuote` ids exist. 修正日期 and retrieved date present. Facts derived from laws have `effectiveFrom` |
| `misconceptions.test.ts` | ≥1 https evidence entry. `<Misconception id>` exists in the registry and is **immediately followed by a check item** (the refutation-text structure) |
| `exam-items.test.ts` | URLs are on ceec.edu.tw. Mapping provenance is set. No CEEC PDF or DOCX files in the repo or `public/` |
| `bibliography.test.ts` | Licence and reuse enums are valid and consistent (a link-only source can't back a `<Quote>`). `accessDate` and `sha256` present |
| `licence.test.ts` | Every file under `public/media` has a media entry. NC assets are allowed only while `site.commercial === false`. ND assets have `modified: false`. Modified SA assets record the derivative licence. PhET licence is derived from the sim's publication date. GeoGebra embeds carry attribution. `MoeDict` output is byte-equal to the dataset. `Quote` length stays under the cap |
| `parity.test.ts` | §5.4 |
| `zh-lint.test.ts`, `en-lint.test.ts` | §5.3 |
| `mdx.test.ts` (ported) | Compiles with remark-dialogue (extended for `PAUSE`, `STUDENT[mc=…]` and the new speaker pair). Frontmatter valid. Imports resolve. `Term` keys exist. Opening and closing dialogues present |
| `quote-in-source` (pipeline step) | Each `<Quote>` text is a substring of the cached extracted source text. It runs where the cache exists. For open-licence sources (NAER, laws), the extracted text may be committed so CI can run it too |
| `pytest verify/` | Math answers, steps, option truth values, 選填 format, generators; chemistry balance; units and dimensions; scoring function against the 簡章 tables |
| `changelog.test.ts` | Any change to a published chapter's content hash needs a new changelog entry. A key change needs an item `@version` bump |

---

## 4. Copyright and attribution checklists

**CEEC (大考中心)**
- [ ] Past papers, answers and 評分原則: deep-link by year, subject and question number. Never re-host files. Never embed full items without written permission. Whether §9(1)(5) applies is unsettled (TIPO 1090203b declined to rule).
- [ ] When discussing an official item: cite it (「115學測數學A第18題」), link it, and quote only the minimum. **Never reproduce third-party passages** inside 國文 or 社會 items. CEEC excerpted those authors under §54 (the 2019 case), and §54 does not cover us.
- [ ] 考試說明: non-profit reproduction is allowed with attribution. Quote sparingly. Commercial use needs prior written consent, so the site must stay non-commercial.
- [ ] 簡章 and the MOE 入學手冊 (marked 版權所有 翻印必究): cite and link only.
- [ ] 選才電子報 analyses: paraphrase and link. Misconceptions taken from them cite the issue and page.
- [ ] Original items are labelled 「原創練習題（仿學測題型，非大考中心試題）」 / "Original practice item (GSAT style, not an official CEEC item)".
- [ ] The course's formula sheet is our own layout carrying the same formulas and values, labelled as ours.

**NAER (課綱, 樂詞網)**
- [ ] Attribution per the 政府網站資料開放宣告 (naer.edu.tw PageDoc fid=324; terms.naer.edu.tw/mysite/about/2/). Third-party or specially marked works are excluded. No distortion.
- [ ] 樂詞網 datasets: record the dataset name and its last-updated date (e.g. 高中以下化學 2026-05-29, 數學 2023-04-06). Attribution goes on the glossary page.
- [ ] 學習內容 text is quoted verbatim, with the code and page locator.

**MOE dictionaries (CC BY-ND 3.0 TW)**
- [ ] Verbatim complete entries only. No edits, no simplified conversion, no translation.
- [ ] Attribution: 教育部, title, version, URL.
- [ ] 異體字字典 (all rights reserved): link only.

**PhET**
- [ ] Record the sim name, version and publication date. Published before 2026-03-29: CC BY 4.0, with no modification except translating the attribution. Newer: CC BY-NC.
- [ ] Use the official embed code in a lazy iframe. Credit "PhET Interactive Simulations, University of Colorado Boulder", the licence and https://phet.colorado.edu. Logo stays visible.
- [ ] Use only as an optional extra; the core teaching uses our own widgets.

**GeoGebra and Desmos**
- [ ] GeoGebra: non-commercial only. "Made with GeoGebra®" plus a link beside each embed. Ask office@geogebra.org before embedding at scale or self-hosting.
- [ ] Desmos: do not use.

**Maps and data**
- [ ] Natural Earth: public domain. Record the version. Decide between the de facto layers and the Taiwan point-of-view file (`ne_10m_admin_0_countries_twn` v5.1.1), and state the choice on the site.
- [ ] 內政部國土測繪中心 boundaries (data.gov.tw 7441 and 7442): 政府資料開放授權條款第1版, attribution in the prescribed format, dataset version recorded.
- [ ] 中央氣象署: attribution; logos and marked images are excluded.
- [ ] OSM, if used: ODbL.

**Images and archives**
- [ ] Wikimedia Commons: check the licence of each file (Commons accepts no NC or ND files). Record author, licence, file URL and any modifications. A modified BY-SA image stays BY-SA.
- [ ] Servier Medical Art (CC BY 4.0, cite as it requests). NIAID BioArt (its credit-line format).
- [ ] 國家文化記憶庫: licensed per item. View-only items are link only. ND items verbatim only.
- [ ] 國史館: 政府資料開放授權 with attribution, except items it marks.
- [ ] Prefer our own isometric drawings.

**Pedagogy and other platforms**
- [ ] OSTEP: format inspiration only. Credit it on the About page with a link to ostep.org. No reused text, analogies or jokes, and no local copies.
- [ ] 均一 (CC BY-NC-SA 3.0 TW): link, or follow NC-SA if any of it is adapted. 因材網 and Khan Academy: concept only, link only.
- [ ] OpenStax Biology 2e (per the research, not re-verified): CC BY-NC-SA 4.0, and it states "no LLM training without permission". Use it only as a cited reference that the claim verifier opens; never paste its text into drafter prompts.

**Modern and classical text**
- [ ] Modern text: summaries plus links. Brief quotation within §52's reasonable scope, with §64 source attribution. Proposed internal cap, which is policy rather than law: ≤2 sentences or about 60 字 per work per chapter, and never a whole poem.
- [ ] Classical text: public domain, with the base-edition provenance recorded. Wikisource transcriptions get CC BY-SA attribution and a share-alike notice on that text block until their status is confirmed.

**Code and fonts**
- [ ] Credits page: OFL fonts; MIT, BSD and ISC libraries (KaTeX, Mafs, JSXGraph under its MIT option, Plot/D3, MapLibre, 3Dmol.js with its requested citation DOI 10.1093/bioinformatics/btu829); Pagefind.

---

## 5. Bilingual quality

### 5.1 Term precedence

**zh term**, in order of precedence:
1. The wording of the code's 學習內容 or 學習內容說明.
2. CEEC 考試說明 or paper wording. For example 正弦定理 on the formula sheet, where the 樂詞網 兩岸 categories list 正弦定律.
3. 樂詞網 高中以下 textbook dataset for the subject (數學, 物理學, 化學, 生命科學, 地球科學, 地理學).
4. Other 樂詞網 categories, **Taiwan column only**. The chemistry research drew on the 兩岸中小學教科書學術名詞 dataset, which lists both usages, so the Taiwan column must be chosen explicitly.
5. The MOE dictionary for general words.

Rejected variants go into `forbiddenVariants`.

**EN term**, in order of precedence:
1. The 樂詞網 高中以下 dataset.
2. Other 樂詞網 categories.
3. Official English versions on law.moj.gov.tw for legal terms; CEEC's English site for exam names (GSAT, AST, TELC; CEEC does not spell them out).
4. The official English names institutions use on their own sites.
5. `proposed`, with reviewer sign-off, shown in the glossary as 「本站譯名 / site rendering」.

**Status per subject:**
- Math pairs were only spot-checked against their 樂詞網 category.
- EN pairs for physics and biology are unverified.
- 17 or more civics pairs are marked UNVERIFIED.
- History's 樂詞網 attributions failed.
- 國文 renderings are "proposed" only.

So a **terminology pass is part of G1 for every subject.** It downloads the ZIP datasets and resolves each term against them. For 歷史, 公民 and 國文 there is no 高中以下 dataset, so it uses 領綱 wording for zh and the documented alternatives above for EN.

### 5.2 Taiwan usage

- zh is written natively, never machine-converted.
- OpenCC is used only as a **detector**:
  - simplified-only characters (those that change under s2t but round-trip under t2s) fail the build;
  - the s2twp phrase table produces suggestions for the zh reviewer.
- A general Mainland-vocabulary list fails the build, for example 信息→資訊, 軟件→軟體, 視頻→影片, 網絡→網路, 概率→機率, 方差→變異數, 摩爾→莫耳. Each entry must be checked against the registry before it is added, so legitimate Taiwan terms are not blocked.
- Code notation follows the registry's canonical form.

### 5.3 Lints

**zh-lint:**
- Full-width punctuation in zh prose: ，。、；：？！「」『』. Math, code and components are excluded.
- No ASCII `,` `.` `?` `!` `:` `;` `()` next to Han characters.
- No `“”`.
- No hand-inserted spaces between Han and Latin letters or digits (the CSS `text-autospace` handles spacing).

**en-lint:**
- No Han characters outside zh-rendering components (`Term`, `Zh`, `ExamChinese`, `MoeDict`, `ClassicalText`).
- So every zh string on an EN page comes from a registry.

### 5.4 Parity tests

For each `lessonKey`, the two locales must have the same:
1. frontmatter keys;
2. heading ids, in order (explicit ids via a remark plugin);
3. ordered sequence of components with their `id` props. The allow-list is `ExamChinese` (EN only) and ruby 注音 (zh only);
4. dialogue turn count, speaker sequence and `PAUSE` ids;
5. sets of `Src` claim ids, `Fact` ids, `Misconception` ids, `Term` keys and `PastPaper` ids;
6. multiset of numbers in prose;
7. math strings, with `\text{}` stripped.

Items are single-sourced, so keys can't differ. `minutes` must be within ±20%.

**EN first use:** `<Term>` renders "real number（實數）" automatically at the first occurrence on the page. The test checks that every newConcept is wrapped in `<Term>` in both locales, and that the visible term string equals the registry form or an alias. Practice items get the 「顯示中文 / show in Chinese」 toggle for free, because each item carries both texts.

---

## 6. Production at scale

### 6.1 Roles

| Role | Writes | Never sees |
|---|---|---|
| Planner | Course spec entries, from the research `final_units` | — |
| Librarian | Source packs; bibliography (fetch, cache, sha256); facts, laws, texts, exam-item and media entries | — |
| Pack checker | Claim verdicts | Drafts |
| Terminologist | Concept registry entries | — |
| Drafter-zh | MDX and item stems, keys and steps | Verify code |
| Computational verifier | `verify/` functions | Keys and steps until it has computed |
| Claim verifier | G3 report | Drafter notes |
| Refuter (two instances for sev1) | Findings | Drafter notes |
| Beginner-reader (zh, en) | Flags and attempted answers | Spec, pack, keys |
| Integrator | **The only editor after the draft**; logs how each finding was resolved | — |
| EN adapter | EN MDX and item `en` fields | — |
| Bilingual checker | Meaning-drift findings | — |
| Language reviewers (zh, en) | Findings | — |
| Owner | Policy decisions, sign-offs | — |

Roles may use the same model but always run in separate contexts with different role prompts.

### 6.2 Batching

- **Job unit:** one chapter × one gate, so each context is small and can be retried.
- **Waves:** chapters move in topological layers. A chapter enters G2 only when its prereqs are at least `verified-zh`, because the beginner-reader needs that text.
- **Batch:** one part (about 4–8 chapters).
- **Pilot:** Math Part 0 plus the first bridge part, run strictly in series. The owner reviews every chapter in full. This calibrates the prompts, the voice guide, the character bible, the chapter template and the gate thresholds, which are then **frozen and versioned**. Any prompt version change marks dependent jobs stale.
- **After the pilot:**
  - Up to about 3–4 parts can be in flight when their prereqs are independent. Integrator throughput is the real limit.
  - Librarian and terminologist work for other subjects (packs, codes, terms) runs ahead in parallel, because it doesn't depend on chapter text.
  - Cross-subject edges still gate drafting. For example, chemistry's mole and pH chapters wait for math N-10-1 and N-10-4.

### 6.3 Caching and resumability

- **Source cache:** `.cache/sources/<sha256>.{pdf,html}` plus extracted `.txt`, with an `index.json` of url → sha256, fetchedAt and type. It is shared across chapters: the 課綱 PDF and the 簡章 are fetched once. 樂詞網 ZIPs, the MOE dictionary dataset and law snapshots are stored with their own dates.
- **Excerpts in a public repo:** packs commit locators. For sources marked `arr-link-only` or CEEC, they commit only an excerpt hash; the excerpt itself stays in the gitignored cache.
- **State files:** `production/state/...` records, per gate: status, input hash, output paths, report path, run id and date. A re-run skips any job whose hash matches and whose gate passed.
- **Reports:** `production/reports/<subject>/<slug>/<gate>.json` holds findings with severity, evidence and resolution, so the owner's review packets are generated from them.

### 6.4 What the owner reviews

**Once:**
- the character pair and the bilingual voice samples;
- the chapter template and the severity policy;
- licence policy decisions: Taiwan map point of view, error-report channel, the quote cap, zh-first publishing.

**Per part:** the G0 outline.

**Pilot:** every chapter.

**After the pilot (proposed policy):**
- the first chapter of each new part;
- a random 20% sample;
- 100% of chapters with contested, legal or time-sensitive content;
- every `proposed` EN term, in batches;
- every licence exception;
- every sev1 fix after publication.

Packets are generated automatically: gate summary, resolved and open findings, rendered diff and preview link.

### 6.5 Re-verification cadence

- **Continuous (CI):**
  - Fails on: a fact past `reviewBy`; parity; licence problems; jump, scope or notation violations; broken internal links; file count over 20,000.
  - Warns on, and opens an issue for: a changed hash on a `watch` source (the affected chapters go to `needs-reverify`); external link rot; chapters with time-sensitive facts that are more than 11 months past `lastVerified`. It fails at 13 months.
- **Weekly:** external link check.
- **Monthly:** law.moj 沿革 diff for every law in `laws.json`.
- **Quarterly:**
  - the NAER 課綱 page, for new orders or 微調;
  - 樂詞網 dataset dates;
  - the CEEC 考試說明 page update stamps.
- **After each 學測 (late January to spring):**
  - Index the new papers.
  - Re-verify the format facts. The 116 layout is assumed to match 111–115, which is unverifiable until the exam.
  - Harvest documented errors from 評分原則 and 選才電子報 into the misconception register.
- **Each August** (the new 簡章 appears; the 116 初版 was 115/8/4): re-verify every `exam-rule` fact, bump `examCycle` and roll the `reviewBy` dates.
- **Around October:** 最低工資. The council meets in Q3 under 最低工資法§10; the 2026 decision was made 9/24 and announced 10/16. Its `reviewBy` is set to October 31.
- **Annually:**
  - licence pages: PhET, GeoGebra, 均一, 中央氣象署;
  - a full refuter re-run on social chapters that hold time-sensitive content.
- **Event-driven:** 憲法法庭 judgments, 修憲 or 公投 outcomes, and election-age changes.

---

## 7. Learner error reports and corrections

- **Entry points:** a 「回報問題 / Report a problem」 link in every chapter footer, on every item and in every `<Fact>` tooltip.
  - It is pre-filled with **non-personal context only**: lessonKey, locale, section id, item id, build commit and URL.
  - The learner's description and any optional contact are typed on the form, never put in the URL.
- **Channel:** a decision for the owner.
  - (A) GitHub Issue Forms: public, with built-in triage, but it needs an account, which many students won't have.
  - (B) A small Cloudflare Worker form endpoint: no account needed, but it adds a Worker to an otherwise static deploy.
  - (C) A mailto fallback.
  - Proposal: A plus C at launch, then B if volume or accessibility needs it.
- **Triage SLAs:**
  - **sev1:** confirmed by the relevant verifier within 48 h. The integrator fixes it, and only the affected gates re-run (harness for a key, claim verifier for a fact, parity, CI). The owner approves. An `<Erratum>` notice sits at the spot until the fix ships and for 30 days after.
  - **sev2:** within 7 days.
  - **sev3:** batched monthly.
- **Regression rule:** every confirmed sev1 adds a test, lint rule, registry alias, misconception entry or refuter checklist line. Two or more sev1s in one part trigger a re-verification of the whole part.
- **Per-chapter changelog:** `src/data/changelog/<lessonKey>.json`. Each entry holds:
  - date, severity, kind (correction, clarification, law update, exam-rule update, new content);
  - summary in zh and en, and the locales affected;
  - item version bumps;
  - opt-in reporter credit and the commit.
  
  It renders as 「更正紀錄 / Revision history」 at the bottom of the chapter, plus a site-wide `/zh-tw/changes/` and `/en/changes/` page. `changelog.test` makes this mandatory for any change to published content. Item `@version` bumps clear stale progress in the per-browser progress store, ported from the reference `src/lib/progress.ts`.

---

## 8. Open items (unverified or needing a decision)

1. **CEEC past-paper reuse:** unresolved. The site links only; a written permission request to CEEC is needed before embedding anything.
2. **English term pairs:** unverified for physics, biology, history, civics and 國文. Math's category attribution was only spot-checked. A full 樂詞網 ZIP-based pass is needed. Documented EN sources for 歷史 and 公民 (for example official museum or agency English names) are not yet verified.
3. **Constants authority:** the research names none for the science constants register.
4. **Canonical code characters:** choosing `Ⅴ` (U+2164) versus the printed form needs checking against the 領綱 PDFs. Range expansion must be verified per code.
5. **Wikisource transcriptions:** whether they carry rights under Taiwan law is unknown; treated as CC BY-SA for now. The base editions for the 15 選文 still need to be identified.
6. **OpenStax "no LLM training" term:** what it permits for agent workflows needs a legal read.
7. **Dev tool licences:** SymPy, pint, OpenCC and any LaTeX-to-SymPy parser are not covered by the research. They are dev-only, but should be confirmed at install.
8. **Facts still unverified:**
   - the exact effective date of the 民法§1223 amendment;
   - the participation count in 114年憲判字第1號 (present it as disputed);
   - whether there were 108課綱 微調 changes in 2025–2026;
   - whether the 116 paper layout matches 111–115;
   - whether 國文 includes 高三 content (don't claim it does).
9. **Owner decisions:** zh-first publishing; error-report channel; the site's own content licence (it must be compatible with SA assets); the Taiwan map point-of-view file; the quote cap.

### Critical Files for Implementation
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\curriculum.test.ts (port to a global cross-subject graph, adding the code coverage and depends_on rules)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\mdx.test.ts (port as the base for parity, the jump detector and lints)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\src\plugins\remark-dialogue.ts (extend with the new speaker pair, `PAUSE` and `STUDENT[mc=…]`)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\codes\math.json (new: canonical code registry seeded from the research `final_units` and `final_bridging_prereqs`)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\verify\math\ (new: SymPy harness behind every math item, step and key)