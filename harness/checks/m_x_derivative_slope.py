"""Checks for src/data/items/math/x-derivative-slope.yaml (分科 advanced tool: the derivative as a tangent slope).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Derivatives are computed from the limit definition (sp.limit of the difference quotient), never from the
power rule the chapter teaches, and every double-root claim is cross-checked by exact polynomial division
by (x − a)², so a check never trusts the shortcut it is testing.

_check_worked_examples() runs at import and asserts every number the lesson's worked examples print.
"""

from __future__ import annotations

import sympy as sp

x, h, t, k = sp.symbols("x h t k")


def _deriv_at(f: sp.Expr, a) -> sp.Expr:
    """f′(a) from the definition: the limit of (f(a + h) − f(a)) / h as h → 0, from both sides."""
    q = (f.subs(x, a + h) - f.subs(x, a)) / h
    left, right = sp.limit(q, h, 0, "-"), sp.limit(q, h, 0, "+")
    assert left == right, f"one-sided limits differ for {f} at {a}"
    return sp.nsimplify(right)


def _deriv_fn(f: sp.Expr) -> sp.Expr:
    """The derivative function from the definition (limit of the difference quotient at a general x)."""
    q = sp.cancel((f.subs(x, x + h) - f) / h)
    return sp.expand(sp.limit(q, h, 0))


def _tangent(f: sp.Expr, a) -> sp.Expr:
    """The tangent line at x = a, as an expression in x: y = f(a) + f′(a)(x − a)."""
    return sp.expand(f.subs(x, a) + _deriv_at(f, a) * (x - a))


def _divisible_by_square(f: sp.Expr, a) -> bool:
    """(x − a)² divides f exactly (exact division, independent of derivatives)."""
    _, r = sp.div(sp.Poly(f, x), sp.Poly((x - a) ** 2, x))
    return r.is_zero


def _check_worked_examples() -> None:
    # Section 1: y = x² at x = 1. Secant slope (f(1 + t) − f(1)) / t = 2 + t; table values; limit 2.
    f = x**2
    sec = sp.cancel((f.subs(x, 1 + t) - f.subs(x, 1)) / t)
    assert sp.expand(sec - (2 + t)) == 0
    for tv, val in ((1, 3), (sp.Rational(1, 10), sp.Rational(21, 10)), (sp.Rational(1, 100), sp.Rational(201, 100)), (-sp.Rational(1, 10), sp.Rational(19, 10))):
        assert sec.subs(t, tv) == val
    assert _deriv_at(f, 1) == 2 and _tangent(f, 1) == 2 * x - 1
    # Velocity perspective: s(t) = 5t², average speed on [2, 2 + h] is 20 + 5h, instantaneous 20.
    s = 5 * x**2
    assert sp.expand(sp.cancel((s.subs(x, 2 + h) - s.subs(x, 2)) / h) - (20 + 5 * h)) == 0
    assert _deriv_at(s, 2) == 20
    # Section 2: f(x) = x³ − 2x + 1 = (x − 1)³ + 3(x − 1)² + (x − 1); f′(1) = 1, tangent y = x − 1.
    g = x**3 - 2 * x + 1
    assert sp.expand(g - ((x - 1) ** 3 + 3 * (x - 1) ** 2 + (x - 1))) == 0
    assert _deriv_at(g, 1) == 1 and _tangent(g, 1) == x - 1
    # Synthetic division perspective: g = (x − 1)(x² + x − 1) + 0, q(1) = 1; second division remainder 1.
    q1, r1 = sp.div(sp.Poly(g, x), sp.Poly(x - 1, x))
    assert q1.as_expr() == x**2 + x - 1 and r1.is_zero and q1.as_expr().subs(x, 1) == 1
    q2, r2 = sp.div(q1, sp.Poly(x - 1, x))
    assert q2.as_expr() == x + 2 and r2.as_expr() == 1
    q3, r3 = sp.div(q2, sp.Poly(x - 1, x))
    assert q3.as_expr() == 1 and r3.as_expr() == 3
    # Section 3: power rule for n = 2, 3 and the general cubic, from the definition.
    a_, b_, c_, d_ = sp.symbols("a b c d")
    assert _deriv_fn(x**3) == 3 * x**2 and _deriv_fn(x**2) == 2 * x and _deriv_fn(sp.Integer(5)) == 0
    assert sp.expand(_deriv_fn(a_ * x**3 + b_ * x**2 + c_ * x + d_) - (3 * a_ * x**2 + 2 * b_ * x + c_)) == 0
    # f(x) = x³ − 6x² + 9x + 1: f′(x) = 3x² − 12x + 9, f′(2) = −3, f′(1) = f′(3) = 0, f(1) = 5, f(3) = 1.
    p = x**3 - 6 * x**2 + 9 * x + 1
    assert _deriv_fn(p) == 3 * x**2 - 12 * x + 9
    assert _deriv_at(p, 2) == -3 and _deriv_at(p, 1) == 0 and _deriv_at(p, 3) == 0
    assert (p.subs(x, 1), p.subs(x, 3), p.subs(x, 2)) == (5, 1, 3)
    # Graph: y = x³ − 3x, f′(x) = 3x² − 3, f′(1.5) = 3.75.
    assert _deriv_fn(x**3 - 3 * x) == 3 * x**2 - 3 and _deriv_at(x**3 - 3 * x, sp.Rational(3, 2)) == sp.Rational(15, 4)
    # Symmetric difference check: (1.1³ − 0.9³)/0.2 = 3.01, and for x³ in general 3a² + h².
    hv = sp.Rational(1, 10)
    assert ((1 + hv) ** 3 - (1 - hv) ** 3) / (2 * hv) == sp.Rational(301, 100)
    assert (sp.Rational(11, 10) ** 3, sp.Rational(9, 10) ** 3) == (sp.Rational(1331, 1000), sp.Rational(729, 1000))
    av = sp.Symbol("a")
    assert sp.expand(((av + h) ** 3 - (av - h) ** 3) / (2 * h) - (3 * av**2 + h**2)) == 0
    # Section 4: tangent to y = x² − 4x + 5 with slope 2 — derivative way and discriminant way.
    par = x**2 - 4 * x + 5
    xs = sp.solve(sp.Eq(_deriv_fn(par), 2), x)
    assert xs == [3] and par.subs(x, 3) == 2 and _tangent(par, 3) == 2 * x - 4
    disc = sp.discriminant(sp.expand(par - (2 * x + k)), x)
    assert sp.expand(disc - (16 + 4 * k)) == 0 and sp.solve(disc, k) == [-4]
    # Section 5: x³ − 3x + k has a double root exactly when k = ±2 — derivative way and coefficient way.
    cub = x**3 - 3 * x + k
    roots_fp = sp.solve(sp.Eq(_deriv_fn(cub), 0), x)
    assert sorted(roots_fp) == [-1, 1]
    ks = sorted(sp.solve(cub.subs(x, r0), k)[0] for r0 in roots_fp)
    assert ks == [-2, 2]
    assert sp.expand((x - 1) ** 2 * (x + 2) - (x**3 - 3 * x + 2)) == 0
    assert sp.expand((x + 1) ** 2 * (x - 2) - (x**3 - 3 * x - 2)) == 0
    r_, s_ = sp.symbols("r s")
    coeff = sp.Poly(sp.expand((x - r_) ** 2 * (x - s_) - (x**3 - 3 * x + k)), x).coeffs()
    sols = sp.solve(coeff, [r_, s_, k], dict=True)
    assert sorted((sl[r_], sl[s_], sl[k]) for sl in sols) == [(-1, 2, -2), (1, -2, 2)]
    # Tangent to y = x³ at x = a is y = 3a²x − 2a³, and x³ − (3a²x − 2a³) = (x − a)²(x + 2a); at a = 1: y = 3x − 2, meets again at (−2, −8).
    assert sp.expand(_tangent(x**3, av) - (3 * av**2 * x - 2 * av**3)) == 0
    assert sp.expand(x**3 - (3 * av**2 * x - 2 * av**3) - (x - av) ** 2 * (x + 2 * av)) == 0
    assert _tangent(x**3, 1) == 3 * x - 2 and (-2) ** 3 == -8
    # comparing coefficients: (x − 1)²(x − s) has x² coefficient −(2 + s) = 0 → s = −2
    s0 = sp.Symbol("s0")
    assert sp.solve(sp.Poly(sp.expand((x - 1) ** 2 * (x - s0)), x).coeff_monomial(x**2), s0) == [-2]
    # symmetric secant is exact for a quadratic: (f(a + h) − f(a − h)) / (2h) = f′(a)
    A2, B2, C2 = sp.symbols("A2 B2 C2")
    quad = A2 * x**2 + B2 * x + C2
    assert sp.simplify((quad.subs(x, av + h) - quad.subs(x, av - h)) / (2 * h) - _deriv_fn(quad).subs(x, av)) == 0
    # TryIt: y = x³ + 2x at x = −1, derivative way and x = t − 1 expansion way both give y = 5x + 2
    ty = x**3 + 2 * x
    assert _tangent(ty, -1) == 5 * x + 2
    ex = sp.Poly(sp.expand(ty.subs(x, t - 1)), t)
    assert sp.expand(ex.coeff_monomial(1) + ex.coeff_monomial(t) * (x + 1)) == 5 * x + 2
    # Later perspective: (x − 1)³ = x³ − 3x² + 3x − 1, f′(1) = 0, f″(1) = 0.
    tri = x**3 - 3 * x**2 + 3 * x - 1
    assert sp.expand((x - 1) ** 3 - tri) == 0
    assert _deriv_at(tri, 1) == 0 and _deriv_fn(_deriv_fn(tri)).subs(x, 1) == 0


_check_worked_examples()


# ---------- x-derivative-slope ----------

def ds_turn_secant(item: dict) -> list[bool]:
    """q-turn: slope of the secant of y = x² through A(1, 1) and B(1 + t, (1 + t)²), t ≠ 0.
    Options: t; 2 + t; 2; 1 + 2t; (1 + t)²."""
    f = x**2
    sec = sp.cancel((f.subs(x, 1 + t) - f.subs(x, 1)) / t)
    options = [t, 2 + t, sp.Integer(2), 1 + 2 * t, (1 + t) ** 2]
    return [sp.expand(sec - o) == 0 for o in options]


def ds_derivative_fill(item: dict) -> int:
    """q1: f(x) = 2x³ − 5x² + x − 4, the value f′(−1)."""
    return _deriv_at(2 * x**3 - 5 * x**2 + x - 4, -1)


def ds_limit_value(item: dict) -> list[bool]:
    """q2: lim_{h→0} ((2 + h)³ − 8) / h. Options: 0; 4; 8; 12; does not exist."""
    q = ((2 + h) ** 3 - 8) / h
    left, right = sp.limit(q, h, 0, "-"), sp.limit(q, h, 0, "+")
    exists = left == right and bool(right.is_finite)
    return [exists and right == v for v in (0, 4, 8, 12)] + [not exists]


def ds_tangent_fill(item: dict) -> tuple:
    """q3: tangent of y = x³ − 4x + 3 at x = 2 written y = mx + b → (m, b)."""
    line = sp.Poly(_tangent(x**3 - 4 * x + 3, 2), x)
    return (line.coeff_monomial(x), line.coeff_monomial(1))


def ds_statements(item: dict) -> list[bool]:
    """q4: statements about f(x) = x³ − 3x² + 4.
    (1) f′(x) = 3x² − 6x; (2) (x − 2)² is a factor of f(x); (3) the tangent at x = 0 is horizontal;
    (4) the tangent at x = 1 has slope −2; (5) (x + 1)² is a factor of f(x)."""
    f = x**3 - 3 * x**2 + 4
    return [
        sp.expand(_deriv_fn(f) - (3 * x**2 - 6 * x)) == 0,
        _divisible_by_square(f, 2),
        _deriv_at(f, 0) == 0,
        _deriv_at(f, 1) == -2,
        _divisible_by_square(f, -1),
    ]


def ds_double_root_fill(item: dict) -> tuple:
    """q5: (x + 2)² divides x³ + ax + b → (a, b). Solved from the remainder of exact division by (x + 2)²."""
    a, b = sp.symbols("a b")
    _, r = sp.div(sp.Poly(x**3 + a * x + b, x), sp.Poly((x + 2) ** 2, x))
    sol = sp.solve(sp.Poly(r.as_expr(), x).coeffs(), [a, b], dict=True)
    assert len(sol) == 1
    av, bv = sol[0][a], sol[0][b]
    # cross-check with the chapter's criterion f(−2) = f′(−2) = 0
    g = x**3 + av * x + bv
    assert g.subs(x, -2) == 0 and _deriv_at(g, -2) == 0
    return (av, bv)


def ds_other_intersection(item: dict) -> list[bool]:
    """q6: the tangent of y = x³ + x² at x = 1 meets the curve again; the other x.
    Options: 1; −1; −3; 3; −2."""
    f = x**3 + x**2
    roots = sp.roots(sp.Poly(f - _tangent(f, 1), x))
    assert roots.get(sp.Integer(1)) == 2  # the tangent point is a double root
    others = [r0 for r0 in roots if r0 != 1]
    assert len(others) == 1
    # explanation's coefficient way: (x − 1)²(x − s) has x² coefficient −(2 + s) = 1 → s = −3
    s1 = sp.Symbol("s1")
    assert sp.solve(sp.Eq(sp.Poly(sp.expand((x - 1) ** 2 * (x - s1)), x).coeff_monomial(x**2), 1), s1) == [others[0]]
    return [others[0] == v for v in (1, -1, -3, 3, -2)]


def ds_parallel_tangent(item: dict) -> list[bool]:
    """q7: the tangent of y = x² + 2x − 1 parallel to y = 4x + 7 is y = 4x + c; the value c.
    Computed by the discriminant (the line y = 4x + c meets the parabola exactly once).
    Options: −3; −2; 0; 2; 7."""
    c = sp.Symbol("c")
    disc = sp.discriminant(sp.expand(x**2 + 2 * x - 1 - (4 * x + c)), x)
    cs = sp.solve(disc, c)
    assert len(cs) == 1
    # cross-check with the derivative: slope 4 at the tangent point
    x0 = sp.solve(sp.Eq(_deriv_fn(x**2 + 2 * x - 1), 4), x)[0]
    assert _tangent(x**2 + 2 * x - 1, x0) == 4 * x + cs[0]
    return [cs[0] == v for v in (-3, -2, 0, 2, 7)]
