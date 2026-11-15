"""Checks for src/data/items/math/s116-periodic-graphs.yaml (116 sprint: trig graphs and periodic models).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Periods come from sp.periodicity, extremes from sp.maximum / sp.minimum over one full period, and the
"how long" answers from solveset over the stated time window, so a key cannot pass by repeating the
amplitude/period shortcut the item is testing.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)
t = sp.Symbol("t", real=True)


def _period(f, var=x) -> sp.Expr:
    p = sp.periodicity(f, var)
    if p is None:
        raise ValueError(f"{f} is not periodic")
    return sp.simplify(p)


def _extremes(f, var=x):
    """(max, min) of f over one full period [0, p]."""
    dom = sp.Interval(0, _period(f, var))
    return sp.simplify(sp.maximum(f, var, dom)), sp.simplify(sp.minimum(f, var, dom))


def _measure(s: sp.Set) -> sp.Expr:
    return sp.simplify(s.measure)


def pg_turn_sine_period(item: dict) -> list[bool]:
    """q-turn: y = sin x (x in radians) repeats every ...; options π/2, π, 2π, 360, 4π (smallest positive period)."""
    p = _period(sp.sin(x))
    options = [sp.pi / 2, sp.pi, 2 * sp.pi, sp.Integer(360), 4 * sp.pi]
    return [sp.simplify(p - o) == 0 for o in options]


def pg_period_3sin4x(item: dict) -> list[bool]:
    """q1: period of y = 3 sin(4x) − 1; options π/4, π/2, 2π, 8π, 3π/2."""
    p = _period(3 * sp.sin(4 * x) - 1)
    options = [sp.pi / 4, sp.pi / 2, 2 * sp.pi, 8 * sp.pi, 3 * sp.pi / 2]
    return [sp.simplify(p - o) == 0 for o in options]


def pg_max_min_period(item: dict) -> tuple:
    """q2: y = −2 sin(x/3) + 5: maximum ①, minimum ②, period ③π."""
    f = -2 * sp.sin(x / 3) + 5
    hi, lo = _extremes(f)
    k = sp.simplify(_period(f) / sp.pi)
    return (hi, lo, k)


def pg_statements_2sin_pix(item: dict) -> list[bool]:
    """q3: f(x) = 2 sin(πx) + 1. (1) amplitude 2; (2) period 2π; (3) minimum −1;
    (4) f(1/4) = f(5/4); (5) f(x + 4) = f(x) for every real x."""
    f = 2 * sp.sin(sp.pi * x) + 1
    hi, lo = _extremes(f)
    return [
        sp.simplify((hi - lo) / 2 - 2) == 0,
        sp.simplify(_period(f) - 2 * sp.pi) == 0,
        sp.simplify(lo + 1) == 0,
        sp.simplify(f.subs(x, sp.Rational(1, 4)) - f.subs(x, sp.Rational(5, 4))) == 0,
        sp.simplify(sp.expand_trig(f.subs(x, x + 4) - f)) == 0,
    ]


def pg_read_graph(item: dict) -> list[bool]:
    """q4: y = a sin(bx) + k (a > 0, b > 0) has a highest point (π/6, 4) and the next lowest point (π/2, −2).
    Options (a, b, k): (3, 3, 1), (3, 6, 1), (6, 3, −2), (3, 3/2, 1), (2, 3, 1).
    Each option is tested directly: f reaches 4 at π/6, −2 at π/2, those are its max and min, and no
    other extreme lies strictly between them (so the low point is the NEXT one)."""
    x1, x2, M, m = sp.pi / 6, sp.pi / 2, sp.Integer(4), sp.Integer(-2)

    def fits(a, b, k) -> bool:
        f = a * sp.sin(b * x) + k
        hi, lo = _extremes(f)
        if not (sp.simplify(hi - M) == 0 and sp.simplify(lo - m) == 0):
            return False
        if sp.simplify(f.subs(x, x1) - M) != 0 or sp.simplify(f.subs(x, x2) - m) != 0:
            return False
        between = sp.solveset(sp.Eq(f, M), x, sp.Interval.open(x1, x2)) | sp.solveset(sp.Eq(f, m), x, sp.Interval.open(x1, x2))
        return between == sp.EmptySet

    options = [(3, 3, 1), (3, 6, 1), (6, 3, -2), (3, sp.Rational(3, 2), 1), (2, 3, 1)]
    return [fits(*o) for o in options]


def pg_temperature_model(item: dict) -> tuple:
    """q5: T(t) = 20 + 6 sin(π/12 · (t − 9)) °C for 0 ≤ t ≤ 24. Time of the maximum ①② and the number of
    hours with T ≥ 23 ③."""
    T = 20 + 6 * sp.sin(sp.pi / 12 * (t - 9))
    day = sp.Interval(0, 24)
    top = sp.maximum(T, t, day)
    at_top = sp.solveset(sp.Eq(T, top), t, day)
    assert isinstance(at_top, sp.FiniteSet) and len(at_top) == 1
    (t_max,) = at_top
    warm = sp.solveset(T >= 23, t, day)
    return (str(int(t_max)), _measure(warm))


def pg_compare_sines(item: dict) -> list[bool]:
    """q6: a = sin 0.6, b = sin 2.4, c = sin 2.8 (radians). Options: a<b<c, c<a<b, b<a<c, a<c<b, c<b<a."""
    a, b, c = (sp.sin(sp.Rational(n, 10)) for n in (6, 24, 28))

    def lt(u, v) -> bool:
        return bool(sp.N(v - u, 30) > 0)

    options = [
        lt(a, b) and lt(b, c),
        lt(c, a) and lt(a, b),
        lt(b, a) and lt(a, c),
        lt(a, c) and lt(c, b),
        lt(c, b) and lt(b, a),
    ]
    return options


def pg_tan_period(item: dict) -> list[bool]:
    """q7 (Math A): period of y = tan 2x; options π/4, π/2, π, 2π, 4π."""
    p = _period(sp.tan(2 * x))
    options = [sp.pi / 4, sp.pi / 2, sp.pi, 2 * sp.pi, 4 * sp.pi]
    return [sp.simplify(p - o) == 0 for o in options]


def pg_ferris_example_sanity(item: dict | None = None) -> bool:
    """Not an item check: the chapter's worked examples, recomputed so the prose numbers stay true.
    Ferris wheel h(t) = 25 + 20 sin(π/6 · (t − 3)): h(0) = 5, h(6) = 45, above 35 m for 4 minutes in [0, 12].
    Graph example: 3 sin 2x + 2 has max 5 at π/4 and min −1 at 3π/4. Ordering sin 3 < sin 1 < sin 2."""
    h = 25 + 20 * sp.sin(sp.pi / 6 * (t - 3))
    ok = [
        h.subs(t, 0) == 5,
        h.subs(t, 6) == 45,
        _period(h, t) == 12,
        _measure(sp.solveset(h > 35, t, sp.Interval(0, 12))) == 4,
    ]
    g = 3 * sp.sin(2 * x) + 2
    ok += [g.subs(x, sp.pi / 4) == 5, g.subs(x, 3 * sp.pi / 4) == -1, _period(g) == sp.pi]
    s1, s2, s3 = sp.sin(1), sp.sin(2), sp.sin(3)
    ok += [bool(sp.N(s1 - s3) > 0), bool(sp.N(s2 - s1) > 0)]
    return all(ok)
