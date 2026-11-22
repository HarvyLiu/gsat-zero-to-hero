"""Checks for src/data/items/chemistry/s116-atomic-structure.yaml (116 sprint: CAa-Ⅴc-3, CAa-Ⅴc-4,
CAb-Ⅴc-2: atomic structure, isotopes and the periodic table).

Everything is recomputed from small tables, never from item["answer"]:
- particle counts from (Z, A): protons = electrons (neutral atom) = Z, neutrons = A − Z;
- relative masses with exact Rationals: proton 1, neutron 1, electron 1/1836 (the chapter's table);
- valence electrons for Z = 1–18 by counting on from the previous noble gas (He 2, Ne 10, Ar 18),
  cross-checked against the group-number rule (groups 1–2: 1–2; groups 13–18: group − 10; He: 2);
- metal / metalloid / nonmetal from a classification table of Z = 1–18 (B and Si are the metalloids).
"""

from __future__ import annotations

from sympy import Rational

# Z: (symbol, group, period, class). Standard periodic-table positions for Z = 1–18; "class" is the
# usual metal / metalloid / nonmetal split taught in 必修化學 (nat:CAb-Vc-2 keyConcepts).
ELEMENTS = {
    1: ("H", 1, 1, "nonmetal"),
    2: ("He", 18, 1, "nonmetal"),
    3: ("Li", 1, 2, "metal"),
    4: ("Be", 2, 2, "metal"),
    5: ("B", 13, 2, "metalloid"),
    6: ("C", 14, 2, "nonmetal"),
    7: ("N", 15, 2, "nonmetal"),
    8: ("O", 16, 2, "nonmetal"),
    9: ("F", 17, 2, "nonmetal"),
    10: ("Ne", 18, 2, "nonmetal"),
    11: ("Na", 1, 3, "metal"),
    12: ("Mg", 2, 3, "metal"),
    13: ("Al", 13, 3, "metal"),
    14: ("Si", 14, 3, "metalloid"),
    15: ("P", 15, 3, "nonmetal"),
    16: ("S", 16, 3, "nonmetal"),
    17: ("Cl", 17, 3, "nonmetal"),
    18: ("Ar", 18, 3, "nonmetal"),
}
Z_OF = {v[0]: z for z, v in ELEMENTS.items()}
NOBLE = (2, 10, 18)
M_P, M_N, M_E = Rational(1), Rational(1), Rational(1, 1836)


def valence(z: int) -> int:
    """Valence electrons for Z = 1–18: count on from the previous noble gas; noble gases He 2, Ne/Ar 8."""
    if z in NOBLE:
        v = 2 if z == 2 else 8
    else:
        v = z - max(n for n in (0,) + NOBLE if n < z)
    group = ELEMENTS[z][1]
    by_group = 2 if z == 2 else (group if group <= 2 else group - 10)
    assert v == by_group, (z, v, by_group)  # the two methods of the chapter must agree
    return v


def family(z: int) -> str | None:
    sym, group, _, cls = ELEMENTS[z]
    if group == 1 and cls == "metal":
        return "alkali-metal"
    if group == 17:
        return "halogen"
    if group == 18:
        return "noble-gas"
    return None


def atom(symbol: str, a: int) -> dict:
    """A neutral atom given by element symbol and mass number."""
    z = Z_OF[symbol]
    n = a - z
    assert n >= 0
    return {"Z": z, "N": n, "A": a, "e": z, "mass": z * M_P + n * M_N + z * M_E}


# Atoms the stems use (isotopes only with C and H, plus same-A non-isotopes in q2 distractors).
H1, H2, H3 = atom("H", 1), atom("H", 2), atom("H", 3)
C12, C13, C14 = atom("C", 12), atom("C", 13), atom("C", 14)
TABLE = [H1, H2, H3, C12, C13, C14]


def as_turn_c12_c14(item: dict) -> list[bool]:
    """q-turn: what is the same for C-12 and C-14? protons, neutrons, mass number, particles in the
    nucleus, mass of one atom."""
    a, b = C12, C14
    return [
        a["Z"] == b["Z"],
        a["N"] == b["N"],
        a["A"] == b["A"],
        a["Z"] + a["N"] == b["Z"] + b["N"],
        a["mass"] == b["mass"],
    ]


def as_name_protium_deuterium(item: dict) -> list[bool]:
    """q-name: protium vs deuterium. An option is right when its verdict (same element or not) is
    correct AND its reason is true AND it is the reason that decides the element (proton number)."""
    a, b = H1, H2
    same = a["Z"] == b["Z"]
    reason_true = {"name": True, "Z": a["Z"] == b["Z"], "N": a["N"] != b["N"], "A": a["A"] == b["A"]}
    options = [(False, "name"), (True, "Z"), (False, "N"), (True, "A")]
    return [verdict == same and reason_true[r] and r == "Z" for verdict, r in options]


def as_c13_counts(item: dict) -> tuple[int, int]:
    """q1: neutrons and electrons of a neutral C-13 atom."""
    return (C13["N"], C13["e"])


def as_isotope_pair(item: dict) -> list[bool]:
    """q2: which pair are isotopes? Both must be atoms, same Z, different A."""
    he3, c14, n14 = atom("He", 3), C14, atom("N", 14)
    pairs = [
        ("atom", H1, "atom", H2),
        ("atom", c14, "atom", n14),
        ("molecule", None, "molecule", None),  # O2 and O3: molecules, not atoms
        ("atom", H1, "molecule", None),  # an H atom and an H2 molecule
        ("atom", H3, "atom", he3),
    ]
    out = []
    for ka, a, kb, b in pairs:
        out.append(ka == kb == "atom" and a["Z"] == b["Z"] and a["A"] != b["A"])
    return out


def as_particle_statements(item: dict) -> list[bool]:
    """q3: statements checked on the H and C isotopes of the chapter.
    (1) Z equals the proton number (definition: the table stores Z as the proton count);
    (2) electrons = neutrons; (3) A = Z + N; (4) electron heavier than proton;
    (5) all atoms of one element have the same neutron number."""
    s1 = all(t["Z"] == t["e"] and t["A"] - t["N"] == t["Z"] for t in TABLE)
    s2 = all(t["e"] == t["N"] for t in TABLE)
    s3 = all(t["A"] == t["Z"] + t["N"] for t in TABLE)
    s4 = M_E > M_P
    by_z: dict[int, set[int]] = {}
    for t in TABLE:
        by_z.setdefault(t["Z"], set()).add(t["N"])
    s5 = all(len(ns) == 1 for ns in by_z.values())
    return [s1, s2, s3, s4, s5]


def as_valence_p_mg(item: dict) -> tuple[int, int]:
    """q4: valence electrons of P (Z = 15) and Mg (Z = 12)."""
    return (valence(15), valence(12))


def as_similar_pair(item: dict) -> list[bool]:
    """q5: the pair most alike chemically: same group and same valence count, hydrogen excluded
    (it shares group 1 but is a nonmetal)."""
    pairs = [("Li", "Na"), ("Na", "Mg"), ("F", "Ne"), ("C", "N"), ("Na", "Cl")]
    out = []
    for a, b in pairs:
        za, zb = Z_OF[a], Z_OF[b]
        out.append(ELEMENTS[za][1] == ELEMENTS[zb][1] and valence(za) == valence(zb) and "H" not in (a, b))
    return out


def as_nonmetals(item: dict) -> list[bool]:
    """q6: which are nonmetals? H, Al, Si, S, Ar."""
    return [ELEMENTS[Z_OF[s]][3] == "nonmetal" for s in ("H", "Al", "Si", "S", "Ar")]


# How the modern table is ordered. Source: nat:CAa-Vc-3 keyConcepts "elements ordered by atomic number".
MODERN_TABLE_ORDER = "atomic number"


def as_table_statements(item: dict) -> list[bool]:
    """q7: (1) every group-18 atom has 8 valence electrons; (2) H is an alkali metal; (3) every
    group-17 atom has 7 valence electrons; (4) across a period, nonmetals on the left change to metals
    on the right; (5) the modern table is ordered by atomic weight."""
    g = lambda grp: [z for z, v in ELEMENTS.items() if v[1] == grp]
    s1 = all(valence(z) == 8 for z in g(18))
    s2 = family(1) == "alkali-metal"
    s3 = all(valence(z) == 7 for z in g(17))
    period3 = sorted(z for z, v in ELEMENTS.items() if v[2] == 3)
    s4 = ELEMENTS[period3[0]][3] == "nonmetal" and ELEMENTS[period3[-1]][3] == "metal"
    s5 = MODERN_TABLE_ORDER == "atomic weight"
    return [s1, s2, s3, s4, s5]
