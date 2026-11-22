"""Checks for src/data/items/chemistry/s116-formulas-and-mole.yaml (116 sprint: CJa-Ⅴc-1 chemical
formulas, CJa-Ⅴc-3 atomic weight and the mole).

Every check recomputes its item's key from the chemistry in the stem, never from item["answer"]:
- formulas are parsed into atom counts (no brackets are needed in this bank);
- empirical formulas are the atom counts divided by their gcd;
- masses, percentages and particle counts are exact SymPy Rationals, with the atomic masses and
  N_A = 6.02 × 10^23 that each stem states;
- an empirical formula from mass data is found the way the chapter teaches it: mass ÷ atomic weight,
  ÷ the smallest, then the smallest whole multiplier that makes every part an integer.
"""

from __future__ import annotations

import re
from functools import reduce
from math import gcd

from sympy import Integer, Rational

# The atomic masses the stems state (H = 1, C = 12, N = 14, O = 16, Fe = 56).
AW = {"H": Integer(1), "C": Integer(12), "N": Integer(14), "O": Integer(16), "Fe": Integer(56)}
# Avogadro's number as the stems state it, exact: 6.02 × 10^23.
NA = Rational(602, 100) * Integer(10) ** 23


def parse(formula: str) -> dict[str, int]:
    """'NH4NO3' → {'N': 2, 'H': 4, 'O': 3}. Accepts mhchem-free plain formulas without brackets."""
    counts: dict[str, int] = {}
    pos = 0
    for m in re.finditer(r"([A-Z][a-z]?)(\d*)", formula):
        if m.start() != pos:
            raise ValueError(f"cannot parse {formula!r}")
        pos = m.end()
        counts[m.group(1)] = counts.get(m.group(1), 0) + (int(m.group(2)) if m.group(2) else 1)
    if pos != len(formula):
        raise ValueError(f"cannot parse {formula!r}")
    return counts


def empirical(counts: dict[str, int]) -> dict[str, int]:
    g = reduce(gcd, counts.values())
    return {el: n // g for el, n in counts.items()}


def formula_weight(counts: dict[str, int]) -> Integer:
    return sum((AW[el] * n for el, n in counts.items()), Integer(0))


def ratio_from_masses(masses: dict[str, Rational]) -> dict[str, int]:
    """Mass of each element → simplest whole-number atom ratio (the chapter's table method)."""
    rel = {el: Rational(m) / AW[el] for el, m in masses.items()}
    smallest = min(rel.values())
    rel = {el: v / smallest for el, v in rel.items()}
    for k in range(1, 11):
        if all((k * v).is_integer for v in rel.values()):
            whole = {el: int(k * v) for el, v in rel.items()}
            return empirical(whole)
    raise ValueError("no small whole-number multiplier")


def _exp10(coef: str, exp: int) -> Rational:
    return Rational(coef) * Integer(10) ** exp


# ---------------------------------------------------------------------------------------------------


def fm_turn_equal_counts(item: dict) -> list[bool]:
    """q-turn: one C atom has 12 times the mass of one H atom. Count = total mass ÷ mass per atom, so
    N(C) / N(H) = (12 / 12) / (1 / 1) = 1 → the same number.
    Options: carbon more; hydrogen more; the same; cannot compare without the real atom masses."""
    m_h = Integer(1)  # any unit: only the ratio 12 : 1 is given, and it is all we need
    m_c = 12 * m_h
    n_c = Integer(12) / m_c
    n_h = Integer(1) / m_h
    outcome = "C" if n_c > n_h else "H" if n_h > n_c else "same"
    return [o == outcome for o in ("C", "H", "same", "cannot")]


def fm_same_empirical_pair(item: dict) -> list[bool]:
    """q1: which pair shares one empirical formula? Reduce each by the gcd of its subscripts."""
    pairs = [("C2H2", "C6H6"), ("C2H4", "C2H6"), ("CH4", "C2H4"), ("H2O", "H2O2"), ("CO", "CO2")]
    return [empirical(parse(a)) == empirical(parse(b)) for a, b in pairs]


def fm_sucrose_mw(item: dict) -> int:
    """q2: molecular weight of sucrose C12H22O11 with H = 1, C = 12, O = 16 → 342."""
    return int(formula_weight(parse("C12H22O11")))


def fm_percent_n_ammonium_nitrate(item: dict) -> list[bool]:
    """q3: mass percent of N in NH4NO3 (N = 14, H = 1, O = 16) = 28 / 80 × 100 = 35.
    Options (in %): 17.5, 35, 46.7, 60, 82.4."""
    c = parse("NH4NO3")
    pct = AW["N"] * c["N"] / formula_weight(c) * 100
    options = [Rational(35, 2), Integer(35), Rational(467, 10), Integer(60), Rational(824, 10)]
    return [pct == o for o in options]


def fm_hydrocarbon_molecular_formula(item: dict) -> tuple[int, int]:
    """q4: a hydrocarbon is 80% C and 20% H by mass, molecular weight 30 (H = 1, C = 12).
    Empirical: 80/12 : 20/1 = 1 : 3 → CH3 (15); 30 / 15 = 2 → C2H6, cells ① = 2, ② = 6."""
    emp = ratio_from_masses({"C": Integer(80), "H": Integer(20)})
    k = Integer(30) / formula_weight(emp)
    assert k.is_integer
    return (int(emp["C"] * k), int(emp["H"] * k))


def fm_mole_statements(item: dict) -> list[bool]:
    """q5 (H = 1, N = 14, O = 16, N_A = 6.02 × 10^23). Each statement recomputed:
    (1) 1 mol H2O holds N_A molecules: a mole is N_A particles of the kind named.
    (2) 1 mol H2O holds 3 mol of atoms: atoms per molecule × 1 mol.
    (3) 1 mol N2 and 1 mol N have the same mass: 28 g vs 14 g.
    (4) 2 g of H2 is 1 mol: 2 g ÷ 2 g/mol.
    (5) 1 mol of any substance has a mass of 1 g: false already for H2O (18 g)."""
    one = Integer(1)
    s1 = one * NA == NA  # molecules in 1 mol of molecules
    s2 = one * sum(parse("H2O").values()) == 3
    s3 = formula_weight(parse("N2")) == formula_weight(parse("N"))
    s4 = Integer(2) / formula_weight(parse("H2")) == 1
    s5 = all(formula_weight(parse(f)) == 1 for f in ("H2O", "N2", "H2"))
    return [s1, s2, s3, s4, s5]


def fm_co2_oxygen_atoms(item: dict) -> list[bool]:
    """q6: O atoms in 4.4 g CO2 (C = 12, O = 16, N_A = 6.02 × 10^23):
    4.4 / 44 = 0.1 mol CO2 → 0.2 mol O → 1.204 × 10^23.
    Options: 6.02e22, 1.204e23, 1.806e23, 6.02e23, 1.204e24."""
    c = parse("CO2")
    n_o = Rational(44, 10) / formula_weight(c) * c["O"]
    value = n_o * NA
    options = [_exp10("6.02", 22), _exp10("1.204", 23), _exp10("1.806", 23), _exp10("6.02", 23), _exp10("1.204", 24)]
    return [value == o for o in options]


def fm_ammonia_mass(item: dict) -> int:
    """q7: mass of 1.204 × 10^24 NH3 molecules (N = 14, H = 1, N_A = 6.02 × 10^23):
    1.204e24 / 6.02e23 = 2 mol, × 17 g/mol = 34 g."""
    n = _exp10("1.204", 24) / NA
    m = n * formula_weight(parse("NH3"))
    assert m.is_integer
    return int(m)


def fm_iron_oxide_from_masses(item: dict) -> list[bool]:
    """q8: 5.6 g Fe combines with oxygen into 8.0 g of oxide (Fe = 56, O = 16).
    O = 8.0 − 5.6 = 2.4 g; 5.6/56 : 2.4/16 = 0.1 : 0.15 = 1 : 1.5 → × 2 → Fe2O3.
    Options: FeO, Fe2O3, Fe3O4, FeO2, Fe3O2."""
    fe = Rational(56, 10)
    o = Rational(80, 10) - fe
    emp = ratio_from_masses({"Fe": fe, "O": o})
    return [empirical(parse(f)) == emp for f in ("FeO", "Fe2O3", "Fe3O4", "FeO2", "Fe3O2")]
