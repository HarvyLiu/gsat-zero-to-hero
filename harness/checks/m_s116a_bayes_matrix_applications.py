"""Checks for src/data/items/math/s116a-bayes-matrix-applications.yaml (116 sprint, 數A: Bayes' theorem, matrix applications).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Probabilities come from a joint distribution built step by step (or from listing equally likely outcomes) and
the definition P(A|B) = P(A and B) / P(B), so a check never just re-types Bayes' formula from the chapter.
Transformation matrices are built from where they send (1, 0) and (0, 1), found geometrically, not typed in.
"""

from __future__ import annotations

from itertools import permutations

import sympy as sp

R = sp.Rational


def _frac(r) -> tuple[int, int]:
    r = sp.Rational(r)
    return (int(r.p), int(r.q))


def _joint(prior: dict, likelihood: dict) -> dict:
    """Joint distribution P(cause, outcome) = P(cause) * P(outcome | cause)."""
    out = {}
    for c, pc in prior.items():
        for o, po in likelihood[c].items():
            out[(c, o)] = pc * po
    return out


def _cond(joint: dict, cause, outcome) -> sp.Rational:
    """P(cause | outcome) straight from the definition: P(cause and outcome) / P(outcome)."""
    p_outcome = sum(p for (c, o), p in joint.items() if o == outcome)
    return joint[(cause, outcome)] / p_outcome


def _point_rotated(x, y, theta):
    """Rotate (x, y) about the origin by theta via polar form: (r cos a, r sin a) -> (r cos(a+theta), r sin(a+theta))."""
    r = sp.sqrt(x**2 + y**2)
    a = sp.atan2(y, x)
    return (sp.simplify(r * sp.cos(a + theta)), sp.simplify(r * sp.sin(a + theta)))


def _matrix_from_images(f) -> sp.Matrix:
    """The matrix of a linear map: its columns are the images of (1, 0) and (0, 1)."""
    e1, e2 = f(1, 0), f(0, 1)
    return sp.Matrix([[e1[0], e2[0]], [e1[1], e2[1]]])


def _rotation(theta) -> sp.Matrix:
    return _matrix_from_images(lambda x, y: _point_rotated(x, y, theta))


# Mirror images found from the geometry of each line, not from a formula sheet.
_REFLECT = {
    "x-axis": lambda x, y: (x, -y),
    "y-axis": lambda x, y: (-x, y),
    "y=x": lambda x, y: (y, x),
    "y=-x": lambda x, y: (-y, -x),
}


def ba_turn_total_late(item: dict) -> list[bool]:
    """q-turn: rain tomorrow with probability 30%; late with probability 20% if it rains, 5% if not; P(late).
    Options: 5%, 9.5%, 12.5%, 20%, 25%."""
    joint = _joint({"rain": R(30, 100), "dry": R(70, 100)},
                   {"rain": {"late": R(20, 100), "on time": R(80, 100)}, "dry": {"late": R(5, 100), "on time": R(95, 100)}})
    p = sum(v for (c, o), v in joint.items() if o == "late")
    opts = [R(5, 100), R(95, 1000), R(125, 1000), R(20, 100), R(25, 100)]
    return [p == o for o in opts]


def ba_second_ball_red(item: dict) -> tuple[int, int]:
    """q1: 4 red and 6 white balls, draw two in order without replacement; P(second is red) as a/b."""
    balls = [f"R{i}" for i in range(4)] + [f"W{i}" for i in range(6)]
    space = list(permutations(balls, 2))
    p = R(sum(1 for w in space if w[1][0] == "R"), len(space))
    return _frac(p)


def ba_bag_from_red(item: dict) -> tuple[int, int]:
    """q2: fair coin picks bag 甲 (3 red, 2 white) or 乙 (1 red, 3 white); one ball drawn is red; P(it came from 甲)."""
    joint = _joint({"jia": R(1, 2), "yi": R(1, 2)},
                   {"jia": {"red": R(3, 5), "white": R(2, 5)}, "yi": {"red": R(1, 4), "white": R(3, 4)}})
    return _frac(_cond(joint, "jia", "red"))


def ba_screening_band(item: dict) -> list[bool]:
    """q3: 2% have the condition; test positive for 95% of them and for 10% of the others.
    P(condition | positive) lies in: <10%, 10-20%, 20-50%, 50-90%, >90%."""
    joint = _joint({"ill": R(2, 100), "well": R(98, 100)},
                   {"ill": {"pos": R(95, 100), "neg": R(5, 100)}, "well": {"pos": R(10, 100), "neg": R(90, 100)}})
    p = _cond(joint, "ill", "pos")  # 19/117
    bands = [(0, R(1, 10)), (R(1, 10), R(2, 10)), (R(2, 10), R(5, 10)), (R(5, 10), R(9, 10)), (R(9, 10), 1)]
    return [bool(lo < p) and bool(p < hi) for lo, hi in bands]


def ba_lunch_transition(item: dict) -> list[bool]:
    """q4: lunch at shop 甲 or 乙. From 甲: 0.9 甲, 0.1 乙 next day; from 乙: 0.4 甲, 0.6 乙.
    Column j = today's shop, row i = tomorrow's shop. Statements:
    (1) every column sums to 1; (2) every row sums to 1; (3) today 甲 -> P(乙 the day after tomorrow) = 0.15;
    (4) in the long run the share of days at 甲 approaches 0.8; (5) today 乙 -> P(乙 tomorrow) = 0.4."""
    A = sp.Matrix([[R(9, 10), R(4, 10)], [R(1, 10), R(6, 10)]])
    cols = all(sum(A[:, j]) == 1 for j in range(2))
    rows = all(sum(A[i, :]) == 1 for i in range(2))
    two_days = (A**2 * sp.Matrix([1, 0]))[1]
    v = (A - sp.eye(2)).nullspace()[0]
    steady = v / sum(v)
    tomorrow_yi_from_yi = (A * sp.Matrix([0, 1]))[1]
    return [cols, rows, two_days == R(15, 100), steady[0] == R(8, 10), tomorrow_yi_from_yi == R(4, 10)]


def ba_population_two_years(item: dict) -> sp.Integer:
    """q5: 1000 people, 500 in 甲 and 500 in 乙. Each year 70% of 甲 stay (30% move to 乙), 80% of 乙 stay (20% move to 甲).
    People in 甲 after two years."""
    A = sp.Matrix([[R(7, 10), R(2, 10)], [R(3, 10), R(8, 10)]])
    x = A**2 * sp.Matrix([500, 500])
    n = x[0]
    assert n.is_integer
    return sp.Integer(n)


def ba_rotation_30(item: dict) -> list[bool]:
    """q6: which matrix rotates the plane 30 degrees counterclockwise about the origin?"""
    target = _rotation(sp.pi / 6)
    h, s3 = R(1, 2), sp.sqrt(3) / 2
    opts = [
        sp.Matrix([[s3, -h], [h, s3]]),
        sp.Matrix([[s3, h], [-h, s3]]),
        sp.Matrix([[h, -s3], [s3, h]]),
        sp.Matrix([[s3, h], [h, -s3]]),
        sp.Matrix([[-h, s3], [s3, h]]),
    ]
    return [sp.simplify(o - target) == sp.zeros(2) for o in opts]


def ba_image_from_columns(item: dict) -> tuple[int, int]:
    """q7: a linear transformation sends (1,0) to (3,1) and (0,1) to (-1,2); the image of (2,3) is (a, b)."""
    A = sp.Matrix([[3, -1], [1, 2]])  # columns = the two given images
    img = A * sp.Matrix([2, 3])
    # cross-check with linearity: 2*(3,1) + 3*(-1,2)
    assert img == 2 * sp.Matrix([3, 1]) + 3 * sp.Matrix([-1, 2])
    return (int(img[0]), int(img[1]))


def ba_reflect_then_rotate(item: dict) -> list[bool]:
    """q8: reflect in the x-axis, then rotate 90 degrees counterclockwise. Which single transformation is this?
    Options: reflection in y=x; reflection in the y-axis; reflection in y=-x; rotation by 180 degrees; rotation by -90 degrees."""
    mirror_x = _matrix_from_images(_REFLECT["x-axis"])
    composite = _rotation(sp.pi / 2) * mirror_x  # the transformation applied first sits on the right
    opts = [
        _matrix_from_images(_REFLECT["y=x"]),
        _matrix_from_images(_REFLECT["y-axis"]),
        _matrix_from_images(_REFLECT["y=-x"]),
        _rotation(sp.pi),
        _rotation(-sp.pi / 2),
    ]
    return [sp.simplify(composite - o) == sp.zeros(2) for o in opts]
