# Glossary and concept registry

One JSON file per chapter that introduces terms:

```
src/data/terms/<subject>/<chapter-slug>.json
```

`<subject>` is `site` or a subject id from `src/data/schema.ts` (`math`, `physics`, …). The file holds
the terms **that chapter introduces** (its `newConcepts` in `src/data/course/<subject>.json`), so every
concept has exactly one owner. `src/data/glossary.ts` merges all files at build time and validates each
entry against `TermEntry` in `src/data/schema.ts`.

## Shape

```jsonc
{
  "terms": [
    {
      "id": "<subject>.<kebab-case-id>",        // must start with this folder's subject
      "zh": "<繁體中文 term, Taiwan usage>",
      "en": "<English term>",
      "zhuyin": "<注音, optional>",
      "def": { "zh-tw": "<zh definition>", "en": "<en definition>" },
      "source": { "id": "<bibliography id>", "locator": "<page/entry, optional>", "verbatim": true },
      "kind": "concept",                         // or "vocab" (glossary-only, exempt from the no-jump rule)
      "deepens": "<earlier term id, optional>",  // a spiral revisit, e.g. 國中 → 高中 version of a law
      "aliases": { "zh": ["…"], "en": ["…"] },   // optional
      "forbidden": ["<wording we must not use>"] // optional, e.g. Mainland-only terms
    }
  ]
}
```

## Rules the merge enforces (tests/components/glossary.test.ts)

- Every entry passes the `TermEntry` schema (both definitions non-empty, ids kebab-case).
- An id appears in exactly one file across the whole folder.
- The id's prefix matches the folder: `math/…json` may only define `math.*` ids.
- `deepens` points at a term that exists.

## Content rules (from the plan; checked by later lint/tests)

- The zh/en pair comes from 樂詞網 (terms.naer.edu.tw) where a 高中以下 term set exists; `source.id`
  names that bibliography entry.
- MOE dictionary definitions are CC BY-ND: copy them verbatim and set `"verbatim": true`. An English
  gloss of such an entry is ours and must be written as our own text.
- Use `<Term t="<id>">` (or `[[<id>]]` inside a dialogue) in lessons; an unknown id fails the build.
