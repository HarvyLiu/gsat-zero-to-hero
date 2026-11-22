# Teaching style

This is binding for every new or rewritten chapter, together with `docs/authoring.md` (chapter shape, language and accuracy rules). It started from ASMClearningPlayground's `docs/teaching-style.md` and is adapted to this course's components. The owner chose it on 2026-11-22. The numbers were measured on the chapters at commit `ce84ee5`.

## How a chapter teaches
- **Concrete before abstract.** Start from something the reader can see, touch or measure (a beaker, a label, a graph), then name the idea.
- **Predict, then reveal.** Before a result that might surprise, the reader commits to a guess: a `<Predict>` for a number, or a `>> turn: <itemId>` pause in a dialogue for a choice. Wrong guesses cost nothing and are expected.
- **One idea per section.** Each section introduces one idea and gives the reader something to do with it before moving on.
- **Everyday analogies** from 老師, who also says where the analogy breaks.
- **`<StudentAsks>` asks what a real beginner would ask,** including the instructive wrong guesses. The answer comes right after, in the text.
- **Every figure has a task.** A `<TryIt>` or a sentence next to the figure says what to drag, read off or compare, and what to notice. Never "play with this". The figure's `desc` still describes it for screen readers.
- **Interaction is spread through the text,** not saved for the end. A long stretch of prose with nothing to do means the section should be split or given a figure, a `<TryIt>` or a prediction.
- **More than one angle** (owner requirement, authoring.md): a `<Perspective>` that is worked out, not just mentioned. Anything that uses later material goes in `<Perspective later>`.
- **Voice:** plain words, short sentences, warm and precise, no emoji.

## Pacing
"Moments" are `<Predict>`, dialogue `>> turn` pauses, `<StudentAsks>`, `<TryIt>`, `<Perspective>` blocks and figures (`<Graph>`, `<NumberLine>`, `<Space3D>`). Counts are taken from the English file, up to "Check yourself". Words leave out math and markup.

**Measured medians** (before this doc existed):

| Set | Chapters | Words | Moments | Words per moment | `<Predict>` | Turns | StudentAsks | Perspectives | Figures | TryIt |
|---|---|---|---|---|---|---|---|---|---|---|
| Math 116 sprint | 40 | ~1,830 | 18 | ~100 | 0 | 1 | 2 | 7 | 8 | 1 |
| Physics 116 sprint | 15 | ~2,570 | 17 | ~146 | 0 | 1 | 2 | 7 | 7 | 1 |

**Targets for new 自然 and 社會 sprint chapters** (from chemistry on, owner 2026-11-22):

| Words | Moments | Words per moment | Predictions | StudentAsks | Perspectives | Figures | Check yourself |
|---|---|---|---|---|---|---|---|
| 2,000–2,700 | 18–24 | ≤130 | ≥2 (the opening turn plus at least one in the body; use `<Predict>` wherever the chapter has a number to guess) | 3–4 | ≥1 per core idea | 5–9, each with a task | one `<Quiz>`, 6–8 items |

Exam-skills chapters keep the same targets, but worked items may stand in for some figures.

Physics and math are not retrofitted (owner choice, 2026-11-22).

## Model chapters
Each writer reads **the model chapter for its Part**, **the chapter right before its own** (for continuity, once it exists), its spec in `src/data/course/<subject>.json`, `docs/authoring.md` and this doc. Don't use one chapter as the model for the whole course.

| Subject / Part | Model chapter | Why |
|---|---|---|
| Math 116 sprint | `math/s116-real-numbers` | the approved pilot |
| Physics 116 sprint | `physics/s116-induction` | closest to the physics medians (2,477 words, 17 moments) |
| Chemistry content Parts (1–4) | `physics/s116-induction`, until a chemistry chapter has been reviewed against these targets; then the first reviewed chemistry chapter that best meets them | no chemistry chapter yet |
| Biology 116 sprint (all Parts) | `chemistry/s116-laws-atomic-theory` | reviewed against these targets (2,342 words, 23 moments, 3 predictions, 4 StudentAsks); history of science plus inference from data, like cell theory, Mendel and evolution |
| Exam-skills chapters (any science subject) | `physics/s116-physics-reasoning` | the reviewed science exam-skills chapter |

The model chapters were written before these targets. Copy their structure, voice, use of figures and perspectives, but take the counts from the targets above: `physics/s116-induction` has no `<Predict>` and only 2 `StudentAsks`.

## What the reviewers check
On top of facts, no jumps and recomputed answers, the teaching reviewer compares each chapter with its model chapter and the targets:
- moments and words per moment are within the target range;
- predictions come before reveals, and `StudentAsks` are real beginner questions;
- every figure has a task;
- the chapter continues from the previous one and its closing dialogue names the actual next one;
- the voice matches.

A chapter that reads as prose followed by a quiz fails this check, even if every fact is right.
