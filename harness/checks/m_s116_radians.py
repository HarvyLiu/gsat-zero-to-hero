"""Checks for src/data/items/math/s116-radians.yaml (116 sprint: radian measure, N-11A-1 / N-11B-1).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Radian measure is taken from its definition (arc length / radius); arc length and sector area are
computed as fractions of the full circle (2πr and πr²), not from the formulas the chapter teaches.
"""

from __future__ import annotations

import sympy as sp

r_ = sp.Symbol("r", positive=True)


def _deg_to_rad(deg) -> sp.Expr:
    """Radian measure of a central angle of `deg` degrees: its arc over the radius, with the arc
    as the fraction deg/360 of the circumference 2πr. The radius cancels."""
    arc = sp.Rational(deg) / 360 * 2 * sp.pi * r_
    return sp.simplify(arc / r_)


def _rad_to_deg(theta) -> sp.Expr:
    """Degrees of an angle of `theta` radians: the fraction theta/(2π) of a full 360° turn."""
    return sp.simplify(sp.sympify(theta) / (2 * sp.pi) * 360)


def _arc(r, theta) -> sp.Expr:
    """Arc length cut off by a central angle theta (radians): that fraction of the circumference."""
    return sp.simplify(sp.sympify(theta) / (2 * sp.pi) * 2 * sp.pi * r)


def _sector_area(r, theta) -> sp.Expr:
    """Sector area for central angle theta (radians): that fraction of the disc πr²."""
    return sp.simplify(sp.sympify(theta) / (2 * sp.pi) * sp.pi * sp.sympify(r) ** 2)


def _quadrant_of_rad(theta) -> int:
    """1–4 for the quadrant of the terminal side, 0 on an axis (decided by the signs of cos and sin)."""
    c, s = sp.cos(theta), sp.sin(theta)
    if sp.simplify(c) == 0 or sp.simplify(s) == 0:
        return 0
    return {(True, True): 1, (False, True): 2, (False, False): 3, (True, False): 4}[(bool(c > 0), bool(s > 0))]


def rad_turn_full_circle(item: dict) -> list[bool]:
    """q-turn: the circumference is how many radii? Options: π, 2π, 4, 6, π² times."""
    ratio = sp.simplify(2 * sp.pi * r_ / r_)
    return [sp.simplify(ratio - o) == 0 for o in (sp.pi, 2 * sp.pi, 4, 6, sp.pi ** 2)]


def rad_240_to_radians(item: dict) -> list[bool]:
    """q1: 240° in radians. Options: 2π/3, 4π/3, 3π/4, 5π/3, 4π/9."""
    t = _deg_to_rad(240)
    p = sp.pi
    return [sp.simplify(t - o) == 0 for o in (2 * p / 3, 4 * p / 3, 3 * p / 4, 5 * p / 3, 4 * p / 9)]


def rad_7pi_10_to_degrees(item: dict) -> sp.Integer:
    """q2: 7π/10 radians in degrees."""
    d = _rad_to_deg(7 * sp.pi / 10)
    assert d.is_integer
    return sp.Integer(d)


def rad_statements(item: dict) -> list[bool]:
    """q3: (1) 1 radian > 60°; (2) π/2 radians = 90°; (3) 5 radians ends in quadrant IV;
    (4) −π/3 and 5π/3 are coterminal; (5) with a larger radius, a central angle of 1 radian is larger
    (checked as: the degree size of 1 radian depends on the radius, which it does not)."""
    one = _rad_to_deg(1)
    # coterminal: same point on the unit circle
    a, b = -sp.pi / 3, 5 * sp.pi / 3
    coterminal = sp.simplify(sp.cos(a) - sp.cos(b)) == 0 and sp.simplify(sp.sin(a) - sp.sin(b)) == 0
    # the central angle (in degrees) whose arc equals the radius, on circles of two different radii:
    # that arc is the fraction r / (2*pi*r) of the circumference, so that fraction of 360 degrees
    def _deg_of_arc_equal_radius(r):
        r = sp.Integer(r)
        return sp.simplify(r / (2 * sp.pi * r) * 360)

    angle_r1 = _deg_of_arc_equal_radius(1)
    angle_r2 = _deg_of_arc_equal_radius(5)
    return [
        bool(one > 60),
        sp.simplify(_rad_to_deg(sp.pi / 2) - 90) == 0,
        _quadrant_of_rad(sp.Integer(5)) == 4,
        coterminal,
        bool(angle_r2 > angle_r1),
    ]


def rad_sector_r8(item: dict) -> tuple[int, int]:
    """q4: radius 8, central angle 3π/4: arc = ①π, area = ②③π. Returns the coefficients of π."""
    s = _arc(8, 3 * sp.pi / 4)
    A = _sector_area(8, 3 * sp.pi / 4)
    cs, cA = sp.simplify(s / sp.pi), sp.simplify(A / sp.pi)
    assert cs.is_integer and cA.is_integer
    return (int(cs), int(cA))


def rad_sector_from_arc_area(item: dict) -> tuple[int, int]:
    """q5: arc 10 and area 25: radius ① and central angle ② radians. Solved as a system in (r, θ)."""
    r, t = sp.symbols("r t", positive=True)
    sols = sp.solve([sp.Eq(_arc(r, t), 10), sp.Eq(_sector_area(r, t), 25)], [r, t], dict=True)
    (sol,) = sols
    return (int(sol[r]), int(sol[t]))


def rad_max_sector_perimeter16(item: dict) -> tuple[int, int]:
    """q6: sector with perimeter 2r + s = 16: the largest area ①② and the central angle ③ (radians)
    at which it occurs. Area as a function of r on 0 < r < 8, maximised by calculus on the closed form."""
    r = sp.Symbol("r", positive=True)
    s = 16 - 2 * r
    theta = s / r
    A = sp.simplify(_sector_area(r, theta))
    # a real sector needs 0 < s <= 2*pi*r (the arc fits on the circle): 16/(2+2*pi) <= r < 8
    r_min = sp.Integer(16) / (2 + 2 * sp.pi)
    crit = [c for c in sp.solve(sp.diff(A, r), r) if bool(c >= r_min) and bool(c < 8)]
    (rc,) = crit
    assert sp.diff(A, r, 2).subs(r, rc) < 0
    return (int(A.subs(r, rc)), int(theta.subs(r, rc)))


def rad_minute_hand(item: dict) -> list[bool]:
    """q7: a 12 cm minute hand turns for 20 minutes: distance travelled by the tip.
    Options: 4π, 6π, 8π, 12π, 1440 (cm; the last is r × 120, degrees misused)."""
    theta = sp.Rational(20, 60) * 2 * sp.pi  # one hour = one full turn
    s = _arc(12, theta)
    p = sp.pi
    return [sp.simplify(s - o) == 0 for o in (4 * p, 6 * p, 8 * p, 12 * p, 1440)]
