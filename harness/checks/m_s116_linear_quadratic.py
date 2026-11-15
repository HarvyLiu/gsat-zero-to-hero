"""Checks for src/data/items/math/s116-linear-quadratic.yaml (116 sprint: linear and quadratic functions, F-10-1).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Vertices are found with calculus (f'(x) = 0), not by completing the square, so the check is an
independent route to the number the lesson gets by 配方.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)


def _vertex(f) -> tuple:
    """Vertex (h, k) of the parabola y = f(x), from f'(h) = 0."""
    (h,) = sp.solve(sp.diff(f, x), x)
    return (sp.simplify(h), sp.simplify(f.subs(x, h)))


def _extremes_on(f, lo, hi) -> tuple:
    """(max, min) of f on the closed interval [lo, hi]: endpoints plus critical points inside."""
    cands = [sp.Integer(lo), sp.Integer(hi)] + [c for c in sp.solve(sp.diff(f, x), x) if lo <= c <= hi]
    vals = [sp.simplify(f.subs(x, c)) for c in cands]
    return (sp.Max(*vals), sp.Min(*vals))


def lq_turn_min(item: dict) -> list[bool]:
    """q-turn: minimum value of y = (x − 2)² + 3. Options: −2, 2, 3, 4, 7."""
    f = (x - 2) ** 2 + 3
    m = sp.minimum(f, x, sp.S.Reals)
    return [m == o for o in (-2, 2, 3, 4, 7)]


def lq_vertex(item: dict) -> list[bool]:
    """q1: vertex of f(x) = 3x² + 12x + 7. Options: (2,−5), (−2,−5), (−2,7), (2,43), (−4,7)."""
    v = _vertex(3 * x**2 + 12 * x + 7)
    opts = [(2, -5), (-2, -5), (-2, 7), (2, 43), (-4, 7)]
    return [v == (sp.Integer(a), sp.Integer(b)) for a, b in opts]


def lq_max_value(item: dict) -> sp.Integer:
    """q2: maximum value of f(x) = −2x² + 12x − 7 over all real x."""
    return sp.Integer(sp.maximum(-2 * x**2 + 12 * x - 7, x, sp.S.Reals))


def lq_signs_from_graph(item: dict) -> list[bool]:
    """q3: y = ax² + bx + c opens upward, vertex (h, k) in quadrant III, y-intercept positive.
    Parametrise every such parabola: a = A, h = −H, k = −K with A, H, K > 0, and c = ah² + k > 0,
    i.e. K = AH² − D with D > 0. Then b = −2ah.
    (1) a > 0; (2) b < 0; (3) c > 0; (4) b² − 4ac > 0; (5) a + b + c < 0."""
    A, H, D = sp.symbols("A H D", positive=True)
    a, h = A, -H
    K = A * H**2 - D
    k = -K
    b = -2 * a * h
    c = sp.expand(a * h**2 + k)  # = D
    f = lambda t: a * t**2 + b * t + c  # noqa: E731
    # vertex form and expanded form agree
    assert sp.expand(f(x) - (a * (x - h) ** 2 + k)) == 0
    disc = sp.expand(b**2 - 4 * a * c)

    def decided(v):
        if v is None:
            raise ValueError("sign not decided by the assumptions")
        return bool(v)

    s1 = decided(a.is_positive)
    s2 = decided(b.is_negative)
    s3 = decided(c.is_positive)
    # the discriminant needs K > 0 (vertex below the x-axis): write D = AH² − K with K positive
    Kp = sp.Symbol("Kp", positive=True)
    s4 = decided(sp.expand(disc.subs(D, A * H**2 - Kp)).is_positive)
    s5 = decided(sp.expand(f(1)).is_negative)
    return [s1, s2, s3, s4, s5]


def lq_shift_reflect(item: dict) -> list[bool]:
    """q4: f(x) = x² − 2x + 5. (1) y = f(x − 3) has vertex (4, 4); (2) y = f(x) + 3 has vertex (1, 7);
    (3) y = f(−x) has vertex (1, −4); (4) y = f(−x) and y = f(x) are mirror images in the y-axis;
    (5) y = f(x + 3) has vertex (4, 4)."""
    f = sp.Lambda(x, x**2 - 2 * x + 5)
    P = lambda a, b: (sp.Integer(a), sp.Integer(b))  # noqa: E731
    s1 = _vertex(f(x - 3)) == P(4, 4)
    s2 = _vertex(f(x) + 3) == P(1, 7)
    s3 = _vertex(f(-x)) == P(1, -4)
    # (x0, y0) on y = f(x) iff (−x0, y0) on y = g(x) = f(−x): g(−x) must equal f(x) identically
    g = sp.Lambda(x, f(-x))
    s4 = sp.expand(g(-x) - f(x)) == 0
    s5 = _vertex(f(x + 3)) == P(4, 4)
    return [s1, s2, s3, s4, s5]


def lq_division_point(item: dict) -> tuple[int, int]:
    """q5: A(−4), B(9) on the number line, P on segment AB with AP : PB = 3 : 2; P = a/b in lowest terms.
    Solve 2·AP = 3·PB with A < P < B directly (no formula)."""
    p = sp.Symbol("p", real=True)
    (sol,) = [s for s in sp.solve(sp.Eq(2 * (p - (-4)), 3 * (9 - p)), p) if -4 < s < 9]
    r = sp.Rational(sol)
    return (int(r.p), int(r.q))


def lq_interpolation(item: dict) -> list[bool]:
    """q6: water depth is a linear function of time; 14 cm at minute 2, 34 cm at minute 7.
    Depth at minute 4? Options: 20, 21, 22, 23, 24."""
    m, k = sp.symbols("m k")
    sol = sp.solve([sp.Eq(m * 2 + k, 14), sp.Eq(m * 7 + k, 34)], [m, k])
    d = sol[m] * 4 + sol[k]
    return [d == o for o in (20, 21, 22, 23, 24)]


def lq_profit_interval(item: dict) -> sp.Integer:
    """q7: price x (dollars) sells 100 − 2x per day, cost 10 each; profit (x − 10)(100 − 2x)
    with the price restricted to 15 ≤ x ≤ 25. Largest daily profit."""
    mx, _ = _extremes_on((x - 10) * (100 - 2 * x), 15, 25)
    return sp.Integer(mx)


def lq_max_min_interval(item: dict) -> tuple:
    """q8: f(x) = x² + 2x − 3 on −3 ≤ x ≤ 2: maximum M then minimum m (cells M, then m with its sign)."""
    mx, mn = _extremes_on(x**2 + 2 * x - 3, -3, 2)
    return (sp.Integer(mx), sp.Integer(mn))
