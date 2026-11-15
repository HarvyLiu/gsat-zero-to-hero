"""Checks for src/data/items/math/s116-sets-toolbox.yaml (116 sprint, D-10-1 sets toolbox).

Each function recomputes its item's answer from the mathematics; none reads item["answer"].
Finite sets are built by filtering an explicit range, and solution sets of inequalities come from
sympy.solveset over the reals, so every set operation is done by SymPy rather than by hand.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x", real=True)
R = sp.S.Reals


def _fs(it) -> sp.FiniteSet:
    return sp.FiniteSet(*[sp.Integer(v) for v in it])


def _divisors(n: int) -> sp.FiniteSet:
    return _fs(d for d in range(1, n + 1) if n % d == 0)


# ---------- s116-sets-toolbox ----------

def st_turn_divisor_intersection(item: dict) -> list[bool]:
    """q-turn: A = positive divisors of 12, B = positive divisors of 18; which set is A ∩ B?
    Options: {1,2,3,6}, {1,2,3,4,6,9,12,18}, {4,12}, {6}, {1,2,3,6,9}."""
    A, B = _divisors(12), _divisors(18)
    target = A.intersect(B)
    options = [
        _fs([1, 2, 3, 6]),
        _fs([1, 2, 3, 4, 6, 9, 12, 18]),
        _fs([4, 12]),
        _fs([6]),
        _fs([1, 2, 3, 6, 9]),
    ]
    return [o == target for o in options]


def st_membership_subset(item: dict) -> list[bool]:
    """q1: A = {x | x is an integer and x² < 5}. Which statements are true?
      (1) 0 ∈ A   (2) {1, 2} ⊂ A   (3) {0} ∈ A   (4) ∅ ⊂ A   (5) −3 ∈ A
    A is found by filtering a range wide enough to hold every integer with x² < 5 (|x| ≤ 2)."""
    A = _fs(n for n in range(-10, 11) if n * n < 5)
    assert all(n * n >= 5 for n in (-10, 10))  # the range is wide enough: x² < 5 forces |x| < 3
    return [
        bool(A.contains(sp.Integer(0))),
        bool(_fs([1, 2]).is_subset(A)),
        bool(A.contains(sp.FiniteSet(sp.Integer(0)))),  # an element of A is a number, never a set
        bool(sp.S.EmptySet.is_subset(A)),
        bool(A.contains(sp.Integer(-3))),
    ]


def st_interval_complement(item: dict) -> list[bool]:
    """q2: U = ℝ, A = {x | x² − 2x − 8 ≤ 0}, B = {x | x > 1}. Which interval is A ∩ B'?
    Options: [−2, 1], [−2, 1), (1, 4], [−2, 4], (−∞, 1]."""
    A = sp.solveset(x**2 - 2 * x - 8 <= 0, x, domain=R)
    B = sp.solveset(x > 1, x, domain=R)
    target = A.intersect(R - B)
    options = [
        sp.Interval(-2, 1),
        sp.Interval.Ropen(-2, 1),
        sp.Interval.Lopen(1, 4),
        sp.Interval(-2, 4),
        sp.Interval(-sp.oo, 1),
    ]
    return [sp.simplify(o.symmetric_difference(target)) == sp.S.EmptySet for o in options]


def st_venn_both(item: dict) -> sp.Integer:
    """q3: 40 students; 23 in club A, 18 in club B, 7 in neither. How many are in both?
    n(A ∪ B) = 40 − 7, and n(A ∪ B) = n(A) + n(B) − n(A ∩ B); solve for n(A ∩ B).
    Cross-check by building one concrete roster with those counts."""
    k = sp.Symbol("k", integer=True)
    both = sp.solve(sp.Eq(23 + 18 - k, 40 - 7), k)[0]
    students = range(40)
    a_only, b_only = 23 - both, 18 - both
    A = set(range(0, a_only + both))
    B = set(range(a_only, a_only + both + b_only))
    assert len(A) == 23 and len(B) == 18 and len(set(students) - (A | B)) == 7
    assert len(A & B) == both
    return sp.Integer(both)


def st_set_operations(item: dict) -> list[bool]:
    """q4: U = {1, …, 10}, A = multiples of 2 in U, B = multiples of 5 in U. Which are true?
      (1) A ∩ B = {10}          (2) A' ∩ B = {5}          (3) (A ∪ B)' = {1, 3, 7, 9}
      (4) (A ∩ B)' = A' ∩ B'    (5) n(A ∪ B) = 7"""
    U = _fs(range(1, 11))
    A = _fs(n for n in range(1, 11) if n % 2 == 0)
    B = _fs(n for n in range(1, 11) if n % 5 == 0)

    def comp(S):
        return U - S

    return [
        A.intersect(B) == _fs([10]),
        comp(A).intersect(B) == _fs([5]),
        comp(A.union(B)) == _fs([1, 3, 7, 9]),
        comp(A.intersect(B)) == comp(A).intersect(comp(B)),
        len(A.union(B)) == 7,
    ]
