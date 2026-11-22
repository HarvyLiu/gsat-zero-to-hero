"""Checks for src/data/items/chemistry/s116-laws-atomic-theory.yaml (116 sprint: CAa-Ⅴc-1, CAa-Ⅴc-2,
CJa-Ⅴc-1, CMb-Ⅴc-1: conservation of mass, definite and multiple proportions, Dalton's atomic theory,
and the scientists behind them).

How the keys are recomputed (never from item["answer"]):
- Masses with SymPy exact Rationals. Atomic weights are the usual whole-number relative masses
  (Cl = 35.5); stems that need a number state the ones they use.
- Formulas are parsed into atom counts, so "same two elements, different compounds" and the
  fixed-mass oxygen ratios are computed, not typed.
- Qualitative rules are code: an open-vessel balance reading changes by (mass gained from the air)
  − (mass of gas escaping); Dalton's postulates are a small table of claims that each statement is
  tested against; history pairings come from an explicit facts table with a source per fact.
"""

from __future__ import annotations

import re

import sympy as sp
from sympy import Rational as R

# Relative atomic masses (standard whole-number values used in Taiwan high-school chemistry).
MASS = {"H": R(1), "C": R(12), "N": R(14), "O": R(16), "Na": R(23), "Mg": R(24), "S": R(32),
        "Cl": R(71, 2), "K": R(39), "Ca": R(40), "Fe": R(56), "Cu": R(64)}


def _atoms(formula: str) -> dict[str, int]:
    """Atom counts of a simple formula without brackets, e.g. 'H2O2' -> {'H': 2, 'O': 2}."""
    out: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        out[el] = out.get(el, 0) + (int(n) if n else 1)
    return out


def _mass(formula: str) -> sp.Rational:
    return sum((MASS[el] * n for el, n in _atoms(formula).items()), R(0))


def _is_simple_whole_ratio(r: sp.Rational, limit: int = 10) -> bool:
    """A ratio p/q in lowest terms with small whole numbers (the 'simple integer ratio' of the law)."""
    r = sp.nsimplify(r)
    return r.is_rational and r > 0 and r.p <= limit and r.q <= limit


# --- opening and mid-chapter turns ---------------------------------------------------------------


def lat_turn_magnesium(item: dict) -> list[bool]:
    """q-turn: 2Mg + O2 -> 2MgO in air; all the powder is collected. The powder's mass is the
    magnesium plus the oxygen it took up from the air (conservation of mass), so it is heavier.
    Options: heavier; lighter; same; first heavier then back; can't tell."""
    m_mg = 2 * MASS["Mg"]  # per 2 Mg in the equation
    m_powder = 2 * _mass("MgO")
    assert m_powder == m_mg + _mass("O2")  # mass balance of the equation itself
    outcome = "heavier" if m_powder > m_mg else ("lighter" if m_powder < m_mg else "same")
    # (4) mass of the collected solid while a fraction f of the magnesium has burned: oxygen only
    # joins, nothing leaves, so it can never fall back.
    solid = [(1 - f) * m_mg + f * m_powder for f in (R(k, 10) for k in range(11))]
    never_falls = all(b >= a for a, b in zip(solid, solid[1:]))
    up_then_back = (not never_falls) and solid[-1] == solid[0]
    # (5) the final mass is fixed by what combines (Mg and the O it takes up); brightness isn't a factor
    mass_factors = {"magnesium", "oxygen combined"}
    depends_on_brightness = "flame brightness" in mass_factors
    return [outcome == "heavier", outcome == "lighter", outcome == "same", up_then_back, depends_on_brightness]


# Dalton's postulates as the chapter states them, with whether each claims the atom has no parts.
DALTON = {
    "indivisible": {"claims_no_internal_parts": True},
    "whole_number_compounds": {"claims_no_internal_parts": False},
    "rearrangement": {"claims_no_internal_parts": False},
    "not_created_destroyed": {"claims_no_internal_parts": False},
}


def lat_turn_dalton_revision(item: dict) -> list[bool]:
    """q-dalton: 國中 Aa-Ⅳ-1 teaches that atoms contain electrons and a nucleus, i.e. internal parts.
    A postulate conflicts with that exactly when it claims the atom has no internal parts.
    Options: indivisible; whole-number compounds; rearrangement; not created/destroyed; none."""
    atom_has_parts = True
    order = ["indivisible", "whole_number_compounds", "rearrangement", "not_created_destroyed"]
    conflicts = [atom_has_parts and DALTON[k]["claims_no_internal_parts"] for k in order]
    return conflicts + [not any(conflicts)]


# --- Check yourself ------------------------------------------------------------------------------


def lat_closed_carbon(item: dict) -> int:
    """q1: 6 g C + 16 g O2 react completely in a sealed vessel to CO2 only. First confirm the masses
    really are in CO2's ratio (so 'nothing left over' is consistent), then conservation of mass."""
    m_c, m_o = R(6), R(16)
    assert m_c / m_o == MASS["C"] / (2 * MASS["O"])
    total = m_c + m_o
    assert total.q == 1
    return int(total)


# Open-vessel processes: (mass taken from the air, mass of gas escaping) per formula unit of the
# equation the stem describes. The balance reading changes by gained − escaped.
OPEN_PROCESSES = [
    # C + O2 -> CO2(g), the CO2 drifts away
    (_mass("O2"), _mass("CO2")),
    # 2Mg + O2 -> 2MgO, all the powder stays
    (_mass("O2"), R(0)),
    # CaCO3 + 2HCl -> CaCl2 + H2O + CO2(g), the CO2 escapes; nothing comes in from the air
    (R(0), _mass("CO2")),
    # iron combines with oxygen from the air; all the rust stays (any iron oxide: only O enters)
    (_mass("O2"), R(0)),
    # ice -> water, a physical change: nothing enters or leaves
    (R(0), R(0)),
]


def lat_open_vessel(item: dict) -> list[bool]:
    """q2: which readings end lower? Reading change = gained from air − gas escaping."""
    return [gained - escaped < 0 for gained, escaped in OPEN_PROCESSES]


def lat_mgo_from_nine(item: dict) -> int:
    """q3: Mg : O = 3 : 2 in MgO (also recomputed from Mg = 24, O = 16); 9 g Mg burns completely."""
    ratio = MASS["Mg"] / MASS["O"]
    assert ratio == R(3, 2)
    m_mg = R(9)
    m_o = m_mg / ratio
    total = m_mg + m_o
    assert total.q == 1
    return int(total)


def lat_copper_table(item: dict) -> list[bool]:
    """q4: copper heated in air to CuO. Oxygen taken up = product − copper. Pure CuO has the fixed
    ratio Cu : O = 64 : 16 = 4 : 1; a group with less oxygen than that did not react completely.
    Options: A; B; C; D; all four complete."""
    data = [(R(2), R(5, 2)), (R(16, 5), R(4)), (R(24, 5), R(28, 5)), (R(6), R(15, 2))]
    pure = MASS["Cu"] / MASS["O"]
    incomplete = [cu / (prod - cu) > pure for cu, prod in data]
    # every complete group must match the pure ratio exactly (no group with too much oxygen)
    assert all(cu / (prod - cu) == pure for (cu, prod), bad in zip(data, incomplete) if not bad)
    return incomplete + [not any(incomplete)]


def _shows_multiple_proportions(f1: str, f2: str) -> bool:
    """Same two elements, two different compounds, and with one element fixed the other's masses are
    in a simple whole-number ratio."""
    a, b = _atoms(f1), _atoms(f2)
    if set(a) != set(b) or len(a) != 2:
        return False  # different element pairs, or not a two-element compound (e.g. O2, O3)
    x, y = sorted(a)
    ra = R(a[y], a[x])  # atoms of y per atom of x; mass ratio y : x is proportional to this
    rb = R(b[y], b[x])
    if ra == rb:
        return False  # one and the same compound: that is definite proportions
    return _is_simple_whole_ratio(rb / ra)


def lat_multiple_pairs(item: dict) -> list[bool]:
    """q5: SO2/SO3; H2O/H2S; FeO/Fe2O3; NO/NO2; diamond/graphite (both carbon only, written 'C')."""
    pairs = [("SO2", "SO3"), ("H2O", "H2S"), ("FeO", "Fe2O3"), ("NO", "NO2"), ("C", "C")]
    return [_shows_multiple_proportions(p, q) for p, q in pairs]


def lat_nitrogen_oxides(item: dict) -> int:
    """q6: N : O = 7 : 4 (A) and 7 : 16 (B). Fix N, compare O. (These are N2O and NO2: recompute the
    stem's ratios from the formulas as a cross-check.)"""
    a, b = (R(7), R(4)), (R(7), R(16))
    assert (2 * MASS["N"]) / MASS["O"] == a[0] / a[1]  # N2O
    assert MASS["N"] / (2 * MASS["O"]) == b[0] / b[1]  # NO2
    o_a = a[1] * (R(1) / a[0])  # oxygen per unit nitrogen
    o_b = b[1] * (R(1) / b[0])
    k = o_b / o_a
    assert k.q == 1 and _is_simple_whole_ratio(k)
    return int(k)


# Dalton's theory as claims, used to judge statements in q7. 'modern_divisible' is the later finding
# (國中 Aa-Ⅳ-1: atoms contain electrons and a nucleus) that revises the first postulate.
THEORY = {
    "atoms_conserved_in_reaction": True,
    "atom_mass_fixed_per_element": True,
    "fixed_number_ratio_in_compound": True,
    "whole_atoms_only": True,
    "modern_divisible": True,
}


def lat_dalton_explains(item: dict) -> list[bool]:
    """q7: each option is a claim; it is right when it agrees with the table above."""
    s1 = THEORY["atoms_conserved_in_reaction"] and THEORY["atom_mass_fixed_per_element"]  # mass conserved
    s2 = not THEORY["atoms_conserved_in_reaction"]  # 'reactions make new atoms'
    s3 = not THEORY["fixed_number_ratio_in_compound"]  # 'ratio changes with preparation'
    s4 = not THEORY["whole_atoms_only"]  # 'half atoms'
    s5 = not THEORY["modern_divisible"]  # 'indivisible is still entirely correct'
    return [s1, s2, s3, s4, s5]


# Contributions, each with its source. Only facts from the chapter's sources are used.
FACTS = {
    # src/data/registry/codes/nat.json, CAa-Vc-1 keyConcepts: "Lavoisier: the element concept and
    # oxidation; quantitative check of mass conservation"
    ("Lavoisier", "element_concept"),
    ("Lavoisier", "oxidation_as_combining_with_oxygen"),
    ("Lavoisier", "quantitative_check_of_mass_conservation"),
    # nat.json CAa-Vc-1 keyConcepts: "Dalton's atomic theory"
    ("Dalton", "atomic_theory"),
}


def lat_history_pairs(item: dict) -> list[bool]:
    """q8: a pairing is correct when every contribution it names is in FACTS for that person.
    Option 5 claims Lavoisier overturned mass conservation, which contradicts his recorded check."""
    options = [
        ("Lavoisier", ["atomic_theory"]),
        ("Dalton", ["element_concept"]),
        ("Lavoisier", ["element_concept", "quantitative_check_of_mass_conservation"]),
        ("Dalton", ["oxidation_as_combining_with_oxygen"]),
        ("Lavoisier", ["overturned_mass_conservation"]),
    ]
    return [all((who, c) in FACTS for c in claims) for who, claims in options]
