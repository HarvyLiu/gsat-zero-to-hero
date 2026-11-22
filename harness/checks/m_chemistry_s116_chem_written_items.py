"""Checks for src/data/items/chemistry/s116-chem-written-items.yaml (116 sprint, chemistry exam skills).

The chapter has no curriculum codes (chemistry.json: codes []): it practises reading inquiry 題組,
writing out working and reasons, and writing equations with the smallest whole-number coefficients.
Every function recomputes its item's answer from the chemistry in the stem; none reads item["answer"].

How the chemistry is encoded:
- formulas are parsed into atom counts (no brackets are needed in this bank); ion charges are given
  with each species;
- an equation is "correctly written" when every coefficient is a positive integer, atoms and charge
  balance, and the coefficients have no common factor (CJa-Vc-2; the 111 GSAT Q57-2 marking guide gave
  only partial points for fractional or doubled coefficients: research slice, confirmed_facts);
- unknown coefficients are found by solving the atom-count (and charge) linear system with SymPy
  (nullspace, scaled to the smallest positive integers);
- masses use the atomic masses stated in each stem, as exact Rationals;
- pH uses [H+][OH-] = 1.00e-14 at 25 °C (CJd-Vc-1 說明) and pH = -log[H+], with exact powers of ten;
- redox roles follow CJc-Vc-1/2: a unit whose charge rises loses electrons (is oxidised), one whose
  charge falls gains electrons (is reduced); free elements carry charge 0;
- inquiry variables are classified from an explicit description of the experiment.
"""

from __future__ import annotations

import re
from functools import reduce

import sympy as sp

# ---------------------------------------------------------------- formulas and equations


def atoms(formula: str) -> dict[str, int]:
    """Atom counts of a bracket-free formula such as C2H5OH or MnO4."""
    out: dict[str, int] = {}
    for sym, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        out[sym] = out.get(sym, 0) + (int(n) if n else 1)
    return out


def sp_(formula: str, charge: int = 0) -> tuple[dict[str, int], int]:
    return atoms(formula), charge


def _rows(species):
    elements = sorted({e for a, _ in species for e in a})
    return elements


def balanced(lhs, rhs, coeffs) -> bool:
    """Atoms and charge both conserved for the given coefficients (lhs then rhs)."""
    species = list(lhs) + list(rhs)
    sign = [1] * len(lhs) + [-1] * len(rhs)
    for e in _rows(species):
        if sum(s * c * a.get(e, 0) for (a, _), s, c in zip(species, sign, coeffs)) != 0:
            return False
    return sum(s * c * q for (_, q), s, c in zip(species, sign, coeffs)) == 0


def written_ok(lhs, rhs, coeffs) -> bool:
    """Balanced, all positive integers, and no common factor: the smallest whole-number form."""
    cs = [sp.nsimplify(c) for c in coeffs]
    if not all(c.is_integer and c > 0 for c in cs):
        return False
    if reduce(sp.igcd, [int(c) for c in cs]) != 1:
        return False
    return balanced(lhs, rhs, cs)


def balance(lhs, rhs) -> list[int]:
    """Smallest positive integer coefficients from the atom-count and charge linear system."""
    species = list(lhs) + list(rhs)
    sign = [1] * len(lhs) + [-1] * len(rhs)
    rows = [[s * a.get(e, 0) for (a, _), s in zip(species, sign)] for e in _rows(species)]
    rows.append([s * q for (_, q), s in zip(species, sign)])
    null = sp.Matrix(rows).nullspace()
    assert len(null) == 1, "the equation must have one balanced form"
    v = null[0]
    v = v * reduce(sp.ilcm, [sp.fraction(x)[1] for x in v])
    if v[0] < 0:
        v = -v
    g = reduce(sp.igcd, [int(x) for x in v])
    v = [int(x) // g for x in v]
    assert all(x > 0 for x in v)
    assert written_ok(lhs, rhs, v)
    return v


# Atomic masses as stated in the stems.
MASS = {"H": sp.Integer(1), "C": sp.Integer(12), "O": sp.Integer(16)}


def molar_mass(formula: str) -> sp.Rational:
    return sum(MASS[e] * n for e, n in atoms(formula).items())


# ---------------------------------------------------------------- items


def cw_turn_methane(item: dict) -> list[bool]:
    """q-turn: methane burns completely to CO2 and H2O. Which way of writing it uses the smallest
    whole-number coefficients? Options as coefficient sets for CH4, O2 -> CO2, H2O."""
    lhs = [sp_("CH4"), sp_("O2")]
    rhs = [sp_("CO2"), sp_("H2O")]
    half = sp.Rational(1, 2)
    opts = [(1, 1, 1, 1), (2, 4, 2, 4), (1, 2, 1, 2), (half, 1, half, 1)]
    return [written_ok(lhs, rhs, o) for o in opts]


# The worked inquiry (temperature and the solubility of solids 甲 and 乙): what the experimenter
# changes, measures and keeps the same, read off the stem's description.
SOLUBILITY_INQUIRY = {
    "changed": {"temperature"},
    "measured": {"mass dissolved"},
    "kept_same": {"mass of water (100 g each time)", "which solid", "stirring until no more dissolves"},
}


def _role(experiment: dict, quantity: str) -> str:
    if quantity in experiment["changed"]:
        return "manipulated"
    if quantity in experiment["measured"]:
        return "responding"
    if quantity in experiment["kept_same"]:
        return "controlled"
    return "unrelated"


def cw_mid_water_mass(item: dict) -> list[bool]:
    """q-mid: which kind of variable is 'take 100 g of water each time'?
    Options: manipulated, responding, controlled, unrelated (need not be fixed)."""
    got = _role(SOLUBILITY_INQUIRY, "mass of water (100 g each time)")
    return [got == r for r in ("manipulated", "responding", "controlled", "unrelated")]


def cw_crystals_from_table(item: dict) -> sp.Integer:
    """q1: solid 丙, solubility per 100 g water (stem table): 20 °C 30 g, 40 °C 45 g, 60 °C 70 g.
    50 g of water saturated at 60 °C is cooled to 20 °C. Mass of 丙 that crystallises (g)?
    A saturated solution holds exactly the solubility; the excess over the new solubility comes out."""
    table = {20: sp.Integer(30), 40: sp.Integer(45), 60: sp.Integer(70)}
    water = sp.Integer(50)
    dissolved_hot = table[60] * water / 100
    dissolved_cold = table[20] * water / 100
    crystals = dissolved_hot - dissolved_cold
    assert crystals.is_integer and crystals > 0
    return sp.Integer(crystals)


CONDUCTIVITY_INQUIRY = {
    "changed": {"molarity of the salt solution"},
    "measured": {"current"},
    "kept_same": {"electrodes", "power supply", "temperature", "volume of solution"},
}


def cw_conductivity_variables(item: dict) -> list[bool]:
    """q2: salt solutions of different molarity, same electrodes, same power supply, same temperature
    and volume; the current is measured. Which statements about the variables are right?"""
    claims = [
        ("molarity of the salt solution", "manipulated"),
        ("current", "responding"),
        ("temperature", "controlled"),
        ("electrodes", "manipulated"),
        ("molarity of the salt solution", "responding"),
    ]
    return [_role(CONDUCTIVITY_INQUIRY, q) == r for q, r in claims]


def cw_which_written_ok(item: dict) -> list[bool]:
    """q3: which equations are balanced AND written with the smallest whole-number coefficients?"""
    half = sp.Rational(1, 2)
    eqs = [
        ([sp_("H2O2")], [sp_("H2O"), sp_("O2")], (2, 2, 1)),
        ([sp_("N2"), sp_("H2")], [sp_("NH3")], (1, 1, 1)),
        ([sp_("C2H6"), sp_("O2")], [sp_("CO2"), sp_("H2O")], (2, 7, 4, 6)),
        ([sp_("Na"), sp_("O2")], [sp_("Na2O2")], (4, 2, 2)),
        ([sp_("Mg"), sp_("O2")], [sp_("MgO")], (1, half, 1)),
    ]
    return [written_ok(lhs, rhs, c) for lhs, rhs, c in eqs]


def cw_butane_oxygen(item: dict) -> sp.Integer:
    """q4: butane burns completely: C4H10 + O2 -> CO2 + H2O. Coefficient of O2 in the smallest
    whole-number form (the a = 1 solution has 13/2, so everything doubles)."""
    coeffs = balance([sp_("C4H10"), sp_("O2")], [sp_("CO2"), sp_("H2O")])
    return sp.Integer(coeffs[1])


def cw_propane_water_mass(item: dict) -> sp.Integer:
    """q5: 22 g of propane burns completely (H = 1, C = 12, O = 16). Mass of water formed (g)?
    Balance first, then moles -> mole ratio -> mass."""
    coeffs = balance([sp_("C3H8"), sp_("O2")], [sp_("CO2"), sp_("H2O")])
    n_propane = sp.Integer(22) / molar_mass("C3H8")
    n_water = n_propane * sp.Rational(coeffs[3], coeffs[0])
    mass = n_water * molar_mass("H2O")
    assert mass.is_integer
    return sp.Integer(mass)


def _ph(h: sp.Expr) -> sp.Expr:
    return sp.simplify(-sp.log(h, 10))


def cw_dilute_hcl(item: dict) -> list[bool]:
    """q6: 25 °C, hydrochloric acid of pH 1 is diluted with water to 1000 times its volume.
    The moles of H+ stay the same, so [H+] falls 1000-fold. Options: pH 2, 3, 4, 7, 9.
    (The acid's [H+] stays far above the 1e-7 M from water itself, so water's ions are ignored.)"""
    h_before = sp.Integer(10) ** -1
    h_after = h_before / 1000
    assert h_after > 100 * sp.Integer(10) ** -7
    ph = _ph(h_after)
    return [sp.simplify(ph - o) == 0 for o in (2, 3, 4, 7, 9)]


def _charge_per_atom(formula: str, charge: int) -> tuple[str, sp.Rational]:
    """Single-element species only: a free element (charge 0) or a monatomic ion."""
    a = atoms(formula)
    assert len(a) == 1
    (e, n), = a.items()
    return e, sp.Rational(charge, n)


def cw_chlorine_bromide(item: dict) -> list[bool]:
    """q7: Cl2 + 2Br- -> 2Cl- + Br2. Statements:
    (1) Cl2 is the oxidising agent; (2) Br- is oxidised; (3) 2 electrons move per Cl2 molecule;
    (4) the full name of the reaction type is 'oxidation reaction'; (5) Br2 is the oxidising agent."""
    lhs = [("Cl2", 0), ("Br", -1)]
    rhs = [("Cl", -1), ("Br2", 0)]
    coeffs = balance([sp_(f, q) for f, q in lhs], [sp_(f, q) for f, q in rhs])
    before = dict(_charge_per_atom(f, q) for f, q in lhs)
    after = dict(_charge_per_atom(f, q) for f, q in rhs)
    change = {e: after[e] - before[e] for e in before}
    oxidised = {e for e, d in change.items() if d > 0}
    reduced = {e for e, d in change.items() if d < 0}
    # reactant whose element is reduced = oxidising agent (always a reactant)
    oxidising_agent = next(f for f, _ in lhs if atoms(f).keys() & reduced)
    electrons_per_cl2 = -change["Cl"] * atoms("Cl2")["Cl"]
    rtype = "oxidation-reduction" if oxidised and reduced else ("oxidation" if oxidised else "reduction")
    # electrons lost equal electrons gained over the balanced equation
    lost = sum(change[e] * atoms(f)[e] * c for (f, _), c in zip(lhs, coeffs[:2]) for e in atoms(f) if e in oxidised)
    gained = -sum(change[e] * atoms(f)[e] * c for (f, _), c in zip(lhs, coeffs[:2]) for e in atoms(f) if e in reduced)
    assert lost == gained
    return [
        oxidising_agent == "Cl2",
        "Br" in oxidised,
        electrons_per_cl2 == 2,
        rtype == "oxidation",
        oxidising_agent == "Br2",
    ]


def cw_peroxide_iron_sum(item: dict) -> sp.Integer:
    """q8 (tested enrichment, 111 Q57-2 style): H2O2 + Fe2+ + H+ -> Fe3+ + H2O, balanced by atom and
    charge conservation. Sum of the smallest whole-number coefficients."""
    coeffs = balance(
        [sp_("H2O2"), sp_("Fe", 2), sp_("H", 1)],
        [sp_("Fe", 3), sp_("H2O")],
    )
    return sp.Integer(sum(coeffs))


# ---------------------------------------------------------------- worked examples (self-test only)


def _worked_examples() -> None:
    """Numbers used in the chapter text, recomputed so the prose and the harness agree."""
    # solubility of 甲: 24, 36, 56, 84 g per 100 g water at 20, 40, 60, 80 °C (S = 20 + T²/100)
    s = lambda t: 20 + sp.Rational(t * t, 100)
    assert [s(t) for t in (20, 40, 60, 80)] == [24, 36, 56, 84]
    assert s(80) - s(20) == 60 and s(60) == 56
    assert 2 * s(80) - 2 * s(20) == 120  # the Predict uses 200 g of water
    # 3.2 g CH4 -> CO2
    assert sp.Rational(32, 10) / molar_mass("CH4") * molar_mass("CO2") == sp.Rational(88, 10)
    # propane and acetylene
    assert balance([sp_("C3H8"), sp_("O2")], [sp_("CO2"), sp_("H2O")]) == [1, 5, 3, 4]
    assert balance([sp_("C2H2"), sp_("O2")], [sp_("CO2"), sp_("H2O")]) == [2, 5, 4, 2]
    # permanganate enrichment example: 1, 5, 8 -> 1, 5, 4
    assert balance(
        [sp_("MnO4", -1), sp_("Fe", 2), sp_("H", 1)], [sp_("Mn", 2), sp_("Fe", 3), sp_("H2O")]
    ) == [1, 5, 8, 1, 5, 4]
    # pH 11 NaOH diluted 100 times -> pH 9
    oh = sp.Integer(10) ** -14 / sp.Integer(10) ** -11 / 100
    assert _ph(sp.Integer(10) ** -14 / oh) == 9


_worked_examples()
