# Status and handoff (read this first after a context reset)

Updated 2026-11-16. The plan is `docs/plan.md`; the binding writing rules are `docs/authoring.md` (including the owner requirements added 2026-11-16).

## Done (committed)
- S0 framework: Astro 7 bilingual site, theme "answer sheet + red pen" on ASMC's thin-grid layout, dialogue/Term/Quiz (學測 scoring, 選填 rows ①②③ left-to-right)/Perspective/Graph/NumberLine/Space3D components, registries, SymPy harness, test suites.
- Site name: zh 從 0 開始的學測牲活 (owner), en GSAT from Zero (placeholder). Character names still placeholders (老師/學生).
- Math: 53 chapters, all `reviewed` — 116 sprint (40), cross-unit 跨單元解題 (5), optional 選修小技巧 track (8). Every chapter has perspectives + figures.

## Next: 自然 sprint chapters (outline APPROVED 2026-11-16)
- Outlines: `src/data/course/{physics,chemistry,biology,earth,inquiry}.json` (60 chapters). Readable: `docs/curriculum/*.md`.
- Owner rule: write ONE SUBJECT AT A TIME (rate limits). Suggested order: physics → chemistry → biology → earth → inquiry (inquiry last: its cross-subject and mock chapters need the others).
- Pipeline per chapter (same as math): writer → independent reviewer (medium effort), both following docs/authoring.md incl. perspectives + visuals; SymPy checks for every numeric answer key (harness/checks/m_<subject>_<slug>.py); status draft → reviewed.
  Template script to adapt: `.claude/.../workflows/scripts/math-extensions-write.js` (CONTEXT + writer/reviewer stages; change subject, chapter list, sources naer-science-guidelines + ceec-spec-science, terms folder src/data/terms/<subject>/, glossary pairs from research.terminology of that subject; physics/chemistry/biology/earth have 樂詞網 sets).
- Owner note for earth/s116-universe-stars: recap the EM spectrum in place and LINK to physics/s116-em-waves as the source.
- After each subject: integrate (set chapter `reviews` from terms + <Term> uses, control-char scan, harness --strict, npx vitest run, npm run build, render scan, set the subject status in src/data/subjects.json to "active"), then commit.

## Then
- 社會 (歷史, 地理, 公民) sprint outline → owner approval → chapters (contested-topic rules: docs/design/03-social-chinese-map.md §1.5).
- 國文 beta.
- Owner actions: GitHub remote + Cloudflare deploy; choose characters; optional email to CEEC about embedding past items.
