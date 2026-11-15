"""Checks for src/data/items/math/s116xb-models-and-tables.yaml (116 sprint, 數B cross-unit:
models, tables and pictures, many ways).

Each item check recomputes its answer from the mathematics with SymPy; none reads item["answer"].
`_check_worked_ways()` runs at import time and asserts that every way shown in the lesson for each
worked problem reaches the same number, so a wrong worked example breaks the harness run.
"""

from __future__ import annotations

import sympy as sp

M = sp.Matrix
t, x, y, D, p, c = sp.symbols("t x y D p c", real=True)
th = sp.symbols("theta", real=True)


def _line_through(P, Q):
    """y as a function of x for the non-vertical line through P and Q."""
    (x1, y1), (x2, y2) = P, Q
    m = sp.Rational(y2 - y1, x2 - x1)
    return m * (x - x1) + y1


def _meet(f, g):
    """Intersection point of y=f(x) and y=g(x) (exactly one)."""
    (xs,) = sp.solve(sp.Eq(f, g), x)
    return sp.simplify(xs), sp.simplify(f.subs(x, xs))


def _solution_interval(expr, lo, hi, var=t):
    """The set of var in [lo, hi] where expr >= 0, as a SymPy set."""
    return sp.solveset(expr >= 0, var, sp.Interval(lo, hi))


def _check_worked_ways() -> None:
    # Problem 1: two shops, three goods. Difference of revenue, three ways.
    S = M([[20, 8, 15], [25, 6, 10]])
    P = M([35, 120, 50])
    direct = (20 * 35 + 8 * 120 + 15 * 50) - (25 * 35 + 6 * 120 + 10 * 50)
    rows_first = (S.row(0) - S.row(1)).dot(P)
    matrix = (M([[1, -1]]) * (S * P))[0, 0]
    assert S * P == M([2410, 2095])
    assert S.row(0) - S.row(1) == M([[-5, 2, 5]])
    assert direct == rows_first == matrix == 315
    # The figure: bread price p varies; revenues 20p+1710 and 25p+1220 meet at p=98, gap 490-5p.
    rev_a = (M([[20, 8, 15]]) * M([p, 120, 50]))[0, 0]
    rev_b = (M([[25, 6, 10]]) * M([p, 120, 50]))[0, 0]
    assert sp.expand(rev_a - (20 * p + 1710)) == 0 and sp.expand(rev_b - (25 * p + 1220)) == 0
    assert sp.solve(sp.Eq(rev_a, rev_b), p) == [98] and rev_a.subs(p, 98) == 3670
    assert sp.expand(rev_a - rev_b - (490 - 5 * p)) == 0

    # Problem 2: set meals 3x+2y=130, 2x+y=80, three ways.
    A = M([[3, 2], [2, 1]])
    B = M([130, 80])
    one_each = 130 - 80  # (row 1 - row 2): one rice ball + one soy milk
    rice = 80 - one_each  # row 2 - (row 1 - row 2): one rice ball
    soy = one_each - rice
    assert (rice, soy) == (30, 20)
    assert A.det() == -1 and A.inv() == M([[-1, 2], [2, -3]])
    assert A.inv() * B == M([30, 20])
    assert _meet(65 - sp.Rational(3, 2) * x, 80 - 2 * x) == (30, 20)
    assert A.inv() * M([145, 90]) == M([35, 20])
    # The figure: the second total is c; the solution is (2c-130, 260-3c).
    sol = A.inv() * M([130, c])
    assert sp.expand(sol[0] - (2 * c - 130)) == 0 and sp.expand(sol[1] - (260 - 3 * c)) == 0
    assert sol.subs(c, 86) == M([42, 2])
    assert A.inv() * M([130, 82]) == M([34, 14])  # the TryIt: second meal at 82
    assert A * M([34, 14]) == M([130, 82])

    # Problem 3: poles 6 and 3 tall, D apart; ropes top-to-foot cross at height 2 whatever D is.
    h = sp.symbols("h", positive=True)
    (h_sim,) = sp.solve(sp.Eq(h / 6 + h / 3, 1), h)
    assert h_sim == 2 and sp.Rational(6 * 3, 6 + 3) == 2
    assert _meet(_line_through((0, 6), (9, 0)), _line_through((9, 3), (0, 0))) == (6, 2)
    xs, ys = _meet(6 - 6 * x / D, 3 * x / D)
    assert sp.simplify(ys - 2) == 0 and sp.simplify(xs - 2 * D / 3) == 0

    # Problem 4: perspective road. Edges through (0,0),(3,2) and (12,0),(9,2); V=(6,4).
    left = _line_through((0, 0), (3, 2))
    right = _line_through((12, 0), (9, 2))
    V = _meet(left, right)
    assert V == (6, 4)
    width = lambda yy: 3 * (4 - yy)  # noqa: E731  similar triangles with apex V: width 12 at y=0, 0 at y=4
    assert width(0) == 12 and width(2) == 6
    (y3,) = sp.solve(sp.Eq(width(y), sp.Rational(12, 3)), y)  # third line: depth 3x, width 12/3
    assert y3 == sp.Rational(8, 3)
    construction = _line_through((0, 0), (6, 2))  # through the midpoint of the second line
    assert _meet(construction, right) == (8, sp.Rational(8, 3))
    assert left.subs(x, 4) == sp.Rational(8, 3)  # the third line runs from (4, 8/3) to (8, 8/3)
    assert 4 - 4 * sp.Rational(1, 3) == sp.Rational(8, 3)  # height below the horizon shrinks like 1/depth
    # figure: the n-th line at y=4-4/n spans x=6-6/n .. 6+6/n on the two edges
    n = sp.symbols("n", positive=True)
    assert sp.simplify(left.subs(x, 6 - 6 / n) - (4 - 4 / n)) == 0
    assert sp.simplify(right.subs(x, 6 + 6 / n) - (4 - 4 / n)) == 0

    # Problem 5: tide d(t)=3 sin(pi t/6)+8 >= 9.5 on [0,12] is [1,5].
    d = 3 * sp.sin(sp.pi * t / 6) + 8
    assert _solution_interval(d - sp.Rational(19, 2), 0, 12) == sp.Interval(1, 5)
    assert sp.solveset(sp.sin(th) >= sp.Rational(1, 2), th, sp.Interval(0, 2 * sp.pi)) == sp.Interval(sp.pi / 6, 5 * sp.pi / 6)
    table = [sp.nsimplify(d.subs(t, k)) for k in range(13)]
    s3 = sp.sqrt(3)
    assert table == [8, sp.Rational(19, 2), 8 + sp.Rational(3, 2) * s3, 11, 8 + sp.Rational(3, 2) * s3, sp.Rational(19, 2), 8,
                     sp.Rational(13, 2), 8 - sp.Rational(3, 2) * s3, 5, 8 - sp.Rational(3, 2) * s3, sp.Rational(13, 2), 8]
    assert [k for k in range(13) if table[k] >= sp.Rational(19, 2)] == [1, 2, 3, 4, 5]
    # monotonic pieces used to fill the gaps between table rows
    dd = sp.diff(d, t)
    assert sp.solveset(dd > 0, t, sp.Interval.open(0, 12)) == sp.Union(sp.Interval.open(0, 3), sp.Interval.open(9, 12))
    assert d.subs(t, 3 + 2) == d.subs(t, 3 - 2)  # symmetry about the peak t=3

    # Problem 6: greenhouse table 20,26,20,14,20 at t=0,3,6,9,12, period 12.
    model = 6 * sp.sin(sp.pi * t / 6) + 20
    assert [model.subs(t, k) for k in (0, 3, 6, 9, 12)] == [20, 26, 20, 14, 20]
    assert 39 % 12 == 3 and model.subs(t, 39) == 26
    first = sp.solveset(sp.Eq(model, 23), t, sp.Interval(0, 3))
    assert first == sp.FiniteSet(1)
    # straight-line interpolation between the rows (0, 20) and (3, 26) would say 1.5, which is wrong
    assert sp.solve(sp.Eq(20 + 2 * t, 23), t) == [sp.Rational(3, 2)]
    assert model.subs(t, sp.Rational(3, 2)) == 20 + 3 * sp.sqrt(2) and round(float(20 + 3 * sp.sqrt(2)), 1) == 24.2
    # rounded table entries quoted in the lesson for problem 5
    assert round(float(8 + sp.Rational(3, 2) * s3), 1) == 10.6 and round(float(8 - sp.Rational(3, 2) * s3), 1) == 5.4


_check_worked_ways()


def xb_turn_apple(item: dict) -> list[bool]:
    """q-turn: 2 apples + 1 pear = 50, 1 apple + 1 pear = 35. Price of one apple.
    Options: 15, 20, 35, 10, 25."""
    sol = M([[2, 1], [1, 1]]).inv() * M([50, 35])
    return [sol[0] == v for v in (15, 20, 35, 10, 25)]


def xb_shop_difference(item: dict) -> sp.Integer:
    """q1: shop 甲 buys 4 pens and 6 notebooks, shop 乙 5 pens and 2 notebooks; pens 15, notebooks 40.
    How much more does 甲 spend than 乙? Computed as [1, -1] (N P)."""
    N = M([[4, 6], [5, 2]])
    P = M([15, 40])
    return sp.Integer((M([[1, -1]]) * N * P)[0, 0])


def xb_system_inverse(item: dict) -> tuple[int, int]:
    """q2: 5x+2y=74, 2x+y=31. Solve by X = A^{-1}B; cells x = ①②, y = ③."""
    sol = M([[5, 2], [2, 1]]).inv() * M([74, 31])
    return (int(sol[0]), int(sol[1]))


def xb_poles_multi(item: dict) -> list[bool]:
    """q3: poles 4 m and 12 m tall stand 10 m apart; each rope runs from one top to the other foot.
    Options: crossing height 3; crossing height 8; height unchanged if the distance changes;
    crossing is 7.5 m (horizontally) from the 4 m pole; the foot of the crossing splits the gap 1:3."""
    # 4 m pole at x=0, 12 m pole at x=dist
    rope1 = lambda dist: 4 - 4 * x / dist  # noqa: E731  (0,4) to (dist,0)
    rope2 = lambda dist: 12 * x / dist  # noqa: E731  (0,0) to (dist,12)
    xs, ys = _meet(rope1(10), rope2(10))
    xg, yg = _meet(rope1(D), rope2(D))
    return [
        ys == 3,
        ys == 8,
        sp.simplify(yg - ys) == 0,
        xs == sp.Rational(15, 2),
        sp.Rational(xs) / (10 - xs) == sp.Rational(1, 3),
    ]


def xb_perspective_fourth(item: dict) -> tuple[int, int]:
    """q4: road edges drawn through (0,0),(2,2) and (10,0),(8,2). The front line (y=0) is at depth d0;
    find the drawn height y of the line at depth 4 d0, as a fraction ①②/③."""
    left = _line_through((0, 0), (2, 2))
    right = _line_through((10, 0), (8, 2))
    vx, vy = _meet(left, right)
    assert (vx, vy) == (5, 5)
    front_width = 10
    # width of the road at drawn height Y, by the similar triangles with apex V
    Y = sp.symbols("Y")
    xl = sp.solve(sp.Eq(left, Y), x)[0]
    xr = sp.solve(sp.Eq(right, Y), x)[0]
    width = sp.simplify(xr - xl)
    assert width.subs(Y, 0) == front_width
    assert width.subs(Y, sp.Rational(5, 2)) == sp.Rational(front_width, 2)  # the explain's example: depth 2 d0
    (y4,) = sp.solve(sp.Eq(width, sp.Rational(front_width, 4)), Y)  # width is proportional to 1/depth
    y4 = sp.Rational(y4)
    assert vy - y4 == vy * sp.Rational(1, 4)  # the second way: distance below the horizon is proportional to 1/depth
    return (int(y4.p), int(y4.q))


def xb_buoy_window(item: dict) -> tuple[int, int]:
    """q5: h(t) = 2 sin(pi t/4) + 6 for 0 <= t <= 8. Total time with h(t) >= 7, as a fraction ①/②."""
    h = 2 * sp.sin(sp.pi * t / 4) + 6
    region = _solution_interval(h - 7, 0, 8)
    total = sp.Rational(region.measure)
    return (int(total.p), int(total.q))


def xb_table_only_multi(item: dict) -> list[bool]:
    """q6: y has period 8 and the table gives y at t = 0, 2, 4, 6 (15, 20, 15, 10).
    Which can be found exactly from the table and the period alone?
    Options: y(18); y(21); y(-2); the first t > 0 with y = 17.5; y(100).
    A value is determined exactly when its t is a tabulated t plus a multiple of 8; the first time
    y = 17.5 comes from the model y = 5 sin(pi t/4) + 15 that fits the table, and it is not a table t."""
    tabulated = {0, 2, 4, 6}
    model = 5 * sp.sin(sp.pi * t / 4) + 15
    assert [model.subs(t, k) for k in (0, 2, 4, 6)] == [15, 20, 15, 10]
    first = min(sp.solveset(sp.Eq(model, sp.Rational(35, 2)), t, sp.Interval.open(0, 8)))
    on_table = lambda tt: sp.Rational(tt) % 8 in tabulated  # noqa: E731
    return [on_table(18), on_table(21), on_table(-2), on_table(first), on_table(100)]


def xb_model_from_table(item: dict) -> list[bool]:
    """q7: table t = 0,1,2,3,4 gives y = 7, 10, 7, 4, 7. Which formula fits every row?
    Options: 3 sin(pi t/2)+7; 3 sin(2 pi t)+7; 3 sin(pi t/4)+7; 6 sin(pi t/2)+7; 3 sin(pi t/2)+10."""
    rows = {0: 7, 1: 10, 2: 7, 3: 4, 4: 7}
    options = [
        3 * sp.sin(sp.pi * t / 2) + 7,
        3 * sp.sin(2 * sp.pi * t) + 7,
        3 * sp.sin(sp.pi * t / 4) + 7,
        6 * sp.sin(sp.pi * t / 2) + 7,
        3 * sp.sin(sp.pi * t / 2) + 10,
    ]
    return [all(sp.simplify(f.subs(t, k) - v) == 0 for k, v in rows.items()) for f in options]
