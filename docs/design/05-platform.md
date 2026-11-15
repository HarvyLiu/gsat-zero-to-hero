<!-- Frozen design output (Platform architecture), 2026-11-15. Superseded where docs/design/06-critique.md or the approved plan says so. -->

# Platform architecture plan: the 學測 Zero-to-Hero site (M0 framework)

Reference files read (nothing modified there): `package.json`, `astro.config.mjs`, `src/data/course.json`, `src/data/curriculum.ts`, `tests/curriculum.test.ts`, `tests/contrast.test.ts`, `tests/mdx.test.ts`, `tests/glossary.test.ts`, `tests/progress.test.ts`, `src/plugins/remark-dialogue.ts`, `src/content.config.ts`, `src/content/chapters/welcome.mdx`, `src/styles/tokens.css`, `src/lib/{progress,saves,paths}.ts`, `src/layouts/{Base,Chapter}Layout.astro`, `src/pages/learn/[slug].astro`, `src/pages/search.astro`, the learning components, `src/iso/*`, `HardwareScene.tsx`, `docs/m2-design.md`, `scripts/{curriculum-doc,shoot}.mjs`. I also queried the research JSON for the tech, pedagogy, math and code-format data.

## 0. Decisions that shape everything

1. **Same stack as the reference**, with nothing new at the core.
   - Astro 7.4.x, @astrojs/mdx 8, @astrojs/react 7, React 19, TypeScript strict, Vitest.
   - Keep `markdown.processor: unified({...})`. remark-dialogue, remark-math and rehype-katex only run under unified().
   - Node ≥ 22.12.
2. **The build is a pure static site.** No server, no accounts, no third-party requests. Fonts, KaTeX CSS and KaTeX fonts are self-hosted; the reference's Google Fonts hotlink goes away.
3. **Every learner-facing string is bilingual data; every id is language-neutral.**
   - Chapter ids look like `math/real-numbers`, item ids like `math/real-numbers/q3`.
   - Progress keys never contain the locale, so progress carries over across languages automatically.
4. **One glossary and one concept registry.** A `newConcepts`/`uses` id is the same id `<Term t>` uses. The no-jump test can therefore check both the outline and the MDX.
5. **The no-jump rule becomes path-aware and cross-subject-aware.**
   - 數A and 數B are two learner paths over one subject.
   - Chemistry may depend on math chapters, but only on chapters that sit on every math path.
6. **Freeze the research input inside the repo.** The verified research file lives in a Temp folder that a cleanup can wipe. M0 step 1 copies it to `research/verified-2026-11-15.json`. All registries are generated from that copy by a deterministic script.
7. **Item text is single-source.** Answer keys and both languages live in one TS file per chapter. MDX only places items. This gives:
   - shared progress across locales;
   - the "顯示中文 / show in Chinese" toggle on EN items (pedagogy 5b);
   - no answer-key drift between the two locales.

## 1. Project layout and data model

### 1.1 Tree (`C:\Users\spp_l\Downloads\Claudechats\projects\學測`)

```
package.json            name "gsat-zero-to-hero" (npm names must be ASCII; placeholder brand)
astro.config.mjs  tsconfig.json  vitest.config.ts  vitest.dist.config.ts  playwright.config.ts
.claude/launch.json     "site" (dev :4321), "site-preview" (preview :4322), as in the reference
.github/workflows/ci.yml  weekly.yml
research/verified-2026-11-15.json            frozen copy of the research output (read-only input)
scripts/
  import-codes.mjs        research → src/data/registry/codes/<subject>.json (normalises, see 1.4)
  curriculum-doc.mjs      → docs/curriculum/<subject>.md, docs/curriculum/coverage.md, cross-subject.md
  fonts.mjs               copies woff2-only slices from @fontsource → public/fonts/, writes src/styles/fonts.css
  katex-assets.mjs        copies katex 0.16.47 css + woff2 only → public/katex/
  check-budgets.mjs       dist file count/size and JS weight vs baseline
  check-external-links.mjs  weekly job
  shoot.mjs               port of the reference (CDP screenshots, 375px + desktop, light/dark)
docs/ architecture.md  authoring.md  ops.md  curriculum/*.md (generated, never hand-edited)
public/ _headers  characters/{teacher,student}.svg  icons/subjects/*.svg  fonts/  katex/
src/
  content.config.ts
  content/lessons/{zh-tw,en}/<subject>/<slug>.mdx     mirrored ASCII paths
  data/
    schema.ts               Zod 4 (astro/zod) schemas + exported types; every loader validates
    subjects.json           subjects, papers, paths, accents, status
    characters.ts           the new teacher/student pair
    course/<subject>.json   one per subject (math.json first) – generalised course.json
    curriculum.ts           typed views (port), build-time only
    terms/<subject>/<chapter>.json   glossary = concept registry (one file per chapter, merged)
    items/<subject>/<chapter>.ts     item banks (TS so LaTeX can use String.raw)
    registry/
      codes/<subject>.json  sources.json  licences.json  facts.json
      misconceptions/<subject>.json
      exam/{sittings.json, papers.json, items/<subject>.json, formula-sheets.json}
  i18n/ ui.ts  urls.ts  locale.ts
  plugins/ remark-dialogue.ts  remark-term-first.ts  remark-locale-props.ts
  lib/ progress.ts saves.ts scoring.ts review.ts mastery.ts graph-layout.ts render-inline.ts paths.ts dates.ts
  iso/ project.ts shapes.ts sort.ts palette.ts        (ported verbatim + tests)
  components/{dialogue,learning,exam,progress,site,scenes,widgets/<subject>/<widget>}/
  layouts/ BaseLayout.astro ChapterLayout.astro
  views/  Home Subject Chapter Glossary Search Review Map Exam Progress About   (shared bodies)
  pages/
    index.astro (bilingual root chooser = x-default)   404.astro (bilingual)
    zh-tw/ index.astro [subject]/index.astro [subject]/[slug].astro [subject]/glossary.astro
           map.astro review.astro exam.astro search.astro progress.astro about.astro
           data/items/[subject].json.ts   (static JSON endpoint for ReviewQueue)
    en/    the same files; each is 3–5 lines delegating to views/ with its locale
  styles/ tokens.css subjects.css fonts.css cjk.css global.css paper.css widgets.css
tests/  tests-dist/  e2e/
```

### 1.2 Core types (`src/data/schema.ts`)

```ts
type Locale = 'zh-tw' | 'en';
type L10n = Record<Locale, string>;                 // both non-empty, enforced by Zod
type SubjectId = 'math'|'physics'|'chemistry'|'biology'|'earth'|'inquiry'|'history'|'geography'|'civics'|'chinese';
type ChapterId = `${SubjectId}/${string}`;          // global, e.g. 'math/real-numbers'
type TermId = `${SubjectId}.${string}`;             // e.g. 'math.real-number'
type CodeKey = `${SubjectId}:${string}`;            // e.g. 'math:N-10-1', 'history:歷Ba-V-1'
type Kind = 'welcome'|'bridge'|'core'|'toolbox'|'exam-toolkit'|'checkpoint'|'extension';
type Mark = '★'|'＃'|'※';
```

**`subjects.json`**

```ts
interface Subject {
  id: SubjectId; title: L10n; short: L10n;
  papers: PaperId[];                       // math → ['mathA','mathB']; physics → ['science']
  accent: CtpHue; icon: string;
  status: 'pilot'|'active'|'beta'|'planned';   // only 'planned' builds no pages
  paths: { id: string; label: L10n }[];        // math: mathA 數A, mathB 數B; others: one default path
  termSource?: SourceId;                       // the 樂詞網 高中以下 list where one exists
}
```

**`course/<subject>.json`** generalises the reference `course.json`. It keeps `$comment`, `version`, `date`, `decisions`, `rationale`, `openQuestions` and `changelog`.

```ts
interface PartDef {
  num: number; id: string; title: L10n; question: L10n; goal?: L10n;
  whyHere: string;                         // internal rationale, docs only (not translated)
  track: 'core' | { id: string; title: L10n; entry: { after: ChapterId[]; note: L10n } };
  chapters: ChapterDef[];
}
interface ChapterDef {
  slug: string;                            // ASCII, identical in both locales
  title: L10n; blurb: L10n; objectives: L10n[];
  kind: Kind;
  paths?: string[];                        // omitted = every path of the subject
  codes: CodeKey[];                        // 學習內容 codes this chapter teaches
  bridgeCodes?: CodeKey[];                 // 國小/國中 codes a bridge re-teaches
  marks?: Mark[];
  strands?: ('inq:discover'|'inq:plan'|'inq:argue-model'|'inq:share')[];  // 探究與實作
  newConcepts: TermId[]; uses: TermId[];
  prereqs: ChapterId[];                    // may cross subjects
  activity: string;                        // internal
  sources: SourceId[];
  examItems?: ExamItemId[];                // OnTheExam links
  justification?: ExamItemId[];            // required when kind === 'exam-toolkit'
  misconceptions?: MisconceptionId[];
}
```

- Readiness is derived, as in the reference's `READY`. A chapter is "ready" when both locale MDX files exist and both have `status: reviewed`. Everything else shows as "soon".
- The requested track tags map like this: bridge, core, exam and extension are `kind` values. 數A and 數B are `paths`. ★ and ＃ codes go in `toolbox` chapters. ※ material (cot/sec/csc) and 分科 加深加廣 go in `extension` parts after the core, mirroring Tracks A–H.

**Glossary and concepts (`terms/<subject>/<chapter>.json`)** are merged with a port of `mergeGlossaries`, which throws on duplicate ids.

```ts
interface TermEntry {
  id: TermId; zh: string; en: string; zhuyin?: string;
  def: L10n;
  source: { id: SourceId; locator?: string; verbatim?: boolean };  // verbatim is required for MOE dictionary definitions (CC BY-ND)
  kind?: 'concept' | 'vocab';            // 'vocab' terms are glossary-only, exempt from no-jump
  aliases?: { zh?: string[]; en?: string[] };
}
```

### 1.3 Registries

- **`registry/codes/<subject>.json`**
  ```ts
  {
    key; code /* official display form */; subject;
    level: '國小3'…'國中9'|'10'|'11A'|'11B'|'12甲'|'12乙'|'必修';
    inGsat: 'yes'|'partial'|'no'|'background'; gsatTrack: 'both'|'A'|'B'|'none';
    marks: Mark[]; title: L10n; keyConcepts: string[]; dependsOn: CodeKey[];
    source: SourceId; status: 'verified'|'corrected'|'added'
  }
  ```
  - It includes the 國小/國中 codes from `final_bridging_prereqs`, as `inGsat: 'background'`.
- **`sources.json`** (the bibliography):
  ```ts
  {
    id; title; url: https; publisher;
    kind: 'curriculum'|'exam-official'|'law'|'term-db'|'dictionary'|'dataset'|'software'|'paper'|'web';
    licence: LicenceId; accessed: 'YYYY-MM-DD'; usedFor; attribution?: L10n
  }
  ```
  - Ids replace the reference's title-as-key.
- **`licences.json`**
  ```ts
  {
    id; name; url;
    mayQuote: 'verbatim-only'|'short'|'yes'|'no';
    mayModify; mayRehost; attributionRequired; nonCommercialOnly
  }
  ```
  - Seed entries, all from the verified facts: `ceec-nonprofit`, `link-only` (past papers), `naer-open`, `ogdl-tw-1` (政府資料開放授權條款), `cc-by-nd-3.0-tw` (MOE), `cc-by-4.0` (PhET before 2026-03-29), `cc-by-nc` (PhET after; version unconfirmed), `geogebra-nc`, `public-domain`, `mit`, `bsd-3`, `isc`, `ofl-1.1`.
- **`facts.json`** holds time-sensitive values:
  ```ts
  {
    id: 'civics.min-wage-monthly'; subject; label: L10n;
    versions: { value: L10n | { n: number; unit: L10n }; validFrom: date; validTo?: date }[];
    asOf: date; reviewBy: date; sources: SourceId[]; note?: L10n
  }
  ```
  - Seeds: 成年 18 (from 2023-01-01), 公投 age 18, 選舉年齡 20, and 最低工資 29,500/196 → 30,900/205 from 2027-01-01.
  - Exam layouts are also facts. Their `reviewBy` is right after the 116 sitting, because the 116 papers aren't published yet.
- **`misconceptions/<subject>.json`**
  ```ts
  { id; codes: CodeKey[]; wrong: L10n; right: L10n; contrast?: L10n; sources: SourceId[] /* ≥1 */; examItems?: ExamItemId[] }
  ```
  - Only documented misconceptions go in, for example the polar-coordinate [r, θ] swap from the 111 數A 評分原則 page.
- **`exam/sittings.json`**
  ```ts
  {
    id: '116'; label: L10n;
    sessions: { paper; start: '2027-01-22T09:20+08:00'; end }[];
    milestones: { id; label: L10n; date }[];
    sources; reviewBy
  }
  ```
  - Milestones: 應考資訊 2027-01-05, score release 2027-02-25.
- **`exam/papers.json`**: each paper's layout, marked "based on the 111–115 papers". 數A is 6/6/5 plus a 15-point 混合; 數B is 7/5/5 plus 15. It also holds minutes, points and the scoring rules.
- **`exam/formula-sheets.json`** describes what the 111–115 papers print:
  - 數A: series sums, sum-of-angle formulas, 正弦/餘弦定理, mean and SD, r and the regression line, √2, √3, √5, √6, π, and log 2/3/5/7.
  - 數B: the same minus the sum-of-angle formulas.
- **`exam/items/<subject>.json`** indexes official items. It stores links only, never question text:
  ```ts
  {
    id: '115-mathA-q18-20'; sitting: 115; paper; numbers: number[];
    type: 'single'|'multi'|'fill'|'mixed'|'nonchoice'|'group';
    codes: CodeKey[]; paperUrl /* ceec.edu.tw */; answerUrl?; rubricUrl?;
    note: L10n; curriculum: '108'|'legacy'; verified: boolean
  }
  ```
  - Papers before 111 predate the 108課綱, so they are tagged `legacy`.

**Item banks (`items/<subject>/<chapter>.ts`)**

```ts
export default defineItems('math/real-numbers', [
  { id: 'q1', type: 'single', options: 5, answer: 2, codes: ['math:N-10-1'], origin: 'original', review: true,
    text: { 'zh-tw': { stem: String.raw`…$\sqrt2$…`, options: […], explain, hint? }, en: { … } } },
  { id: 'q2', type: 'multi', options: 5, answer: [0, 3], … },
  { id: 'q3', type: 'fill', cells: 2, answer: ['−', '3'], … },    // alphabet 0–9 and '−'
  { id: 'q4', type: 'numeric', accept: 'int'|'decimal'|'fraction', answer: 0.25, … },
  { id: 'q5', type: 'mixed', parts: [ /* single|fill|written */ ], rubric: { criteria: [{ id, points, text: L10n }] } },
  { id: 'q6', type: 'predict', answer: 12, … },
  { id: 'q7', type: 'explain', model: L10n },                    // self-explanation, not graded
]);
```

- `origin` must be `'original'`. A `modelledOn?: ExamItemId` field is allowed, but official item text is never stored.
- `locales?: ['zh-tw']` is allowed only for Chinese-only mock items (pedagogy 5b: final mocks in Chinese).

### 1.4 `scripts/import-codes.mjs` (from the frozen research)

Querying the research showed the codes are not uniform:
- Roman numeral `Ⅴ` (U+2164) in physics, biology, history, geography, civics and 國文, but ASCII `V` in earth science and chemistry;
- ranges such as `PKd-Ⅴa-1~8`;
- wildcards such as `EIc-Va-*`;
- spaced prefixes such as `地 Aa-Ⅴ-1`;
- free-text pseudo-codes for 探究與實作 and 田野實察.

The script:
- normalises keys to ASCII (`Ⅴ`→`V`, spaces removed) and keeps the official form in `code`;
- expands ranges;
- maps the 探究 strands to `inq:*` and 田野實察 to `geography:field-1..3`;
- writes per-subject JSON and prints unmapped entries.

It is re-runnable. Manual corrections go in `codes/overrides.json`, never in the generated files. Open item: confirm the official glyph form (U+2164 or ASCII V) against the 領綱 PDF text layer.

### 1.5 Generated docs

`npm run docs:curriculum` writes:
- `docs/curriculum/<subject>.md`: parts, chapters, kind, paths, codes, new ideas in zh and en, prereqs, sources;
- `coverage.md`: a code → chapters matrix, plus the list of uncovered codes;
- `cross-subject.md`.

`tests/docs-fresh.test.ts` regenerates the docs in memory and fails if the committed files differ.

## 2. i18n

### Config

```js
export default defineConfig({
  site: process.env.SITE_URL,                 // required for hreflang/sitemap; the domain is an open item
  base: '/',
  trailingSlash: 'always', build: { format: 'directory' },
  compressHTML: true,                          // Astro 7 default 'jsx' strips spaces between inline elements
  i18n: { locales: ['zh-tw', 'en'], defaultLocale: 'zh-tw',
          routing: { prefixDefaultLocale: true, redirectToDefaultLocale: false } },   // no fallback option
  integrations: [react(), mdx(), sitemap({ i18n: { defaultLocale: 'zh-tw', locales: { 'zh-tw': 'zh-TW', en: 'en' } } })],
  markdown: {
    processor: unified({
      remarkPlugins: [remarkMath, [remarkDialogue, { base }], remarkTermFirst, remarkLocaleProps],
      rehypePlugins: [[rehypeKatex, { strict: 'warn' }]],     // output stays 'htmlAndMathml'
    }),
    shikiConfig: { theme: 'catppuccin-mocha' },
  },
});
```

### Routes (ASCII slugs, the same in both locales)

| Route | Page |
|---|---|
| `/` | Bilingual chooser, the x-default target |
| `/zh-tw/` | Home: subject cards, ExamCountdown, "continue" |
| `/zh-tw/math/` | Subject index with the 數A/數B path picker |
| `/zh-tw/math/real-numbers/` | Chapter |
| `/zh-tw/math/glossary/` | Subject glossary |
| `/zh-tw/map/` | MasteryMap |
| `/zh-tw/review/` | ReviewQueue |
| `/zh-tw/exam/` | Formats, scoring, countdown, links to past papers |
| `/zh-tw/search/` | Search |
| `/zh-tw/progress/` | Export, import, reset |
| `/zh-tw/about/` | Credits, licences, OSTEP format credit, privacy |

`/en/...` mirrors every route. Planned subjects show "coming later" cards with no links, so nothing points at a 404. There is one bilingual `404.html`.

### Root chooser and first visit

`src/pages/index.astro` is a complete page with both links ("中文（台灣）", "English", each in its own script), so it works without JS and for crawlers. An inline script runs first:
- If `?choose` is present, the chooser just shows.
- Otherwise, if `localStorage['gsat:lang']` holds a stored choice, it calls `location.replace` to that locale.
- Otherwise it uses the first entry in `navigator.languages` that matches `en*` or `zh*`. If nothing matches, it uses `zh-tw`.

Only explicit clicks store a choice: the chooser buttons and LangSwitch. Deep links are never redirected. If a stored preference differs from the page's language, a dismissible banner offers the other version.

Open item for the lead: Google advises against automatic language redirects, and this follows the owner's decision anyway. "First supported entry in `navigator.languages`" is my reading of "browser language".

### Switcher, hreflang and lang attributes

- Use our own `i18n/urls.ts` (`localizedPath(locale, subject?, slug?)`, `alternatePath(url, target)`) built on `withBase`. It is unverified whether `getRelativeLocaleUrl` prepends `base`, so avoid it.
- `LangSwitch.astro` links to the same page in the other locale and writes `gsat:lang` on click. With strict parity the target always exists. The disabled "尚未翻譯 / Not translated yet" state is a guard only.
- `BaseLayout` emits `<link rel="alternate">` with fully qualified URLs for `zh-TW`, `en` and `x-default` (→ `/`) on every page, reciprocally.
- `<html lang>` is `zh-TW` or `en`. Inline zh on EN pages goes through `<Zh>` (`<span lang="zh-TW">`).
- Pagefind documents only lowercase `zh-tw`. If the smoke test shows `zh-TW` doesn't trigger segmentation, switch to `lang="zh-tw"` (tags are case-insensitive).

### UI strings and widget labels

- `i18n/ui.ts`: `const ui = { 'zh-tw': {...}, en: {...} } satisfies Parity`, so a missing key is a compile error. `t(locale, key)` throws instead of falling back silently.
- Widget labels go in a co-located `labels.ts` created with `defineLabels({ 'zh-tw', en })`. Both locales ship, which costs a few hundred bytes, and they are parity-tested.
- `remark-locale-props` injects `locale` (taken from the file path `/lessons/<locale>/`) and `chapter` (the global id) into every capitalised JSX element in MDX. Authors never write either one.

### Shared quiz data

- MDX writes `<Quiz items={['q1','q2']} />`, a `Quiz.astro` wrapper.
- At build time the wrapper loads the chapter's item bank and pre-renders each text field with `lib/render-inline.ts` (remark-math + rehype-katex → HTML). Pages therefore ship no KaTeX JS.
- It passes `{ ids, answers, html: <locale>, altHtml?: zh-tw (EN pages only) }` to the `ItemRunner.tsx` island (`client:visible`).
- Ids and answers exist once, text exists per locale, and progress is shared across languages.

## 3. Components

All components are bilingual through `locale`. Names and avatars come from `characters.ts`.

### Dialogue (`plugins/remark-dialogue.ts`, ported and extended)

```ts
// characters.ts
{ id: 'teacher' | 'student', tags: ['T', 'TEACHER', <zh name>], name: L10n, avatar: '/characters/<id>.svg', tone: '--teacher' | '--student' }
```

- Character names are TBD (lead/owner). MDX uses role tags `T:` and `S:`. The plugin also accepts the localised name tags.
- Changes from the reference:
  - the speaker regex accepts CJK tags and the full-width colon `：`;
  - `（…）` and `(...)` are stage directions;
  - inline `$…$` becomes `inlineMath` nodes, in the same shape as remark-math output, so rehype-katex renders them;
  - `[[math.real-number]]` and `[[id|text]]` become `<Term>`;
  - the aria-label is localised (對話 / Conversation).
- **Your turn:** a line `>> turn: q-turn1` emits `<DialogueTurn item=… />`. The lines after it are hidden until the reader answers or skips. Without JS, all lines show (pedagogy 2a).
- The plugin marks the first and last dialogue blocks for the open/close lint.

### Learning components

| Component | Notes |
|---|---|
| `StudentAsks.astro` | Port of HarvyAsks. Prop `q`; the slot holds the teacher's answer. |
| `Term.astro` (+ `remark-term-first`) | The plugin adds `first` to the first `<Term t>` of each id, in document order. **EN:** first use renders `real number（實數）`; later uses render `real number`; the tooltip shows the zh term, optional zhuyin and the EN definition. **zh:** renders `實數`; hover, focus or tap shows "real number" and the zh definition. The English is exposed to Pagefind through `data-en` plus `data-pagefind-index-attrs` (attribute indexing: verify in M0). The button and tooltip markup is ported. |
| `Predict.astro` | Ported. `mode="pre"` turns it into the lesson's pre-questions or diagnostic (pedagogy 3f). |
| `TryIt.astro` | Port. |
| `Quiz.astro` / `ExamItem.astro` → `ItemRunner.tsx` | **單選:** all or nothing. **多選:** n toggles, scored by `scoreMulti`. **選填:** `FillBubbles`, one radio column per cell with 0–9 and "−", keyboard operable, scored all-or-nothing. **混合:** sub-items plus a written answer box; then reveal an original rubric modelled on the CEEC 評分原則 categories. The learner ticks the criteria they met; the score is stored as `selfScored`. Every item shows hint, explanation, tries and "show answer". On EN pages, "顯示中文" swaps in `altHtml`. |
| `Exercise.astro` | Typed int, decimal, fraction or text answers, with hints. `normalizeText` ported. |
| `WorkedExample.astro` + `Step.astro` | Steps state the principle in MDX prose. `fade={n}` turns the last n steps into blanks tied to item ids. Each step can carry `explain="q7"`, an open self-explanation prompt with a model answer (pedagogy 3d). |
| `Misconception.astro` | `id` from the registry. Three parts: the wrong idea, an explicit "this is wrong because", and the right idea with a contrast; then a `check` item. The source is cited inline. |

### Exam components

| Component | Notes |
|---|---|
| `OnTheExam.astro` | `item="115-mathA-q18-20"`. Card reads "115學測 數學A 第18–20題" (EN: "GSAT 115 (Jan 2026) Math A, Q18–20"), with CodeBadges, links to paper, answers and rubric, and our commentary in the slot. Link only. |
| `CodeBadge.astro` | Official code; tooltip with title, inGsat and marks; links to the 領綱 source. The chapter header renders badges from `chapter.codes` automatically. |
| `Fact.astro` | Renders every version with `validFrom`/`validTo`, plus an "as of {asOf} · source" badge. A tiny script picks the version valid today, so 2027-01-01 wage pages are right even without a rebuild. No-JS shows the build-date value plus the upcoming change. |
| `FormulaSheet.astro` | Our typeset version of the printed sheet for 數A/數B, labelled "as printed on 111–115 papers". |
| `ExamCountdown.astro` | Static HTML shows the dates; a script computes days in Asia/Taipei for the learner's chosen papers. After 2027-01-24 it shows "next sitting not yet announced" until a 117 entry exists. |

### Progress components

| Component | Notes |
|---|---|
| `YouNeed.astro` | Auto-generated at the top of each chapter from course data: direct prereqs with links, and "ideas you'll use" chips (the `uses` terms with their source chapters). A script adds mastery dots and a "review first" link for prereqs below Familiar. |
| `ReviewQueue.tsx` | Island on `/review/` and at the end of each chapter. Fetches `/<locale>/data/items/<subject>.json` (static endpoint, pre-rendered HTML) on demand. |
| `MasteryMap.astro` | Build-time SVG from `lib/graph-layout.ts`: longest-path layering, subject swimlanes, highlighted cross-subject edges. Our own pure layout code, with no unverified dependency. A small script fills node glyphs by level. |
| `CompleteChapter.tsx` | Port. |
| `ProgressPanel.tsx` | Export, import and reset. |

### Site components and theming

- `CourseNav.astro` (port, path-aware filter), `ChapterNav.astro`, `SourcesList.astro` (auto "Go deeper" with licence attribution), `SubjectCard.astro`, `ThemeToggle`.
- **ChapterNav at a branch point:** static pages can't know the learner's path. Where next(A) ≠ next(B), it renders both, labelled 數A and 數B, and a script hides the one off the learner's path. The default shows both.
- **Per-subject theming:** `<body data-subject="math">` sets `--subj`, `--subj-text`, `--subj-soft` and the icon. Colour is never the only cue: every subject also has an icon and a text label.

## 4. Widgets and visuals

### Libraries (versions and licences verified)

| Library | Use |
|---|---|
| **Mafs** (MIT, version not shown) | Primary 2D math library |
| **JSXGraph** 1.14.3 (choose the MIT option) | Only constructions and 3D views (View3D), evaluated in M1 |
| **Observable Plot** 0.6.19 / **D3** 7.9.2 (ISC) | Charts and statistics |
| **3Dmol.js** 2.5.5 (BSD) | Chemistry and biology later; local SDF/PDB files, citation on the credits page |
| **MapLibre** 6.18.0 (BSD-3) | Geography later; `localIdeographFontFamily` set to the TC stack |
| **Natural Earth** (public domain) + **內政部** datasets 7441/7442 (政府資料開放授權) | Map data, converted to TopoJSON at build time. de facto vs Taiwan-POV layer is an editorial open item |
| **KaTeX 0.16.47** pinned top-level, plus remark-math 6.0.0 and rehype-katex 7.0.1 | Math at build time; `import 'katex/contrib/mhchem'` for chemistry (needs a test build) |

- Widgets with live formulas (e.g. a grapher label) lazy-import the same katex.
- No Desmos. GeoGebra and PhET only as click-to-load iframes with attribution, never as core content.

### Isometric system

- Port `src/iso/*` verbatim with `tests/iso.test.ts`.
- `HardwareScene` becomes `scenes/IsoScene.tsx`: graph paper, teal hotspot buttons, localised hotspot text via props, and a `student?` aside instead of `harvy?`.
- First math scenes: isometric 3D axes box (G-11A-2/G-11B-4), a solids table for the S-5-6/S-9-12 bridges, and a cuboid with diagonals for 空間概念.

### Motion and accessibility

- Port `useReducedMotion`. The global `prefers-reduced-motion` CSS turns animation into step buttons.
- 44px targets, full keyboard use, 375px layouts.
- KaTeX hidden MathML is kept.
- Each graph widget has a text description and a values table. Maps get a static SVG plus a data table.

### Performance budget

- Measure a baseline in M0. `check-budgets.mjs` then fails CI on more than 10% regression in JS bytes per page type, rather than using invented absolute numbers.
- Hard rules:
  - zero JS by default; islands use `client:visible`;
  - MapLibre, 3Dmol and JSXGraph only via dynamic import behind a "load" button;
  - no third-party requests;
  - preload only the Latin body woff2.

### First math widgets

M0 builds the item family plus the first two widgets; M1 builds the rest in chapter order.
- **M0:** `ItemRunner` (single, multi, fill, mixed), `FormulaSheet`, `NumberLine` (N-10-1/2, bridges N-7-3..5, |x−a| as distance), `FunctionGrapher` (Mafs sliders, vertex form, symmetry: G-10-1, F-10-1/2).
- **M1:**
  - `SciNotationLab` (N-10-1; reused by chemistry);
  - `LogLab` using the formula-sheet log values (N-10-3/4, A-11A-4, F-11A-4);
  - `SignChart` (F-10-3);
  - `LineCircleLab` (G-10-2..4);
  - `UnitCircle`/`PolarPlot` (G-10-5..7; targets the documented [r, θ] swap);
  - `SequenceStepper` (N-10-6);
  - `CountingTree` and `ProbabilitySim` with a seeded RNG (D-10-3/4);
  - `ScatterRegression` (D-10-2);
  - `VectorPlayground` (11A/11B);
  - `Space3D` (11A);
  - `MatrixStepper` (A-11A-1..3);
  - `BayesTree` (D-11A-2/3).

Each widget has a pure `model.ts` and `tests/widgets/<subject>/<widget>.test.ts`.

## 5. Progress, mastery and spaced review (`src/lib`)

### Storage

`progress.ts` keeps the reference's KV abstraction, its blocked-storage fallback, the `subscribe`/`reload` pattern and cross-tab `storage` events. Keys: `gsat:progress` (big) and `gsat:prefs` (tiny, read by the inline head script for theme and language).

```ts
interface ProgressV1 {
  v: 1;
  chapters: Record<ChapterId, { done: true; at: string }>;
  items: Record<ItemId, { firstAt: string; lastAt: string; best: number /*0..1*/; attempts: { at: string; score: number; self?: true }[] /* last 5 */ }>;
  mastery: Record<ChapterId, { level: 0|1|2|3|4; at: string }>;
  review: Record<ItemId, { due: string /*YYYY-MM-DD*/; interval: number; reps: number; lapses: number }>;
}
interface Prefs { v: 1; lang?: Locale; theme?: 'light'|'dark'; mathPath?: 'A'|'B'|'both'; showZhInEn?: boolean; papers?: PaperId[] }
```

- `parseProgress` runs a `MIGRATIONS` chain (`v → v+1`). Unknown or corrupt data gives empty progress.
- Attempt history is trimmed to stay well under the localStorage quota.

### Mastery (`mastery.ts`)

- Levels: 未開始 Not started → 嘗試 Attempted → 熟悉 Familiar → 精熟 Proficient → 掌握 Mastered (pedagogy 3h).
- Rules are pure functions over item results:
  - **Familiar:** chapter checks passed.
  - **Proficient:** criterion score on a mixed set.
  - **Mastered:** Proficient plus two successful spaced reviews on different days.
- Thresholds are tunable constants, documented as design choices rather than evidence-backed numbers.
- Progress is reported as "nodes at Proficient or above".

### Review (`review.ts`)

- `schedule(card, result, today, examDate)` uses expanding intervals capped by a fraction of the days left to the exam (pedagogy 6b).
- The cap is a labelled, tunable interpolation, not a tested value.
- Sessions interleave due cards across subjects. Self-scored 混合 items count with lower weight.
- The clock is injected, so the logic is fully testable.

### Scoring (`scoring.ts`)

- `scoreSingle`: all or nothing.
- `scoreMulti(selected, key, n)`: options are judged independently; k = number of options judged wrongly; score = max(0, (n−2k)/n); a blank answer scores 0.
- `scoreFill(cells, key)`: every cell must be right.

### Export and import

- `/progress/` downloads `gsat-progress-YYYY-MM-DD.json` containing `{ app, exportedAt, progress, prefs }`.
- Import validates and migrates, shows a preview ("adds 12 chapters, 40 items"), then merges: union, max `best`, earliest `firstAt`, latest `lastAt`, the sooner `due`.
- Reset needs confirmation. No accounts and no network calls.

## 6. Tests (Vitest)

Each suite is ported from the reference or new.

| File | Asserts |
|---|---|
| `tests/curriculum/no-jump.test.ts` (port) | Chapter ids are unique globally. Prereqs exist. Within-subject prereqs come earlier. The global prereq graph is acyclic. Every chapter except a subject's `welcome` has ≥1 prereq. **Each concept is introduced exactly once**, and normalised zh/en term text is not duplicated across subjects unless an alias is declared. `uses` ⊆ newConcepts of the chapter itself or its ancestors (ancestors across subjects). ≤5 new concepts per chapter, ≤2 for checkpoints, welcome exempt. **Path rules:** every prereq is on every path the chapter is on. Cross-subject prereqs only target core or bridge chapters on all paths of the target subject. Extension chapters are never prereqs of core chapters. |
| `tests/curriculum/structure.test.ts` (port) | Parts numbered 0..n per subject. Core parts come before tracks, and tracks declare an entry. Every part after Part 0 ends with a `checkpoint`. Path-aware neighbours never cross tracks, and on 數B they skip 11A chapters. Exam-toolkit chapters have a `justification` item. ※ codes appear only in extension. |
| `tests/curriculum/coverage.test.ts` | For subjects that aren't `planned`: every `inGsat: 'yes'` code is taught on the right path(s) (both / mathA / mathB); every `partial` (★/＃) code is in a toolbox or core chapter; every `no` code is only in extension. **Official `dependsOn` is respected:** the chapter teaching X has the chapter teaching Y as itself or an ancestor. Every background code a taught code depends on is covered by a bridge or listed in `assumed.json` with a reason. All referenced codes exist. Prints "math: 58/58 codes covered". |
| `tests/curriculum/sources.test.ts` (port) | ≥1 source per chapter. Every source id exists, is https, has a known licence and an `accessed` date, and is cited somewhere. |
| `tests/registry/codes.test.ts` | Normalisation of Ⅴ/V and spaces, range expansion, unique keys, overrides applied. |
| `tests/registry/glossary.test.ts` (port) | No duplicate ids across files. Every entry has zh, en, def.zh-tw, def.en and an existing `source.id`. In subjects with a 樂詞網 高中以下 list (math, physics, chemistry, biology, earth, geography), a non-NAER source needs a `locator` note. MOE-dictionary definitions have `verbatim: true`. Every `<Term t>` and `[[id]]` in MDX exists. |
| `tests/registry/terms-before-taught.test.ts` | Every Term in a chapter's MDX (both locales) is in its newConcepts or uses or its ancestors', unless `kind: 'vocab'`. |
| `tests/registry/licences.test.ts` | CEEC items are `link-only` with no stored text. Embed sources carry their required attribution. PhET entries record their publish date (CC BY 4.0 before 2026-03-29, otherwise CC BY-NC). A credits page entry exists for every `attributionRequired` source. |
| `tests/registry/facts.test.ts` | **Fails if today > `reviewBy`.** Version intervals don't overlap. Facts have sources. Every `<Fact id>` exists. |
| `tests/registry/exams.test.ts` | Sessions are in +08:00 and ordered. A future sitting exists, or the 116 `reviewBy` hasn't passed. Exam items are https on `ceec.edu.tw`, their codes exist, and pre-111 items are marked legacy. |
| `tests/registry/misconceptions.test.ts` | ≥1 source each; ids used in MDX exist. |
| `tests/i18n/locale-parity.test.ts` | The same chapter set in `zh-tw/` and `en/`. Per chapter: the same `minutes`, the same ordered list of interactive ids (Quiz, ExamItem, Predict, Exercise, DialogueTurn, widget progress ids), the same Term set, the same OnTheExam/Fact/Misconception ids, and the same dialogue-block count. Every L10n field in course, terms, items and registries is non-empty in both locales (`locales: ['zh-tw']` items excepted). Route files are the same in `pages/zh-tw` and `pages/en`. |
| `tests/i18n/ui-strings.test.ts` | Key parity for `ui.ts` and every `labels.ts`; no empty strings. |
| `tests/i18n/urls.test.ts` | `localizedPath` and `alternatePath` with base `/` and a fake `/repo/`; trailing slashes. |
| `tests/mdx/mdx.test.ts` (port) | Compiles with the real plugin chain (remark-math, dialogue, term-first, locale-props) and rehype-katex with `throwOnError`, which catches bad TeX and the MDX-brace issue. Frontmatter schema: `minutes` ≤ 30, `status` is `draft` or `reviewed`. Imports resolve. **The first block after imports is a dialogue and so is the last.** Item ids exist in the chapter's bank. |
| `tests/mdx/zh-typography.test.ts` | In zh prose (outside code, math and JSX): flags ASCII `,` `;` `:` `?` `!` next to Han characters, `"…"` instead of 「」, and hand-typed spaces between Han and Latin or digits. On EN pages, flags CJK outside `<Term>`/`<Zh>`. |
| `tests/plugins/remark-dialogue.test.ts` (port) | CJK tags, full-width colon, （） stage directions, `$x^2$` reaching rehype-katex, `[[term]]`, the turn gating markup, localised aria-label, open/close markers. |
| `tests/plugins/remark-term-first.test.ts`, `remark-locale-props.test.ts`, `tests/lib/render-inline.test.ts` | Plugin and renderer behaviour. `render-inline` includes a `\ce{H2O}` mhchem case. |
| `tests/lib/scoring.test.ts` | n=5: 0 wrong → 1, 1 → 0.6, 2 → 0.2, ≥3 → 0, blank → 0. Fill is all-or-nothing including "−". |
| `tests/lib/progress.test.ts` (port) | Plus migrations, export/import merge, blocked storage, and locale-free keys. |
| `tests/lib/review.test.ts`, `mastery.test.ts`, `graph-layout.test.ts`, `dates.test.ts` | Countdown in Asia/Taipei; ROC 116 → 2027. |
| `tests/contrast.test.ts` (port) | Reads `tokens.css` and `subjects.css`: the reference pairs, plus each subject's `--subj-text` on paper, card and `--subj-soft` (≥4.5), `--subj` on paper (≥3), and the teacher/student name colours on their bubbles, in Latte and Mocha. |
| `tests/iso.test.ts` (port) | |
| `tests/docs-fresh.test.ts` | Generated docs are current. |
| `tests-dist/budget.test.ts` | Runs after build, with its own config. **dist file count < 19,000** (warn at 15,000; Cloudflare's limit is 20,000). No file > 25 MiB. Reports the top directories (fonts, pagefind, _astro). |
| `tests-dist/html.test.ts` | Every page's `lang` matches its folder (root is bilingual). hreflang is reciprocal with x-default. Internal links resolve and end with `/`. No external `<script>`/`<link>` hosts. `data-pagefind-body` on lessons and the glossary. No `draft` pages in production. Sitemap lists both locales. |
| `tests-dist/pagefind.test.ts` | The zh-tw and en indexes both exist, with page counts matching built lessons per locale. Parsing `pagefind/pagefind-entry.json`: file name and shape to verify in M0. |
| `e2e/*.spec.ts` (Playwright) | `navigator.languages` set to en, zh-TW and ja → /en/, /zh-tw/, /zh-tw/. A stored choice wins. `?choose` shows the chooser. The switcher keeps the page. An item solved on zh shows solved on en. Search finds 實數 on zh and "real number" on en. Theme and reduced motion. 375px keyboard pass through a quiz. |

## 7. Typography and theming

### Fonts

- All self-hosted.
  - **Body Han:** Noto Sans TC, SIL OFL 1.1; TC is the Taiwan glyph set with centred punctuation.
  - **Latin:** Barlow (body), Barlow Condensed (display), JetBrains Mono (code).
  - The Barlow and JetBrains Mono licences aren't in the verified research; confirm them in each package's LICENSE during M0.
- The reference's stacks are kept, with `'Noto Sans TC'` inserted before system-ui. Latin glyphs come from Barlow; Han and full-width punctuation fall through to Noto TC. SC fonts never come before TC.
- **Slicing and file count:**
  - `scripts/fonts.mjs` copies only the woff2 unicode-range slices from @fontsource and writes our own `fonts.css`.
  - The Fontsource CSS references a .woff fallback next to every .woff2, and there are 116+ slices per weight. Importing it through Vite could double the file count.
  - Prefer the variable 100–900 build if it ships woff2-only slices: one set covers 400 and 700. Otherwise use static 400 and 700. Measure in M0.
  - The Astro Fonts API's handling of CJK slices is undocumented, so don't use it.
- **Other faces:**
  - Noto Serif TC (classical quotes in 國文 later) is optional.
  - Iansui for the dialogue voice is an open decision: it is still beta and follows MOE forms loosely.
  - Never use LXGW WenKai TC for content, because it uses 傳承字形.

### CJK CSS (`cjk.css`)

- `:lang(zh-TW)` rules:
  - body `line-height` around 1.8 (a starting value: clreq gives none, so tune it by visual testing with mixed zh/en/math);
  - `text-transform: none` and much smaller `letter-spacing` on `.label` and headings;
  - zh headings at weight 700 and about 0.92× size, so they sit with the condensed uppercase Latin.
- `text-autospace: normal` as progressive enhancement (it inserts 1/8 ic, per the correction). `text-spacing-trim` only as an enhancement.
- Extra line gap (≥ half the font size) wherever `<ruby>` appears. Use `ruby-position: over` only; inter-character placement isn't supported.
- KaTeX: `.katex .cjk_fallback { font-family: 'Noto Sans TC' }`. Authors wrap Chinese in `\text{}`. KaTeX warnings are counted in the build log.

### Authoring conventions (`docs/authoring.md`, linted)

- Full-width punctuation ，。、；：「」『』？！ in zh prose; no hand-typed Han–Latin spaces.
- EN: first use of a term gives "English（中文）", via Term.
- The voice rules are ported from m2-design §5: plain words, warm and precise, no emoji. Second person 你/you (pedagogy 2b).

### Tokens

- Port `tokens.css` (Latte light, Mocha dark, graph paper, iso grid, heading tile, aha LED).
- Add `subjects.css` with a proposed mapping:

  | Subject | Latte / Mocha base hue |
  |---|---|
  | math | mauve |
  | physics | sapphire |
  | chemistry | peach |
  | biology | green |
  | earth | yellow |
  | inquiry | flamingo |
  | history | maroon |
  | geography | sky |
  | civics | lavender |
  | chinese | red |

  - Teal stays reserved for hotspots and blue for links.
  - Each subject has `--subj` (UI, ≥3:1), `--subj-text` (darkened from the hue until ≥4.5:1, with the derivation in a comment, as the reference does) and `--subj-soft`.
  - The contrast test decides the exact hex values; none are pre-claimed.
- Character tones `--teacher`/`--student` use hues not already taken by subjects. The lead picks them along with the names.

## 8. Hosting and ops

- **Host:** Cloudflare Pages, direct upload from CI (`wrangler pages deploy dist`). Main → production; PRs → preview URLs.
  - `base: '/'`. Everything goes through `withBase`/`localizedPath`, so a GitHub Pages fallback is a one-line change (`base: '/repo/'`), and the html test checks it.
  - `site` comes from `SITE_URL`. The domain or `*.pages.dev` project name is an owner decision.
  - The owner creates the Cloudflare project and API token and stores the token as a GitHub secret. The implementer never handles tokens.
- **`public/_headers`:** `/_astro/*`, `/fonts/*` and `/katex/*` get `immutable, max-age=31536000`; `/pagefind/*` gets a short max-age. No `_redirects` are needed.
- **File budget:** these are estimates to measure in M0.
  - HTML is about 2 per chapter.
  - Pagefind writes about 1 fragment per indexed page, plus index chunks per language.
  - CJK fonts are 116+ per weight (×2 if woff fallbacks leak in).
  - KaTeX is about 20 woff2 after trimming to woff2.
  - Plus JS chunks and SVGs.
  - A full multi-subject site should land in the low thousands. The 19,000 hard test is the guard.
- **CI (`ci.yml`):** Node 22 (≥22.12), then:
  1. `npm ci`
  2. `npm run typecheck` (`astro check` + `tsc`)
  3. `npm test`
  4. `npm run build` (`astro build && pagefind --site dist`)
  5. `npm run test:dist`
  6. `npm run e2e` against `astro preview`
  7. `check-budgets`
  8. deploy (main) or a preview (PR)
- **Weekly scheduled job (`weekly.yml`):** facts freshness, external link check (CEEC, NAER, laws, etc.; it opens a failure but never blocks a PR), and a dependency audit.
- **Pagefind:**
  - `data-pagefind-body` on lesson `<article>`, the glossary and subject indexes. Once one page uses it, all unmarked pages are excluded.
  - `data-pagefind-ignore` on nav, speaker names and item chrome.
  - `data-pagefind-filter="subject:…"`.
  - Use the 1.5+ **Component UI**, which replaces the reference's `PagefindUI`. Read its API from the Pagefind docs at implementation; it isn't in the research.
- **Owner preview:**
  - `npm install` → `npm run dev` (http://localhost:4321/; search doesn't work here).
  - `npm run build && npm run preview` (:4322, search works).
  - The two `.claude/launch.json` entries make both one click from the Browser pane.
  - `npm run shoot -- --dark math/real-numbers` for screenshots.
  - The README gives PowerShell-friendly commands.
- **Git:** the folder is not a repo yet. M0 runs `git init`; the owner chooses the GitHub remote.

## 9. M0: what exists when the framework is done

### Deliverables

1. **Scaffold.**
   - Astro 7.4 project in `學測`, pinned versions, the `astro.config.mjs` above.
   - `research/verified-2026-11-15.json` frozen.
   - README, `docs/architecture.md`, `docs/authoring.md`, `docs/ops.md`, `.claude/launch.json`, git.
2. **Data layer:**
   - `schema.ts`, `subjects.json` (math `pilot`, the rest `planned`), `characters.ts` (placeholder names until chosen);
   - registries seeded from the research by `import-codes.mjs` (all subjects' codes, so coverage can switch on per subject);
   - `sources.json`, `licences.json`;
   - `facts.json` with the civics and exam facts;
   - `exam/{sittings,papers,formula-sheets}.json` for 116;
   - `exam/items/math.json` with the 111–115 math papers (link-only);
   - `course/math.json`: the full math outline from the curriculum planner, all chapters "soon". If the outline isn't ready yet, use a test fixture and mark that criterion as pending.
3. **i18n:** `ui.ts`, `urls.ts`, root chooser, LangSwitch, hreflang, sitemap, per-locale route folders delegating to `views/`.
4. **Layouts and styles:**
   - BaseLayout and ChapterLayout (header with CodeBadges, goals and aha, YouNeed, body, CompleteChapter, SourcesList, path-aware ChapterNav);
   - tokens, subjects, fonts, cjk, global;
   - theme toggle; self-hosted fonts and KaTeX.
5. **Components:** everything in §3, plus `IsoScene`, `NumberLine` and `FunctionGrapher`.
6. **Libraries:** progress v1 with migrations, saves (port), scoring, review, mastery, graph-layout, render-inline, dates.
7. **Pages:** home, math subject index, glossary, map, review, exam, search, progress, about/credits, and a style-guide page built only in dev or with `STYLE_GUIDE=1` that shows every component in both locales.
8. **Two real chapters in both locales,** written to the authoring rules and sourced: `math/welcome` (how the course works, path choice, exam format and scoring, countdown) and one bridge chapter (for example negative numbers and the number line, N-7-3..5).
9. **Tests, CI and deploy:**
   - every §6 suite;
   - `ci.yml` and `weekly.yml`;
   - a first deployment to a Cloudflare preview URL (needs the owner's account).

### Acceptance criteria

All of these must hold.
- On Windows in the `學測` folder and on Linux CI: `npm test`, `npm run typecheck`, `npm run build` and `npm run test:dist` all pass, and `npm run e2e` passes on CI.
- Coverage for math reports every `inGsat: 'yes'` math code mapped on its correct path(s), and every official `dependsOn` respected by chapter ancestry. This is at outline level; chapters may still be "soon".
- dist file count and largest file are reported and under the guard. A JS-weight baseline is recorded in `docs/ops.md`.
- Manual check by the owner on the preview URL:
  - the first visit follows browser language (en → /en/, zh → /zh-tw/, other → /zh-tw/), and an explicit choice is remembered;
  - the switcher keeps the page;
  - an item answered in zh shows as answered in en;
  - a 多選 item scores by (n−2k)/n and a 選填 item uses digit bubbles;
  - EN pages show "real number（實數）" on first use, and zh pages show English on hover or tap;
  - dialogues open and close both sample chapters, and a "your turn" pause gates the next lines;
  - light and dark themes, 375px width and keyboard-only use all work;
  - search finds 實數 on zh and "real number" on en;
  - Fact shows its as-of date and source, and the countdown shows 116 dates in Taipei time.
- No request leaves the site's origin; the html test verifies this.
- The credits page lists every attributed source and licence, and the OSTEP credit appears as a format idea only.

## 10. Open items and risks (none of these is assumed)

1. **mhchem with rehype-katex under Astro 7 unified** is untested. The fallback is a roughly 30-line rehype plugin calling katex directly.
2. **remark-math `$…{}$` inside MDX 8** is unverified. The mdx test catches it.
3. **Library behaviour to check in M0 builds:**
   - whether `getRelativeLocaleUrl` adds `base` (avoided with our own helper);
   - whether Pagefind segments `lang="zh-TW"` (smoke test; switch to `zh-tw` if not);
   - Pagefind `data-pagefind-index-attrs` for the hidden English on zh Terms;
   - the shape of `pagefind-entry.json`;
   - the Component UI API.
4. **Fonts:**
   - Fontsource variable vs static slice counts and woff fallbacks (measure);
   - Barlow and JetBrains Mono licences (confirm OFL);
   - Iansui for the dialogue voice;
   - whether Noto TC conforms to MOE standard forms (unverified, matters for 國文).
5. **Official glyph form of codes** (U+2164 `Ⅴ` vs ASCII `V`) in the 領綱 PDFs. Only the import script is affected.
6. **The full 選填 bubble alphabet** beyond digits and "−" on the 116 answer sheet.
7. **Exam facts:** the 116 paper layout is unpublished (111–115 basis) and the 117 sitting dates are unknown, so the countdown needs its fallback state.
8. **Owner decisions:**
   - brand and site name, domain or `site` URL;
   - Cloudflare and GitHub accounts;
   - character names and avatars;
   - Natural Earth de facto vs Taiwan-POV layer (geography and history later);
   - whether bridges come in a block before 10年級 or just in time (the data model supports both).
9. **Non-ASCII project path:** Vite, Pagefind and Playwright with the `學測` path on Windows is unverified. Build in this folder on day 1. If it fails, use an ASCII junction, which the owner creates.
10. **Timeline:** the first exam day is 68 days from 2026-11-15, so the math pilot can't be completed before 116. Prioritising exam-format and practice chapters early is a product call for the lead; nothing in the framework depends on it.
11. **Answer keys are visible:** island props put answer keys in page HTML. That is acceptable for a self-study site, and it is documented.

### Critical Files for Implementation
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\schema.ts
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\course\math.json
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\tests\curriculum\no-jump.test.ts
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\plugins\remark-dialogue.ts
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\astro.config.mjs