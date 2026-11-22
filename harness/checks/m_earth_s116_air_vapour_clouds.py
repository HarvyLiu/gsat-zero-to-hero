"""Checks for src/data/items/earth/s116-air-vapour-clouds.yaml (116 sprint: EFa-Ⅴc-3 vertical change of
atmospheric temperature and pressure; EIb-Ⅴc-1~3 water vapour, saturation, dew point, relative and
absolute humidity; EIb-Ⅴc-4 rising air expands, cools and forms cloud or fog).

How the keys are recomputed (never from item["answer"]):
- Pressure is the weight of the air above (hydrostatic picture): an atmosphere of stacked layers with
  stated masses; the pressure at a level is the mass above it, so the fraction of the atmosphere's mass
  below a level is 1 - p/p_ground, with exact Fractions.
- Saturation vapour pressure comes from the (illustrative) table stated in each stem, parsed from the
  stem text and checked in both locales; dew points are found by inverse piecewise-linear interpolation
  of that table, relative humidity as e / e_s(T) with exact Fractions.
- Rising air: temperature and dew point fall at the rates stated in the stem (the chapter never teaches
  a lapse rate; the rates are given data); cloud base is where the two meet, solved exactly.
- Qualitative facts are small tables, each with a source comment.
"""

from __future__ import annotations

import re
from fractions import Fraction as F

# --- the chapter's illustrative saturation vapour pressure table (hPa) ------------------------------
# Illustrative data rounded to whole numbers (the chapter labels them 示意數據). Only the qualitative
# fact "e_s rises with temperature" is curricular (nat:EIb-Vc-1 keyConcepts: saturation vapour pressure
# curve).
CHAPTER_ES = {0: 6, 5: 9, 10: 12, 15: 17, 20: 23, 25: 32, 30: 42, 35: 56}


def stem_table(item: dict) -> dict[int, int]:
    """Parse 'T ℃: e hPa' pairs from the en stem and the same pairs ('T℃為e hPa') from the zh stem."""
    en = item["text"]["en"]["stem"]
    zh = item["text"]["zh-tw"]["stem"]
    pe = {int(t): int(e) for t, e in re.findall(r"(\d+) ℃: (\d+) hPa", en)}
    pz = {int(t): int(e) for t, e in re.findall(r"(\d+)℃為(\d+) hPa", zh)}
    assert pe and pe == pz, (pe, pz)
    temps = sorted(pe)
    assert all(pe[a] < pe[b] for a, b in zip(temps, temps[1:])), "e_s must rise with temperature"
    return pe


def es_at(table: dict[int, int], t) -> F:
    """Saturation vapour pressure at temperature t by linear interpolation in the table."""
    t = F(t)
    temps = sorted(table)
    for a, b in zip(temps, temps[1:]):
        if a <= t <= b:
            return F(table[a]) + (F(table[b]) - table[a]) * (t - a) / (b - a)
    raise ValueError(f"{t} outside the table")


def dew_point(table: dict[int, int], e) -> F:
    """Temperature at which the table's e_s equals e (inverse interpolation): the dew point."""
    e = F(e)
    temps = sorted(table)
    for a, b in zip(temps, temps[1:]):
        if table[a] <= e <= table[b]:
            return a + (e - table[a]) * (b - a) / (F(table[b]) - table[a])
    raise ValueError(f"{e} hPa outside the table")


def round_half_up(x: F) -> int:
    return int((x + F(1, 2)) // 1)


def stem_numbers(item: dict, zh_pat: str, en_pat: str) -> tuple[F, ...]:
    """The numbers a stem states, parsed from both locales; they must agree."""
    mz = re.search(zh_pat, item["text"]["zh-tw"]["stem"])
    me = re.search(en_pat, item["text"]["en"]["stem"])
    assert mz and me, (zh_pat, en_pat)
    vz, ve = tuple(F(g) for g in mz.groups()), tuple(F(g) for g in me.groups())
    assert vz == ve, (vz, ve)
    return vz


# --- pressure as the weight of the air above ------------------------------------------------------
# Source: nat:EFa-Vc-3 keyConcepts ("only the basic causes of the vertical temperature and pressure
# profiles"); the basic cause of pressure falling with height is that less air lies above (國中 Ec-Ⅳ-1
# 大氣壓力). A toy atmosphere of 10 layers, denser (heavier) near the ground: pressure at the top of layer
# k is the mass of all layers above it.
LAYER_MASSES = [F(m) for m in (200, 160, 130, 110, 90, 70, 40, 90, 60, 50)]  # sum 1000 (hPa units)
assert sum(LAYER_MASSES) == 1000


def pressure_at_level(k: int) -> F:
    """Pressure at the top of layer k (k = 0 is the ground): the weight of the layers above."""
    return sum(LAYER_MASSES[k:], F(0))


def cd_turn_crisp_bag(item: dict) -> list[bool]:
    """q-turn: a bag sealed on the plains puffs up on a mountain. Options: (1) lower pressure outside;
    (2) mountain air is warmer; (3) the crisps give off gas; (4) weaker gravity makes the bag lighter;
    (5) stronger sunshine heats the bag up."""
    p_plain = pressure_at_level(0)
    p_mountain = pressure_at_level(3)  # a few kilometres up
    inside = p_plain  # sealed at plains pressure; the bag's air keeps that pressure until it expands
    outward_push = inside > p_mountain
    # Source: troposphere temperature falls with height (EFa-Ⅴc-3, heated from the ground; chapter
    # section 2), so "warmer on the mountain" is false as a premise.
    mountain_warmer = False
    # Crisps do not produce gas; gravity changes by a negligible amount over a few km; the bag puffs up
    # in shade or at night too, so sunshine is not the main cause (standard facts, listed in the report).
    return [outward_push, mountain_warmer, False, False, False]


# --- what heats each layer ------------------------------------------------------------------------
# Source: nat:EFa-Vc-3 (basic causes of the temperature profile; 國中 Fa-Ⅳ-4 layers by temperature).
# Standard 必修地科 content, listed in the report: the troposphere is heated from the ground, which
# absorbs sunlight; the stratosphere is warmed by ozone absorbing solar ultraviolet; the thermosphere by
# thin gas absorbing high-energy solar radiation.
HEAT_SOURCE = {
    "troposphere": "ground heated by sunlight",
    "stratosphere": "ozone absorbs UV",
    "thermosphere": "thin gas absorbs high-energy radiation",
}


def cd_stratosphere_heat(item: dict) -> list[bool]:
    """q1: the main reason the stratosphere warms with height."""
    options = ["ozone absorbs UV", "closer to the Sun", "ground heated by sunlight", "condensation releases heat",
               "sinking air compressed"]
    return [o == HEAT_SOURCE["stratosphere"] for o in options]


# --- humidity -------------------------------------------------------------------------------------
# Source: nat:EIb-Vc-1~3 keyConcepts: saturation vapour pressure curve; at saturation the excess vapour
# condenses or deposits; dew point; relative vs absolute humidity; wet/dry-bulb thermometer activity.


def cd_noon_rh(item: dict) -> list[bool]:
    """q-noon: dawn 15 ℃ at 90 %, noon 25 ℃ with the same vapour. Options: higher; about the same; lower;
    reaches 100 % and condenses; cannot tell. Uses the chapter's illustrative table."""
    e = F(9, 10) * CHAPTER_ES[15]
    rh_dawn = e / CHAPTER_ES[15]
    rh_noon = e / CHAPTER_ES[25]
    return [rh_noon > rh_dawn, rh_noon == rh_dawn, rh_noon < rh_dawn, rh_noon >= 1, False]


def cd_cooling_to_dew(item: dict) -> tuple[str, str]:
    """q2: evening air at the stem's temperature and vapour pressure; how far must it cool (vapour
    unchanged) to saturate? Dew point from the stem's table; the answer is T - Td."""
    table = stem_table(item)
    t, e = stem_numbers(item, r"測得氣溫(\d+)℃、水氣壓(\d+) hPa", r"air temperature of (\d+) ℃ and a vapour pressure of (\d+) hPa")
    td = dew_point(table, e)
    drop = t - td
    assert drop > 0 and drop.denominator == 1 and 10 <= drop < 100
    return tuple(str(int(drop)))


def cd_rh_station(item: dict) -> int:
    """q3: 20 ℃, dew point 10 ℃. e = e_s(10); RH = e / e_s(20) in %, rounded half up."""
    table = stem_table(item)
    rh = es_at(table, 10) / es_at(table, 20) * 100
    return round_half_up(rh)


def cd_evening_cooling(item: dict) -> list[bool]:
    """q4 (multi): vapour unchanged, temperature falling through the evening but still above the dew
    point. (1) RH rises; (2) dew point falls; (3) e_s falls; (4) actual vapour pressure rises; (5) if the
    temperature falls to the dew point, the air is saturated."""
    e = F(14)  # any fixed vapour pressure inside the table
    temps = [F(30), F(27), F(24), F(21)]  # falling, all above the dew point
    td = dew_point(CHAPTER_ES, e)
    assert all(t > td for t in temps)
    es = [es_at(CHAPTER_ES, t) for t in temps]
    rh = [e / s for s in es]
    tds = [dew_point(CHAPTER_ES, e) for _ in temps]  # the dew point depends on e only
    s1 = all(a < b for a, b in zip(rh, rh[1:]))
    s2 = all(a > b for a, b in zip(tds, tds[1:]))
    s3 = all(a > b for a, b in zip(es, es[1:]))
    s4 = False  # e is held fixed by the stem
    s5 = es_at(CHAPTER_ES, td) == e  # at T = dew point, e = e_s: saturated
    return [s1, s2, s3, s4, s5]


def wet_bulb_depression_sign(es_air: F, e: F) -> int:
    """Qualitative wet-bulb model: the gauze's water evaporates (carrying heat away) only while the air
    is unsaturated; the larger e_s - e, the faster the evaporation and the larger the depression. Returns
    the sign of the dry-minus-wet reading."""
    gap = es_air - e
    assert gap >= 0
    return 1 if gap > 0 else 0


def cd_wet_dry_bulb(item: dict) -> list[bool]:
    """q5 (multi): (1) in unsaturated air the wet bulb reads lower; (2) at the same temperature a bigger
    difference means higher RH; (3) equal readings mean RH 100 %; (4) the wet bulb is lower because
    evaporation carries heat away; (5) humidifying a closed room makes the difference grow."""
    es_air = F(CHAPTER_ES[25])
    s1 = wet_bulb_depression_sign(es_air, es_air * F(1, 2)) == 1
    # the depression grows with e_s - e (model above); compare two airs at the same temperature
    gap = lambda rh: es_air - es_air * rh  # noqa: E731
    drier, moister = F(4, 10), F(8, 10)
    bigger_gap_is_moister = gap(moister) > gap(drier)
    s2 = bigger_gap_is_moister
    s3 = wet_bulb_depression_sign(es_air, es_air) == 0  # equal readings <=> e = e_s <=> RH = 100 %
    s4 = True  # chapter / 說明 wet-dry bulb activity: evaporation from the gauze takes heat away
    s5 = gap(F(9, 10)) > gap(F(6, 10))  # more vapour -> smaller gap -> smaller difference
    return [s1, s2, s3, s4, s5]


# --- rising air and cloud base --------------------------------------------------------------------
# Source: nat:EIb-Vc-4 keyConcepts (rising air treated as adiabatic: it cools, may saturate and form
# cloud or fog; no lapse rates taught) and the 113 Q34 note (cloud-base height from temperature and dew
# point). The cooling rates are given in the stem.


def cloud_base_m(t0: F, td0: F, t_rate: F, td_rate: F) -> F:
    """Height (m) where temperature meets dew point; rates in ℃ per 100 m."""
    assert t_rate > td_rate >= 0 and t0 >= td0
    return (t0 - td0) / (t_rate - td_rate) * 100


def cd_pilot_dew_point(item: dict) -> tuple[str, str]:
    """q6: the stem's cloud base, ground temperature and cooling rates per 100 m: solve for the ground
    dew point."""
    h, t0 = stem_numbers(item, r"雲底約在(\d+)公尺高，當時地面氣溫(\d+)℃", r"base is about (\d+) m up, while the air temperature at the ground is (\d+) ℃")
    rt, rd = stem_numbers(item, r"每上升100公尺，氣溫降低([\d.]+)℃、露點降低([\d.]+)℃", r"its temperature fell by ([\d.]+) ℃ and its dew point by ([\d.]+) ℃")
    # (t0 - td0) / (rt - rd) * 100 = h  ->  td0 = t0 - h/100 * (rt - rd)
    td0 = t0 - h / 100 * (rt - rd)
    assert cloud_base_m(t0, td0, rt, rd) == h
    # cross-check by stepping up 50 m at a time: temperature and dew point meet at the cloud base
    t, d, z = t0, td0, F(0)
    while t > d:
        t, d, z = t - rt / 2, d - rd / 2, z + 50
    assert z == h and t == d
    assert td0.denominator == 1 and 10 <= td0 < 100
    return tuple(str(int(td0)))


# Facts about cloud and fog formation. Source: nat:EIb-Vc-4 keyConcepts (adiabatic cooling of rising
# air, saturation, cloud or fog) and research.common_misconceptions in the chapter's research slice
# ("rising air cools because it meets colder air" is wrong; it cools because it expands). Cloud drops vs
# invisible vapour and night-time ground cooling are standard facts, listed in the report.
CLOUD_FACTS = {
    "rising air cools by expanding": True,
    "rising air cools mainly by meeting colder air": False,
    "cooling to the dew point saturates the air and vapour condenses": True,
    "a cloud is made of invisible water vapour": False,
    "near-ground air cooled to its dew point on a clear calm night can form fog": True,
}


def cd_cloud_statements(item: dict) -> list[bool]:
    """q7 (multi): five statements in the order of CLOUD_FACTS."""
    return list(CLOUD_FACTS.values())


def cd_balloon_mass(item: dict) -> list[bool]:
    """q8: the stem's ground pressure and balloon pressure. Fraction of the atmosphere's mass below the
    balloon. Options: four percentages (parsed from the options), then 'cannot be estimated'."""
    (p0,) = stem_numbers(item, r"地面氣壓是(\d+) hPa", r"ground pressure at a place is (\d+) hPa")
    (p,) = stem_numbers(item, r"升到氣壓(\d+) hPa的高度", r"where the pressure is (\d+) hPa")
    # pressure = weight of the air above, so mass above / total = p / p0; checked on the toy atmosphere
    # at every level: mass below level k / total == 1 - p_k / p_ground
    for k in range(len(LAYER_MASSES)):
        assert sum(LAYER_MASSES[:k], F(0)) / pressure_at_level(0) == 1 - pressure_at_level(k) / pressure_at_level(0)
    below = 1 - p / p0
    zh, en = item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]
    pct = [F(int(re.fullmatch(r"(\d+)%", o).group(1)), 100) for o in zh[:4]]
    assert pct == [F(int(re.fullmatch(r"(\d+)%", o).group(1)), 100) for o in en[:4]]
    return [below == x for x in pct] + [False]
