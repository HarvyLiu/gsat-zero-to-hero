"""Checks for src/data/items/math/s116-polynomial-inequalities.yaml (116 sprint: polynomial inequalities).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Solution sets come from sp.solveset over the reals and are compared with each option as an exact set,
so a missing endpoint or a missing single point (a double root) makes an option false.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)
k = sp.Symbol("k", real=True)
oo = sp.oo
R = sp.Rational


def _sol(ineq):
    return sp.solveset(ineq, x, domain=sp.S.Reals)


def _count_integers(s, lo: int = -200, hi: int = 200) -> sp.Integer:
    """Integers in the set s; every set in this bank is bounded well inside [lo, hi] (asserted)."""
    assert sp.Integer(lo) not in s and sp.Integer(hi) not in s, s
    return sp.Integer(sum(1 for n in range(lo, hi + 1) if sp.Integer(n) in s))


def pi_turn_below_axis(item: dict) -> list[bool]:
    """q-turn: y = (x − 1)(x − 4); which x give y < 0?
    Options: x < 1; 1 < x < 4; x > 4; x < 1 or x > 4; x = 1 or x = 4."""
    s = _sol((x - 1) * (x - 4) < 0)
    options = [
        sp.Interval.open(-oo, 1),
        sp.Interval.open(1, 4),
        sp.Interval.open(4, oo),
        sp.Union(sp.Interval.open(-oo, 1), sp.Interval.open(4, oo)),
        sp.FiniteSet(1, 4),
    ]
    return [s == o for o in options]


def pi_quadratic_lt(item: dict) -> list[bool]:
    """q1: solve x² − x − 12 < 0.
    Options: −3 < x < 4; −4 < x < 3; x < −3 or x > 4; x < −4 or x > 3; x > 4."""
    s = _sol(x**2 - x - 12 < 0)
    options = [
        sp.Interval.open(-3, 4),
        sp.Interval.open(-4, 3),
        sp.Union(sp.Interval.open(-oo, -3), sp.Interval.open(4, oo)),
        sp.Union(sp.Interval.open(-oo, -4), sp.Interval.open(3, oo)),
        sp.Interval.open(4, oo),
    ]
    return [s == o for o in options]


def pi_integers_quadratic_le(item: dict) -> sp.Integer:
    """q2: how many integers satisfy 3x² − 10x − 8 ≤ 0 (−2/3 ≤ x ≤ 4 → 0 … 4)."""
    return _count_integers(_sol(3 * x**2 - 10 * x - 8 <= 0))


def pi_perfect_square_ge(item: dict) -> list[bool]:
    """q3: solve −x² + 6x − 9 ≥ 0.
    Options: every real x; only x = 3; no real x; every real x except 3; x ≥ 3."""
    s = _sol(-(x**2) + 6 * x - 9 >= 0)
    options = [
        sp.S.Reals,
        sp.FiniteSet(3),
        sp.S.EmptySet,
        sp.Union(sp.Interval.open(-oo, 3), sp.Interval.open(3, oo)),
        sp.Interval(3, oo),
    ]
    return [s == o for o in options]


def pi_always_true(item: dict) -> list[bool]:
    """q4: which inequalities hold for every real x?
    x² + x + 1 > 0; x² − 4x + 4 > 0; x² − 4x + 4 ≥ 0; −x² + 2x − 3 < 0; x² + 3x − 1 > 0."""
    options = [
        x**2 + x + 1 > 0,
        x**2 - 4 * x + 4 > 0,
        x**2 - 4 * x + 4 >= 0,
        -(x**2) + 2 * x - 3 < 0,
        x**2 + 3 * x - 1 > 0,
    ]
    return [_sol(o) == sp.S.Reals for o in options]


def pi_parameter_always_positive(item: dict) -> sp.Integer:
    """q5: x² − 2kx + k + 6 > 0 for every real x; how many integers k?
    Leading coefficient 1 > 0, so the condition is: the minimum value k + 6 − k² is positive.
    Cross-checked against the discriminant condition D < 0."""
    f = x**2 - 2 * k * x + k + 6
    vertex = sp.solve(sp.diff(f, x), x)[0]
    min_value = sp.expand(f.subs(x, vertex))
    by_min = sp.solveset(min_value > 0, k, domain=sp.S.Reals)
    by_disc = sp.solveset(sp.discriminant(f, x) < 0, k, domain=sp.S.Reals)
    assert by_min == by_disc, (by_min, by_disc)
    return sp.Integer(sum(1 for n in range(-200, 201) if sp.Integer(n) in by_min))


def pi_cubic_factored_lt(item: dict) -> list[bool]:
    """q6: solve (x + 1)(x − 2)(x − 5) < 0.
    Options: x < −1 or 2 < x < 5; −1 < x < 2 or x > 5; −1 < x < 5; x < −1 or x > 5; 2 < x < 5."""
    s = _sol((x + 1) * (x - 2) * (x - 5) < 0)
    options = [
        sp.Union(sp.Interval.open(-oo, -1), sp.Interval.open(2, 5)),
        sp.Union(sp.Interval.open(-1, 2), sp.Interval.open(5, oo)),
        sp.Interval.open(-1, 5),
        sp.Union(sp.Interval.open(-oo, -1), sp.Interval.open(5, oo)),
        sp.Interval.open(2, 5),
    ]
    return [s == o for o in options]


def pi_integers_double_root_lt(item: dict) -> sp.Integer:
    """q7: how many integers satisfy (x − 2)²(x + 1)(x − 4) < 0 (−1 < x < 4 with x ≠ 2 → 0, 1, 3)."""
    return _count_integers(_sol((x - 2) ** 2 * (x + 1) * (x - 4) < 0))


def pi_negative_factor_interval(item: dict) -> list[bool]:
    """q8: solution of (3 − x)(x + 2) ≥ 0 in interval notation.
    Options: [−2, 3]; (−2, 3); (−∞, −2] ∪ [3, ∞); [−3, 2]; (−∞, −2) ∪ (3, ∞)."""
    s = _sol((3 - x) * (x + 2) >= 0)
    options = [
        sp.Interval(-2, 3),
        sp.Interval.open(-2, 3),
        sp.Union(sp.Interval(-oo, -2), sp.Interval(3, oo)),
        sp.Interval(-3, 2),
        sp.Union(sp.Interval.open(-oo, -2), sp.Interval.open(3, oo)),
    ]
    return [s == o for o in options]
