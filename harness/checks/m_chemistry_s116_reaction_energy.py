"""Checks for src/data/items/chemistry/s116-reaction-energy.yaml (116 sprint: CBa-Ⅴc-1 and CBa-Ⅴc-2,
energy changes in reactions and thermochemical equations).

Every check recomputes its item's key from the chemistry in the stem, never from item["answer"]:
- a thermochemical equation is a dict of signed coefficients (reactants negative, products positive)
  plus an exact Delta H; scaling multiplies both, reversing negates both;
- an equation is balanced when every element's atom count sums to zero over the signed coefficients;
- Delta H = (energy of products) - (energy of reactants); negative means exothermic;
- energy conservation: the surroundings gain -Delta H, so they warm when Delta H < 0;
- heat from a mass goes mass / molar mass -> moles -> moles x |Delta H| / coefficient, all with SymPy
  Rationals and the atomic masses each stem states.
The Delta H values are the ones written in each stem (rounded textbook values).
"""

from __future__ import annotations

import re

import sympy as sp
from sympy import Integer, Rational

# The atomic masses the stems state (H = 1, C = 12, O = 16, Ca = 40).
AW = {"H": Integer(1), "C": Integer(12), "O": Integer(16), "Ca": Integer(40)}


def parse(formula: str) -> dict[str, int]:
    """'C2H5OH' -> {'C': 2, 'H': 6, 'O': 1}. Plain formulas without brackets; no states."""
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


def molar_mass(formula: str) -> Integer:
    return sum((AW[el] * n for el, n in parse(formula).items()), Integer(0))


class Thermo:
    """A thermochemical equation: signed coefficients (reactants < 0, products > 0) and Delta H in kJ."""

    def __init__(self, reactants: dict[str, Rational], products: dict[str, Rational], dh) -> None:
        self.coef: dict[str, Rational] = {}
        for sp, c in reactants.items():
            self.coef[sp] = self.coef.get(sp, Integer(0)) - Rational(c)
        for sp, c in products.items():
            self.coef[sp] = self.coef.get(sp, Integer(0)) + Rational(c)
        self.dh = Rational(dh)

    def scaled(self, k) -> "Thermo":
        k = Rational(k)
        t = Thermo({}, {}, self.dh * k)
        t.coef = {sp: c * k for sp, c in self.coef.items()}
        return t

    def reversed(self) -> "Thermo":
        return self.scaled(-1)

    def balanced(self) -> bool:
        totals: dict[str, Rational] = {}
        for sp, c in self.coef.items():
            for el, n in parse(sp).items():
                totals[el] = totals.get(el, Integer(0)) + c * n
        return all(v == 0 for v in totals.values())

    def heat_per_mole_of(self, species: str) -> Rational:
        """|Delta H| per mole of one species: Delta H / its coefficient, in size."""
        return abs(self.dh / self.coef[species])

    def same_as(self, other: "Thermo") -> bool:
        keys = set(self.coef) | set(other.coef)
        return all(self.coef.get(k, 0) == other.coef.get(k, 0) for k in keys) and self.dh == other.dh


def kind(dh) -> str:
    """Sign rule of Delta H = E(products) - E(reactants)."""
    dh = Rational(dh)
    return "exo" if dh < 0 else "endo" if dh > 0 else "none"


# Shared equations, with the Delta H values the stems give.
H2_COMBUSTION = Thermo({"H2": 2, "O2": 1}, {"H2O": 2}, -572)  # 2H2(g) + O2(g) -> 2H2O(l)


# ---------------------------------------------------------------------------------------------------


# What a temperature observation of the container says about the heat q_out that flows from the
# reacting substances to the surroundings: its SIGN only (the size stays unknown).
OBSERVATION_SIGN = {"container gets hot": 1, "container gets cold": -1}


def re_turn_before_higher(item: dict) -> list[bool]:
    """q-turn: hydrogen burns and the container gets very hot (the stem's observation).
    Conservation of total energy: E_chem(before) = E_chem(after) + q_out. The observation fixes only the
    sign of q_out, its size is a positive unknown, and E_chem(after) is an unknown reference level.
    Options: before (2H2 + O2) higher; after (2H2O) higher; equal because energy is conserved;
    cannot tell without real values (true only if the observation gave no sign)."""
    observed = "container gets hot"
    sign = OBSERVATION_SIGN.get(observed)
    if sign is None:
        outcome = "cannot"
    else:
        size = sp.Symbol("q", positive=True)
        e_after = sp.Symbol("E_after", real=True)
        e_before = e_after + sign * size
        diff = sp.simplify(e_before - e_after)
        outcome = ("before" if diff.is_positive else "after" if diff.is_negative
                   else "equal" if diff.is_zero else "cannot")
    return [o == outcome for o in ("before", "after", "equal", "cannot")]


def re_reverse_water(item: dict) -> list[bool]:
    """q-reverse: 2H2(g) + O2(g) -> 2H2O(l), Delta H = -572 kJ. Decomposing 2 mol H2O(l) is the whole
    equation reversed: Delta H = +572 kJ. Options: -572, +572, +286, 0."""
    rev = H2_COMBUSTION.reversed()
    assert rev.coef["H2O"] == -2  # 2 mol of water is used up: exactly the reversed equation
    return [rev.dh == o for o in (Integer(-572), Integer(572), Integer(286), Integer(0))]


def re_read_diagram(item: dict) -> list[bool]:
    """q1: reactants at 350 kJ, products at 230 kJ (relative). Delta H = 230 - 350 = -120 -> exo.
    Options as (kind, Delta H): (endo, +120), (exo, -120), (exo, +120), (endo, -120), (exo, -580)."""
    dh = Integer(230) - Integer(350)
    options = [("endo", 120), ("exo", -120), ("exo", 120), ("endo", -120), ("exo", -580)]
    return [k == kind(dh) and Integer(v) == dh for k, v in options]


def re_generic_endothermic(item: dict) -> list[bool]:
    """q2: A2(g) + B2(g) -> 2AB(g), Delta H = +60 kJ.
    (1) endothermic: sign rule. (2) 1 mol AB absorbs 30 kJ: scale by 1/2.
    (3) 2AB -> A2 + B2 has Delta H = +60: reversing negates, so false.
    (4) reactants' total energy is higher than products': E_p - E_r = Delta H > 0, so false.
    (5) without outside heating the surroundings cool: they gain -Delta H < 0."""
    eq = Thermo({"A2": 1, "B2": 1}, {"AB": 2}, 60)
    s1 = kind(eq.dh) == "endo"
    half = eq.scaled(Rational(1, 2))
    s2 = half.coef["AB"] == 1 and half.dh == 30
    s3 = eq.reversed().dh == 60
    e_r = Integer(0)
    e_p = e_r + eq.dh
    s4 = e_r > e_p
    s5 = -eq.dh < 0
    return [s1, s2, s3, s4, s5]


def re_hydrogen_heat(item: dict) -> int:
    """q3: heat released by burning 10 g H2 (H = 1) with 2H2 + O2 -> 2H2O(l), Delta H = -572 kJ:
    10 / 2 = 5 mol; 572 / 2 = 286 kJ per mol H2; 5 x 286 = 1430 kJ."""
    n = Integer(10) / molar_mass("H2")
    q = n * H2_COMBUSTION.heat_per_mole_of("H2")
    assert kind(H2_COMBUSTION.dh) == "exo" and q.is_integer
    return int(q)


def re_limestone_heat(item: dict) -> int:
    """q4: CaCO3(s) -> CaO(s) + CO2(g), Delta H = +178 kJ (Ca = 40, C = 12, O = 16).
    25 g / 100 g/mol = 0.25 mol; 0.25 x 178 = 44.5 kJ absorbed; the stem writes ①②.③ kJ."""
    eq = Thermo({"CaCO3": 1}, {"CaO": 1, "CO2": 1}, 178)
    assert eq.balanced() and kind(eq.dh) == "endo"
    q = Integer(25) / molar_mass("CaCO3") * eq.heat_per_mole_of("CaCO3")
    tenths = q * 10
    assert tenths.is_integer and 100 <= tenths < 1000
    t = int(tenths)
    return (t // 100, t // 10 % 10, t % 10)


def re_propane_equation(item: dict) -> list[bool]:
    """q5: 1 mol C3H8(g) burns to CO2(g) and H2O(l), releasing 2220 kJ. An option is right when it is
    balanced, has the right sign (exo -> negative) and Delta H = -2220 x (coefficient of C3H8).
    Options: (A) 1:5:3:4, +2220; (B) 2:10:6:8, -2220; (C) 1:5:3:4, -2220; (D) 1:4:3:4, -2220."""
    per_mol = Integer(-2220)  # released -> negative Delta H per mole of propane

    def eq(c, o, co2, h2o, dh):
        return Thermo({"C3H8": c, "O2": o}, {"CO2": co2, "H2O": h2o}, dh)

    options = [eq(1, 5, 3, 4, 2220), eq(2, 10, 6, 8, -2220), eq(1, 5, 3, 4, -2220), eq(1, 4, 3, 4, -2220)]
    return [t.balanced() and t.dh == per_mol * (-t.coef["C3H8"]) for t in options]


def re_fuel_per_gram(item: dict) -> list[bool]:
    """q6: which fuel releases the LEAST heat per gram? (H = 1, C = 12, O = 16; Delta H per mole of fuel
    as the stem gives it.) Per gram = |Delta H| / M: C 394/12 = 32.8; C2H5OH 1370/46 = 29.8;
    C3H8 2220/44 = 50.5; CH4 890/16 = 55.6. Options in that order."""
    fuels = [("C", 394), ("C2H5OH", 1370), ("C3H8", 2220), ("CH4", 890)]
    per_gram = [Integer(dh) / molar_mass(f) for f, dh in fuels]
    least = min(per_gram)
    return [v == least for v in per_gram]


def re_concept_statements(item: dict) -> list[bool]:
    """q7: 2A(g) -> B(g), Delta H = -80 kJ (imaginary substances, as the stem says).
    (1) exothermic, and 1 mol B(g) has less energy than 2 mol A(g): E_p = E_r + Delta H < E_r.
    (2) 3 mol A releases 120 kJ: 3 x |Delta H| / coefficient of A.
    (3) if B(g) -> B(l) releases heat (Delta H_c = -c, c > 0), then 2A(g) -> B(l) releases less than 80 kJ:
        Delta H adds along the two steps, so it releases 80 + c, which is NOT less than 80.
    (4) run in a cup of water, the water warms: the surroundings gain -Delta H > 0.
    (5) breaking the reactant bonds absorbs more than forming the product bonds releases: in the bond
        picture Delta H = E_break - E_form, so E_break > E_form would need Delta H > 0."""
    eq = Thermo({"A": 2}, {"B": 1}, -80)
    e_r = sp.Symbol("E_r", real=True)
    s1 = kind(eq.dh) == "exo" and bool(e_r + eq.dh < e_r)
    s2 = kind(eq.dh) == "exo" and 3 * eq.heat_per_mole_of("A") == 120
    c = sp.Symbol("c", positive=True)  # the heat released on condensing 1 mol B, size unknown
    released_to_liquid = -(eq.dh + (-c))
    s3 = bool(released_to_liquid < 80)
    s4 = bool(-eq.dh > 0)
    e_form = sp.Symbol("E_form", positive=True)
    e_break = e_form + eq.dh
    s5 = bool(e_break > e_form)
    return [s1, s2, s3, s4, s5]


def re_hcl_reverse_half(item: dict) -> int:
    """q8: H2(g) + Cl2(g) -> 2HCl(g), Delta H = -184 kJ. HCl(g) -> 1/2 H2(g) + 1/2 Cl2(g) is the
    equation reversed and halved: Delta H = -184 x (-1/2) = +92 kJ; the stem writes '+①②'."""
    eq = Thermo({"H2": 1, "Cl2": 1}, {"HCl": 2}, -184)
    target = eq.scaled(Rational(-1, 2))
    assert target.coef["HCl"] == -1 and target.coef["H2"] == Rational(1, 2)
    assert target.dh > 0
    return int(target.dh)
