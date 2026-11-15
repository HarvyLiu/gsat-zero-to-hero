"""Checks for src/data/items/math/s116xa-vectors-space-matrices.yaml (116 sprint, 數A cross-unit:
A-11A-2, G-11A-9, G-11A-7, G-11A-5).

Each item check recomputes its answer from the mathematics with SymPy; none reads item["answer"].
The chapter solves every worked problem several ways; `_worked_examples()` (run at import, so the
harness fails if any of them is wrong) recomputes each way separately and asserts they agree.
"""

from __future__ import annotations

import sympy as sp

x, y, z, t = sp.symbols("x y z t", real=True)
M = sp.Matrix


def _unique(eqs, unknowns) -> tuple:
    sol = sp.linsolve(eqs, unknowns)
    (pt,) = tuple(sol)
    assert all(not sp.sympify(v).free_symbols for v in pt), "the system must have exactly one solution"
    return tuple(sp.nsimplify(v) for v in pt)


def _kind(eqs, unknowns) -> str:
    """'one', 'many' or 'none'."""
    sol = sp.linsolve(eqs, unknowns)
    if sol == sp.S.EmptySet:
        return "none"
    (pt,) = tuple(sol)
    return "one" if all(not sp.sympify(v).free_symbols for v in pt) else "many"


def _dist_point_plane(p, n, d):
    """Distance from point p to the plane n·X + d = 0, by the formula."""
    p, n = M(p), M(n)
    return sp.nsimplify(sp.Abs(n.dot(p) + d) / n.norm())


def _worked_examples() -> None:
    # ---------- Problem 1: x+2y−z=3, 2x−y+z=7, x+y+2z=8 ----------
    eqs = [x + 2 * y - z - 3, 2 * x - y + z - 7, x + y + 2 * z - 8]
    want = (3, 1, 2)
    # way 1: elimination on the augmented matrix (the steps shown in the chapter)
    r1, r2, r3 = M([[1, 2, -1, 3]]), M([[2, -1, 1, 7]]), M([[1, 1, 2, 8]])
    r2, r3 = r2 - 2 * r1, r3 - r1
    assert list(r2) == [0, -5, 3, 1] and list(r3) == [0, -1, 3, 5]
    r2, r3 = r3, r2  # swap
    r3 = r3 - 5 * r2
    assert list(r3) == [0, 0, -12, -24]
    zz = sp.Rational(r3[3], r3[2])
    yy = (r2[3] - r2[2] * zz) / r2[1]
    xx = r1[3] - r1[1] * yy - r1[2] * zz
    assert (xx, yy, zz) == want
    # way 2: E1 and E3 meet in the line (13−5t, 3t−5, t); put it into E2
    line = (13 - 5 * t, 3 * t - 5, t)
    for e in (eqs[0], eqs[2]):
        assert sp.expand(e.subs({x: line[0], y: line[1], z: line[2]})) == 0
    n1, n2, n3 = M([1, 2, -1]), M([2, -1, 1]), M([1, 1, 2])
    assert n1.cross(n3) == M([5, -3, -1])  # the line's direction (−5, 3, 1) is parallel to n1 × n3
    assert sp.expand(eqs[1].subs({x: line[0], y: line[1], z: line[2]})) == (31 - 12 * t) - 7  # 2x − y + z = 31 − 12t, minus the 7 on the right
    ts = sp.solve(sp.Eq(31 - 12 * t, 7), t)
    assert ts == [2] and tuple(v.subs(t, 2) for v in line) == want
    # way 3: columns; dot with cross products of the other two columns
    c1, c2, c3, dv = M([1, 2, 1]), M([2, -1, 1]), M([-1, 1, 2]), M([3, 7, 8])
    w1, w2, w3 = c2.cross(c3), c3.cross(c1), c1.cross(c2)
    assert w1 == M([-3, -5, 1]) and w2 == M([-3, 3, -3]) and w3 == M([3, 1, -5])
    vol = c1.dot(w1)
    assert vol == -12 == c2.dot(w2) == c3.dot(w3) == M.hstack(c1, c2, c3).det()
    assert dv.dot(w1) == -36 and dv.dot(w2) == -12 and dv.dot(w3) == -24
    assert (dv.dot(w1) / vol, dv.dot(w2) / vol, dv.dot(w3) / vol) == want
    assert _unique(eqs, [x, y, z]) == want

    # ---------- Problem 2: P(3, 0, 4) to E: 2x − 2y + z − 1 = 0 ----------
    P, n, d = M([3, 0, 4]), M([2, -2, 1]), -1
    # way 1: formula
    assert _dist_point_plane(P, n, d) == 3
    # way 2: project AP on n, A = (0, 0, 1) on E
    A = M([0, 0, 1])
    assert n.dot(A) + d == 0
    AP = P - A
    assert AP == M([3, 0, 3]) and AP.dot(n) == 9 and sp.Abs(AP.dot(n)) / n.norm() == 3
    # way 3: foot of the perpendicular along P + t n
    foot_t = sp.solve(n.dot(P + t * n) + d, t)
    assert foot_t == [-1]
    H = P + foot_t[0] * n
    assert H == M([1, 2, 3]) and (P - H).norm() == 3
    assert P + 2 * foot_t[0] * n == M([-1, 4, 2])  # the mirror image of P in E
    # way 4: Cauchy: for Q on E, n·(Q − P) = −(n·P + d) = −9, so 81 ≤ |n|²|PQ|² = 9|PQ|²
    assert n.dot(P) + d == 9 and sp.sqrt(sp.Rational(81, 9)) == 3

    # ---------- Problem 3: triangle A(1,0,2), B(3,1,0), C(0,2,3) ----------
    A, B, C = M([1, 0, 2]), M([3, 1, 0]), M([0, 2, 3])
    AB, AC, BC = B - A, C - A, C - B
    assert AB == M([2, 1, -2]) and AC == M([-1, 2, 1])
    # way 1: cross product
    cr = AB.cross(AC)
    assert cr == M([5, 0, 5])
    area1 = cr.norm() / 2
    # way 2: |AB|²|AC|² − (AB·AC)²
    assert AB.dot(AB) == 9 and AC.dot(AC) == 6 and AB.dot(AC) == -2
    area2 = sp.sqrt(AB.dot(AB) * AC.dot(AC) - AB.dot(AC) ** 2) / 2
    # way 3: side lengths only, law of cosines then ½ bc sin A
    a2, b2, c2_ = BC.dot(BC), AC.dot(AC), AB.dot(AB)
    assert (a2, b2, c2_) == (19, 6, 9)
    cosA = (b2 + c2_ - a2) / (2 * sp.sqrt(b2) * sp.sqrt(c2_))
    assert sp.simplify(cosA - sp.Rational(-2, 3) / sp.sqrt(6)) == 0
    sinA = sp.sqrt(1 - cosA**2)
    area3 = sp.sqrt(b2) * sp.sqrt(c2_) * sinA / 2
    want_area = 5 * sp.sqrt(2) / 2
    for a in (area1, area2, area3):
        assert sp.simplify(a - want_area) == 0

    # ---------- Problem 4: tetrahedron ABCD, D(2, 3, 4) ----------
    D = M([2, 3, 4])
    AD = D - A
    assert AD == M([1, 3, 2])
    # way 1: 1/6 |det|
    det = M.hstack(AB, AC, AD).det()
    assert det == 15 == AD.dot(cr)
    vol1 = sp.Abs(det) / 6
    # way 2: plane ABC is x + z = 3, height by the distance formula, V = 1/3 · base · height
    for p in (A, B, C):
        assert p[0] + p[2] == 3
    h = _dist_point_plane(D, [1, 0, 1], -3)
    assert sp.simplify(h - 3 * sp.sqrt(2) / 2) == 0
    vol2 = want_area * h / 3
    assert vol1 == sp.Rational(5, 2) and sp.simplify(vol2 - vol1) == 0
    foot = D - sp.Rational(3, 2) * M([1, 0, 1])
    assert foot == M([sp.Rational(1, 2), 3, sp.Rational(5, 2)]) and foot[0] + foot[2] == 3

    # ---------- Problem 5: A(4, 3), B(5, 12), the angle AOB ----------
    a, b = M([4, 3]), M([5, 12])
    assert a.norm() == 5 and b.norm() == 13
    # way 1: difference formulas with cos α = 4/5, sin α = 3/5, cos β = 5/13, sin β = 12/13
    ca, sa, cb, sb = sp.Rational(4, 5), sp.Rational(3, 5), sp.Rational(5, 13), sp.Rational(12, 13)
    cos1 = cb * ca + sb * sa
    sin1 = sb * ca - cb * sa
    # way 2: inner product and the 2×2 determinant (area)
    cos2 = a.dot(b) / (a.norm() * b.norm())
    det2 = M.hstack(a, b).det()
    assert a.dot(b) == 56 and det2 == 33
    sin2 = det2 / (a.norm() * b.norm())
    # way 3: law of cosines with AB² = 82, then sin from sin² + cos² = 1 (the angle is acute)
    AB2 = (b - a).dot(b - a)
    assert AB2 == 82
    cos3 = sp.Rational(25 + 169 - AB2, 2 * 5 * 13)
    sin3 = sp.sqrt(1 - cos3**2)
    assert cos1 == cos2 == cos3 == sp.Rational(56, 65)
    assert sin1 == sin2 == sin3 == sp.Rational(33, 65)
    # cross-check with actual angles
    ang = sp.atan2(12, 5) - sp.atan2(3, 4)
    assert sp.simplify(sp.cos(ang) - sp.Rational(56, 65)) == 0 and sp.simplify(sp.sin(ang) - sp.Rational(33, 65)) == 0
    # tan by the difference formula
    assert (sp.Rational(12, 5) - sp.Rational(3, 4)) / (1 + sp.Rational(12, 5) * sp.Rational(3, 4)) == sp.Rational(33, 56)
    # triangle OAB area
    assert sp.Rational(1, 2) * det2 == sp.Rational(33, 2)

    # ---------- Problem 6: x+y+z=3, x−y+2z=1, 2x+3z=k ----------
    k = sp.Symbol("k")
    eqs6 = lambda kv: [x + y + z - 3, x - y + 2 * z - 1, 2 * x + 3 * z - kv]  # noqa: E731
    # way 1: R3 − R1 − R2 leaves 0 = k − 4
    r1, r2, r3 = M([[1, 1, 1, 3]]), M([[1, -1, 2, 1]]), M([[2, 0, 3, k]])
    assert list(r3 - r1 - r2) == [0, 0, 0, k - 4]
    assert _kind(eqs6(4), [x, y, z]) == "many"
    assert all(_kind(eqs6(kv), [x, y, z]) == "none" for kv in (0, 3, 5, -2))
    # way 2: the line E1 ∩ E2 has direction n1 × n2 = (3, −1, −2), through (2, 1, 0)
    m1, m2, m3 = M([1, 1, 1]), M([1, -1, 2]), M([2, 0, 3])
    dirv = m1.cross(m2)
    assert dirv == M([3, -1, -2]) and m3.dot(dirv) == 0 and m3 == m1 + m2
    p0 = M([2, 1, 0])
    assert m1.dot(p0) == 3 and m2.dot(p0) == 1 and m3.dot(p0) == 4
    for u, v in ((m1, m2), (m1, m3), (m2, m3)):
        assert u.cross(v) != M([0, 0, 0])  # no two planes are parallel
    # way 3: columns c1, c2, c3 and the dot with c2 × c3
    c1, c2, c3, dv = M([1, 1, 2]), M([1, -1, 0]), M([1, 2, 3]), M([3, 1, k])
    w = c2.cross(c3)
    assert w == M([-3, -3, 3])
    assert M.hstack(c1, c2, c3).det() == 0 == c1.dot(w)
    assert sp.expand(dv.dot(w)) == 3 * k - 12
    # TryIt: third equation 2x + 4z = k instead: the determinant is −2, exactly one solution for every k
    assert M([[1, 1, 1], [1, -1, 2], [2, 0, 4]]).det() == -2
    assert all(_kind([x + y + z - 3, x - y + 2 * z - 1, 2 * x + 4 * z - kv], [x, y, z]) == "one" for kv in (0, 4, 6))


_worked_examples()


# ---------------------------------------------------------------------------
# item checks
# ---------------------------------------------------------------------------


def xa_turn_distance(item: dict) -> list[bool]:
    """q-turn: distance from O to the plane 2x − y + 2z = 9. Options: 1, √3, 3, 9, 9/√5."""
    dist = _dist_point_plane([0, 0, 0], [2, -1, 2], -9)
    # cross-check: the foot of the perpendicular is t·n with n·(t n) = 9
    tt = sp.solve(M([2, -1, 2]).dot(t * M([2, -1, 2])) - 9, t)[0]
    assert (tt * M([2, -1, 2])).norm() == dist
    opts = [1, sp.sqrt(3), 3, 9, 9 / sp.sqrt(5)]
    return [sp.simplify(dist - o) == 0 for o in opts]


def xa_system_fill(item: dict) -> tuple:
    """q1: x − y + 2z = 5, 2x + y − z = 2, x + 2y + z = 1. Cells: x, y, z."""
    return _unique([x - y + 2 * z - 5, 2 * x + y - z - 2, x + 2 * y + z - 1], [x, y, z])


def xa_foot_and_distance(item: dict) -> tuple:
    """q2: P(7, 1, −2), E: 2x + y − 2z − 1 = 0. Cells: the foot H = (h1, h2, h3), then the distance."""
    P, n = M([7, 1, -2]), M([2, 1, -2])
    (tt,) = sp.solve(n.dot(P + t * n) - 1, t)
    H = P + tt * n
    assert n.dot(H) - 1 == 0 and (P - H).cross(n) == M([0, 0, 0])
    dist = (P - H).norm()
    assert dist == _dist_point_plane(P, n, -1)
    return (H[0], H[1], H[2], dist)


def xa_triangle_area(item: dict) -> list[bool]:
    """q3: area of the triangle A(0, 1, 1), B(2, 1, 0), C(1, 3, 1).
    Computed with Heron's formula from the side lengths (not the cross product).
    Options: √21/2, √21, √23/2, 5/2, 2."""
    A, B, C = M([0, 1, 1]), M([2, 1, 0]), M([1, 3, 1])
    a, b, c = (B - C).norm(), (C - A).norm(), (A - B).norm()
    s = (a + b + c) / 2
    area = sp.sqrt(sp.expand(s * (s - a) * (s - b) * (s - c)))
    area = sp.nsimplify(sp.radsimp(sp.simplify(area)))
    assert sp.simplify(area - (B - A).cross(C - A).norm() / 2) == 0
    opts = [sp.sqrt(21) / 2, sp.sqrt(21), sp.sqrt(23) / 2, sp.Rational(5, 2), 2]
    return [sp.simplify(area - o) == 0 for o in opts]


def xa_angle_statements(item: dict) -> list[bool]:
    """q4: A(3, 4), B(−8, 15), θ = ∠AOB.
    (1) cos θ = 36/85; (2) sin θ = 77/85; (3) area of △OAB = 77; (4) tan θ = 36/77; (5) |AB| = 11√2.
    Uses the actual direction angles (atan2), not the formulas the item teaches."""
    th = sp.atan2(15, -8) - sp.atan2(4, 3)
    assert 0 < float(th) < float(sp.pi)
    cos_t, sin_t = sp.simplify(sp.cos(th)), sp.simplify(sp.sin(th))
    area = sp.Polygon(sp.Point(0, 0), sp.Point(3, 4), sp.Point(-8, 15)).area
    ab = sp.Point(3, 4).distance(sp.Point(-8, 15))
    return [
        sp.simplify(cos_t - sp.Rational(36, 85)) == 0,
        sp.simplify(sin_t - sp.Rational(77, 85)) == 0,
        sp.Abs(area) == 77,
        sp.simplify(sin_t / cos_t - sp.Rational(36, 77)) == 0,
        sp.simplify(ab - 11 * sp.sqrt(2)) == 0,
    ]


def xa_method_choice(item: dict) -> list[bool]:
    """q5: a triangle given only by its sides 5, 6, 7 (no coordinates). Which method computes its area
    directly from the given data?
    Options: (1) ½|AB × AC| (needs coordinates of the vectors); (2) ½|AB|·|AC|, treating A as a right angle
    (gives the wrong value); (3) law of cosines for cos A, then ½ bc sin A; (4) Gaussian elimination
    (solves systems, gives no area); (5) the point-to-plane distance formula (needs a plane equation).
    A method counts when the data it needs are all given AND it returns the true area (Heron: 6√6)."""
    given = {"side lengths"}
    needs = [{"coordinates"}, {"side lengths"}, {"side lengths"}, {"a linear system"}, {"a plane equation", "coordinates"}]
    a, b, c = 7, 5, 6  # a = BC, b = CA, c = AB
    s = sp.Rational(a + b + c, 2)
    true_area = sp.sqrt(s * (s - a) * (s - b) * (s - c))
    assert true_area == 6 * sp.sqrt(6)
    cosA = sp.Rational(b**2 + c**2 - a**2, 2 * b * c)
    by_cosines = sp.Rational(1, 2) * b * c * sp.sqrt(1 - cosA**2)
    right_angle_guess = sp.Rational(1, 2) * b * c
    value = [None, right_angle_guess, by_cosines, None, None]
    return [n <= given and v is not None and sp.simplify(v - true_area) == 0 for n, v in zip(needs, value)]


def xa_parameter_system(item: dict) -> list[bool]:
    """q6: x + 2y − z = 1, 2x − y + z = 3, 3x + y + a z = b.
    (1) a = 1, b = 4: exactly one solution; (2) a = 0, b = 4: infinitely many;
    (3) a = 0, b = 5: exactly one solution; (4) a = 0, b = 4: the three planes share one line;
    (5) a = 0, b = 5: two of the planes are parallel."""

    def eqs(av, bv):
        return [x + 2 * y - z - 1, 2 * x - y + z - 3, 3 * x + y + av * z - bv]

    def normals(av):
        return [M([1, 2, -1]), M([2, -1, 1]), M([3, 1, av])]

    def distinct_planes(av, bv):
        rows = [M([[1, 2, -1, 1]]), M([[2, -1, 1, 3]]), M([[3, 1, av, bv]])]
        return all(M.vstack(r, s).rank() == 2 for i, r in enumerate(rows) for s in rows[i + 1 :])

    def some_parallel(av):
        ns = normals(av)
        return any(ns[i].cross(ns[j]) == M([0, 0, 0]) for i in range(3) for j in range(i + 1, 3))

    s4 = _kind(eqs(0, 4), [x, y, z]) == "many" and distinct_planes(0, 4)
    if s4:
        # the solution set is a line: exactly one free parameter
        (pt,) = tuple(sp.linsolve(eqs(0, 4), [x, y, z]))
        s4 = len(set().union(*(sp.sympify(v).free_symbols for v in pt))) == 1
    return [
        _kind(eqs(1, 4), [x, y, z]) == "one",
        _kind(eqs(0, 4), [x, y, z]) == "many",
        _kind(eqs(0, 5), [x, y, z]) == "one",
        bool(s4),
        some_parallel(0),
    ]


def xa_tetra_fill(item: dict) -> tuple:
    """q7: O(0,0,0), A(3,0,0), B(0,6,0), C(0,0,3). Cells: the volume of OABC, then the area of △ABC
    as a fraction p/q (from V = ⅓ · area · distance from O to plane ABC)."""
    O, A, B, C = M([0, 0, 0]), M([3, 0, 0]), M([0, 6, 0]), M([0, 0, 3])
    vol = sp.Abs(M.hstack(A - O, B - O, C - O).det()) / 6
    n = (B - A).cross(C - A)
    d = -n.dot(A)
    h = _dist_point_plane(O, n, d)
    area = sp.nsimplify(3 * vol / h)
    assert sp.simplify(area - n.norm() / 2) == 0
    area = sp.Rational(area)
    return (vol, area.p, area.q)
