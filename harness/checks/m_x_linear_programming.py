"""Checks for src/data/items/math/x-linear-programming.yaml (分科 advanced tool: linear programming, A-12乙-1,
built on the G-10-2 regions of linear inequalities in two variables).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
A region is a list of constraints (a, b, c) meaning a*x + b*y <= c. Its corner points are found by
intersecting every pair of boundary lines and keeping the points that satisfy all constraints; extrema
of a linear function are then cross-checked on a fine rational grid of feasible points, so a check never
relies only on the "look at the vertices" rule that the chapter teaches. Unbounded regions are probed by
adding a box |x|, |y| <= M for growing M and watching whether the optimum keeps moving.

The worked examples of the lesson are asserted at import time (every way of solving them must agree), so
a wrong number in the page fails the harness run.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations

import sympy as sp

x, y = sp.symbols("x y", real=True)
Q = sp.Rational


def _feasible(region, p) -> bool:
    return all(a * p[0] + b * p[1] <= c for a, b, c in region)


def _vertices(region) -> list[tuple]:
    """Corner points of {a x + b y <= c for all constraints}, by pairwise intersection + feasibility."""
    pts = set()
    for (a1, b1, c1), (a2, b2, c2) in combinations(region, 2):
        sol = sp.solve([a1 * x + b1 * y - c1, a2 * x + b2 * y - c2], [x, y], dict=True)
        if len(sol) == 1 and len(sol[0]) == 2:
            p = (sp.nsimplify(sol[0][x]), sp.nsimplify(sol[0][y]))
            if _feasible(region, p):
                pts.add(p)
    return sorted(pts)


def _grid_extrema(region, f, lo=-12, hi=12, step=Fraction(1, 4)):
    """Max and min of f over feasible points of a rational grid (an independent brute-force check)."""
    vals = []
    n = int((hi - lo) / step)
    for i in range(n + 1):
        for j in range(n + 1):
            p = (lo + i * step, lo + j * step)
            if _feasible(region, p):
                vals.append(f(*p))
    hi_v, lo_v = Fraction(max(vals)), Fraction(min(vals))
    return sp.Rational(hi_v.numerator, hi_v.denominator), sp.Rational(lo_v.numerator, lo_v.denominator)


def _extrema(region, f):
    """(max, min, argmax list, argmin list) of f over a bounded region, checked against the grid."""
    vs = _vertices(region)
    vals = [f(*v) for v in vs]
    mx, mn = max(vals), min(vals)
    gmx, gmn = _grid_extrema(region, f)
    assert gmx <= mx and gmn >= mn, "a grid point beats every vertex"
    return mx, mn, [v for v in vs if f(*v) == mx], [v for v in vs if f(*v) == mn]


def _bounded_above(region, f) -> bool:
    """f bounded above on the region? Add the box |x|, |y| <= M and see whether the max stops growing."""
    maxima = []
    for M in (50, 500, 5000):
        boxed = region + [(1, 0, M), (-1, 0, M), (0, 1, M), (0, -1, M)]
        maxima.append(max(f(*v) for v in _vertices(boxed)))
    return maxima[0] == maxima[1] == maxima[2]


def _bounded_below(region, f) -> bool:
    return _bounded_above(region, lambda u, v: -f(u, v))


def _min_unbounded_region(region, f):
    """Min of f when it is bounded below: optimum over the region cut by a large box (box not active)."""
    boxed = region + [(1, 0, 5000), (0, 1, 5000)]
    vs = _vertices(boxed)
    return min(f(*v) for v in vs)


# ---------- worked examples in the lesson (asserted at import) ----------

def _worked_examples() -> None:
    # Region R: x >= 0, y >= 0, x + y <= 5, x + 3y <= 9.
    R = [(-1, 0, 0), (0, -1, 0), (1, 1, 5), (1, 3, 9)]
    assert _vertices(R) == [(0, 0), (0, 3), (3, 2), (5, 0)]
    # the "no drawing" way: of the six pairwise intersections, (0, 5) and (9, 0) are rejected
    assert not _feasible(R, (0, 5)) and not _feasible(R, (9, 0))
    # the two failed checks quoted on the page: (0, 5) gives x + 3y = 15 > 9, (9, 0) gives x + y = 9 > 5
    assert 0 + 3 * 5 == 15 > 9 and 9 + 0 == 9 > 5
    # test point (1, 1) is inside
    assert _feasible(R, (1, 1))
    # f = 2x + 3y: vertex values 0, 10, 12, 9; max 12 at (3, 2), min 0 at (0, 0)
    f = lambda u, v: 2 * u + 3 * v
    assert [f(*p) for p in [(0, 0), (5, 0), (3, 2), (0, 3)]] == [0, 10, 12, 9]
    mx, mn, amx, amn = _extrema(R, f)
    assert (mx, mn, amx, amn) == (12, 0, [(3, 2)], [(0, 0)])
    # edge walk from (5, 0) to (3, 2): (5 - 2t, 2t), f = 10 + 2t
    t = sp.Symbol("t")
    assert sp.expand(f(5 - 2 * t, 2 * t)) == 10 + 2 * t
    # slopes: objective −2/3 lies between the edge slopes −1 (x + y = 5) and −1/3 (x + 3y = 9)
    assert Q(-1) < Q(-2, 3) < Q(-1, 3)
    # inequality-combination way: 2x + 3y = 3/2 (x + y) + 1/2 (x + 3y) <= 3/2*5 + 1/2*9 = 12
    a, b = sp.symbols("a b")
    sol = sp.solve([a + b - 2, a + 3 * b - 3], [a, b])
    assert sol == {a: Q(3, 2), b: Q(1, 2)}
    assert sol[a] * 5 + sol[b] * 9 == 12
    # f = x + y: max 5 along the whole edge from (5, 0) to (3, 2)
    mx, _, amx, _ = _extrema(R, lambda u, v: u + v)
    assert mx == 5 and amx == [(3, 2), (5, 0)]
    assert (Q(4) + 1) == 5  # midpoint (4, 1) of that edge also gives 5
    # GSAT-type: line x + 2y = k meets R exactly for 0 <= k <= 7 (vertex values 0, 5, 7, 6)
    g = lambda u, v: u + 2 * v
    assert [g(*p) for p in [(0, 0), (5, 0), (3, 2), (0, 3)]] == [0, 5, 7, 6]
    mx, mn, _, _ = _extrema(R, g)
    assert (mx, mn) == (7, 0)
    # same-side view at k = 8: every vertex gives x + 2y − 8 < 0, so the line misses R
    assert all(g(*p) - 8 < 0 for p in _vertices(R))

    # Production example: 2x + y <= 10 (kg of material), x + 3y <= 15 (hours), x, y >= 0;
    # profit 300x + 400y: vertices (0, 0), (5, 0), (3, 4), (0, 5); max 2500 at (3, 4).
    P = [(-1, 0, 0), (0, -1, 0), (2, 1, 10), (1, 3, 15)]
    assert _vertices(P) == [(0, 0), (0, 5), (3, 4), (5, 0)]
    h = lambda u, v: 300 * u + 400 * v
    assert [h(*p) for p in [(0, 0), (5, 0), (3, 4), (0, 5)]] == [0, 1500, 2500, 2000]
    mx, _, amx, _ = _extrema(P, h)
    assert mx == 2500 and amx == [(3, 4)]
    # slope check: −3/4 lies between −2 (2x + y = 10) and −1/3 (x + 3y = 15)
    assert Q(-2) < Q(-3, 4) < Q(-1, 3)
    # inequality-combination way: 300x + 400y = 100(2x + y) + 100(x + 3y) <= 100*10 + 100*15 = 2500
    sol = sp.solve([2 * a + b - 300, a + 3 * b - 400], [a, b])
    assert sol == {a: 100, b: 100}
    assert sol[a] * 10 + sol[b] * 15 == 2500
    # GSAT-type, way 1 (same-side test): x + 2y − k at the vertices is −k, 5 − k, 7 − k, 6 − k;
    # all < 0 iff k > 7, all > 0 iff k < 0, so the line meets R iff 0 <= k <= 7 (sweep k to confirm)
    hits = [Q(k2, 2) for k2 in range(-20, 21)
            if min(g(*p) - Q(k2, 2) for p in _vertices(R)) <= 0 <= max(g(*p) - Q(k2, 2) for p in _vertices(R))]
    assert (min(hits), max(hits)) == (0, 7)


_worked_examples()


# ---------- items ----------

def lp_turn_in_region(item: dict) -> list[bool]:
    """q-turn: which point lies in x >= 0, y >= 0, x + 2y <= 4?
    Options: (1, 1), (2, 2), (−1, 1), (0, 3), (4, 1)."""
    region = [(-1, 0, 0), (0, -1, 0), (1, 2, 4)]
    return [_feasible(region, p) for p in [(1, 1), (2, 2), (-1, 1), (0, 3), (4, 1)]]


def lp_max_triangle(item: dict) -> list[bool]:
    """q1: max of 3x + 2y on x >= 0, y >= 0, x + y <= 6, 2x + y <= 8. Options: 12, 14, 16, 18, 24."""
    region = [(-1, 0, 0), (0, -1, 0), (1, 1, 6), (2, 1, 8)]
    mx, _, _, _ = _extrema(region, lambda u, v: 3 * u + 2 * v)
    return [mx == o for o in (12, 14, 16, 18, 24)]


def lp_min_unbounded(item: dict) -> int:
    """q2: min of 2x + 3y on x >= 0, y >= 0, x + y >= 4, x + 3y >= 6 (an unbounded region)."""
    region = [(-1, 0, 0), (0, -1, 0), (-1, -1, -4), (-1, -3, -6)]
    f = lambda u, v: 2 * u + 3 * v
    assert _bounded_below(region, f) and not _bounded_above(region, f)
    return _min_unbounded_region(region, f)


def lp_region_statements(item: dict) -> list[bool]:
    """q3: R: x >= 0, y >= 0, x + 2y <= 8, 3x + y <= 9.
    (1) (1, 3) in R; (2) (3, 1) in R; (3) max of x + y is 5;
    (4) min of x − y is −3; (5) max of 2x + 4y is 16, reached at more than one point of R."""
    R = [(-1, 0, 0), (0, -1, 0), (1, 2, 8), (3, 1, 9)]
    s1 = _feasible(R, (1, 3))
    s2 = _feasible(R, (3, 1))
    s3 = _extrema(R, lambda u, v: u + v)[0] == 5
    s4 = _extrema(R, lambda u, v: u - v)[1] == -3
    mx, _, amx, _ = _extrema(R, lambda u, v: 2 * u + 4 * v)
    # two optimal vertices => the whole edge between them is optimal
    s5 = mx == 16 and len(amx) >= 2
    return [s1, s2, s3, s4, s5]


def lp_line_meets_triangle(item: dict) -> tuple[int, int]:
    """q4: the line x + y = k meets the triangle with vertices (1, 1), (5, 2), (2, 6) (edges included)
    exactly when m <= k <= M; return (m, M). Recomputed by sweeping k and testing a sign change
    of x + y − k over the vertices (the 10th-grade same-side test), not by taking min and max."""
    tri = [(1, 1), (5, 2), (2, 6)]
    meets = []
    for k2 in range(-40, 41):  # k = k2 / 2
        k = Q(k2, 2)
        vals = [u + v - k for u, v in tri]
        if min(vals) <= 0 <= max(vals):
            meets.append(k)
    m, M = min(meets), max(meets)
    # the set of such k is an interval: every half-step between m and M meets the triangle
    assert len(meets) == int((M - m) * 2) + 1
    return (m, M)


def lp_production(item: dict) -> int:
    """q5: A uses 2 h machine + 1 h labour, B uses 1 h machine + 2 h labour; machine <= 14 h,
    labour <= 10 h. Profit 500 per A, 400 per B. Max profit (whole numbers of products)."""
    region = [(-1, 0, 0), (0, -1, 0), (2, 1, 14), (1, 2, 10)]
    f = lambda u, v: 500 * u + 400 * v
    mx, _, amx, _ = _extrema(region, f)
    # the products are whole numbers: the best lattice point must reach the same value
    best = max(f(i, j) for i in range(0, 15) for j in range(0, 15) if _feasible(region, (i, j)))
    assert best == mx and all(p[0].is_integer and p[1].is_integer for p in amx)
    return mx


def lp_unbounded_statements(item: dict) -> list[bool]:
    """q6: S: x >= 0, y >= 0, x + y >= 2. (1) min of x + y is 2; (2) x + y has a max on S;
    (3) x − y has a max on S; (4) min of x + 2y is 2; (5) x − 2y has a min on S."""
    S = [(-1, 0, 0), (0, -1, 0), (-1, -1, -2)]
    s = lambda u, v: u + v
    s1 = _bounded_below(S, s) and _min_unbounded_region(S, s) == 2
    s2 = _bounded_above(S, s)
    s3 = _bounded_above(S, lambda u, v: u - v)
    t = lambda u, v: u + 2 * v
    s4 = _bounded_below(S, t) and _min_unbounded_region(S, t) == 2
    s5 = _bounded_below(S, lambda u, v: u - 2 * v)
    return [s1, s2, s3, s4, s5]
