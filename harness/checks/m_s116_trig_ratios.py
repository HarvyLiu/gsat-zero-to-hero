"""Checks for src/data/items/math/s116-trig-ratios.yaml (116 sprint: trigonometric ratios).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Angles are given in degrees in the items and converted with deg() so SymPy evaluates special angles exactly.
Right-triangle ratios are recomputed from coordinates (angle at a vertex via dot and cross products), not
from the SOH-CAH-TOA rule the item tests, so a wrong key cannot pass by repeating the same slip.
"""

from __future__ import annotations

import sympy as sp

s, c = sp.symbols("s c", real=True)


def deg(d) -> sp.Expr:
    return sp.pi * sp.Rational(d) / 180


def _angle_trig(vertex, p, q):
    """(sin, cos) of the angle at `vertex` between rays to p and q, from vectors."""
    u = sp.Matrix([p[0] - vertex[0], p[1] - vertex[1]])
    v = sp.Matrix([q[0] - vertex[0], q[1] - vertex[1]])
    norm = sp.sqrt(u.dot(u)) * sp.sqrt(v.dot(v))
    cross = sp.Abs(u[0] * v[1] - u[1] * v[0])
    return sp.simplify(cross / norm), sp.simplify(u.dot(v) / norm)


def _right_triangle(ac, bc):
    """Right angle at C = (0, 0), A on the x-axis, B on the y-axis."""
    return (sp.Integer(ac), 0), (0, sp.Integer(bc)), (0, 0)


def _as_pair(r: sp.Rational) -> tuple[int, int]:
    r = sp.Rational(r)
    return (int(r.p), int(r.q))


def tr_turn_sin_a(item: dict) -> list[bool]:
    """q-turn: ∠C = 90°, BC = 3, AC = 4; sin A against 3/5, 4/5, 3/4, 4/3, 5/3."""
    A, B, C = _right_triangle(4, 3)
    sin_a, _ = _angle_trig(A, B, C)
    options = [sp.Rational(3, 5), sp.Rational(4, 5), sp.Rational(3, 4), sp.Rational(4, 3), sp.Rational(5, 3)]
    return [sp.simplify(sin_a - o) == 0 for o in options]


def tr_tan_from_sides(item: dict) -> tuple[int, int]:
    """q1: ∠C = 90°, AB = 25, AC = 24; tan A = a/b in lowest terms → (a, b).
    BC is found from AB² = AC² + BC² (positive root), then tan A = sin A / cos A from the vectors."""
    bc = sp.Symbol("bc", positive=True)
    (bc_val,) = sp.solve(sp.Eq(24**2 + bc**2, 25**2), bc)
    A, B, C = _right_triangle(24, bc_val)
    sin_a, cos_a = _angle_trig(A, B, C)
    return _as_pair(sp.nsimplify(sin_a / cos_a))


def tr_measure_estimate(item: dict) -> list[bool]:
    """q2: a right triangle drawn with a 40° angle, hypotenuse measured 10.0 cm, opposite side 6.4 cm.
    The estimate of sin 40° is opposite / hypotenuse; the key is the option nearest to it, and it must also be
    the option nearest the true sin 40° (so the measurement and the exact value agree on the answer)."""
    options = [sp.Rational(40, 100), sp.Rational(64, 100), sp.Rational(77, 100), sp.Rational(84, 100), sp.Rational(156, 100)]
    measured = sp.Rational(64, 10) / 10
    true = sp.N(sp.sin(deg(40)), 30)
    near_m = min(range(len(options)), key=lambda i: abs(options[i] - measured))
    near_t = min(range(len(options)), key=lambda i: abs(options[i] - true))
    assert near_m == near_t, (near_m, near_t)
    return [i == near_m for i in range(len(options))]


def tr_terminal_point_sin(item: dict) -> list[bool]:
    """q3: P(5, −12) is on the terminal side of θ; sin θ = y / r against 5/13, −5/13, 12/13, −12/13, −12/5.
    Cross-checked against sin(atan2(y, x)), which places θ in the right quadrant by itself."""
    x, y = sp.Integer(5), sp.Integer(-12)
    r = sp.sqrt(x**2 + y**2)
    value = y / r
    assert sp.simplify(sp.sin(sp.atan2(y, x)) - value) == 0
    options = [sp.Rational(5, 13), sp.Rational(-5, 13), sp.Rational(12, 13), sp.Rational(-12, 13), sp.Rational(-12, 5)]
    return [sp.simplify(value - o) == 0 for o in options]


def tr_which_negative(item: dict) -> list[bool]:
    """q4: which of sin 200°, cos 300°, tan 135°, sin(−60°), cos 100° are negative (exact or 30-digit numeric sign)."""
    values = [sp.sin(deg(200)), sp.cos(deg(300)), sp.tan(deg(135)), sp.sin(deg(-60)), sp.cos(deg(100))]
    out = []
    for v in values:
        neg = v.is_negative
        if neg is None:
            neg = bool(sp.N(v, 30) < 0)
        out.append(bool(neg))
    return out


def tr_special_sum(item: dict) -> sp.Integer:
    """q5: cos 120° + sin 330°."""
    return sp.Integer(sp.simplify(sp.cos(deg(120)) + sp.sin(deg(330))))


def tr_tan_from_cos_q4(item: dict) -> tuple[int, int]:
    """q6: 270° < θ < 360° and cos θ = 3/4; tan θ = −√a / b with a square-free → (a, b).
    sin θ is solved from sin² + cos² = 1 and the quadrant (sin θ < 0 in quadrant IV)."""
    cos_t = sp.Rational(3, 4)
    roots = [r for r in sp.solve(sp.Eq(s**2 + cos_t**2, 1), s) if r.is_negative]
    (sin_t,) = roots
    tan_t = sp.radsimp(sin_t / cos_t)
    num, den = sp.fraction(sp.radsimp(-tan_t))
    a = sp.Integer(num**2)
    assert sp.sqrt(a) == num and a.is_integer and all(e == 1 for e in sp.factorint(a).values())
    assert sp.simplify(-sp.sqrt(a) / den - tan_t) == 0
    # Independent cross-check: θ = 360° − arccos(3/4) is the quadrant-IV angle with this cosine.
    theta = 2 * sp.pi - sp.acos(cos_t)
    assert sp.simplify(sp.tan(theta) - tan_t) == 0
    return (int(a), int(den))


def tr_sin_cos_product(item: dict) -> tuple[int, int]:
    """q7: sin θ + cos θ = 1/3; sin θ cos θ = p/q in lowest terms, q > 0 → (p, q).
    Solves the system s + c = 1/3, s² + c² = 1 directly; every real solution must give the same product."""
    sols = sp.solve([sp.Eq(s + c, sp.Rational(1, 3)), sp.Eq(s**2 + c**2, 1)], [s, c], dict=True)
    real = [d for d in sols if d[s].is_real and d[c].is_real]
    assert real
    products = {sp.nsimplify(sp.simplify(d[s] * d[c])) for d in real}
    (product,) = products
    return _as_pair(product)


def tr_cofunction_product(item: dict) -> list[bool]:
    """q8: tan 25° · tan 65° against 1/2, √3/3, 1, √3, 2.
    Symbolically tan t · tan(90° − t) = 1 for acute t; also checked numerically to 40 digits."""
    t = sp.Symbol("t", positive=True)
    assert sp.simplify(sp.tan(t) * sp.tan(sp.pi / 2 - t) - 1) == 0
    value = sp.tan(deg(25)) * sp.tan(deg(65))
    exact = sp.Integer(1)
    assert abs(sp.N(value - exact, 40)) < sp.Float("1e-35")
    options = [sp.Rational(1, 2), sp.sqrt(3) / 3, sp.Integer(1), sp.sqrt(3), sp.Integer(2)]
    return [sp.simplify(exact - o) == 0 for o in options]
