"""Checks for src/data/items/math/s116-sequences.yaml (116 sprint: sequences, series and recursion).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Sequences are generated term by term from their definitions (recursion or a_1, d / a_1, r), so a check
never relies on the closed-form formula the chapter teaches.
"""

from __future__ import annotations

import sympy as sp

k = sp.Symbol("k", integer=True, positive=True)
i = sp.Symbol("i", integer=True, positive=True)


def _recurse(a1, step, n: int) -> list:
    """The first n terms of a_1 = a1, a_{m+1} = step(a_m, m)."""
    terms = [sp.Integer(a1)]
    for m in range(1, n):
        terms.append(sp.Integer(step(terms[-1], m)))
    return terms


def sq_turn_recursion(item: dict) -> list[bool]:
    """q-turn: a_1 = 1, a_{n+1} = 2a_n + 1; a_4 = ? Options: 7, 8, 15, 16, 31."""
    a4 = _recurse(1, lambda a, m: 2 * a + 1, 4)[-1]
    return [a4 == o for o in (7, 8, 15, 16, 31)]


def sq_ap_term(item: dict) -> list[bool]:
    """q1: arithmetic sequence with a_2 = 5, a_7 = 20; a_20 = ? Options: 56, 59, 60, 62, 65."""
    a1, d = sp.symbols("a1 d")
    sol = sp.solve([sp.Eq(a1 + d, 5), sp.Eq(a1 + 6 * d, 20)], [a1, d], dict=True)[0]
    terms = _recurse(sol[a1], lambda a, m: a + sol[d], 20)
    return [terms[-1] == o for o in (56, 59, 60, 62, 65)]


def sq_ap_sum(item: dict) -> sp.Integer:
    """q2: 4 + 7 + 10 + ... + 61 (difference 3)."""
    terms, t = [], sp.Integer(4)
    while t <= 61:
        terms.append(t)
        t += 3
    assert terms[-1] == 61
    return sp.Integer(sum(terms))


def sq_gp_sum(item: dict) -> sp.Integer:
    """q3: 2 + 6 + 18 + ... + 2·3^6 (ratio 3)."""
    terms = _recurse(2, lambda a, m: 3 * a, 7)
    assert terms[-1] == 2 * 3**6
    return sp.Integer(sum(terms))


def sq_gp_statements(item: dict) -> list[bool]:
    """q4: geometric sequence a_1 = 3, r = −2. Statements: a_5 = 48; a_4 = 24; a_1+…+a_4 = −15;
    a_2·a_4 = a_3²; every term is positive."""
    a = [None] + _recurse(3, lambda x, m: -2 * x, 30)  # 1-based
    return [
        a[5] == 48,
        a[4] == 24,
        sum(a[1:5]) == -15,
        a[2] * a[4] == a[3] ** 2,
        all(t > 0 for t in a[1:]),
    ]


def sq_recursion_value(item: dict) -> sp.Integer:
    """q5: a_1 = 1, a_{n+1} = 2a_n + 3; a_5 = ?"""
    return _recurse(1, lambda a, m: 2 * a + 3, 5)[-1]


def sq_recursion_plus_2n(item: dict) -> list[bool]:
    """q6: a_1 = 3, a_{n+1} = a_n + 2n; a_6 = ? Options: 23, 31, 33, 35, 45."""
    a6 = _recurse(3, lambda a, m: a + 2 * m, 6)[-1]
    return [a6 == o for o in (23, 31, 33, 35, 45)]


def sq_log_first_exceed(item: dict) -> list[bool]:
    """q7: smallest positive integer n with 2^n > 10^6. Options: 18, 19, 20, 21, 30.
    Found by exact integer comparison, so the log 2 ≈ 0.3010 hint is not needed to check it."""
    n = 1
    while not sp.Integer(2) ** n > sp.Integer(10) ** 6:
        n += 1
    return [n == o for o in (18, 19, 20, 21, 30)]


def sq_induction_step(item: dict) -> list[bool]:
    """q8: proving 1·2 + 2·3 + … + n(n+1) = n(n+1)(n+2)/3 by induction. Going from n = k to n = k+1,
    which term is added to the left side? Options: k(k+1); (k+1)(k+2); (k+1)(k+2)(k+3)/3; (k+2)(k+3); k+1.
    Also confirms the identity itself holds for all n (so the item proves a true statement)."""
    lhs = lambda n: sp.summation(i * (i + 1), (i, 1, n))  # noqa: E731
    assert sp.simplify(lhs(k) - k * (k + 1) * (k + 2) / 3) == 0
    added = sp.simplify(lhs(k + 1) - lhs(k))
    options = [k * (k + 1), (k + 1) * (k + 2), (k + 1) * (k + 2) * (k + 3) / 3, (k + 2) * (k + 3), k + 1]
    return [sp.simplify(added - o) == 0 for o in options]
