"""Checks for src/data/items/earth/s116-ocean-currents-el-nino.yaml (116 sprint: EFa-Ⅴc-4/5 surface salinity
and ocean temperature, EIc-Ⅴc-1 surface currents and prevailing winds, EIb-Ⅴc-7 ocean–atmosphere interaction
and El Niño).

How the keys are recomputed (never from item["answer"]):
- Salinity is salt mass / seawater mass x 1000 with exact Fractions. The salt stays; evaporation removes
  water, rain and rivers add fresh water (nat:EFa-Vc-4 keyConcepts: surface salinity is controlled by
  precipitation, evaporation and river input).
- Temperature profiles: the cooling per 100 m of each stated depth range, exact.
- Gyres: the prevailing wind pushes the surface water along the low- and mid-latitude edges of a basin
  closed by continents (nat:EIc-Vc-1: surface currents are linked to the prevailing winds). The sense of
  the loop is the sign of the circulation of the edge flows around the basin; warm or cold follows from
  where the water comes from and a surface temperature that falls with latitude.
- El Niño: a small two-sided model of the equatorial Pacific driven by one trade-wind strength w, whose
  monotone dependences are standard 必修 content (listed in the chapter report); nat:EIb-Vc-7 asks for the
  explanation from eastern and western observations, and for its dynamic and thermal sides.
"""

from __future__ import annotations

import re
from fractions import Fraction as F


def stem_numbers(item: dict, zh_pat: str, en_pat: str) -> tuple[F, ...]:
    """Numbers a stem states, parsed from both locales; they must agree."""
    mz = re.search(zh_pat, item["text"]["zh-tw"]["stem"])
    me = re.search(en_pat, item["text"]["en"]["stem"])
    assert mz and me, (zh_pat, en_pat)
    vz, ve = tuple(F(g) for g in mz.groups()), tuple(F(g) for g in me.groups())
    assert vz == ve, (vz, ve)
    return vz

# --- salinity ------------------------------------------------------------------------------------


def salinity(salt_g: F, sea_g: F) -> F:
    """‰: grams of salts in 1000 g of seawater."""
    return F(salt_g) / F(sea_g) * 1000


def after_budget(salt_g: F, sea_g: F, evaporation: F, rain: F, river: F) -> F:
    """Salinity after the water budget: evaporation removes water only; rain and river water are fresh
    (nat:EFa-Vc-4 keyConcepts)."""
    return salinity(salt_g, F(sea_g) - evaporation + rain + river)


def cd_turn_salinity_order(item: dict) -> list[bool]:
    """q-turn: A (about 25° latitude, sunny and dry, strong evaporation), B (equator, heavy rain almost
    daily), C (off a large river mouth). The stem's words are encoded as illustrative yearly budgets for a
    surface layer of 1000 g that held 34 g of salts (only the signs and the river's size matter):
    A: evaporation far above rain; B: rain above evaporation; C: river input dominates."""
    budgets = {
        "A": dict(evaporation=F(150), rain=F(30), river=F(0)),
        "B": dict(evaporation=F(120), rain=F(200), river=F(0)),
        "C": dict(evaporation=F(100), rain=F(100), river=F(400)),
    }
    s = {k: after_budget(F(34), F(1000), **b) for k, b in budgets.items()}
    rankings = [("A", "B", "C"), ("B", "A", "C"), ("C", "A", "B"), ("A", "C", "B")]
    ranked = [all(s[r[i]] > s[r[i + 1]] for i in range(2)) for r in rankings]
    same = max(s.values()) - min(s.values()) < 1  # within 1 ‰
    return ranked + [same]


def cd_rain_dilution(item: dict) -> int:
    """q1: the stem's sample (seawater mass, salts) and the fresh water the rain adds."""
    sea, salt = stem_numbers(item, r"取出 \$(\d+)\$ 克海水，其中含鹽類 \$(\d+)\$ 克", r"You take \$(\d+)\$ g of seawater.*?contains \$(\d+)\$ g of salts")
    (rain,) = stem_numbers(item, r"加入了 \$(\d+)\$ 克的淡水", r"as if \$(\d+)\$ g of fresh water")
    s = after_budget(salt, sea, evaporation=F(0), rain=rain, river=F(0))
    assert 10 <= s < 100
    assert s.denominator == 1
    return int(s)


def cd_raises_salinity(item: dict) -> list[bool]:
    """q2 (multi): each option as a change to the water budget of a surface layer, everything else fixed.
    Options: strong evaporation; river inflow; days of heavy rain; evaporation > rain over a year;
    rain > evaporation over a year."""
    base = salinity(F(35), F(1000))
    options = [
        dict(evaporation=F(50), rain=F(0), river=F(0)),
        dict(evaporation=F(0), rain=F(0), river=F(50)),
        dict(evaporation=F(0), rain=F(50), river=F(0)),
        dict(evaporation=F(120), rain=F(80), river=F(0)),
        dict(evaporation=F(80), rain=F(120), river=F(0)),
    ]
    return [after_budget(F(35), F(1000), **o) > base for o in options]


# --- temperature ---------------------------------------------------------------------------------


def cd_fastest_drop(item: dict) -> list[bool]:
    """q3: the stem's (illustrative) profile; cooling per 100 m in each option's range."""
    zh, en = item["text"]["zh-tw"], item["text"]["en"]
    profile = {int(d): F(t) for d, t in re.findall(r"\$(\d+)\$ 公尺 \$([\d.]+)\$℃", zh["stem"])}
    assert profile and profile == {int(d): F(t) for d, t in re.findall(r"\$(\d+)\$ m \$([\d.]+)\$ ℃", en["stem"])}
    ranges = [tuple(int(x) for x in re.fullmatch(r"\$(\d+)\$～\$(\d+)\$ 公尺", o).groups()) for o in zh["options"]]
    assert ranges == [tuple(int(x) for x in re.fullmatch(r"\$(\d+)\$–\$(\d+)\$ m", o).groups()) for o in en["options"]]
    rate = [(profile[a] - profile[b]) / F(b - a, 100) for a, b in ranges]
    best = max(rate)
    assert rate.count(best) == 1
    return [r == best for r in rate]


# Surface sea temperature falls from low to high latitudes because low latitudes receive more solar
# radiation per unit area (nat:EFa-Vc-5 keyConcepts: basic causes of horizontal temperature change; the
# monotone fall itself is standard 必修 content). Illustrative monotone profile, ℃ by latitude.
def surface_temp(lat_deg: int) -> F:
    return F(28) - F(lat_deg, 3)


def current_type(from_lat: int, to_lat: int) -> tuple[str, str]:
    """A surface current keeps (some of) the temperature of where it came from: compared with local water
    at its destination it is colder (a cold current) or warmer (a warm current). Standard 必修 content."""
    src, local = surface_temp(abs(from_lat)), surface_temp(abs(to_lat))
    if src < local:
        return "colder", "cold"
    if src > local:
        return "warmer", "warm"
    return "same", "none"


def cd_current_from_north(item: dict) -> list[bool]:
    """q4: a current from about 40°N to about 20°N. Options: (colder, cold); (warmer, warm); (colder, warm);
    (warmer, cold); (same, cannot tell)."""
    t = current_type(40, 20)
    return [t == ("colder", "cold"), t == ("warmer", "warm"), t == ("colder", "warm"),
            t == ("warmer", "cold"), t == ("same", "none")]


# --- gyres ---------------------------------------------------------------------------------------
# Prevailing winds over the oceans (standard 必修/國中 content, listed in the report): trade winds at
# about 0–30° blow from east to west in both hemispheres (NE trades in the north, SE trades in the
# south); the westerlies at about 30–60° blow from west to east. Positive u = eastward.
WIND_U = {"trades": -1, "westerlies": +1}


def gyre(hemisphere: str) -> dict:
    """Square basin with north at the top, closed by continents on the west and east. The wind drives the
    flow along the low- and mid-latitude edges; the continents turn it along the west and east edges.
    Returns the loop sense and the flow direction on the west and east edges."""
    # which edge is at low latitude: in the north the equator is at the bottom, in the south at the top
    if hemisphere == "N":
        bottom, top = WIND_U["trades"], WIND_U["westerlies"]
    else:
        bottom, top = WIND_U["westerlies"], WIND_U["trades"]
    # circulation counter-clockwise around the unit square: bottom edge traversed east (+u), top edge
    # traversed west (-u); the side edges carry the turned flow and add with the same sign, so only the
    # sign of bottom - top matters
    circulation = bottom - top
    assert circulation != 0, "no loop"
    sense = "anticlockwise" if circulation > 0 else "clockwise"
    # flow on the west edge: clockwise goes north there, anticlockwise goes south
    west = "north" if sense == "clockwise" else "south"
    east = "south" if west == "north" else "north"
    return {"sense": sense, "west": west, "east": east, "edges_u": (bottom, top)}


def toward_pole(hemisphere: str, direction: str) -> bool:
    return (hemisphere, direction) in {("N", "north"), ("S", "south")}


def cd_gyre_northern(item: dict) -> list[bool]:
    """q-gyre: Northern Hemisphere basin. Options: clockwise loop; anticlockwise loop; all west, no loop;
    all east, no loop."""
    g = gyre("N")
    # "no loop" would need both wind-driven edges to push the same way (the side edges then carry nothing
    # back); the winds push the two edges opposite ways, so neither "all west" nor "all east" holds
    all_west = all(u < 0 for u in g["edges_u"])
    all_east = all(u > 0 for u in g["edges_u"])
    return [g["sense"] == "clockwise", g["sense"] == "anticlockwise", all_west, all_east]


def cd_gyre_southern(item: dict) -> list[bool]:
    """q5: Southern Hemisphere basin. Options: (anticlockwise, warm west); (clockwise, warm west);
    (anticlockwise, warm east); (clockwise, warm east). Warm = flowing from low to high latitude."""
    g = gyre("S")
    warm_side = "west" if toward_pole("S", g["west"]) else "east"
    assert toward_pole("S", g[warm_side])
    combos = [("anticlockwise", "west"), ("clockwise", "west"), ("anticlockwise", "east"), ("clockwise", "east")]
    return [(g["sense"], warm_side) == c for c in combos]


# --- equatorial Pacific --------------------------------------------------------------------------
# Standard 必修 content (listed in the chapter report), as monotone dependences on the trade-wind strength
# w (1 = normal), matching the chapter's cross-section figure:
# - the trade winds push warm surface water west: the warm layer thickens in the west and thins in the
#   east as w grows; the east's surface water is replaced from below (upwelling) more strongly as w grows;
# - upwelled water is cold and rich in nutrients, so stronger upwelling means a colder east and better
#   fishing;
# - the air rises and it rains most over the warmest water, which spreads east as w falls.
NORMAL_W = F(1)


def pacific(w: F) -> dict:
    east_warm_depth = 2 - F(13, 10) * w  # thickness of the warm layer in the east (figure units)
    upwelling = w
    east_sst = F(22) + F(3) * east_warm_depth  # illustrative: a thicker warm layer -> warmer surface
    rain_x = F(12, 10) + F(45, 10) * (F(12, 10) - w)  # longitude-like position of the rainy region (east +)
    return {"east_sst": east_sst, "upwelling": upwelling, "rain_x": rain_x, "fish": upwelling}


def compare(w: F) -> dict:
    """Signs of each change from normal for trade-wind strength w."""
    p, n = pacific(w), pacific(NORMAL_W)

    def sgn(a, b):
        return (a > b) - (a < b)

    return {k: sgn(p[k], n[k]) for k in p} | {"trades": sgn(w, NORMAL_W)}


EL_NINO_W = F(2, 10)  # weaker trades (the figure's lower end)
LA_NINA_W = F(14, 10)  # stronger trades


def cd_turn_weak_trades(item: dict) -> list[bool]:
    """q-east: trades much weaker. Options: (east warmer, rain east); (warmer, west); (colder, east);
    (colder, west)."""
    c = compare(EL_NINO_W)
    combos = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    return [(c["east_sst"], c["rain_x"]) == combo for combo in combos]


def cd_el_nino_statements(item: dict) -> list[bool]:
    """q6 (multi), El Niño compared with normal: (1) weaker trades; (2) stronger eastern upwelling;
    (3) warmer eastern surface; (4) more rain in Indonesia and Australia (the west); (5) fewer fish off
    South America."""
    c = compare(EL_NINO_W)
    west_wetter = c["rain_x"] < 0  # the rainy region moving west would bring the west more rain
    return [c["trades"] < 0, c["upwelling"] > 0, c["east_sst"] > 0, west_wetter, c["fish"] < 0]


def cd_rain_fish_year(item: dict) -> list[bool]:
    """q7 (illustrative data): west rain x 1/2, east rain x 3, fish sharply down. Match the observed signs
    (rain region moved east, fish down) against the model's signature for each state."""
    west_ratio, east_ratio = F(1, 2), F(3)
    observed = {"rain_x": 1 if (west_ratio < 1 and east_ratio > 1) else -1, "fish": -1}
    states = {"el_nino": EL_NINO_W, "la_nina": LA_NINA_W, "normal": NORMAL_W}
    match = {s: all(compare(w)[k] == v for k, v in observed.items()) for s, w in states.items()}
    assert sum(match.values()) == 1
    trades = {s: compare(w)["trades"] for s, w in states.items()}
    options = [("el_nino", -1), ("el_nino", 1), ("la_nina", 1), ("la_nina", -1), ("normal", 0)]
    return [match[s] and trades[s] == t for s, t in options]


# Dynamic vs thermal (nat:EIb-Vc-7 keyConcepts: the interaction has dynamic and thermal aspects). Each
# option is tagged by what passes between ocean and air: a force on the water (dynamic) or heat and water
# vapour (thermal).
def cd_thermal_processes(item: dict) -> list[bool]:
    """q8 (multi): which are thermal? (1) wind piles surface water on a downwind coast; (2) cold air over a
    warmer sea gains heat and vapour; (3) trade winds drive equatorial water west; (4) warm sea heats the
    air, which rises (low pressure); (5) a cold sea cools the air, which sinks."""
    passes = ["force", "heat+vapour", "force", "heat", "heat"]
    kind = {"force": "dynamic", "heat": "thermal", "heat+vapour": "thermal"}
    return [kind[p] == "thermal" for p in passes]
