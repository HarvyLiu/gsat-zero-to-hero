"""Checks for src/data/items/earth/s116-climate-change.yaml (116 sprint: ENb-Ⅴc-1~4: climate change on many
timescales, glacial and interglacial periods, human activity as the main cause of recent rapid warming,
adaptation).

How the keys are recomputed (never from item["answer"]):
- Timescales: a table of the order of magnitude (log10 of years) over which each driver acts. The drivers
  are the ones nat:ENb-Vc-1 keyConcepts name (plate motion, mountain building, solar activity); the
  ranges are standard 必修 content, listed in the chapter report. A driver can explain a change that
  happens within T years only if its shortest timescale is at most T.
- Sea level: a water budget. Total water is conserved; water held as ice on land is missing from the
  ocean, and the change of sea level is that volume spread over the stated ocean area (exact Fractions).
- Glacial vs interglacial effects: a small model in which the temperature at a place falls with altitude
  (only the sign is used, no rate: the 說明 excludes lapse rates) and the whole profile shifts down in a
  glacial period; a cold-tolerant forest lives where it is cold enough.
- Rates and the temperature distribution: exact arithmetic on the stem's numbers, parsed from both
  locales, which must agree.
- Human cause and mitigation/adaptation: fact tables, each with a source comment.
"""

from __future__ import annotations

import re
from fractions import Fraction as F

import sympy as sp


def stem_numbers(item: dict, zh_pat: str, en_pat: str) -> tuple[F, ...]:
    """Numbers a stem states, parsed from both locales; they must agree."""
    mz = re.search(zh_pat, item["text"]["zh-tw"]["stem"])
    me = re.search(en_pat, item["text"]["en"]["stem"])
    assert mz and me, (zh_pat, en_pat)
    vz, ve = tuple(F(g) for g in mz.groups()), tuple(F(g) for g in me.groups())
    assert vz == ve, (vz, ve)
    return vz


# --- timescales ----------------------------------------------------------------------------------

# log10(years): (shortest, longest) span over which each driver noticeably changes climate.
# Drivers from nat:ENb-Vc-1 keyConcepts ("plate motion, mountain building, solar activity"); spans are
# standard 必修 content (plates move a few cm a year, so climate zones are crossed over tens of millions
# of years; mountain ranges rise over millions of years; solar activity varies over years to centuries).
TIMESCALE = {
    "plate_motion": (7, 9),
    "mountain_building": (6, 7),
    "solar_activity": (0, 2.5),
}

# nat:ENb-Vc-1/2 (title: 多重時間尺度、冰期間冰期): glacial and interglacial periods alternated in Earth's
# past, long before humans; they are natural changes between cold and warm.
GLACIAL_CYCLES_NATURAL = True
GLACIAL_CYCLES_BEFORE_HUMANS = True


def can_act_within(driver: str, years: float) -> bool:
    return TIMESCALE[driver][0] <= sp.log(years, 10)


# --- water budget ---------------------------------------------------------------------------------


def sea_level_change_km(extra_land_ice_water_km3: F, ocean_area_km2: F) -> F:
    """Water conserved: water added to land ice leaves the ocean; spread over the ocean area."""
    return -F(extra_land_ice_water_km3) / F(ocean_area_km2)


def cc_turn_glacial_sea_level(item: dict) -> list[bool]:
    """q-turn: sea level at the coldest point of a glacial period. Options: much lower (water stored as
    ice on land); much higher (cold seawater expands); about the same (total water unchanged); much
    lower (seawater lost to space)."""
    # illustrative glacial budget: more ice on land than today (only the sign matters)
    dh = sea_level_change_km(F(10**7), F(3 * 10**8))
    lower = dh < 0
    # seawater, like most liquids in this range, contracts on cooling (standard; it does not expand)
    cold_water_expands = False
    # total water on Earth is conserved (no significant loss to space)
    water_lost_to_space = False
    return [
        lower and not water_lost_to_space,  # lower, and the reason (land ice) is the model's reason
        (not lower) and cold_water_expands,
        dh == 0,
        lower and water_lost_to_space,
    ]


def cc_timescale_statements(item: dict) -> list[bool]:
    """q1 (multi): (1) plates change a continent's latitude over tens of millions of years; (2) mountain
    building takes only years, so it explains recent decades; (3) solar activity acts over years to
    centuries; (4) natural drivers can never alternate cold and warm; (5) glacial/interglacial
    alternation began only in the last two hundred years."""
    s1 = can_act_within("plate_motion", 5 * 10**7)
    s2 = TIMESCALE["mountain_building"][0] <= 1 and can_act_within("mountain_building", 50)
    lo, hi = TIMESCALE["solar_activity"]
    s3 = lo <= 1 and hi >= 2  # from years (10^0..10^1) to centuries (10^2)
    s4 = not GLACIAL_CYCLES_NATURAL
    s5 = not GLACIAL_CYCLES_BEFORE_HUMANS
    return [bool(s1), bool(s2), s3, s4, s5]


SCI = r"\$(\d+(?:\.\d+)?)\\times10\^\{(\d+)\}\$"


def cc_two_glacials_difference(item: dict) -> tuple[str, ...]:
    """q2: two glacial periods store V1 and V2 km³ more water as land ice than today, ocean area A km²;
    how many metres lower was sea level in the second than in the first."""
    m1, e1, m2, e2, a, b = stem_numbers(
        item,
        SCI + r" 和 " + SCI + r" 立方公里.*?" + SCI + r" 平方公里",
        SCI + r" and " + SCI + r" cubic kilometres.*?" + SCI + r" square",
    )
    area = a * 10 ** int(b)
    h1 = sea_level_change_km(m1 * 10 ** int(e1), area)  # negative: below today
    h2 = sea_level_change_km(m2 * 10 ** int(e2), area)
    lower_by_m = (h1 - h2) * 1000
    assert lower_by_m > 0 and lower_by_m.denominator == 1
    s = str(int(lower_by_m))
    assert len(s) == 2
    return tuple(s)


# --- glacial effects on life ----------------------------------------------------------------------


def cc_mountain_forest(item: dict) -> list[bool]:
    """q3: a cold-tolerant forest lives where T(h) <= T_max; T falls with altitude h (sign only, slope
    k > 0 symbolic: no lapse rate is used) and a glacial period lowers T everywhere by d > 0. Options:
    spreads to lower altitudes; can only retreat higher; stays put; disappears (whole Earth frozen)."""
    h, t0, tmax = sp.symbols("h T0 Tmax", real=True)
    k_, d_ = sp.symbols("k d", positive=True)  # T falls with altitude; a glacial period is colder
    lower_limit_now = sp.solve(sp.Eq(t0 - k_ * h, tmax), h)[0]
    lower_limit_glacial = sp.solve(sp.Eq(t0 - d_ - k_ * h, tmax), h)[0]
    shift = sp.simplify(lower_limit_glacial - lower_limit_now)  # = -d/k
    moves_down = bool(shift.is_negative)
    # a glacial period is a colder period with expanded ice at high latitudes and on high mountains,
    # not a frozen Earth (nat:ENb-Vc-2; glossary earth.glacial-period)
    whole_earth_frozen = False
    # plant populations shift their range through seed dispersal (standard; chapter report)
    ranges_can_shift = True
    return [
        moves_down and ranges_can_shift,
        (not moves_down) and ranges_can_shift,
        not ranges_can_shift,
        whole_earth_frozen,
    ]


# glacial: land ice larger than today, sea level lower; interglacial: land ice smaller, sea level higher
# (nat:ENb-Vc-2 keyConcepts: glacial vs interglacial temperature and sea level). No source gives the size
# of the glacial fall, so the q4 stem STATES it as an assumption, and it is read from the stem below.


def cc_land_layer_on_shelf(item: dict) -> list[bool]:
    """q4: a land layer (roots of land plants, freshwater lake sediment) between marine layers on a sea
    floor about 50 m deep today; the stem assumes the glacial sea level was about F m lower than today.
    Options: glacial, lower sea level, exposed; interglacial, higher, exposed; glacial, higher, deeper
    sea; interglacial, lower, deeper sea."""
    (depth,) = stem_numbers(item, r"水深約 \$(\d+)\$ 公尺", r"about \$(\d+)\$ metres deep")
    (fall,) = stem_numbers(item, r"海平面比今天低約 \$(\d+)\$ 公尺", r"about \$(\d+)\$ metres lower than today")
    SEA_LEVEL_VS_TODAY = {"glacial": -fall, "interglacial": F(0)}  # interglacial: about today's level

    def exposed(period: str) -> bool:
        return SEA_LEVEL_VS_TODAY[period] < -depth

    def lower(period: str) -> bool:
        return SEA_LEVEL_VS_TODAY[period] < SEA_LEVEL_VS_TODAY[
            "interglacial" if period == "glacial" else "glacial"
        ]

    land_layer = True  # land plants and lake sediment form only on land
    return [
        land_layer and lower("glacial") and exposed("glacial"),
        land_layer and (not lower("interglacial")) and exposed("interglacial"),
        (not land_layer) and not lower("glacial"),
        (not land_layer) and lower("interglacial"),
    ]


# --- rates and the human cause --------------------------------------------------------------------


def cc_table_slopes(item: dict) -> tuple[str, ...]:
    """q5: a table of (year, concentration); ratio of the average rates over two stated spans."""
    zh, en = item["text"]["zh-tw"]["stem"], item["text"]["en"]["stem"]
    tz = {F(y): F(v) for y, v in re.findall(r"第(\d+)年是 \$(\d+)\$", zh)}
    te = {F(y): F(v) for v, y in re.findall(r"\$(\d+)\$ in year (\d+)", en)}
    assert tz == te and len(tz) == 4, (tz, te)
    sz = re.search(r"第(\d+)年到第(\d+)年的平均增加速率，約是第(\d+)年到第(\d+)年的", zh).groups()
    se = re.search(r"from year (\d+) to year (\d+) is about ① times that from year (\d+) to year (\d+)", en).groups()
    assert sz == se
    a0, a1, b0, b1 = (F(x) for x in sz)
    slope = lambda u, v: (tz[v] - tz[u]) / (v - u)  # noqa: E731
    ratio = slope(a0, a1) / slope(b0, b1)
    assert ratio.denominator == 1 and 0 < ratio < 10
    return (str(int(ratio)),)


# nat:ENb-Vc-3 keyConcepts: natural long-term drivers cannot fully explain the recent rapid change;
# human activity is the main factor. chemistry.greenhouse-effect (glossary, 樂詞網): more greenhouse gas
# strengthens the greenhouse effect; burning fossil fuels releases CO2 (chemistry/s116-environment-energy).
HUMAN_MAIN_FACTOR = True
FOSSIL_FUELS_ADD_GHG = True
# earth/s116-earth-history (habitable Earth): the greenhouse effect keeps the surface warm and is one of
# the conditions for liquid water and life; with none the surface would be far colder.
GREENHOUSE_EFFECT_KEEPS_SURFACE_WARM = True
RECENT_SPAN_YEARS = 100


def cc_human_cause_statements(item: dict) -> list[bool]:
    """q6 (multi): (1) plates and mountain building too slow for the last hundred years; (2) human
    activity is the main factor; (3) fossil fuels add greenhouse gases and strengthen the effect;
    (4) past natural cycles mean recent warming must be natural; (5) the greenhouse effect only harms,
    and without it the surface would suit life better."""
    s1 = not can_act_within("plate_motion", RECENT_SPAN_YEARS) and not can_act_within(
        "mountain_building", RECENT_SPAN_YEARS
    )
    return [bool(s1), HUMAN_MAIN_FACTOR, FOSSIL_FUELS_ADD_GHG, not HUMAN_MAIN_FACTOR, not GREENHOUSE_EFFECT_KEEPS_SURFACE_WARM]


def cc_cold_nights_ratio(item: dict) -> tuple[str, ...]:
    """q7: two tables of (daily minimum, days); ratio of days at or below the cold threshold,
    earlier / later."""
    zh = item["text"]["zh-tw"]["stem"]
    en = item["text"]["en"]["stem"]

    def tables(stem: str, sep: str, unit: str, days: str, below: str):
        early_txt, later_txt = re.split(sep, stem)[1:3]
        pat = r"\$(\d+)\$ ?" + unit + r"\s*(?:有|on) \$(\d+)\$ ?" + days
        early = [(F(a), F(b)) for a, b in re.findall(pat, early_txt)]
        later = [(F(a), F(b)) for a, b in re.findall(pat, later_txt)]
        thr = F(re.search(r"\$(\d+)\$ ?" + unit + r"\s*" + below, stem).group(1))
        return early, later, thr

    ez, lz, tz = tables(zh, r"前期：|後期：", "℃", "天", "以下")
    ee, le, te = tables(en, r"Earlier: |Later: ", "°C", "days", "or below")
    assert (ez, lz, tz) == (ee, le, te) and len(ez) == len(lz) == 5
    assert "冬" in zh and "winter" in en and "最低" in zh and "minimum" in en
    assert sum(d for _, d in ez) == 100 and sum(d for _, d in lz) == 100
    mean = lambda tb: sum(t * d for t, d in tb) / sum(d for _, d in tb)  # noqa: E731
    assert mean(lz) - mean(ez) == 1  # the chapter's point: the average rises by only 1 °C
    cold = lambda tb: sum(d for t, d in tb if t <= tz)  # noqa: E731  ("以下" includes the threshold)
    ratio = F(cold(ez), cold(lz))
    assert ratio.denominator == 1 and 0 < ratio < 10
    return (str(int(ratio)),)


# --- mitigation and adaptation --------------------------------------------------------------------

# 國中 Nb-Ⅳ-3 / nat:ENb-Vc-4 (adaptation, brief): mitigation reduces greenhouse gas emissions or increases
# their uptake (acts on the cause); adaptation reduces the impacts and losses (acts on the effects).
# Each measure is encoded by what it changes.
MEASURES = [
    ("water storage and recycling for longer droughts", "reduces_impact"),
    ("solar power replaces coal power", "cuts_emissions"),
    ("rice planted to avoid the hottest time", "reduces_impact"),
    ("planting forests to take up CO2", "increases_uptake"),
    ("public transport instead of cars and scooters", "cuts_emissions"),
]


def cc_adaptation_measures(item: dict) -> list[bool]:
    """q8 (multi): which measures are adaptation rather than mitigation."""
    assert len(item["text"]["en"]["options"]) == len(MEASURES)
    mitigation = {"cuts_emissions", "increases_uptake"}
    return [effect == "reduces_impact" and effect not in mitigation for _, effect in MEASURES]
