"""Checks for src/data/items/chemistry/s116-chemical-bonds.yaml (116 sprint: CAb-Vc-3, CCa-Vc-2,
CCb-Vc-1, CCb-Vc-2, chemical bonds and the properties of substances).

The chemistry is encoded as code, never read from the answer key:
- valence electrons for Z = 1–18 from the atomic number (the 必修 limit: Z 1~18 only);
- Lewis structures by the octet rule (H needs 2, every other atom here needs 8): bond orders are found by
  searching every assignment of single/double/triple bonds on the given skeleton, and must be unique;
- the counting shortcut "shared pairs = (electrons needed − valence electrons) / 2" with exact Rationals;
- bonding types and properties from a small model table (ionic / molecular / covalent network / metal),
  with a decision rule that classifies a substance from its properties;
- network-solid formulas from neighbour counting (each shared neighbour counts 1/n).
Sources: 108課綱 自然領綱 附錄四 化學必修 (Lewis structures of H2O, NH3, CH4, C2H4, CO2 only; ionic bonding
with NaCl/MgO; electron-sea model; carbon allotropes and Si network solids; valence electrons Z 1~18).
"""

from __future__ import annotations

from itertools import product

import re

import sympy as sp

SYMBOL_Z = {"H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
            "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18}
# Metals among Z = 1–18 (Li, Be, Na, Mg, Al); everything else used here is a nonmetal or metalloid (Si).
METALS = {"Li", "Be", "Na", "Mg", "Al"}
NOBLE_ELECTRONS = (2, 10, 18)  # He, Ne, Ar


def valence(symbol: str) -> int:
    """Valence electrons for Z = 1–18: the electrons beyond the previous noble gas (H 1 … Cl 7)."""
    z = SYMBOL_Z[symbol]
    assert z <= 18 and symbol not in ("He", "Ne", "Ar")
    return z if z <= 2 else (z - 2 if z <= 10 else z - 10)


def full_shell(symbol: str) -> int:
    """Octet rule: H needs 2 electrons around it (like He); the other atoms here need 8."""
    return 2 if symbol == "H" else 8


# Skeletons (which atoms are joined) for the five 必修 molecules; bond orders are NOT given.
SKELETONS = {
    "H2O": (["O", "H", "H"], [(0, 1), (0, 2)]),
    "NH3": (["N", "H", "H", "H"], [(0, 1), (0, 2), (0, 3)]),
    "CH4": (["C", "H", "H", "H", "H"], [(0, 1), (0, 2), (0, 3), (0, 4)]),
    "C2H4": (["C", "C", "H", "H", "H", "H"], [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5)]),
    "CO2": (["C", "O", "O"], [(0, 1), (0, 2)]),
}


def lewis(mol: str):
    """Unique (bond orders, lone pairs per atom) that give every atom a full shell."""
    atoms, links = SKELETONS[mol]
    found = []
    for orders in product((1, 2, 3), repeat=len(links)):
        used = [0] * len(atoms)
        for (a, b), o in zip(links, orders):
            used[a] += o
            used[b] += o
        ok, lone = True, []
        for i, el in enumerate(atoms):
            left = valence(el) - used[i]  # valence electrons not put into bonds
            if left < 0 or left % 2:
                ok = False
                break
            if 2 * used[i] + left != full_shell(el):  # each bond pair counts 2 around the atom
                ok = False
                break
            lone.append(left // 2)
        if ok:
            found.append((orders, lone))
    assert len(found) == 1, (mol, found)
    return found[0]


def shared_pairs_by_counting(mol: str) -> sp.Rational:
    """Shortcut: (electrons needed − valence electrons) / 2."""
    atoms, _ = SKELETONS[mol]
    need = sum(full_shell(a) for a in atoms)
    have = sum(valence(a) for a in atoms)
    return sp.Rational(need - have, 2)


def _shared_pairs(mol: str) -> int:
    orders, _ = lewis(mol)
    s = sum(orders)
    assert shared_pairs_by_counting(mol) == s  # both methods must agree
    return s


# ---- bonding model --------------------------------------------------------------------------------
# kind: ionic / molecular / network / metal. Properties follow the 必修 comparison of ionic compounds,
# molecular compounds, covalent network solids and metals.
SUBSTANCES = {
    "NaCl": {"kind": "ionic", "elements": {"Na", "Cl"}},
    "MgO": {"kind": "ionic", "elements": {"Mg", "O"}},
    "sugar": {"kind": "molecular", "elements": {"C", "H", "O"}, "ionizes_in_water": False},
    "CO2": {"kind": "molecular", "elements": {"C", "O"}, "ionizes_in_water": False},
    "SiO2": {"kind": "network", "elements": {"Si", "O"}},
    "diamond": {"kind": "network", "elements": {"C"}, "neighbours": 4, "structure": "3D network"},
    "graphite": {"kind": "network", "elements": {"C"}, "neighbours": 3, "structure": "layers"},
    "Si": {"kind": "network", "elements": {"Si"}, "neighbours": 4, "structure": "3D network"},
}


def bond_type(elements: set[str]) -> str:
    """Metal + nonmetal → ionic; nonmetals only → covalent; one metal alone → metallic."""
    metals = elements & METALS
    if metals and elements - METALS:
        return "ionic"
    if metals:
        return "metallic"
    return "covalent"


def mobile_charges(kind: str, state: str, ionizes_in_water: bool = False) -> bool:
    """Are there charged particles free to move? state: solid / molten / aqueous."""
    if kind == "metal":
        return True  # the electron sea moves in solid and liquid metal
    if kind == "ionic":
        return state in ("molten", "aqueous")  # ions are fixed in the solid, free once melted or dissolved
    if kind == "molecular":
        return state == "aqueous" and ionizes_in_water
    return False  # network solids (graphite, with its free electrons, is handled by free_electrons)


def free_electrons_per_atom(name: str) -> int:
    s = SUBSTANCES[name]
    (el,) = s["elements"]
    return valence(el) - s["neighbours"]  # one single bond per neighbour


def classify(conducts_solid: bool, conducts_melt_or_aq: bool, high_mp: bool, malleable: bool) -> str:
    """Decision steps taught in the chapter."""
    if conducts_solid:
        return "metal" if malleable else "network"  # conducting but brittle: think of graphite
    if conducts_melt_or_aq:
        return "ionic"
    return "network" if high_mp else "molecular"


# ---- item checks -----------------------------------------------------------------------------------

def bonds_turn_salt_sugar(item):
    """q-turn: which aqueous solution lights the bulb? Options: only salt, only sugar, both, neither."""
    salt = mobile_charges(SUBSTANCES["NaCl"]["kind"], "aqueous")
    sugar = mobile_charges(SUBSTANCES["sugar"]["kind"], "aqueous", SUBSTANCES["sugar"]["ionizes_in_water"])
    return [salt and not sugar, sugar and not salt, salt and sugar, not salt and not sugar]


def bonds_broken_on_melting(kind: str) -> str:
    """Which bonds must break to melt (or sublime) a solid of this kind. A molecular solid only has its
    molecules pulled apart (the attraction between molecules), so no bond inside a molecule breaks; a
    network solid has to break covalent bonds; an ionic solid has to free its ions from ionic bonds."""
    return {"molecular": "none", "network": "covalent", "ionic": "ionic", "metal": "none"}[kind]


def bonds_mid_co2_sio2(item):
    """q-mid: why dry ice sublimes but quartz is hard with a high melting point."""
    co2, sio2 = SUBSTANCES["CO2"], SUBSTANCES["SiO2"]
    return [
        # (A) "heavier Si makes it harder": refuted by diamond, a hard network solid of the lighter C atom
        SUBSTANCES["diamond"]["kind"] != "network",
        co2["kind"] == "molecular" and sio2["kind"] == "network",  # (B)
        bond_type(sio2["elements"]) == "ionic",  # (C) SiO2 ionic?
        bonds_broken_on_melting(co2["kind"]) == "covalent",  # (D) C=O bonds break when dry ice sublimes?
    ]


def bonds_c2h4_shared_pairs(item):
    """q1: shared electron pairs in C2H4."""
    return _shared_pairs("C2H4")


def bonds_central_lone_pairs(item):
    """q2: which central atom has the most lone pairs? Options: O in H2O, N in NH3, C in CH4, C in CO2."""
    vals = [lewis(m)[1][0] for m in ("H2O", "NH3", "CH4", "CO2")]  # atom 0 is the central atom
    top = max(vals)
    return [v == top and vals.count(top) == 1 for v in vals]


def bonds_double_bonds(item):
    """q3: which molecules contain a double bond? Options: H2O, NH3, CH4, C2H4, CO2."""
    return [2 in lewis(m)[0] for m in ("H2O", "NH3", "CH4", "C2H4", "CO2")]


def bonds_molten_nacl(item):
    """q4: why molten NaCl conducts while solid NaCl does not."""
    k = SUBSTANCES["NaCl"]["kind"]
    ions_in_solid = k == "ionic"  # an ionic solid is already made of ions
    return [
        mobile_charges(k, "molten") and not mobile_charges(k, "solid"),  # (A) ions become free to move
        k == "molecular",  # (B) NaCl molecules break into atoms?
        k == "metal",  # (C) free electrons appear, as in a metal?
        not ions_in_solid,  # (D) the solid has no ions?
        # (E) bonds turn covalent on melting? The bond type follows the elements (metal + nonmetal), which
        # melting does not change.
        bond_type(SUBSTANCES["NaCl"]["elements"]) == "covalent",
    ]


def bonds_classify_unknowns(item):
    """q5: classify X, Y, Z, W from their properties in the stem."""
    X = classify(conducts_solid=False, conducts_melt_or_aq=True, high_mp=True, malleable=False)
    Y = classify(conducts_solid=False, conducts_melt_or_aq=False, high_mp=False, malleable=False)
    Z = classify(conducts_solid=True, conducts_melt_or_aq=True, high_mp=True, malleable=True)
    W = classify(conducts_solid=False, conducts_melt_or_aq=False, high_mp=True, malleable=False)
    return [
        X == "ionic",
        Y == "molecular",
        Z == "metal",  # electron-sea model
        W == SUBSTANCES["diamond"]["kind"],  # W could be diamond
        W == "ionic",
    ]


def bonds_allotropes(item):
    """q6: which pair are allotropes? Allotropes are two different substances made of one and the same
    single element. Each option member is described by what it is (a substance, or a single atom such as
    an isotope) and its formula / structure; the verdict is derived from those fields.
    Options: diamond & graphite; CO & CO2; protium & deuterium; H2O & H2O2; NaCl & MgO."""
    things = {
        "diamond": {"level": "substance", "formula": "C", "structure": SUBSTANCES["diamond"]["structure"]},
        "graphite": {"level": "substance", "formula": "C", "structure": SUBSTANCES["graphite"]["structure"]},
        "CO": {"level": "substance", "formula": "CO", "structure": "molecule"},
        "CO2": {"level": "substance", "formula": "CO2", "structure": "molecule"},
        # isotopes are kinds of atom (same Z = 1, mass numbers 1 and 2), not substances
        "protium": {"level": "atom", "formula": "H", "structure": "A=1"},
        "deuterium": {"level": "atom", "formula": "H", "structure": "A=2"},
        "H2O": {"level": "substance", "formula": "H2O", "structure": "molecule"},
        "H2O2": {"level": "substance", "formula": "H2O2", "structure": "molecule"},
        "NaCl": {"level": "substance", "formula": "NaCl", "structure": "ionic lattice"},
        "MgO": {"level": "substance", "formula": "MgO", "structure": "ionic lattice"},
    }

    def elements(f: str) -> set[str]:
        return set(re.findall(r"[A-Z][a-z]?", f))

    def allotropes(a: str, b: str) -> bool:
        x, y = things[a], things[b]
        both_substances = x["level"] == y["level"] == "substance"
        one_same_element = elements(x["formula"]) == elements(y["formula"]) and len(elements(x["formula"])) == 1
        different = (x["formula"], x["structure"]) != (y["formula"], y["structure"])
        return both_substances and one_same_element and different

    pairs = [("diamond", "graphite"), ("CO", "CO2"), ("protium", "deuterium"), ("H2O", "H2O2"), ("NaCl", "MgO")]
    return [allotropes(a, b) for a, b in pairs]


def bonds_network_statements(item):
    """q7: statements about graphite, diamond, Si and SiO2."""
    return [
        SUBSTANCES["graphite"]["neighbours"] == 3 and free_electrons_per_atom("graphite") == 1,  # (1)
        SUBSTANCES["diamond"]["neighbours"] == 4,  # (2)
        SUBSTANCES["SiO2"]["kind"] == "molecular",  # (3) discrete SiO2 molecules?
        SUBSTANCES["Si"]["neighbours"] == 4 and SUBSTANCES["Si"]["structure"] == SUBSTANCES["diamond"]["structure"],  # (4)
        "C" in METALS,  # (5) graphite conducts because carbon is a metal?
    ]


def bonds_network_formula(item):
    """q8: hypothetical network: each X bonded to 6 Y, each Y bonded to 2 X; formula XYn, n = ?"""
    n = 6 * sp.Rational(1, 2)  # each Y counts 1/2 to a given X
    assert n.is_integer
    return int(n)


def _self_test():
    # ion electron counts match noble gases (Na+ 10, Cl- 18, Mg2+ 10, O2- 10)
    for el, change in (("Na", -1), ("Cl", 1), ("Mg", -2), ("O", 2)):
        assert SYMBOL_Z[el] + change in NOBLE_ELECTRONS
    assert _shared_pairs("H2O") == 2 and _shared_pairs("CO2") == 4 and _shared_pairs("NH3") == 3
    assert lewis("CO2") == ((2, 2), [0, 2, 2])
    assert sum(lewis("CO2")[1]) == 4  # the Predict in the chapter: 4 lone pairs on CO2


_self_test()
