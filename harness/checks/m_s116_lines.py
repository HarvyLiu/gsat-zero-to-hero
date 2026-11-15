"""Checks for src/data/items/math/s116-lines.yaml (116 sprint: equations of lines, G-10-2).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import sympy as sp

x, y = sp.symbols("x y", real=True)


def _slope(expr) -> sp.Expr | None:
    """Slope of the line expr = 0 (expr linear in x, y); None for a vertical line."""
    a, b = sp.diff(expr, x), sp.diff(expr, y)
    return None if b == 0 else sp.simplify(-a / b)


def _point_line_distance(p: tuple, expr) -> sp.Expr:
    """Distance from p to the line expr = 0, computed geometrically (SymPy Line), not by the formula."""
    a, b = sp.diff(expr, x), sp.diff(expr, y)
    c = expr.subs({x: 0, y: 0})
    # two distinct points on the line
    if b != 0:
        p1, p2 = sp.Point(0, -c / b), sp.Point(1, -(a + c) / b)
    else:
        p1, p2 = sp.Point(-c / a, 0), sp.Point(-c / a, 1)
    return sp.simplify(sp.Line(p1, p2).distance(sp.Point(*p)))


def _relation(e1, e2) -> str:
    """'one' (meet in exactly one point), 'parallel' (no common point) or 'same' (coincide)."""
    sol = sp.linsolve([e1, e2], [x, y])
    if sol == sp.S.EmptySet:
        return "parallel"
    (pt,) = tuple(sol)
    return "one" if all(not v.free_symbols for v in pt) else "same"


def ln_turn_slope(item: dict) -> list[bool]:
    """q-turn: slope of the line through (1, 2) and (4, 8). Options: 1/2, 2, 6, −2, 3."""
    m = sp.Line(sp.Point(1, 2), sp.Point(4, 8)).slope
    return [m == o for o in (sp.Rational(1, 2), 2, 6, -2, 3)]


def ln_line_properties(item: dict) -> list[bool]:
    """q1: statements about L: 2x + 3y − 6 = 0.
    (1) slope −2/3; (2) passes through (3, 1); (3) parallel to 4x + 6y + 1 = 0;
    (4) perpendicular to 2x − 3y = 0; (5) (0, 0) and (1, 1) lie on the same side of L."""
    L = 2 * x + 3 * y - 6
    M = 4 * x + 6 * y + 1
    N = 2 * x - 3 * y
    s1 = _slope(L) == sp.Rational(-2, 3)
    s2 = L.subs({x: 3, y: 1}) == 0
    s3 = _relation(L, M) == "parallel"
    s4 = sp.simplify(_slope(L) * _slope(N)) == -1
    v0, v1 = L.subs({x: 0, y: 0}), L.subs({x: 1, y: 1})
    s5 = bool(v0 * v1 > 0)
    return [s1, s2, s3, s4, s5]


def ln_translate_intercept(item: dict) -> sp.Integer:
    """q2: y = −x + 4 moved 2 to the left and 3 down; the y-intercept of the image.
    Translate two points of the line by (−2, −3) and take the line through the images."""
    v = sp.Point(-2, -3)
    a, b = sp.Point(0, 4) + v, sp.Point(1, 3) + v
    image = sp.Line(a, b)
    (yi,) = [pt.y for pt in image.intersection(sp.Line(sp.Point(0, 0), sp.Point(0, 1)))]
    return sp.Integer(yi)


def ln_perpendicular(item: dict) -> list[bool]:
    """q3: which line is perpendicular to 3x − y + 2 = 0?
    Options: y = 3x − 1; y = −3x + 2; x + 3y − 6 = 0; 3x + y = 0; x − 3y + 1 = 0."""
    base = sp.Line(sp.Point(0, 2), sp.Point(1, 5))  # two points of 3x − y + 2 = 0
    opts = [y - (3 * x - 1), y - (-3 * x + 2), x + 3 * y - 6, 3 * x + y, x - 3 * y + 1]
    out = []
    for e in opts:
        m = _slope(e)
        other = sp.Line(sp.Point(0, -e.subs({x: 0, y: 0}) / sp.diff(e, y)), slope=m)
        out.append(sp.Line.is_perpendicular(base, other))
    return out


def ln_coincide_parallel(item: dict) -> list[bool]:
    """q4: L1: x + ay = 2, L2: ax + 4y = 4. Which statement is true?
    (1) a = 2: parallel; (2) a = −2: coincide; (3) a = −2: parallel; (4) a = 0: parallel;
    (5) a = 1: no common point."""
    def rel(a):
        return _relation(x + a * y - 2, a * x + 4 * y - 4)
    return [rel(2) == "parallel", rel(-2) == "same", rel(-2) == "parallel", rel(0) == "parallel", rel(1) == "parallel"]


def ln_point_distance(item: dict) -> sp.Integer:
    """q5: distance from (1, 3) to 5x − 12y + 5 = 0."""
    return sp.Integer(_point_line_distance((1, 3), 5 * x - 12 * y + 5))


def ln_parallel_distance(item: dict) -> tuple[int, int]:
    """q6: distance between 5x + 12y − 3 = 0 and 10x + 24y + 7 = 0, as a/b in lowest terms.
    Take a point on the first line and measure its distance to the second."""
    l1 = 5 * x + 12 * y - 3
    l2 = 10 * x + 24 * y + 7
    assert _relation(l1, l2) == "parallel"
    p = (sp.Rational(3, 5), 0)  # on l1
    assert l1.subs({x: p[0], y: p[1]}) == 0
    d = sp.nsimplify(_point_line_distance(p, l2))
    return (int(d.p), int(d.q))


def ln_lattice_points(item: dict) -> sp.Integer:
    """q7: lattice points (x, y) with x ≥ 0, y ≥ 0, x + 2y ≤ 6 (brute force)."""
    n = sum(1 for i in range(-20, 21) for j in range(-20, 21) if i >= 0 and j >= 0 and i + 2 * j <= 6)
    return sp.Integer(n)


def ln_triangle_area(item: dict) -> tuple[int, int]:
    """q8: area of △OPQ with P(5, 2), Q(−1, 3), as a/b in lowest terms (SymPy Polygon, not the formula)."""
    area = sp.Abs(sp.Polygon(sp.Point(0, 0), sp.Point(5, 2), sp.Point(-1, 3)).area)
    r = sp.Rational(area)
    return (int(r.p), int(r.q))
