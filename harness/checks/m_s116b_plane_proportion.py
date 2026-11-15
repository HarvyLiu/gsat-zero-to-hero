"""Checks for src/data/items/math/s116b-plane-proportion.yaml (116 sprint, Math B: proportion, design and
one-point perspective, G-11B-3).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Perspective items are checked against a central-projection model, not against the rules in the lesson:
the eye is at the origin, the paper is the plane z = f, and a point (X, Y, Z) with depth Z > 0 is drawn
at (fX/Z, fY/Z).
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational
f = sp.Symbol("f", positive=True)


def _project(X, Y, Z):
    """Where the line of sight from the eye (origin) to (X, Y, Z) meets the paper z = f."""
    return sp.Matrix([f * X / Z, f * Y / Z])


def _cross2(u, v):
    return sp.simplify(u[0] * v[1] - u[1] * v[0])


def pp_turn_tree_shadow(item: dict) -> list[bool]:
    """q-turn: person 1.6 m with a 2 m shadow; tree shadow 15 m. Tree height from h/15 = 1.6/2.
    Options: 9.6, 10, 12, 13.6, 18.75."""
    h = sp.Symbol("h", positive=True)
    (height,) = sp.solve(sp.Eq(h / 15, R(16, 10) / 2), h)
    opts = [R(96, 10), 10, 12, R(136, 10), R(1875, 100)]
    return [height == o for o in opts]


def pp_logo_area_factor(item: dict) -> list[bool]:
    """q1: a 3 × 5 rectangle enlarged in proportion to a short side of 4.5; new area / old area.
    Options: 1.5, 2.25, 3, 3.375, 4.5."""
    k = R(45, 10) / 3
    old = sp.Polygon((0, 0), (3, 0), (3, 5), (0, 5)).area
    new = sp.Polygon((0, 0), (3 * k, 0), (3 * k, 5 * k), (0, 5 * k)).area
    factor = sp.nsimplify(new / old)
    opts = [R(15, 10), R(225, 100), 3, R(3375, 1000), R(45, 10)]
    return [factor == o for o in opts]


def pp_parallel_segment(item: dict) -> sp.Integer:
    """q2: DE ∥ BC in △ABC with AD = 4, DB = 6, BC = 20. Built in coordinates: A(0,0), B(10,0), C(10,20)
    (so BC = 20), D = (4,0); E is where the line through D parallel to BC meets AC."""
    A, B, C = sp.Point(0, 0), sp.Point(10, 0), sp.Point(10, 20)
    assert B.distance(C) == 20
    D = sp.Point(4, 0)
    assert A.distance(D) == 4 and D.distance(B) == 6
    (E,) = sp.Line(D, D + (C - B)).intersection(sp.Line(A, C))
    return sp.Integer(D.distance(E))


def pp_lamp_shadow(item: dict) -> sp.Integer:
    """q3: lamp 6 m tall at the origin, person 1.5 m tall at x = 9. The shadow tip is where the line through
    the lamp top and the person's head meets the ground y = 0."""
    top, head = sp.Point(0, 6), sp.Point(9, R(3, 2))
    (tip,) = sp.Line(top, head).intersection(sp.Line(sp.Point(0, 0), sp.Point(1, 0)))
    return sp.Integer(tip.x - 9)


def pp_perspective_rules(item: dict) -> list[bool]:
    """q4: a straight railway in one-point perspective (paper parallel to the sleepers). Model: ground
    y = −1, rails x = ±1 running in the +z direction, sleepers along x at fixed z, poles vertical at x = 3.
    (1) the rails' images meet at one point; (2) vertical poles are drawn parallel; (3) equally spaced
    sleepers are drawn equally spaced; (4) a straight rail may be drawn as a curve; (5) equal pieces of the
    same sleeper are drawn equal."""
    t = sp.Symbol("t", positive=True)
    # (1) points far along each rail approach the same image point
    left = [sp.limit(c, t, sp.oo) for c in _project(-1, -1, t)]
    right = [sp.limit(c, t, sp.oo) for c in _project(1, -1, t)]
    s1 = left == right
    # (2) each pole (x = 3, depth z0, y varying) is drawn along a direction; two poles' directions are parallel
    y = sp.Symbol("y", real=True)
    dirs = [sp.diff(_project(3, y, z0), y) for z0 in (5, 17)]
    s2 = _cross2(dirs[0], dirs[1]) == 0
    # (3) sleepers at depths 10, 11, 12 (equally spaced): compare the drawn gaps
    ys = [_project(0, -1, z)[1] for z in (10, 11, 12)]
    s3 = sp.simplify((ys[1] - ys[0]) - (ys[2] - ys[1])) == 0
    # (4) three points of any line (P + sD) are drawn collinear, so a straight rail is never drawn curved
    px, py, pz, dx, dy, dz = sp.symbols("px py pz dx dy dz", real=True)
    pts = [_project(px + s * dx, py + s * dy, pz + s * dz) for s in (0, 1, 2)]
    collinear = _cross2(pts[1] - pts[0], pts[2] - pts[0]) == 0
    s4 = not collinear
    # (5) two equal pieces of one sleeper at depth 8: x from −1 to 0 and from 0 to 1
    a, b, c = (_project(xx, -1, 8) for xx in (-1, 0, 1))
    s5 = sp.simplify((b - a).norm() - (c - b).norm()) == 0
    return [s1, s2, s3, s4, s5]


def pp_vanishing_point(item: dict) -> tuple[int, int]:
    """q5: drawn rails through (0,0),(3,4) and (12,0),(9,4); the vanishing point is their crossing."""
    (vp,) = sp.Line(sp.Point(0, 0), sp.Point(3, 4)).intersection(sp.Line(sp.Point(12, 0), sp.Point(9, 4)))
    return (int(vp.x), int(vp.y))


def pp_true_half(item: dict) -> tuple[int, int]:
    """q6: A(0,0), B(12,0), C(9,4), D(3,4) draw a rectangle; the front/back halving line is drawn through the
    crossing of the diagonals, horizontally. Cross-checked against the projection model: the drawn depth
    line y(Z) is fitted to the two edges and evaluated at the true middle depth."""
    A, B, C, D = (sp.Point(*p) for p in [(0, 0), (12, 0), (9, 4), (3, 4)])
    (centre,) = sp.Line(A, C).intersection(sp.Line(B, D))
    # projection cross-check: ground y = −g, front edge at depth z0. Drawn width ∝ 1/Z gives the back
    # edge's depth; the drawn height above the front edge is affine in 1/Z.
    z0 = sp.Symbol("z0", positive=True)
    z_back = z0 * (B.x - A.x) / (C.x - D.x)
    u, v = sp.symbols("u v")
    drawn = lambda Z: u + v / Z  # noqa: E731
    sol = sp.solve([drawn(z0) - A.y, drawn(z_back) - D.y], [u, v], dict=True)[0]
    y_mid = sp.simplify(drawn((z0 + z_back) / 2).subs(sol))
    assert sp.simplify(y_mid - centre.y) == 0
    r = sp.Rational(centre.y)
    return (int(r.p), int(r.q))


def pp_pole_image_height(item: dict) -> list[bool]:
    """q7: two equal poles at depths 20 and 30 (parallel to the paper); the nearer is drawn 6 cm tall.
    Options: 9, 4, 3, 2, 6."""
    h = sp.Symbol("h", positive=True)
    height = lambda Z: sp.simplify(_project(0, h, Z)[1] - _project(0, 0, Z)[1])  # noqa: E731
    fh = sp.solve(sp.Eq(height(20), 6), h)[0]
    far = sp.simplify(height(30).subs(h, fh))
    return [far == o for o in (9, 4, 3, 2, 6)]
