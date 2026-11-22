"""Checks for src/data/items/earth/s116-sky-motion.yaml (116 sprint: EFb-Ⅴc-1 diurnal and annual
motion of the stars; EId-Ⅴc-1 the Sun's daily path at the local equinoxes and solstices).

How the keys are recomputed (never from item["answer"]):
- A small celestial-sphere engine in the observer's local frame (east, north, up). The sky turns about
  the axis that points to the north celestial pole; a star is placed by its angular distance p from that
  pole and an hour angle H that grows westward with time. Altitudes, rising directions, whether a star
  ever rises or sets, and the part of a day a star (or the Sun) spends above the horizon all come out of
  the vectors, not out of typed rules. The chapter uses no celestial coordinates; p and H live only here.
- Exact SymPy trigonometry on rational degrees; signs and comparisons are decided numerically to high
  precision and asserted to be far from zero, so no answer rests on a rounding.
- The Sun is a star whose p changes with the season (table SUN_SHIFT below).

Facts used, with their sources:
- The sky turns east to west about the axis through the celestial poles, once a day, because Earth
  rotates west to east (EFb-Ⅴc-1 恆星的周日運動; 國中 Fb-Ⅳ-1 rotation and revolution, as dependsOn in
  src/data/registry/codes/nat.json).
- The Sun's daily path moves north and south with the seasons because Earth's axis is tilted to its
  orbital plane (EId-Ⅴc-1; 國中 Id-Ⅳ-3, slice research.common_misconceptions).
- TILT = 23.5°: the standard textbook value of the axial tilt. NOT in the sources; listed for the owner.
- One solar day is a little longer than one turn relative to the stars, because revolution runs the same
  way as rotation (國中 Fb-Ⅳ-1); the per-day shift is 360°/365 (a year of about 365 days, standard).
"""

from __future__ import annotations

from fractions import Fraction as F

import sympy as sp

D = sp.pi / 180
TILT = sp.Rational(47, 2)  # degrees; standard textbook value, not in the sources (see module docstring)
TURN_HOURS = 24  # the sky turns once in about a day (EFb-Ⅴc-1)
DAYS_PER_YEAR = 365  # standard; only the sign of the annual shift is used by the items

# Season -> how far the Sun's daily path is shifted north of the celestial equator (EId-Ⅴc-1).
SUN_SHIFT = {"春分": 0, "夏至": TILT, "秋分": 0, "冬至": -TILT}


def _num(x) -> float:
    v = sp.N(x, 40)
    return float(v)


def _sign(x) -> int:
    v = sp.N(x, 40)
    assert abs(v) > sp.Float("1e-20"), f"undecided sign: {x}"
    return 1 if v > 0 else -1


def frame(lat):
    """Unit vectors (east, north, up) and the sky's axis k, the meridian direction m on the equator
    (south-up side) and east e, at latitude lat in degrees (north positive)."""
    f = sp.Rational(lat) * D
    e = sp.Matrix([1, 0, 0])
    k = sp.Matrix([0, sp.cos(f), sp.sin(f)])
    m = sp.Matrix([0, -sp.sin(f), sp.cos(f)])
    return e, k, m


def star(lat, p, H):
    """Direction to a star at angular distance p (deg) from the north celestial pole, hour angle H (deg,
    westward from the meridian)."""
    e, k, m = frame(lat)
    pp, hh = sp.Rational(p) * D, sp.Rational(H) * D if not isinstance(H, sp.Basic) else H * D
    return sp.cos(pp) * k + sp.sin(pp) * (sp.cos(hh) * m - sp.sin(hh) * e)


def velocity(lat, p, H):
    """d(direction)/dH: the way the star is moving at hour angle H."""
    Hs = sp.Symbol("H")
    r = star(lat, p, Hs)
    return r.diff(Hs).subs(Hs, sp.Rational(H) if not isinstance(H, sp.Basic) else H)


def altitude_sin(lat, p, H):
    return star(lat, p, H)[2]


def alt_range(lat, p):
    """(min, max) of sin(altitude) over a day: the up-component is A + B cos H."""
    e, k, m = frame(lat)
    pp = sp.Rational(p) * D
    A = sp.cos(pp) * k[2]
    B = sp.sin(pp) * m[2]
    return sp.simplify(A - abs(B)), sp.simplify(A + abs(B))


def never_sets(lat, p) -> bool:
    return _sign(alt_range(lat, p)[0]) > 0


def never_rises(lat, p) -> bool:
    return _sign(alt_range(lat, p)[1]) < 0


def altitude_constant(lat, p) -> bool:
    """True when the star's altitude does not change during the day (path parallel to the horizon)."""
    lo, hi = alt_range(lat, p)
    return abs(_num(hi - lo)) < 1e-25


def fraction_above(lat, p):
    """Share of one turn that a star spends above the horizon (0..1), from A + B cos H > 0."""
    lo, hi = alt_range(lat, p)
    if _sign(lo) > 0:
        return sp.Integer(1)
    if _sign(hi) < 0:
        return sp.Integer(0)
    e, k, m = frame(lat)
    pp = sp.Rational(p) * D
    A, B = sp.cos(pp) * k[2], sp.sin(pp) * m[2]
    H0 = sp.acos(-A / B)  # radians
    return H0 / sp.pi


def rising_hour_angle(lat, p):
    e, k, m = frame(lat)
    pp = sp.Rational(p) * D
    A, B = sp.cos(pp) * k[2], sp.sin(pp) * m[2]
    return -sp.acos(-A / B) / D  # degrees, east of the meridian


def rising_point(lat, p):
    return star(lat, p, rising_hour_angle(lat, p))


def noon_altitude_deg(lat, p):
    """Altitude (deg) when the star crosses the meridian above the pole's opposite side (H = 0)."""
    s = altitude_sin(lat, p, 0)
    h = sp.asin(s) / D
    return h


def sun_p(season: str):
    return 90 - SUN_SHIFT[season]


# --- opening turn ---------------------------------------------------------------------------------


def sm_turn_north_pole(item: dict) -> list[bool]:
    """q-turn: at latitude 90°, how do the stars move during the night? Tested on a spread of stars
    above the horizon (p = 10..80°)."""
    lat = 90
    ps = [10, 30, 50, 80]
    o1 = any(not never_sets(lat, p) and not never_rises(lat, p) for p in range(1, 180, 7))  # rise E, set W
    o2 = all(altitude_constant(lat, p) for p in ps) and all(never_sets(lat, p) for p in ps)
    # vertical rising needs a rising at all
    o3 = o1
    # standing still: the direction changes with H for any p > 0
    o4 = all(_num((star(lat, p, 0) - star(lat, p, 90)).norm()) < 1e-25 for p in ps)
    # half the visible stars circle, half rise and set: needs some stars that rise and set
    o5 = o1
    return [o1, o2, o3, o4, o5]


# --- quiz -----------------------------------------------------------------------------------------


def sm_trail_hours(item: dict) -> int:
    """q1: a trail arc of 75°; hours of exposure at one turn per TURN_HOURS."""
    rate = F(360, TURN_HOURS)
    hours = F(75) / rate
    assert hours.denominator == 1
    return int(hours)


def sm_pole_altitude(item: dict) -> list[bool]:
    """q2: Polaris (taken as at the north celestial pole) stands 35° above the northern horizon.
    Options: N35, N55, S35, S55, equator. The pole's altitude is asin(k_up)."""
    target = sp.Rational(35)
    lats = [35, 55, -35, -55, 0]
    out = []
    for lat in lats:
        h = sp.asin(frame(lat)[1][2]) / D
        out.append(abs(_num(h - target)) < 1e-25)
    return out


def sm_equator(item: dict) -> list[bool]:
    """q3 (multi), at latitude 0: (1) both celestial poles lie on the horizon; (2) every star rises
    perpendicular to the horizon; (3) some stars never set; (4) every star is above the horizon for about
    half a turn; (5) Polaris is at the zenith."""
    lat = 0
    e, k, m = frame(lat)
    s1 = abs(_num(k[2])) < 1e-25 and abs(_num(-k[2])) < 1e-25
    ps = [5, 30, 60, 90, 120, 150, 175]
    s2 = True
    for p in ps:
        v = velocity(lat, p, rising_hour_angle(lat, p))
        horiz = sp.sqrt(v[0] ** 2 + v[1] ** 2)
        s2 = s2 and abs(_num(horiz)) < 1e-25 and _sign(v[2]) > 0
    s3 = any(never_sets(lat, p) for p in ps)
    s4 = all(abs(_num(fraction_above(lat, p) - sp.Rational(1, 2))) < 1e-25 for p in ps)
    s5 = abs(_num(k[2] - 1)) < 1e-25
    return [s1, s2, s3, s4, s5]


def _rise_tilt(lat):
    """For a star on the celestial equator (rises due east): (angle with the horizon in degrees,
    'south' or 'north' for the horizontal drift at rising)."""
    v = velocity(lat, 90, rising_hour_angle(lat, 90))
    horiz = sp.sqrt(v[0] ** 2 + v[1] ** 2)
    ang = sp.atan2(v[2], horiz) / D
    drift = "north" if _sign(v[1]) > 0 else "south"
    assert _sign(v[2]) > 0  # it is climbing
    # rises due east: the rising point has no north component
    assert abs(_num(rising_point(lat, 90)[1])) < 1e-25 and _sign(rising_point(lat, 90)[0]) > 0
    return ang, drift


def sm_rise_tilt(item: dict) -> list[bool]:
    """q4: facing due east at 10°N and at 40°N, a star rising due east. Facing east, 'right' is south.
    (1) both drift right (south) and the 10°N path is steeper; (2) both drift left (north), 10°N
    steeper; (3) both drift right, 40°N steeper; (4) both rise vertically; (5) right at 10°N, left at
    40°N."""
    a10, d10 = _rise_tilt(10)
    a40, d40 = _rise_tilt(40)
    steeper10 = _sign(a10 - a40) > 0
    vertical = abs(_num(a10 - 90)) < 1e-25 and abs(_num(a40 - 90)) < 1e-25
    return [
        d10 == d40 == "south" and steeper10,
        d10 == d40 == "north" and steeper10,
        d10 == d40 == "south" and not steeper10,
        vertical,
        d10 == "south" and d40 == "north",
    ]


def sm_month_later(item: dict) -> list[bool]:
    """q5: at 28°N a star rises due east at 10 p.m. Sixty days later at 10 p.m.: (1) still on the eastern
    horizon; (2) risen, in the south-eastern sky; (3) still below the horizon; (4) in the western sky
    (above the horizon); (5) moved into the northern sky. Per solar day the sky has turned an extra
    360°/365 westward relative to the stars (hour angle grows)."""
    lat = 28
    p = 90  # the star that rises due east: find it from the rising point, do not assume it
    rp = rising_point(lat, p)
    assert abs(_num(rp[1])) < 1e-25 and _sign(rp[0]) > 0  # rising point has no north component: due east
    H0 = rising_hour_angle(lat, p)
    H = H0 + sp.Rational(60 * 360, DAYS_PER_YEAR)
    before = star(lat, p, H0)
    after = star(lat, p, H)
    same = _num((after - before).norm()) < 1e-25
    up = _sign(after[2]) > 0
    east = _sign(after[0]) > 0
    south = _sign(after[1]) < 0
    return [
        same,
        up and east and south,
        _sign(after[2]) < 0,
        up and _sign(after[0]) < 0,
        _sign(after[1]) > 0,
    ]


def sm_shortest_shadow(item: dict) -> list[bool]:
    """q6: at 30°N, on which day is the noon shadow of a vertical stick shortest? Shadow length is
    cot(noon altitude); shortest = highest noon Sun. Options: 春分, 夏至, 秋分, 冬至, all the same."""
    lat = 30
    days = ["春分", "夏至", "秋分", "冬至"]
    hs = {d: noon_altitude_deg(lat, sun_p(d)) for d in days}
    best = max(_num(h) for h in hs.values())
    winners = [d for d in days if abs(_num(hs[d]) - best) < 1e-12]
    out = [d in winners and len(winners) == 1 for d in days]
    out.append(len(winners) == len(days))
    return out


def sm_summer_40(item: dict) -> list[bool]:
    """q7 (multi): at 40°N on 夏至: (1) sunrise north of due east; (2) noon Sun at the zenith; (3) day
    longer than night; (4) noon stick shadow points north; (5) sunset due west."""
    lat = 40
    p = sun_p("夏至")
    rise = rising_point(lat, p)
    s1 = _sign(rise[1]) > 0 and _sign(rise[0]) > 0
    s2 = abs(_num(noon_altitude_deg(lat, p) - 90)) < 1e-25
    s3 = _sign(fraction_above(lat, p) - sp.Rational(1, 2)) > 0
    noon = star(lat, p, 0)
    s4 = _sign(noon[1]) < 0  # Sun to the south, so the shadow points north
    set_pt = star(lat, p, -rising_hour_angle(lat, p))
    s5 = abs(_num(set_pt[1])) < 1e-25
    return [s1, s2, s3, s4, s5]


def sm_winter_noon(item: dict) -> int:
    """q8: noon altitude of the Sun on 冬至 at 33.5°N, in degrees."""
    lat = sp.Rational(67, 2)
    h = noon_altitude_deg(lat, sun_p("冬至"))
    exact = 90 - abs(lat - SUN_SHIFT["冬至"])  # the chapter's rule, cross-checked against the vectors
    assert abs(_num(h - exact)) < 1e-25
    assert exact.q == 1
    return int(exact)
