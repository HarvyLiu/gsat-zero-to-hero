"""Checks for src/data/items/math/s116-angles-polar.yaml (116 sprint: generalized angles and polar coordinates, G-10-5).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Angles are in degrees; every trig value is exact (sp.cos / sp.sin of a rational multiple of pi).
"""

from __future__ import annotations

import sympy as sp


def _rad(deg) -> sp.Expr:
    return sp.Rational(deg) * sp.pi / 180


def _terminal_point(deg) -> tuple[sp.Expr, sp.Expr]:
    """The point at distance 1 on the terminal side of an angle in standard position."""
    t = _rad(deg)
    return sp.cos(t), sp.sin(t)


def _quadrant(deg) -> int:
    """1–4 for the quadrant of the terminal side, 0 when it lies on an axis (decided by signs, not by ranges)."""
    cx, cy = (sp.nsimplify(v) for v in _terminal_point(deg))
    if cx == 0 or cy == 0:
        return 0
    return {(True, True): 1, (False, True): 2, (False, False): 3, (True, False): 4}[(bool(cx > 0), bool(cy > 0))]


def _coterminal(a, b) -> bool:
    """Same terminal side: the unit points on both terminal sides coincide."""
    pa, pb = _terminal_point(a), _terminal_point(b)
    return all(sp.simplify(u - v) == 0 for u, v in zip(pa, pb))


def _polar_to_rect(r, deg) -> tuple[sp.Expr, sp.Expr]:
    t = _rad(deg)
    return sp.simplify(r * sp.cos(t)), sp.simplify(r * sp.sin(t))


def _same_point(p, q) -> bool:
    return all(sp.simplify(sp.sympify(u) - sp.sympify(v)) == 0 for u, v in zip(p, q))


def _inclination(slope) -> sp.Expr:
    """Angle of inclination in degrees, 0 ≤ θ < 180, from the direction (1, slope) via atan2."""
    deg = sp.atan2(slope, 1) * 180 / sp.pi
    deg = sp.nsimplify(sp.simplify(deg))
    return deg + 180 if deg < 0 else deg


def ap_turn_coterminal(item: dict) -> list[bool]:
    """q-turn: which angle has the same terminal side as −90°? Options: 90°, 180°, 270°, 360°, −270°."""
    return [_coterminal(-90, o) for o in (90, 180, 270, 360, -270)]


def ap_third_quadrant(item: dict) -> list[bool]:
    """q1: which angle in standard position has its terminal side in quadrant III?
    Options: 135°, −120°, 300°, −45°, 270°."""
    return [_quadrant(o) == 3 for o in (135, -120, 300, -45, 270)]


def ap_coterminal_statements(item: dict) -> list[bool]:
    """q2: (1) −60° and 300° coterminal; (2) −180° and 180° coterminal; (3) 120° and −120° coterminal;
    (4) −100° ends in quadrant III; (5) 90° ends in quadrant I."""
    return [
        _coterminal(-60, 300),
        _coterminal(-180, 180),
        _coterminal(120, -120),
        _quadrant(-100) == 3,
        _quadrant(90) == 1,
    ]


def ap_coterminal_0_360(item: dict) -> sp.Integer:
    """q3: the angle θ with 0° ≤ θ < 360° coterminal with −35° (search all whole degrees)."""
    (hit,) = [d for d in range(0, 360) if _coterminal(-35, d)]
    return sp.Integer(hit)


def ap_polar_to_rect(item: dict) -> list[bool]:
    """q4: rectangular coordinates of [6, 330°].
    Options: (3, −3√3), (−3√3, 3), (3√3, −3), (3√3, 3), (6, 330)."""
    p = _polar_to_rect(6, 330)
    s3 = sp.sqrt(3)
    opts = [(3, -3 * s3), (-3 * s3, 3), (3 * s3, -3), (3 * s3, 3), (6, 330)]
    return [_same_point(p, o) for o in opts]


def ap_rect_to_polar(item: dict) -> list[bool]:
    """q5: which is a polar coordinate of (−√3, −1)? Options read as [r, θ]:
    [2, 30°], [2, −150°], [2, −120°], [4, 210°], [210°, 2] (the last read literally: r = 210, θ = 2°)."""
    target = (-sp.sqrt(3), -1)
    opts = [(2, 30), (2, -150), (2, -120), (4, 210), (210, 2)]
    return [_same_point(_polar_to_rect(r, d), target) for r, d in opts]


def ap_polar_to_rect_fill(item: dict) -> tuple[int, int]:
    """q6: [4√2, 225°] = (a, b); the cells spell a then b."""
    a, b = _polar_to_rect(4 * sp.sqrt(2), 225)
    return (int(a), int(b))


def ap_inclination_of_line(item: dict) -> list[bool]:
    """q7: angle of inclination of x + √3 y + 1 = 0. Options: 30°, 60°, 120°, 150°, −30°."""
    x, y = sp.symbols("x y")
    e = x + sp.sqrt(3) * y + 1
    m = sp.simplify(-sp.diff(e, x) / sp.diff(e, y))
    th = _inclination(m)
    return [sp.simplify(th - o) == 0 for o in (30, 60, 120, 150, -30)]


def ap_inclination_statements(item: dict) -> list[bool]:
    """q8: L1, L2 have inclinations 45° and 135°.
    (1) slope of L1 is 1; (2) L1 ⊥ L2; (3) slope of L2 is positive;
    (4) a line with inclination 60° is steeper than L1; (5) a line with inclination 90° has slope 0.
    Slopes come from the direction (cos θ, sin θ), i.e. a point on the terminal side."""
    def slope(deg):
        cx, cy = _terminal_point(deg)
        return None if sp.simplify(cx) == 0 else sp.simplify(cy / cx)

    m1, m2, m60, m90 = slope(45), slope(135), slope(60), slope(90)
    return [
        m1 == 1,
        sp.simplify(m1 * m2) == -1,
        bool(m2 > 0),
        bool(sp.Abs(m60) > sp.Abs(m1)),
        m90 is not None and m90 == 0,
    ]
