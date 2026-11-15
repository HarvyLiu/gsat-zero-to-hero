"""Checks for src/data/items/math/s116a-planes-lines.yaml (116 sprint, 數A: planes G-11A-9, lines in space G-11A-10).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Where the chapter teaches a formula, the check uses a different route (SymPy geometry objects, or a
minimisation) so a wrong formula in the text cannot hide behind a wrong check.
"""

from __future__ import annotations

import sympy as sp

x, y, z, t, s = sp.symbols("x y z t s", real=True)
P3 = sp.Point3D


def _plane(expr) -> sp.Plane:
    """The plane expr = 0 (expr linear in x, y, z) as a SymPy Plane, through one of its points."""
    a, b, c = (sp.diff(expr, v) for v in (x, y, z))
    d = expr.subs({x: 0, y: 0, z: 0})
    if a != 0:
        pt = P3(-d / a, 0, 0)
    elif b != 0:
        pt = P3(0, -d / b, 0)
    else:
        pt = P3(0, 0, -d / c)
    return sp.Plane(pt, normal_vector=(a, b, c))


def _parallel(u, v) -> bool:
    return sp.Matrix(u).cross(sp.Matrix(v)) == sp.zeros(3, 1)


def _same_plane(e1, e2) -> bool:
    """e1 = 0 and e2 = 0 are the same plane: the coefficient vectors (a, b, c, d) are proportional."""
    c1 = sp.Matrix([sp.diff(e1, v) for v in (x, y, z)] + [e1.subs({x: 0, y: 0, z: 0})])
    c2 = sp.Matrix([sp.diff(e2, v) for v in (x, y, z)] + [e2.subs({x: 0, y: 0, z: 0})])
    return sp.Matrix.hstack(c1, c2).rank() == 1


def _line_distance(a1, v1, a2, v2) -> sp.Expr:
    """Shortest distance between the lines a1 + t v1 and a2 + s v2, by minimising the squared distance."""
    p = sp.Matrix(a1) + t * sp.Matrix(v1)
    q = sp.Matrix(a2) + s * sp.Matrix(v2)
    f = (p - q).dot(p - q)
    sol = sp.solve([sp.diff(f, t), sp.diff(f, s)], [t, s], dict=True)
    assert len(sol) == 1  # unique closest pair: the lines are not parallel
    return sp.sqrt(sp.simplify(f.subs(sol[0])))


def pl_turn_normal(item: dict) -> list[bool]:
    """q-turn: a normal vector of 2x − y + 3z = 5. Options: (2,−1,3), (2,−1,5), (−1,3,5), (2,1,3), (3,−1,2).
    A normal is perpendicular to every vector lying in the plane: test against two independent ones."""
    pts = [P3(0, -5, 0), P3(1, -3, 0), P3(0, 1, 2)]  # three points of the plane
    for p in pts:
        assert 2 * p.x - p.y + 3 * p.z == 5
    u = sp.Matrix(pts[1] - pts[0])
    w = sp.Matrix(pts[2] - pts[0])
    opts = [(2, -1, 3), (2, -1, 5), (-1, 3, 5), (2, 1, 3), (3, -1, 2)]
    return [sp.Matrix(o).dot(u) == 0 and sp.Matrix(o).dot(w) == 0 for o in opts]


def pl_point_normal(item: dict) -> list[bool]:
    """q1: the plane through (1, −2, 3) with normal (3, 1, −2).
    Options: 3x+y−2z+5=0; 3x+y−2z−5=0; x−2y+3z−14=0; 3x+y−2z=0; x−2y+3z+5=0."""
    target = sp.Plane(P3(1, -2, 3), normal_vector=(3, 1, -2))
    opts = [
        3 * x + y - 2 * z + 5,
        3 * x + y - 2 * z - 5,
        x - 2 * y + 3 * z - 14,
        3 * x + y - 2 * z,
        x - 2 * y + 3 * z + 5,
    ]
    return [_plane(e).equals(target) for e in opts]


def pl_three_points(item: dict) -> tuple[int, int, int]:
    """q2: the plane through A(2,1,−1), B(0,3,1), C(1,0,2) written as 2x + ay + bz = c; return (a, b, c)."""
    A, B, C = P3(2, 1, -1), P3(0, 3, 1), P3(1, 0, 2)
    assert not sp.Point3D.are_collinear(A, B, C)
    a, b, c = sp.symbols("a b c")
    sol = sp.solve([2 * p.x + a * p.y + b * p.z - c for p in (A, B, C)], [a, b, c], dict=True)
    assert len(sol) == 1
    return (sol[0][a], sol[0][b], sol[0][c])


def pl_plane_angle(item: dict) -> list[bool]:
    """q3: the acute angle θ between x + 2y + 2z = 3 and 2x + 2y + z = −1; options for cos θ:
    8/9, 8/3, 4/9, 1/9, 2/3. Uses SymPy's Plane.angle_between, folded to the acute angle."""
    ang = _plane(x + 2 * y + 2 * z - 3).angle_between(_plane(2 * x + 2 * y + z + 1))
    c = sp.simplify(sp.cos(ang))
    c = sp.Abs(c)  # the two planes make angles θ and π − θ; the acute one has cos θ = |cos|
    opts = [sp.Rational(8, 9), sp.Rational(8, 3), sp.Rational(4, 9), sp.Rational(1, 9), sp.Rational(2, 3)]
    return [sp.simplify(c - o) == 0 for o in opts]


def pl_parallel_planes(item: dict) -> tuple[int, int]:
    """q4: distance between x − 2y + 2z + 4 = 0 and −2x + 4y − 4z + 7 = 0, as p/q in lowest terms.
    Distance from a point of the first plane to the second (SymPy Plane.distance)."""
    e1, e2 = x - 2 * y + 2 * z + 4, -2 * x + 4 * y - 4 * z + 7
    assert _parallel((1, -2, 2), (-2, 4, -4)) and not _same_plane(e1, e2)
    p = P3(-4, 0, 0)
    assert e1.subs({x: p.x, y: p.y, z: p.z}) == 0
    d = sp.nsimplify(_plane(e2).distance(p))
    r = sp.Rational(d)
    return (int(r.p), int(r.q))


def pl_line_plane_meet(item: dict) -> tuple[int, int, int]:
    """q5: where (x−2)/1 = (y+1)/(−2) = z/3 meets x + y + z = 7 (SymPy intersection); return the point."""
    L = sp.Line3D(P3(2, -1, 0), direction_ratio=(1, -2, 3))
    (pt,) = _plane(x + y + z - 7).intersection(L)
    return (pt.x, pt.y, pt.z)


def pl_line_statements(item: dict) -> list[bool]:
    """q6: L: x = 1 + 2t, y = −t, z = 3 + t.
    (1) L passes through (3, 1, 4); (2) L is (x−1)/2 = y/1 = (z−3)/1;
    (3) L is parallel to x + y − z = 5 and has no point in common with it;
    (4) L meets x + 3y + z = 4 in exactly one point; (5) L is perpendicular to 4x − 2y + 2z = 1."""
    L = sp.Line3D(P3(1, 0, 3), direction_ratio=(2, -1, 1))
    s1 = L.contains(P3(3, 1, 4))
    # (2): the line written by the statement, as points (1,0,3) + k(2,1,1)
    s2 = L.equals(sp.Line3D(P3(1, 0, 3), direction_ratio=(2, 1, 1)))

    def meets(expr):
        return _plane(expr).intersection(L)

    m3 = meets(x + y - z - 5)
    s3 = m3 == []
    m4 = meets(x + 3 * y + z - 4)
    s4 = len(m4) == 1 and isinstance(m4[0], sp.Point3D)
    s5 = _plane(4 * x - 2 * y + 2 * z - 1).is_perpendicular(L)
    return [s1, s2, s3, s4, s5]


def pl_point_line_distance(item: dict) -> tuple[int, int]:
    """q7: distance from P(0, 3, 1) to the line (1,1,1) + t(1,0,1), written a√2/b; return (a, b).
    SymPy Line3D.distance (closest point), not the cross-product formula."""
    L = sp.Line3D(P3(1, 1, 1), direction_ratio=(1, 0, 1))
    d = sp.nsimplify(L.distance(P3(0, 3, 1)))
    r = sp.Rational(sp.simplify(d / sp.sqrt(2)))
    return (int(r.p), int(r.q))


def pl_skew_distance(item: dict) -> tuple[int, int]:
    """q8: L1: (1,0,0) + t(0,1,0), L2: (0,0,3) + s(1,1,1). Check they are skew, then return (a, b) with
    distance a√b (b square-free), by minimising the squared distance."""
    L1 = sp.Line3D(P3(1, 0, 0), direction_ratio=(0, 1, 0))
    L2 = sp.Line3D(P3(0, 0, 3), direction_ratio=(1, 1, 1))
    assert not L1.is_parallel(L2) and L1.intersection(L2) == []
    d = sp.simplify(_line_distance((1, 0, 0), (0, 1, 0), (0, 0, 3), (1, 1, 1)))
    coeff, rad = d.as_coeff_Mul()
    b = rad.args[0] if isinstance(rad, sp.Pow) else rad
    assert sp.simplify(coeff * sp.sqrt(b) - d) == 0
    return (int(coeff), int(b))
