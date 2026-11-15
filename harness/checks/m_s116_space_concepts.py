"""Checks for src/data/items/math/s116-space-concepts.yaml (116 sprint: lines and planes in space).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Position questions about the cube are decided with coordinates: the cube ABCD-EFGH has base ABCD,
top EFGH and vertical edges AE, BF, CG, DH, placed as the unit cube below. Lines are classified by
direction vectors (parallel when the cross product is 0) and coplanarity (triple product 0), so the
verdict comes from the geometry, never from a lookup table of answers.
Shortest surface paths on a box are found by minimising over the crossing point on the shared edge
and cross-checked against the unfolded straight-line length; sphere arcs use exact radians.
"""

from __future__ import annotations

from itertools import permutations

import sympy as sp
from sympy import Matrix

DEG = sp.pi / 180

# The unit cube ABCD-EFGH (A at the origin, AB along x, AD along y, AE along z).
CUBE = {
    "A": Matrix([0, 0, 0]),
    "B": Matrix([1, 0, 0]),
    "C": Matrix([1, 1, 0]),
    "D": Matrix([0, 1, 0]),
    "E": Matrix([0, 0, 1]),
    "F": Matrix([1, 0, 1]),
    "G": Matrix([1, 1, 1]),
    "H": Matrix([0, 1, 1]),
}


def _line(name: str) -> tuple[Matrix, Matrix]:
    """Line through two named vertices, e.g. 'AB': (point, direction)."""
    p, q = CUBE[name[0]], CUBE[name[1]]
    return p, q - p


def _plane(name: str) -> tuple[Matrix, Matrix]:
    """Plane through the first three named vertices (the rest must lie on it): (point, normal)."""
    pts = [CUBE[c] for c in name]
    n = (pts[1] - pts[0]).cross(pts[2] - pts[0])
    assert n != Matrix([0, 0, 0]), f"{name}: the first three points are collinear"
    for p in pts[3:]:
        assert n.dot(p - pts[0]) == 0, f"{name}: {p.T} is not on the plane"
    return pts[0], n


def _two_lines(l1: str, l2: str) -> str:
    """'coincide', 'parallel', 'intersect' or 'skew'."""
    p1, d1 = _line(l1)
    p2, d2 = _line(l2)
    if d1.cross(d2) == Matrix([0, 0, 0]):
        return "coincide" if d1.cross(p2 - p1) == Matrix([0, 0, 0]) else "parallel"
    return "intersect" if (p2 - p1).dot(d1.cross(d2)) == 0 else "skew"


def _line_plane(line: str, plane: str) -> str:
    """'in', 'parallel', 'perpendicular' (meets at one point at right angles) or 'meets'."""
    p, d = _line(line)
    q, n = _plane(plane)
    if n.dot(d) == 0:
        return "in" if n.dot(p - q) == 0 else "parallel"
    return "perpendicular" if d.cross(n) == Matrix([0, 0, 0]) else "meets"


def _two_planes(pl1: str, pl2: str) -> str:
    """'coincide', 'parallel', 'perpendicular' or 'oblique'."""
    q1, n1 = _plane(pl1)
    q2, n2 = _plane(pl2)
    if n1.cross(n2) == Matrix([0, 0, 0]):
        return "coincide" if n1.dot(q2 - q1) == 0 else "parallel"
    return "perpendicular" if n1.dot(n2) == 0 else "oblique"


def sc_turn_ab_cg(item: dict) -> list[bool]:
    """q-turn: lines AB and CG in the cube. Options: parallel, intersect, skew, coincide, cannot tell."""
    rel = _two_lines("AB", "CG")
    return [rel == "parallel", rel == "intersect", rel == "skew", rel == "coincide", False]


def sc_which_skew(item: dict) -> list[bool]:
    """q1: which pairs are skew: AB & HG, AE & CD, BD & FH, AG & BH, EG & BD."""
    pairs = [("AB", "HG"), ("AE", "CD"), ("BD", "FH"), ("AG", "BH"), ("EG", "BD")]
    return [_two_lines(a, b) == "skew" for a, b in pairs]


def sc_planes_perp_to_ae(item: dict) -> list[bool]:
    """q2: which planes are perpendicular to line AE: ABCD, EFGH, BCGF, ACGE, BDHF."""
    planes = ["ABCD", "EFGH", "BCGF", "ACGE", "BDHF"]
    return [_line_plane("AE", pl) == "perpendicular" for pl in planes]


def sc_planes_perp_to_base(item: dict) -> list[bool]:
    """q3: which planes are perpendicular to plane ABCD: BDE, ACGE, EFGH, BDHF, ABGH."""
    planes = ["BDE", "ACGE", "EFGH", "BDHF", "ABGH"]
    return [_two_planes("ABCD", pl) == "perpendicular" for pl in planes]


def sc_three_perpendiculars(item: dict) -> sp.Integer:
    """q4: PA ⊥ plane E at A, PA = 5; line L in E with AB ⊥ L at B, AB = 12: the distance from P to L.
    Built in coordinates (E: z = 0, L: y = 12, A at the origin, P = (0, 0, 5)); the distance from P to L
    is the minimum of |PX| over X on L, and the foot of that minimum must be B (the theorem itself)."""
    t = sp.Symbol("t", real=True)
    p = Matrix([0, 0, 5])
    b = Matrix([0, 12, 0])
    x_on_l = Matrix([t, 12, 0])
    d2 = (x_on_l - p).dot(x_on_l - p)
    t0 = sp.solve(sp.diff(d2, t), t)
    assert t0 == [0]  # the nearest point of L to P is B, the foot from A
    foot = x_on_l.subs(t, t0[0])
    assert foot == b and (b - p).dot(Matrix([1, 0, 0])) == 0  # PB ⊥ L
    return sp.Integer(sp.sqrt(d2.subs(t, t0[0])))


def _box_shortest(a, b, c) -> sp.Expr:
    """Shortest path on the surface of the box [0,a]×[0,b]×[0,c] from (0,0,0) to (a,b,c).
    Every route over two faces crosses one edge; for each ordering of the dimensions, minimise over the
    crossing point and check it against the unfolded straight line √((p+q)² + r²)."""
    t = sp.Symbol("t", real=True)
    best = None
    for p, q, r in permutations([sp.Integer(a), sp.Integer(b), sp.Integer(c)]):
        # first face spans p × r, second face q × r; they share an edge of length r, crossed at height t
        length = sp.sqrt(p**2 + t**2) + sp.sqrt(q**2 + (r - t) ** 2)
        crit = [s for s in sp.solve(sp.diff(length, t), t) if 0 <= s <= r]
        cands = [length.subs(t, s) for s in crit + [sp.Integer(0), r]]
        m = min(cands, key=lambda e: float(e))
        assert sp.simplify(m - sp.sqrt((p + q) ** 2 + r**2)) == 0
        best = m if best is None or float(m) < float(best) else best
    return sp.simplify(best)


def sc_box_surface_path(item: dict) -> sp.Integer:
    """q5: a 3 × 5 × 6 box: the shortest path on the surface between opposite vertices."""
    d = _box_shortest(3, 5, 6)
    assert d.is_Integer
    return d


def sc_latitude_arc(item: dict) -> sp.Integer:
    """q6: sphere of radius 6, two points on latitude 60° N whose longitudes differ by 120°:
    the arc along the latitude circle is kπ; return k. The circle's radius is the distance from a point
    on it to the axis, computed from coordinates."""
    r, lat, dlon = sp.Integer(6), 60 * DEG, 120 * DEG
    pt = Matrix([r * sp.cos(lat), 0, r * sp.sin(lat)])
    small_r = sp.sqrt(pt[0] ** 2 + pt[1] ** 2)
    arc = sp.simplify(small_r * dlon)
    k = sp.simplify(arc / sp.pi)
    assert k.is_Integer
    return k


def sc_sphere_statements(item: dict) -> list[bool]:
    """q7: on a sphere of radius R:
    (1) the equator is a great circle; (2) every parallel of latitude is a great circle;
    (3) the 30° N parallel has radius R/2; (4) every meridian is half of a great circle;
    (5) the planes of two different parallels of latitude are parallel."""
    R = sp.Symbol("R", positive=True)
    phi, lam = sp.symbols("phi lam", real=True)

    def lat_circle(theta):
        """Plane height and radius of the parallel at latitude theta."""
        return R * sp.sin(theta), R * sp.cos(theta)

    # a circle on the sphere is great exactly when its plane passes through the centre (height 0)
    s1 = lat_circle(0)[0] == 0
    sample = [DEG * k for k in (10, 30, 45, 60, 80)]
    s2 = all(sp.simplify(lat_circle(th)[0]) == 0 for th in sample)
    s3 = sp.simplify(lat_circle(30 * DEG)[1] - R / 2) == 0
    # meridian at longitude lam: points with latitude phi in [−90°, 90°]; its plane contains the z-axis
    merid = Matrix([R * sp.cos(phi) * sp.cos(lam), R * sp.cos(phi) * sp.sin(lam), R * sp.sin(phi)])
    normal = Matrix([-sp.sin(lam), sp.cos(lam), 0])
    through_centre = sp.simplify(normal.dot(merid)) == 0  # plane through O, so its circle is great
    span = sp.pi / 2 - (-sp.pi / 2)  # angle swept from S pole to N pole
    s4 = through_centre and span == sp.pi
    # every parallel's plane is z = const, normal (0, 0, 1)
    n_a, n_b = Matrix([0, 0, 1]), Matrix([0, 0, 1])
    s5 = n_a.cross(n_b) == Matrix([0, 0, 0]) and sp.simplify(lat_circle(20 * DEG)[0] - lat_circle(50 * DEG)[0]) != 0
    return [bool(s1), bool(s2), bool(s3), bool(s4), bool(s5)]
