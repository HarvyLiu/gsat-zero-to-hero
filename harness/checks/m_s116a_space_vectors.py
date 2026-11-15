"""Checks for src/data/items/math/s116a-space-vectors.yaml (116 sprint, 數A: space vectors and the triangle inequality).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Vectors are sympy Matrix columns; lengths are exact square roots, so equalities are decided exactly.
Where a shortcut gives the answer (a section formula, the bounds of the triangle inequality), it is
cross-checked against a direct construction so a wrong shortcut cannot agree with a wrong key.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)


def _v(*c) -> sp.Matrix:
    return sp.Matrix([sp.nsimplify(t) for t in c])


def _len(v: sp.Matrix) -> sp.Expr:
    return sp.sqrt(sum(t**2 for t in v))


def _same(u: sp.Matrix, w: sp.Matrix) -> bool:
    return all(sp.simplify(a - b) == 0 for a, b in zip(u, w))


def _combo(a: sp.Matrix, b: sp.Matrix, c: sp.Matrix):
    """All (s, t) with s·a + t·b = c, as a SymPy set (EmptySet when c is not a combination)."""
    s, t = sp.symbols("s t")
    return sp.linsolve(list(s * a + t * b - c), [s, t])


def sv_turn_vector_ab(item: dict) -> list[bool]:
    """q-turn: A(1,2,3), B(4,0,5): the components of vector AB (end point minus start point).
    Options (3,−2,2), (5,2,8), (−3,2,−2), (3,2,2), (4,0,5)."""
    a, b = _v(1, 2, 3), _v(4, 0, 5)
    ab = b - a
    assert _same(a + ab, b)  # walking AB from A lands on B
    options = [_v(3, -2, 2), _v(5, 2, 8), _v(-3, 2, -2), _v(3, 2, 2), _v(4, 0, 5)]
    return [_same(ab, o) for o in options]


def sv_scalar_combination(item: dict) -> list[bool]:
    """q1: a = (2,1,−3), b = (−1,4,0): the vector 3a + 2b.
    Options (4,11,−9), (8,11,−9), (4,−5,−9), (1,5,−3), (4,11,9)."""
    a, b = _v(2, 1, -3), _v(-1, 4, 0)
    w = 3 * a + 2 * b
    options = [_v(4, 11, -9), _v(8, 11, -9), _v(4, -5, -9), _v(1, 5, -3), _v(4, 11, 9)]
    return [_same(w, o) for o in options]


def sv_combo_coefficients(item: dict) -> tuple:
    """q2: (3,7,2) = x(1,1,0) + y(0,2,1): the unique (x, y)."""
    sol = _combo(_v(1, 1, 0), _v(0, 2, 1), _v(3, 7, 2))
    (pair,) = list(sol)  # exactly one solution
    s, t = pair
    return (sp.Integer(s), sp.Integer(t))


def sv_which_combinations(item: dict) -> list[bool]:
    """q3: which vectors are linear combinations of a = (1,0,2) and b = (0,1,−1)?
    Options (1,1,1), (1,2,3), (0,0,0), (3,−1,5), (−2,4,−8)."""
    a, b = _v(1, 0, 2), _v(0, 1, -1)
    options = [_v(1, 1, 1), _v(1, 2, 3), _v(0, 0, 0), _v(3, -1, 5), _v(-2, 4, -8)]
    return [_combo(a, b, o) != sp.S.EmptySet for o in options]


def sv_length_2a_minus_b(item: dict) -> sp.Integer:
    """q4: a = (2,1,4), b = (2,−1,2): the length |2a − b|."""
    w = 2 * _v(2, 1, 4) - _v(2, -1, 2)
    r = sp.simplify(_len(w))
    assert r.is_integer
    return sp.Integer(r)


def sv_possible_lengths(item: dict) -> list[bool]:
    """q5: |a| = 4, |b| = 7: which values can |a + b| take? Options 2, 3, 6, 11, 12.
    Put a = (4,0,0) and b = 7(cos θ, sin θ, 0): |a + b|² = 65 + 56 cos θ, and cos θ runs over [−1, 1].
    So v is possible exactly when (v² − 65)/56 lies in [−1, 1]; cross-checked against the bounds
    |7 − 4| ≤ v ≤ 7 + 4 of the triangle inequality."""
    th = sp.Symbol("theta", real=True)
    a = _v(4, 0, 0)
    b = sp.Matrix([7 * sp.cos(th), 7 * sp.sin(th), 0])
    sq = sp.simplify(sum(t**2 for t in (a + b)))
    assert sp.simplify(sq - (65 + 56 * sp.cos(th))) == 0
    out = []
    for v in [2, 3, 6, 11, 12]:
        c = sp.Rational(v * v - 65, 56)
        possible = bool(-1 <= c <= 1)
        assert possible == (abs(7 - 4) <= v <= 7 + 4)
        out.append(possible)
    return out


def sv_equality_case(item: dict) -> list[bool]:
    """q6: for which pair does |u + v| = |u| + |v| hold?
    Pairs ((1,2,2),(2,4,4)), ((1,2,2),(−1,−2,−2)), ((1,0,0),(0,1,0)), ((1,2,2),(2,1,2)), ((2,−1,0),(−4,2,0))."""
    pairs = [
        (_v(1, 2, 2), _v(2, 4, 4)),
        (_v(1, 2, 2), _v(-1, -2, -2)),
        (_v(1, 0, 0), _v(0, 1, 0)),
        (_v(1, 2, 2), _v(2, 1, 2)),
        (_v(2, -1, 0), _v(-4, 2, 0)),
    ]
    out = []
    for u, w in pairs:
        lhs, rhs = _len(u + w), _len(u) + _len(w)
        assert sp.simplify(rhs - lhs) >= 0  # the triangle inequality itself
        out.append(sp.simplify(lhs - rhs) == 0)
    return out


def sv_real_triangle_min(item: dict) -> tuple:
    """q7: f(x) = |x + 2| + |x − 6|: the minimum value m, and how many integers x give f(x) = m.
    f is convex and piecewise linear with corners at −2 and 6, so its minimum is at a corner; the set
    where f(x) ≤ m is then solved exactly and its integers counted."""
    f = sp.Abs(x + 2) + sp.Abs(x - 6)
    m = min(f.subs(x, c) for c in (-2, 6))
    # far from the corners f grows, so nothing beats the corner value
    assert all(f.subs(x, c) >= m for c in range(-50, 51))
    where = sp.solveset(f <= m, x, domain=sp.S.Reals)
    count = sum(1 for n in range(-100, 101) if sp.Integer(n) in where)
    return (sp.Integer(m), sp.Integer(count))


def sv_division_point(item: dict) -> list[bool]:
    """q8: A(1,4,−2), B(5,0,2), P on segment AB with AP:PB = 1:3: the coordinates of P.
    By the section formula OP = (3/4)OA + (1/4)OB; cross-checked by AP = (1/4)AB and |AP|:|PB| = 1:3.
    Options (2,3,−1), (4,1,1), (3,2,0), (2,3,1), (6,4,0)."""
    a, b = _v(1, 4, -2), _v(5, 0, 2)
    p = sp.Rational(3, 4) * a + sp.Rational(1, 4) * b
    assert _same(p - a, sp.Rational(1, 4) * (b - a))
    assert sp.simplify(3 * _len(p - a) - _len(b - p)) == 0
    options = [_v(2, 3, -1), _v(4, 1, 1), _v(3, 2, 0), _v(2, 3, 1), _v(6, 4, 0)]
    return [_same(p, o) for o in options]
