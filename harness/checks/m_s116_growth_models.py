"""Checks for src/data/items/math/s116-growth-models.yaml (116 sprint: laws of logarithms,
exponential and logarithmic functions, proportional growth models, e).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"Least number of periods" answers come from the exact rational powers, so they do not depend on the
rounded log values the explanations use.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)
n = sp.Symbol("n", positive=True, integer=True)
M, N = sp.symbols("M N", positive=True)


def _eq(a, b) -> bool:
    return bool(sp.simplify(a - b) == 0)


def _least_n(holds, limit: int = 1000) -> int:
    """Smallest positive integer k with holds(k) True."""
    for k in range(1, limit + 1):
        if holds(k):
            return k
    raise AssertionError("no k found")


def gm_turn_doubling(item: dict) -> list[bool]:
    """q-turn: 100 bacteria, doubling every hour; how many after 3 hours? Options: 300, 600, 800, 900, 106."""
    v = 100 * sp.Integer(2) ** 3
    return [v == o for o in (300, 600, 800, 900, 106)]


def gm_log3_difference(item: dict) -> list[bool]:
    """q1: log_3 54 − log_3 2. Options: 1, 2, 3, 27, log_3 52."""
    v = sp.log(54, 3) - sp.log(2, 3)
    options = [sp.Integer(1), sp.Integer(2), sp.Integer(3), sp.Integer(27), sp.log(52, 3)]
    return [_eq(v, o) for o in options]


def gm_log_laws_true(item: dict) -> list[bool]:
    """q2: for M, N > 0, which always hold? (1) log(MN) = log M + log N; (2) log(M+N) = log M + log N;
    (3) log M^3 = 3 log M; (4) log_25 125 = 3/2; (5) log_2 5 = log 2 / log 5."""
    lg = lambda t: sp.log(t, 10)  # noqa: E731
    s1 = _eq(sp.expand_log(lg(M * N), force=True), sp.expand_log(lg(M) + lg(N), force=True))
    # (2) must hold for every M, N > 0; one counterexample (M = N = 1) settles it.
    s2 = all(_eq(lg(m + k), lg(m) + lg(k)) for m, k in ((1, 1), (2, 3), (10, 10)))
    s3 = _eq(sp.expand_log(lg(M**3), force=True), 3 * lg(M))
    s4 = _eq(sp.log(125, 25), sp.Rational(3, 2))
    s5 = _eq(sp.log(5, 2), lg(2) / lg(5))
    return [s1, s2, s3, s4, s5]


def gm_exp_equation(item: dict) -> sp.Integer:
    """q3: solve 9^x = 27^(x − 2)."""
    sol = sp.solveset(sp.Eq(sp.Integer(9) ** x, sp.Integer(27) ** (x - 2)), x, domain=sp.S.Reals)
    assert len(sol) == 1
    v = next(iter(sol))
    assert v.is_Integer
    return sp.Integer(v)


def gm_graph_statements(item: dict) -> list[bool]:
    """q4: which is true? (1) y = 2^x passes through (1, 0); (2) y = (1/2)^x is increasing;
    (3) y = log x passes through (1, 0); (4) y = log x is defined for every real x; (5) 2^x can be negative."""
    s1 = _eq(sp.Integer(2) ** 1, 0)
    s2 = sp.diff(sp.Rational(1, 2) ** x, x).is_positive is True
    s3 = _eq(sp.log(1, 10), 0)
    # Defined for every real x would need a real value at x = −1; log(−1) is not real.
    s4 = sp.log(-1, 10).is_real is True
    # 2^x for real x is always positive, so "can be negative" is false.
    s5 = (sp.Integer(2) ** x).is_positive is not True
    return [s1, s2, s3, s4, s5]


def gm_growth_years(item: dict) -> sp.Integer:
    """q5: population becomes 1.2 times the previous year's each year; least n with 1.2^n > 2."""
    r = sp.Rational(12, 10)
    return sp.Integer(_least_n(lambda k: r**k > 2))


def gm_average_rate(item: dict) -> list[bool]:
    """q6: +60% in year 1, −10% in year 2; average annual rate r with (1 + r)^2 = 1.6 × 0.9.
    Options: 20%, 25%, 30%, 35%, 44%."""
    r = sp.Symbol("r", positive=True)
    sols = sp.solve(sp.Eq((1 + r) ** 2, sp.Rational(16, 10) * sp.Rational(9, 10)), r)
    assert len(sols) == 1
    v = sols[0]
    options = [sp.Rational(p, 100) for p in (20, 25, 30, 35, 44)]
    return [_eq(v, o) for o in options]


def gm_magnitude(item: dict) -> sp.Integer:
    """q7: with M = log(A/A0), an earthquake whose amplitude is 1000 times a magnitude-5 one has magnitude M."""
    A0, A5 = sp.symbols("A0 A5", positive=True)
    m5 = sp.log(A5 / A0, 10)
    assert _eq(m5.subs(A5, 10**5 * A0), 5)
    m = sp.simplify(sp.expand_log(sp.log(1000 * 10**5 * A0 / A0, 10), force=True))
    assert m.is_Integer
    return sp.Integer(m)


def gm_e_statements(item: dict) -> list[bool]:
    """q8: about (1 + 1/n)^n: (1) at n = 3 it is 64/27; (2) at n = 3 it is greater than 3;
    (3) as n grows it gets closer and closer to e; (4) as n grows it becomes arbitrarily large; (5) ln e = 1."""
    f = (1 + 1 / n) ** n
    v3 = f.subs(n, 3)
    lim = sp.limit(f, n, sp.oo)
    s1 = _eq(v3, sp.Rational(64, 27))
    s2 = bool(v3 > 3)
    s3 = _eq(lim, sp.E)
    s4 = lim == sp.oo
    s5 = _eq(sp.log(sp.E), 1)
    return [s1, s2, s3, bool(s4), s5]
