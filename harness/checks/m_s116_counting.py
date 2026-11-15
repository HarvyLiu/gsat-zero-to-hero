"""Checks for src/data/items/math/s116-counting.yaml (116 sprint, D-10-3 systematic counting).

Each function recomputes its item's answer from the mathematics; none reads item["answer"].
Wherever it is cheap, a count is made by brute-force enumeration (itertools) rather than by the
formula the chapter teaches, so the check does not share the method it is checking.
"""

from __future__ import annotations

from itertools import combinations, permutations
from math import gcd

import sympy as sp

x = sp.Symbol("x")


# ---------- s116-counting ----------

def ct_turn_three_digit(item: dict) -> list[bool]:
    """q-turn: three-digit numbers from the digits 1, 2, 3, 4 with no digit repeated.
    Options: 4, 12, 24, 64, 81."""
    n = len(list(permutations([1, 2, 3, 4], 3)))
    return [n == o for o in (4, 12, 24, 64, 81)]


def ct_officers(item: dict) -> list[bool]:
    """q1: choose a class leader and a deputy (two different people) from 8 students.
    Options: 15, 16, 28, 56, 64."""
    n = len(list(permutations(range(8), 2)))
    return [n == o for o in (15, 16, 28, 56, 64)]


def ct_odd_three_digit(item: dict) -> sp.Integer:
    """q2: three-digit odd numbers from the digits 0–5, no digit repeated."""
    n = sum(1 for a, b, c in permutations(range(6), 3) if a != 0 and c % 2 == 1)
    return sp.Integer(n)


def ct_first_to_three(item: dict) -> sp.Integer:
    """q3: two players, every game has a winner, the first to win 3 games wins the match and play stops.
    Count the possible sequences of game winners, built game by game (a tree)."""
    def grow(a: int, b: int) -> int:
        if a == 3 or b == 3:
            return 1
        return grow(a + 1, b) + grow(a, b + 1)
    return sp.Integer(grow(0, 0))


def ct_mixed_committee(item: dict) -> sp.Integer:
    """q4: choose 4 people from 6 men and 5 women with at least one man and at least one woman."""
    people = ["M"] * 6 + ["W"] * 5
    n = sum(1 for c in combinations(range(11), 4) if {people[i] for i in c} == {"M", "W"})
    return sp.Integer(n)


def ct_equal_c10_3(item: dict) -> list[bool]:
    """q5: which equal C(10,3)? Options: C(10,7); P(10,3)/3!; 10×9×8; C(9,2)+C(9,3); 10!/3!."""
    target = len(list(combinations(range(10), 3)))
    options = [
        sp.binomial(10, 7),
        sp.ff(10, 3) / sp.factorial(3),
        sp.Integer(10 * 9 * 8),
        sp.binomial(9, 2) + sp.binomial(9, 3),
        sp.factorial(10) / sp.factorial(3),
    ]
    return [sp.Integer(target) == o for o in options]


def ct_multiples_3_or_5(item: dict) -> sp.Integer:
    """q6: integers from 1 to 200 that are multiples of 3 or of 5."""
    return sp.Integer(sum(1 for k in range(1, 201) if k % 3 == 0 or k % 5 == 0))


def ct_coprime_60(item: dict) -> sp.Integer:
    """q7: integers from 1 to 60 that share no common factor greater than 1 with 60."""
    return sp.Integer(sum(1 for k in range(1, 61) if gcd(k, 60) == 1))


def ct_binomial_coefficient(item: dict) -> sp.Integer:
    """q8: the coefficient of x⁴ in the expansion of (2x − 1)⁶."""
    return sp.Integer(sp.Poly(sp.expand((2 * x - 1) ** 6), x).coeff_monomial(x**4))
