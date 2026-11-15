"""Checks for src/data/items/math/s116-mock-b.yaml (116 sprint, 數B original practice paper).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

from itertools import combinations

import sympy as sp

M = sp.Matrix
x = sp.Symbol("x", real=True)


# ---------- opening dialogue ----------

def mb_turn_multi_score(item: dict) -> list[bool]:
    """q-turn: a 5-option 多選 item with k = 2 options judged wrong earns (n − 2k)/n of its points (0 if negative).
    Options: 3/5, 1/5, 2/5, 1/2, 0."""
    n, k = 5, 2
    share = sp.Max(sp.Rational(n - 2 * k, n), 0)
    return [share == v for v in (sp.Rational(3, 5), sp.Rational(1, 5), sp.Rational(2, 5), sp.Rational(1, 2), 0)]


# ---------- 單選 1–7 ----------

def mb_digits_12_pow_15(item: dict) -> list[bool]:
    """q1: how many digits does 12^15 have? Options: 15, 16, 17, 18, 20.
    Counted exactly from the integer (log 12^15 = 15(2 log 2 + log 3) ≈ 16.19 is how a student finds it)."""
    digits = len(str(sp.Integer(12) ** 15))
    # the explanation's table-value estimate must land in the same decade
    est = 15 * (2 * sp.Rational("0.3010") + sp.Rational("0.4771"))
    assert sp.floor(est) + 1 == digits
    return [digits == v for v in (15, 16, 17, 18, 20)]


def mb_largest_angle(item: dict) -> list[bool]:
    """q2: a triangle with sides 7, 8, 13; its largest angle (opposite 13) by the law of cosines.
    Options: 90°, 105°, 120°, 135°, 150°."""
    a, b, c = 13, 8, 7
    cos_A = sp.Rational(b**2 + c**2 - a**2, 2 * b * c)
    angle = sp.acos(cos_A)
    return [sp.simplify(angle - sp.rad(d)) == 0 for d in (90, 105, 120, 135, 150)]


def mb_cubic_inequality(item: dict) -> list[bool]:
    """q3: solve (x + 3)(x − 1)(x − 4) ≤ 0.
    Options: −3≤x≤1 or x≥4; x≤−3 or 1≤x≤4; −3≤x≤4; x≤−3 or x≥4; 1≤x≤4."""
    sol = sp.solveset((x + 3) * (x - 1) * (x - 4) <= 0, x, domain=sp.S.Reals)
    I, oo = sp.Interval, sp.oo
    options = [
        sp.Union(I(-3, 1), I(4, oo)),
        sp.Union(I(-oo, -3), I(1, 4)),
        I(-3, 4),
        sp.Union(I(-oo, -3), I(4, oo)),
        I(1, 4),
    ]
    return [sol == o for o in options]


def mb_conic_type(item: dict) -> list[bool]:
    """q4: generators at 40° to the axis; a plane not through the apex at 25° to the axis.
    For such a plane the section's eccentricity is e = cos(plane–axis angle) / cos(generator–axis angle):
    e = 0 circle (plane ⊥ axis), 0 < e < 1 ellipse, e = 1 parabola, e > 1 hyperbola.
    Options: circle, ellipse (not a circle), parabola, hyperbola, two crossing lines (needs the apex)."""
    e = sp.cos(sp.rad(25)) / sp.cos(sp.rad(40))
    through_apex = False
    return [
        sp.simplify(e) == 0,
        bool(e > 0) and bool(e < 1),
        sp.simplify(e - 1) == 0,
        bool(e > 1),
        through_apex,
    ]


def mb_even_sum_probability(item: dict) -> list[bool]:
    """q5: two different numbers drawn from 1–9; probability that their sum is even.
    Options: 1/2, 4/9, 5/9, 5/18, 2/9."""
    pairs = list(combinations(range(1, 10), 2))
    p = sp.Rational(sum(1 for a, b in pairs if (a + b) % 2 == 0), len(pairs))
    return [p == v for v in (sp.Rational(1, 2), sp.Rational(4, 9), sp.Rational(5, 9), sp.Rational(5, 18), sp.Rational(2, 9))]


def mb_sine_period_max(item: dict) -> list[bool]:
    """q6: y = 2 sin(πx/3) + 1: period and maximum.
    Options: (6, 3), (6, 2), (3, 3), (π/3, 3), (2π, 1)."""
    f = 2 * sp.sin(sp.pi * x / 3) + 1
    period = sp.periodicity(f, x)
    top = sp.maximum(f, x, sp.Interval(0, period))
    options = [(6, 3), (6, 2), (3, 3), (sp.pi / 3, 3), (2 * sp.pi, 1)]
    return [sp.simplify(period - p) == 0 and sp.simplify(top - m) == 0 for p, m in options]


def mb_map_area(item: dict) -> list[bool]:
    """q7: on a 1:25000 map a rectangle measures 3 cm × 8 cm; its real area in km².
    Options: 0.15, 1.5, 15, 150, 0.6."""
    cm_per_km = 100 * 1000
    w = sp.Rational(3 * 25000, cm_per_km)
    h = sp.Rational(8 * 25000, cm_per_km)
    area = w * h
    return [area == sp.Rational(v) for v in ("0.15", "1.5", "15", "150", "0.6")]


# ---------- 多選 8–12 ----------

def mb_matrix_statements(item: dict) -> list[bool]:
    """q8: A = [[3,1],[1,2]], B = [[1,0],[−1,2]].
    Options: AB = [[2,2],[−1,4]]; AB = BA; A has an inverse; A⁻¹ = [[2,−1],[−1,3]]; A(1,1)ᵀ = (4,3)ᵀ."""
    A = M([[3, 1], [1, 2]])
    B = M([[1, 0], [-1, 2]])
    return [
        A * B == M([[2, 2], [-1, 4]]),
        A * B == B * A,
        A.det() != 0,
        A.det() != 0 and A.inv() == M([[2, -1], [-1, 3]]),
        A * M([1, 1]) == M([4, 3]),
    ]


def _sd(data: list) -> sp.Expr:
    n = len(data)
    mu = sp.Rational(sum(data), n)
    return sp.sqrt(sp.Rational(sum((d - mu) ** 2 for d in data), n))


def _corr(u: list, v: list) -> sp.Expr:
    n = len(u)
    mu, mv = sp.Rational(sum(u), n), sp.Rational(sum(v), n)
    num = sum((a - mu) * (b - mv) for a, b in zip(u, v))
    den = sp.sqrt(sum((a - mu) ** 2 for a in u) * sum((b - mv) ** 2 for b in v))
    return sp.simplify(num / den)


def mb_data_transform(item: dict) -> list[bool]:
    """q9: x = 2, 4, 6, 8, 10 and y = 3x − 1; z = 10 − x.
    Options: mean of y is 17; SD(y) = 3 SD(x); SD(y) = 3 SD(x) − 1; r(x, y) = 1; r(x, z) = 1.
    (The SD ratios hold whether one divides by n or n − 1; _sd divides by n.)"""
    xs = [2, 4, 6, 8, 10]
    ys = [3 * v - 1 for v in xs]
    zs = [10 - v for v in xs]
    return [
        sp.Rational(sum(ys), len(ys)) == 17,
        sp.simplify(_sd(ys) - 3 * _sd(xs)) == 0,
        sp.simplify(_sd(ys) - (3 * _sd(xs) - 1)) == 0,
        _corr(xs, ys) == 1,
        _corr(xs, zs) == 1,
    ]


def mb_vector_statements(item: dict) -> list[bool]:
    """q10: a = (4,3), b = (3,−4), c = (1,7).
    Options: a ⊥ b; a ∥ (−8,−6); the angle between a and c is 45°; the projection of c on a is (3,−4); |a + b| = 10."""
    a, b, c = M([4, 3]), M([3, -4]), M([1, 7])
    w = M([-8, -6])
    cos_ac = a.dot(c) / (a.norm() * c.norm())
    proj = (a.dot(c) / a.dot(a)) * a
    return [
        a.dot(b) == 0,
        a[0] * w[1] - a[1] * w[0] == 0,
        sp.simplify(sp.acos(cos_ac) - sp.pi / 4) == 0,
        proj == M([3, -4]),
        sp.simplify((a + b).norm() - 10) == 0,
    ]


def mb_independent_events(item: dict) -> list[bool]:
    """q11: P(A) = 0.4, P(B) = 0.5, P(A∩B) = 0.2.
    Options: A, B independent; P(B|A) = 0.5; P(A∪B) = 0.7; A, B mutually exclusive; P(A′∩B′) = 0.3."""
    pa, pb, pab = sp.Rational(2, 5), sp.Rational(1, 2), sp.Rational(1, 5)
    union = pa + pb - pab
    return [
        pab == pa * pb,
        pab / pa == sp.Rational(1, 2),
        union == sp.Rational(7, 10),
        pab == 0,
        1 - union == sp.Rational(3, 10),
    ]


def mb_circle_line(item: dict) -> list[bool]:
    """q12: C: (x − 1)² + (y + 2)² = 13 (centre (1,−2), radius √13).
    Options: (3,1) is on C; the tangent at (3,1) is 2x + 3y = 9; x = 4 is tangent to C;
    3x − 2y = 0 meets C at two points; the origin is inside C."""
    y = sp.Symbol("y", real=True)
    h, k, r = 1, -2, sp.sqrt(13)
    F = (x - h) ** 2 + (y - k) ** 2 - r**2

    def dist(A, B, Cc):
        return sp.Abs(A * h + B * k + Cc) / sp.sqrt(A**2 + B**2)

    on_c = F.subs({x: 3, y: 1}) == 0
    # 2x + 3y = 9 is the tangent at P(3,1) when P is on both the circle and the line,
    # and the line is at distance r from the centre (so it meets C only at P)
    p_on_line = 2 * 3 + 3 * 1 == 9
    return [
        on_c,
        bool(on_c and p_on_line and sp.simplify(dist(2, 3, -9) - r) == 0),
        sp.simplify(dist(1, 0, -4) - r) == 0,
        bool(dist(3, -2, 0) < r),
        bool(F.subs({x: 0, y: 0}) < 0),
    ]


# ---------- 選填 13–17 ----------

def mb_recursive_sum(item: dict) -> sp.Integer:
    """q13: a₁ = 2, aₙ₊₁ = 2aₙ − 1; the sum of the first 6 terms."""
    terms = [sp.Integer(2)]
    while len(terms) < 6:
        terms.append(2 * terms[-1] - 1)
    return sp.Integer(sum(terms))


def mb_remainder(item: dict) -> tuple[int, int]:
    """q14: f(x) ÷ (x − 1) leaves 3 and f(x) ÷ (x + 2) leaves −9; the remainder of f(x) ÷ (x − 1)(x + 2) is ax + b.
    By the remainder theorem a + b = 3 and −2a + b = −9; then a sample f confirms both remainders."""
    a, b = sp.symbols("a b")
    sol = sp.solve([sp.Eq(a + b, 3), sp.Eq(-2 * a + b, -9)], [a, b])
    f = (x - 1) * (x + 2) * (x**2 + 5) + sol[a] * x + sol[b]
    assert sp.rem(f, x - 1) == 3 and sp.rem(f, x + 2) == -9
    return (int(sol[a]), int(sol[b]))


def mb_sector_area(item: dict) -> sp.Integer:
    """q15: a sector of radius 9 with central angle 2π/3 has area kπ; k = (½ r² θ)/π."""
    r, theta = 9, 2 * sp.pi / 3
    return sp.Integer(sp.simplify(sp.Rational(1, 2) * r**2 * theta / sp.pi))


def mb_decay_hours(item: dict) -> sp.Integer:
    """q16: 10% of the drug is cleared each hour; the fewest whole hours until under 10% remains.
    Exact: the least n with (9/10)^n < 1/10."""
    n = 0
    while not sp.Rational(9, 10) ** n < sp.Rational(1, 10):
        n += 1
    return sp.Integer(n)


def mb_distance_to_x_axis(item: dict) -> sp.Integer:
    """q17: P(2, −6, 9); its distance d to the x-axis is the distance to its projection (2, 0, 0); d²."""
    P = M([2, -6, 9])
    foot = M([P[0], 0, 0])
    return sp.Integer((P - foot).dot(P - foot))


# ---------- 混合題組 18–20 ----------

_PROFIT = (x - 10) * (200 - 4 * x)


def mb_profit_expression(item: dict) -> list[bool]:
    """q18: price x dollars, 200 − 4x cups a day, cost 10 dollars a cup; the daily profit.
    Options: (x−10)(200−4x); x(200−4x) − 10; (x+10)(200−4x); x(200−4x); (x−10)(200−x)."""
    options = [
        (x - 10) * (200 - 4 * x),
        x * (200 - 4 * x) - 10,
        (x + 10) * (200 - 4 * x),
        x * (200 - 4 * x),
        (x - 10) * (200 - x),
    ]
    return [sp.expand(o - _PROFIT) == 0 for o in options]


def mb_profit_max(item: dict) -> bool:
    """q19: completing the square P(x) = −4(x − 30)² + 1600 on 10 ≤ x ≤ 50, so the maximum is 1600 at x = 30."""
    square_form = sp.expand(_PROFIT - (-4 * (x - 30) ** 2 + 1600)) == 0
    top = sp.maximum(_PROFIT, x, sp.Interval(10, 50))
    at_30 = _PROFIT.subs(x, 30)
    return bool(square_form and top == 1600 and at_30 == 1600)


def mb_profit_max_restricted(item: dict) -> bool:
    """q20: on 35 ≤ x ≤ 45 the vertex x = 30 is outside, P is decreasing there, so the maximum is P(35) = 1500
    (25 dollars profit a cup × 60 cups)."""
    dom = sp.Interval(35, 45)
    top = sp.maximum(_PROFIT, x, dom)
    decreasing = sp.is_strictly_decreasing(_PROFIT, dom)
    return bool(top == 1500 and _PROFIT.subs(x, 35) == 1500 and decreasing and (35 - 10) * (200 - 4 * 35) == 1500)
