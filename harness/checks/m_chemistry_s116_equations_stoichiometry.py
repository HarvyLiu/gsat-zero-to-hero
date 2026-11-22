"""Checks for src/data/items/chemistry/s116-equations-stoichiometry.yaml (116 sprint: CJa-Ⅴc-2 balancing
chemical equations, CJa-Ⅴc-3 stoichiometry from a balanced equation).

Every check recomputes its item's key from the chemistry in the stem, never from item["answer"]:
- a formula is parsed into atom counts; a species is (formula, charge);
- an equation is balanced when every element (and, for ionic equations, the total charge) is the same
  on both sides;
- the smallest whole-number coefficients come from the null space of the atom (and charge) count
  matrix, solved exactly with SymPy and scaled to coprime positive integers (the chapter's 代數法);
- masses are exact SymPy Rationals with the atomic masses each stem states, and go
  mass ÷ M → moles → × coefficient ratio → moles → × M (the chapter's route).
"""

from __future__ import annotations

import re
from functools import reduce
from math import gcd

from sympy import Integer, Matrix, Rational, ilcm

# The atomic masses the stems state (H = 1, C = 12, O = 16, Mg = 24, Al = 27, Fe = 56).
AW = {"H": Integer(1), "C": Integer(12), "O": Integer(16), "Mg": Integer(24), "Al": Integer(27), "Fe": Integer(56)}

Species = tuple[str, int]  # (formula without brackets, charge)
Side = list[tuple[int, Species]]  # [(coefficient, species), ...]


def parse(formula: str) -> dict[str, int]:
    """'Al2O3' → {'Al': 2, 'O': 3}. Plain formulas without brackets."""
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


def sp(formula: str, charge: int = 0) -> Species:
    return (formula, charge)


def side_counts(side: Side) -> tuple[dict[str, int], int]:
    atoms: dict[str, int] = {}
    charge = 0
    for k, (f, q) in side:
        for el, n in parse(f).items():
            atoms[el] = atoms.get(el, 0) + k * n
        charge += k * q
    return atoms, charge


def balanced(left: Side, right: Side) -> bool:
    """Same count of every element and the same total charge on both sides."""
    return side_counts(left) == side_counts(right)


def smallest_coefficients(reactants: list[Species], products: list[Species]) -> list[int]:
    """Coprime positive integer coefficients that balance atoms and charge (null space of the count matrix)."""
    species = reactants + products
    elements = sorted({el for f, _ in species for el in parse(f)})
    rows = [[(1 if i < len(reactants) else -1) * parse(f).get(el, 0) for i, (f, _) in enumerate(species)] for el in elements]
    rows.append([(1 if i < len(reactants) else -1) * q for i, (_, q) in enumerate(species)])
    ns = Matrix(rows).nullspace()
    if len(ns) != 1:
        raise ValueError("the equation does not have a single balanced ratio")
    v = ns[0]
    v = v * reduce(ilcm, [Rational(x).q for x in v], 1)
    g = reduce(gcd, [int(abs(x)) for x in v])
    v = [int(x) // g for x in v]
    if all(x < 0 for x in v):
        v = [-x for x in v]
    if not all(x > 0 for x in v):
        raise ValueError("no all-positive balanced ratio")
    return v


def molar_mass(formula: str) -> Integer:
    return sum((AW[el] * n for el, n in parse(formula).items()), Integer(0))


def mass_of_product(given: str, given_mass: Rational, wanted: str, reactants: list[Species], products: list[Species]) -> Rational:
    """The chapter's route: mass ÷ M → mol → × coefficient ratio → mol → × M."""
    species = [f for f, _ in reactants + products]
    coef = dict(zip(species, smallest_coefficients(reactants, products)))
    n_given = Rational(given_mass) / molar_mass(given)
    n_wanted = n_given * Rational(coef[wanted], coef[given])
    return n_wanted * molar_mass(wanted)


# ---------------------------------------------------------------------------------------------------


def es_turn_coefficients_only(item: dict) -> list[bool]:
    """q-turn: carbon burns to carbon monoxide; C + O2 → CO is unbalanced. A fix is right only if it keeps
    the real substances (reactants C and O2, product CO: only coefficients may change) and balances.
    Options: C + O2 → CO2; 2C + O2 → 2CO; C + O → CO; C + O2 → CO + O."""
    real_reactants = {sp("C"), sp("O2")}
    real_products = {sp("CO")}
    options: list[tuple[Side, Side]] = [
        ([(1, sp("C")), (1, sp("O2"))], [(1, sp("CO2"))]),
        ([(2, sp("C")), (1, sp("O2"))], [(2, sp("CO"))]),
        ([(1, sp("C")), (1, sp("O"))], [(1, sp("CO"))]),
        ([(1, sp("C")), (1, sp("O2"))], [(1, sp("CO")), (1, sp("O"))]),
    ]
    return [
        {s for _, s in left} == real_reactants and {s for _, s in right} == real_products and balanced(left, right)
        for left, right in options
    ]


def es_aluminium_oxide(item: dict) -> list[bool]:
    """q1: which equation for aluminium burning to Al2O3 is balanced? Count every element on both sides.
    Options: 2Al + 3O2 → 2Al2O3; 4Al + 3O2 → 2Al2O3; 4Al + 6O2 → 2Al2O3; 2Al + O2 → Al2O3; 4Al + 2O2 → 2Al2O3."""
    options = [(2, 3, 2), (4, 3, 2), (4, 6, 2), (2, 1, 1), (4, 2, 2)]
    return [balanced([(a, sp("Al")), (b, sp("O2"))], [(c, sp("Al2O3"))]) for a, b, c in options]


def es_iron_oxide_co(item: dict) -> tuple[int, int, int, int]:
    """q2: a Fe2O3 + b CO → c Fe + d CO2 in smallest whole numbers → 1, 3, 2, 3."""
    a, b, c, d = smallest_coefficients([sp("Fe2O3"), sp("CO")], [sp("Fe"), sp("CO2")])
    return (a, b, c, d)


def es_co_statements(item: dict) -> list[bool]:
    """q3: 2CO + O2 → 2CO2 (C = 12, O = 16). Each statement recomputed from the balanced equation:
    (1) molecule ratio CO : O2 : CO2 = 2 : 1 : 2;  (2) mass ratio CO : O2 : CO2 = 2 : 1 : 2;
    (3) total atoms before = after;  (4) total molecules before = after;  (5) 2 mol CO gives 88 g CO2."""
    reac, prod = [sp("CO"), sp("O2")], [sp("CO2")]
    k = smallest_coefficients(reac, prod)  # [2, 1, 2]
    names = ["CO", "O2", "CO2"]
    masses = [k[i] * molar_mass(n) for i, n in enumerate(names)]

    def same_ratio(xs, ys) -> bool:
        return all(Rational(x, xs[0]) == Rational(y, ys[0]) for x, y in zip(xs, ys))

    left: Side = [(k[0], reac[0]), (k[1], reac[1])]
    right: Side = [(k[2], prod[0])]
    atoms_before = sum(side_counts(left)[0].values())
    atoms_after = sum(side_counts(right)[0].values())
    s1 = same_ratio(k, [2, 1, 2])
    s2 = same_ratio(masses, [2, 1, 2])
    s3 = atoms_before == atoms_after
    s4 = k[0] + k[1] == k[2]
    s5 = Integer(2) * Rational(k[2], k[0]) * molar_mass("CO2") == 88
    return [s1, s2, s3, s4, s5]


def es_butane_o2(item: dict) -> list[bool]:
    """q4: a C4H10 + b O2 → c CO2 + d H2O in smallest whole numbers: 2, 13, 8, 10, so b = 13.
    Options for b: 13/2, 9, 13, 8, 26."""
    b = smallest_coefficients([sp("C4H10"), sp("O2")], [sp("CO2"), sp("H2O")])[1]
    options = [Rational(13, 2), Integer(9), Integer(13), Integer(8), Integer(26)]
    return [b == o for o in options]


def es_peroxide_oxygen_mass(item: dict) -> int:
    """q5: H2O2 decomposes to H2O and O2 (H = 1, O = 16): 2H2O2 → 2H2O + O2.
    34 g H2O2 = 1 mol → 1/2 mol O2 → 16 g."""
    m = mass_of_product("H2O2", Integer(34), "O2", [sp("H2O2")], [sp("H2O"), sp("O2")])
    assert m.is_integer
    return int(m)


def es_magnesium_oxide_mass(item: dict) -> list[bool]:
    """q6: 4.8 g Mg burns to MgO (Mg = 24, O = 16): 2Mg + O2 → 2MgO; 0.2 mol Mg → 0.2 mol MgO → 8.0 g.
    Options (g): 4.0, 8.0, 3.2, 9.6, 16."""
    m = mass_of_product("Mg", Rational(48, 10), "MgO", [sp("Mg"), sp("O2")], [sp("MgO")])
    options = [Integer(4), Integer(8), Rational(32, 10), Rational(96, 10), Integer(16)]
    return [m == o for o in options]


def es_silver_copper_ionic(item: dict) -> list[bool]:
    """q7 (enrichment): copper in a silver-ion solution, Ag+ + Cu → Ag + Cu2+. The right equation balances
    atoms AND charge with coprime whole-number coefficients.
    Options: (1,1,1,1); (2,1,2,1); (1,2,1,2); (2,2,2,1); (1,1,2,1) for Ag+, Cu, Ag, Cu2+."""
    ag_ion, cu, ag, cu_ion = sp("Ag", 1), sp("Cu"), sp("Ag"), sp("Cu", 2)
    options = [(1, 1, 1, 1), (2, 1, 2, 1), (1, 2, 1, 2), (2, 2, 2, 1), (1, 1, 2, 1)]
    return [
        balanced([(a, ag_ion), (b, cu)], [(c, ag), (d, cu_ion)]) and reduce(gcd, (a, b, c, d)) == 1
        for a, b, c, d in options
    ]
