"""Checks for src/data/items/math/s116a-vector-operations.yaml (116 sprint, 數A: G-11A-6, G-11A-7, G-11A-8).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Where a formula gives the answer, it is cross-checked against an independent route: the inner product
against the law of cosines, a determinant area against the shoelace area of the polygon, a cross product
against its two defining properties (perpendicular to both, length |a||b| sin θ), a triple product against
the determinant, and a Cauchy maximum against a direct maximisation on the circle.
"""

from __future__ import annotations

import sympy as sp
from sympy import Matrix, Point, Polygon

t = sp.Symbol("t", real=True)


def _v(*xs) -> Matrix:
    return Matrix([sp.nsimplify(c) for c in xs])


def _angle(a: Matrix, b: Matrix) -> sp.Expr:
    """Angle between a and b from a·b = |a||b|cos θ, cross-checked with the law of cosines on the
    triangle with sides |a|, |b|, |a − b|."""
    cos_dot = a.dot(b) / (a.norm() * b.norm())
    cos_law = (a.norm() ** 2 + b.norm() ** 2 - (a - b).norm() ** 2) / (2 * a.norm() * b.norm())
    assert sp.simplify(cos_dot - cos_law) == 0
    return sp.acos(sp.nsimplify(sp.simplify(cos_dot)))


def _cross(a: Matrix, b: Matrix) -> Matrix:
    """a × b, cross-checked: perpendicular to a and b, and |a × b|² = |a|²|b|² − (a·b)²."""
    c = a.cross(b)
    assert c.dot(a) == 0 and c.dot(b) == 0
    assert sp.simplify(c.dot(c) - (a.dot(a) * b.dot(b) - a.dot(b) ** 2)) == 0
    return c


def _det3(a: Matrix, b: Matrix, c: Matrix) -> sp.Expr:
    """det with rows a, b, c, cross-checked with the triple product (a × b)·c."""
    d = Matrix.vstack(a.T, b.T, c.T).det()
    assert sp.simplify(d - _cross(a, b).dot(c)) == 0
    return d


def vo_turn_angle(item: dict) -> list[bool]:
    """q-turn: the angle between (1, 2) and (3, 1). Options 30°, 45°, 60°, 90°, 135°."""
    theta = _angle(_v(1, 2), _v(3, 1))
    options = [sp.pi * d / 180 for d in (30, 45, 60, 90, 135)]
    return [sp.simplify(theta - o) == 0 for o in options]


def vo_projection_vector(item: dict) -> list[bool]:
    """q1: the orthogonal projection of a = (3, 4) onto b = (2, 1).
    Options (4,2), (2,1), (6/5, 8/5), (8,4), (10,5).
    Computed as the foot of the perpendicular: the point s·b with (a − s·b) ⊥ b, solved for s."""
    a, b = _v(3, 4), _v(2, 1)
    s = sp.Symbol("s")
    (s0,) = sp.solve((a - s * b).dot(b), s)
    proj = s0 * b
    assert proj == (a.dot(b) / b.dot(b)) * b  # agrees with the formula (a·b / |b|²) b
    R = sp.Rational
    options = [_v(4, 2), _v(2, 1), Matrix([R(6, 5), R(8, 5)]), _v(8, 4), _v(10, 5)]
    return [proj == o for o in options]


def vo_space_relations(item: dict) -> list[bool]:
    """q2: u = (1, 2, −2), v = (2, −2, −1), w = (−2, −4, 4). Statements:
    (1) u ⊥ v; (2) u ∥ w; (3) |u × v| = 9; (4) u·w = 18; (5) u × w is not the zero vector."""
    u, v, w = _v(1, 2, -2), _v(2, -2, -1), _v(-2, -4, 4)
    uw = _cross(u, w)
    parallel = uw == sp.zeros(3, 1) and u != sp.zeros(3, 1) and w != sp.zeros(3, 1)
    return [
        u.dot(v) == 0,
        bool(parallel),
        sp.simplify(_cross(u, v).norm() - 9) == 0,
        u.dot(w) == 18,
        uw != sp.zeros(3, 1),
    ]


def vo_cauchy_max(item: dict) -> sp.Integer:
    """q3: x² + y² = 10, the largest value of 3x − y.
    Cauchy gives √10·√(3² + 1²); cross-checked by maximising on the circle x = √10 cos t, y = √10 sin t."""
    r = sp.sqrt(10)
    by_cauchy = r * sp.sqrt(3**2 + 1**2)
    f = 3 * r * sp.cos(t) - r * sp.sin(t)
    crit = sp.solve(sp.diff(f, t), t)
    by_calc = max(sp.simplify(f.subs(t, c)) for c in crit)
    assert sp.simplify(by_cauchy - by_calc) == 0
    return sp.Integer(sp.simplify(by_cauchy))


def vo_triangle_area_det(item: dict) -> sp.Integer:
    """q4: the area of the triangle A(−1, 2), B(3, 1), C(1, 5): ½|det(AB, AC)|, cross-checked by shoelace."""
    A, B, C = _v(-1, 2), _v(3, 1), _v(1, 5)
    ab, ac = B - A, C - A
    by_det = sp.Abs(Matrix.hstack(ab, ac).det()) / 2
    by_poly = sp.Abs(Polygon(Point(-1, 2), Point(3, 1), Point(1, 5)).area)
    assert by_det == by_poly
    return sp.Integer(by_det)


def vo_cross_product(item: dict) -> tuple[int, int, int]:
    """q5: (2, 1, −1) × (1, 3, 2), as its three components (the key spells 5, −5, 5)."""
    c = _cross(_v(2, 1, -1), _v(1, 3, 2))
    return tuple(int(k) for k in c)


def vo_coplanar_k(item: dict) -> list[bool]:
    """q6: (1, 2, 3), (2, k, 1), (1, 1, 1) lie in one plane (through the origin): k?
    Options 1/2, 1, 3/2, 2, 3. Coplanar ⇔ the 3×3 determinant is 0."""
    k = sp.Symbol("k")
    d = _det3(_v(1, 2, 3), Matrix([2, k, 1]), _v(1, 1, 1))
    sols = sp.solve(d, k)
    assert len(sols) == 1
    R = sp.Rational
    options = [R(1, 2), sp.Integer(1), R(3, 2), sp.Integer(2), sp.Integer(3)]
    return [sols[0] == o for o in options]


def vo_tetrahedron_volume(item: dict) -> tuple[int, int]:
    """q7: the volume of the tetrahedron O, A(1, 1, 0), B(0, 1, 1), C(1, 0, 1), as p/q in lowest terms.
    ⅙|det(OA, OB, OC)|, cross-checked by ⅓ · base area · height (base OAB, height = distance from C)."""
    a, b, c = _v(1, 1, 0), _v(0, 1, 1), _v(1, 0, 1)
    vol = sp.Abs(_det3(a, b, c)) / 6
    n = _cross(a, b)
    base = n.norm() / 2
    height = sp.Abs(n.dot(c)) / n.norm()
    assert sp.simplify(vol - base * height / 3) == 0
    vol = sp.Rational(vol)
    return (int(vol.p), int(vol.q))
