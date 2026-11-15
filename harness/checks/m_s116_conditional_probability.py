"""Checks for src/data/items/math/s116-conditional-probability.yaml (116 sprint: subjective and objective
probability, conditional probability, independence, basic Bayes).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Conditional probabilities are found by listing a sample space and counting inside the given event (or, for
independent trials and two-stage draws, by building the weighted product space), so a check never relies on
the formula P(B|A) = P(A∩B)/P(A) or on Bayes' theorem as written in the chapter.
"""

from __future__ import annotations

from itertools import permutations, product

import sympy as sp


def _frac(r) -> tuple[int, int]:
    r = sp.Rational(r)
    return (int(r.p), int(r.q))


def _cond(space: list, given, event) -> sp.Rational:
    """Equally likely outcomes: count the outcomes of `given` that are also in `event`."""
    restricted = [w for w in space if given(w)]
    return sp.Rational(sum(1 for w in restricted if event(w)), len(restricted))


def cp_turn_two_coins(item: dict) -> list[bool]:
    """q-turn: two fair coins; given at least one head, P(both heads). Options: 1/4, 1/3, 1/2, 2/3, 3/4."""
    space = list(product("HT", repeat=2))
    p = _cond(space, lambda w: "H" in w, lambda w: w == ("H", "H"))
    opts = [sp.Rational(1, 4), sp.Rational(1, 3), sp.Rational(1, 2), sp.Rational(2, 3), sp.Rational(3, 4)]
    return [p == o for o in opts]


def _consistent(pa, pb, pab, pu) -> bool:
    """Can some probability give P(A)=pa, P(B)=pb, P(A∩B)=pab, P(A∪B)=pu? Solve for the four Venn
    regions and ask that they are non-negative and that the union is what was claimed."""
    pa, pb, pab, pu = (sp.Rational(str(x)) for x in (pa, pb, pab, pu))
    regions = [pab, pa - pab, pb - pab]
    regions.append(1 - sum(regions))
    union = sum(regions[:3])
    return all(r >= 0 for r in regions) and union == pu


def cp_subjective_consistent(item: dict) -> list[bool]:
    """q1: which (P(A), P(B), P(A∩B), P(A∪B)) assignment is possible?"""
    opts = [
        ("0.6", "0.5", "0.2", "0.8"),
        ("0.4", "0.3", "0.5", "0.2"),
        ("0.7", "0.5", "0.3", "0.9"),
        ("0.8", "0.6", "0.3", "1.1"),
        ("0.9", "0.4", "0.2", "0.9"),
    ]
    return [_consistent(*o) for o in opts]


def cp_spinner_not_red(item: dict) -> tuple[int, int]:
    """q2: 500 spins: red 180, yellow 145, blue 175; relative frequency of 'not red' as a/b."""
    counts = {"red": 180, "yellow": 145, "blue": 175}
    total = sum(counts.values())
    assert total == 500
    return _frac(sp.Rational(total - counts["red"], total))


def cp_club_table(item: dict) -> tuple[int, int]:
    """q3: grade 10: 96 in a club, 64 not; grade 11: 70 in a club, 70 not. P(grade 11 | in a club)."""
    people = [("10", True)] * 96 + [("10", False)] * 64 + [("11", True)] * 70 + [("11", False)] * 70
    assert len(people) == 300
    return _frac(_cond(people, lambda w: w[1], lambda w: w[0] == "11"))


def cp_die_independence(item: dict) -> list[bool]:
    """q4: one fair die; A = even, B = {1,2,3,4}, D = prime. Statements: A, B independent; A, D independent;
    P(A|D) = 1/3; B, D mutually exclusive; A', B independent."""
    S = set(range(1, 7))
    A = {f for f in S if f % 2 == 0}
    B = {1, 2, 3, 4}
    D = {f for f in S if sp.isprime(f)}
    P = lambda E: sp.Rational(len(E), len(S))  # noqa: E731
    indep = lambda X, Y: P(X & Y) == P(X) * P(Y)  # noqa: E731
    return [
        indep(A, B),
        indep(A, D),
        sp.Rational(len(A & D), len(D)) == sp.Rational(1, 3),
        len(B & D) == 0,
        indep(S - A, B),
    ]


def cp_three_solvers(item: dict) -> tuple[int, int]:
    """q5: three people solve independently with probabilities 2/3, 1/2, 2/5; P(at least one solves)."""
    ps = [sp.Rational(2, 3), sp.Rational(1, 2), sp.Rational(2, 5)]
    total = sp.Integer(0)
    for w in product([True, False], repeat=3):
        weight = sp.Integer(1)
        for solved, p in zip(w, ps):
            weight *= p if solved else 1 - p
        if any(w):
            total += weight
    return _frac(total)


def cp_two_red_no_replacement(item: dict) -> list[bool]:
    """q6: 5 red, 3 white, draw two in order without replacement; P(both red).
    Options: 25/64, 5/14, 5/8, 4/7, 15/56."""
    balls = [f"R{i}" for i in range(5)] + [f"W{i}" for i in range(3)]
    space = list(permutations(balls, 2))
    p = sp.Rational(sum(1 for a, b in space if a[0] == "R" and b[0] == "R"), len(space))
    opts = [sp.Rational(25, 64), sp.Rational(5, 14), sp.Rational(5, 8), sp.Rational(4, 7), sp.Rational(15, 56)]
    return [p == o for o in opts]


def cp_two_bags(item: dict) -> tuple[int, int, int, int]:
    """q7: fair coin picks bag X (2 red, 3 white) on heads, bag Y (4 red, 1 white) on tails; draw one ball.
    Returns (a, b, c, d) with P(red) = a/b and P(bag X | red) = c/d."""
    bags = {"X": ["R"] * 2 + ["W"] * 3, "Y": ["R"] * 4 + ["W"] * 1}
    # weighted outcomes (bag, ball index) -> probability
    outcomes = {(bag, i): sp.Rational(1, 2) * sp.Rational(1, len(balls)) for bag, balls in bags.items() for i in range(len(balls))}
    red = {k: v for k, v in outcomes.items() if bags[k[0]][k[1]] == "R"}
    p_red = sum(red.values())
    p_x_given_red = sum(v for k, v in red.items() if k[0] == "X") / p_red
    return _frac(p_red) + _frac(p_x_given_red)
