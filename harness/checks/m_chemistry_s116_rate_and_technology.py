"""Checks for src/data/items/chemistry/s116-rate-and-technology.yaml (116 sprint: CJe-Vc-2 surface area
and reaction rate, CMc-Vc-3 chemistry and advanced technology).

The chemistry is encoded as code, never read from the answer key:
- masses and rates are exact SymPy Rationals from the atomic masses stated in each stem;
- total product comes from the balanced equation and the amount of the solid only (the acid is stated to
  be in excess); the solid's shape does not enter that calculation;
- surface area of a cube cut into n pieces per edge is computed from the piece count and piece size, and
  the chapter's stated model (initial rate proportional to total contact area, other conditions equal)
  turns an area ratio into a rate ratio;
- average rate = change in amount / time, read from the data table in the stem;
- balancing solves the atom-count linear system (nullspace, smallest positive integers);
- a catalyst (MnO2, TiO2 photocatalyst) leaves the reaction with the same mass and identity, changes
  only how fast the product forms, never how much;
- carbon nanotube and photocatalyst statements come from a facts table, one source per fact.
Sources: 108課綱 自然領綱 附錄四 化學必修 CJe-Vc-2 / CMc-Vc-3 (surface area is the only rate factor in
必修; carbon nanotubes and TiO2 photocatalysts without structure), via the frozen research slice.
"""

from __future__ import annotations

from functools import reduce

import sympy as sp

R = sp.Rational
MASS = {"H": 1, "C": 12, "O": 16, "Ca": 40}  # atomic masses stated in the stems


def molar_mass(formula: dict[str, int]) -> sp.Rational:
    return sum(R(MASS[e]) * n for e, n in formula.items())


CACO3 = {"Ca": 1, "C": 1, "O": 3}
CO2 = {"C": 1, "O": 2}
H2O2 = {"H": 2, "O": 2}
O2 = {"O": 2}


def balance(reactants: list[dict[str, int]], products: list[dict[str, int]]) -> list[int]:
    """Smallest positive integer coefficients from atom conservation."""
    species = reactants + products
    sign = [1] * len(reactants) + [-1] * len(products)
    elements = sorted({e for s in species for e in s})
    m = sp.Matrix([[g * s.get(e, 0) for s, g in zip(species, sign)] for e in elements])
    null = m.nullspace()
    assert len(null) == 1
    v = null[0] * reduce(sp.ilcm, [x.q for x in null[0]], 1)
    g = reduce(sp.igcd, [int(x) for x in v])
    v = [int(x) // g for x in v]
    if v[0] < 0:
        v = [-x for x in v]
    assert all(x > 0 for x in v)
    return v


def co2_from_caco3(mass_caco3, shape: str) -> sp.Rational:
    """CaCO3 + 2HCl -> CaCl2 + H2O + CO2 with excess acid: total CO2 mass. Shape only changes the rate."""
    assert shape in ("lump", "powder")
    # balancing needs atom counts only (no mass for Cl is used)
    coef = balance([CACO3, {"H": 1, "Cl": 1}], [{"Ca": 1, "Cl": 2}, {"H": 2, "O": 1}, CO2])
    assert coef == [1, 2, 1, 1, 1]
    mol = R(mass_caco3) / molar_mass(CACO3)
    return mol * R(coef[4], coef[0]) * molar_mass(CO2)


def cube_area(edge, pieces_per_edge: int):
    """Total surface area after cutting a cube of the given edge into pieces_per_edge pieces per edge."""
    n = pieces_per_edge
    small = R(edge) / n
    return n**3 * 6 * small**2


def avg_rate(table: dict, t0, t1):
    return (R(table[t1]) - R(table[t0])) / (R(t1) - R(t0))


# ---- items --------------------------------------------------------------------------------------

def rt_turn_same_total(item):
    """5.00 g CaCO3 as lump vs powder, excess HCl: which gives more CO2 in the end?"""
    lump = co2_from_caco3(R(5), "lump")
    powder = co2_from_caco3(R(5), "powder")
    assert lump == R(11, 5)  # 2.20 g, as in the chapter
    # "cannot tell" would be right only if the total depended on something besides the CaCO3 mass;
    # test whether the total is the same function of the mass for every shape
    determined = all(co2_from_caco3(R(m), "lump") == co2_from_caco3(R(m), "powder") for m in (1, 3, 5, 7))
    return [powder > lump, lump > powder, lump == powder, not determined]


# Catalyst table (chapter: MnO2 in the H2O2 decomposition; TiO2 photocatalyst, CMc-Vc-3) and the rules for
# a catalyst (chapter, 催化劑 definition): it speeds the reaction up, and afterwards its own mass and
# identity are unchanged; it does not change how much product forms.
CATALYST = {"MnO2": {"role": "catalyst", "needs": None}, "TiO2": {"role": "catalyst", "needs": "light"}}
CATALYST_RULE = {"rate": "faster", "mass_change": 0, "identity_changes": False, "changes_total": False}


def after_reaction(name, mass_before):
    """(mass, identity) of an added substance after the reaction, from the catalyst table and rules."""
    if CATALYST[name]["role"] == "catalyst":
        identity = None if CATALYST_RULE["identity_changes"] else name
        return mass_before + CATALYST_RULE["mass_change"], identity
    raise ValueError(name)


def catalyst_after(name, mass_before):
    return after_reaction(name, mass_before)[0]


def rt_mid_tio2(item):
    """After a TiO2 photocatalyst breaks down organic dirt, what happens to the TiO2?"""
    before = R(1)
    after, identity_after = after_reaction("TiO2", before)
    return [
        after < before,                                   # used up, less of it
        after == before and identity_after == "TiO2",     # still there, unchanged, keeps working
        identity_after == "CO2+H2O",                      # all turned into CO2 and water
        identity_after == "dirt",                         # becomes part of the dirt
    ]


def rt_cube_3cm(item):
    """Cube of edge 3 cm cut into 1 cm cubes: total surface area in cm² (fill ①②③)."""
    a = cube_area(3, 3)
    assert a.is_integer and 100 <= a < 1000
    return int(a)


def rt_rate_ratio_4mm(item):
    """Same mass: one 4 mm cube vs 1 mm cubes. Initial rate ratio by the chapter's model (rate ∝ area)."""
    ratio = cube_area(4, 4) / cube_area(4, 1)
    return [ratio == r for r in (4, 16, 64, 1)]


# q3 data table (stated in the stem): CO2 mass released (g) at t minutes, 3.00 g CaCO3, excess HCl.
POWDER = {0: "0", 2: "0.88", 4: "1.21", 6: "1.32", 8: "1.32"}
LUMP = {0: "0", 2: "0.30", 4: "0.58", 6: "0.82", 8: "1.02"}


def rt_data_table(item):
    total = co2_from_caco3(R(3), "lump")  # 1.32 g, whatever the shape
    assert total == co2_from_caco3(R(3), "powder") == R(132, 100)
    powder_0_2 = avg_rate(POWDER, 0, 2)
    lump_0_2, lump_4_8 = avg_rate(LUMP, 0, 2), avg_rate(LUMP, 4, 8)
    caco3_used = R(POWDER[2]) / molar_mass(CO2) * molar_mass(CACO3)
    return [
        powder_0_2 == R(44, 100),           # powder, first 2 min: 0.44 g/min
        total == R(132, 100),               # the lump also ends at 1.32 g
        lump_4_8 > lump_0_2,                # lump faster in 4–8 min than in 0–2 min
        caco3_used == 2,                    # powder used 2.00 g CaCO3 in the first 2 min
        co2_from_caco3(R(3), "powder") > co2_from_caco3(R(3), "lump"),  # powder gives more in total
    ]


def rt_nano_100nm(item):
    """1 cm cube cut into 100 nm cubes: area grows by 10^k; k (fill ①)."""
    edge = R(1, 10**2)       # 1 cm in m
    piece = R(100, 10**9)    # 100 nm in m
    n = edge / piece
    assert n.is_integer
    ratio = cube_area(edge, int(n)) / cube_area(edge, 1)
    k = sp.log(ratio, 10)
    assert sp.simplify(10**k - ratio) == 0 and k.is_integer
    return int(k)


# q5 facts table. Each fact: source in the comment.
SUBSTANCES = {
    # elements making it up; structure label. 碳的同素異形體 diamond/graphite/graphene: chemistry/s116-chemical-bonds
    # (CAb-Vc). Carbon nanotube: carbon only, a rolled graphene layer (CMc-Vc-3, standard chemistry; 課綱 asks
    # no structure detail).
    "carbon nanotube": {"elements": {"C"}, "structure": "rolled layer"},
    "diamond": {"elements": {"C"}, "structure": "3D network"},
}
PHOTOCATALYST = {
    # TiO2 photocatalyst (CMc-Vc-3): a catalyst activated by light, mainly ultraviolet; not consumed.
    "TiO2": {"consumed": False, "light": "ultraviolet"},
}


def are_allotropes(a: str, b: str) -> bool:
    ea, eb = SUBSTANCES[a]["elements"], SUBSTANCES[b]["elements"]
    return len(ea) == 1 and ea == eb and SUBSTANCES[a]["structure"] != SUBSTANCES[b]["structure"]


def is_compound(name: str) -> bool:
    return len(SUBSTANCES[name]["elements"]) > 1


def rt_cnt_tio2_facts(item):
    cnt = SUBSTANCES["carbon nanotube"]
    return [
        cnt["elements"] == {"C"},                              # only carbon atoms
        are_allotropes("carbon nanotube", "diamond"),          # allotropes of diamond
        PHOTOCATALYST["TiO2"]["consumed"],                     # TiO2 used up, must be topped up
        PHOTOCATALYST["TiO2"]["light"] == "ultraviolet",       # works mainly with UV light
        is_compound("carbon nanotube"),                        # an ionic compound (needs ≥ 2 elements)
    ]


def rt_ethanol_sum(item):
    """C2H5OH + O2 -> CO2 + H2O, smallest integer coefficients: their sum (fill ①)."""
    coef = balance([{"C": 2, "H": 6, "O": 1}, O2], [CO2, {"H": 2, "O": 1}])
    s = sum(coef)
    assert 0 < s < 10
    return s


def rt_h2o2_mno2(item):
    """6.8 g H2O2 with 1.0 g MnO2 (H = 1, O = 16): 2H2O2 -> 2H2O + O2."""
    coef = balance([H2O2], [{"H": 2, "O": 1}, O2])
    assert coef == [2, 2, 1]
    o2 = R(68, 10) / molar_mass(H2O2) * R(coef[2], coef[0]) * molar_mass(O2)
    mno2 = R(1)

    def o2_total(catalyst_mass):
        # the total comes from H2O2 alone unless the catalyst rule said a catalyst changes the total
        assert not CATALYST_RULE["changes_total"]
        return o2

    speeds_up = CATALYST["MnO2"]["role"] == "catalyst" and CATALYST_RULE["rate"] == "faster"
    return [
        o2 == R(32, 10),                       # at most 3.2 g O2
        catalyst_after("MnO2", mno2) == R(1),  # 1.0 g MnO2 recovered
        o2_total(R(2)) == R(64, 10),           # 2.0 g MnO2 gives 6.4 g O2
        speeds_up,                             # MnO2 makes H2O2 decompose faster
        catalyst_after("MnO2", mno2) < mno2,   # MnO2 turns into part of the oxygen
    ]
