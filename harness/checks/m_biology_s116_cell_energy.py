"""Checks for src/data/items/biology/s116-cell-energy.yaml (116 sprint: BDa-Ⅴc-3, BDa-Ⅴc-4: ATP as the
direct energy source, and the energy relationship between photosynthesis and respiration).

How the keys are recomputed (never from item["answer"]):
- Summary equations are balanced by counting atoms (exact integers), so oxygen counts are computed.
- Gas data in a sealed box follow one rule: observed CO2 change = respiration release - photosynthesis
  uptake, with respiration > 0 in every living cell. Statements about a data segment are tested over a
  grid of (respiration, photosynthesis) rates consistent with that segment; a statement is true only if
  it holds for every consistent pair.
- Qualitative facts are code tables, each with a source comment. Sources: src/data/registry/codes/nat.json
  (BDa-Ⅴc-3, BDa-Ⅴc-4 keyConcepts), the research slice for this chapter (verification.corrections:
  國中理化 Ba-Ⅳ-2; research.common_misconceptions: plants respire all the time), and standard 必修/國中
  biology within the 說明 depth limits (no ATP structural formula, no mechanisms).
"""

from __future__ import annotations

import math
import re
from fractions import Fraction as F


def _atoms(formula: str) -> dict[str, int]:
    """Atom counts of a simple formula without brackets, e.g. 'C6H12O6' -> {'C': 6, 'H': 12, 'O': 6}."""
    out: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        out[el] = out.get(el, 0) + (int(n) if n else 1)
    return out


def _side(terms: list[tuple[int, str]]) -> dict[str, int]:
    tot: dict[str, int] = {}
    for coef, f in terms:
        for el, n in _atoms(f).items():
            tot[el] = tot.get(el, 0) + coef * n
    return tot


# --- fact tables ---------------------------------------------------------------------------------

# nat.json BDa-Ⅴc-3 keyConcepts: "ATP supplies the energy that cell activities need" (direct source).
DIRECT_ENERGY_SOURCE = "ATP"

# Standard 必修 content within 說明 3-1 (no structural formula): ATP -> ADP + phosphate releases energy;
# the reverse takes energy in, supplied mainly by respiration.
ATP_BREAKDOWN_RELEASES_ENERGY = True
ATP_SYNTHESIS_TAKES_IN_ENERGY = True
# Long-term energy stores are organic substances such as carbohydrates and lipids, not ATP
# (ATP is used and rebuilt continuously). Standard 必修 content.
LONG_TERM_STORES = {"carbohydrate", "lipid"}
# Research slice, verification.corrections: 國中理化 Ba-Ⅳ-2 "呼吸作用是將化學能轉換成熱能"; with
# BDa-Ⅴc-3 (ATP made from that energy): respiration's released energy goes partly to ATP, the rest heat.
RESPIRATION_ENERGY_GOES_TO = {"ATP", "heat"}

# nat.json BDa-Ⅴc-4 keyConcepts: photosynthesis turns light energy into chemical energy stored in
# organic matter; cells use it for metabolism. Inputs/outputs are the 國中 Bc-Ⅳ summary equations.
PROCESS = {
    "photosynthesis": {
        "inputs": {"CO2", "H2O"},
        "outputs": {"glucose", "O2"},
        "energy_from": "light",
        "energy_to": "chemical energy in organic matter",
        "needs_light": True,
        "organelle": "chloroplast",
    },
    "respiration": {
        "inputs": {"glucose", "O2"},
        "outputs": {"CO2", "H2O"},
        "energy_from": "chemical energy in organic matter",
        "energy_to": "ATP and heat",
        "needs_light": False,
        "organelle": "mitochondrion",
    },
}

# Research slice, research.common_misconceptions: "Plant cells respire all the time. Photosynthesis
# needs light." Organelles per cell type: standard 必修 (BDa-Ⅴc-2, previous chapter).
CELL_TYPES = {
    "plant mesophyll": {"chloroplast": True, "mitochondrion": True},
    "animal": {"chloroplast": False, "mitochondrion": True},
}


def _processes_running(cell: str, light: bool, alive: bool = True) -> set[str]:
    org = CELL_TYPES[cell]
    running = set()
    if alive and org["mitochondrion"]:
        running.add("respiration")  # a living cell respires whether or not there is light
    if alive and org["chloroplast"] and light:
        running.add("photosynthesis")
    return running


# Energy transfers taught in the chapter (directed edges). Sources: BDa-Ⅴc-4 (light -> organic matter
# by photosynthesis; organic matter used by cells), BDa-Ⅴc-3 (ATP is the direct source for activities),
# Ba-Ⅳ-2 (respiration: chemical energy -> heat).
ENERGY_EDGES = {
    ("light", "glucose"),
    ("glucose", "ATP"),
    ("glucose", "heat"),
    ("ATP", "muscle contraction"),
}

# Enzymes: 國中 Bc-Ⅳ-1 (enzymes catalyse metabolism; temperature affects them) and standard content:
# most are proteins, they are not used up, they supply no energy, overheating inactivates them.
ENZYME = {"used_up": False, "mostly_protein": True, "inactivated_by_overheating": True, "supplies_energy": False}
# Photosynthesis and respiration are chains of reactions, each step needing enzymes (standard content).
PROCESS_IS_SINGLE_REACTION = False


def _enzyme_rate(x: F) -> float:
    """The chapter's schematic rate curve (relative), optimum at x = 6, steeper on the hot side."""
    width = 4 if x <= 6 else F(3, 5)
    return 1 + 3.5 * math.exp(-float((x - 6) ** 2) / float(width))


# --- turn ----------------------------------------------------------------------------------------


def ce_turn_leaf_noon(item: dict) -> list[bool]:
    """q-turn: a mesophyll cell in bright light. Options claim which processes run:
    photosynthesis only (respiration at night); respiration only; both; neither (stored ATP);
    chloroplast only, mitochondria paused (= photosynthesis without respiration)."""
    actual = _processes_running("plant mesophyll", light=True)
    claims = [
        {"photosynthesis"},
        {"respiration"},
        {"photosynthesis", "respiration"},
        set(),
        {"photosynthesis"},
    ]
    return [c == actual for c in claims]


# --- Check yourself ------------------------------------------------------------------------------


def ce_direct_source(item: dict) -> list[bool]:
    """q1: the direct energy source of muscle contraction. Options: glucose, ATP, starch, sunlight, enzyme."""
    return [o == DIRECT_ENERGY_SOURCE for o in ["glucose", "ATP", "starch", "sunlight", "enzyme"]]


def ce_atp_statements(item: dict) -> list[bool]:
    """q2: (1) ATP breakdown releases energy; (2) making ATP takes energy in; (3) ATP is the main
    long-term store; (4) part of respiration's energy makes ATP; (5) all of it goes to ATP, none to heat."""
    return [
        ATP_BREAKDOWN_RELEASES_ENERGY,
        ATP_SYNTHESIS_TAKES_IN_ENERGY,
        "ATP" in LONG_TERM_STORES,
        "ATP" in RESPIRATION_ENERGY_GOES_TO,
        RESPIRATION_ENERGY_GOES_TO == {"ATP"},
    ]


FORMULA = {"glucose": "C6H12O6", "O2": "O2", "CO2": "CO2", "H2O": "H2O"}


def _on_cycle(edges: set[tuple[str, str]], node: str) -> bool:
    """True when the directed graph has a path from node back to itself."""
    seen, stack = set(), [b for a, b in edges if a == node]
    while stack:
        n = stack.pop()
        if n == node:
            return True
        if n in seen:
            continue
        seen.add(n)
        stack.extend(b for a, b in edges if a == n)
    return False


def _element_edges(el: str) -> set[tuple[str, str]]:
    """Matter graph for one element: in each process, an edge from every input that holds the element
    to every output that holds it (PROCESS inputs/outputs; atoms counted from the formulas)."""
    edges = set()
    for proc in PROCESS.values():
        for a in proc["inputs"]:
            for b in proc["outputs"]:
                if _atoms(FORMULA[a]).get(el) and _atoms(FORMULA[b]).get(el):
                    edges.add((a, b))
    return edges


def ce_what_cycles(item: dict) -> list[bool]:
    """q3: which can go round between photosynthesis and respiration? Options: hydrogen atoms;
    oxygen atoms; light energy; heat from respiration; energy released by ATP breakdown.
    An element cycles when some species holding it lies on a cycle of its matter graph; an energy
    form cycles when its node lies on a cycle of ENERGY_EDGES."""
    def element_cycles(el: str) -> bool:
        edges = _element_edges(el)
        return any(_on_cycle(edges, sp) for sp in FORMULA if _atoms(FORMULA[sp]).get(el))
    return [
        element_cycles("H"),
        element_cycles("O"),
        _on_cycle(ENERGY_EDGES, "light"),
        _on_cycle(ENERGY_EDGES, "heat"),
        _on_cycle(ENERGY_EDGES, "ATP"),
    ]


def ce_box_uptake(item: dict) -> int:
    """q4: dark +3 per hour (respiration only); light -6 per hour, respiration unchanged.
    observed = r - p, so p = r - observed."""
    r = F(3)
    observed_light = F(-6)
    p = r - observed_light
    assert p.denominator == 1
    return int(p)


def ce_segments(item: dict) -> list[bool]:
    """q5: CO2 in a sealed box rises in segment 甲, is flat in 乙, falls in 丙. A statement is true only
    if it holds for every (r, p) with r > 0 (living plant) and sign(r - p) matching the segment.
    Options: 甲 no respiration; 乙 both stopped; 乙 uptake = release; 丙 no respiration; 甲 p > r."""
    grid = [(F(r), F(p)) for r in range(0, 9) for p in range(0, 17)]

    def consistent(sign: int):
        return [(r, p) for r, p in grid if r > 0 and ((r - p > 0) - (r - p < 0)) == sign]

    rise, flat, fall = consistent(1), consistent(0), consistent(-1)
    assert rise and flat and fall

    def always(pairs, pred):
        return all(pred(r, p) for r, p in pairs)

    return [
        always(rise, lambda r, p: r == 0),
        always(flat, lambda r, p: r == 0 and p == 0),
        always(flat, lambda r, p: p == r),
        always(fall, lambda r, p: r == 0),
        always(rise, lambda r, p: p > r),
    ]


def ce_two_processes(item: dict) -> list[bool]:
    """q6: (1) photosynthesis: light -> chemical energy in organic matter; (2) only plant cells respire;
    (3) respiration releases the chemical energy of organic matter; (4) photosynthesis products are the
    inputs of aerobic respiration; (5) animal cells have chloroplasts and photosynthesise."""
    ps, rs = PROCESS["photosynthesis"], PROCESS["respiration"]
    respiring = {c for c in CELL_TYPES if "respiration" in _processes_running(c, light=True)}
    return [
        ps["energy_from"] == "light" and ps["energy_to"] == "chemical energy in organic matter",
        respiring == {"plant mesophyll"},
        rs["energy_from"] == "chemical energy in organic matter",
        ps["outputs"] == rs["inputs"],
        CELL_TYPES["animal"]["chloroplast"],
    ]


def ce_enzyme(item: dict) -> list[bool]:
    """q7: (1) enzymes are used up; (2) most are proteins and overheating inactivates them; (3) hotter
    always means faster (tested on the chapter's rate curve); (4) enzymes supply the energy; (5) the
    two processes are single reactions needing no enzymes."""
    xs = [F(k, 4) for k in range(4, 37)]
    rates = [_enzyme_rate(x) for x in xs]
    monotonic_up = all(b >= a for a, b in zip(rates, rates[1:]))
    return [
        ENZYME["used_up"],
        ENZYME["mostly_protein"] and ENZYME["inactivated_by_overheating"],
        monotonic_up,
        ENZYME["supplies_energy"],
        PROCESS_IS_SINGLE_REACTION,
    ]


def ce_energy_route(item: dict) -> list[bool]:
    """q8: a route is right when every step is an energy transfer in ENERGY_EDGES and it runs from
    light to muscle contraction."""
    routes = [
        ["light", "glucose", "ATP", "muscle contraction"],
        ["glucose", "light", "ATP", "muscle contraction"],
        ["heat", "glucose", "ATP", "muscle contraction"],
        ["light", "glucose", "muscle contraction"],
        ["muscle contraction", "ATP", "glucose", "light"],
    ]

    def ok(route):
        return route[0] == "light" and route[-1] == "muscle contraction" and all(
            (a, b) in ENERGY_EDGES for a, b in zip(route, route[1:])
        )

    return [ok(r) for r in routes]
