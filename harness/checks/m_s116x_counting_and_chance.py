"""Checks for src/data/items/math/s116x-counting-and-chance.yaml (116 sprint, cross-unit chapter:
counting and probability solved several ways).

Each item check recomputes its answer from the mathematics with SymPy (by brute-force listing of the
sample space wherever that is feasible); none reads item["answer"].

The chapter solves six worked problems two to four different ways. `_worked_examples()` recomputes
every way independently and asserts that all ways agree with each other and with the numbers printed in
the lesson. It runs when this module is imported, so any check in the bank fails if a worked example is
wrong.
"""

from __future__ import annotations

from itertools import combinations, permutations, product

import sympy as sp

R = sp.Rational


def _frac(r) -> tuple[int, int]:
    r = sp.Rational(r)
    return (int(r.p), int(r.q))


def _digits(n: int) -> tuple[int, ...]:
    """A non-negative integer as its fill cells, e.g. 120 -> (1, 2, 0)."""
    return tuple(int(c) for c in str(n))


def _lattice_paths(w: int, h: int, blocked: set[tuple[int, int]] | None = None) -> int:
    """Shortest paths (one unit right or up per step) from (0,0) to (w,h), by labelling every lattice
    point with the number of ways to reach it (left neighbour + lower neighbour); blocked points get 0."""
    blocked = blocked or set()
    f: dict[tuple[int, int], int] = {}
    for x in range(w + 1):
        for y in range(h + 1):
            if (x, y) in blocked:
                f[(x, y)] = 0
            elif (x, y) == (0, 0):
                f[(x, y)] = 1
            else:
                f[(x, y)] = f.get((x - 1, y), 0) + f.get((x, y - 1), 0)
    return f[(w, h)]


def _brute_paths(w: int, h: int, avoid: tuple[int, int]) -> int:
    """The same count by listing every word of w R's and h U's and walking it."""
    n = 0
    for ups in combinations(range(w + h), h):
        x = y = 0
        ok = True
        for i in range(w + h):
            if i in ups:
                y += 1
            else:
                x += 1
            if (x, y) == avoid:
                ok = False
        n += ok
    return n


# ---------------------------------------------------------------------------
# worked examples in the lesson: every way, separately
# ---------------------------------------------------------------------------
def _worked_examples() -> None:
    C = sp.binomial

    # Problem 1: 4 boys, 3 girls, choose 3 with at least one girl.
    people = ["B"] * 4 + ["G"] * 3
    brute = sum(1 for s in combinations(range(7), 3) if any(people[i] == "G" for i in s))
    cases = C(3, 1) * C(4, 2) + C(3, 2) * C(4, 1) + C(3, 3)
    assert (C(3, 1) * C(4, 2), C(3, 2) * C(4, 1), C(3, 3)) == (18, 12, 1)
    complement = C(7, 3) - C(4, 3)
    assert (C(7, 3), C(4, 3)) == (35, 4)
    assert brute == cases == complement == 31
    # the overcount "pick a girl first, then any two" gives 45, not 31
    assert C(3, 1) * C(6, 2) == 45

    # Problem 2: 1..90, multiples of none of 2, 3, 5.
    nums = range(1, 91)
    brute = sum(1 for n in nums if n % 2 and n % 3 and n % 5)
    m = lambda d: 90 // d  # noqa: E731
    assert (m(2), m(3), m(5), m(6), m(10), m(15), m(30)) == (45, 30, 18, 15, 9, 6, 3)
    union = m(2) + m(3) + m(5) - m(6) - m(10) - m(15) + m(30)
    assert union == 66
    incl_excl = 90 - union
    # sieve layer by layer: odd numbers, then drop multiples of 3, then of 5
    odd = [n for n in nums if n % 2]
    odd_not3 = [n for n in odd if n % 3]
    assert len(odd) == 45 and len(odd) - len(odd_not3) == 15 and len(odd_not3) == 30
    sieve = [n for n in odd_not3 if n % 5]
    assert len(odd_not3) - len(sieve) == 6
    assert R(len(odd_not3), len(odd)) == R(2, 3) and R(len(sieve), len(odd_not3)) == R(4, 5)
    product_rule = 90 * R(1, 2) * R(2, 3) * R(4, 5)
    # one block of 30 repeated three times
    block = [n for n in range(1, 31) if n % 2 and n % 3 and n % 5]
    assert block == [1, 7, 11, 13, 17, 19, 23, 29]
    periodic = 3 * len(block)
    assert brute == incl_excl == len(sieve) == product_rule == periodic == 24
    # Venn regions printed in the figure
    regions = {
        "only2": sum(1 for n in nums if n % 2 == 0 and n % 3 and n % 5),
        "only3": sum(1 for n in nums if n % 3 == 0 and n % 2 and n % 5),
        "only5": sum(1 for n in nums if n % 5 == 0 and n % 2 and n % 3),
        "23": sum(1 for n in nums if n % 6 == 0 and n % 5),
        "25": sum(1 for n in nums if n % 10 == 0 and n % 3),
        "35": sum(1 for n in nums if n % 15 == 0 and n % 2),
        "235": sum(1 for n in nums if n % 30 == 0),
    }
    assert regions == {"only2": 24, "only3": 12, "only5": 6, "23": 12, "25": 6, "35": 3, "235": 3}
    # the product shortcut is not a general rule: 1..10 has 2 such numbers, 10*(1/2)(2/3)(4/5) is not 2
    assert sum(1 for n in range(1, 11) if n % 2 and n % 3 and n % 5) == 2
    assert 10 * R(1, 2) * R(2, 3) * R(4, 5) == R(8, 3)
    # independence view: in 1..90 the three events are independent; in 1..10 A and B are not
    P90 = lambda f: R(sum(1 for n in nums if f(n)), 90)  # noqa: E731
    pa, pb5, pc = P90(lambda n: n % 2 == 0), P90(lambda n: n % 3 == 0), P90(lambda n: n % 5 == 0)
    assert P90(lambda n: n % 6 == 0) == pa * pb5 == R(1, 6)
    assert P90(lambda n: n % 10 == 0) == pa * pc and P90(lambda n: n % 15 == 0) == pb5 * pc
    assert P90(lambda n: n % 30 == 0) == pa * pb5 * pc
    assert (1 - pa) * (1 - pb5) * (1 - pc) == R(4, 15) and 90 * R(4, 15) == 24
    # the complements are independent too (the lesson uses this for "none of the three")
    assert P90(lambda n: n % 2 and n % 3 and n % 5) == (1 - pa) * (1 - pb5) * (1 - pc)
    P10 = lambda f: R(sum(1 for n in range(1, 11) if f(n)), 10)  # noqa: E731
    assert P10(lambda n: n % 6 == 0) == R(1, 10) and P10(lambda n: n % 2 == 0) * P10(lambda n: n % 3 == 0) == R(3, 20)
    # odd multiples of 3, and the multiples of 5 left after the second sieve
    assert len([n for n in odd if n % 3 == 0]) == 15
    assert [n for n in odd_not3 if n % 5 == 0] == [5, 25, 35, 55, 65, 85]

    # Problem 3: grid (0,0) -> (4,3), not through P(2,1).
    total = C(7, 3)
    through = C(3, 1) * C(4, 2)
    assert (total, through) == (35, 18)
    labels = _lattice_paths(4, 3, {(2, 1)})
    assert total - through == labels == _brute_paths(4, 3, (2, 1)) == 17

    # Problem 4: 3 red 2 white, two draws without replacement.
    balls = ["R", "R", "R", "W", "W"]
    pairs = list(permutations(range(5), 2))
    assert len(pairs) == 20
    second_red = [p for p in pairs if balls[p[1]] == "R"]
    both_red = [p for p in second_red if balls[p[0]] == "R"]
    table = {
        (a, b): sum(1 for p in pairs if balls[p[0]] == a and balls[p[1]] == b) for a in "RW" for b in "RW"
    }
    assert table == {("R", "R"): 6, ("R", "W"): 6, ("W", "R"): 6, ("W", "W"): 2}
    tree = R(3, 5) * R(2, 4) + R(2, 5) * R(3, 4)
    counting = R(len(second_red), len(pairs))
    symmetry = R(3, 5)
    assert tree == counting == symmetry == R(3, 5)
    cond_tree = (R(3, 5) * R(2, 4)) / tree
    cond_count = R(len(both_red), len(second_red))
    cond_symmetry = R(2, 4)  # the other four balls: 2 red, 2 white
    assert cond_tree == cond_count == cond_symmetry == R(1, 2)

    # Problem 5: 40% by bus, late 10%; others late 5%; P(bus | late).
    pb, lb, lo = R(2, 5), R(1, 10), R(1, 20)
    tree = pb * lb / (pb * lb + (1 - pb) * lo)
    assert (pb * lb, (1 - pb) * lo) == (R(4, 100), R(3, 100))
    late_bus, late_other = 400 * lb, 600 * lo
    assert (late_bus, late_other) == (40, 30)
    assert (400 - late_bus, 600 - late_other, 1000 - late_bus - late_other) == (360, 570, 930)
    table = R(late_bus, late_bus + late_other)
    ratio = (R(4, 6) * R(10, 5))  # odds bus:other among the late = 4:6 times 10:5 = 4:3
    assert ratio == R(4, 3)
    assert tree == table == ratio / (1 + ratio) == R(4, 7)
    # area picture: widths 4 and 6, heights 10 and 5 (percent) -> 40 and 30 cells
    assert (4 * 10, 6 * 5) == (40, 30)

    # Problem 6: two dice, score = sum, plus 6 if a double.
    cells = [(i, j) for i in range(1, 7) for j in range(1, 7)]
    score = lambda i, j: i + j + (6 if i == j else 0)  # noqa: E731
    assert all(score(i, j) == score(j, i) for i, j in cells)  # table symmetric about the diagonal
    full = R(sum(score(i, j) for i, j in cells), 36)
    assert sum(score(i, j) for i, j in cells) == 288 and sum(i + j for i, j in cells) == 252
    # distribution table printed in the lesson
    dist: dict[int, int] = {}
    for i, j in cells:
        dist[score(i, j)] = dist.get(score(i, j), 0) + 1
    assert dist == {3: 2, 4: 2, 5: 4, 6: 4, 7: 6, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1, 14: 1, 16: 1, 18: 1}
    by_dist = R(sum(v * c for v, c in dist.items()), 36)
    # row by row: first die i, average over the second die
    rows = [R(sum(score(i, j) for j in range(1, 7)), 6) for i in range(1, 7)]
    assert rows == [i + R(9, 2) for i in range(1, 7)]
    by_rows = sum(rows) / 6
    # split into parts: the sum part averages 7, the bonus part averages 6 * 6/36 = 1
    split = (R(7, 2) + R(7, 2)) + 6 * R(6, 36)
    assert full == by_dist == by_rows == split == 8


_worked_examples()


# ---------------------------------------------------------------------------
# item checks
# ---------------------------------------------------------------------------
def cc_turn_die_three_times(item: dict) -> list[bool]:
    """q-turn: a fair die rolled 3 times; P(at least one 6). Options: 1/2, 91/216, 125/216, 1/216, 75/216."""
    space = list(product(range(1, 7), repeat=3))
    p = R(sum(1 for w in space if 6 in w), len(space))
    assert p == 1 - R(5, 6) ** 3
    opts = [R(1, 2), R(91, 216), R(125, 216), R(1, 216), R(75, 216)]
    return [p == o for o in opts]


def cc_mixed_committee(item: dict) -> tuple[int, ...]:
    """q1: 5 boys and 4 girls; choose 4 with at least one boy and at least one girl."""
    people = ["B"] * 5 + ["G"] * 4
    n = sum(1 for s in combinations(range(9), 4) if {people[i] for i in s} == {"B", "G"})
    assert n == sp.binomial(9, 4) - sp.binomial(5, 4) - sp.binomial(4, 4)
    return _digits(n)


def cc_not_multiple_3_5_7(item: dict) -> tuple[int, ...]:
    """q2: how many of 1..105 are multiples of none of 3, 5, 7?"""
    n = sum(1 for k in range(1, 106) if k % 3 and k % 5 and k % 7)
    return _digits(n)


def cc_grid_avoid_point(item: dict) -> tuple[int, ...]:
    """q3: shortest paths (0,0) -> (5,3) that do not pass through (2,2)."""
    n = _brute_paths(5, 3, (2, 2))
    assert n == _lattice_paths(5, 3, {(2, 2)})
    return _digits(n)


def cc_third_ball_white(item: dict) -> list[bool]:
    """q4: 4 red and 3 white; three draws without replacement; P(third ball white).
    Options: 3/7, 2/7, 1/3, 4/7, 3/5."""
    balls = ["R"] * 4 + ["W"] * 3
    seqs = list(permutations(range(7), 3))
    p = R(sum(1 for s in seqs if balls[s[2]] == "W"), len(seqs))
    opts = [R(3, 7), R(2, 7), R(1, 3), R(4, 7), R(3, 5)]
    return [p == o for o in opts]


def cc_coin_then_box(item: dict) -> tuple[int, int]:
    """q5: a fair coin picks box X (2 red, 3 white) on heads, box Y (4 red, 1 white) on tails; one ball
    is drawn. Given it is red, P(it came from box Y). Built as a weighted sample space."""
    boxes = {"X": ["R"] * 2 + ["W"] * 3, "Y": ["R"] * 4 + ["W"] * 1}
    # each (box, ball) outcome has weight 1/2 * 1/5
    outcomes = [(b, c) for b, balls in boxes.items() for c in balls]
    red = [o for o in outcomes if o[1] == "R"]
    return _frac(R(sum(1 for o in red if o[0] == "Y"), len(red)))


def cc_dice_prize(item: dict) -> tuple[int, ...]:
    """q6: two fair dice; 30 dollars for every die showing 6, plus 12 if the two dice match.
    Expected prize, averaged over the 36 equally likely cells."""
    cells = list(product(range(1, 7), repeat=2))
    prize = lambda i, j: 30 * ((i == 6) + (j == 6)) + (12 if i == j else 0)  # noqa: E731
    e = R(sum(prize(i, j) for i, j in cells), 36)
    assert e.q == 1
    return _digits(int(e))


def cc_method_choice(item: dict) -> list[bool]:
    """q7: p = P(at least one 6 in four rolls of a fair die). Statements:
    (1) p = 1 - (5/6)^4; (2) adding the classes 'exactly k sixes', k = 1..4, gives p;
    (3) p = 4 * 1/6; (4) the complement needs one class against four for the direct count;
    (5) p < 1/2."""
    space = list(product(range(1, 7), repeat=4))
    p = R(sum(1 for w in space if 6 in w), len(space))
    classes_direct = [k for k in range(0, 5) if k >= 1]  # exactly k sixes, k = 1..4
    by_classes = sum(R(sum(1 for w in space if w.count(6) == k), len(space)) for k in classes_direct)
    classes_complement = [0]  # exactly zero sixes
    return [
        p == 1 - R(5, 6) ** 4,
        by_classes == p,
        p == 4 * R(1, 6),
        len(classes_complement) == 1 and len(classes_direct) == 4 and 1 - R(sum(1 for w in space if w.count(6) == 0), len(space)) == p,
        p < R(1, 2),
    ]
