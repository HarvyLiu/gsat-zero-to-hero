"""Checks for src/data/items/math/s116-plane-vectors.yaml (116 sprint: plane vectors, G-11A-1 / G-11B-1 / G-11B-2).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Unknowns (k, x, y) are solved for, never assumed. Angles and projections computed from the coordinate
inner product are cross-checked against an independent construction (the law of cosines on the triangle
the two vectors span, or SymPy's own perpendicular-foot geometry), so a wrong formula cannot agree with a wrong key.
"""

from __future__ import annotations

import sympy as sp
from sympy.geometry import Line, Point

k, x, y = sp.symbols("k x y", real=True)
DEG = sp.pi / 180


def _v(*c) -> sp.Matrix:
    return sp.Matrix([sp.nsimplify(t) for t in c])


def _same(u: sp.Matrix, w: sp.Matrix) -> bool:
    return all(sp.simplify(a - b) == 0 for a, b in zip(u, w))


def _parallel(u: sp.Matrix, w: sp.Matrix) -> bool:
    """Non-zero u, w are parallel when one is a real multiple of the other (solved, not cross-multiplied)."""
    t = sp.symbols("t")
    return bool(sp.solve(list(w - t * u), t, dict=True))


def _angle(u: sp.Matrix, w: sp.Matrix) -> sp.Expr:
    """Angle between u and w in radians from the inner product, cross-checked with the law of cosines on △OUW."""
    by_dot = sp.acos(u.dot(w) / (u.norm() * w.norm()))
    a, b, c = u.norm(), w.norm(), (w - u).norm()
    by_cosines = sp.acos((a**2 + b**2 - c**2) / (2 * a * b))
    assert sp.simplify(by_dot - by_cosines) == 0
    return sp.simplify(by_dot)


def pv_turn_ab(item: dict) -> list[bool]:
    """q-turn: A(1,2) → B(4,6). Options (3,4), (−3,−4), (5,8), (4,3), (4,6)."""
    ab = Point(4, 6) - Point(1, 2)
    v = _v(ab.x, ab.y)
    assert v.norm() == Point(1, 2).distance(Point(4, 6))  # the vector's length is the distance AB
    options = [_v(3, 4), _v(-3, -4), _v(5, 8), _v(4, 3), _v(4, 6)]
    return [_same(v, o) for o in options]


def pv_combo_2a_minus_3b(item: dict) -> tuple[int, int]:
    """q1: a = (3,−2), b = (−1,4): 2a − 3b → (p, q)."""
    a, b = _v(3, -2), _v(-1, 4)
    r = 2 * a - 3 * b
    return (int(r[0]), int(r[1]))


def pv_parallel_k(item: dict) -> list[bool]:
    """q2: (k,−4) ∥ (3,6). Options −2, 2, −8, 8, −9/2. Solve (k,−4) = t(3,6) for k and t."""
    t = sp.symbols("t", real=True)
    sols = sp.solve(list(_v(k, -4) - t * _v(3, 6)), [k, t], dict=True)
    assert len(sols) == 1
    kv = sols[0][k]
    assert _parallel(_v(3, 6), _v(kv, -4))
    options = [sp.Integer(-2), sp.Integer(2), sp.Integer(-8), sp.Integer(8), sp.Rational(-9, 2)]
    return [sp.simplify(kv - o) == 0 for o in options]


def pv_linear_combination(item: dict) -> tuple[int, int]:
    """q3: (4,9) = x(2,1) + y(−1,3) → (x, y); the solution must be unique (a, b not parallel)."""
    a, b, c = _v(2, 1), _v(-1, 3), _v(4, 9)
    assert not _parallel(a, b)
    sols = sp.solve(list(x * a + y * b - c), [x, y], dict=True)
    assert len(sols) == 1
    xs, ys = sols[0][x], sols[0][y]
    assert _same(xs * a + ys * b, c)
    return (int(xs), int(ys))


def pv_division_point(item: dict) -> tuple[int, int]:
    """q4: A(−2,5), B(6,1), P on AB with AP:PB = 3:1 → P = (p, q).
    From OP = ¼OA + ¾OB, cross-checked: P is on line AB and AP / PB = 3 by distances."""
    pa, pb = Point(-2, 5), Point(6, 1)
    p = Point(*(sp.Rational(1, 4) * _v(pa.x, pa.y) + sp.Rational(3, 4) * _v(pb.x, pb.y)))
    assert Line(pa, pb).contains(p)
    assert sp.simplify(pa.distance(p) / p.distance(pb) - 3) == 0
    assert pa.distance(p) + p.distance(pb) == pa.distance(pb)  # between A and B, not beyond
    return (int(p.x), int(p.y))


def pv_angle(item: dict) -> list[bool]:
    """q5: angle between (2,1) and (−3,1). Options 45°, 60°, 90°, 120°, 135°."""
    theta = _angle(_v(2, 1), _v(-3, 1))
    return [sp.simplify(theta - d * DEG) == 0 for d in (45, 60, 90, 120, 135)]


def pv_perpendicular_k(item: dict) -> sp.Integer:
    """q6: (k,3) ⊥ (4,k−7): solve the inner product = 0; both vectors must be non-zero at the solution."""
    sols = sp.solve(_v(k, 3).dot(_v(4, k - 7)), k)
    assert len(sols) == 1
    kv = sols[0]
    u, w = _v(kv, 3), _v(4, kv - 7)
    assert u.norm() != 0 and w.norm() != 0
    assert sp.simplify(_angle(u, w) - sp.pi / 2) == 0
    return sp.Integer(kv)


def pv_statements(item: dict) -> list[bool]:
    """q7: a = (4,−2), b = (1,2). Statements: a ⊥ b; |a| = 20; a ∥ (−2,1); a·b > 0; |a+b| = |a−b|."""
    a, b = _v(4, -2), _v(1, 2)
    return [
        sp.simplify(_angle(a, b) - sp.pi / 2) == 0,
        sp.simplify(a.norm() - 20) == 0,
        _parallel(_v(-2, 1), a),
        bool(a.dot(b) > 0),
        sp.simplify((a + b).norm() - (a - b).norm()) == 0,
    ]


def pv_projection(item: dict) -> tuple[int, int]:
    """q8: projection of a = (6,2) on b = (1,2) → (p, q).
    By (a·b / |b|²) b, cross-checked with the foot of the perpendicular from a's end point to the line along b."""
    a, b = _v(6, 2), _v(1, 2)
    proj = (a.dot(b) / b.dot(b)) * b
    foot = Line(Point(0, 0), Point(b[0], b[1])).projection(Point(a[0], a[1]))
    assert _same(proj, _v(foot.x, foot.y))
    assert (a - proj).dot(b) == 0
    return (int(proj[0]), int(proj[1]))
