"""Checks for src/data/items/math/s116a-matrices.yaml (116 sprint, 數A: A-11A-1, A-11A-2, A-11A-3).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Systems are solved with sp.linsolve (not with Cramer's formula), so a check does not repeat the
method the item is teaching.
"""

from __future__ import annotations

import sympy as sp

x, y, z = sp.symbols("x y z", real=True)
M = sp.Matrix


def _kind(eqs, unknowns) -> str:
    """'one' (exactly one solution), 'many' (infinitely many) or 'none' (no solution)."""
    sol = sp.linsolve(eqs, unknowns)
    if sol == sp.S.EmptySet:
        return "none"
    (pt,) = tuple(sol)
    return "one" if all(not sp.sympify(v).free_symbols for v in pt) else "many"


def _unique(eqs, unknowns) -> tuple:
    sol = sp.linsolve(eqs, unknowns)
    (pt,) = tuple(sol)
    assert all(not sp.sympify(v).free_symbols for v in pt), "the system must have exactly one solution"
    return tuple(sp.nsimplify(v) for v in pt)


def mx_turn_column_combination(item: dict) -> list[bool]:
    """q-turn: [[1, 2], [3, 4]] times the column (2, 1).
    Options (as columns): (4, 10); (5, 8); (3, 7); (2, 8); (10, 4)."""
    prod = M([[1, 2], [3, 4]]) * M([2, 1])
    options = [M([4, 10]), M([5, 8]), M([3, 7]), M([2, 8]), M([10, 4])]
    return [prod == o for o in options]


def mx_parameter_cases(item: dict) -> list[bool]:
    """q1: the system x + k y = 2, k x + 4 y = 4.
    (1) k = 2: infinitely many solutions; (2) k = −2: no solution; (3) k = 0: exactly one solution;
    (4) k = 1: x = 2/3; (5) for every k with Δ = 0 the system has no solution."""
    k = sp.Symbol("k")

    def eqs(kv):
        return [x + kv * y - 2, kv * x + 4 * y - 4]

    s1 = _kind(eqs(2), [x, y]) == "many"
    s2 = _kind(eqs(-2), [x, y]) == "none"
    s3 = _kind(eqs(0), [x, y]) == "one"
    s4 = _unique(eqs(1), [x, y])[0] == sp.Rational(2, 3)
    delta = M([[1, k], [k, 4]]).det()
    singular = sp.solve(delta, k)
    s5 = all(_kind(eqs(kv), [x, y]) == "none" for kv in singular)
    return [s1, s2, s3, s4, s5]


def mx_cramer_fill(item: dict) -> tuple:
    """q2: 2x + 5y = 1, 3x + 4y = 5. Cells: Δ (the coefficient determinant), then x, then y."""
    delta = M([[2, 5], [3, 4]]).det()
    xs, ys = _unique([2 * x + 5 * y - 1, 3 * x + 4 * y - 5], [x, y])
    return (delta, xs, ys)


def mx_parallelogram_area(item: dict) -> list[bool]:
    """q3: area of the parallelogram with adjacent sides (4, 1) and (2, 3).
    Computed with the shoelace formula on its four vertices, not with the determinant.
    Options: 5, 10, 12, 14, 20."""
    a, b = sp.Point(4, 1), sp.Point(2, 3)
    o = sp.Point(0, 0)
    area = abs(sp.Polygon(o, a, a + b, b).area)
    return [area == v for v in (5, 10, 12, 14, 20)]


def mx_three_unknowns(item: dict) -> tuple:
    """q4: x + 2y + z = 3, 2x + y − z = 0, x − y + 2z = 9. Cells: x, y, z."""
    return _unique([x + 2 * y + z - 3, 2 * x + y - z, x - y + 2 * z - 9], [x, y, z])


def mx_reduced_augmented(item: dict) -> list[bool]:
    """q5: a system whose augmented matrix reduces to
        [1 2 −1 | 3]
        [0 1  2 | 1]
        [0 0  0 | k]
    (1) k = 0: infinitely many solutions; (2) k ≠ 0 (try k = 1, 5, −3): no solution;
    (3) k = 0: (x, y, z) = (1, 1, 0) is a solution; (4) k = 0: exactly one solution; (5) k = 1: z = 1."""

    def eqs(kv):
        return [x + 2 * y - z - 3, y + 2 * z - 1, 0 * x - kv]

    s1 = _kind(eqs(0), [x, y, z]) == "many"
    s2 = all(_kind(eqs(kv), [x, y, z]) == "none" for kv in (1, 5, -3))
    s3 = all(sp.simplify(e.subs({x: 1, y: 1, z: 0})) == 0 for e in eqs(0))
    s4 = _kind(eqs(0), [x, y, z]) == "one"
    sol1 = sp.linsolve(eqs(1), [x, y, z])
    s5 = sol1 != sp.S.EmptySet and all(pt[2] == 1 for pt in sol1)
    return [s1, s2, s3, s4, bool(s5)]


def mx_quadratic_through_points(item: dict) -> tuple:
    """q6: y = a x² + b x + c through (1, 2), (2, 3), (3, 6). Cells: a, b, c.
    Cross-checked against SymPy's interpolating polynomial."""
    a, b, c = sp.symbols("a b c")
    pts = [(1, 2), (2, 3), (3, 6)]
    sol = _unique([a * px**2 + b * px + c - py for px, py in pts], [a, b, c])
    t = sp.Symbol("t")
    poly = sp.Poly(sp.interpolate(pts, t), t)
    assert tuple(poly.all_coeffs()) == sol
    return sol


def mx_operation_statements(item: dict) -> list[bool]:
    """q7: A = [[1, 2], [0, 1]], B = [[3, 0], [1, 2]].
    (1) AB = [[5, 4], [1, 2]]; (2) AB = BA; (3) A + B = [[4, 2], [1, 3]];
    (4) 2A − B = [[−1, 4], [−1, 0]]; (5) the inverse of A is [[−1, −2], [0, −1]]."""
    A = M([[1, 2], [0, 1]])
    B = M([[3, 0], [1, 2]])
    s5 = (A * M([[-1, -2], [0, -1]])) == sp.eye(2)
    return [A * B == M([[5, 4], [1, 2]]), A * B == B * A, A + B == M([[4, 2], [1, 3]]), 2 * A - B == M([[-1, 4], [-1, 0]]), s5]


def mx_inverse_fill(item: dict) -> tuple:
    """q8: the inverse of A = [[3, 2], [4, 3]], read row by row: four cells-groups p, q, r, s."""
    inv = M([[3, 2], [4, 3]]).inv()
    assert M([[3, 2], [4, 3]]) * inv == sp.eye(2)
    return tuple(inv[i, j] for i in range(2) for j in range(2))
