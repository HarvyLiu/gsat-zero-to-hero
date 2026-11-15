# Writing a chapter

Each chapter's spec lives in `src/data/course/<subject>.json`, and that spec is binding. The spec lists:
- what the chapter teaches (`codes`, `newConcepts`);
- what it may assume (`uses`, `prereqs`);
- which sources back it.

A chapter is written in zh-TW first and verified. The English version is then **adapted** from the verified Chinese. The adaptation may restructure sentences, but it never adds, drops or changes a claim, item, fact, example or widget.

## File layout

- `src/content/lessons/zh-tw/<subject>/<slug>.mdx` and `src/content/lessons/en/<subject>/<slug>.mdx`, with the same slug.
- Frontmatter:
  - `title`, `description`
  - `goals` (1–5)
  - `aha` (the one big idea)
  - `minutes`
  - `status` (`draft` → `reviewed` → `published`)
  - `lastVerified` and `verifiedAgainst` (source ids), set at publish time
- Practice items: `src/data/items/<subject>/<slug>.yaml`. Items are always original. An item that copies a real exam question is a licence breach.

## Shape of a chapter

1. **Opening dialogue.** A ```` ```dialogue ```` block (`T:` teacher, `S:` student). It sets up one concrete question and links back to the previous chapter.
2. **Pre-question** (`<Predict>`), low stakes. Wrong answers are expected.
3. **Body.** Short sections. Each section has:
   - one idea;
   - one diagram or widget;
   - a worked example;
   - a `<StudentAsks>` callout where a beginner would get stuck.
4. **Misconception moment** (`<Misconception id>`). Use only misconceptions documented in the registry with status `verified`.
5. **On the exam** (`<OnTheExam item>`). Links to the official CEEC item; never copy its text.
6. **Check yourself** (`<Quiz items={[…]}>`), using 學測 scoring.
7. **Closing dialogue.** The student recaps and the teacher points to the next chapter.

Inside dialogues:
- `>> turn: <itemId>` pauses for the reader to answer before the conversation goes on.
- `S[mc=<id>]:` marks a line where the student voices a documented misconception.
- `[[term-id|text]]` is a glossary term.

## Language rules

- **zh-TW:**
  - Full-width punctuation `，。、；：「」『』？！`. Do not type spaces between Han characters and Latin letters or digits; CSS adds them.
  - Use Taiwan usage and 課綱/樂詞網 terms. Never use Mainland-only terms (e.g. 正弦定理 as on the CEEC formula sheet).
  - Address the reader as 你.
- **en:**
  - Plain, warm, precise. Address the reader as "you".
  - The first use of every key term goes through `<Term>`, which renders "English（中文）".
  - Chinese elsewhere goes inside `<Zh>`.
- **No emoji.** Comments in code explain *why*.

## Accuracy rules

- Every factual sentence must be supported by a source in the chapter's source pack.
- Time-sensitive values (laws, wages, exam dates and layouts) are rendered with `<Fact id>`, never typed as plain text.
- Numbers in examples and answer keys are recomputed by the Python harness (`verify:` on each item).
- Contested topics in history and civics follow `docs/design/03-social-chinese-map.md` §1.5. Every claim is one of three types: a documented fact, an attributed perspective, or the course's own question. At least two cited perspectives are shown, and the teacher character stays neutral.

## Owner requirements added 2026-11-16 (binding for every chapter, especially Math)

1. **More than one angle.** Every major method gets at least one alternative perspective that genuinely differs — geometric, algebraic, graphical, counting/probabilistic, physical intuition, or a different representation. Example: a system of three linear equations is solved by elimination AND seen geometrically as planes meeting (or a plane meeting a line). Alternatives are worked out, not just mentioned.
2. **Future knowledge goes behind a click.** If a perspective uses something not yet taught at that point (a later chapter, or 分科/beyond-學測 material), put it in a collapsible `<Perspective later>` block, labelled with what it assumes and linking to where that is taught. The main path never depends on it.
3. **Always visualize.** Every chapter has at least one graph, diagram or interactive figure for its core idea, and graphing is taught as a solving tool, not decoration. Prefer interactive widgets (sliders, draggable points); every visual has a text description for accessibility.
4. **Cross-unit problem solving.** After all units, a dedicated lesson collects problems that can be solved several different ways across units, showing each way side by side and when to prefer which.
5. **分科 as advanced tools for 學測.** At the end, an optional part teaches selected 分科 (加深加廣) ideas ONLY where they help with 學測 problems, taught from zero (never assume the learner knows AST material), clearly labelled 「不考學測／進階工具」.
