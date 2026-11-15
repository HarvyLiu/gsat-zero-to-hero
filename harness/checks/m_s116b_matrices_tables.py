"""Checks for src/data/items/math/s116b-matrices-tables.yaml (116 sprint, 數B: matrices and data tables).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import sympy as sp

M = sp.Matrix
x, y = sp.symbols("x y")


def _defined(op) -> bool:
    """True when a matrix operation is defined (SymPy raises ShapeError when the sizes do not fit)."""
    try:
        op()
        return True
    except sp.ShapeError:
        return False


def mt_turn_revenue(item: dict) -> list[bool]:
    """q-turn: 40 cups of black tea at 20 dollars and 15 cups of milk tea at 50 dollars.
    The day's revenue is the row (40, 15) times the price column (20, 50)^T.
    Options: 800, 1550, 2300, 3850, 70."""
    revenue = (M([[40, 15]]) * M([[20], [50]]))[0, 0]
    return [revenue == v for v in (800, 1550, 2300, 3850, 70)]


def mt_product_sizes(item: dict) -> list[bool]:
    """q1: A is 3×2, B is 2×4. Options: AB is 3×4; AB is 2×2; BA is 4×3; A+B is 3×4; AB and BA are both defined."""
    A = sp.zeros(3, 2)
    B = sp.zeros(2, 4)
    ab = (A * B).shape if _defined(lambda: A * B) else None
    ba = (B * A).shape if _defined(lambda: B * A) else None
    a_plus_b = (A + B).shape if _defined(lambda: A + B) else None
    return [
        ab == (3, 4),
        ab == (2, 2),
        ba == (4, 3),
        a_plus_b == (3, 4),
        ab is not None and ba is not None,
    ]


def mt_operations_multi(item: dict) -> list[bool]:
    """q2: A = [[1,3],[2,−1]], B = [[0,2],[1,4]].
    Options: A+B = [[1,5],[3,3]]; AB = [[3,14],[−1,0]]; AB = BA; 2A−B = [[2,4],[3,−6]];
    the entry of AB in row 2, column 1 is 9."""
    A = M([[1, 3], [2, -1]])
    B = M([[0, 2], [1, 4]])
    return [
        A + B == M([[1, 5], [3, 3]]),
        A * B == M([[3, 14], [-1, 0]]),
        A * B == B * A,
        2 * A - B == M([[2, 4], [3, -6]]),
        (A * B)[1, 0] == 9,
    ]


def mt_class_lunch_total(item: dict) -> sp.Integer:
    """q3: class 甲 orders 12 of meal no. 1 and 8 of meal no. 2, class 乙 orders 10 and 15; meal no. 1 costs 80, meal no. 2 costs 65.
    Row 2 of (order table)(price column) is class 乙's total."""
    orders = M([[12, 8], [10, 15]])
    prices = M([[80], [65]])
    return sp.Integer((orders * prices)[1, 0])


def mt_matrix_times_vector(item: dict) -> list[bool]:
    """q4: [[1,2],[3,−1]] [x, y]^T as a combination of vectors.
    Options: x(1,3)+y(2,−1); x(1,2)+y(3,−1); (x+y)(3,2); (x+2y, 3x+y); (x+3y, 2x−y), all as column vectors."""
    A = M([[1, 2], [3, -1]])
    lhs = A * M([x, y])
    options = [
        x * M([1, 3]) + y * M([2, -1]),
        x * M([1, 2]) + y * M([3, -1]),
        (x + y) * M([3, 2]),
        M([x + 2 * y, 3 * x + y]),
        M([x + 3 * y, 2 * x - y]),
    ]
    return [sp.simplify(lhs - o) == sp.zeros(2, 1) for o in options]


def mt_inverse_entries(item: dict) -> tuple[int, int, int, int]:
    """q5: the inverse of [[3,5],[1,2]], read entry by entry (row 1 then row 2)."""
    inv = M([[3, 5], [1, 2]]).inv()
    return tuple(int(inv[i, j]) for i in range(2) for j in range(2))  # type: ignore[return-value]


def mt_ticket_prices(item: dict) -> tuple[int, int]:
    """q6: 4 full tickets and 3 student tickets cost 1000; 3 full and 2 student cost 720.
    Solve by X = A^{-1} B (x = full price, y = student price)."""
    A = M([[4, 3], [3, 2]])
    sol = A.inv() * M([1000, 720])
    return (int(sol[0]), int(sol[1]))


def mt_no_inverse(item: dict) -> list[bool]:
    """q7: which matrix has no inverse? A 2×2 matrix is invertible exactly when ad − bc ≠ 0.
    Options: [[1,2],[3,4]], [[2,1],[1,1]], [[2,4],[1,2]], [[0,1],[1,0]], [[3,0],[0,2]]."""
    options = [M([[1, 2], [3, 4]]), M([[2, 1], [1, 1]]), M([[2, 4], [1, 2]]), M([[0, 1], [1, 0]]), M([[3, 0], [0, 2]])]
    return [m.det() == 0 for m in options]
