"""Checks for src/data/items/math/s116-space-coordinates.yaml (116 sprint: coordinates in space, G-11A-2 / G-11B-4).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Projections and distances go through sympy.geometry (Plane.projection, Line3D.distance), not through the
"drop a coordinate" shortcut the chapter teaches, so the shortcut itself is being checked too.
Latitude/longitude convention (stated in each stem): sphere centred at O, equator in the xy-plane,
north pole on the positive z-axis, longitude 0 through the positive x-axis, east longitude positive.
"""

from __future__ import annotations

import sympy as sp
from sympy.geometry import Line3D, Plane, Point3D

O = Point3D(0, 0, 0)
X_AXIS = Line3D(O, Point3D(1, 0, 0))
Y_AXIS = Line3D(O, Point3D(0, 1, 0))
Z_AXIS = Line3D(O, Point3D(0, 0, 1))
XY_PLANE = Plane(O, normal_vector=(0, 0, 1))
YZ_PLANE = Plane(O, normal_vector=(1, 0, 0))
XZ_PLANE = Plane(O, normal_vector=(0, 1, 0))


def _eq(a, b) -> bool:
    return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0


def _same_point(p, q) -> bool:
    return all(_eq(u, v) for u, v in zip(p, q))


def _deg(d) -> sp.Expr:
    return sp.Rational(d) * sp.pi / 180


def _from_lat_long(R, lat_deg, long_deg) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Point on the sphere of radius R; north latitude and east longitude are positive (degrees)."""
    phi, theta = _deg(lat_deg), _deg(long_deg)
    return (sp.simplify(R * sp.cos(phi) * sp.cos(theta)),
            sp.simplify(R * sp.cos(phi) * sp.sin(theta)),
            sp.simplify(R * sp.sin(phi)))


# ---------- items ----------

def sc_turn_distance_origin(item: dict) -> list[bool]:
    """q-turn: distance from O to P(2, 3, 6). Options: √13, 7, 11, √40, 49."""
    d = O.distance(Point3D(2, 3, 6))
    options = [sp.sqrt(13), 7, 11, sp.sqrt(40), 49]
    return [_eq(d, o) for o in options]


def sc_projection_xz(item: dict) -> list[bool]:
    """q1: projection of P(5, −2, 7) onto the xz-plane.
    Options: (5,0,7), (0,−2,7), (5,−2,0), (5,0,0), (0,0,7)."""
    foot = XZ_PLANE.projection(Point3D(5, -2, 7))
    options = [(5, 0, 7), (0, -2, 7), (5, -2, 0), (5, 0, 0), (0, 0, 7)]
    return [_same_point(foot, o) for o in options]


def sc_point_facts(item: dict) -> list[bool]:
    """q2: statements about P(−6, 2, 3).
    (1) distance to the xy-plane is 3; (2) distance to the x-axis is √13; (3) projection on the yz-plane is (0,2,3);
    (4) distance to the y-axis is 2; (5) distance to Q(6, 2, 3) is 6."""
    P = Point3D(-6, 2, 3)
    return [
        _eq(XY_PLANE.distance(P), 3),
        _eq(X_AXIS.distance(P), sp.sqrt(13)),
        _same_point(YZ_PLANE.projection(P), (0, 2, 3)),
        _eq(Y_AXIS.distance(P), 2),
        _eq(P.distance(Point3D(6, 2, 3)), 6),
    ]


def sc_two_point_distance(item: dict) -> sp.Integer:
    """q3: distance between A(2, −1, 3) and B(−2, 7, 4)."""
    d = sp.nsimplify(Point3D(2, -1, 3).distance(Point3D(-2, 7, 4)))
    assert d.is_Integer, d
    return d


def sc_equidistant_on_x_axis(item: dict) -> sp.Integer:
    """q4: the point (t, 0, 0) on the x-axis equidistant from A(1, 2, 3) and B(3, 0, −1); find t."""
    t = sp.Symbol("t", real=True)
    Q = Point3D(t, 0, 0)
    sols = sp.solve(sp.Eq(Q.distance(Point3D(1, 2, 3)) ** 2, Q.distance(Point3D(3, 0, -1)) ** 2), t)
    assert len(sols) == 1, sols
    return sp.Integer(sols[0])


def sc_lat_long_to_xyz(item: dict) -> list[bool]:
    """q5: sphere radius 10; the point at 60°N, 90°W (longitude −90°).
    Options: (0,−5,5√3), (0,5,5√3), (0,−5√3,5), (5,0,5√3), (0,−5,−5√3)."""
    p = _from_lat_long(10, 60, -90)
    r3 = sp.sqrt(3)
    options = [(0, -5, 5 * r3), (0, 5, 5 * r3), (0, -5 * r3, 5), (5, 0, 5 * r3), (0, -5, -5 * r3)]
    return [_same_point(p, o) for o in options]


def sc_same_latitude_chord(item: dict) -> sp.Integer:
    """q6: sphere radius 8; straight-line distance between the points at 60°N 10°E and 60°N 70°E."""
    A = Point3D(*_from_lat_long(8, 60, 10))
    B = Point3D(*_from_lat_long(8, 60, 70))
    d = sp.nsimplify(sp.simplify(A.distance(B)))
    assert d.is_Integer, d
    return d


def sc_distance_from_axis_and_plane(item: dict) -> list[bool]:
    """q7: P is 6 from the z-axis and 8 from the xy-plane; find OP for every such P.
    Options: 10, 14, 2√7, √14, 48."""
    s = sp.Symbol("s", real=True)  # P = (6 cos s, 6 sin s, ±8) covers every such point
    lengths = set()
    for z in (8, -8):
        P = Point3D(6 * sp.cos(s), 6 * sp.sin(s), z)
        assert _eq(Z_AXIS.distance(P), 6) and _eq(XY_PLANE.distance(P), 8)
        lengths.add(sp.simplify(O.distance(P)))
    assert len(lengths) == 1, lengths
    d = lengths.pop()
    options = [10, 14, 2 * sp.sqrt(7), sp.sqrt(14), 48]
    return [_eq(d, o) for o in options]
