"""Checks for src/data/items/physics/s116-galileo-kepler.yaml (116 sprint: PEb-Ⅴc-1~3).

Each function recomputes its item's answer from the physics (or, for history/method items, from an
explicit facts table with a source per fact); none reads item["answer"].
Numeric work uses exact SymPy Rationals.
"""

from __future__ import annotations

import sympy as sp

g, h, m, t = sp.symbols("g h m t", positive=True)

# ---------- facts tables (history and method) ----------

# Who held which view. Sources: nat.json PEb-Ⅴc-1 (observation and debate about motion before Galileo),
# PEb-Ⅴc-2 (Galileo's research and reasoning about motion), PEb-Ⅴc-3 (Kepler's three laws as an inductive
# result from accumulated observation data); research physics final_units 6 (Newton explains Kepler's
# laws deductively). The views themselves are standard history of physics taught under these codes.
VIEWS = {
    "motion-needs-a-sustaining-push": "aristotle",      # PEb-Ⅴc-1: pre-Galilean view of motion
    "heavier-falls-faster": "aristotle",                # PEb-Ⅴc-1
    "no-friction-motion-continues": "galileo",          # PEb-Ⅴc-2: Galileo's reasoning (inclined planes)
    "all-bodies-fall-together-in-vacuum": "galileo",    # PEb-Ⅴc-2
    "planet-orbits-are-ellipses": "kepler",             # PEb-Ⅴc-3
}

# How each law was reached. Source: nat.json PEb-Ⅴc-3 keyConcepts ("an inductive result from
# accumulated observation data"); research physics final_units 6 ("Deductive (Newton) vs inductive
# (Kepler) reasoning").
METHOD = {
    "kepler-laws": "induction-from-observation-data",
    "newton-explains-kepler": "deduction-from-laws",
}

# Order of events (standard history; years are the publication years taught with PEb-Ⅴc-3 and PKb-Ⅴc-1):
# Kepler's first two laws 1609, third law 1619; Newton's Principia 1687.
YEAR = {"kepler-law-1-2": 1609, "kepler-law-3": 1619, "newton-principia": 1687}


# ---------- small physics models ----------

def _fall_time(mass, height):
    """Free fall from rest in a vacuum (Galileo): h = g t^2 / 2, with no dependence on the mass.
    The mass is an argument on purpose: the formula below simply has no place for it."""
    (tt,) = sp.solve(sp.Eq(height, g * t**2 / 2), t)
    return tt


def _ideal_height_reached(h0):
    """Frictionless double incline: mechanical energy m g h is conserved, so the ball climbs back to h0."""
    h1 = sp.Symbol("h1", positive=True)
    (sol,) = sp.solve(sp.Eq(m * g * h0, m * g * h1), h1)
    return sol


def _distance_along_slope(h1, theta):
    """Distance travelled up a slope of angle theta to rise h1."""
    return h1 / sp.sin(theta)


def _kepler_period(a):
    """Kepler's third law in years and AU (Sun as the central body): T^2 = a^3."""
    T = sp.Symbol("T", positive=True)
    (sol,) = sp.solve(sp.Eq(T**2, a**3), T)
    return sol


def _kepler_axis(T):
    """Inverse of _kepler_period: a^3 = T^2."""
    a = sp.Symbol("a", positive=True)
    (sol,) = sp.solve(sp.Eq(a**3, T**2), a)
    return sp.nsimplify(sol)


def _nearest(value, options):
    """Truth list: True for the option closest to value (exact comparison)."""
    d = [sp.Abs(value - o) for o in options]
    best = min(d, key=lambda z: sp.N(z, 30))
    return [bool(sp.simplify(z - best) == 0) for z in d]


# ---------- items ----------

def gk_turn_free_fall(item: dict) -> list[bool]:
    """q-turn: in a vacuum, an iron ball and one of 10 times its mass are released together from the
    same height. Options: (1) heavy first, in about 1/10 of the time; (2) heavy first, slightly;
    (3) together; (4) light first; (5) depends on the size of the balls."""
    t_light = _fall_time(m, h)
    t_heavy = _fall_time(10 * m, h)
    same = sp.simplify(t_heavy - t_light) == 0
    heavy_first = bool(sp.simplify(t_light - t_heavy) > 0) if not same else False
    light_first = bool(sp.simplify(t_heavy - t_light) > 0) if not same else False
    tenth = sp.simplify(t_heavy - t_light / 10) == 0
    # (5): the vacuum fall time has no size parameter at all
    size_matters = bool(t_light.free_symbols - {g, h})
    return [heavy_first and tenth, heavy_first and not tenth, same, light_first, size_matters]


def gk_double_incline(item: dict) -> list[bool]:
    """q1 (multi): Galileo's frictionless double incline, released from height h0.
    (1) climbs back to the starting height; (2) gentler second slope → travels farther along it;
    (3) gentler second slope → climbs less high; (4) horizontal second track → moves on forever at
    constant speed; (5) it keeps moving because a force keeps pushing it along."""
    h0 = sp.Symbol("h0", positive=True)
    th = sp.Symbol("theta", positive=True)
    h1 = _ideal_height_reached(h0)
    s1 = sp.simplify(h1 - h0) == 0
    d = _distance_along_slope(h1, th)
    # d decreases with theta on (0, pi/2): derivative < 0 there
    dd = sp.diff(d, th)
    s2 = all(bool(dd.subs(th, v) < 0) for v in (sp.pi / 12, sp.pi / 6, sp.pi / 4, sp.pi / 3))
    s3 = bool(sp.diff(h1, th) != 0)  # the height reached does not depend on the slope
    # horizontal track: the distance needed to regain h0 grows without bound as theta -> 0, and with no
    # change of height the kinetic energy (so the speed) cannot change
    s4 = sp.limit(d, th, 0, "+") == sp.oo
    # (5): along a frictionless horizontal track the only forces (weight, normal force) are vertical,
    # so the force along the motion is zero
    weight, normal = sp.Matrix([0, -m * g]), sp.Matrix([0, m * g])
    along = (weight + normal)[0]
    s5 = along != 0
    return [s1, s2, s3, s4, s5]


def gk_tied_stones(item: dict) -> list[bool]:
    """q2: Galileo's tied-stones argument against 'heavier falls faster' (speed ∝ weight).
    Options: (1) the tied pair must be both slower and faster than the heavy stone: a contradiction;
    (2) the light stone lands first; (3) the tied stones hover; (4) the heavy stone's weight shrinks;
    (5) air resistance slows the heavy stone."""
    k, wh, wl = sp.symbols("k w_H w_L", positive=True)
    v = lambda w: k * w  # the Aristotelian premise
    vh, vl = v(wh), v(wl)
    # reading 1: the slower light stone holds the heavy one back -> pair speed strictly between vl and vh
    lam = sp.Symbol("lam", positive=True)
    pair_drag = lam * vh + (1 - lam) * vl  # 0 < lam < 1
    slower = sp.simplify((pair_drag - vh).subs({wh: 10, wl: 1, lam: sp.Rational(1, 2)})) < 0
    # reading 2: the pair weighs w_H + w_L -> faster than the heavy stone alone
    faster = sp.simplify(v(wh + wl) - vh) > 0
    contradiction = bool(slower) and bool(faster)
    sub = {wh: 10, wl: 1, k: 1}
    # (2) under the premise the light stone is the slower one, so it cannot land first
    light_first = bool((vl - vh).subs(sub) > 0)
    # (3) both readings give the pair a positive speed: it does not hover
    hovers = bool(pair_drag.subs({**sub, lam: sp.Rational(1, 2)}) == 0) or bool(v(wh + wl).subs(sub) == 0)
    # (4) the weights are fixed inputs of the argument; nothing in it changes them
    weight_shrinks = False
    # (5) the argument is pure logic on the premise v = k w: no air-resistance term appears anywhere
    air_term_used = any(str(s).startswith("air") for s in (pair_drag.free_symbols | v(wh + wl).free_symbols))
    return [contradiction, light_first, hovers, weight_shrinks, air_term_used]


def gk_asteroid_axis(item: dict) -> sp.Integer:
    """q3: an asteroid of the Sun with period 27 years; its semi-major axis in AU (T^2 = a^3)."""
    return sp.Integer(_kepler_axis(sp.Integer(27)))


def gk_ceres_period(item: dict) -> list[bool]:
    """q4: Ceres, a = 2.77 AU; period closest to 1.7, 2.8, 4.6, 7.7, 21.3 years."""
    T = _kepler_period(sp.Rational(277, 100))
    opts = [sp.Rational(17, 10), sp.Rational(28, 10), sp.Rational(46, 10), sp.Rational(77, 10), sp.Rational(213, 10)]
    return _nearest(T, opts)


def gk_kepler_statements(item: dict) -> list[bool]:
    """q5 (multi): (1) ellipse with the Sun at one focus; (2) Sun at the centre of the ellipse;
    (3) faster near perihelion than near aphelion; (4) farther planets have longer periods;
    (5) the laws were first derived from Newton's gravitation and only then found in the data."""
    s1 = VIEWS["planet-orbits-are-ellipses"] == "kepler"  # first law: ellipse, Sun at a focus
    # (2) the Sun sits at a focus (c, 0) with c^2 = a^2 - b^2; it is the centre (0, 0) only if c = 0,
    # i.e. a circle. A planetary ellipse (b < a, e.g. the lesson's a = 5, b = 4) has c > 0.
    ae, be = sp.Integer(5), sp.Integer(4)
    s2 = sp.sqrt(ae**2 - be**2) == 0
    # (3) equal areas in equal times: a thin triangle of area r*v*dt/2 at each apsis -> v ∝ 1/r
    rp, ra, A = sp.symbols("r_p r_a A", positive=True)
    vp, va = 2 * A / rp, 2 * A / ra  # same swept area A per unit time
    s3 = bool(sp.simplify((vp - va).subs({rp: 1, ra: 3})) > 0) and bool(sp.simplify(vp / va - ra / rp) == 0)
    # (4) T = a^(3/2) increases with a
    a = sp.Symbol("a", positive=True)
    s4 = bool(sp.diff(_kepler_period(a), a).subs(a, 1) > 0) and sp.simplify(sp.diff(_kepler_period(a), a)).is_positive
    # (5) Kepler (1609, 1619) came before Newton (1687), and the laws were induced from data
    s5 = YEAR["newton-principia"] < YEAR["kepler-law-1-2"] or METHOD["kepler-laws"] == "deduction-from-laws"
    return [bool(s1), s2, s3, bool(s4), bool(s5)]


def gk_kepler_method(item: dict) -> list[bool]:
    """q6: how Kepler reached his laws. Options: (1) induction from many precise observations;
    (2) deduction from universal gravitation; (3) a thought experiment; (4) controlled lab experiments;
    (5) the philosophical rule that heavenly bodies move in perfect circles."""
    m_ = METHOD["kepler-laws"]
    return [
        m_ == "induction-from-observation-data",
        m_ == "deduction-from-laws",
        m_ == "thought-experiment",
        m_ == "controlled-lab-experiment",
        m_ == "philosophical-principle",
    ]


def gk_moons_table(item: dict) -> list[bool]:
    """q7 (multi): moons of one planet; moon A: a = 2, T = 4; moon B: a = 8, T = 32 (same units).
    (1) A and B have the same T^2/a^3; (2) a moon with a = 18 has T = 108; (3) a 4 times larger → T 4 times;
    (4) a doubled → T multiplied by 2√2; (5) in the same units, these moons and Earth around the Sun
    must share the same T^2/a^3."""
    kA = sp.Rational(4**2, 2**3)
    kB = sp.Rational(32**2, 8**3)
    s1 = kA == kB
    T18 = sp.sqrt(kA * 18**3)
    s2 = T18 == 108
    a = sp.Symbol("a", positive=True)
    Tof = lambda r: sp.sqrt(kA * r**3)
    s3 = sp.simplify(Tof(4 * a) / Tof(a)) == 4
    s4 = sp.simplify(Tof(2 * a) / Tof(a) - 2 * sp.sqrt(2)) == 0
    # (5) T^2/a^3 = 4π²/(G M): it depends on the central body's mass; a planet and the Sun differ in mass
    G, M_planet, M_sun = sp.symbols("G M_planet M_sun", positive=True)
    K = lambda M: 4 * sp.pi**2 / (G * M)
    s5 = sp.simplify(K(M_planet) - K(M_sun)).subs({M_planet: 1, M_sun: 1000}) == 0
    return [s1, s2, bool(s3), bool(s4), bool(s5)]


def gk_real_incline_energy(item: dict) -> list[bool]:
    """q8: on a real double incline the ball stops a little below its starting height. Why?
    Options: (1) friction and air resistance turn part of the mechanical energy into heat;
    (2) gravity is weaker on the second slope; (3) the ball's mass decreases; (4) the second slope is
    steeper; (5) total energy is not conserved."""
    h0, Wf = sp.symbols("h0 W_f", positive=True)
    h1 = sp.Symbol("h1")
    (h_end,) = sp.solve(sp.Eq(m * g * h0, m * g * h1 + Wf), h1)  # energy turned to heat: W_f > 0
    lower_because_of_heat = bool(sp.simplify(h_end - h0).is_negative)
    # the ideal height does not depend on g, the mass or the slope angle (see _ideal_height_reached)
    ideal = _ideal_height_reached(h0)
    # (2) one g for both slopes (the same Earth): the energy balance above uses a single g
    g_differs = len({s for s in (m * g * h0).free_symbols | (m * g * h1).free_symbols if str(s).startswith("g")}) > 1
    # (3) the mass cancels from the balance: h_end = h0 - W_f/(m g) only shifts by the heat term,
    # and in the ideal case the height reached has no mass in it at all
    mass_in_ideal = m in ideal.free_symbols
    th = sp.Symbol("theta", positive=True)
    depends_on_slope = bool(sp.diff(ideal, th) != 0)
    total_conserved = sp.simplify((m * g * h_end + Wf) - m * g * h0) == 0
    return [lower_because_of_heat, g_differs, mass_in_ideal, depends_on_slope, not total_conserved]


# ---------- the lesson's data table (not an item; kept so the numbers in the text are checked) ----------

# Standard planetary data: semi-major axis a (AU) and sidereal period T (years), rounded as in the lesson.
PLANETS = {
    "Mercury": (sp.Rational(387, 1000), sp.Rational(241, 1000)),
    "Venus": (sp.Rational(723, 1000), sp.Rational(615, 1000)),
    "Earth": (sp.Integer(1), sp.Integer(1)),
    "Mars": (sp.Rational(1524, 1000), sp.Rational(1881, 1000)),
    "Jupiter": (sp.Rational(5203, 1000), sp.Rational(1186, 100)),
    "Saturn": (sp.Rational(9537, 1000), sp.Rational(2946, 100)),
}


def table_ratios_round_to_one() -> bool:
    """Every T^2/a^3 in the lesson table rounds to 1.00."""
    return all(abs(sp.N(T**2 / a**3, 20) - 1) < sp.Rational(5, 1000) for a, T in PLANETS.values())


def worked_example_period() -> bool:
    """Lesson worked example: a = 4 AU gives T = 8 years."""
    return _kepler_period(sp.Integer(4)) == 8


def worked_example_apsis_speeds() -> bool:
    """Lesson perspective: ellipse with a = 5, c = 3 → r_p = 2, r_a = 8; equal thin triangles give
    v_p / v_a = r_a / r_p = 4. Also check that the two drawn sectors have (nearly) equal areas, which
    the lesson figure claims (about 6 each)."""
    a, c = sp.Integer(5), sp.Integer(3)
    rp, ra = a - c, a + c
    sp_, sa = sp.symbols("s_p s_a", positive=True)
    (ratio,) = sp.solve(sp.Eq(rp * sp_ / 2, ra * sa / 2), sp_)
    ok_ratio = sp.simplify(ratio / sa) == 4
    peri = [(3, 0), (3.9, -2.5), (4.32, -2.01), (4.67, -1.42), (4.91, -0.74), (5, 0), (4.91, 0.74), (4.67, 1.42), (4.32, 2.01), (3.9, 2.5)]
    apo = [(3, 0), (-4.91, 0.75), (-4.95, 0.56), (-4.98, 0.37), (-4.99, 0.19), (-5, 0), (-4.99, -0.19), (-4.98, -0.37), (-4.95, -0.56), (-4.91, -0.75)]
    area = lambda P: abs(sp.Rational(1, 2) * sum(sp.nsimplify(P[i][0]) * sp.nsimplify(P[(i + 1) % len(P)][1]) - sp.nsimplify(P[(i + 1) % len(P)][0]) * sp.nsimplify(P[i][1]) for i in range(len(P))))
    A1, A2 = area(peri), area(apo)
    ok_areas = abs(A1 - A2) < sp.Rational(3, 10) and abs(A1 - 6) < sp.Rational(1, 2)
    # Earth: perihelion and aphelion distances differ by about 3 % (0.983 vs 1.017 AU, standard values)
    ok_earth = abs((sp.Rational(1017, 1000) - sp.Rational(983, 1000)) - sp.Rational(3, 100)) < sp.Rational(1, 100)
    return bool(ok_ratio) and bool(ok_areas) and bool(ok_earth)


assert table_ratios_round_to_one()
assert worked_example_period()
assert worked_example_apsis_speeds()
