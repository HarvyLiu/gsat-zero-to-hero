"""Checks for src/data/items/math/s116-cubic-functions.yaml (116 sprint: graphs of cubic functions).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Symmetry centres come from the defining identity f(h + t) + f(h − t) = 2k (solved for h and k), not from
the h = −b/(3a) shortcut the chapter teaches; approximating lines come from a series expansion at x = h.
"""

from __future__ import annotations

import sympy as sp

x, t, h, k, p = sp.symbols("x t h k p", real=True)


def _centre(f: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """The unique (h, k) with f(h + t) + f(h − t) ≡ 2k, found by solving the coefficient equations in t."""
    expr = sp.expand(f.subs(x, h + t) + f.subs(x, h - t) - 2 * k)
    eqs = sp.Poly(expr, t).coeffs()
    sols = sp.solve(eqs, [h, k], dict=True)
    assert len(sols) == 1, f"expected one symmetry centre for {f}, got {sols}"
    return sols[0][h], sols[0][k]


def _symmetric_about_point(f: sp.Expr, h0, k0) -> bool:
    return sp.expand(f.subs(x, h0 + t) + f.subs(x, h0 - t) - 2 * k0) == 0


def _symmetric_about_vertical(f: sp.Expr, h0) -> bool:
    return sp.expand(f.subs(x, h0 + t) - f.subs(x, h0 - t)) == 0


def _line_at(f: sp.Expr, h0) -> sp.Expr:
    """The approximating line at x = h0: drop the (x − h0)² and higher terms of the expansion."""
    return sp.series(f, x, h0, 2).removeO()


# ---------- s116-cubic-functions ----------

def cf_turn_odd_cubic(item: dict) -> list[bool]:
    """q-turn: the graph of y = x³ − 3x is symmetric about which: the y-axis; the x-axis; the origin;
    the line x = 1; the line y = x."""
    f = x**3 - 3 * x
    y = sp.Symbol("y", real=True)
    g = y - f  # the graph as g(x, y) = 0
    # A function graph is symmetric about the x-axis only if (x0, y0) and (x0, −y0) are both on it;
    # test at a point of the graph with y0 ≠ 0.
    x0 = sp.Integer(2)
    y0 = f.subs(x, x0)
    x_axis = y0 == 0 or sp.simplify(g.subs({x: x0, y: -y0})) == 0
    # Symmetry about y = x: swap the coordinates of a point on the graph and test it.
    pts = [(sp.Integer(n), f.subs(x, n)) for n in range(-3, 4)]
    diag = all(sp.simplify(g.subs({x: b, y: a}, simultaneous=True)) == 0 for a, b in pts)
    return [
        _symmetric_about_vertical(f, 0),
        bool(x_axis),
        _symmetric_about_point(f, 0, 0),
        _symmetric_about_vertical(f, 1),
        bool(diag),
    ]


def cf_centre_fill(item: dict) -> tuple[int, int]:
    """q1: the symmetry centre (h, k) of y = x³ + 3x² − x + 2."""
    hc, kc = _centre(x**3 + 3 * x**2 - x + 2)
    return (int(hc), int(kc))


def cf_translate_p(item: dict) -> list[bool]:
    """q2: f(x) = 2x³ − 12x² + 19x − 4 is a translate of y = 2x³ + px. Options for p: −12, −5, 2, 5, 19."""
    f = 2 * x**3 - 12 * x**2 + 19 * x - 4
    # f is a translate of y = 2x³ + px exactly when f(x) ≡ 2(x − h)³ + p(x − h) + k for some h, k.
    expr = sp.expand(f - (2 * (x - h) ** 3 + p * (x - h) + k))
    sols = sp.solve(sp.Poly(expr, x).coeffs(), [h, k, p], dict=True)
    ps = {s[p] for s in sols}
    return [sp.Integer(o) in ps for o in (-12, -5, 2, 5, 19)]


def cf_statements(item: dict) -> list[bool]:
    """q3: statements about f(x) = −x³ + 3x² + 1.
    (1) the symmetry centre is (1, 3); (2) f(x) > 0 for all large x; (3) the graph is a translate of
    y = −x³ + 3x; (4) the graph is symmetric about the line x = 1; (5) f(1 + t) + f(1 − t) = 6 for all t."""
    f = -(x**3) + 3 * x**2 + 1
    hc, kc = _centre(f)
    s1 = (hc, kc) == (1, 3)
    s2 = sp.limit(f, x, sp.oo) == sp.oo
    expr = sp.expand(f - (-((x - h) ** 3) + 3 * (x - h) + k))
    s3 = bool(sp.solve(sp.Poly(expr, x).coeffs(), [h, k], dict=True))
    s4 = _symmetric_about_vertical(f, 1)
    s5 = sp.expand(f.subs(x, 1 + t) + f.subs(x, 1 - t) - 6) == 0
    return [bool(s1), bool(s2), s3, s4, bool(s5)]


def cf_line_fill(item: dict) -> tuple[int, int]:
    """q4: the approximating line y = mx + b of f(x) = x³ − 3x² + 4x − 1 near x = 2."""
    line = sp.Poly(sp.expand(_line_at(x**3 - 3 * x**2 + 4 * x - 1, 2)), x)
    m, b = line.coeff_monomial(x), line.coeff_monomial(1)
    return (int(m), int(b))


def cf_end_behaviour(item: dict) -> list[bool]:
    """q5: far to the left and far to the right, y = −2x³ + x² + 100x goes:
    left up, right down; left down, right up; up on both sides; down on both sides; levels off to a horizontal line."""
    f = -2 * x**3 + x**2 + 100 * x
    left, right = sp.limit(f, x, -sp.oo), sp.limit(f, x, sp.oo)
    oo = sp.oo
    return [
        left == oo and right == -oo,
        left == -oo and right == oo,
        left == oo and right == oo,
        left == -oo and right == -oo,
        bool(left.is_finite) and bool(right.is_finite),
    ]


def cf_estimate(item: dict) -> list[bool]:
    """q6: estimate g(1.02) for g(x) = x³ + x² − 2x with its approximating line at x = 1.
    Options: 0.02, 0.03, 0.06, 1.06, 3.06."""
    g = x**3 + x**2 - 2 * x
    est = _line_at(g, 1).subs(x, sp.Rational(102, 100))
    # The estimate should also be close to the true value (the dropped terms are tiny near x = 1).
    assert abs(est - g.subs(x, sp.Rational(102, 100))) < sp.Rational(1, 100)
    options = [sp.Rational(n, 100) for n in (2, 3, 6, 106, 306)]
    return [sp.simplify(est - o) == 0 for o in options]


def cf_translates_of_x3(item: dict) -> list[bool]:
    """q7: which graphs are translates of y = x³: (x − 1)³ + 2; x³ + 3x² + 3x; x³ + 3x; x³ − 3x² + 3x + 5; 2x³."""
    options = [(x - 1) ** 3 + 2, x**3 + 3 * x**2 + 3 * x, x**3 + 3 * x, x**3 - 3 * x**2 + 3 * x + 5, 2 * x**3]
    out = []
    for f in options:
        expr = sp.expand(f - ((x - h) ** 3 + k))
        out.append(bool(sp.solve(sp.Poly(expr, x).coeffs(), [h, k], dict=True)))
    return out
