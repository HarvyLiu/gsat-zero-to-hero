"""Checks for src/data/items/math/s116-circles.yaml (116 sprint: circles and lines).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
A circle is handled as f(x, y) = 0 with f = (x − h)² + (y − k)² − r², so the centre is where both partial
derivatives vanish and r² = −f(centre). Intersections are solved exactly, never estimated.
"""

from __future__ import annotations

import sympy as sp

x, y = sp.symbols("x y", real=True)


def _centre_r2(f):
    """Centre (h, k) and r² of the circle f = 0, where f has x² and y² with coefficient 1."""
    (sol,) = sp.solve([sp.diff(f, x), sp.diff(f, y)], [x, y], dict=True)
    h, k = sol[x], sol[y]
    return (h, k), sp.simplify(-f.subs({x: h, y: k}))


def _real_meets(f, g) -> list[tuple]:
    """Real common points of the curves f = 0 and g = 0."""
    sols = sp.solve([f, g], [x, y], dict=True)
    pts = {(sp.nsimplify(s[x]), sp.nsimplify(s[y])) for s in sols}
    return [p for p in pts if all(sp.im(c) == 0 for c in p)]


def _dist(p, q):
    return sp.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def ci_turn_distance(item: dict) -> list[bool]:
    """q-turn: which point is at distance 5 from (1, 2)? Options (4,6), (3,5), (5,4), (1,−2), (6,3)."""
    options = [(4, 6), (3, 5), (5, 4), (1, -2), (6, 3)]
    return [sp.simplify(_dist(o, (1, 2)) - 5) == 0 for o in options]


def ci_read_centre_radius(item: dict) -> list[bool]:
    """q1: centre and radius of (x + 3)² + (y − 4)² = 9.
    Options: (−3,4) r 3; (3,−4) r 3; (−3,4) r 9; (3,−4) r 9; (−3,−4) r 3."""
    centre, r2 = _centre_r2((x + 3) ** 2 + (y - 4) ** 2 - 9)
    r = sp.sqrt(r2)
    options = [((-3, 4), 3), ((3, -4), 3), ((-3, 4), 9), ((3, -4), 9), ((-3, -4), 3)]
    return [tuple(centre) == c and sp.simplify(r - rr) == 0 for c, rr in options]


def ci_r2_through_point(item: dict) -> sp.Integer:
    """q2: the circle with centre (1, −2) through (4, 4) is (x − 1)² + (y + 2)² = r²; r² is the squared distance."""
    return sp.Integer(sp.simplify(_dist((4, 4), (1, -2)) ** 2))


def ci_line_meets_circle(item: dict) -> list[bool]:
    """q3: how 3x + 4y − 12 = 0 meets (x − 1)² + (y − 1)² = 4.
    Options: two points; tangent (one point); no point; the line passes through the centre; infinitely many points.
    Decided by solving the system, then cross-checked against the distance test d vs r."""
    f = (x - 1) ** 2 + (y - 1) ** 2 - 4
    g = 3 * x + 4 * y - 12
    pts = _real_meets(f, g)
    centre, r2 = _centre_r2(f)
    d = sp.Abs(g.subs({x: centre[0], y: centre[1]})) / sp.sqrt(3**2 + 4**2)
    by_distance = 2 if d < sp.sqrt(r2) else (1 if d == sp.sqrt(r2) else 0)
    assert by_distance == len(pts), (by_distance, pts)
    return [len(pts) == 2, len(pts) == 1, len(pts) == 0, g.subs({x: centre[0], y: centre[1]}) == 0, len(pts) > 2]


def ci_tangent_intercept(item: dict) -> sp.Integer:
    """q4: y = x + k is tangent to x² + y² = 8; the positive k. Substitute and set the discriminant to 0."""
    k = sp.Symbol("k", real=True)
    quad = sp.expand((x**2 + (x + k) ** 2 - 8))
    disc = sp.discriminant(quad, x)
    roots = [r for r in sp.solve(sp.Eq(disc, 0), k) if r > 0]
    (root,) = roots
    return sp.Integer(root)


def ci_statements(item: dict) -> list[bool]:
    """q5: C: (x − 2)² + (y + 1)² = 10. Statements: (5,0) is on C; the origin is inside C;
    the line x = 6 meets C; the radius is 10; the centre is (−2, 1)."""
    f = (x - 2) ** 2 + (y + 1) ** 2 - 10
    centre, r2 = _centre_r2(f)
    return [
        f.subs({x: 5, y: 0}) == 0,
        bool(f.subs({x: 0, y: 0}) < 0),
        len(_real_meets(f, x - 6)) > 0,
        sp.sqrt(r2) == 10,
        tuple(centre) == (-2, 1),
    ]


def ci_tangent_at_point(item: dict) -> tuple[int, int]:
    """q6: tangent to (x − 1)² + (y − 3)² = 25 at P(4, −1), written 3x + ay = b → (a, b).
    The tangent is perpendicular to the radius CP: (P − C)·((x, y) − P) = 0."""
    f = (x - 1) ** 2 + (y - 3) ** 2 - 25
    centre, _ = _centre_r2(f)
    p = (4, -1)
    assert f.subs({x: p[0], y: p[1]}) == 0  # P is on the circle
    nx, ny = p[0] - centre[0], p[1] - centre[1]
    line = nx * (x - p[0]) + ny * (y - p[1])
    assert len(_real_meets(f, line)) == 1  # it really is a tangent
    s = sp.Rational(3, nx)  # scale so the x-coefficient is 3
    a = ny * s
    b = (nx * p[0] + ny * p[1]) * s
    return (int(a), int(b))


def ci_chord_length(item: dict) -> sp.Integer:
    """q7: length of the chord cut from x² + y² = 25 by 3x + 4y = 15 (distance between the two meeting points)."""
    pts = _real_meets(x**2 + y**2 - 25, 3 * x + 4 * y - 15)
    assert len(pts) == 2
    return sp.Integer(sp.simplify(_dist(pts[0], pts[1])))


def ci_tangent_length(item: dict) -> sp.Integer:
    """q8: length of a tangent segment from P(7, 5) to (x − 1)² + (y − 2)² = 9.
    The touching points T satisfy (T − C)·(T − P) = 0 (radius ⟂ tangent); both give the same PT."""
    f = (x - 1) ** 2 + (y - 2) ** 2 - 9
    (h, k), _ = _centre_r2(f)
    p = (7, 5)
    perp = (x - h) * (x - p[0]) + (y - k) * (y - p[1])
    pts = _real_meets(f, perp)
    assert len(pts) == 2
    lengths = {sp.simplify(_dist(t, p)) for t in pts}
    (length,) = lengths
    return sp.Integer(length)
