"""Checks for src/data/items/chemistry/s116-redox.yaml (116 sprint: CJc-Vc-1, CJc-Vc-2, oxidation and
reduction).

The chemistry is encoded as code, never read from the answer key:
- every species is written as units (atoms, or a polyatomic ion that stays intact such as NO3-) with
  counts; the charge carried by each unit is DERIVED: 0 in a free element, the written charge in an ion,
  and in an ionic compound the anion charges come from the valence-electron rule (Z 1~18: a nonmetal
  gains 8 − valence electrons) or from the stem (NO3- = −1), and the metal's charge from neutrality;
- equations are balanced by solving the unit-count and charge-conservation linear system with SymPy
  (nullspace, scaled to the smallest positive integers);
- a unit that loses electrons (its charge goes up) is oxidized, one that gains electrons is reduced;
  the oxidizing agent is the reactant whose unit is reduced, the reducing agent the one that is oxidized;
- an antioxidant is modelled by competition: the electron acceptor takes electrons from the donor that
  loses them most easily first (the stem states the order and every amount).
Sources: 108課綱 自然領綱 附錄四 化學必修 CJc-Vc-1/2 (broad definition by electron transfer; oxidizers
O2, O3, H2O2, HOCl, Cl2; reducers coke, SO2; antioxidant vitamin C; no 氧化數). Atom and charge
balancing of ionic equations is tested enrichment (111 學測 Q57-2, CEEC 評分原則), done here by CJa-Vc-2
algebra only.
"""

from __future__ import annotations

from functools import reduce

import sympy as sp

# Atomic numbers (standard periodic table); valence electrons are used only for Z = 1–18.
Z = {"H": 1, "C": 6, "O": 8, "Na": 11, "Mg": 12, "Al": 13, "S": 16, "Cl": 17,
     "Mn": 25, "Fe": 26, "Cu": 29, "Zn": 30, "Ag": 47}
NONMETALS = {"H", "C", "O", "S", "Cl"}
GIVEN_ANION_CHARGE = {"NO3": -1}  # stated in the stem; polyatomic, kept intact


def valence(sym: str) -> int:
    z = Z[sym]
    assert z <= 18, sym
    return z if z <= 2 else (z - 2 if z <= 10 else z - 10)


def anion_charge(unit: str) -> int:
    if unit in GIVEN_ANION_CHARGE:
        return GIVEN_ANION_CHARGE[unit]
    assert unit in NONMETALS and unit != "H"
    return -(8 - valence(unit))  # O → −2, Cl → −1, S → −2


class Species:
    """units: {unit: count}; charge: the species' total charge; kind: element / ion / salt."""

    def __init__(self, units: dict[str, int], charge: int = 0, kind: str = "element"):
        self.units, self.charge, self.kind = units, charge, kind

    def unit_charges(self) -> dict[str, sp.Rational]:
        if self.kind == "element":
            assert len(self.units) == 1 and self.charge == 0
            return {u: sp.Integer(0) for u in self.units}
        if self.kind == "ion":
            assert len(self.units) == 1
            (u, n), = self.units.items()
            return {u: sp.Rational(self.charge, n)}
        # ionic compound: one metal (cation) unit, the rest anions with known charges; total charge 0
        anions = {u: anion_charge(u) for u in self.units if u in NONMETALS or u in GIVEN_ANION_CHARGE}
        metals = [u for u in self.units if u not in anions]
        assert len(metals) == 1 and self.charge == 0
        m = metals[0]
        q = sp.Rational(-sum(anions[u] * self.units[u] for u in anions), self.units[m])
        assert q.is_integer and q > 0
        return {m: q, **{u: sp.Integer(c) for u, c in anions.items()}}


def el(sym: str, n: int = 1) -> Species:
    return Species({sym: n})


def ion(unit: str, charge: int, n: int = 1) -> Species:
    return Species({unit: n}, charge, "ion")


def salt(**units: int) -> Species:
    return Species(dict(units), 0, "salt")


SP = {
    "Mg": el("Mg"), "Na": el("Na"), "Al": el("Al"), "Fe": el("Fe"), "Cu": el("Cu"), "Zn": el("Zn"),
    "Ag": el("Ag"), "O2": el("O", 2), "Cl2": el("Cl", 2), "H2": el("H", 2), "S": el("S"),
    "H+": ion("H", 1), "Cl-": ion("Cl", -1), "O2-": ion("O", -2), "S2-": ion("S", -2),
    "Na+": ion("Na", 1), "Mg2+": ion("Mg", 2), "Al3+": ion("Al", 3), "Cu2+": ion("Cu", 2),
    "Zn2+": ion("Zn", 2), "Fe2+": ion("Fe", 2), "Fe3+": ion("Fe", 3), "Ag+": ion("Ag", 1),
    "NaCl": salt(Na=1, Cl=1), "MgCl2": salt(Mg=1, Cl=2), "AgCl": salt(Ag=1, Cl=1),
    "Fe2O3": salt(Fe=2, O=3), "Al2O3": salt(Al=2, O=3), "MgO": salt(Mg=1, O=1),
    "AgNO3": salt(Ag=1, NO3=1), "Cu(NO3)2": salt(Cu=1, NO3=2), "Zn(NO3)2": salt(Zn=1, NO3=2),
    "Mn": el("Mn"), "MnO2": salt(Mn=1, O=2),
}


def balance(reactants: list[str], products: list[str]) -> list[int]:
    """Smallest positive integer coefficients from unit counts and total charge."""
    names = reactants + products
    units = sorted({u for n in names for u in SP[n].units})
    sign = [1] * len(reactants) + [-1] * len(products)
    rows = [[s * SP[n].units.get(u, 0) for n, s in zip(names, sign)] for u in units]
    rows.append([s * SP[n].charge for n, s in zip(names, sign)])
    null = sp.Matrix(rows).nullspace()
    assert len(null) == 1, (reactants, products)  # a unique ratio
    v = null[0]
    lcm = reduce(sp.ilcm, [x.q for x in v], 1)
    v = v * lcm
    g = reduce(sp.igcd, [int(x) for x in v])
    v = [int(x) // g for x in v]
    if v[0] < 0:
        v = [-x for x in v]
    assert all(x > 0 for x in v)
    return v


def charge_on_side(names: list[str], unit: str):
    qs = {SP[n].unit_charges()[unit] for n in names if unit in SP[n].units}
    assert len(qs) <= 1, (unit, qs)  # one charge per unit on each side
    return qs.pop() if qs else None


def changes(reactants: list[str], products: list[str]) -> dict[str, sp.Rational]:
    """Per-unit charge change (after − before): > 0 means electrons lost (oxidized), < 0 gained."""
    units = {u for n in reactants for u in SP[n].units}
    return {u: charge_on_side(products, u) - charge_on_side(reactants, u) for u in units}


def electrons_moved(reactants: list[str], products: list[str]):
    """(electrons lost, electrons gained) in the balanced equation; they must be equal."""
    coef = balance(reactants, products)
    ch = changes(reactants, products)
    lost = gained = 0
    for n, c in zip(reactants, coef):
        for u, k in SP[n].units.items():
            d = ch[u] * k * c
            if d > 0:
                lost += d
            else:
                gained -= d
    assert lost == gained  # electrons are only moved, never created
    return lost, gained


def is_redox(reactants: list[str], products: list[str]) -> bool:
    return any(d != 0 for d in changes(reactants, products).values())


def oxidizing_agents(reactants, products) -> set[str]:
    ch = changes(reactants, products)
    return {n for n in reactants if any(ch[u] < 0 for u in SP[n].units)}


def reducing_agents(reactants, products) -> set[str]:
    ch = changes(reactants, products)
    return {n for n in reactants if any(ch[u] > 0 for u in SP[n].units)}


# ---- items --------------------------------------------------------------------------------------

def redox_turn_na_cl2(item):
    """2Na + Cl2 -> 2NaCl: redox although no oxygen takes part."""
    r, p = ["Na", "Cl2"], ["NaCl"]
    ch = changes(r, p)
    lost = any(d > 0 for d in ch.values())
    gained = any(d < 0 for d in ch.values())
    red = is_redox(r, p)
    na_loses, cl_gains = ch["Na"] > 0, ch["Cl"] < 0
    return [red and na_loses and cl_gains, not red, lost and not gained, gained and not lost]


def redox_mid_fe_cu(item):
    """Fe + Cu2+ -> Fe2+ + Cu: which species is the oxidizing agent?"""
    r, p = ["Fe", "Cu2+"], ["Fe2+", "Cu"]
    ox = oxidizing_agents(r, p)
    return [s in ox for s in ("Fe", "Cu2+", "Fe2+", "Cu")]


def redox_which_is_oxidation(item):
    """Which change is an oxidation (electrons lost)? Each option is one species turning into another."""
    pairs = [("Fe2+", "Fe3+"), ("Cl2", "Cl-"), ("Cu2+", "Cu"), ("O2", "O2-"), ("S", "S2-")]
    out = []
    for a, b in pairs:
        (u,) = SP[a].units
        d = SP[b].unit_charges()[u] - SP[a].unit_charges()[u]
        out.append(d > 0)
    return out


def redox_mg_acid(item):
    """Mg + 2H+ -> Mg2+ + H2: statements about who is oxidized and the oxidizing agent."""
    r, p = ["Mg", "H+"], ["Mg2+", "H2"]
    assert balance(r, p) == [1, 2, 1, 1]
    ch = changes(r, p)
    ox, rd = oxidizing_agents(r, p), reducing_agents(r, p)
    return [
        ch["Mg"] > 0,          # Mg is oxidized
        "H+" in ox,            # H+ is the oxidizing agent
        "Mg" in ox,            # Mg is the oxidizing agent
        ch["Mg"] == 2,         # each Mg atom loses 2 electrons
        "H+" in rd,            # H+ is oxidized
    ]


def redox_al_acid_sum(item):
    """Al + H+ -> Al3+ + H2, smallest integer coefficients by atoms and charge: their sum."""
    return sum(balance(["Al", "H+"], ["Al3+", "H2"]))


# q4: an antioxidant competing with a food substance for the electrons oxygen takes (CJc-Vc-2 說明:
# 抗氧化劑 維生素C). The stem gives every number: O2 can accept 6 portions of electrons; vitamin C can
# give 4, substance X can give 10; vitamin C loses electrons more easily (rank 1) than X (rank 2), so
# the acceptor takes from the easier donor first and from the next one only for the shortfall.
O2_CAPACITY = 6
DONOR_CAPACITY = {"vitamin C": 4, "X": 10}
EASE_RANK = {"vitamin C": 1, "X": 2}  # 1 = loses electrons most easily


def share_electrons(acceptor_capacity: int, donor_capacity: dict[str, int]) -> dict[str, int]:
    """Portions of electrons each donor hands to the acceptor, easiest donor first."""
    given, need = {}, acceptor_capacity
    for d in sorted(donor_capacity, key=EASE_RANK.__getitem__):
        given[d] = min(need, donor_capacity[d])
        need -= given[d]
    return given


def redox_vitamin_c(item):
    """Vitamin C (4 portions) and X (10 portions) both able to give electrons to O2 (accepts 6).
    (1) all vitamin C oxidized; (2) none of X oxidized; (3) vitamin C acts as a reducing agent (it gives
    electrons); (4) with 8 portions of vitamin C, none of X is oxidized; (5) O2 loses electrons."""
    given = share_electrons(O2_CAPACITY, DONOR_CAPACITY)
    lost = {**given, "O2": 0}           # donors lose what they give; the acceptor loses none
    gained = {"O2": sum(given.values())}
    assert gained["O2"] == O2_CAPACITY  # enough donors in total to fill the acceptor
    role_vc = "reducer" if lost["vitamin C"] > 0 else "oxidizer" if gained.get("vitamin C", 0) else "none"
    more_vc = share_electrons(O2_CAPACITY, {**DONOR_CAPACITY, "vitamin C": 8})
    return [
        given["vitamin C"] == DONOR_CAPACITY["vitamin C"],  # all of the vitamin C is oxidized
        given["X"] == 0,                                     # none of X is oxidized
        role_vc == "reducer",                                # vitamin C is the reducing agent
        more_vc["X"] == 0,                                   # 8 portions of vitamin C spare X entirely
        lost["O2"] > 0,                                      # O2 loses electrons
    ]


def redox_thermite_electrons(item):
    """4Al + 3MnO2 -> 3Mn + 2Al2O3 (oxide oxygen taken as O2-, as the stem says): electrons transferred
    in the equation as written. Mn's charge in MnO2 comes from neutrality: x + 2(-2) = 0."""
    r, p = ["Al", "MnO2"], ["Mn", "Al2O3"]
    assert balance(r, p) == [4, 3, 3, 2]
    lost, _ = electrons_moved(r, p)
    assert lost.is_integer and 10 <= lost < 100
    return (int(lost) // 10, int(lost) % 10)


def redox_not_redox(item):
    """Which reaction is NOT a redox reaction?"""
    reactions = [
        (["Mg", "Cl2"], ["MgCl2"]),
        (["Zn", "H+"], ["Zn2+", "H2"]),
        (["Ag+", "Cl-"], ["AgCl"]),
        (["Fe", "Ag+"], ["Fe2+", "Ag"]),
    ]
    return [not is_redox(r, p) for r, p in reactions]


def redox_zn_silver_nitrate(item):
    """Zn + AgNO3 -> Zn(NO3)2 + Ag (NO3- given as −1): statements."""
    r, p = ["Zn", "AgNO3"], ["Zn(NO3)2", "Ag"]
    coef = balance(r, p)
    ch = changes(r, p)
    ox = oxidizing_agents(r, p)
    # net ionic form: units whose charge does not change are left out
    net = balance(["Zn", "Ag+"], ["Zn2+", "Ag"])
    return [
        ch["Zn"] > 0,                # zinc is oxidized
        "AgNO3" in ox and ch["Ag"] < 0 and ch["NO3"] == 0,  # Ag+ (not nitrate) is the oxidizing agent
        net[1] == 2 and coef[1] == 2,  # Ag+ coefficient 2 in the smallest integer equation
        -ch["Ag"] == 2,              # each Ag formed takes 2 electrons
        ch["NO3"] < 0,               # nitrate gains electrons
    ]
