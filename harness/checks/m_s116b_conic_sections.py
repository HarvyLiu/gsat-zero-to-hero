"""Checks for src/data/items/math/s116b-conic-sections.yaml (116 sprint: conic sections, 數B).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Model: the double cone x² + y² = k² z² (apex at the origin, axis the z-axis, k = tan α where α is the
angle between the axis and every generator). A plane is P0 + u·e1 + v·e2 with e1, e2 orthonormal, so
(u, v) are true lengths in the plane. Substituting gives a quadratic A u² + B uv + C v² + D u + E v + F = 0,
classified the usual way: its 3×3 matrix singular → degenerate (the plane goes through the apex);
otherwise B² − 4AC < 0 → ellipse (a circle when B = 0 and A = C), = 0 → parabola, > 0 → hyperbola.
"""

from __future__ import annotations

import sympy as sp

x, y, z, u, v = sp.symbols("x y z u v", real=True)

SHAPES = ["circle", "ellipse", "parabola", "hyperbola"]


def _sign(e) -> int:
    """Exact sign: 0 only if the expression is proved to be 0 (it simplifies to 0, or its minimal
    polynomial is t, i.e. it is the algebraic number 0); otherwise the sign of a 50-digit value."""
    e = sp.simplify(sp.expand_trig(e))
    if e == 0:
        return 0
    val = sp.N(e, 50)
    if abs(val) < sp.Float("1e-40"):
        t = sp.Symbol("t")
        if sp.minimal_polynomial(e, t) == t:
            return 0
    assert abs(val) > sp.Float("1e-40"), f"cannot decide the sign of {e}"
    return 1 if val > 0 else -1


def classify(alpha_deg, p0, e1, e2) -> str:
    """Shape of the cut of the double cone with half-angle alpha_deg by the plane P0 + u e1 + v e2."""
    k = sp.tan(sp.rad(sp.nsimplify(alpha_deg)))
    p0, e1, e2 = (sp.Matrix(t) for t in (p0, e1, e2))
    assert sp.simplify(e1.dot(e1) - 1) == 0 and sp.simplify(e2.dot(e2) - 1) == 0 and sp.simplify(e1.dot(e2)) == 0
    pt = p0 + u * e1 + v * e2
    q = sp.expand(pt[0] ** 2 + pt[1] ** 2 - k**2 * pt[2] ** 2)
    poly = sp.Poly(q, u, v)
    c = lambda i, j: poly.coeff_monomial(u**i * v**j)  # noqa: E731
    A, B, C, D, E, F = c(2, 0), c(1, 1), c(0, 2), c(1, 0), c(0, 1), c(0, 0)
    M = sp.Matrix([[A, B / 2, D / 2], [B / 2, C, E / 2], [D / 2, E / 2, F]])
    if _sign(M.det()) == 0:
        return "degenerate"
    s = _sign(B**2 - 4 * A * C)
    if s < 0:
        return "circle" if _sign(B) == 0 and _sign(A - C) == 0 else "ellipse"
    return "parabola" if s == 0 else "hyperbola"


def plane_at_angle(alpha_deg, theta_deg, h=1) -> str:
    """Cut by a plane making angle theta with the axis. It contains the x-direction and
    e2 = (0, sin θ, cos θ), whose angle with the z-axis is θ; it passes through (0, 0, h), or through
    (0, h, 0) when θ = 0 (a plane through a point of the axis and parallel to it would contain the apex)."""
    t = sp.rad(sp.nsimplify(theta_deg))
    p0 = (0, h, 0) if theta_deg == 0 else (0, 0, h)
    return classify(alpha_deg, p0, (1, 0, 0), (0, sp.sin(t), sp.cos(t)))


def _one_hot(shape: str, options: list[str]) -> list[bool]:
    assert shape in options, shape
    return [o == shape for o in options]


def cs_turn_flashlight(item: dict) -> list[bool]:
    """q-turn: flashlight beam (half-angle 20°, any value works) aimed straight at a wall: the wall is
    perpendicular to the beam's axis (θ = 90°). Options: circle, ellipse, parabola, hyperbola, two crossing lines."""
    return _one_hot(plane_at_angle(20, 90, h=3), SHAPES + ["degenerate"])


def cs_angle_50_on_30(item: dict) -> list[bool]:
    """q1: half-angle 30°, plane at 50° to the axis, not through the apex. Options: circle, ellipse, parabola, hyperbola, a point."""
    return _one_hot(plane_at_angle(30, 50, h=2), SHAPES + ["degenerate"])


def cs_parallel_to_generator(item: dict) -> list[bool]:
    """q2: a plane parallel to exactly one generator, not through the apex. With half-angle 35° (any value
    works) the generator in the y–z plane has direction (0, sin α, cos α); the plane contains it and the
    x-direction and passes through (0, 0, 1). Options: circle, ellipse, parabola, hyperbola, a line."""
    a = sp.rad(35)
    e2 = sp.Matrix([0, sp.sin(a), sp.cos(a)])
    n = sp.Matrix([1, 0, 0]).cross(e2)
    phi = sp.Symbol("phi", real=True)
    gen = sp.Matrix([sp.cos(phi) * sp.sin(a), sp.sin(phi) * sp.sin(a), sp.cos(a)])
    parallel = sp.solveset(sp.simplify(n.dot(gen)), phi, sp.Interval.Ropen(0, 2 * sp.pi))
    assert len(parallel) == 1, parallel  # the stem says: parallel to exactly one generator
    shape = classify(35, (0, 0, 1), (1, 0, 0), e2)
    return _one_hot(shape, SHAPES + ["degenerate"])


def cs_possible_shapes(item: dict) -> list[bool]:
    """q3: which curves a plane NOT through the apex can cut from a double cone.
    Options: circle, ellipse, parabola, hyperbola, two parallel lines.
    Sweeps θ = 0°, 1°, …, 90° for two cones and several distances; every cut is non-degenerate,
    so no pair of lines (parallel or not) ever appears."""
    seen = set()
    for alpha in (30, 45):
        for theta in range(0, 91):
            for h in (1, 2, -3):
                seen.add(plane_at_angle(alpha, theta, h=h))
    assert "degenerate" not in seen
    return [s in seen for s in SHAPES] + [False]


def cs_section_radius(item: dict) -> sp.Integer:
    """q4: right circular cone, height 12, base radius 9; a plane parallel to the base, 8 from the apex.
    The cone is x² + y² = (9/12)² z²; on z = 8 the section is a circle of radius r."""
    r = sp.Symbol("r", positive=True)
    rad2 = sp.Rational(9, 12) ** 2 * 8**2
    (sol,) = sp.solve(sp.Eq(r**2, rad2), r)
    assert classify(sp.deg(sp.atan(sp.Rational(9, 12))), (0, 0, 8), (1, 0, 0), (0, 1, 0)) == "circle"
    return sp.Integer(sol)


def cs_lamp_wall(item: dict) -> list[bool]:
    """q5: lamp with a shade open at top and bottom, bulb at the apex, vertical axis, next to a vertical
    wall: the wall is parallel to the axis, 0.5 from it; half-angle 50° (any value works).
    Options: circle, ellipse, parabola, hyperbola, a straight line."""
    shape = classify(50, (0, sp.Rational(1, 2), 0), (1, 0, 0), (0, 0, 1))
    return _one_hot(shape, SHAPES + ["line"])


def cs_which_hyperbola(item: dict) -> list[bool]:
    """q6: half-angle 40°; planes not through the apex at 80°, 65°, 40°, 25°, 0° to the axis.
    Which cuts are hyperbolas?"""
    return [plane_at_angle(40, t, h=1) == "hyperbola" for t in (80, 65, 40, 25, 0)]


def cs_flashlight_parabola_angle(item: dict) -> sp.Integer:
    """q7: flashlight beam half-angle 25°; at which whole-degree angle between the beam's axis and the wall
    (1°–89°) is the edge of the lit patch a parabola? Must be exactly one."""
    hits = [t for t in range(1, 90) if plane_at_angle(25, t, h=1) == "parabola"]
    assert len(hits) == 1, hits
    return sp.Integer(hits[0])


def cs_two_shades(item: dict) -> list[bool]:
    """q8: one wall, two lamps whose light cones have half-angles 30° (A) and 45° (B); the wall makes 40°
    with both axes. Options: (A, B) = (ellipse, ellipse), (ellipse, hyperbola), (hyperbola, ellipse),
    (parabola, parabola), (hyperbola, hyperbola)."""
    pair = (plane_at_angle(30, 40, h=2), plane_at_angle(45, 40, h=2))
    options = [("ellipse", "ellipse"), ("ellipse", "hyperbola"), ("hyperbola", "ellipse"), ("parabola", "parabola"), ("hyperbola", "hyperbola")]
    return [o == pair for o in options]
