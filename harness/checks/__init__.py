"""SymPy answer checks for practice items.

An item names its check as `verify: <module>:<function>`; the harness imports
`checks.<module>` (harness/checks/<module>.py, dots for sub-packages) and calls
`<function>(item)` with the item as parsed from YAML.

A check recomputes the answer FROM THE STEM ALONE, never by reading the stored key, and returns:
  - 單選 / 多選: one truth value per option, in option order (bool or a decided SymPy boolean).
    單選 needs exactly one True; 多選 at least one (the 簡章 says at least one option is correct).
  - 選填: an exact integer (compared with the number the cells spell), or a tuple of parts for
    several groups of cells, e.g. (p, q) for a fraction p/q; a string part keeps leading zeros ('05').
  - numeric: an exact number (Integer or Rational; floats are refused).
  - 混合題: True when the identities behind the model answer hold.
See harness/README.md for the full contract and how to add a check.
"""
