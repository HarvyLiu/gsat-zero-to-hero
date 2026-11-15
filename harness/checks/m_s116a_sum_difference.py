"""Checks for src/data/items/math/s116a-sum-difference.yaml (116 sprint, 數A: sum and difference formulas, combining sine and cosine).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
A value found with a formula (sum, difference, double or half angle; r sin(x + φ)) is cross-checked
against an independent route: SymPy's own exact value of the angle, a point on the unit circle, or
the argument of a product of complex numbers. Angles are exact: degrees are converted with sp.pi / 180.
"""

from __future__ import annotations

import sympy as sp

DEG = sp.pi / 180
x = sp.symbols("x", real=True)


def _same(a, b) -> bool:
    return sp.simplify(sp.nsimplify(a) - sp.nsimplify(b)) == 0


def _acute_from_sin(s) -> sp.Expr:
    """An acute angle with the given sine (in radians)."""
    t = sp.asin(s)
    assert 0 < t < sp.pi / 2
    return t


def _combine(a, b):
    """a sin x + b cos x = r sin(x + φ): (r, φ) with r > 0, cos φ = a/r, sin φ = b/r; the identity is checked."""
    r = sp.sqrt(a**2 + b**2)
    phi = sp.atan2(b, a)
    assert sp.simplify(sp.expand_trig(r * sp.sin(x + phi)) - (a * sp.sin(x) + b * sp.cos(x))) == 0
    return sp.simplify(r), phi


def _extremes(expr) -> tuple[sp.Expr, sp.Expr]:
    """Max and min of a periodic expression in x over one period [0, 2π], from its critical points."""
    crit = sp.solveset(sp.diff(expr, x), x, sp.Interval(0, 2 * sp.pi))
    vals = [sp.simplify(expr.subs(x, c)) for c in crit] + [sp.simplify(expr.subs(x, 0))]
    return sp.Max(*vals), sp.Min(*vals)


def sd_turn_not_additive(item: dict) -> list[bool]:
    """q-turn: which option equals sin(30° + 60°)? Options sin30° + sin60°, 1, (1 + √3)/2, √3/2, 1/2."""
    target = sp.sin(90 * DEG)
    options = [sp.sin(30 * DEG) + sp.sin(60 * DEG), sp.Integer(1), (1 + sp.sqrt(3)) / 2, sp.sqrt(3) / 2, sp.Rational(1, 2)]
    return [_same(target, o) for o in options]


def sd_cos105(item: dict) -> list[bool]:
    """q1: cos 105° by cos(60° + 45°), cross-checked with SymPy's exact cos(7π/12).
    Options (√6+√2)/4, (√6−√2)/4, (√2−√6)/4, −(√6+√2)/4, (√2+√3)/2."""
    a, b = 60 * DEG, 45 * DEG
    by_formula = sp.cos(a) * sp.cos(b) - sp.sin(a) * sp.sin(b)
    assert _same(by_formula, sp.cos(105 * DEG))
    s2, s6 = sp.sqrt(2), sp.sqrt(6)
    options = [(s6 + s2) / 4, (s6 - s2) / 4, (s2 - s6) / 4, -(s6 + s2) / 4, (s2 + sp.sqrt(3)) / 2]
    return [_same(by_formula, o) for o in options]


def sd_cos_difference(item: dict) -> tuple[int, int]:
    """q2: α, β acute, sin α = 8/17, cos β = 4/5: cos(α − β) as p/q → (p, q).
    Formula value cross-checked with the cosine of the actual angle difference."""
    alpha = _acute_from_sin(sp.Rational(8, 17))
    beta = sp.acos(sp.Rational(4, 5))
    ca, sa = sp.sqrt(1 - sp.Rational(8, 17) ** 2), sp.Rational(8, 17)
    cb, sb = sp.Rational(4, 5), sp.sqrt(1 - sp.Rational(4, 5) ** 2)
    by_formula = sp.nsimplify(ca * cb + sa * sb)
    assert sp.simplify(sp.expand_trig(sp.cos(alpha - beta)) - by_formula) == 0
    v = sp.Rational(by_formula)
    return (int(v.p), int(v.q))


def sd_cos_double(item: dict) -> tuple[int, int]:
    """q3: cos θ = 1/3: cos 2θ = 2cos²θ − 1 as p/q → (p, q); cross-checked with cos(2·acos(1/3))."""
    c = sp.Rational(1, 3)
    by_formula = 2 * c**2 - 1
    assert sp.simplify(sp.expand_trig(sp.cos(2 * sp.acos(c))) - by_formula) == 0
    v = sp.Rational(by_formula)
    return (int(v.p), int(v.q))


def sd_half_angle_sign(item: dict) -> list[bool]:
    """q4: 270° < θ < 360°, cos θ = 1/8: cos(θ/2). Options 3/4, −3/4, 9/16, −9/16, √7/4.
    The half angle lies in (135°, 180°), so the negative root; cross-checked by building θ itself."""
    c = sp.Rational(1, 8)
    root = sp.sqrt((1 + c) / 2)
    theta = 2 * sp.pi - sp.acos(c)  # the angle in (270°, 360°) with cosine 1/8
    assert 270 * DEG < theta < 360 * DEG and _same(sp.cos(theta), c)
    half = theta / 2
    assert 135 * DEG < half < 180 * DEG
    value = -root  # cosine is negative in the second quadrant
    # SymPy leaves cos(acos(1/8)/2) unevaluated, so: the double angle formula undoes the half angle,
    # and the actual cosine of the actual half angle agrees to 50 digits (this fixes the sign).
    assert 2 * value**2 - 1 == c
    assert abs(sp.N(sp.cos(half) - value, 50)) < sp.Float("1e-45")
    options = [sp.Rational(3, 4), sp.Rational(-3, 4), sp.Rational(9, 16), sp.Rational(-9, 16), sp.sqrt(7) / 4]
    return [_same(value, o) for o in options]


def sd_combine_statements(item: dict) -> list[bool]:
    """q5: f(x) = √3 sin x − cos x. Statements: max is 2; max is √3 + 1; the period is 2π;
    f(x) = 2 sin(x − π/6); f(0) = 1."""
    f = sp.sqrt(3) * sp.sin(x) - sp.cos(x)
    r, phi = _combine(sp.sqrt(3), -1)
    hi, _lo = _extremes(f)
    assert _same(hi, r)
    periodic_2pi = sp.simplify(f.subs(x, x + 2 * sp.pi) - f) == 0
    # no shorter period: any period p must satisfy f(p) = f(0) and f'(p) = f'(0); none in (0, 2π) does
    shorter = [p for p in sp.solveset(sp.Eq(f, f.subs(x, 0)), x, sp.Interval.open(0, 2 * sp.pi))
               if sp.simplify(sp.diff(f, x).subs(x, p) - sp.diff(f, x).subs(x, 0)) == 0]
    return [
        _same(hi, 2),
        _same(hi, sp.sqrt(3) + 1),
        periodic_2pi and not shorter,
        sp.simplify(sp.expand_trig(2 * sp.sin(x - sp.pi / 6)) - f) == 0 and _same(phi, -sp.pi / 6),
        _same(f.subs(x, 0), 1),
    ]


def sd_max_min_shifted(item: dict) -> tuple[int, int]:
    """q6: y = 5 sin x + 12 cos x + 1: (max, min), from r = √(5² + 12²) and from the critical points."""
    r, _ = _combine(5, 12)
    expr = 5 * sp.sin(x) + 12 * sp.cos(x) + 1
    hi, lo = _extremes(expr)
    assert _same(hi, r + 1) and _same(lo, -r + 1)
    return (int(hi), int(lo))


def sd_same_frequency_waves(item: dict) -> list[bool]:
    """q7: y = 3 sin t + 3√3 cos t. Options: amplitude 3 + 3√3; amplitude 6 and period 2π;
    amplitude 6 and period 4π; amplitude 6 and period π; amplitude √3 and period 2π."""
    r, phi = _combine(3, 3 * sp.sqrt(3))
    assert _same(phi, sp.pi / 3)
    amp = r
    hi, lo = _extremes(3 * sp.sin(x) + 3 * sp.sqrt(3) * sp.cos(x))
    assert _same((hi - lo) / 2, amp)
    y = 3 * sp.sin(x) + 3 * sp.sqrt(3) * sp.cos(x)
    # smallest positive period: 2π is a period, and no p in (0, 2π) has y(p) = y(0) and y'(p) = y'(0)
    assert sp.simplify(y.subs(x, x + 2 * sp.pi) - y) == 0
    shorter = [p for p in sp.solveset(sp.Eq(y, y.subs(x, 0)), x, sp.Interval.open(0, 2 * sp.pi))
               if sp.simplify(sp.diff(y, x).subs(x, p) - sp.diff(y, x).subs(x, 0)) == 0]
    assert not shorter
    period = 2 * sp.pi
    return [
        _same(amp, 3 + 3 * sp.sqrt(3)),
        _same(amp, 6) and period == 2 * sp.pi,
        _same(amp, 6) and period == 4 * sp.pi,
        _same(amp, 6) and period == sp.pi,
        _same(amp, sp.sqrt(3)) and period == 2 * sp.pi,
    ]


def sd_tan_sum_angle(item: dict) -> sp.Integer:
    """q8: α, β acute, tan α = 2, tan β = 3: α + β in degrees.
    tan(α + β) = (2 + 3)/(1 − 6) = −1 and both angles exceed 45°, so α + β = 135°; cross-checked with
    the argument of (1 + 2i)(1 + 3i), whose argument is α + β."""
    ta, tb = sp.Integer(2), sp.Integer(3)
    tan_sum = (ta + tb) / (1 - ta * tb)
    assert tan_sum == -1
    by_complex = sp.arg(sp.expand((1 + 2 * sp.I) * (1 + 3 * sp.I)))
    assert sp.simplify(by_complex - (sp.atan(2) + sp.atan(3))) == 0 or abs(float(by_complex - sp.atan(2) - sp.atan(3))) < 1e-15
    deg = sp.simplify(by_complex / DEG)
    assert sp.simplify(sp.tan(deg * DEG) - tan_sum) == 0
    return sp.Integer(deg)
