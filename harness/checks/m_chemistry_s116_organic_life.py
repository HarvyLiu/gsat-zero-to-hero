"""Checks for src/data/items/chemistry/s116-organic-life.yaml (116 sprint: CJf-Vc-1~3, biomolecules and
surfactants).

The chemistry is encoded as code, never read from the answer key:
- molecular formulas are parsed into atom counts; molecular weights are exact sums with the atomic
  masses each stem states (H = 1, C = 12, N = 14, O = 16, Na = 23);
- joining units by condensation is modelled as atom bookkeeping: n units minus (n − 1) H2O;
- the saponification equations are balanced by solving the atom-count linear system with SymPy
  (nullspace, scaled to the smallest positive integers);
- the composition of the four kinds of biomolecule (elements, building units, polymer or not, the parts
  of a nucleotide) is a small table, and every option is decided from it;
- surfactant behaviour is a rule on the parts of a molecule: a hydrocarbon part goes to the oil, a
  charged part to the water; a wrapped droplet's surface carries the charge of the outward ends, and
  like charges repel; a scum's formula comes from charge neutrality, with the metal ion's charge from
  its group (valence electrons, Z 1–18).
Sources: 108課綱 自然領綱 化學必修 CJf-Vc-1~3 as summarised in src/data/registry/codes/nat.json
(composition of carbohydrates, proteins, lipids and nucleic acids, no complex structures; soap and
detergent structure with an oil-loving and a water-loving end; how they remove dirt; surfactant lab)
and 國中 Jf-Ⅳ-1~4 (alkanes, alcohols, organic acids, esters, esterification and saponification).
The composition table is standard required-chemistry content within those limits.
"""

from __future__ import annotations

import re
from functools import reduce

import sympy as sp
from sympy import Integer

# Atomic masses as the stems state them.
AW = {"H": Integer(1), "C": Integer(12), "N": Integer(14), "O": Integer(16), "Na": Integer(23)}
# Atomic numbers, for the valence-electron rule (Z 1–18 only).
Z = {"H": 1, "C": 6, "N": 7, "O": 8, "Na": 11, "Mg": 12, "Ca": 20}


def parse(formula: str) -> dict[str, int]:
    """'C17H35COONa' → {'C': 18, 'H': 35, 'O': 2, 'Na': 1}; one level of brackets, e.g. 'C3H5(OH)3'."""
    def flat(s: str) -> dict[str, int]:
        out: dict[str, int] = {}
        pos = 0
        for m in re.finditer(r"([A-Z][a-z]?)(\d*)", s):
            assert m.start() == pos, s
            pos = m.end()
            out[m.group(1)] = out.get(m.group(1), 0) + (int(m.group(2)) if m.group(2) else 1)
        assert pos == len(s), s
        return out

    total: dict[str, int] = {}
    for m in re.finditer(r"\(([^()]*)\)(\d*)|([^()]+)", formula):
        part, k = (m.group(1), int(m.group(2) or 1)) if m.group(1) is not None else (m.group(3), 1)
        for e, n in flat(part).items():
            total[e] = total.get(e, 0) + n * k
    return total


def mw(formula: str) -> Integer:
    return sum((AW[e] * n for e, n in parse(formula).items()), Integer(0))


def condense(units: list[str]) -> dict[str, int]:
    """Atom counts of a chain of units joined in a row, one H2O removed at each of the len−1 joins."""
    total: dict[str, int] = {}
    for u in units:
        for e, n in parse(u).items():
            total[e] = total.get(e, 0) + n
    joins = len(units) - 1
    total["H"] -= 2 * joins
    total["O"] -= joins
    assert all(v > 0 for v in total.values())
    return total


def mass_of(counts: dict[str, int]) -> Integer:
    return sum((AW[e] * n for e, n in counts.items()), Integer(0))


def balance(reactants: list[str], products: list[str]) -> list[int]:
    """Smallest positive integer coefficients that conserve every kind of atom."""
    names = reactants + products
    elems = sorted({e for n in names for e in parse(n)})
    sign = [1] * len(reactants) + [-1] * len(products)
    rows = [[s * parse(n).get(e, 0) for n, s in zip(names, sign)] for e in elems]
    null = sp.Matrix(rows).nullspace()
    assert len(null) == 1, (reactants, products)
    v = null[0] * reduce(sp.ilcm, [x.q for x in null[0]], 1)
    g = reduce(sp.igcd, [int(x) for x in v])
    v = [int(x) // g for x in v]
    if v[0] < 0:
        v = [-x for x in v]
    assert all(x > 0 for x in v)
    return v


# ---- composition table (CJf-Vc: composition only, no structures) --------------------------------
ELEMENTS = {  # elements every member of the class contains (some proteins also contain S)
    "carbohydrate": {"C", "H", "O"},
    "protein": {"C", "H", "O", "N"},
    "fat": {"C", "H", "O"},
    "nucleic acid": {"C", "H", "O", "N", "P"},
    "hydrocarbon": {"C", "H"},
}
CLASS_OF = {"starch": "carbohydrate", "sucrose": "carbohydrate", "glucose": "carbohydrate",
            "cellulose": "carbohydrate", "egg-white protein": "protein", "butter fat": "fat",
            "fat": "fat", "DNA": "nucleic acid", "RNA": "nucleic acid", "methane": "hydrocarbon"}
# What complete hydrolysis gives, and whether the substance is a polymer (a long chain of many units).
UNITS = {"starch": {"glucose"}, "cellulose": {"glucose"}, "sucrose": {"glucose", "fructose"},
         "protein": {"amino acid"}, "DNA": {"nucleotide"}, "RNA": {"nucleotide"},
         "fat": {"glycerol", "fatty acid"}}
POLYMER = {"starch": True, "cellulose": True, "protein": True, "DNA": True, "RNA": True,
           "sucrose": False, "glucose": False, "fat": False}
NUCLEOTIDE = {"DNA": {"phosphate", "deoxyribose", "base"}, "RNA": {"phosphate", "ribose", "base"}}
SUGARS = {"deoxyribose", "ribose", "glucose", "fructose"}
UNIT_ELEMENTS = {"amino acid": ELEMENTS["protein"]}  # an amino acid has -NH2 and -COOH: C, H, O, N


def q_turn_nitrogen(item):
    """Starch, protein, fat: which always contains N; option 4 = none of them."""
    has = [("N" in ELEMENTS[CLASS_OF[s]]) for s in ("starch", "egg-white protein", "butter fat")]
    return has + [not any(has)]


def q1_only_cho(item):
    """Which could be a sample whose analysis finds exactly C, H and O."""
    return [ELEMENTS[CLASS_OF[s]] == {"C", "H", "O"}
            for s in ("starch", "sucrose", "fat", "egg-white protein", "methane")]


def q2_chain_units(item):
    """A glucose chain (C6H12O6 units, H = 1, C = 12, O = 16) has molecular weight 1638: how many units?
    Searches the chain length whose condensed formula has that mass; it must be unique."""
    hits = [n for n in range(1, 101) if mass_of(condense(["C6H12O6"] * n)) == 1638]
    assert len(hits) == 1
    return hits[0]


def q3_composition(item):
    """(1) every product of protein hydrolysis contains N; (2) DNA and RNA nucleotides have different
    sugars; (3) DNA's sugar is glucose; (4) fat is a polymer; (5) starch hydrolysis gives one sugar."""
    dna_sugar = NUCLEOTIDE["DNA"] & SUGARS
    rna_sugar = NUCLEOTIDE["RNA"] & SUGARS
    return [
        all("N" in UNIT_ELEMENTS[u] for u in UNITS["protein"]),
        dna_sugar != rna_sugar,
        dna_sugar == {"glucose"},
        POLYMER["fat"],
        len(UNITS["starch"] & SUGARS) == 1 and UNITS["starch"] <= SUGARS,
    ]


def q4_dipeptide(item):
    """Glycine C2H5NO2 + alanine C3H7NO2 joined by one peptide bond: molecular weight (N = 14)."""
    return int(mass_of(condense(["C2H5NO2", "C3H7NO2"])))


TRIPALMITIN, PALMITATE = "C51H98O6", "C15H31COONa"
TRIOLEIN, OLEATE = "C57H104O6", "C17H33COONa"
GLYCEROL = "C3H5(OH)3"


def q5_naoh_mass(item):
    """0.25 mol of glyceryl tripalmitate saponified completely: grams of NaOH (Na = 23)."""
    a, b, c, d = balance([TRIPALMITIN, "NaOH"], [PALMITATE, GLYCEROL])
    g = sp.Rational(1, 4) * sp.Rational(b, a) * mw("NaOH")
    assert g.is_integer
    return int(g)


def q6_soap_mass(item):
    """884 g of glyceryl trioleate saponified completely: grams of sodium oleate formed."""
    a, b, c, d = balance([TRIOLEIN, "NaOH"], [OLEATE, GLYCEROL])
    mol_fat = Integer(884) / mw(TRIOLEIN)
    g = mol_fat * sp.Rational(c, a) * mw(OLEATE)
    assert g.is_integer
    return int(g)


# ---- surfactants -------------------------------------------------------------------------------
def affinity(part: dict) -> str:
    """A hydrocarbon part stays with oil (like mixes with like); a charged part is surrounded by water."""
    return "water" if part["charge"] != 0 else "oil"


SOAP = {"chain": {"kind": "hydrocarbon", "charge": 0}, "head": {"kind": "COO-", "charge": -1}}
DETERGENT = {"chain": {"kind": "hydrocarbon with benzene ring", "charge": 0},
             "head": {"kind": "SO3-", "charge": -1}}
COUNTERION_ATTACHED_IN_WATER = False  # Na+ separates from the anion in water (an ionic compound dissolving)


def q_mid_arrangement(item):
    """How soap molecules line up on an oil drop: each part goes to the phase it loves."""
    want = {p: affinity(SOAP[p]) for p in SOAP}
    options = [{"chain": "oil", "head": "water"}, {"chain": "water", "head": "oil"},
               {"chain": "oil", "head": "oil"}, {"chain": "oil", "head": "oil"}]
    return [o == want for o in options]


def q7_surfactant(item):
    """(1) the long chain is oil-loving; (2) the water-loving end goes into the drop; (3) wrapped drops
    are negatively charged and repel; (4) a detergent has no oil-loving end; (5) Na+ is attached to the
    chain in water as the water-loving end."""
    surface_charge = SOAP["head"]["charge"]  # heads face outwards, into the water
    repel = surface_charge * surface_charge > 0  # two drops carry the same sign
    return [
        affinity(SOAP["chain"]) == "oil",
        affinity(SOAP["head"]) == "oil",
        surface_charge < 0 and repel,
        not any(affinity(p) == "oil" for p in DETERGENT.values()),
        COUNTERION_ATTACHED_IN_WATER,
    ]


def metal_charge(sym: str) -> int:
    z = Z[sym]
    assert z <= 18, sym
    return z if z <= 2 else (z - 2 if z <= 10 else z - 10)  # group 1, 2 metals lose all valence electrons


def q8_mg_scum(item):
    """Formula of the scum from Mg2+ and the soap anion C17H35COO− (charge −1): (metal, anion) counts."""
    q_metal, q_anion = metal_charge("Mg"), SOAP["head"]["charge"]
    options = [(1, 2), (1, 1), (2, 1), (1, 3)]  # Mg(A)2, MgA, Mg2A, Mg(A)3
    return [m * q_metal + n * q_anion == 0 and sp.igcd(m, n) == 1 for m, n in options]
