"""Checks for src/data/items/math/s116-exponents.yaml (116 sprint, N-10-3).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational
x = sp.Symbol("x", positive=True)
a = sp.Symbol("a", positive=True)


def ex_turn_nine_half(item: dict) -> list[bool]:
    """q-turn: if a^r · a^s = a^(r+s) holds for fractions, 9^(1/2) · 9^(1/2) = 9^1, so 9^(1/2) is the
    positive y with y² = 9. Options: 3, 4.5, 18, 81, 1/3."""
    y = sp.Symbol("y", positive=True)
    (sol,) = sp.solve(sp.Eq(y**2, sp.Integer(9) ** (R(1, 2) + R(1, 2))), y)
    options = [sp.Integer(3), R(9, 2), sp.Integer(18), sp.Integer(81), R(1, 3)]
    return [sp.simplify(sol - o) == 0 for o in options]


def ex_value_27_neg_two_thirds(item: dict) -> list[bool]:
    """q1: 27^(−2/3). Options: 1/9, −9, −18, 9, 1/18."""
    v = sp.Integer(27) ** R(-2, 3)
    options = [R(1, 9), sp.Integer(-9), sp.Integer(-18), sp.Integer(9), R(1, 18)]
    return [sp.simplify(v - o) == 0 for o in options]


def _identity(lhs, rhs) -> bool:
    """True when lhs = rhs for every a > 0: symbolic zero difference, cross-checked at sample points.
    A false statement must also fail at some sample point, so the verdict is never a guess."""
    symbolic = sp.simplify(sp.powsimp(lhs - rhs, force=False)) == 0
    samples = [sp.Integer(2), sp.Integer(5), R(1, 3)]
    numeric = all(abs(sp.N((lhs - rhs).subs(a, s), 30)) < 1e-25 for s in samples)
    if symbolic != numeric:
        raise ValueError(f"symbolic and numeric verdicts disagree for {lhs} = {rhs}")
    return symbolic


def ex_laws_which_true(item: dict) -> list[bool]:
    """q2 (a > 0): a^(1/2)·a^(1/3) = a^(5/6); (a^(2/3))^(3/4) = a^(1/2); a^(1/2) + a^(1/2) = a;
    a^(3/4) / a^(1/4) = a^3; a^(−1/2) = 1/√a."""
    h = R(1, 2)
    pairs = [
        (a**h * a ** R(1, 3), a ** R(5, 6)),
        ((a ** R(2, 3)) ** R(3, 4), a**h),
        (a**h + a**h, a),
        (a ** R(3, 4) / a ** R(1, 4), a**3),
        (a ** (-h), 1 / sp.sqrt(a)),
    ]
    return [_identity(lhs, rhs) for lhs, rhs in pairs]


def ex_sum_from_half_powers(item: dict) -> sp.Integer:
    """q3: x > 0 and x^(1/2) + x^(−1/2) = 4; find x + x^(−1). Solve for every such x and require one value."""
    sols = sp.solve(sp.Eq(x ** R(1, 2) + x ** R(-1, 2), 4), x)
    values = {sp.nsimplify(sp.simplify(s + 1 / s)) for s in sols}
    if len(sols) == 0 or len(values) != 1:
        raise ValueError(f"expected one value of x + 1/x, got {values} from {sols}")
    return values.pop()


def ex_order_three_roots(item: dict) -> list[bool]:
    """q4: order 2^(1/3), 3^(1/4), 5^(1/6). Options (left to right, increasing):
    (A,B,C), (A,C,B), (B,A,C), (C,A,B), (C,B,A) with A = 2^(1/3), B = 3^(1/4), C = 5^(1/6)."""
    A, B, C = sp.Integer(2) ** R(1, 3), sp.Integer(3) ** R(1, 4), sp.Integer(5) ** R(1, 6)
    orders = [(A, B, C), (A, C, B), (B, A, C), (C, A, B), (C, B, A)]
    return [bool(p < q) and bool(q < r) for p, q, r in orders]


def ex_largest_power_of_two(item: dict) -> list[bool]:
    """q5: the largest of 2^√3, 2^1.7, 2^(7/4), 4^0.8, (1/2)^(−1.8)."""
    options = [
        sp.Integer(2) ** sp.sqrt(3),
        sp.Integer(2) ** R(17, 10),
        sp.Integer(2) ** R(7, 4),
        sp.Integer(4) ** R(8, 10),
        R(1, 2) ** R(-18, 10),
    ]
    return [all(bool(v > w) for j, w in enumerate(options) if j != i) for i, v in enumerate(options)]


def _min_over_positive(f, var) -> sp.Basic:
    """Minimum of f on var > 0 by calculus: the only critical point, confirmed by f'' > 0 there and by
    f growing without bound at both ends of (0, ∞)."""
    crit = [c for c in sp.solve(sp.diff(f, var), var) if c.is_positive]
    if len(crit) != 1:
        raise ValueError(f"expected one positive critical point, got {crit}")
    c = crit[0]
    if not sp.diff(f, var, 2).subs(var, c).is_positive:
        raise ValueError("critical point is not a minimum")
    if sp.limit(f, var, 0, "+") != sp.oo or sp.limit(f, var, sp.oo) != sp.oo:
        raise ValueError("f does not blow up at both ends, so the local minimum may not be global")
    return sp.simplify(f.subs(var, c))


def ex_min_2x_plus_8_over_x(item: dict) -> sp.Basic:
    """q6: x > 0, the minimum of 2x + 8/x."""
    return _min_over_positive(2 * x + 8 / x, x)


def ex_min_a_plus_2b(item: dict) -> sp.Basic:
    """q7: a, b > 0 with ab = 50; the minimum of a + 2b. Substitute a = 50/b."""
    b = sp.Symbol("b", positive=True)
    return _min_over_positive(50 / b + 2 * b, b)
