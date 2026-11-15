# Item verification harness (Python + SymPy)

Dev-only; nothing here ships with the site. It reads the same YAML item banks as the site
(`src/data/items/<subject>/<slug>.yaml`), checks their shape, and recomputes answer keys with SymPy.

```sh
# from the repo root
harness/.venv/Scripts/python -m pytest harness                      # the test suite (fixtures + every real bank)
harness/.venv/Scripts/python harness/verify_items.py                # every bank in src/data/items
harness/.venv/Scripts/python harness/verify_items.py --fixtures     # ... plus tests/fixtures/items/*.yaml
harness/.venv/Scripts/python harness/verify_items.py path/to/bank.yaml
harness/.venv/Scripts/python harness/verify_items.py --strict       # math/physics/chemistry items must all have a check
```

Exit status 0 means every file passed; 1 means at least one problem, listed per file and item.
The venv has `sympy`, `pyyaml` and `pytest` (harness/.venv is git-ignored).

## What is checked

1. **Shape.** A plain-Python mirror of `schema.ItemBank` (src/data/schema.ts) plus the cross-field rules of
   `src/lib/items.ts`: both locales present with the same fields, option counts equal across locales,
   0-based answer indices in range, fill cells only `0`–`9` and `−` (U+2212), numeric keys readable in their
   `accept` form, unique ids ignoring `@version`, the chapter matching the file path. Keep the two in sync
   when the schema changes. Items with shape problems are not run.
2. **Keys.** For every item with `verify: <module>:<function>`, the harness imports
   `harness/checks/<module>.py` (dots for sub-packages: `math.real_numbers` → `checks/math/real_numbers.py`)
   and calls `<function>(item)`. The check **recomputes the answer from the stem alone**. It never reads
   `item["answer"]`. The harness compares the result with the stored key:

| type | the check returns | passes when |
|---|---|---|
| `single` | one truth value per option, in order | exactly one is true, and it is the key |
| `multi` | one truth value per option, in order | at least one is true (the 簡章 says at least one option is correct) and the true set equals the key |
| `fill` | an exact integer | the cells spell that integer (`['−','1','2']` → −12) |
| `fill` | a tuple of parts, e.g. `(p, q)` for p/q | the parts written out (`−` for minus) equal the cells joined; a string part keeps leading zeros, e.g. `'05'` |
| `numeric` | an exact Integer or Rational | it equals the key by value (a float key is read through its shortest decimal, like `String(n)` in JS) |
| `mixed` | `True` | the identities behind the model answer hold |

Truth values may be Python bools or decided SymPy booleans. An undecided one (`None`, an unevaluated
relational) is an error rather than a silent False. Floats are refused: return exact numbers.

Without `--strict`, a math, physics or chemistry item that has no check is a warning. G3 of the accuracy
pipeline (docs/design/04-accuracy-pipeline.md) expects every such key to be machine-checked, so CI should
run with `--strict` once real banks exist.

## Adding a check

```python
# harness/checks/math_real_numbers.py   (item: verify: math_real_numbers:q3)
import sympy as sp

def q3(item):
    """√2 × √8 against the five options of q3."""
    value = sp.sqrt(2) * sp.sqrt(8)
    return [sp.simplify(value - o) == 0 for o in (2, 4, sp.sqrt(10), 8, 16)]
```

When you revise an item, bump its `@version` and update its check in the same change.

## YAML conventions (the site reads YAML 1.2)

- Single-quote any string with TeX (`'$\sqrt{2}$'`): single-quoted YAML keeps backslashes as typed.
  Double quotes would turn `\f` and `\t` into escapes.
- Quote fill cells: `answer: ['−', '1', '2']`. A bare `1` is a number, not a cell.
- `verify_items.py` reads YAML 1.2 core scalars like the `yaml` npm package (`no` stays a string,
  `010` is 10, dates stay strings) and rejects duplicate keys, so Python and the site never disagree
  about a value.
- Inline text supports `**bold**`, `*italic*`, `` `code` ``, `$math$`, `$$display$$` and one line break per
  newline. Write `\$` and `\*` for literal characters. CJK text inside math must be in `\text{…}`.

## Fixtures

`tests/fixtures/items/*.yaml` are small original banks covering every item type. They are test data,
not lessons, and are checked by `harness/checks/fixtures.py`. `tests/fixtures/items/bad/` holds banks
that must fail: `wrong-key.yaml` (schema-valid, wrong keys that only SymPy can catch) and `missing-en.yaml`
(no English text). `--fixtures` does not read `bad/`; `harness/test_items.py` runs those files on purpose.
