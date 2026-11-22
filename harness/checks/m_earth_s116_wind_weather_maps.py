"""Checks for src/data/items/earth/s116-wind-weather-maps.yaml (116 sprint: EIb-Ⅴc-5 pressure gradient force,
Coriolis force, friction and wind; EIb-Ⅴc-6 reading weather maps).

How the keys are recomputed (never from item["answer"]):
- A small force-balance engine. Horizontal vectors are (east, north) pairs of exact SymPy numbers. A steady
  wind v satisfies  PGF + Coriolis + friction = 0, with
    PGF       = P * g            (g: unit vector from high towards low, perpendicular to the isobars),
    Coriolis  = f * rot(v)       (perpendicular to v: to its right in the Northern Hemisphere, left in the South),
    friction  = -k * v           (opposite to v; k = 0 high above the ground),
  and v is solved exactly from this linear system. This only encodes the qualitative 必修 statements
  (directions, "bigger wind, bigger Coriolis", "friction opposes the wind"); no formula is taught.
- Wind directions on a compass: bearings in degrees clockwise from north. A wind is NAMED by where it
  comes from (bearing + 180). Geostrophic wind: k = 0. Near-surface wind: some k > 0 that the stem does not
  give, so an option is true only if it is the wind for SOME friction ratio r = k/f > 0 (solved exactly).
- Circulation around a centre: the sign of the cross product (turning sense) and of the dot product with the
  position (inflow or outflow), checked at several points and several friction ratios.
- Weather and map-reading facts are small tables, one source comment per fact.
"""

from __future__ import annotations

import re
from fractions import Fraction as F

import sympy as sp


def stem_ints(item: dict, zh_pat: str, en_pat: str) -> tuple[int, ...]:
    """Integers a stem states, parsed from both locales; they must agree."""
    mz = re.search(zh_pat, item["text"]["zh-tw"]["stem"])
    me = re.search(en_pat, item["text"]["en"]["stem"])
    assert mz and me, (zh_pat, en_pat)
    vz, ve = tuple(int(g) for g in mz.groups()), tuple(int(g) for g in me.groups())
    assert vz == ve, (vz, ve)
    return vz

# --- force facts (source comments per fact) ----------------------------------------------------------
# nat:EIb-Vc-5 keyConcepts: "Qualitative meaning, size and direction of each force; no formulas", "Force
# diagrams: geostrophic vs near-surface wind". The individual directions below are standard 必修地科 content
# (listed in the chapter report as standard facts not quoted in the sources):
# - PGF: perpendicular to the isobars, from high to low; bigger where the isobars are closer.
# - Coriolis: perpendicular to the motion, right of it in the Northern Hemisphere, left in the Southern;
#   changes direction only; zero for still air, bigger for faster wind; zero at the equator.
# - friction: opposite to the wind's motion; bigger over rough land than over the sea.
FORCE_FACTS = {
    ("pgf", "perpendicular_to_isobars"): True,
    ("pgf", "points_to"): "low",
    ("coriolis", "side_N"): "right",
    ("coriolis", "side_S"): "left",
    ("friction", "relative_to_wind"): "opposite",
}


def vec(e, n):
    return sp.Matrix([sp.nsimplify(e), sp.nsimplify(n)])


def unit_from_bearing(b) -> sp.Matrix:
    """Unit vector (east, north) pointing towards compass bearing b (degrees clockwise from north)."""
    r = sp.pi * sp.nsimplify(b) / 180
    return sp.Matrix([sp.sin(r), sp.cos(r)])


def rot(hemisphere: str) -> sp.Matrix:
    """Matrix turning a velocity into the Coriolis direction: right of it (N) or left of it (S)."""
    side = FORCE_FACTS[("coriolis", f"side_{hemisphere}")]
    # right of (x, y) is (y, -x); left of it is (-y, x)
    return sp.Matrix([[0, 1], [-1, 0]]) if side == "right" else sp.Matrix([[0, -1], [1, 0]])


def steady_wind(g: sp.Matrix, hemisphere: str, r, P=1, f=1) -> sp.Matrix:
    """Solve P*g + f*rot(v) - k*v = 0 for v, with k = r*f (r = 0: geostrophic)."""
    assert FORCE_FACTS[("friction", "relative_to_wind")] == "opposite"
    k = sp.nsimplify(r) * f
    A = f * rot(hemisphere) - k * sp.eye(2)
    return sp.simplify(A.LUsolve(-P * g))


def same_direction(u: sp.Matrix, w: sp.Matrix) -> bool:
    cross = sp.simplify(u[0] * w[1] - u[1] * w[0])
    dot = sp.simplify(u.dot(w))
    return cross == 0 and bool(dot > 0)


def pgf_unit(towards_low_bearing) -> sp.Matrix:
    assert FORCE_FACTS[("pgf", "points_to")] == "low"
    return unit_from_bearing(towards_low_bearing)


def wind_to_options(towards_low_bearing, hemisphere: str, surface: bool, to_bearings) -> list[bool]:
    """For each option (a bearing the wind blows TO), is it the steady wind?
    Geostrophic: r = 0 exactly. Surface: true iff some friction ratio r > 0 gives exactly that direction."""
    g = pgf_unit(towards_low_bearing)
    out = []
    for b in to_bearings:
        u = unit_from_bearing(b)
        if not surface:
            out.append(same_direction(steady_wind(g, hemisphere, 0), u))
            continue
        r = sp.Symbol("r", positive=True)
        v = steady_wind(g, hemisphere, r)
        sols = sp.solve(sp.Eq(sp.simplify(v[0] * u[1] - v[1] * u[0]), 0), r)
        out.append(any(same_direction(v.subs(r, s), u) for s in sols if s.is_positive))
    return out


def from_to(from_bearing) -> int:
    """A wind is named by where it comes from; it blows towards the opposite bearing."""
    return (from_bearing + 180) % 360


COMPASS = {"北": 0, "東北": 45, "東": 90, "東南": 135, "南": 180, "西南": 225, "西": 270, "西北": 315}

# --- circulation around a centre ---------------------------------------------------------------------
RATIOS = [F(1, 4), F(1, 2), 1, 2]  # several friction ratios: the answer must not depend on the unknown one
POSITIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # east, north, west, south of the centre


def circulation(centre: str, hemisphere: str) -> tuple[str, str]:
    """(turning sense seen from above, inflow/outflow) of the near-surface wind around a closed low or high."""
    seen = set()
    for r in RATIOS:
        for px, py in POSITIONS:
            p = vec(px, py)
            g = -p if centre == "low" else p  # PGF points to the lower pressure: the centre of a low, away from a high
            v = steady_wind(g, hemisphere, r)
            cross = sp.simplify(p[0] * v[1] - p[1] * v[0])
            dot = sp.simplify(p.dot(v))
            assert cross != 0 and dot != 0
            seen.add(("ccw" if cross > 0 else "cw", "in" if dot < 0 else "out"))
    assert len(seen) == 1, seen
    return seen.pop()


# --- weather at highs and lows (source comments per fact) --------------------------------------------
# nat:EIb-Vc-5 keyConcepts: "Convergence and divergence at surface highs and lows, and the resulting weather".
# nat:EIb-Vc-4 keyConcepts: rising air cools, may saturate and forms cloud (the previous chapter).
# Sinking air is compressed and warms, so it moves away from saturation: standard 必修 content (listed in the
# chapter report).
VERTICAL = {"in": "rising", "out": "sinking"}  # surface convergence must rise; surface divergence is fed by sinking
WEATHER = {"rising": "cloud_rain", "sinking": "clear"}


def weather_at(centre: str, hemisphere: str = "N") -> tuple[str, str, str]:
    sense, flow = circulation(centre, hemisphere)
    vertical = VERTICAL[flow]
    return sense, vertical, WEATHER[vertical]


# --- weather-map facts (source comments per fact) ----------------------------------------------------
# nat:EIb-Vc-6 keyConcepts: "Maps are drawn from station observations"; "Isobars show highs, lows and major
# weather systems; satellite cloud images can supplement" (so they do not replace station data).
# A closed isobar pattern with pressure falling towards the centre is a low (rising: a high): definition,
# standard 必修 content. Station pressures are reduced to sea level before isobars are drawn: standard 必修
# content (listed in the chapter report).
MAP_FACTS = {
    "drawn_from_simultaneous_station_obs": True,
    "closed_falling_to_centre_is_low": True,
    "satellite_replaces_station_pressure": False,
    "pressures_reduced_to_sea_level": True,
}


def pgf_size(dp, dx) -> F:
    """Size of the PGF up to a constant: pressure difference per distance (the qualitative 'closer isobars,
    bigger force' rule, made exact only to compare)."""
    return abs(F(dp)) / F(dx)


# --- item checks -------------------------------------------------------------------------------------

def ww_turn_geostrophic(item):
    """Upper air, NH, straight E-W isobars, high to the south, low to the north: the low lies to the north."""
    to_bearings = [0, 90, 270, 180, 45]  # the five options' directions, in order
    assert len(item["text"]["zh-tw"]["options"]) == len(to_bearings)
    return wind_to_options(0, "N", surface=False, to_bearings=to_bearings)


def ww_turn_winter(item):
    """Near-surface, NH, isobars E-W, higher to the north: the low lies to the south (PGF bearing 180)."""
    names = ["東北", "西南", "東南", "西北", "北"]  # options: 東北風, 西南風, 東南風, 西北風, 北風 (where they come from)
    assert len(item["text"]["zh-tw"]["options"]) == len(names)
    return wind_to_options(180, "N", surface=True, to_bearings=[from_to(COMPASS[x]) for x in names])


def ww_geostrophic_sh(item):
    """Upper air, Southern Hemisphere, straight N-S isobars, high to the east, low to the west (PGF bearing 270)."""
    assert "南半球" in item["text"]["zh-tw"]["stem"] and "Southern Hemisphere" in item["text"]["en"]["stem"]
    names = ["北", "東", "南", "西", "東南"]  # options: 北風, 東風, 南風, 西風, 東南風
    assert [x + "風" for x in names] == item["text"]["zh-tw"]["options"]
    return wind_to_options(270, "S", surface=False, to_bearings=[from_to(COMPASS[x]) for x in names])


def ww_force_statements(item):
    """(1) PGF perpendicular to isobars, high to low; (2) closer isobars, bigger PGF; (3) Coriolis speeds the
    wind up; (4) SH Coriolis to the left; (5) friction along the wind."""
    # (2): same 4 hPa over a shorter distance against a longer one (any two distances give the same verdict)
    denser_bigger = pgf_size(4, 100) > pgf_size(4, 200)
    # (3): the Coriolis force is perpendicular to the velocity, so it does no work on the air: dot product 0
    v = vec(3, 1)
    coriolis_changes_speed = sp.simplify((rot("N") * v).dot(v)) != 0
    return [
        FORCE_FACTS[("pgf", "perpendicular_to_isobars")] and FORCE_FACTS[("pgf", "points_to")] == "low",
        denser_bigger,
        coriolis_changes_speed,
        FORCE_FACTS[("coriolis", "side_S")] == "left",
        FORCE_FACTS[("friction", "relative_to_wind")] == "same",
    ]


def ww_sh_low(item):
    """Southern Hemisphere surface low."""
    options = [("cw", "in"), ("ccw", "in"), ("cw", "out"), ("ccw", "out"), (None, "in")]
    assert len(item["text"]["zh-tw"]["options"]) == len(options)
    actual = circulation("low", "S")
    return [opt == actual for opt in options]


def ww_highs_lows_weather(item):
    """NH surface: (1) low converges; (2) low rises, cloud and rain; (3) high sinks, clear;
    (4) high turns anticlockwise outwards; (5) low sinks."""
    low_sense, low_vertical, low_weather = weather_at("low")
    high_sense, high_vertical, high_weather = weather_at("high")
    _, low_flow = circulation("low", "N")
    _, high_flow = circulation("high", "N")
    return [
        low_flow == "in",
        low_vertical == "rising" and low_weather == "cloud_rain",
        high_vertical == "sinking" and high_weather == "clear",
        high_sense == "ccw" and high_flow == "out",
        low_vertical == "sinking",
    ]


def ww_ring_pressure(item):
    """Isobars every step hPa around a low; innermost ring and the station's ring (counting outwards) from the stem."""
    (step,) = stem_ints(item, r"每 \$(\d+)\$ hPa 畫一條", r"isobar is drawn every \$(\d+)\$ hPa")
    (inner,) = stem_ints(item, r"最內圈是 \$(\d+)\$ hPa", r"the innermost is \$(\d+)\$ hPa")
    (n,) = stem_ints(item, r"第 \$(\d+)\$ 圈", r"on the \$(\d+)\$th isobar")
    rings = [inner + step * i for i in range(n + 5)]  # pressure rises outwards from a low
    return rings[n - 1]


def ww_station_line(item):
    """Five stations equally spaced on a line perpendicular to the isobars (illustrative); pressures and spacing
    from the stem."""
    zh, en = item["text"]["zh-tw"]["stem"], item["text"]["en"]["stem"]
    pz = [int(x) for x in re.findall(r"\$(\d{3,4})\$", zh.split("依序是")[1])]
    pe = [int(x) for x in re.findall(r"\$(\d{3,4})\$", en.split("in order,")[1])]
    assert len(pz) == 5 and pz == pe, (pz, pe)
    (dx,) = stem_ints(item, r"每兩站相距 \$(\d+)\$ km", r"\$(\d+)\$ km apart")
    pressures = pz
    sizes = [pgf_size(b - a, dx) for a, b in zip(pressures, pressures[1:])]
    top = max(sizes)
    all_equal = len(set(sizes)) == 1
    segs = [s == top and sizes.count(top) == 1 for s in sizes]
    return segs + [all_equal]


def ww_map_statements(item):
    """(1) drawn from simultaneous station data; (2) closed, falling to the centre: a low; (3) satellite images
    make station pressures unnecessary; (4) closer isobars, weaker wind; (5) reduced to sea level first."""
    closer_weaker = pgf_size(4, 100) < pgf_size(4, 200)  # same pressure step, shorter distance
    return [
        MAP_FACTS["drawn_from_simultaneous_station_obs"],
        MAP_FACTS["closed_falling_to_centre_is_low"],
        MAP_FACTS["satellite_replaces_station_pressure"],
        closer_weaker,
        MAP_FACTS["pressures_reduced_to_sea_level"],
    ]


def ww_land_sea(item):
    """Same latitude (same f), same isobar spacing (same PGF), friction ratio bigger over land than over sea."""
    g = pgf_unit(0)
    geo = steady_wind(g, "N", 0)
    r_sea, r_land = F(1, 4), F(1, 1)  # any 0 < r_sea < r_land gives the same comparison
    out = {}
    for name, r in (("sea", r_sea), ("land", r_land)):
        v = steady_wind(g, "N", r)
        speed2 = sp.simplify(v.dot(v))
        cos_angle = sp.simplify(v.dot(geo) / sp.sqrt(v.dot(v) * geo.dot(geo)))  # larger cos: smaller angle
        out[name] = (speed2, cos_angle)
    sea_faster = out["sea"][0] > out["land"][0]
    sea_smaller_angle = out["sea"][1] > out["land"][1]
    same = out["sea"] == out["land"]
    land_faster = out["land"][0] > out["sea"][0]
    land_smaller_angle = out["land"][1] > out["sea"][1]
    # options: each names the faster place and that place's angle with the isobars
    return [
        sea_faster and sea_smaller_angle,
        sea_faster and not sea_smaller_angle and not same,
        land_faster and land_smaller_angle,
        land_faster and not land_smaller_angle and not same,
        same,
    ]
