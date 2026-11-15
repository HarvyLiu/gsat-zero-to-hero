"""Checks for math/s116-mock-a (original 數A practice paper, src/data/items/math/s116-mock-a.yaml).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import itertools

import sympy as sp

x, y, t = sp.symbols("x y t", real=True)
R = sp.Rational


def _vec(*c):
    return sp.Matrix(c)


# ---------- opening dialogue ----------

def ma_turn_pacing(item: dict) -> list[bool]:
    """q-turn: 100 minutes; 17 Part-1 items at 4 minutes each. Minutes left: 22, 28, 32, 36, 68."""
    left = 100 - 17 * 4
    return [left == o for o in (22, 28, 32, 36, 68)]


# ---------- 單選 1–6 ----------

def ma_digits_3_pow_40(item: dict) -> list[bool]:
    """q1: number of digits of 3^40 (options 18, 19, 20, 21, 40). Counted exactly, and cross-checked
    against the printed value log 3 ≈ 0.4771 (40 × 0.4771 = 19.084 → 20 digits)."""
    digits = len(str(3**40))
    assert sp.floor(40 * R(4771, 10000)) + 1 == digits
    return [digits == o for o in (18, 19, 20, 21, 40)]


def ma_triangle_area(item: dict) -> list[bool]:
    """q2: AB = 3, AC = 8, BC = 7. Area of △ABC. Options 12, 6√3, 12√3, 24, 3√3."""
    b, c, a = 8, 3, 7  # b = CA, c = AB, a = BC
    cos_a = R(b**2 + c**2 - a**2, 2 * b * c)
    sin_a = sp.sqrt(1 - cos_a**2)
    area = sp.Rational(1, 2) * b * c * sin_a
    # Heron as an independent check
    s = R(a + b + c, 2)
    assert sp.simplify(area - sp.sqrt(s * (s - a) * (s - b) * (s - c))) == 0
    options = [12, 6 * sp.sqrt(3), 12 * sp.sqrt(3), 24, 3 * sp.sqrt(3)]
    return [sp.simplify(area - o) == 0 for o in options]


def ma_cos_period_max(item: dict) -> list[bool]:
    """q3: f(x) = 2cos(3x) + 1: (period, maximum). Options (2π,3), (6π,3), (2π/3,2), (2π/3,3), (π/3,1)."""
    f = 2 * sp.cos(3 * x) + 1
    period = sp.periodicity(f, x)
    fmax = sp.maximum(f, x, sp.Interval(0, 2 * sp.pi))
    options = [(2 * sp.pi, 3), (6 * sp.pi, 3), (2 * sp.pi / 3, 2), (2 * sp.pi / 3, 3), (sp.pi / 3, 1)]
    return [sp.simplify(period - p) == 0 and sp.simplify(fmax - m) == 0 for p, m in options]


def ma_system_no_solution(item: dict) -> list[bool]:
    """q4: x + ay = 2, ax + 4y = 4. Which a gives no solution? Options −4, −2, 0, 2, 4."""
    out = []
    for a in (-4, -2, 0, 2, 4):
        sol = sp.linsolve([x + a * y - 2, a * x + 4 * y - 4], x, y)
        out.append(sol == sp.EmptySet)
    return out


def ma_dice_conditional(item: dict) -> list[bool]:
    """q5: two fair dice; given the sum is 8, P(at least one die shows 3). Options 1/18, 1/5, 11/36, 1/3, 2/5."""
    space = list(itertools.product(range(1, 7), repeat=2))
    given = [p for p in space if sum(p) == 8]
    both = [p for p in given if 3 in p]
    prob = R(len(both), len(given))
    return [prob == o for o in (R(1, 18), R(1, 5), R(11, 36), R(1, 3), R(2, 5))]


def ma_point_plane_distance(item: dict) -> list[bool]:
    """q6: distance from P(3, 1, 4) to the plane x − 2y + 2z = 4. Options 5/3, 5/9, 1, 3, 13/3.
    Computed as the distance from P to its foot on the plane (not with the distance formula)."""
    n = _vec(1, -2, 2)
    p = _vec(3, 1, 4)
    s = sp.Symbol("s")
    foot = p + s * n
    s0 = sp.solve(foot[0] - 2 * foot[1] + 2 * foot[2] - 4, s)[0]
    d = (p - foot.subs(s, s0)).norm()
    return [sp.simplify(d - o) == 0 for o in (R(5, 3), R(5, 9), 1, 3, R(13, 3))]


# ---------- 多選 7–12 ----------

def ma_cubic_statements(item: dict) -> list[bool]:
    """q7: f(x) = x³ − 6x² + 9x + 1.
    (1) symmetric about (2, 3); (2) remainder on division by x − 2 is 1; (3) f(1) + f(3) = 6;
    (4) the graph is a translation of y = x³; (5) near x = 2 the graph is close to y = −3x + 9."""
    f = x**3 - 6 * x**2 + 9 * x + 1
    s1 = sp.expand(f.subs(x, 4 - x) + f - 6) == 0  # f(2 − u) + f(2 + u) = 6 for all u
    rem = sp.rem(f, x - 2, x)
    s2 = rem == 1
    s3 = f.subs(x, 1) + f.subs(x, 3) == 6
    # a translation of y = x³ would be (x − h)³ + k: compare with f
    h, k = sp.symbols("h k")
    s4 = bool(sp.solve(sp.Poly(sp.expand((x - h) ** 3 + k - f), x).all_coeffs(), [h, k], dict=True))
    # write f in powers of (x − 2) and keep the linear part
    u = sp.Symbol("u")
    g = sp.Poly(sp.expand(f.subs(x, u + 2)), u)
    linear = g.coeff_monomial(u) * (x - 2) + g.coeff_monomial(1)
    s5 = sp.expand(linear - (-3 * x + 9)) == 0
    return [s1, s2, s3, s4, s5]


def ma_data_transform(item: dict) -> list[bool]:
    """q8: x data 2, 4, 6, 8, 10; y = −3x + 2.
    (1) σ_y = −6√2; (2) mean of y = −16; (3) σ_y = 6√2; (4) r(x, y) = −1; (5) range of y = 22.
    Standard deviation divides by n, as on the formula sheet."""
    xs = [2, 4, 6, 8, 10]
    ys = [-3 * v + 2 for v in xs]
    n = len(xs)
    mx, my = R(sum(xs), n), R(sum(ys), n)
    sx = sp.sqrt(sum((v - mx) ** 2 for v in xs) / n)
    sy = sp.sqrt(sum((v - my) ** 2 for v in ys) / n)
    r = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (n * sx * sy)
    return [
        sp.simplify(sy + 6 * sp.sqrt(2)) == 0,
        my == -16,
        sp.simplify(sy - 6 * sp.sqrt(2)) == 0,
        sp.simplify(r + 1) == 0,
        max(ys) - min(ys) == 22,
    ]


def ma_space_vectors(item: dict) -> list[bool]:
    """q9: u = (2, 1, 2), v = (1, −2, 0).
    (1) u ⊥ v; (2) u × v ∥ (−4, −2, 5); (3) |u + v| = |u| + |v|; (4) parallelogram area 3√5;
    (5) with w = (1, 1, 1) the parallelepiped volume is 3."""
    u, v, w = _vec(2, 1, 2), _vec(1, -2, 0), _vec(1, 1, 1)
    c = u.cross(v)
    par = c.cross(_vec(-4, -2, 5)).is_zero_matrix and not c.is_zero_matrix
    vol = abs(sp.Matrix.hstack(u, v, w).det())
    return [
        u.dot(v) == 0,
        bool(par),
        sp.simplify((u + v).norm() - u.norm() - v.norm()) == 0,
        sp.simplify(c.norm() - 3 * sp.sqrt(5)) == 0,
        vol == 3,
    ]


def ma_harmonic_form(item: dict) -> list[bool]:
    """q10: f(x) = √3 sin x − cos x.
    (1) max √3 + 1; (2) period π; (3) f(2π/3) = 2; (4) f(x) = 2 sin(x + π/6) for all x;
    (5) f(x) = 0 has exactly 2 solutions in [0, 2π)."""
    f = sp.sqrt(3) * sp.sin(x) - sp.cos(x)
    dom = sp.Interval.Ropen(0, 2 * sp.pi)
    fmax = sp.maximum(f, x, dom)
    zeros = sp.solveset(f, x, dom)
    identity = sp.simplify(sp.expand_trig(f - 2 * sp.sin(x + sp.pi / 6))) == 0
    return [
        sp.simplify(fmax - (sp.sqrt(3) + 1)) == 0,
        sp.simplify(sp.periodicity(f, x) - sp.pi) == 0,
        sp.simplify(f.subs(x, 2 * sp.pi / 3) - 2) == 0,
        identity,
        len(zeros) == 2,
    ]


def ma_circle_line(item: dict) -> list[bool]:
    """q11: circle (x − 1)² + (y + 2)² = 25, line L: 3x + 4y + k = 0.
    (1) k = 30: tangent; (2) k = 0: no intersection; (3) k = −20: no intersection;
    (4) 4x − 3y = 0 ⊥ L; (5) (4, 2) on the circle. Intersections counted by solving."""
    circle = (x - 1) ** 2 + (y + 2) ** 2 - 25

    def meets(k):
        sols = sp.solve([circle, 3 * x + 4 * y + k], [x, y], dict=True)
        return len([s for s in sols if all(val.is_real for val in s.values())])

    slope_l = R(-3, 4)
    slope_m = R(4, 3)
    return [
        meets(30) == 1,
        meets(0) == 0,
        meets(-20) == 0,
        slope_l * slope_m == -1,
        circle.subs({x: 4, y: 2}) == 0,
    ]


def ma_independence(item: dict) -> list[bool]:
    """q12: P(A) = 0.5, P(B) = 0.4, P(A ∪ B) = 0.7.
    (1) A, B mutually exclusive; (2) P(A ∩ B) = 0.2; (3) independent; (4) P(B | A) = 0.5; (5) P(A' ∩ B') = 0.3."""
    pa, pb, pu = R(1, 2), R(2, 5), R(7, 10)
    pab = pa + pb - pu
    return [
        pab == 0,
        pab == R(1, 5),
        pab == pa * pb,
        pab / pa == R(1, 2),
        1 - pu == R(3, 10),
    ]


# ---------- 選填 13–17 ----------

def ma_recursion_a7(item: dict) -> sp.Integer:
    """q13: a₁ = 3, a_{n+1} = 2a_n − 1. a₇ (iterated, not from the closed form)."""
    a = sp.Integer(3)
    for _ in range(6):
        a = 2 * a - 1
    return a


def ma_binomial_coeff(item: dict) -> sp.Integer:
    """q14: coefficient of x² in (3x − 2)⁵."""
    return sp.Poly(sp.expand((3 * x - 2) ** 5), x).coeff_monomial(x**2)


def ma_exponential_equation(item: dict) -> sp.Integer:
    """q15: 4^x − 10·2^x + 16 = 0 has roots a, b. a² + b²."""
    roots = sp.solveset(4**x - 10 * 2**x + 16, x, domain=sp.S.Reals)
    roots = list(roots)
    assert len(roots) == 2
    return sp.Integer(sp.simplify(sum(r**2 for r in roots)))


def ma_bayes_defective(item: dict) -> tuple[int, int]:
    """q16: machine 甲 makes 60% with 2% defective, 乙 40% with 5% defective.
    P(乙 | defective) = p/q in lowest terms."""
    p_jia, p_yi = R(3, 5), R(2, 5)
    d_jia, d_yi = R(2, 100), R(5, 100)
    post = p_yi * d_yi / (p_jia * d_jia + p_yi * d_yi)
    return (int(post.p), int(post.q))


def ma_line_plane_meet(item: dict) -> tuple[int, int, int]:
    """q17: line x = 1 + t, y = 2 − t, z = 3 + 2t meets the plane x + y + z = 12 at (①, ②③, ④)."""
    pt = (1 + t, 2 - t, 3 + 2 * t)
    t0 = sp.solve(sum(pt) - 12, t)[0]
    return tuple(int(c.subs(t, t0)) for c in pt)


# ---------- 混合題組 18–20 ----------

T_SHOP = sp.Matrix([[R(9, 10), R(2, 10)], [R(1, 10), R(8, 10)]])


def _shop_matrix():
    """Build T from the story: column j = this week's shop, row i = next week's shop.
    甲 keeps 90% and loses 10% to 乙; 乙 loses 20% to 甲 and keeps 80%."""
    stay_jia, jia_to_yi = R(90, 100), R(10, 100)
    yi_to_jia, stay_yi = R(20, 100), R(80, 100)
    return sp.Matrix([[stay_jia, yi_to_jia], [jia_to_yi, stay_yi]])


def ma_mixed_matrix(item: dict) -> list[bool]:
    """q18: which matrix is the transition matrix? Options (rows listed):
    (1) [[0.9,0.1],[0.2,0.8]] (2) [[0.9,0.2],[0.1,0.8]] (3) [[0.9,0.8],[0.1,0.2]]
    (4) [[0.1,0.8],[0.9,0.2]] (5) [[0.2,0.9],[0.8,0.1]]"""
    T = _shop_matrix()
    d = R(1, 10)
    options = [
        sp.Matrix([[9, 1], [2, 8]]) * d,
        sp.Matrix([[9, 2], [1, 8]]) * d,
        sp.Matrix([[9, 8], [1, 2]]) * d,
        sp.Matrix([[1, 8], [9, 2]]) * d,
        sp.Matrix([[2, 9], [8, 1]]) * d,
    ]
    return [T == o for o in options]


def ma_mixed_two_weeks(item: dict) -> bool:
    """q19: X₀ = (0.4, 0.6). The model answer's X₁ = (0.48, 0.52) and X₂ = (0.536, 0.464) hold,
    and the stated matrix is the one built from the story."""
    T = _shop_matrix()
    x0 = sp.Matrix([R(4, 10), R(6, 10)])
    x1 = T * x0
    x2 = T * x1
    return bool(
        T == T_SHOP
        and x1 == sp.Matrix([R(48, 100), R(52, 100)])
        and x2 == sp.Matrix([R(536, 1000), R(464, 1000)])
        and x2 == T**2 * x0
    )


def ma_mixed_steady_state(item: dict) -> bool:
    """q20: the steady state X = (x, y) with TX = X and x + y = 1 is (2/3, 1/3), it is unique,
    and the model answer's reduction 0.1x = 0.2y (x = 2y) is equivalent to TX = X."""
    T = _shop_matrix()
    a, b = sp.symbols("a b")
    X = sp.Matrix([a, b])
    sols = sp.solve(list(T * X - X) + [a + b - 1], [a, b], dict=True)
    reduced = sp.solve([R(1, 10) * a - R(2, 10) * b, a + b - 1], [a, b], dict=True)
    return bool(sols == [{a: R(2, 3), b: R(1, 3)}] and reduced == sols)


# ---------- page claims (not an item check) ----------

def ma_self_marking_table() -> bool:
    """The self-marking table on the page: a 5-point 多選 item with n = 5 options earns
    (n − 2k)/n of 5 points for k wrong options, and 0 when that is negative: 5, 3, 1, 0, 0, 0.
    Also: the paper's points add up to 100 (6×5 + 6×5 + 5×5 + 3 + 6 + 6)."""
    n, full = 5, 5
    scores = [max(R(n - 2 * k, n) * full, 0) for k in range(0, 6)]
    total = 6 * 5 + 6 * 5 + 5 * 5 + 3 + 6 + 6
    return scores == [5, 3, 1, 0, 0, 0] and total == 100


if __name__ == "__main__":  # python -X utf8 harness/checks/m_s116_mock_a.py
    assert ma_self_marking_table()
    print("page claims OK")
