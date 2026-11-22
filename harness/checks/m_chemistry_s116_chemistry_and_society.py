"""Checks for src/data/items/chemistry/s116-chemistry-and-society.yaml (116 sprint: CMa-Vc-1, CMb-Vc-1,
CMb-Vc-2, CMc-Vc-1, CMc-Vc-2: water treatment, common medicines, scientists, the future of chemistry).

The chemistry is encoded as code, never read from the answer key:
- water treatment: each contaminant has the treatment steps that remove it (a table built from the
  property each step uses: settling by weight, filtering by size, adsorption on activated carbon,
  killing by an oxidising agent); what is left after some steps is computed from the table;
- disinfection: a step is a redox step when its reagent is one of the 課綱's oxidising agents
  (CJc-Vc-2 說明: O2, O3, H2O2, HOCl, Cl2); alum's Al3+ keeps its charge, so coagulation is not redox;
- softening: a particle model of a hard-water sample (Ca2+ paired with HCO3- or with Cl-) and what each
  method does to it (boiling removes only the Ca(HCO3)2 part; carbonate precipitates all; resin swaps
  one Ca2+ for two Na+; a filter or activated carbon leaves dissolved ions);
- antacids and precipitation: equations are balanced by solving the atom-count and charge linear
  system with SymPy; amounts use exact Rationals with the atomic masses stated in each stem;
- antacid suitability: a strong base (fully dissociated in water: NaOH, KOH, CJd-Vc-4 as taught in
  chemistry/s116-acids-bases) is unsuitable; the other bases are suitable;
- history: an explicit facts table, each fact with its source.
"""

from __future__ import annotations

from functools import reduce

import sympy as sp

# Atomic masses stated in the item stems.
MASS = {"H": 1, "C": 12, "O": 16, "Na": 23, "Mg": 24, "Al": 27, "Cl": sp.Rational(71, 2), "Ca": 40}

# Species as (atom counts, charge).
SP = {
    "H+": ({"H": 1}, 1), "H2O": ({"H": 2, "O": 1}, 0), "CO2": ({"C": 1, "O": 2}, 0),
    "Mg2+": ({"Mg": 1}, 2), "Al3+": ({"Al": 1}, 3), "Na+": ({"Na": 1}, 1), "Ca2+": ({"Ca": 1}, 2),
    "CO3^2-": ({"C": 1, "O": 3}, -2),
    "Mg(OH)2": ({"Mg": 1, "O": 2, "H": 2}, 0), "Al(OH)3": ({"Al": 1, "O": 3, "H": 3}, 0),
    "NaHCO3": ({"Na": 1, "H": 1, "C": 1, "O": 3}, 0), "CaCO3": ({"Ca": 1, "C": 1, "O": 3}, 0),
    "MgO": ({"Mg": 1, "O": 1}, 0), "Na2CO3": ({"Na": 2, "C": 1, "O": 3}, 0),
}


def molar_mass(name: str):
    atoms, _ = SP[name]
    return sum(MASS[a] * n for a, n in atoms.items())


def balance(reactants: list[str], products: list[str]) -> list[int]:
    """Smallest positive integer coefficients from atom counts and total charge."""
    names = reactants + products
    elems = sorted({a for n in names for a in SP[n][0]})
    sign = [1] * len(reactants) + [-1] * len(products)
    rows = [[s * SP[n][0].get(a, 0) for n, s in zip(names, sign)] for a in elems]
    rows.append([s * SP[n][1] for n, s in zip(names, sign)])
    null = sp.Matrix(rows).nullspace()
    assert len(null) == 1, (reactants, products)
    v = null[0] * reduce(sp.ilcm, [x.q for x in null[0]], 1)
    g = reduce(sp.igcd, [int(x) for x in v])
    v = [int(x) // g for x in v]
    if v[0] < 0:
        v = [-x for x in v]
    assert all(x > 0 for x in v)
    return v


# ---- water treatment ----------------------------------------------------------------------------

# Which steps remove each contaminant, from the property each step uses (chapter section 1):
# settling removes the heavy flocs that alum builds from silt; the sand filter holds back particles
# bigger than its gaps; activated carbon adsorbs odour and colour molecules; chlorine (an oxidiser)
# kills microbes. Dissolved ions are about the size of water molecules and are not oxidised away, so
# none of these steps removes them (softening, distillation or reverse osmosis would).
REMOVED_BY = {
    "silt": {"settle"},
    "fine particles": {"settle", "filter"},
    "odour molecules": {"carbon"},
    "bacteria": {"chlorine"},
    "dissolved ions": set(),
}


def may_remain(steps: set[str]) -> set[str]:
    return {c for c, by in REMOVED_BY.items() if not (by & steps)}


def cs_turn_clear_water(item):
    left = may_remain({"settle", "filter"})
    ions, germs = "dissolved ions" in left, "bacteria" in left
    return [ions and germs, not left, germs and not ions, ions and not germs]


OXIDISERS = {"O2", "O3", "H2O2", "HOCl", "Cl2"}  # CJc-Vc-2 說明
# step → (reagent or None for a purely physical step, charge of the reagent's metal before/after)
STEPS = {
    "alum": ("Al3+", (3, 3)),   # Al3+ → Al(OH)3: aluminium stays +3, so no electrons move
    "filter": (None, None),
    "carbon": (None, None),
    "chlorine": ("HOCl", None),  # Cl2 + H2O ⇌ HCl + HOCl; HOCl is a listed oxidiser
    "boil": (None, None),        # heat kills microbes; no reagent
}


def is_redox_step(step: str) -> bool:
    reagent, charges = STEPS[step]
    if reagent is None:
        return False
    if reagent in OXIDISERS:
        return True
    before, after = charges
    return before != after


def cs_which_step_redox(item):
    return [is_redox_step(s) for s in ("alum", "filter", "carbon", "chlorine", "boil")]


# ---- softening ----------------------------------------------------------------------------------

SAMPLE = {"Ca_with_HCO3": 2, "Ca_with_Cl": 3}  # the stem says the water holds both salts


def ca_left(method: str, sample: dict[str, int]) -> int:
    total = sample["Ca_with_HCO3"] + sample["Ca_with_Cl"]
    if method == "boil":          # Ca(HCO3)2 → CaCO3↓ + H2O + CO2↑ only
        return sample["Ca_with_Cl"]
    if method in ("carbonate", "resin"):
        return 0
    if method in ("filter", "carbon"):  # dissolved ions pass a filter and are not adsorbed
        return total
    raise ValueError(method)


def cs_softening_methods(item):
    start = SAMPLE["Ca_with_HCO3"] + SAMPLE["Ca_with_Cl"]
    return [ca_left(m, SAMPLE) < start for m in ("boil", "carbonate", "resin", "filter", "carbon")]


def cs_na2co3_mass(item):
    ca = sp.Rational(5, 1000)  # mol Ca2+ in the stem
    c = balance(["Ca2+", "CO3^2-"], ["CaCO3"])
    assert c == [1, 1, 1]
    n_na2co3 = ca * sp.Rational(c[1], c[0])  # one CO3^2- per Na2CO3
    mass = n_na2co3 * molar_mass("Na2CO3")   # 0.53 g
    cells = mass * 100
    assert cells.is_integer and 10 <= cells < 100
    return int(cells)


def cs_ppm_chlorine(item):
    """q8: 1.8 mg of Cl in about 3000 g of water; ppm = solute mass / solution mass × 10^6 = 0.6.
    The stem prints '0.①', so the blank is the tenths digit."""
    solute_g, solution_g = sp.Rational(18, 10) / 1000, 3000
    ppm = solute_g / solution_g * 10**6
    tenths = ppm * 10
    assert 0 < ppm < 1 and tenths.is_integer
    return int(tenths)


# ---- antacids -----------------------------------------------------------------------------------

ANTACID_ION = {"Mg(OH)2": "Mg2+", "Al(OH)3": "Al3+", "NaHCO3": "Na+", "CaCO3": "Ca2+", "MgO": "Mg2+"}


def neutralisation(antacid: str):
    """Products: the metal ion, water, and CO2 when the antacid contains carbon (a carbonate or
    hydrogencarbonate). Returns (products, coefficients) of the balanced equation with H+."""
    products = [ANTACID_ION[antacid], "H2O"]
    if "C" in SP[antacid][0]:
        products.append("CO2")
    return products, balance([antacid, "H+"], products)


def cs_antacid_co2(item):
    return ["CO2" in neutralisation(a)[0] for a in ("Mg(OH)2", "NaHCO3", "Al(OH)3", "CaCO3", "MgO")]


def cs_mgoh2_mmol(item):
    grams = sp.Rational(29, 100)
    _, c = neutralisation("Mg(OH)2")
    mmol = grams / molar_mass("Mg(OH)2") * sp.Rational(c[1], c[0]) * 1000
    assert mmol.is_integer and 10 <= mmol < 100
    return int(mmol)


STRONG_BASES = {"NaOH", "KOH"}  # fully dissociated in water (chemistry/s116-acids-bases)
BASES = {"Al(OH)3", "NaHCO3", "NaOH", "CaCO3", "Mg(OH)2"}  # all react with H+


def unsuitable_antacid(name: str) -> bool:
    return name not in BASES or name in STRONG_BASES


def cs_unsuitable_antacid(item):
    return [unsuitable_antacid(n) for n in ("Al(OH)3", "NaHCO3", "NaOH", "CaCO3", "Mg(OH)2")]


# ---- history ------------------------------------------------------------------------------------

FACTS = {
    # nat.json nat:CMb-Vc-1 keyConcepts: "Lavoisier: the element concept and oxidation; quantitative
    # check of mass conservation"
    ("Lavoisier", "mass conservation by weighing"),
    ("Lavoisier", "combustion is combining with oxygen"),
    # nat.json nat:CMb-Vc-1 keyConcepts: "Dalton's atomic theory"
    ("Dalton", "atomic theory"),
    # research slice (verification.corrections; 115 試卷 stem): Q44–46 used the 2023 Nobel Chemistry
    # topic, quantum dots
    ("Nobel Chemistry 2023", "quantum dots"),
}


def cs_history(item):
    claims = [
        ("Lavoisier", "mass conservation by weighing"),
        ("Dalton", "atomic theory"),
        ("Lavoisier", "atomic theory"),
        ("Nobel Chemistry 2023", "quantum dots"),
        ("Dalton", "combustion is combining with oxygen"),
    ]
    return [c in FACTS for c in claims]
