"""Checks for src/data/items/earth/s116-typhoons.yaml (116 sprint: EMd-Ⅴc-1 formation conditions, EMd-Ⅴc-2
structure and near-surface flow, EMd-Ⅴc-3 tracks around the Pacific High and impact on Taiwan).

How the keys are recomputed (never from item["answer"]):
- A small force-balance engine (the same qualitative 必修 statements as the wind chapter, no formula taught).
  Horizontal vectors are (east, north) pairs of exact SymPy numbers. A steady wind v satisfies
    PGF + Coriolis + friction = 0,  PGF = g (unit, towards lower pressure), Coriolis = rot(v)
    (right of v in the Northern Hemisphere, left in the Southern), friction = -r * v (r = 0 aloft).
  Around a typhoon (a low) g points to the centre; near the ground r > 0 is not given, so a claim about the
  wind must hold for every r > 0. Around the Pacific High g points away from its centre and the steering flow
  is taken frictionless (r = 0).
- Wind directions as compass bearings (degrees clockwise from north), computed exactly with atan2. A wind is
  named by where it comes from (bearing + 180).
- Structure, formation, track and impact facts are small tables with one source comment per fact.
- Data items read their numbers from the stem (both locales must agree) and work with exact Rationals.
"""

from __future__ import annotations

import re
from fractions import Fraction as F

import sympy as sp

# --- facts (one source comment each) ------------------------------------------------------------------
# nat:EMd-Vc-1 keyConcepts: "Needs a warm sea surface, enough Coriolis force and a suitable atmospheric
# environment".
FORMATION_CONDITIONS = {"warm_sea": True, "coriolis": True, "suitable_atmosphere": True}
# Energy from the latent heat released when water vapour condenses (the warm sea supplies the vapour):
# standard 必修/國中 content, listed in the chapter report as a standard fact not quoted in the sources.
ENERGY_SOURCE = "condensation_heat"
# Wind chapter (nat:EIb-Vc-5, standard 必修 content): no Coriolis force on horizontally moving air at the
# equator.
CORIOLIS_AT_EQUATOR = 0

# nat:EMd-Vc-2 keyConcepts: "Spiral rainbands, lowest pressure at the centre; centre nearly calm, strongest
# winds just outside; surface flow counter-clockwise (Northern Hemisphere)" (slice correction: state the
# hemisphere). The surface flow itself is recomputed below from the forces, and checked against this fact.
STRUCTURE = {
    "lowest_pressure": "centre",
    "centre_wind": "nearly_calm",
    "strongest_wind": "just_outside_centre",
    "rainbands": "spiral",
    "surface_flow_N": ("ccw", "in"),
}

# nat:EMd-Vc-3 keyConcepts: "Tracks guided by the Pacific High, mostly moving clockwise around it; local impact
# depends on track, terrain and circulation".
TRACK_SENSE_AROUND_HIGH = "cw"
IMPACT_FACTORS = {"track", "terrain", "circulation"}
# Standard facts (listed in the chapter report): air forced up a windward slope cools (rising air cools:
# nat:EIb-Vc-4, the clouds chapter) and gives heavy rain; after landfall a typhoon loses the warm sea's vapour
# supply and usually weakens; the winds on the far side of the eye return from the opposite direction (this
# last one is recomputed by the engine).
WINDWARD_LIFTING_RAIN = True
WEAKENS_AFTER_LANDFALL = True


# --- force-balance engine -------------------------------------------------------------------------------

def vec(e, n) -> sp.Matrix:
    return sp.Matrix([sp.nsimplify(e), sp.nsimplify(n)])


def unit(v: sp.Matrix) -> sp.Matrix:
    return sp.simplify(v / sp.sqrt(v.dot(v)))


def unit_from_bearing(b) -> sp.Matrix:
    r = sp.pi * sp.nsimplify(b) / 180
    return sp.Matrix([sp.sin(r), sp.cos(r)])


def rot(hemisphere: str) -> sp.Matrix:
    """Coriolis direction from the velocity: right of it (N) or left of it (S)."""
    return sp.Matrix([[0, 1], [-1, 0]]) if hemisphere == "N" else sp.Matrix([[0, -1], [1, 0]])


def steady_wind(g: sp.Matrix, hemisphere: str, r) -> sp.Matrix:
    """Solve g + rot(v) - r*v = 0 for v."""
    A = rot(hemisphere) - sp.nsimplify(r) * sp.eye(2)
    return sp.simplify(A.LUsolve(-g))


def bearing(v: sp.Matrix):
    """Compass bearing (degrees, [0, 360)) that v points towards, exact."""
    b = sp.simplify(sp.atan2(v[0], v[1]) * 180 / sp.pi)
    return sp.nsimplify(sp.Mod(b, 360))


def from_bearing(v: sp.Matrix):
    return sp.nsimplify(sp.Mod(bearing(v) + 180, 360))


def around_low(p: sp.Matrix, hemisphere: str, r) -> sp.Matrix:
    """Near-surface wind at position p (relative to the centre of a low): PGF points to the centre."""
    return steady_wind(-unit(p), hemisphere, r)


def low_circulation(hemisphere: str) -> tuple[str, str]:
    """(turning sense seen from above, inflow/outflow), the same at several positions and friction ratios."""
    seen = set()
    for r in (F(1, 4), F(1, 2), 1, 2):
        for px, py in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            p = vec(px, py)
            v = around_low(p, hemisphere, r)
            cross = sp.simplify(p[0] * v[1] - p[1] * v[0])
            dot = sp.simplify(p.dot(v))
            seen.add(("ccw" if cross > 0 else "cw", "in" if dot < 0 else "out"))
    assert len(seen) == 1, seen
    return seen.pop()


assert low_circulation("N") == STRUCTURE["surface_flow_N"]  # the engine agrees with the sourced fact


def from_arc_for_all_friction(p: sp.Matrix, hemisphere: str) -> tuple:
    """The near-surface wind's 'from' bearing at p, as r runs over (0, inf), sweeps an open arc between its two
    limits: r -> 0 (pure turning) and r -> inf (pure inflow, along the PGF). Return (limit0, mid at r=1,
    limit_inf)."""
    e0 = from_bearing(around_low(p, hemisphere, 0))
    e1 = from_bearing(-unit(p))
    mid = from_bearing(around_low(p, hemisphere, 1))
    return e0, mid, e1


def in_closed_arc(x, lo, hi) -> bool:
    """Is bearing x on the clockwise arc from lo to hi (inclusive)?"""
    span = sp.Mod(hi - lo, 360)
    off = sp.Mod(x - lo, 360)
    return bool(off <= span)


def arc_options(e0, mid, e1, arcs) -> list[bool]:
    """An option arc is true iff the whole set of possible 'from' bearings (both limits and the middle) lies in it."""
    out = []
    for lo, hi in arcs:
        out.append(all(in_closed_arc(x, lo, hi) for x in (e0, mid, e1)))
    return out


COMPASS = {"北": 0, "東北": 45, "東": 90, "東南": 135, "南": 180, "西南": 225, "西": 270, "西北": 315}


def parse_arcs(item) -> list[tuple[int, int]]:
    """Options '甲方到乙方之間': the clockwise arc from 甲 to 乙 or from 乙 to 甲, whichever is 90 degrees."""
    arcs = []
    for opt in item["text"]["zh-tw"]["options"]:
        m = re.fullmatch(r"(\S+?)方到(\S+?)方之間", opt)
        assert m, opt
        a, b = COMPASS[m.group(1)], COMPASS[m.group(2)]
        if (b - a) % 360 == 90:
            arcs.append((a, b))
        else:
            assert (a - b) % 360 == 90, opt
            arcs.append((b, a))
    return arcs


def steering(p: sp.Matrix) -> sp.Matrix:
    """Flow around the Pacific High at position p (relative to its centre): PGF points away from the centre,
    frictionless (Northern Hemisphere)."""
    return steady_wind(unit(p), "N", 0)


def high_turning_sense() -> str:
    senses = set()
    for px, py in ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1)):
        p = vec(px, py)
        v = steering(p)
        senses.add("ccw" if sp.simplify(p[0] * v[1] - p[1] * v[0]) > 0 else "cw")
    assert len(senses) == 1
    return senses.pop()


assert high_turning_sense() == TRACK_SENSE_AROUND_HIGH  # the engine agrees with the sourced fact


def moves_towards(p: sp.Matrix, to_bearing) -> bool:
    v = steering(p)
    u = unit_from_bearing(to_bearing)
    return sp.simplify(v[0] * u[1] - v[1] * u[0]) == 0 and bool(sp.simplify(v.dot(u)) > 0)


def position(bearing_from_high) -> sp.Matrix:
    return unit_from_bearing(bearing_from_high)


# --- item checks -------------------------------------------------------------------------------------------

def ty_turn_eye(item):
    """Options: strongest wind; nearly calm; strong outflow from the centre; same as before the centre arrived."""
    _, flow = low_circulation("N")
    # just before the centre arrives, the ring of strongest wind ("just_outside_centre") passes the station
    return [
        STRUCTURE["strongest_wind"] == "centre",
        STRUCTURE["centre_wind"] == "nearly_calm",
        flow == "out",
        STRUCTURE["strongest_wind"] == "centre" or STRUCTURE["centre_wind"] != "nearly_calm",
    ]


def ty_turn_track(item):
    """Typhoon due south of the high: options west, east, north, south, standing still."""
    p = position(180)
    still = sp.simplify(steering(p).dot(steering(p))) == 0
    return [moves_towards(p, b) for b in (270, 90, 0, 180)] + [still]


def ty_formation_statements(item):
    """(1) energy from condensation heat; (2) weakens over cold sea; (3) Coriolis not needed; (4) sea temperature
    irrelevant; (5) needs a suitable atmosphere."""
    return [
        ENERGY_SOURCE == "condensation_heat",
        FORMATION_CONDITIONS["warm_sea"],  # cold sea removes a needed condition: the fuel runs short
        not FORMATION_CONDITIONS["coriolis"],
        not FORMATION_CONDITIONS["warm_sea"],
        FORMATION_CONDITIONS["suitable_atmosphere"],
    ]


def ty_structure_statements(item):
    """NH: (1) lowest pressure at centre; (2) strongest wind at centre; (3) ccw inflow; (4) spiral rainbands;
    (5) cw outflow."""
    sense, flow = low_circulation("N")
    return [
        STRUCTURE["lowest_pressure"] == "centre",
        STRUCTURE["strongest_wind"] == "centre",
        (sense, flow) == ("ccw", "in"),
        STRUCTURE["rainbands"] == "spiral",
        (sense, flow) == ("cw", "out"),
    ]


def _series(stem: str, after: str, unit_word: str) -> list[int]:
    part = stem.split(after)[1].split(unit_word)[0]
    return [int(x) for x in re.findall(r"\$(\d+)\$", part)]


def ty_buoy_eye_or_side(item):
    """Closest approach: the time of lowest pressure (STRUCTURE: lowest pressure at the centre). The eye passed over
    the buoy iff that reading is a wind lull between two higher readings (STRUCTURE: centre nearly calm, strongest
    winds just outside); otherwise the centre went past to one side. Options: (eye over or not, hour)."""
    zh, en = item["text"]["zh-tw"]["stem"], item["text"]["en"]["stem"]
    pz, pe = _series(zh, "氣壓依序是", "hPa"), _series(en, "pressures, in order, are", "hPa")
    wz, we = _series(zh, "風速依序是", "m/s"), _series(en, "wind speeds, in order, are", "m/s")
    assert pz == pe and wz == we and len(pz) == len(wz) == 7, (pz, pe, wz, we)
    hours = [int(x) for x in re.search(r"第([\d、]+)時的氣壓", zh).group(1).split("、")]
    hours_en = [int(x) for x in re.search(r"At hours ([\d, and]+?) the pressures", en).group(1).replace("and", ",").replace(" ", "").split(",") if x]
    assert hours == hours_en and len(hours) == 7, (hours, hours_en)
    i = min(range(7), key=lambda k: pz[k])
    assert pz.count(pz[i]) == 1
    assert 0 < i < 6, "the lowest pressure must not be at the edge of the record"
    lull = wz[i] < wz[i - 1] and wz[i] < wz[i + 1]
    assert STRUCTURE["lowest_pressure"] == "centre" and STRUCTURE["centre_wind"] == "nearly_calm"
    eye_over, closest = lull, hours[i]
    out = []
    for oz, oe in zip(item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]):
        over_z = "沒有經過" not in oz
        over_e = "did not pass" not in oe
        hz = int(re.search(r"第(\d+)時", oz).group(1))
        he = int(re.search(r"hour (\d+)", oe).group(1))
        assert (over_z, hz) == (over_e, he), (oz, oe)
        out.append(over_z == eye_over and hz == closest)
    return out


def ty_ship_southwest(item):
    """NH, ship south-west of the centre (bearing 225 from the centre); options are 90-degree 'from' arcs."""
    assert "西南方" in item["text"]["zh-tw"]["stem"] and "south-west" in item["text"]["en"]["stem"]
    p = unit_from_bearing(225)
    return arc_options(*from_arc_for_all_friction(p, "N"), parse_arcs(item))


def ty_track_statements(item):
    """(1) mostly clockwise along the edge; (2) through the centre; (3) SW edge -> NW; (4) anticlockwise flow;
    (5) due east -> north."""
    # crossing the centre would need a component towards it; the steering flow is purely along the edge
    towards_centre = any(sp.simplify(steering(position(b)).dot(-position(b))) > 0 for b in (0, 90, 180, 270, 225))
    return [
        high_turning_sense() == "cw",
        towards_centre,
        moves_towards(position(225), 315),
        high_turning_sense() == "ccw",
        moves_towards(position(90), 0),
    ]


def ty_impact_statements(item):
    """(1) same everywhere; (2) track, terrain, circulation; (3) windward lifting rain; (4) weakens after
    landfall; (5) no strong wind after the eye."""
    # (5): on the far side of the eye the wind is again strong (the ring of strongest wind surrounds the eye) and
    # reversed: recompute the reversal for a station the centre crosses (west of it before, east after).
    before = around_low(vec(-1, 0), "N", 1)
    after = around_low(vec(1, 0), "N", 1)
    reversed_ = sp.simplify(before + after) == sp.zeros(2, 1)
    strong_again = STRUCTURE["strongest_wind"] == "just_outside_centre" and reversed_
    return [
        len(IMPACT_FACTORS) == 0,
        IMPACT_FACTORS == {"track", "terrain", "circulation"},
        WINDWARD_LIFTING_RAIN,
        WEAKENS_AFTER_LANDFALL and FORMATION_CONDITIONS["warm_sea"],
        not strong_again,
    ]


def ty_eye_diameter(item):
    """The centre passes directly over: the station crosses one eye diameter in the calm spell."""
    zh, en = item["text"]["zh-tw"]["stem"], item["text"]["en"]["stem"]
    vz = int(re.search(r"每小時 \$(\d+)\$ km", zh).group(1))
    ve = int(re.search(r"\$(\d+)\$ km per hour", en).group(1))
    tz = int(re.search(r"共經過 \$(\d+)\$ 小時", zh).group(1))
    te = int(re.search(r"\$(\d+)\$ hours pass", en).group(1))
    assert (vz, tz) == (ve, te)
    d = F(vz) * F(tz)
    assert d.denominator == 1
    return int(d)


def ty_sh_station_east(item):
    """Southern Hemisphere low, station due east of the centre; options are 90-degree 'from' arcs."""
    assert "南半球" in item["text"]["zh-tw"]["stem"] and "正東方" in item["text"]["zh-tw"]["stem"]
    p = unit_from_bearing(90)
    return arc_options(*from_arc_for_all_friction(p, "S"), parse_arcs(item))
