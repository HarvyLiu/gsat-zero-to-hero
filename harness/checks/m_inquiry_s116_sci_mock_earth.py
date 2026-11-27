"""Checks for the Earth science items of inquiry/s116-sci-mock (the original science practice paper):
Part 1 q28–q36 and the Part 2 Earth science set q54–q56.

Every key is recomputed from the stem (numbers and settings are parsed from the zh-tw stem and, where
they carry numbers, cross-checked against the en stem); nothing reads item["answer"]. Exact Rationals
throughout.

Subject content comes only from the reviewed Earth science sprint chapters (src/content/lessons/zh-tw/
earth/*.mdx), named per check:
- q28  earth/s116-universe-stars (視星等: 5 magnitudes = 100× brightness; 絕對星等 = apparent magnitude
       at 10 pc; brightness ∝ L / d²; "每多5等，距離就乘以10").
- q29  earth/s116-sky-motion (天球 turns ~15° an hour, the same angle for every star; Polaris altitude =
       latitude, on the horizon at the equator and below it farther south; in the southern hemisphere the
       south celestial pole's altitude = the southern latitude and, facing south, stars turn clockwise;
       rising in the east and setting in the west comes from Earth spinning west to east).
- q30  earth/s116-earth-history (half-life halving table: parent left (1/2)^n, daughter:parent 2^n − 1;
       superposition; cross-cutting; bracketing a sedimentary layer with dated igneous bodies).
- q31  earth/s116-earth-layers-plates (age = distance ÷ rate; rock youngest at the ridge; farther from
       the ridge = older sea floor = thicker sediment).
- q32  earth/s116-plate-boundaries-taiwan (boundary evidence table: magma, metamorphism, structures,
       focal depths; deep foci in a sloping band only where a plate is pushed down; continental
       collision: neither plate sinks, they squeeze and rise into high mountains; shallow quakes alone do
       not rule out a convergent boundary).
- q33  earth/s116-air-vapour-clouds (relative humidity = vapour pressure ÷ saturation vapour pressure at
       the same temperature; dew point depends only on the vapour pressure; saturated air that cools
       condenses).
- q34  earth/s116-wind-weather-maps (wind named by where it comes from; near the surface the wind crosses
       the isobars towards the low: "背風而立，低壓在左前方", right in the southern hemisphere; less
       friction over the sea = closer to along the isobars).
- q35  earth/s116-ocean-currents-el-nino (trade winds blow surface water west, eastern upwelling; weaker
       trades = El Niño: east warms, rain area east, west dry; stronger trades = 反聖嬰 / La Niña: east
       colder, rain area farther west).
- q36  earth/s116-climate-change (floating sea ice melting hardly changes sea level; land ice and the
       expansion of warming seawater raise it; mitigation vs adaptation; adaptation cannot stop warming).
- q54–q56  earth/s116-typhoons (northern-hemisphere typhoon: near-surface wind anticlockwise and blowing
       in towards the centre; windward slopes: air forced up, cools to the dew point, heavy rain; far side
       much drier).

Bearings are compass degrees (0 = N, 90 = E). "Blowing in at a slant" is modelled by every inflow angle
0 < α < 90 (the chapter gives no number), so a direction holds only if it holds for all such α.
"""

from __future__ import annotations

import re

import sympy as sp
from sympy import Rational as Q

# --- helpers ------------------------------------------------------------------------------------------


def zh(item: dict) -> str:
    return item["text"]["zh-tw"]["stem"]


def en(item: dict) -> str:
    return item["text"]["en"]["stem"]


def nums(s: str) -> list[Q]:
    return [Q(x) for x in re.findall(r"\$(-?\d+(?:\.\d+)?)\$", s)]


def norm(x, centre) -> Q:
    """x relative to centre, in (−180, 180]."""
    d = (Q(x) - Q(centre)) % 360
    return d - 360 if d > 180 else d


def arc_within(lo, hi, centre, half) -> bool:
    """The open arc from lo to hi (hi − lo in (0, 360), measured clockwise in bearings) lies inside the
    closed arc centre ± half."""
    a = norm(lo, centre)
    width = (Q(hi) - Q(lo)) % 360
    assert 0 < width < 360
    return a >= -half and a + width <= half


# Northern hemisphere surface wind around a low (earth/s116-typhoons, s116-wind-weather-maps): turning
# anticlockwise seen from above = decreasing bearing, plus an inward part. With the centre at bearing c
# from the station, the station sits at c + 180 from the centre; the anticlockwise tangent there points to
# c + 180 − 90 = c + 90, and inward points to c. Rotating from the tangent towards inward by α:
# toward = c + 90 − α, so from = toward + 180 = c + 270 − α = c − 90 − α (mod 360).
def nh_from_arc_around_low(c) -> tuple[Q, Q]:
    """Open arc of 'from' bearings for 0 < α < 90, as (lo, hi) going clockwise."""
    c = Q(c)
    return ((c - 180) % 360, (c - 90) % 360)


ARCS = {"北東": (0, 90), "東南": (90, 180), "南西": (180, 270), "西北": (270, 360)}


def arc_of(lo, hi, name: str) -> bool:
    a0, a1 = ARCS[name]
    return arc_within(lo, hi, Q(a0 + a1, 2), 45)


def windward_slope_ew_ridge(lo, hi) -> str | None:
    """For an east–west ridge: wind coming from the north half makes the northern slope windward, from
    the south half the southern slope (earth/s116-typhoons: 風吹向山時，空氣被迫沿著山坡上升)."""
    if arc_within(lo, hi, 0, 90):
        return "north"
    if arc_within(lo, hi, 180, 90):
        return "south"
    return None


# --- q28 universe-stars ---------------------------------------------------------------------------------

STANDARD_DISTANCE_PC = Q(10)  # 絕對星等: apparent magnitude at 10 parsecs (s116-universe-stars)


def distance_pc(m, M):
    """Every 5 magnitudes of (m − M) is 100× in brightness, i.e. 10× in distance (brightness ∝ 1/d²)."""
    return STANDARD_DISTANCE_PC * sp.Integer(10) ** (sp.Rational(m - M, 5))


def lum_ratio(M_b, M_a):
    """Luminosity of b over a from absolute magnitudes: 5 magnitudes = 100×, smaller = more luminous."""
    return sp.Integer(100) ** (sp.Rational(M_a - M_b, 5))


def me_equal_brightness_stars(item: dict) -> list[bool]:
    s = zh(item)
    m = Q(re.search(r"視星等都是 \$(-?\d+)\$", s).group(1))
    Ma = Q(re.search(r"甲的絕對星等是 \$(-?\d+)\$", s).group(1))
    Mb = Q(re.search(r"乙的絕對星等是 \$(-?\d+)\$", s).group(1))
    assert nums(en(item)) == [m, Ma, Mb]
    dist = sp.nsimplify(distance_pc(m, Mb) / distance_pc(m, Ma))
    lum = sp.nsimplify(lum_ratio(Mb, Ma))
    # second route: equal brightness, so L ∝ d² (brightness ∝ L / d²)
    assert lum == dist**2
    return [
        dist == 100 and lum == 100,
        dist == 5 and lum == 5,
        dist == 10 and lum == 100,
        dist == 1 and lum == 1,
        1 / dist == 10 and 1 / lum == 100,
    ]


# --- q29 sky-motion -------------------------------------------------------------------------------------

DEG_PER_HOUR = Q(360, 24)  # the celestial sphere turns once in about 24 h, the same angle for every star
TURN_SENSE_FACING_POLE = {"N": "anticlockwise", "S": "clockwise"}  # StudentAsks 南半球
RISE_EAST_SET_WEST_EVERYWHERE = True  # Earth spins west to east at every latitude


def polaris_visible(lat) -> bool:
    """Polaris (taken at the north celestial pole) has altitude = latitude; at 0 it is on the horizon,
    south of the equator it is below the horizon."""
    return lat > 0


def own_pole_altitude(lat):
    return abs(lat)


def me_southern_sky(item: dict) -> list[bool]:
    s = zh(item)
    lat_deg = Q(re.search(r"南緯 \$(\d+)°\$", s).group(1))
    lat = -lat_deg
    hours = Q(re.search(r"連續曝光 \$(\d+)\$ 小時", item["text"]["zh-tw"]["options"][3]).group(1))
    near, far = hours * DEG_PER_HOUR, hours * DEG_PER_HOUR  # same angle near and far from the pole
    return [
        TURN_SENSE_FACING_POLE["S"] == "anticlockwise",
        not polaris_visible(lat),
        own_pole_altitude(lat) == 30,
        far > near,
        RISE_EAST_SET_WEST_EVERYWHERE,
    ]


# --- q30 earth-history ----------------------------------------------------------------------------------


def half_lives_from_fraction(frac: Q) -> int:
    n = sp.log(1 / frac, 2)
    assert n.is_integer
    return int(n)


def half_lives_from_ratio(daughter_to_parent: Q) -> int:
    n = sp.log(daughter_to_parent + 1, 2)  # daughter:parent = 2^n − 1
    assert n.is_integer
    return int(n)


def me_sandstone_bracket(item: dict) -> list[bool]:
    s = zh(item)
    t_lava = Q(re.search(r"甲同位素（半衰期 \$([\d.]+)\$ 億年）", s).group(1))
    p, q = re.search(r"只剩原來的 \$\\tfrac\{(\d+)\}\{(\d+)\}\$", s).groups()
    t_dike = Q(re.search(r"乙同位素（半衰期 \$([\d.]+)\$ 億年）", s).group(1))
    d, pa = re.search(r"\$(\d+):(\d+)\$", s).groups()
    age_lava = half_lives_from_fraction(Q(int(p), int(q))) * t_lava
    age_dike = half_lives_from_ratio(Q(int(d), int(pa))) * t_dike
    # en gives the same half-lives in millions of years
    e = en(item)
    assert Q(re.search(r"half-life \$(\d+)\$ million years\)", e).group(1)) == t_lava * 100
    # (older, younger) relations from the stem's geometry:
    #   dike cuts the sandstone  -> sandstone older than dike (cross-cutting)
    #   lava flow covers the sandstone -> sandstone older than lava (superposition, not overturned)
    #   dike does not cut the lava flow, which lies on top -> dike older than lava
    assert "岩脈切穿了砂岩" in s and "沒有切進上方的熔岩流" in s and "頂面被一層熔岩流覆蓋" in s
    older = [("sandstone", "dike"), ("sandstone", "lava"), ("dike", "lava")]
    ages = {"dike": age_dike, "lava": age_lava}
    for a, b in older:
        if a in ages and b in ages:
            assert ages[a] > ages[b]  # dating agrees with the relative order
    lower = max(ages[b] for a, b in older if a == "sandstone")  # older than everything it precedes
    upper = sp.oo  # nothing in the section is older than the sandstone and dated
    deduced = (lower, upper)
    return [
        deduced == (Q(12, 10), Q(15, 10)),
        deduced == (Q(15, 10), sp.oo),
        deduced == (0, Q(12, 10)),
        deduced == (Q(135, 100), Q(135, 100)),
        lower == Q(12, 10) and upper == sp.oo,
    ]


# --- q31 earth-layers-plates ----------------------------------------------------------------------------

CM_PER_KM = 100000


def me_ridge_two_sides(item: dict) -> list[bool]:
    rows = re.findall(r"\\text\{(西側|東側|中洋脊)\}&(\d+)&([\d.]+)", zh(item))
    assert len(rows) == 5
    en_rows = re.findall(r"\\text\{(west|east|ridge)\}&(\d+)&([\d.]+)", en(item))
    assert [(b, c) for _, b, c in rows] == [(b, c) for _, b, c in en_rows]
    data = {"西側": {}, "東側": {}, "中洋脊": {}}
    for side, dist, age in rows:
        data[side][Q(dist)] = Q(age)

    def rate(side):  # cm per year, must be the same for every row of the side
        rs = {d * CM_PER_KM / (a * 10**6) for d, a in data[side].items()}
        assert len(rs) == 1
        return rs.pop()

    w, e = rate("西側"), rate("東側")
    all_ages = [a for side in data.values() for a in side.values()]
    youngest_at_ridge = min(all_ages) == data["中洋脊"][0] and all_ages.count(min(all_ages)) == 1
    # older sea floor has had longer to collect sediment (earth/s116-earth-layers-plates)
    east_thicker_at_60 = data["東側"][60] > data["西側"][60]
    return [youngest_at_ridge, w > e, e == 3, east_thicker_at_60, w + e == 5]


# --- q32 plate-boundaries-taiwan ------------------------------------------------------------------------

# Predictions per setting (None = the chapter says nothing, so it cannot contradict an observation).
# Source: the evidence table and the subduction / Taiwan sections of earth/s116-plate-boundaries-taiwan.
SETTINGS = {
    "divergent": {"structure": "tension", "metamorphism": False, "deep_sloping_foci": False,
                  "trench": False, "volcano": None},
    "transform": {"structure": "strike-slip", "metamorphism": False, "deep_sloping_foci": False,
                  "trench": False, "volcano": False},
    "subduction": {"structure": "compression", "metamorphism": True, "deep_sloping_foci": True,
                   "trench": True, "volcano": True},
    # neither continental plate sinks; they squeeze and rise into high mountains; deep foci only where a
    # plate is pushed down at a slant
    "collision": {"structure": "compression", "metamorphism": True, "deep_sloping_foci": False,
                  "trench": False, "volcano": None},
    # folds, reverse faults and wide metamorphism are evidence of plates squeezing (Taiwan section): a
    # place away from any boundary would not show them
    "no_boundary": {"structure": None, "metamorphism": False, "deep_sloping_foci": False,
                    "trench": False, "volcano": None},
}


def me_boundary_from_evidence(item: dict) -> list[bool]:
    s = zh(item)
    obs = {
        "structure": "compression" if ("褶皺" in s and "逆斷層" in s) else None,
        "metamorphism": "變質岩" in s,
        "deep_sloping_foci": not ("沒有排成由淺到深的傾斜帶" in s),
        "trench": not ("沒有海溝" in s),
        "volcano": not ("沒有火山" in s),
    }

    def consistent(name):
        pred = SETTINGS[name]
        return all(pred[k] is None or pred[k] == v for k, v in obs.items())

    return [consistent(n) for n in ("divergent", "transform", "subduction", "collision", "no_boundary")]


# --- q33 air-vapour-clouds ------------------------------------------------------------------------------


def me_two_towns_dew_point(item: dict) -> list[bool]:
    s = zh(item)
    table = {Q(t): Q(p) for t, p in re.findall(r"\$(\d+)\$℃為 \$(\d+)\$ hPa", s)}
    temps = sorted(table)
    assert all(table[a] < table[b] for a, b in zip(temps, temps[1:]))  # rises with temperature

    def svp(t):
        return table[Q(t)]

    def dew_point(vp):
        """Temperature where the (piecewise linear) saturation curve reaches vp; only its order matters."""
        for a, b in zip(temps, temps[1:]):
            if table[a] <= vp <= table[b]:
                return a + (b - a) * (vp - table[a]) / (table[b] - table[a])
        raise AssertionError("vapour pressure outside the table")

    (ta, ra), (tb, rb) = [(Q(t), Q(r)) for t, r in re.findall(r"地氣溫 \$(\d+)\$℃、相對濕度 \$(\d+)\\%\$", s)]
    vpa, vpb = ra / 100 * svp(ta), rb / 100 * svp(tb)
    dpa, dpb = dew_point(vpa), dew_point(vpb)
    # B cooling below tb: saturated air (vp = svp) meets a smaller saturation value, so the extra condenses
    colder = max(t for t in temps if t < tb)
    b_condenses_on_cooling = vpb > svp(colder)
    return [dpa > dpb, vpb > vpa, dpa == ta, dpa == dpb, not b_condenses_on_cooling]


# --- q34 wind-weather-maps ------------------------------------------------------------------------------

COMPASS = {"東": 90, "南": 180, "西": 270, "北": 0, "東北": 45, "東南": 135, "西南": 225, "西北": 315}
FRICTION = {"land": 2, "sea": 1}  # land rougher than the sea (s116-wind-weather-maps)


def crossing_angle_rank(surface: str) -> int:
    """More friction -> slower wind -> smaller Coriolis force -> larger angle across the isobars."""
    return FRICTION[surface]


def low_arc(from_bearing, hemisphere: str) -> tuple[Q, Q]:
    """Open arc of bearings of the low for every crossing angle 0 < α < 90.
    NH: low is ahead-left of the wind's travel (toward − (90 − α)); SH: ahead-right."""
    toward = (Q(from_bearing) + 180) % 360
    if hemisphere == "N":
        return ((toward - 90) % 360, toward)
    return (toward, (toward + 90) % 360)


def me_east_wind_low(item: dict) -> list[bool]:
    s = zh(item)
    wind = re.search(r"近地面吹(東|南|西|北)風", s).group(1)
    f = COMPASS[wind]
    lo, hi = low_arc(f, "N")
    hlo, hhi = (lo + 180) % 360, (hi + 180) % 360  # the high lies on the opposite side
    slo, shi = low_arc(f, "S")
    toward = (f + 180) % 360
    return [
        arc_within(lo, hi, COMPASS["西南"], 45),
        arc_within(slo, shi, COMPASS["西北"], 45),
        toward == COMPASS["東"],
        arc_within(hlo, hhi, COMPASS["東北"], 45),
        crossing_angle_rank("sea") > crossing_angle_rank("land"),
    ]


# --- q35 ocean-currents-el-nino -------------------------------------------------------------------------


def pacific_state(s: int) -> dict:
    """s = +1: trade winds stronger than usual; s = −1: weaker (El Niño). Source: s116-ocean-currents-el-nino
    table 平常 / 聖嬰現象時 and the w = 1.4 case (反聖嬰)."""
    return {
        "upwelling_east": s,  # trades blow the east's surface water away
        "sst_east": -s,
        "ew_sst_difference": s,  # warm water piles up in the west when trades are strong
        "rain_region": "west" if s > 0 else "east",
        "rain_east": -s,  # air sinks over the cold east
        "west_dry": s < 0,
    }


def me_strong_upwelling_year(item: dict) -> list[bool]:
    s = zh(item)
    assert "湧升流比平常更明顯" in s and "表層海溫比平常低" in s
    obs = {"upwelling_east": 1, "sst_east": -1}
    fits = [k for k in (1, -1) if all(pacific_state(k)[a] == v for a, v in obs.items())]
    assert len(fits) == 1
    k = fits[0]
    st = pacific_state(k)
    return [
        k < 0 and st["rain_region"] == "east",
        st["ew_sst_difference"] < 0,
        k > 0 and st["rain_east"] > 0,
        k < 0 and st["west_dry"],
        k > 0 and st["rain_region"] == "west",
    ]


# --- q36 climate-change ---------------------------------------------------------------------------------


def floating_ice_melt_level_change():
    """Floating ice of mass m displaces mass m of water; melted, it is mass m of water filling that
    volume (densities equal for this rough argument, as in the chapter's StudentAsks)."""
    m, rho = sp.symbols("m rho", positive=True)
    displaced_volume = m / rho
    meltwater_volume = m / rho
    return sp.simplify(meltwater_volume - displaced_volume)


RAISES_SEA_LEVEL = {"land_ice_melt": True, "thermal_expansion": True}  # s116-climate-change StudentAsks
MEASURE_ACTS_ON = {"higher_embankment": "impact", "solar_electric_bus": "emission"}  # the chain figure


def kind(measure: str) -> str:
    return "mitigation" if MEASURE_ACTS_ON[measure] == "emission" else "adaptation"


ADAPTATION_STOPS_WARMING = False  # "調適只能減少損失，不能讓暖化停下來"


def me_coastal_city_measures(item: dict) -> list[bool]:
    return [
        floating_ice_melt_level_change() != 0,
        kind("higher_embankment") == "adaptation",
        ADAPTATION_STOPS_WARMING,
        RAISES_SEA_LEVEL["land_ice_melt"] and RAISES_SEA_LEVEL["thermal_expansion"],
        kind("solar_electric_bus") == "mitigation",
    ]


# --- q54–q56 typhoons -----------------------------------------------------------------------------------

BEARING = {"正東方": 90, "正北方": 0, "正西方": 270, "正南方": 180}


def island_table(item: dict) -> list[tuple[int, int, Q, Q]]:
    rows = re.findall(r"(\d+)&\\text\{(正東方|正北方|正西方|正南方)\}&(\d+)&(\d+)", zh(item))
    assert len(rows) == 3
    en_rows = re.findall(r"(\d+)&\\text\{due ([ENSW])\}&(\d+)&(\d+)", en(item))
    letter = {"正東方": "E", "正北方": "N", "正西方": "W", "正南方": "S"}
    assert [(h, letter[c], a, b) for h, c, a, b in rows] == en_rows
    return [(int(h), BEARING[c], Q(a), Q(b)) for h, c, a, b in rows]


def me_island_wind_east_centre(item: dict) -> list[bool]:
    s = zh(item)
    assert "東西走向" in s and "北半球" in s
    # q55/q56 read the shared table from Q54_ZH / Q54_EN: they must be exactly this stem's table
    assert Q54_ZH in s and Q54_EN in en(item)
    rows = island_table(item)
    asked = int(re.search(r"第(\d+)時，島上近地面的風", s).group(1))
    c = next(b for h, b, _, _ in rows if h == asked)
    lo, hi = nh_from_arc_around_low(c)
    distance_km = Q(re.search(r"離島嶼都約 \$(\d+)\$ km", s).group(1))
    in_eye = distance_km == 0  # the eye is at the centre
    return [arc_of(lo, hi, "北東"), arc_of(lo, hi, "東南"), arc_of(lo, hi, "南西"), arc_of(lo, hi, "西北"), in_eye]


def _set_intro(item: dict) -> dict:
    """q55/q56 continue q54: the shared table is restated here from the q54 stem text."""
    return {"text": {"zh-tw": {"stem": Q54_ZH}, "en": {"stem": Q54_EN}}}


# The set's shared context (q54 stem), kept in sync with the bank by me_island_wind_east_centre's parser.
Q54_ZH = (r"$$\begin{array}{c|c|c|c}\text{時刻}&\text{中心}&\text{甲}&\text{乙}\\ \hline "
          r"6&\text{正東方}&24&3\\ 12&\text{正北方}&6&11\\ 18&\text{正西方}&2&30\end{array}$$")
Q54_EN = (r"$$\begin{array}{c|c|c|c}\text{Hour}&\text{Centre}&\text{A}&\text{B}\\ \hline "
          r"6&\text{due E}&24&3\\ 12&\text{due N}&6&11\\ 18&\text{due W}&2&30\end{array}$$")


def windward_station(c) -> str | None:
    slope = windward_slope_ew_ridge(*nh_from_arc_around_low(c))
    return {"north": "甲", "south": "乙", None: None}[slope]


def me_island_rain_statements(item: dict) -> list[bool]:
    assert "承第54題" in zh(item)
    rows = island_table(_set_intro(item))
    by_hour = {h: (c, a, b) for h, c, a, b in rows}
    hours = sorted(by_hour)
    # (1) centre bearing when B is largest
    h_bmax = max(hours, key=lambda h: by_hour[h][2])
    s1 = by_hour[h_bmax][0] == BEARING["正東方"]
    # (2) hour 6: A windward and A > B
    c6, a6, b6 = by_hour[6]
    s2 = windward_station(c6) == "甲" and a6 > b6
    # (3) clockwise seen from above = increasing bearing
    steps = [norm(by_hour[h2][0], by_hour[h1][0]) for h1, h2 in zip(hours, hours[1:])]
    assert all(st != 0 and abs(st) < 180 for st in steps)
    s3 = all(st > 0 for st in steps)
    # (4) the two stations' rainfall added together is smallest at hour 12 (a table reading; it does
    # not state any wind direction that q56 asks for)
    totals = {h: by_hour[h][1] + by_hour[h][2] for h in hours}
    s4 = min(totals, key=totals.get) == 12 and list(totals.values()).count(min(totals.values())) == 1
    # (5) independent of terrain would need the windward station not to be the wetter one
    terrain_matters = all(
        (windward_station(c) == "甲" and a > b) or (windward_station(c) == "乙" and b > a)
        for h, (c, a, b) in by_hour.items() if windward_station(c) is not None
    )
    s5 = not terrain_matters
    return [s1, s2, s3, s4, s5]


def me_island_written(item: dict) -> bool:
    """q56: the model answer's winds at hour 12 (centre N: from S–W) and hour 18 (centre W: from E–S),
    the windward station at both (乙), the stem's claims about the table (A > B at hour 6; B > A from
    hour 12 on) and the rainfall the model quotes all follow from the q54 setting."""
    s = zh(item)
    assert "承第54題" in s and "第12時（颱風中心在正北方）" in s and "第18時（颱風中心在正西方）" in s
    rows = island_table(_set_intro(item))
    by_hour = {h: (c, a, b) for h, c, a, b in rows}
    assert by_hour[12][0] == BEARING["正北方"] and by_hour[18][0] == BEARING["正西方"]
    model = item["model"]["zh-tw"]
    quoted = re.findall(r"\$(\d+)\$ mm/h", model)
    crit = item["rubric"]["criteria"]
    return (
        arc_of(*nh_from_arc_around_low(BEARING["正北方"]), "南西")
        and arc_of(*nh_from_arc_around_low(BEARING["正西方"]), "東南")
        and windward_station(BEARING["正北方"]) == "乙"
        and windward_station(BEARING["正西方"]) == "乙"
        and by_hour[6][1] > by_hour[6][2]
        and all(by_hour[h][2] > by_hour[h][1] for h in (12, 18))
        and [Q(x) for x in quoted] == [by_hour[12][2], by_hour[18][2], by_hour[12][1], by_hour[18][1]]
        and len(crit) == 4 and all(c["points"] == 1 for c in crit)
    )
