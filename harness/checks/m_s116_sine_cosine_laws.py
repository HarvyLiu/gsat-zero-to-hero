"""Checks for src/data/items/math/s116-sine-cosine-laws.yaml (116 sprint: laws of sines and cosines).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Where a formula gives the answer (area = ½ab sin C, the two laws), the result is cross-checked against an
independent construction with coordinates, so a wrong formula cannot agree with a wrong key.
Angles are exact: degrees are converted with sp.pi / 180, never with floats.
"""

from __future__ import annotations

import sympy as sp
from sympy.geometry import Point, Triangle

DEG = sp.pi / 180


def _deg(d) -> sp.Expr:
    return sp.Integer(d) * DEG


def _place(b, c, angle_a):
    """Triangle with A at the origin, AB = c along the positive x-axis and AC = b at angle A: (A, B, C)."""
    a_pt = Point(0, 0)
    b_pt = Point(c, 0)
    c_pt = Point(b * sp.cos(angle_a), b * sp.sin(angle_a))
    return a_pt, b_pt, c_pt


def _area_sas(b, c, angle_a) -> sp.Expr:
    """½bc sin A, cross-checked against the coordinate (shoelace) area of the placed triangle."""
    by_formula = sp.Rational(1, 2) * b * c * sp.sin(angle_a)
    by_coords = sp.Abs(Triangle(*_place(b, c, angle_a)).area)
    assert sp.simplify(by_formula - by_coords) == 0
    return sp.nsimplify(sp.simplify(by_formula))


def _angle_from_sides(opposite, s1, s2) -> sp.Expr:
    """The angle opposite `opposite` by the law of cosines, in radians."""
    return sp.acos(sp.Rational(s1**2 + s2**2 - opposite**2, 2 * s1 * s2))


def slc_turn_area(item: dict) -> list[bool]:
    """q-turn: sides 6 and 8 with included angle 30°: the area. Options 12, 24, 12√3, 24√3, 48."""
    area = _area_sas(6, 8, _deg(30))
    options = [sp.Integer(12), sp.Integer(24), 12 * sp.sqrt(3), 24 * sp.sqrt(3), sp.Integer(48)]
    return [sp.simplify(area - o) == 0 for o in options]


def slc_area_sas(item: dict) -> sp.Integer:
    """q1: AB = 8, AC = 5, ∠A = 150°: the area of △ABC (½·8·5·sin 150°)."""
    return sp.Integer(_area_sas(5, 8, _deg(150)))


def slc_sines_side(item: dict) -> list[bool]:
    """q2: ∠A = 30°, ∠B = 45°, a = 6: the side b. Options 3√2, 6√2, 6√3, 12, 3√6.
    b = a sin B / sin A; cross-checked by building the triangle (C = 105°, c from the law of sines)
    and confirming b² = a² + c² − 2ac cos B."""
    a, angle_a, angle_b = sp.Integer(6), _deg(30), _deg(45)
    b = sp.simplify(a * sp.sin(angle_b) / sp.sin(angle_a))
    angle_c = sp.pi - angle_a - angle_b
    c = a * sp.sin(angle_c) / sp.sin(angle_a)
    assert sp.simplify(b**2 - (a**2 + c**2 - 2 * a * c * sp.cos(angle_b))) == 0
    options = [3 * sp.sqrt(2), 6 * sp.sqrt(2), 6 * sp.sqrt(3), sp.Integer(12), 3 * sp.sqrt(6)]
    return [sp.simplify(b - o) == 0 for o in options]


def slc_circumradius(item: dict) -> sp.Integer:
    """q3: ∠A = 120°, a = 6√3: the circumradius R = a / (2 sin A).
    Cross-checked with SymPy's circumradius of a concrete triangle with these data (B = C = 30°)."""
    a, angle_a = 6 * sp.sqrt(3), _deg(120)
    r = sp.simplify(a / (2 * sp.sin(angle_a)))
    side = a * sp.sin(_deg(30)) / sp.sin(angle_a)  # b = c in the isosceles example
    tri = Triangle(*_place(side, side, angle_a))
    assert sp.simplify(tri.sides[1].length - a) == 0  # side BC really is a
    assert sp.simplify(tri.circumradius - r) == 0
    return sp.Integer(r)


def slc_cosines_side(item: dict) -> sp.Integer:
    """q4: b = 7, c = 8, ∠A = 120°: the side a by the law of cosines, cross-checked with the distance BC."""
    b, c, angle_a = 7, 8, _deg(120)
    a = sp.sqrt(b**2 + c**2 - 2 * b * c * sp.cos(angle_a))
    _, p_b, p_c = _place(b, c, angle_a)
    assert sp.simplify(p_b.distance(p_c) - a) == 0
    return sp.Integer(sp.simplify(a))


def slc_triangle_568(item: dict) -> list[bool]:
    """q5: a = 5, b = 6, c = 8. Statements: ∠C is the largest angle; cos C = −1/20; △ABC is obtuse;
    sin A : sin B = 6 : 5; the circumradius is less than 4."""
    a, b, c = 5, 6, 8
    angles = {"A": _angle_from_sides(a, b, c), "B": _angle_from_sides(b, c, a), "C": _angle_from_sides(c, a, b)}
    assert abs(float(sum(angles.values()) - sp.pi)) < 1e-12  # the three angles do close up (acos sums resist simplify)
    cos_c = sp.cos(angles["C"])
    largest = max(angles, key=lambda k: float(angles[k]))
    r = sp.simplify(c / (2 * sp.sin(angles["C"])))
    ratio = sp.simplify(sp.sin(angles["A"]) / sp.sin(angles["B"]))
    return [
        largest == "C",
        sp.simplify(cos_c - sp.Rational(-1, 20)) == 0,
        any(bool(sp.cos(t) < 0) for t in angles.values()),
        sp.simplify(ratio - sp.Rational(6, 5)) == 0,
        bool(r < 4),
    ]


def slc_area_sss(item: dict) -> tuple[int, int]:
    """q6: sides 3, 7, 8: the area written m√n → (m, n).
    Angle opposite 7 by the law of cosines (60°), area ½·3·8·sin 60°; cross-checked with Heron's formula."""
    angle = _angle_from_sides(7, 3, 8)
    area = sp.simplify(sp.Rational(1, 2) * 3 * 8 * sp.sin(angle))
    s = sp.Rational(3 + 7 + 8, 2)
    heron = sp.sqrt(s * (s - 3) * (s - 7) * (s - 8))
    assert sp.simplify(area - heron) == 0
    coeff, rad = area.as_coeff_Mul()
    n = sp.Integer(rad**2)
    assert sp.sqrt(n) == rad and sp.sqrt(n).is_integer is False  # m√n with n not a perfect square
    return (int(coeff), int(n))


def slc_lines_angle(item: dict) -> sp.Integer:
    """q7: L₁: x − √3 y = 0 and L₂: x + y = 1; the acute angle between them in degrees.
    From the angles of inclination (tan θ = slope, 0° ≤ θ < 180°), cross-checked with direction vectors."""

    def inclination(m):
        t = sp.atan(m)
        return t if t >= 0 else t + sp.pi

    t1, t2 = inclination(1 / sp.sqrt(3)), inclination(sp.Integer(-1))
    d = sp.Abs(t1 - t2)
    acute = sp.Min(d, sp.pi - d)
    u, v = sp.Matrix([sp.sqrt(3), 1]), sp.Matrix([1, -1])  # directions of L₁ and L₂
    by_vectors = sp.acos(sp.Abs(u.dot(v)) / (u.norm() * v.norm()))
    assert sp.simplify(acute - by_vectors) == 0
    return sp.Integer(sp.simplify(acute / DEG))


def slc_cuboid_angle(item: dict) -> list[bool]:
    """q8: cuboid ABCD-EFGH, AB = 3, AD = 4, AE = 5 (E above A, G above C). ∠GAC in the cross-section ACGE.
    Options 30°, 45°, 60°, 75°, 90°. Computed from the 3-D coordinates with a dot product."""
    p_a = sp.Matrix([0, 0, 0])
    p_c = sp.Matrix([3, 4, 0])
    p_g = sp.Matrix([3, 4, 5])
    u, v = p_c - p_a, p_g - p_a
    angle = sp.simplify(sp.acos(u.dot(v) / (u.norm() * v.norm())) / DEG)
    return [sp.simplify(angle - d) == 0 for d in (30, 45, 60, 75, 90)]
