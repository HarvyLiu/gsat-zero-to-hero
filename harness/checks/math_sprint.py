"""Checks for the math 116-sprint item banks (src/data/items/math/s116-*.yaml).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)


def _same_set(expr, interval) -> bool:
    return sp.solveset(expr, x, domain=sp.S.Reals) == interval


# ---------- s116-real-numbers ----------

def rn_turn_distance(item: dict) -> list[bool]:
    """q-turn: points on the number line at distance 5 from 3, i.e. |x − 3| = 5.
    Options: x = 8 only; x = −2 only; x = −2 or 8; x = ±5; x = 3 ± 2.5."""
    sol = sp.solveset(sp.Eq(sp.Abs(x - 3), 5), x, domain=sp.S.Reals)
    options = [sp.FiniteSet(8), sp.FiniteSet(-2), sp.FiniteSet(-2, 8), sp.FiniteSet(-5, 5), sp.FiniteSet(sp.Rational(1, 2), sp.Rational(11, 2))]
    return [sol == o for o in options]


def rn_which_irrational(item: dict) -> list[bool | None]:
    """q1: which one is irrational: 0.(3), √9, 22/7, √5, 1.25."""
    options = [sp.Rational(1, 3), sp.sqrt(9), sp.Rational(22, 7), sp.sqrt(5), sp.Rational(5, 4)]
    return [o.is_irrational for o in options]


def rn_which_rational(item: dict) -> list[bool | None]:
    """q2: which are rational: 0.(12), π, √2.25, √8, −3/4."""
    options = [sp.Rational(12, 99), sp.pi, sp.sqrt(sp.Rational(9, 4)), sp.sqrt(8), sp.Rational(-3, 4)]
    return [o.is_rational for o in options]


def rn_repeating_27_to_fraction(item: dict) -> tuple[int, int]:
    """q3: 0.(27) = a/b in lowest terms. Built from the series 27/100 + 27/100² + …"""
    k = sp.Symbol("k", integer=True, positive=True)
    value = sp.summation(sp.Rational(27) / sp.Integer(100) ** k, (k, 1, sp.oo))
    r = sp.nsimplify(value)
    return (int(r.p), int(r.q))


def rn_integers_in_abs_lt(item: dict) -> sp.Integer:
    """q4: how many integers satisfy |x − 3| < 5 (−2 < x < 8 → −1 … 7)."""
    sol = sp.solveset(sp.Abs(x - 3) < 5, x, domain=sp.S.Reals)
    return sp.Integer(sum(1 for n in range(-100, 101) if sp.Integer(n) in sol))


def rn_integers_outside_abs_ge(item: dict) -> sp.Integer:
    """q5: how many integers do NOT satisfy |2x + 1| ≥ 7 (the solution is x ≤ −4 or x ≥ 3)."""
    sol = sp.solveset(sp.Abs(2 * x + 1) >= 7, x, domain=sp.S.Reals)
    return sp.Integer(sum(1 for n in range(-100, 101) if sp.Integer(n) not in sol))


def rn_tolerance_label(item: dict) -> list[bool]:
    """q6: a length labelled 50 ± 0.2 cm, i.e. 49.8 ≤ x ≤ 50.2. Which inequality says exactly that?
    Options: |x − 50| ≤ 0.2; |x − 0.2| ≤ 50; |x + 50| ≤ 0.2; |x − 50| ≥ 0.2; x − 50 ≤ 0.2."""
    target = sp.Interval(sp.Rational(498, 10), sp.Rational(502, 10))
    t = sp.Rational(2, 10)
    options = [sp.Abs(x - 50) <= t, sp.Abs(x - t) <= 50, sp.Abs(x + 50) <= t, sp.Abs(x - 50) >= t, x - 50 <= t]
    return [_same_set(o, target) for o in options]


def rn_sqrt7_estimate(item: dict) -> list[bool]:
    """q7: which interval contains √7: (2.4,2.5), (2.5,2.6), (2.6,2.7), (2.7,2.8), (2.8,2.9)."""
    r = sp.sqrt(7)
    bounds = [(sp.Rational(n, 10), sp.Rational(n + 1, 10)) for n in range(24, 29)]
    return [bool(lo < r) and bool(r < hi) for lo, hi in bounds]
