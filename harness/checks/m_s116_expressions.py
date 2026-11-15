"""Checks for src/data/items/math/s116-expressions.yaml (116 sprint, A-10-1 式的運算).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x")


def _equal(a, b) -> bool:
    """Exact identity test for expressions in x or radical constants."""
    return sp.simplify(sp.radsimp(sp.expand(a - b))) == 0


def ex_turn_cube_gap(item: dict) -> list[bool]:
    """q-turn: (1 + 2)^3 − (1^3 + 2^3). Options: 0, 6, 9, 18, 27."""
    value = sp.Integer(1 + 2) ** 3 - (sp.Integer(1) ** 3 + sp.Integer(2) ** 3)
    return [value == o for o in (0, 6, 9, 18, 27)]


def ex_expand_cube(item: dict) -> list[bool]:
    """q1: expand (x − 2)^3 against the five options."""
    target = sp.expand((x - 2) ** 3)
    options = [
        x**3 - 8,
        x**3 - 6 * x**2 + 12 * x - 8,
        x**3 + 6 * x**2 + 12 * x - 8,
        x**3 - 6 * x**2 - 12 * x - 8,
        x**3 - 2 * x**2 + 4 * x - 8,
    ]
    return [sp.expand(o - target) == 0 for o in options]


def ex_sum_of_cubes_value(item: dict) -> sp.Integer:
    """q2: a + b = 4, ab = 2; a^3 + b^3. a, b are the two roots of t^2 − 4t + 2 = 0."""
    t = sp.Symbol("t")
    a, b = sp.solve(t**2 - 4 * t + 2, t)
    value = sp.simplify(sp.expand(a**3 + b**3))
    assert value.is_Integer
    return value


def ex_diff_reciprocal_cubes(item: dict) -> sp.Integer:
    """q3: x − 1/x = 2; x^3 − 1/x^3. Solve x^2 − 2x − 1 = 0 and check both roots agree."""
    roots = sp.solve(x**2 - 2 * x - 1, x)
    values = {sp.simplify(sp.radsimp(sp.expand(r**3 - 1 / r**3))) for r in roots}
    assert len(values) == 1
    (value,) = values
    assert value.is_Integer
    return value


def ex_radical_statements(item: dict) -> list[bool]:
    """q4: which are true: √8 + √18 = 5√2; √9 + √16 = √25; √((−3)^2) = −3; √2·√6 = 2√3; √6/√2 = √3."""
    s = sp.sqrt
    pairs = [
        (s(8) + s(18), 5 * s(2)),
        (s(9) + s(16), s(25)),
        (s((-3) ** 2), sp.Integer(-3)),
        (s(2) * s(6), 2 * s(3)),
        (s(6) / s(2), s(3)),
    ]
    return [_equal(lhs, rhs) for lhs, rhs in pairs]


def ex_rationalize(item: dict) -> list[bool]:
    """q5: 1/(√5 − √3) against (√5+√3), (√5+√3)/2, (√5−√3)/2, (√5+√3)/8, √2."""
    s5, s3 = sp.sqrt(5), sp.sqrt(3)
    value = 1 / (s5 - s3)
    options = [s5 + s3, (s5 + s3) / 2, (s5 - s3) / 2, (s5 + s3) / 8, sp.sqrt(2)]
    return [_equal(value, o) for o in options]


def ex_rationalize_then_evaluate(item: dict) -> sp.Integer:
    """q6: x = 1/(√2 − 1); x^2 − 2x + 5."""
    xv = 1 / (sp.sqrt(2) - 1)
    value = sp.simplify(sp.radsimp(sp.expand(xv**2 - 2 * xv + 5)))
    assert value.is_Integer
    return value


def ex_fraction_subtract(item: dict) -> tuple[int, int]:
    """q7: 2/(x − 2) − 8/(x^2 − 4) written as a/(x + b); returns (a, b)."""
    r = sp.cancel(sp.Rational(2) / (x - 2) - sp.Rational(8) / (x**2 - 4))
    num, den = sp.fraction(r)
    lead = sp.Poly(den, x).LC()
    a = sp.simplify(num / lead)
    b = sp.expand(den / lead - x)
    assert sp.Poly(den, x).degree() == 1 and a.is_Integer and b.is_Integer
    return (int(a), int(b))


def ex_fraction_cancel(item: dict) -> list[bool]:
    """q8: (x^3 + 8)/(x^2 − 4) in lowest terms against the five options."""
    target = sp.cancel((x**3 + 8) / (x**2 - 4))
    options = [
        (x**2 - 2 * x + 4) / (x - 2),
        (x**2 + 2 * x + 4) / (x - 2),
        (x**2 - 2 * x + 4) / (x + 2),
        (x**3 + 2) / (x**2 - 1),
        x + 2,
    ]
    return [sp.cancel(o - target) == 0 for o in options]
