"""Checks for src/data/items/earth/s116-earth-history.yaml (116 sprint: EHa-Ⅴc-1~3 and EHb-Ⅴc-1~2: the
solar nebula hypothesis and the members of the solar system, Earth's habitability and the evolution of
its atmosphere, relative and absolute geologic age).

How the keys are recomputed (never from item["answer"]):
- Orderings (events in the atmosphere's history, strata in a cross-section)
  are decided by a topological sort of stated "A comes before B" relations: every linear order that
  respects the relations is enumerated, and an option is true only if it is the one and only such order.
- Strata relations come from the rules the chapter teaches, applied to the relations stated in the stem:
  superposition (a layer above is younger, layers not overturned) and cross-cutting (what cuts is younger
  than what it cuts; what covers is younger than what it covers).
- Half-lives with exact Rationals: after n half-lives the parent left is (1/2)^n; the stem's measured
  daughter : parent ratio gives n.
- Qualitative facts are small tables, each with a source comment. Facts marked "standard" are standard
  必修 earth science that is not in the chapter's frozen sources; they are listed in the writer's report.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import permutations

import sympy as sp


# --- a small topological sorter ---------------------------------------------------------------------


def linear_orders(nodes: list[str], before: set[tuple[str, str]]) -> list[tuple[str, ...]]:
    """Every order of `nodes` in which a comes before b for every (a, b) in `before`."""
    out = []
    for perm in permutations(nodes):
        pos = {n: i for i, n in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b in before):
            out.append(perm)
    return out


def unique_order(nodes: list[str], before: set[tuple[str, str]]) -> tuple[str, ...]:
    orders = linear_orders(nodes, before)
    assert len(orders) == 1, f"the stated relations allow {len(orders)} orders, not exactly one"
    return orders[0]


def strata_relations(bottom_to_top: list[str], cuts: dict[str, list[str]], covers: dict[str, list[str]]):
    """'older than' pairs (older, younger) from the chapter's rules.
    Superposition (疊置定律; 國中 Hb-Ⅳ-1/2 學習內容說明, slice correction): in layers that are not
    overturned, a layer above is younger than the one below it.
    Cross-cutting (截切; same appendix): a body that cuts other rocks is younger than every rock it cuts.
    Covering: a layer deposited on top of a body is younger than that body (superposition again)."""
    rel = set()
    for i, lower in enumerate(bottom_to_top):
        for upper in bottom_to_top[i + 1 :]:
            rel.add((lower, upper))
    for cutter, victims in cuts.items():
        for v in victims:
            rel.add((v, cutter))
    for top, below in covers.items():
        for b in below:
            rel.add((b, top))
    return rel


# --- opening turn: early atmosphere -------------------------------------------------------------------

# Early vs present atmosphere, as relative levels (standard 必修 content of EHa-Ⅴc-3, whose verified key
# concept is "atmospheric evolution from early Earth to today; oceans and life changed its composition";
# the levels themselves are standard: the early atmosphere came from volcanic gases, rich in CO2 and
# water vapour, with almost no free oxygen; oxygen built up only after photosynthesis).
# Present-day N2 about 4/5 and O2 about 1/5 of air: 國中 Fa-Ⅳ-3 (atmospheric composition).
LEVEL = {"almost none": 0, "some": 1, "much": 2, "most": 3}
EARLY = {"O2": "almost none", "CO2": "much", "atmosphere": True}
TODAY = {"O2": "some", "CO2": "almost none", "N2": "most", "atmosphere": True}


def eh_turn_early_air(item: dict) -> list[bool]:
    """q-turn: compared with today, the biggest difference in the early atmosphere. Options: (1) almost
    no oxygen and far more CO2; (2) more oxygen than today; (3) about the same as today (mostly N2, about
    1/5 O2); (4) almost all oxygen; (5) no atmosphere at all."""
    o2_early, o2_now = LEVEL[EARLY["O2"]], LEVEL[TODAY["O2"]]
    co2_early, co2_now = LEVEL[EARLY["CO2"]], LEVEL[TODAY["CO2"]]
    s1 = EARLY["O2"] == "almost none" and co2_early > co2_now
    s2 = o2_early > o2_now
    s3 = o2_early == o2_now and co2_early == co2_now
    s4 = EARLY["O2"] == "most"
    s5 = not EARLY["atmosphere"]
    return [s1, s2, s3, s4, s5]


# --- mid-chapter turn: a dike through three layers ------------------------------------------------------


def eh_turn_dike(item: dict) -> list[bool]:
    """q-strata: layers A (bottom), B, C (top), not overturned; dike X cuts A, B and C. Which formed last?
    Options: A, B, C, X, cannot be decided."""
    nodes = ["A", "B", "C", "X"]
    rel = strata_relations(["A", "B", "C"], {"X": ["A", "B", "C"]}, {})
    orders = linear_orders(nodes, rel)
    lasts = {o[-1] for o in orders}
    decided = len(lasts) == 1
    return [decided and lasts == {n} for n in nodes] + [not decided]


# --- Check yourself -----------------------------------------------------------------------------------

# Where the Sun and the planets came from (EHa-Ⅴc-1 key concept in the slice: "The solar nebula formed
# from a collapsing molecular cloud"; members "Sun, planets, moons, ..."). That most of the matter went
# into the Sun (the Sun holds most of the solar system's mass) is standard and listed in the report.
# The spin-up and the disc are elective (EHa-Ⅴa-1) and are not tested.
NEBULA_FACTS = {
    "cloud": "contracting",
    "sun_from": "nebula",
    "planets_from": "nebula",
    "most_matter_to": "Sun",
}


def eh_nebula_origin(item: dict) -> list[bool]:
    """q1: each option is a set of claims; it is true only if every claim matches NEBULA_FACTS."""
    options = [
        {"sun_from": "nebula", "planets_from": "nebula", "cloud": "contracting", "most_matter_to": "Sun"},
        {"planets_from": "thrown off the Sun"},
        {"cloud": "expanding"},
        {"most_matter_to": "planets"},
        {"planets_from": "captured from elsewhere"},
    ]
    return [all(NEBULA_FACTS[k] == v for k, v in o.items()) for o in options]


# Members of the solar system (EHa-Ⅴc-1 key concept: "Sun, planets, moons, asteroids, comets";
# terrestrial planets: 國中 Fb-Ⅳ-2, slice bridging topic 「太陽系、類地行星」; which planets are terrestrial
# or Jovian, that Jovian planets are mostly gas, and where the asteroid belt lies are standard).
PLANETS = {
    "Mercury": "terrestrial", "Venus": "terrestrial", "Earth": "terrestrial", "Mars": "terrestrial",
    "Jupiter": "jovian", "Saturn": "jovian", "Uranus": "jovian", "Neptune": "jovian",
}
MAKEUP = {"terrestrial": "rock", "jovian": "mostly gas"}
ORDER_FROM_SUN = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
ASTEROID_BELT_BETWEEN = ("Mars", "Jupiter")
MEMBER_KIND = {"Moon": "moon", "comet": "member", "asteroid": "member"}


def eh_members(item: dict) -> list[bool]:
    """q2 (multi): (1) Mercury, Venus, Earth, Mars are terrestrial; (2) Jupiter and Saturn are mostly rock
    with a hard surface; (3) asteroids lie mainly between the orbits of Mars and Jupiter; (4) the Moon is
    a planet; (5) comets are members of the solar system."""
    s1 = all(PLANETS[p] == "terrestrial" for p in ["Mercury", "Venus", "Earth", "Mars"])
    s2 = all(MAKEUP[PLANETS[p]] == "rock" for p in ["Jupiter", "Saturn"])
    a, b = ASTEROID_BELT_BETWEEN
    s3 = ORDER_FROM_SUN.index(b) == ORDER_FROM_SUN.index(a) + 1
    s4 = "Moon" in PLANETS
    s5 = MEMBER_KIND["comet"] == "member"
    assert MEMBER_KIND["Moon"] == "moon"
    return [s1, s2, s3, s4, s5]


# Liquid water at about 1 atm lies between 0 and 100 ℃ (國中 physical science: melting and boiling points
# of water at 1 atm; the stem states the pressure). A global magnetic field (magnetosphere) shields the
# surface from the Sun's charged particles (EHa-Ⅴc-2 key concept: magnetosphere; the shielding is standard).
def can_be_liquid(t_min: int, t_max: int) -> bool:
    """Liquid somewhere on the surface: the stated temperature range overlaps (0, 100)."""
    return t_max > 0 and t_min < 100


def eh_liquid_water(item: dict) -> list[bool]:
    """q3 (multi): illustrative planets at about 1 atm. 甲 −120 to −60 ℃, magnetic field; 乙 5 to 35 ℃, no
    global field; 丙 380 to 420 ℃, magnetic field. (1) 甲 may have liquid water; (2) 乙 may; (3) 丙 may;
    (4) on temperature alone 乙 is the most likely, but without a field its surface is less shielded from
    the Sun's charged particles; (5) a planet with a magnetic field must have liquid water."""
    planets = {"甲": (-120, -60, True), "乙": (5, 35, False), "丙": (380, 420, True)}
    liquid = {k: can_be_liquid(lo, hi) for k, (lo, hi, _) in planets.items()}
    s1, s2, s3 = liquid["甲"], liquid["乙"], liquid["丙"]
    only_b = [k for k, v in liquid.items() if v] == ["乙"]
    s4 = only_b and not planets["乙"][2]
    # (5) is a universal claim: one planet with a field and no liquid water refutes it
    s5 = all(liquid[k] for k, (_, _, field) in planets.items() if field)
    return [s1, s2, s3, s4, s5]


# Atmosphere's history (EHa-Ⅴc-3; the sequence is standard 必修 content): volcanic gases form the early
# atmosphere -> water vapour condenses and rain forms the oceans -> photosynthesis (in the oceans) lets
# oxygen build up in the atmosphere -> an ozone layer forms and life moves onto land.
ATMOSPHERE_BEFORE = {("volcanic", "ocean"), ("ocean", "oxygen"), ("oxygen", "ozone-land")}


def eh_atmosphere_order(item: dict) -> list[bool]:
    """q4: 甲 oxygen starts to build up; 乙 volcanic gases form the early atmosphere; 丙 an ozone layer forms
    and life moves onto land; 丁 vapour condenses into rain and forms the oceans."""
    name = {"甲": "oxygen", "乙": "volcanic", "丙": "ozone-land", "丁": "ocean"}
    order = unique_order(list(name.values()), ATMOSPHERE_BEFORE)
    options = ["乙丁甲丙", "丁乙甲丙", "乙甲丁丙", "甲乙丁丙", "乙丁丙甲"]
    return [tuple(name[c] for c in o) == order for o in options]


def eh_strata_order(item: dict) -> list[bool]:
    """q5: bottom to top P (sandstone), Q (shale), R (limestone), not overturned. Dike G cuts P and Q, and
    R covers G's top without being cut. Fault F offsets P, Q, R and G. Oldest to youngest?"""
    rel = strata_relations(["P", "Q", "R"], {"G": ["P", "Q"], "F": ["P", "Q", "R", "G"]}, {"R": ["G"]})
    order = unique_order(["P", "Q", "R", "G", "F"], rel)
    options = ["PQGRF", "PQRGF", "GPQRF", "PQRFG", "FPQGR"]
    return [tuple(o) == order for o in options]


def half_lives_from_ratio(daughter: int, parent: int) -> int:
    """Parent left = P/(P+D) = (1/2)^n, with no daughter at the start and every daughter atom from decay."""
    left = F(parent, parent + daughter)
    n = 0
    while left < 1:
        left *= 2
        n += 1
    assert left == 1, "the ratio is not a whole number of half-lives"
    return n


def eh_age_from_ratio(item: dict) -> int:
    """q6: an illustrative isotope with half-life 2 億年; daughter : parent = 31 : 1. Age in 億年."""
    n = half_lives_from_ratio(31, 1)
    return int(n * F(2))


def eh_choose_isotope(item: dict) -> list[bool]:
    """q7: a rock about 9 億年 old. The stem's rule: the age can be measured only if the parent left is at
    least 1/1000 and at most 99/100 of the original. Illustrative half-lives: 甲 8 days, 乙 6 thousand
    years, 丙 7 億年, 丁 1000 億年, 戊 50 萬年. Parent left = (1/2)^(t/T); compare through n = t/T:
    left >= 1/1000 <=> n <= log2(1000); left <= 99/100 <=> n >= log2(100/99)."""
    age = sp.Integer(9) * 10**8  # years
    halves = {
        "甲": sp.Rational(8, 365),
        "乙": sp.Integer(6000),
        "丙": sp.Integer(7) * 10**8,
        "丁": sp.Integer(1000) * 10**8,
        "戊": sp.Integer(500000),
    }
    out = []
    for k in ["甲", "乙", "丙", "丁", "戊"]:
        n = age / halves[k]
        ok = sp.Le(n, sp.log(1000, 2)) & sp.Ge(n, sp.log(sp.Rational(100, 99), 2))
        out.append(bool(ok))
    return out


# Statement table for q8, each with its source:
# - weathering depends mainly on rock type and environment, not age (slice research.common_misconceptions,
#   from the 考試說明);
# - strata with the same index fossil formed at about the same time (EHb-Ⅴc-1 key concept: some organisms
#   lived only in specific periods, so fossils help order strata);
# - a half-life does not change with heating (standard: radioactive decay is regular, EHb-Ⅴc-2 key
#   concept; not changed by temperature or pressure is standard);
# - a dike that cuts other rocks is younger (cross-cutting; 國中 Hb-Ⅳ appendix, slice correction).
MORE_WEATHERED_MEANS_OLDER = False
SAME_INDEX_FOSSIL_SAME_TIME = True
HEATING_SHORTENS_HALF_LIFE = False


def eh_dating_statements(item: dict) -> list[bool]:
    """q8 (multi): (1) more weathered rock is always older; (2) far-apart strata with the same index fossil
    formed at about the same time; (3) heating a rock shortens its isotopes' half-lives; (4) a dike that
    cuts other layers is younger than they are; (5) after two half-lives the parent is all gone."""
    rel = strata_relations(["L1", "L2"], {"D": ["L1", "L2"]}, {})
    s4 = all(o.index("D") > o.index("L1") and o.index("D") > o.index("L2") for o in linear_orders(["L1", "L2", "D"], rel))
    left_after_two = F(1, 2) ** 2
    s5 = left_after_two == 0
    return [MORE_WEATHERED_MEANS_OLDER, SAME_INDEX_FOSSIL_SAME_TIME, HEATING_SHORTENS_HALF_LIFE, s4, s5]
