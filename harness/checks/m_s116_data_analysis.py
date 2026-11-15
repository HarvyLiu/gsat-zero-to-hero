"""Checks for src/data/items/math/s116-data-analysis.yaml (116 sprint: data analysis, D-10-2).

Each function recomputes its item's answer from the data with SymPy; none reads item["answer"].
Standard deviation divides by n (the definition the chapter uses). Percentiles use the definition
written in the item's stem.
"""

from __future__ import annotations

import math

import sympy as sp


def _mean(d) -> sp.Expr:
    return sp.Rational(1, len(d)) * sum(sp.nsimplify(v) for v in d)


def _sd(d) -> sp.Expr:
    m = _mean(d)
    return sp.sqrt(sp.Rational(1, len(d)) * sum((sp.nsimplify(v) - m) ** 2 for v in d))


def _r(xs, ys) -> sp.Expr:
    mx, my = _mean(xs), _mean(ys)
    sxy = sum((sp.nsimplify(a) - mx) * (sp.nsimplify(b) - my) for a, b in zip(xs, ys))
    sxx = sum((sp.nsimplify(a) - mx) ** 2 for a in xs)
    syy = sum((sp.nsimplify(b) - my) ** 2 for b in ys)
    return sp.simplify(sxy / sp.sqrt(sxx * syy))


def _least_squares(xs, ys) -> tuple[sp.Expr, sp.Expr]:
    """(slope, intercept) minimising the sum of squared vertical errors, solved from the normal
    equations (not from the r * sigma_y / sigma_x formula)."""
    a, b = sp.symbols("a b")
    sse = sum((sp.nsimplify(yv) - (a * sp.nsimplify(xv) + b)) ** 2 for xv, yv in zip(xs, ys))
    sol = sp.solve([sp.diff(sse, a), sp.diff(sse, b)], [a, b], dict=True)[0]
    return sp.simplify(sol[a]), sp.simplify(sol[b])


def _percentile(data, k: int) -> sp.Expr:
    """The stem's definition: sort; if n*k/100 is an integer m, average the m-th and (m+1)-th values;
    otherwise take the value in position ceil(n*k/100)."""
    s = sorted(data)
    pos = sp.Rational(len(s) * k, 100)
    if pos.is_integer:
        m = int(pos)
        return sp.Rational(s[m - 1] + s[m], 2)
    return sp.Integer(s[math.ceil(pos) - 1])


def _median(data) -> sp.Expr:
    s = sorted(data)
    n = len(s)
    return sp.Integer(s[n // 2]) if n % 2 else sp.Rational(s[n // 2 - 1] + s[n // 2], 2)


def da_turn_spread(item: dict) -> list[bool]:
    """q-turn: A = 68, 70, 72; B = 50, 70, 90. Options: A larger; equal; B larger and twice A;
    B larger and 10 times A."""
    a, b = [68, 70, 72], [50, 70, 90]
    assert _mean(a) == _mean(b)
    sa, sb = _sd(a), _sd(b)
    ratio = sp.simplify(sb / sa)
    return [bool(sa > sb), sa == sb, bool(sb > sa) and ratio == 2, bool(sb > sa) and ratio == 10]


def da_sd_value(item: dict) -> sp.Integer:
    """q1: standard deviation of 11, 14, 18, 20, 22 (dividing by n)."""
    s = _sd([11, 14, 18, 20, 22])
    assert s.is_integer
    return sp.Integer(s)


def da_linear_transform(item: dict) -> list[bool]:
    """q2: X has mean 64 and SD 8; Y = 1.5X - 20; W = 100 - X.
    (1) mean of Y is 76; (2) SD of Y is 12; (3) variance of Y is 96; (4) SD of W is -8;
    (5) every student's standardized score is the same in X and Y.
    Checked on two different data sets with mean 64 and SD 8; both must give the same truth values."""
    results = []
    for xs in ([56, 72], [56, 64, 64, 72, 64 - 8 * sp.sqrt(2), 64 + 8 * sp.sqrt(2)]):
        xs = [sp.nsimplify(v) for v in xs]
        assert _mean(xs) == 64 and sp.simplify(_sd(xs) - 8) == 0
        ys = [sp.Rational(3, 2) * v - 20 for v in xs]
        ws = [100 - v for v in xs]
        zx = [(v - _mean(xs)) / _sd(xs) for v in xs]
        zy = [(v - _mean(ys)) / _sd(ys) for v in ys]
        results.append(
            [
                sp.simplify(_mean(ys) - 76) == 0,
                sp.simplify(_sd(ys) - 12) == 0,
                sp.simplify(_sd(ys) ** 2 - 96) == 0,
                sp.simplify(_sd(ws) + 8) == 0,
                all(sp.simplify(p - q) == 0 for p, q in zip(zx, zy)),
            ]
        )
    assert results[0] == results[1]
    return results[0]


def da_percentile(item: dict) -> sp.Integer:
    """q3: the 70th percentile of 42, 35, 50, 61, 38, 47, 54, 40, 58, 44 by the stem's definition."""
    p = _percentile([42, 35, 50, 61, 38, 47, 54, 40, 58, 44], 70)
    assert p.is_integer
    return sp.Integer(p)


def da_r_transform(item: dict) -> list[bool]:
    """q4: r(X, Y) = 0.6, U = -2X + 5, V = 3Y - 1; r(U, V)? Options: 0.6, -0.6, -3.6, -0.2, 0.36.
    Built on a data set with r exactly 3/5: z_x = (1, 1, -1, -1), z_y = 0.6 z_x + 0.8 w, w = (1, -1, 1, -1)."""
    zx = [1, 1, -1, -1]
    w = [1, -1, 1, -1]
    xs = [sp.Integer(v) for v in zx]
    ys = [sp.Rational(3, 5) * a + sp.Rational(4, 5) * b for a, b in zip(zx, w)]
    assert _r(xs, ys) == sp.Rational(3, 5)
    us = [-2 * v + 5 for v in xs]
    vs = [3 * v - 1 for v in ys]
    ruv = _r(us, vs)
    opts = [sp.Rational(3, 5), sp.Rational(-3, 5), sp.Rational(-18, 5), sp.Rational(-1, 5), sp.Rational(9, 25)]
    return [sp.simplify(ruv - o) == 0 for o in opts]


def da_regression_predict(item: dict) -> sp.Integer:
    """q5: mu_X = 10, sigma_X = 2, mu_Y = 50, sigma_Y = 6, r = 0.5; the regression line's value at x = 14.
    Built on a data set with exactly these statistics, then fitted by least squares."""
    zx = [1, 1, -1, -1]
    w = [1, -1, 1, -1]
    r = sp.Rational(1, 2)
    xs = [10 + 2 * sp.Integer(a) for a in zx]
    ys = [50 + 6 * (r * a + sp.sqrt(1 - r**2) * b) for a, b in zip(zx, w)]
    assert _mean(xs) == 10 and _sd(xs) == 2 and sp.simplify(_mean(ys) - 50) == 0
    assert sp.simplify(_sd(ys) - 6) == 0 and sp.simplify(_r(xs, ys) - r) == 0
    a, b = _least_squares(xs, ys)
    v = sp.simplify(a * 14 + b)
    assert v.is_integer
    return sp.Integer(v)


def da_scatter_statements(item: dict) -> list[bool]:
    """q6: data (2, 9), (4, 7), (6, 8), (8, 4), (10, 2).
    (1) negative correlation; (2) regression slope -0.85; (3) the line passes (6, 6);
    (4) r equals the regression slope; (5) adding 10 to every y makes r larger."""
    xs, ys = [2, 4, 6, 8, 10], [9, 7, 8, 4, 2]
    r = _r(xs, ys)
    a, b = _least_squares(xs, ys)
    r_shift = _r(xs, [v + 10 for v in ys])
    return [
        bool(r < 0),
        a == sp.Rational(-17, 20),
        sp.simplify(a * 6 + b - 6) == 0,
        sp.simplify(r - a) == 0,
        bool(r_shift > r),
    ]


def da_standard_score(item: dict) -> sp.Integer:
    """q7: physics 67 with mu 58, sigma 6; the chemistry score (mu 45, sigma 14) with the same z."""
    z = sp.Rational(67 - 58, 6)
    c = sp.symbols("c")
    (sol,) = sp.solve(sp.Eq((c - 45) / 14, z), c)
    assert sol.is_integer
    return sp.Integer(sol)


def da_choose_statistic(item: dict) -> list[bool]:
    """q8: salaries 3, 3, 4, 4, 4, 5, 5, 6, 47.
    (1) mean is 4; (2) median is 9; (3) the mean is higher than 8 of the 9 salaries;
    (4) without 47 the median becomes 5; (5) without 47 the SD gets larger."""
    d = [3, 3, 4, 4, 4, 5, 5, 6, 47]
    rest = [v for v in d if v != 47]
    m = _mean(d)
    return [
        m == 4,
        _median(d) == 9,
        sum(1 for v in d if v < m) == 8,
        _median(rest) == 5,
        bool(_sd(rest) > _sd(d)),
    ]
