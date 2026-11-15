"""Checks for src/data/items/math/s116x-algebra-meets-graphs.yaml (116 sprint, cross-unit: algebra meets graphs).

Each item check recomputes its answer from the mathematics with SymPy and never reads item["answer"].
The chapter solves five worked problems several ways; check_worked_examples() recomputes every way's
final answer (and the numbers its figures show) and asserts that the ways agree. The q-turn check calls
it, so a run of harness/verify_items.py fails if any worked number in the lesson is wrong.

    harness/.venv/Scripts/python -c "import sys; sys.path.insert(0, 'harness'); from checks import m_s116x_algebra_meets_graphs as m; m.check_worked_examples()"
"""

from __future__ import annotations

import sympy as sp

x, y, k, t = sp.symbols("x y k t", real=True)
R = sp.Rational
REALS = sp.S.Reals


def _solve(rel, domain=REALS) -> sp.Set:
    return sp.solveset(rel, x, domain)


def _min_on(f, domain: sp.Interval):
    """Exact minimum of f on a closed interval (endpoints and critical points); used only to cross-check."""
    crit = [c for c in sp.solveset(sp.diff(f, x), x, domain) if c.is_real]
    cands = [f.subs(x, c) for c in crit] + [f.subs(x, e) for e in (domain.inf, domain.sup) if e.is_finite]
    return sp.Min(*cands)


# ---------------------------------------------------------------------------
# Worked problems in the lesson, every way
# ---------------------------------------------------------------------------
def _problem1() -> None:
    """|2x − 5| < 3 by distance, sandwich, graph and squaring: all give 1 < x < 4."""
    target = sp.Interval.open(1, 4)
    direct = _solve(sp.Abs(2 * x - 5) < 3)
    # distance: |x − 5/2| < 3/2
    c, r = R(5, 2), R(3, 2)
    assert sp.simplify(sp.Abs(2 * x - 5) - 2 * sp.Abs(x - c)) == 0
    by_distance = sp.Interval.open(c - r, c + r)
    # sandwich: −3 < 2x − 5 < 3  ⇔  2 < 2x < 8
    by_sandwich = sp.Interval.open(R(-3 + 5, 2), R(3 + 5, 2))
    # graph: V meets y = 3 at x = (5 ± 3)/2; slider k gives (5 − k)/2 and (5 + k)/2
    meets = sp.solveset(sp.Eq(sp.Abs(2 * x - 5), 3), x, REALS)
    assert meets == sp.FiniteSet(1, 4)
    for kv in range(1, 6):
        assert sp.solveset(sp.Eq(sp.Abs(2 * x - 5), kv), x, REALS) == sp.FiniteSet(R(5 - kv, 2), R(5 + kv, 2))
    by_graph = sp.Interval.open(min(meets), max(meets))
    # squaring: (2x − 5)² < 9  ⇔  4x² − 20x + 16 < 0  ⇔  (x − 1)(x − 4) < 0
    assert sp.expand((2 * x - 5) ** 2 - 9) == 4 * x**2 - 20 * x + 16 == sp.expand(4 * (x - 1) * (x - 4))
    by_square = _solve((x - 1) * (x - 4) < 0)
    assert direct == by_distance == by_sandwich == by_graph == by_square == target
    # "when to prefer which": |x − 1| < x needs the graph/cases (x > 1/2), and |x − 1| < |x + 3| squares to x > −1
    assert _solve(sp.Abs(x - 1) < x) == sp.Interval.open(R(1, 2), sp.oo)
    assert _solve(sp.Abs(x - 1) < sp.Abs(x + 3)) == sp.Interval.open(-1, sp.oo)


def _problem2() -> None:
    """Fence of 20 m on three sides against a wall: area A = x(20 − 2x).
    Completing the square, root symmetry and AM-GM all give max 50 at x = 5; with a wall of 8 m, x ≥ 6 and the max is 48."""
    A = x * (20 - 2 * x)
    # completing the square
    assert sp.expand(A - (-2 * (x - 5) ** 2 + 50)) == 0
    # graph: roots 0 and 10, axis at their midpoint
    roots = sp.solveset(A, x, REALS)
    assert roots == sp.FiniteSet(0, 10) and (0 + 10) / sp.Integer(2) == 5 and A.subs(x, 5) == 50
    # AM-GM on 2x and 20 − 2x (sum 20): 2x(20 − 2x) ≤ ((20)/2)² = 100, so A ≤ 50, equality at 2x = 20 − 2x
    assert sp.expand(2 * A) == sp.expand((2 * x) * (20 - 2 * x)) and (R(20, 2)) ** 2 / 2 == 50
    assert sp.solve(sp.Eq(2 * x, 20 - 2 * x), x) == [5]
    assert -_min_on(-A, sp.Interval(0, 10)) == 50
    # the other side 20 − 2x at x = 5 is 10
    assert 20 - 2 * 5 == 10
    # wall only 8 m: 20 − 2x ≤ 8  ⇔  x ≥ 6, so 6 ≤ x < 10; A decreases right of 5; max A(6) = 6·8 = 48
    assert _solve(20 - 2 * x <= 8) == sp.Interval(6, sp.oo)
    assert A.subs(x, 6) == 48 == 6 * 8
    assert -_min_on(-A, sp.Interval(6, 10)) == 48
    # AM-GM's equality point x = 5 is outside [6, 10), so its bound 50 is not reached there
    assert 5 not in sp.Interval.Ropen(6, 10) and A.subs(x, 6) < 50
    # figure: best x = max(10 − L/2, 5) written as (15 − L/2 + |5 − L/2|)/2
    for Lv in range(4, 21):
        m = 10 - R(Lv, 2)
        best = (15 - R(Lv, 2) + abs(5 - R(Lv, 2))) / 2
        assert best == max(m, 5)
        assert -_min_on(-A, sp.Interval(max(m, 0), 10)) == A.subs(x, best)
    # later block: A'(x) = 20 − 4x = 0 at x = 5
    assert sp.diff(A, x) == 20 - 4 * x and sp.solve(sp.diff(A, x), x) == [5]


def _problem3() -> None:
    """Circle (x − 1)² + (y + 2)² = 8 and line x + y = k: two points iff −5 < k < 3, by distance, discriminant and tangent points."""
    f = (x - 1) ** 2 + (y + 2) ** 2 - 8
    r = sp.sqrt(8)
    assert r == 2 * sp.sqrt(2)
    # distance: |1 − 2 − k|/√2 < 2√2  ⇔  |k + 1| < 4
    d = sp.Abs(1 + (-2) - k) / sp.sqrt(2)
    by_distance = sp.solveset(d < r, k, REALS)
    assert sp.solveset(sp.Abs(k + 1) < 4, k, REALS) == by_distance
    # discriminant: y = k − x gives 2x² − (2k + 6)x + (k + 2)² − 7 = 0
    quad = sp.expand(f.subs(y, k - x))
    assert sp.expand(quad - (2 * x**2 - (2 * k + 6) * x + (k + 2) ** 2 - 7)) == 0
    D = sp.discriminant(quad, x)
    assert sp.expand(D - (-4 * k**2 - 8 * k + 60)) == 0 and sp.expand(D + 4 * (k + 5) * (k - 3)) == 0
    by_disc = sp.solveset(D > 0, k, REALS)
    # tangent points: centre ± r · (1, 1)/√2 = (3, 0) and (−1, −4), on lines k = 3 and k = −5
    unit = (1 / sp.sqrt(2), 1 / sp.sqrt(2))
    T1 = (1 + r * unit[0], -2 + r * unit[1])
    T2 = (1 - r * unit[0], -2 - r * unit[1])
    assert tuple(sp.simplify(c) for c in T1) == (3, 0) and tuple(sp.simplify(c) for c in T2) == (-1, -4)
    assert f.subs({x: 3, y: 0}) == 0 and f.subs({x: -1, y: -4}) == 0
    by_tangents = sp.Interval.open(sp.simplify(T2[0] + T2[1]), sp.simplify(T1[0] + T1[1]))
    assert by_distance == by_disc == by_tangents == sp.Interval.open(-5, 3)
    # at k = 3 the double root is x = 3 (tangent point (3, 0)); at k = −5 it is x = −1
    assert sp.solveset(quad.subs(k, 3), x, REALS) == sp.FiniteSet(3)
    assert sp.solveset(quad.subs(k, -5), x, REALS) == sp.FiniteSet(-1)
    # figure: foot of the perpendicular (1 + (k + 1)/2, −2 + (k + 1)/2) lies on x + y = k
    foot = (1 + (k + 1) / 2, -2 + (k + 1) / 2)
    assert sp.simplify(foot[0] + foot[1] - k) == 0
    # k = 1 (inside the range): two points; k = 4: none
    assert len(sp.solveset(quad.subs(k, 1), x, REALS)) == 2 and sp.solveset(quad.subs(k, 4), x, REALS) == sp.S.EmptySet


def _problem4() -> None:
    """(x − 3)(x² − 4) ≥ 0 by sign chart, graph and cases: −2 ≤ x ≤ 2 or x ≥ 3."""
    p = (x - 3) * (x**2 - 4)
    target = sp.Union(sp.Interval(-2, 2), sp.Interval(3, sp.oo))
    assert sp.expand(p - (x + 2) * (x - 2) * (x - 3)) == 0
    assert sp.expand(p - (x**3 - 3 * x**2 - 4 * x + 12)) == 0
    direct = _solve(p >= 0)
    # sign chart: signs on (−∞,−2), (−2,2), (2,3), (3,∞) are −, +, −, +
    signs = [sp.sign(p.subs(x, v)) for v in (-3, 0, R(5, 2), 4)]
    assert signs == [-1, 1, -1, 1]
    # cases on x − 3: x > 3 needs x² ≥ 4 (always there); x = 3 gives 0; x < 3 needs x² ≤ 4
    case_right = sp.Interval.open(3, sp.oo).intersect(_solve(x**2 - 4 >= 0))
    case_left = sp.Interval.open(-sp.oo, 3).intersect(_solve(x**2 - 4 <= 0))
    by_cases = sp.Union(case_right, sp.FiniteSet(3), case_left)
    assert case_right == sp.Interval.open(3, sp.oo) and case_left == sp.Interval(-2, 2)
    assert direct == by_cases == target
    # check point x = 0: (−3)(−4) = 12 ≥ 0
    assert p.subs(x, 0) == 12


def _problem5() -> None:
    """f(x) = x² + bx + c with f(−1) = f(5) and minimum −4: by symmetry and by algebra b = −4, c = 0.
    y = f(x) is y = x² shifted right 2 and down 4; y = f(−x) = x² + 4x has vertex (−2, −4)."""
    b, c = sp.symbols("b c", real=True)
    f = x**2 + b * x + c
    # algebra
    (bsol,) = sp.solve(sp.Eq(f.subs(x, -1), f.subs(x, 5)), b)
    assert bsol == -4
    fb = f.subs(b, bsol)
    assert sp.expand(fb - ((x - 2) ** 2 + c - 4)) == 0
    (csol,) = sp.solve(sp.Eq(c - 4, -4), c)
    # symmetry: axis at the midpoint (−1 + 5)/2 = 2, so f = (x − 2)² − 4
    axis = (-1 + 5) / sp.Integer(2)
    sym = (x - axis) ** 2 - 4
    assert axis == 2 and csol == 0 and sp.expand(sym - fb.subs(c, csol)) == 0
    F = sp.expand(sym)
    assert F == x**2 - 4 * x and F.subs(x, -1) == F.subs(x, 5) == 5
    # mirror: f(−x) = x² + 4x = (x + 2)² − 4, vertex (−2, −4)
    G = sp.expand(F.subs(x, -x))
    assert G == x**2 + 4 * x and sp.expand(G - ((x + 2) ** 2 - 4)) == 0
    # figure: f(2 ± t) = t² − 4, and f(−x) at −2 ∓ t is the same height
    assert sp.expand(F.subs(x, 2 + t) - (t**2 - 4)) == 0 and sp.expand(F.subs(x, 2 - t) - (t**2 - 4)) == 0
    assert sp.expand(G.subs(x, -2 - t) - (t**2 - 4)) == 0 and sp.expand(G.subs(x, -2 + t) - (t**2 - 4)) == 0
    # roots 0 and 4 of f, midpoint 2 again
    assert sp.solveset(F, x, REALS) == sp.FiniteSet(0, 4)


def check_worked_examples() -> None:
    _problem1()
    _problem2()
    _problem3()
    _problem4()
    _problem5()
    # q-turn dialogue: y = x² − 6x + 11 = (x − 3)² + 2, roots of nothing (D = 36 − 44 < 0)
    assert sp.expand((x - 3) ** 2 + 2 - (x**2 - 6 * x + 11)) == 0


# ---------------------------------------------------------------------------
# Item checks
# ---------------------------------------------------------------------------
def amg_turn_min(item: dict) -> list[bool]:
    """q-turn: the minimum of y = x² − 6x + 11. Options 2, 11, −2, 3, 5. Also runs the worked-example checks."""
    check_worked_examples()
    f = x**2 - 6 * x + 11
    m = _min_on(f, sp.Interval(-100, 100))
    # cross-check by completing the square
    assert sp.expand(f - ((x - 3) ** 2 + 2)) == 0
    return [sp.simplify(m - o) == 0 for o in (2, 11, -2, 3, 5)]


def amg_abs_integer_count(item: dict) -> sp.Integer:
    """q1: the number of integers x with |3x − 7| ≤ 8."""
    sol = _solve(sp.Abs(3 * x - 7) <= 8)
    ints = sol.intersect(sp.S.Integers)
    # cross-check by the sandwich −1/3 ≤ x ≤ 5
    assert sol == sp.Interval(R(-1, 3), 5)
    return sp.Integer(len(list(ints)))


def amg_fence_with_short_wall(item: dict) -> list[bool]:
    """q2: 24 m of fence on three sides against a 10 m wall; side perpendicular to the wall x.
    The parallel side 24 − 2x must be positive and at most 10, so 7 ≤ x < 12. Max area?
    Options 72, 70, 64, 54, 50."""
    A = x * (24 - 2 * x)
    allowed = sp.Interval(7, 12).intersect(_solve(24 - 2 * x <= 10)).intersect(_solve(24 - 2 * x >= 0))
    assert allowed == sp.Interval(7, 12)
    best = -_min_on(-A, allowed)
    return [sp.simplify(best - o) == 0 for o in (72, 70, 64, 54, 50)]


def amg_am_gm_product(item: dict) -> sp.Integer:
    """q3: x, y > 0 with x + 4y = 12; the maximum of xy."""
    P = x * (12 - x) / 4  # y = (12 − x)/4, with 0 < x < 12
    best = -_min_on(-P, sp.Interval(0, 12))
    # AM-GM: x·4y ≤ ((x + 4y)/2)² = 36, equality x = 4y = 6, y = 3/2 > 0
    assert R(12, 2) ** 2 / 4 == best and (12 - 6) / sp.Integer(4) == R(3, 2)
    return sp.Integer(best)


def amg_line_circle_integer_k(item: dict) -> sp.Integer:
    """q4: the number of integers k for which 3x + 4y = k meets (x − 2)² + (y − 1)² = 4 in two points.
    Decided by the discriminant, cross-checked by the distance |10 − k|/5 < 2."""
    f = (x - 2) ** 2 + (y - 1) ** 2 - 4
    quad = sp.expand(f.subs(y, (k - 3 * x) / 4) * 16)
    D = sp.discriminant(quad, x)
    by_disc = sp.solveset(D > 0, k, REALS)
    by_dist = sp.solveset(sp.Abs(3 * 2 + 4 * 1 - k) / 5 < 2, k, REALS)
    assert by_disc == by_dist == sp.Interval.open(0, 20)
    return sp.Integer(len(list(by_disc.intersect(sp.S.Integers))))


def amg_double_root_inequality(item: dict) -> list[bool]:
    """q5: (x + 3)(x − 1)²(x − 5) < 0. Statements: x = 0 is a solution; x = 1 is a solution; x = −4 is a solution;
    the solution set is (−3, 1) ∪ (1, 5); there are exactly 7 integer solutions."""
    p = (x + 3) * (x - 1) ** 2 * (x - 5)
    sol = _solve(p < 0)
    ints = list(sol.intersect(sp.S.Integers))
    return [
        0 in sol,
        1 in sol,
        -4 in sol,
        sol == sp.Union(sp.Interval.open(-3, 1), sp.Interval.open(1, 5)),
        len(ints) == 7,
    ]


def amg_when_am_gm_fails(item: dict) -> list[bool]:
    """q6: in which problem does the AM-GM equality case give a wrong answer (its equality point is not allowed)?
    (1) min x + 16/x, x > 0   (2) min x + 16/x, x ≥ 5   (3) min 4x + 1/x, x > 0
    (4) max x(4 − x), 0 < x < 4   (5) min x + 1/(x − 1), x > 1.
    For each: the AM-GM value and equality point, versus the true extremum on the allowed set."""
    big = 10**4
    problems = [
        # (expression, allowed set, kind, AM-GM bound, equality point)
        (x + 16 / x, sp.Interval.open(0, sp.oo), "min", 2 * sp.sqrt(16), 4),
        (x + 16 / x, sp.Interval(5, sp.oo), "min", 2 * sp.sqrt(16), 4),
        (4 * x + 1 / x, sp.Interval.open(0, sp.oo), "min", 2 * sp.sqrt(4), R(1, 2)),
        (x * (4 - x), sp.Interval.open(0, 4), "max", R(4, 2) ** 2, 2),
        (x + 1 / (x - 1), sp.Interval.open(1, sp.oo), "min", 2 * sp.sqrt(1) + 1, 2),
    ]
    fails = []
    for expr, allowed, kind, bound, eq_pt in problems:
        # the bound itself is a true AM-GM bound: equality point gives exactly the bound
        assert sp.simplify(expr.subs(x, eq_pt) - bound) == 0
        g = expr if kind == "min" else -expr
        lo = allowed.inf if allowed.left_open is False else allowed.inf + R(1, big)
        hi = allowed.sup if allowed.sup.is_finite and not allowed.right_open else (allowed.sup - R(1, big) if allowed.sup.is_finite else big)
        true = _min_on(g, sp.Interval(lo, hi))
        true = true if kind == "min" else -true
        fails.append(not (eq_pt in allowed and sp.simplify(true - bound) == 0))
    return fails


def amg_symmetric_values(item: dict) -> list[bool]:
    """q7: a quadratic f with f(−3) = f(7). Which value must equal f(0)? Options f(1), f(4), f(5), f(−2), f(10)."""
    a, b, c = sp.symbols("a b c", real=True)
    f = a * x**2 + b * x + c
    (bsol,) = sp.solve(sp.Eq(f.subs(x, -3), f.subs(x, 7)), b)  # a ≠ 0 cancels: b = −4a
    g = f.subs(b, bsol)
    return [sp.expand(g.subs(x, 0) - g.subs(x, o)) == 0 for o in (1, 4, 5, -2, 10)]
