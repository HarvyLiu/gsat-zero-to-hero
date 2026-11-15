"""Checks for src/data/items/math/s116-probability.yaml (116 sprint: classical probability, expected value).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Probabilities are found by listing an equally likely sample space with itertools and counting, so a check
never relies on the shortcut (inclusion-exclusion, complement, C(n, k)) the chapter teaches.
"""

from __future__ import annotations

from itertools import combinations, product

import sympy as sp


def _prob(space: list, event) -> sp.Rational:
    """Classical probability: outcomes in the event over all outcomes (all equally likely)."""
    return sp.Rational(sum(1 for w in space if event(w)), len(space))


def _frac(r: sp.Rational) -> tuple[int, int]:
    r = sp.Rational(r)
    return (int(r.p), int(r.q))


def _balls(red: int, white: int) -> list[str]:
    """Numbered balls, so that every draw is equally likely."""
    return [f"R{i}" for i in range(red)] + [f"W{i}" for i in range(white)]


def pr_turn_two_coins(item: dict) -> list[bool]:
    """q-turn: two fair coins, P(exactly one head). Options: 1/4, 1/3, 1/2, 2/3, 3/4."""
    space = list(product("HT", repeat=2))
    p = _prob(space, lambda w: w.count("H") == 1)
    opts = [sp.Rational(1, 4), sp.Rational(1, 3), sp.Rational(1, 2), sp.Rational(2, 3), sp.Rational(3, 4)]
    return [p == o for o in opts]


def pr_dice_sum_8(item: dict) -> list[bool]:
    """q1: two fair dice, P(sum = 8). Options: 1/11, 1/12, 5/36, 1/6, 7/36."""
    space = list(product(range(1, 7), repeat=2))
    p = _prob(space, lambda w: sum(w) == 8)
    opts = [sp.Rational(1, 11), sp.Rational(1, 12), sp.Rational(5, 36), sp.Rational(1, 6), sp.Rational(7, 36)]
    return [p == o for o in opts]


def pr_two_red_one_white(item: dict) -> tuple[int, int]:
    """q2: 5 red, 4 white, take 3; P(exactly 2 red and 1 white) as a/b in lowest terms."""
    space = list(combinations(_balls(5, 4), 3))
    p = _prob(space, lambda w: sum(b[0] == "R" for b in w) == 2)
    return _frac(p)


def pr_multiple_3_or_5(item: dict) -> tuple[int, int]:
    """q3: pick an integer from 1 to 50; P(multiple of 3 or of 5) as a/b in lowest terms."""
    space = list(range(1, 51))
    p = _prob(space, lambda n: n % 3 == 0 or n % 5 == 0)
    return _frac(p)


def pr_event_statements(item: dict) -> list[bool]:
    """q4: P(A) = 1/2, P(B) = 2/5, P(A∩B) = 1/5. Statements: P(A∪B) = 7/10; A, B mutually exclusive;
    P(A') = 1/2; P(A∩B') = 3/10; P(A'∩B') = 1/10.
    Built on a model: 10 equally likely outcomes with |A| = 5, |B| = 4, |A∩B| = 2. Every statement only
    depends on the three given probabilities, so one model decides them all."""
    S = set(range(10))
    A = {0, 1, 2, 3, 4}
    B = {3, 4, 5, 6}
    P = lambda E: sp.Rational(len(E), len(S))  # noqa: E731
    assert (P(A), P(B), P(A & B)) == (sp.Rational(1, 2), sp.Rational(2, 5), sp.Rational(1, 5))
    Ac, Bc = S - A, S - B
    return [
        P(A | B) == sp.Rational(7, 10),
        len(A & B) == 0,
        P(Ac) == sp.Rational(1, 2),
        P(A & Bc) == sp.Rational(3, 10),
        P(Ac & Bc) == sp.Rational(1, 10),
    ]


def pr_coin_at_least_one_head(item: dict) -> tuple[int, int]:
    """q5: toss a fair coin 4 times; P(at least one head) as a/b in lowest terms."""
    space = list(product("HT", repeat=4))
    p = _prob(space, lambda w: "H" in w)
    return _frac(p)


def pr_fair_game(item: dict) -> list[bool]:
    """q6: one fair die; 1 wins 60, 2 or 3 wins 15, else 0; each game costs 15. Options: average gain 5;
    average loss 5; average gain 0 (fair); average gain 15; every game pays back exactly 15."""
    prize = {1: 60, 2: 15, 3: 15, 4: 0, 5: 0, 6: 0}
    net = sum(sp.Rational(prize[f] - 15, 6) for f in range(1, 7))
    every_game_pays_15 = all(prize[f] == 15 for f in range(1, 7))
    return [net == 5, net == -5, net == 0, net == 15, every_game_pays_15]


def pr_expected_red(item: dict) -> tuple[int, int]:
    """q7: 2 red, 3 white, take 2; expected number of red balls as a/b in lowest terms."""
    space = list(combinations(_balls(2, 3), 2))
    e = sum(sp.Rational(sum(b[0] == "R" for b in w), len(space)) for w in space)
    return _frac(e)
