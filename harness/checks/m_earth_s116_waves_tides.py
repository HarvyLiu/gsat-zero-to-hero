"""Checks for src/data/items/earth/s116-waves-tides.yaml (116 sprint: EIc-Ⅴc-2 waves and coasts;
EIc-Ⅴc-3, EIc-Ⅴc-4 tides from the Sun–Earth–Moon and tidal currents in the Taiwan Strait).

How the keys are recomputed (never from item["answer"]):
- Waves: a small decay model (relative height exp(-d / L) with the decay length L growing with the
  wavelength; only that monotonic rule is used) and fact tables with a source comment each.
- Coasts: a crest line is advanced over a depth profile with a speed that grows with depth (only the
  monotonic rule "shallower is slower" is used); the bend of the crest and the convergence of the wave
  rays are read off the computed crest, and wavelength / height follow from a fixed period and a fixed
  energy flux.
- Tides: tidal ranges and times from the stem's numbers with exact Rationals; spring and neap tides from
  the sum of a Moon part M and a Sun part S with 0 < S < M (symbolic: the truth holds for every such
  ratio, not for one chosen number); the lunar-day delay from the synodic month.
- Taiwan Strait: a 1-D model in which the tidal wave enters at both ends and the flood current runs
  from each entry towards the meeting point.

Facts used, with their sources:
- Waves are raised mainly by wind on the sea surface, and also by submarine landslides and earthquakes;
  longer wavelengths lose energy more slowly and travel farther (nat.json EIc-Ⅴc-2 keyConcepts; slice
  verification.final_units order 20).
- Swell = waves that have left the generating wind area (樂詞網 湧浪 swell, slice terminology).
- The Sun–Earth–Moon system drives the tides and the Moon is the main cause (nat.json EIc-Ⅴc-3/4;
  slice research.common_misconceptions).
- The tidal wave entering the Taiwan Strait from both ends and meeting in the middle, with flood
  currents towards the middle: standard Taiwan textbook explanation, NOT in the sources; the item states
  it in the stem, and it is listed for the owner.
- Synodic month 29.5 days (standard 國中 Fb-Ⅳ-3 content, not in the sources; listed for the owner).
- Two bulges (near and far side), shallow water slows waves, wave period unchanged on shoaling: standard
  textbook content, not in the sources; listed for the owner.
"""

from __future__ import annotations

import re

import sympy as sp
from sympy import Rational as Q

# --- waves --------------------------------------------------------------------------------------------

# EIc-Ⅴc-2: the causes of sea waves (waves of a few seconds' period).
WAVE_CAUSES = {"wind", "submarine_landslide", "submarine_earthquake"}
# Not causes of such waves: salinity differences (not a wave source in EIc-Ⅴc-2); the Moon's pull, which
# makes the tide, a rise and fall of about half a day (EIc-Ⅴc-3), not waves every few seconds.
TIDE_PERIOD_HOURS = Q(1242, 100)  # semidiurnal tide, about 12 h 25 min (half a lunar day, see below)
SEA_WAVE_PERIOD_MAX_HOURS = Q(1, 60)  # "every few seconds": far below a minute


def makes_sea_waves(cause: str) -> bool:
    if cause == "moon_pull":
        # the Moon's pull makes a rise and fall with the tidal period, not every few seconds
        return TIDE_PERIOD_HOURS <= SEA_WAVE_PERIOD_MAX_HOURS
    return cause in WAVE_CAUSES


def decay_length(wavelength):
    """Any length scale that grows with wavelength (EIc-Ⅴc-2: longer waves decay more slowly)."""
    return 5 * wavelength


def relative_height(wavelength, distance):
    return sp.exp(-sp.Integer(distance) / decay_length(sp.Integer(wavelength)))


def longer_travels_farther() -> bool:
    """Compare a short and a long wave over a range of distances (positive)."""
    short, long_ = 10, 100
    return all(relative_height(long_, d) > relative_height(short, d) for d in (100, 500, 1000, 2000))


# Properties of wind waves vs swell (EIc-Ⅴc-2; 樂詞網 湧浪 swell). 'wavelength' follows from the decay
# rule: waves that have left the wind area and travelled are the long ones.
WIND_WAVE = {"in_wind_area": True, "crests": "sharp_irregular"}
SWELL = {"in_wind_area": False, "crests": "smooth_regular", "wavelength": "longer"}
# A wave carries energy; in deep water the water mostly circles in place (國中 Ka-Ⅳ-1 wave basics).
WATER_TRAVELS_WITH_WAVE = False


# --- coasts -------------------------------------------------------------------------------------------


def speed(depth):
    """Wave speed grows with depth: shallower is slower (standard; only monotonicity is used)."""
    return sp.Integer(depth)


def advance_crest(depths: list[int], dt: int = 10):
    """A straight crest y = 0 across x = 0..n-1 advances in +y with the local speed for dt."""
    return [(x, speed(d) * dt) for x, d in enumerate(depths)]


def headland_model():
    """Headland in the middle: shallower water in front of it than in front of the two bays."""
    depths = [6, 5, 4, 2, 4, 5, 6]  # x = 3 is the headland
    crest = advance_crest(depths)
    mid = len(depths) // 2
    # direction of travel = normal of the crest, pointing forward (+y); for a segment from p to q the
    # forward normal is (-(qy - py), qx - px)
    def ray(i):
        (px, py), (qx, qy) = crest[i], crest[i + 1]
        return (-(qy - py), qx - px)

    left = ray(mid - 2)  # a segment on the left of the headland
    right = ray(mid + 1)  # a segment on the right
    bent = len({y for _, y in crest}) > 1
    converge_on_headland = left[0] > 0 and right[0] < 0  # left rays tilt right, right rays tilt left
    return {"bent": bent, "converge_on_headland": converge_on_headland}


def shoaling(deep: int, shallow: int):
    """Period fixed: wavelength = speed * period shrinks; energy flux (energy * speed) fixed: energy
    per length grows as 1/speed, height grows with it (height^2 ~ energy)."""
    period = 1
    v_d, v_s = speed(deep), speed(shallow)
    wavelength_ratio = (v_s * period) / (v_d * period)
    height_ratio = sp.sqrt(v_d / v_s)
    return {"slower": v_s < v_d, "wavelength_shorter": wavelength_ratio < 1, "taller": height_ratio > 1}


# --- tides --------------------------------------------------------------------------------------------

M, S = sp.symbols("M S", positive=True)
# The Moon is the main cause (EIc-Ⅴc-3): every check below holds for all 0 < S < M (see holds_for_all).


def tidal_range(theta_deg):
    """Range of the Moon part (amplitude M) plus the Sun part (amplitude S) when the Moon's direction
    is theta from the Sun's. The two semidiurnal parts are in step at 0° and 180°, opposite at 90°:
    combined amplitude sqrt(M^2 + S^2 + 2 M S cos 2θ); the range is twice that."""
    th = sp.Rational(theta_deg) * sp.pi / 180
    return 2 * sp.sqrt(M**2 + S**2 + 2 * M * S * sp.cos(2 * th))


# The phase names and the Moon–Sun angle (國中 Fb-Ⅳ-3 moon phases).
PHASE_ANGLE = {"新月": 0, "上弦": 90, "滿月": 180, "下弦": 270}


def holds_for_all(lhs, op: str, rhs) -> bool:
    """Decide lhs <op> rhs (op: 'gt', 'lt', 'eq') for every 0 < S < M, by writing M = S + d, d > 0.
    Refuses (AssertionError) if the truth depends on the ratio."""
    d = sp.Symbol("d", positive=True)
    diff = sp.simplify((sp.sympify(lhs) - sp.sympify(rhs)).subs(M, S + d))
    pred = {"gt": sp.Q.positive, "lt": sp.Q.negative, "eq": sp.Q.zero}[op]
    res = sp.ask(pred(diff))
    if res is None and op != "eq":
        res = sp.ask(pred(sp.factor(diff)))
    assert res is not None, f"undecided: {lhs} {op} {rhs}"
    return bool(res)


def range_cmp(a_deg, b_deg, op: str) -> bool:
    # ranges are positive, so compare their squares
    return holds_for_all(sp.expand(tidal_range(a_deg) ** 2), op, sp.expand(tidal_range(b_deg) ** 2))


def largest_range_phases() -> set[str]:
    out = set()
    for name, ang in PHASE_ANGLE.items():
        if all(name == other or not range_cmp(PHASE_ANGLE[other], ang, "gt") for other in PHASE_ANGLE):
            out.add(name)
    return out


def smallest_range_phases() -> set[str]:
    out = set()
    for name, ang in PHASE_ANGLE.items():
        if all(name == other or not range_cmp(PHASE_ANGLE[other], ang, "lt") for other in PHASE_ANGLE):
            out.add(name)
    return out


SYNODIC_MONTH_DAYS = Q(59, 2)  # 29.5 days, standard (not in the sources)


def lunar_day_minutes():
    """Earth must turn 1 + 1/(synodic - 1) days' worth to face the Moon again: 24 h * P/(P - 1)."""
    p = SYNODIC_MONTH_DAYS
    return 24 * 60 * p / (p - 1)


def spring_tides_per_month():
    """Spring tides at 0° and 180°: two per synodic month (positions counted from the phase table)."""
    return len(largest_range_phases())


def minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def hhmm_parts(total: int) -> tuple[str, str]:
    total %= 24 * 60
    return (f"{total // 60:02d}", f"{total % 60:02d}")


def decimal_cells(x) -> tuple[str, str]:
    """A non-negative value with one decimal place → ('integer part', 'tenths digit') for ①.②."""
    x = sp.Rational(x)
    whole = int(sp.floor(x))
    tenth = (x - whole) * 10
    assert tenth.is_integer and 0 <= tenth < 10, f"{x} has more than one decimal place"
    return (str(whole), str(int(tenth)))


# --- items --------------------------------------------------------------------------------------------


def wt_turn_distant_typhoon(item: dict) -> list[bool]:
    """q-turn: a distant typhoon, little local wind, big waves at the beach. Options: (1) the typhoon's low
    lifts the sea here; (2) swell from the typhoon's winds; (3) water flows here from the typhoon; (4) the
    typhoon's winds blow high above here and raise the waves; (5) the typhoon enlarges the tide here."""
    typhoon_here = False  # the stem: the typhoon (with its low pressure and strong winds) is still far away
    local_wind_strong = False  # the stem: little wind here
    distant_wind_area = True  # the typhoon's strong winds far away
    swell_reaches = distant_wind_area and longer_travels_farther()
    o1 = typhoon_here  # its low pressure is where the typhoon is, not here
    o2 = swell_reaches
    o3 = WATER_TRAVELS_WITH_WAVE  # a wave carries energy; the water circles in place
    # waves are raised by wind on the sea SURFACE (EIc-Ⅴc-2); wind high above does not touch the sea, and
    # the surface wind here is light
    o4 = "wind_aloft" in WAVE_CAUSES or local_wind_strong
    o5 = makes_sea_waves("moon_pull")  # tides (Moon and Sun) rise and fall every half day, not every few seconds
    return [o1, o2, o3, o4, o5]


def wt_spring_phase(item: dict) -> list[bool]:
    """q-spring: around which phases is the tidal range largest?"""
    big = largest_range_phases()
    same_every_day = range_cmp(0, 90, "eq")
    return [
        big == {"新月", "滿月"},
        big == {"滿月"},
        big == {"新月"},
        big == {"上弦", "下弦"},
        same_every_day,
    ]


def wt_wind_wave_vs_swell(item: dict) -> list[bool]:
    """q1: wind waves vs swell."""
    short_decays_slower = not longer_travels_farther()
    return [
        (not SWELL["in_wind_area"]) and SWELL["wavelength"] == "longer" and longer_travels_farther(),
        short_decays_slower,
        SWELL["in_wind_area"],  # 'there must be a strong local wind'
        WIND_WAVE["crests"] == "smooth_regular",
        WATER_TRAVELS_WITH_WAVE,
    ]


def wt_wave_causes(item: dict) -> list[bool]:
    """q2: which of these make sea waves?"""
    return [makes_sea_waves(c) for c in ("wind", "submarine_landslide", "submarine_earthquake", "salinity", "moon_pull")]


def tide_record(item: dict) -> list[tuple[str, str, Q]]:
    """The stem's record [(time, 'high'|'low', level)], parsed from both locales; they must agree."""
    zh = [(t, "high" if k == "滿潮" else "low", Q(v)) for t, k, v in
          re.findall(r"(\d\d:\d\d)(滿潮|乾潮) \$(-?[\d.]+)\$ 公尺", item["text"]["zh-tw"]["stem"])]
    en = [(t, k, Q(v)) for k, v, t in re.findall(r"(high|low) tide \$(-?[\d.]+)\$ m at (\d\d:\d\d)", item["text"]["en"]["stem"])]
    assert len(zh) >= 3 and zh == en, (zh, en)
    assert all(a[1] != b[1] for a, b in zip(zh, zh[1:])), "high and low tides must alternate"
    return zh


def wt_island_range(item: dict) -> tuple[str, str]:
    """q3: the stem's record; the largest range between neighbouring high and low tides."""
    record = tide_record(item)
    ranges = [abs(a[2] - b[2]) for a, b in zip(record, record[1:])]
    best = max(ranges)
    assert ranges.count(best) == 1
    return decimal_cells(best)


def wt_next_low_tide(item: dict) -> tuple[str, str, str, str]:
    """q4: the first high tide on several days in a row (from the stem); extrapolate the same daily delay
    to the day asked."""
    zh, en = item["text"]["zh-tw"]["stem"], item["text"]["en"]["stem"]
    days_z = {int(d): minutes(t) for d, t in re.findall(r"第(\d)天(\d\d:\d\d)", zh)}
    days_e = {int(d): minutes(t) for t, d in re.findall(r"(\d\d:\d\d) on day (\d)", en)}
    assert len(days_z) >= 3 and days_z == days_e, (days_z, days_e)
    target_z = int(re.search(r"第(\d)天的第一次滿潮大約", zh).group(1))
    target_e = int(re.search(r"on day (\d) is at about", en).group(1))
    assert target_z == target_e and target_z not in days_z
    ds = sorted(days_z)
    delays = {days_z[b] - days_z[a] for a, b in zip(ds, ds[1:])}
    assert len(delays) == 1, "the stem must show a steady daily delay"
    delay = delays.pop()
    # the delay matches the lunar day (about 24 h 50 min): the tide follows the Moon
    assert abs(lunar_day_minutes() - 24 * 60 - delay) < 2
    t = days_z[ds[-1]] + delay * (target_z - ds[-1])
    h, m = hhmm_parts(t)
    return (h[0], h[1], m[0], m[1])


def wt_quarter_moon(item: dict) -> list[bool]:
    """q5: first-quarter moon (90°)."""
    q = PHASE_ANGLE["上弦"]
    return [
        "上弦" in smallest_range_phases(),
        "上弦" in largest_range_phases(),
        range_cmp(q, PHASE_ANGLE["新月"], "eq"),
        holds_for_all(tidal_range(q), "eq", 0),
        range_cmp(q, PHASE_ANGLE["滿月"], "gt"),
    ]


def wt_moon_statements(item: dict) -> list[bool]:
    """q6: statements on the Sun, Earth, Moon and tides."""
    moon_main = holds_for_all(M, "gt", S)
    two_bulges = True  # near and far side (standard; chapter StudentAsks)
    two_springs = spring_tides_per_month() == 2 and len(smallest_range_phases()) == 2
    sun_no_effect = False  # S > 0 by the symbol's assumption: the Sun part is not zero
    assert sp.ask(sp.Q.positive(S))
    spring_only_full = largest_range_phases() == {"滿月"}
    return [moon_main, two_bulges, two_springs, sun_no_effect, spring_only_full]


def wt_headland(item: dict) -> list[bool]:
    """q7: a straight crest line approaching a headland whose front water is shallower."""
    h = headland_model()
    s = shoaling(deep=6, shallow=2)
    return [
        s["slower"] and h["bent"] and h["converge_on_headland"],
        h["bent"] and not h["converge_on_headland"],
        not s["slower"] and not s["wavelength_shorter"],
        not h["bent"],
        not s["taller"],
    ]


def wt_strait_flood_current(item: dict) -> list[bool]:
    """q8: tidal wave enters at both ends (north y = 10, south y = 0) and meets at y = 5. Flood current
    runs from each entry towards the meeting point; ebb is the reverse."""
    north, south, meet = 10, 0, 5

    def flood_dir(entry):
        return "N" if meet - entry > 0 else "S"

    n, s_ = flood_dir(north), flood_dir(south)
    ebb_reverses = True  # ebb is the reverse of flood (semidiurnal tide, chapter)
    return [
        (n, s_) == ("S", "N"),
        (n, s_) == ("N", "N"),
        (n, s_) == ("S", "S"),
        (n, s_) == ("N", "S"),
        not ebb_reverses,
    ]


# The lunar-day delay used in the chapter (about 50 minutes) is checked here so a change to the
# constant cannot slip by.
assert abs(lunar_day_minutes() - 24 * 60 - 50) < 2
