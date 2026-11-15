"""Checks for src/data/items/math/s116-polynomial-division.yaml (116 sprint: polynomial division).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Quotients and remainders come from sp.div (exact polynomial division), and every use of the remainder
theorem is cross-checked against that division, so a check never trusts the theorem it is testing.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x")


def _qr(f, g):
    q, r = sp.div(sp.Poly(f, x), sp.Poly(g, x))
    return q, r


def pd_turn_value(item: dict) -> list[bool]:
    """q-turn: f(x) = x³ − 2x + 5, the value f(2). Options 1, 5, 9, 13, 17."""
    f = x**3 - 2 * x + 5
    v = f.subs(x, 2)
    _, r = _qr(f, x - 2)
    assert r.as_expr() == v  # the dialogue's claim: dividing by x − 2 leaves the same 9
    return [v == o for o in (1, 5, 9, 13, 17)]


def pd_possible_remainder(item: dict) -> list[bool]:
    """q1: which could be the remainder of some f(x) divided by x² − 1?
    A remainder must be 0 or have degree < 2. Options x² − 1, 2x + 3, x² + x, x³, 3x² − 2."""
    divisor = sp.Poly(x**2 - 1, x)
    options = [x**2 - 1, 2 * x + 3, x**2 + x, x**3, 3 * x**2 - 2]
    out = []
    for o in options:
        p = sp.Poly(o, x)
        ok = p.is_zero or p.degree() < divisor.degree()
        if ok:
            # realisable: f = (x² − 1)·x + o leaves exactly o
            _, r = _qr(divisor.as_expr() * x + o, divisor.as_expr())
            assert sp.expand(r.as_expr() - o) == 0
        out.append(ok)
    return out


def pd_long_division_remainder(item: dict) -> tuple:
    """q2: remainder of x³ + 2x² − 3x + 4 divided by x² + x − 2, written ax + b → cells of a then b."""
    _, r = _qr(x**3 + 2 * x**2 - 3 * x + 4, x**2 + x - 2)
    a, b = r.as_expr().coeff(x, 1), r.as_expr().coeff(x, 0)
    return (a, b)


def pd_synthetic_quotient(item: dict) -> tuple:
    """q3: x³ − 4x² + 2x + 5 divided by x − 3; quotient x² + ax + b → (a, b)."""
    q, _ = _qr(x**3 - 4 * x**2 + 2 * x + 5, x - 3)
    qe = q.as_expr()
    assert qe.coeff(x, 2) == 1
    return (qe.coeff(x, 1), qe.coeff(x, 0))


def pd_remainder_by_x_plus_2(item: dict) -> list[bool]:
    """q4: remainder of x⁴ + 2x³ − x + 3 divided by x + 2. Options −5, 3, 5, 13, 33."""
    f = x**4 + 2 * x**3 - x + 3
    _, r = _qr(f, x + 2)
    assert r.as_expr() == f.subs(x, -2)
    return [r.as_expr() == o for o in (-5, 3, 5, 13, 33)]


def pd_factor_unknown_k(item: dict) -> sp.Integer:
    """q5: x³ + kx² − 4x + 3 has the factor x − 3; find k by solving for a zero remainder."""
    k = sp.Symbol("k")
    _, r = sp.div(sp.Poly(x**3 + k * x**2 - 4 * x + 3, x), sp.Poly(x - 3, x))
    (root,) = sp.solve(sp.Eq(r.as_expr(), 0), k)
    _, r2 = _qr(x**3 + root * x**2 - 4 * x + 3, x - 3)
    assert r2.is_zero
    return sp.Integer(root)


def pd_remainder_two_conditions(item: dict) -> tuple:
    """q6: f ÷ (x − 3) leaves 10, f ÷ (x + 1) leaves −2; remainder of f ÷ (x − 3)(x + 1) is ax + b → (a, b).
    Solved from r(3) = 10, r(−1) = −2, then confirmed on a concrete f with that remainder."""
    a, b = sp.symbols("a b")
    sol = sp.solve([sp.Eq(3 * a + b, 10), sp.Eq(-a + b, -2)], [a, b], dict=True)[0]
    rem = sol[a] * x + sol[b]
    g = (x - 3) * (x + 1)
    f = sp.expand(g * (x**2 + 5) + rem)
    assert _qr(f, x - 3)[1].as_expr() == 10 and _qr(f, x + 1)[1].as_expr() == -2
    assert sp.expand(_qr(f, g)[1].as_expr() - rem) == 0
    return (sol[a], sol[b])


def pd_which_factors(item: dict) -> list[bool]:
    """q7: which are factors of x³ − 7x + 6? Options x − 1, x + 1, x − 2, x + 3, x − 3 (exact division)."""
    f = x**3 - 7 * x + 6
    return [_qr(f, d)[1].is_zero for d in (x - 1, x + 1, x - 2, x + 3, x - 3)]


def pd_powers_of_x_minus_2(item: dict) -> tuple:
    """q8: x³ − 4x² + 3x + 1 = (x − 2)³ + a(x − 2)² + b(x − 2) + c → cells of a, b, c.
    Coefficients read off by substituting x = t + 2 and expanding in t."""
    t = sp.Symbol("t")
    p = sp.Poly(sp.expand((x**3 - 4 * x**2 + 3 * x + 1).subs(x, t + 2)), t)
    assert p.coeff_monomial(t**3) == 1
    return (p.coeff_monomial(t**2), p.coeff_monomial(t), p.coeff_monomial(1))
