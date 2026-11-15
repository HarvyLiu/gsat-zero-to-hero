"""Checks for src/data/items/math/x-random-variables-binomial.yaml (分科 advanced tool, not in 學測: discrete
random variables, linearity of expectation, the binomial distribution, the geometric distribution (數甲 only)
and the 合理性檢定 use of a binomial tail).

Each item function recomputes its answer from the mathematics with SymPy; none reads item["answer"].
Probabilities are found by building the sample space (or the weighted product space of independent trials)
and summing, so a check never relies on the formula C(n,k) p^k (1-p)^(n-k) or on E = np as the chapter writes
them. `chapter_examples()` re-derives every number in the chapter's worked examples, each worked way
separately, and runs at import so a wrong example number stops the harness.
"""

from __future__ import annotations

from itertools import combinations, permutations, product

import sympy as sp

R = sp.Rational


def _frac(r) -> tuple[int, int]:
    r = sp.Rational(r)
    return (int(r.p), int(r.q))


def _trials(p, n: int) -> dict[tuple[bool, ...], sp.Rational]:
    """All 2^n success/failure sequences of n independent trials with success probability p, with weights."""
    p = sp.nsimplify(p)
    return {w: sp.Mul(*[p if s else 1 - p for s in w]) for w in product([True, False], repeat=n)}


def _successes_dist(p, n: int) -> dict[int, sp.Rational]:
    """Distribution of the number of successes, by summing sequence weights (no binomial formula)."""
    dist: dict[int, sp.Rational] = {}
    for w, pr in _trials(p, n).items():
        dist[sum(w)] = dist.get(sum(w), 0) + pr
    return {k: sp.nsimplify(v) for k, v in dist.items()}


def _mean(dist: dict) -> sp.Rational:
    return sp.nsimplify(sum(k * v for k, v in dist.items()))


def _var(dist: dict) -> sp.Rational:
    m = _mean(dist)
    return sp.nsimplify(sum((k - m) ** 2 * v for k, v in dist.items()))


def _die_options(p, opts) -> list[bool]:
    return [sp.nsimplify(p) == sp.nsimplify(o) for o in opts]


# ---------------------------------------------------------------- items


def rv_turn_two_sixes(item: dict) -> list[bool]:
    """q-turn: roll a fair die 3 times; P(exactly two sixes). Options: 1/36, 5/216, 5/72, 25/216, 1/12."""
    space = list(product(range(1, 7), repeat=3))
    p = R(sum(1 for w in space if w.count(6) == 2), len(space))
    return _die_options(p, [R(1, 36), R(5, 216), R(5, 72), R(25, 216), R(1, 12)])


def rv_linear_transform(item: dict) -> list[bool]:
    """q1: X takes 0,1,2,3 with probabilities 0.1, a, 0.3, 0.2; E(2X+1)? Options: 3.2, 4.2, 3.4, 4.4, 5.2."""
    a = sp.symbols("a")
    probs = [R(1, 10), a, R(3, 10), R(2, 10)]
    a_val = sp.solve(sp.Eq(sum(probs), 1), a)[0]
    probs = [pr.subs(a, a_val) if hasattr(pr, "subs") else pr for pr in probs]
    assert all(0 <= pr <= 1 for pr in probs)
    e = sum((2 * x + 1) * pr for x, pr in zip(range(4), probs))  # directly, not via 2E(X)+1
    return _die_options(e, [R(32, 10), R(42, 10), R(34, 10), R(44, 10), R(52, 10)])


def rv_red_balls_mean(item: dict) -> tuple[int, int]:
    """q2: 5 red and 7 white balls, take 4 at once; expected number of red balls (full enumeration)."""
    balls = ["R"] * 5 + ["W"] * 7
    hands = list(combinations(range(12), 4))
    e = R(sum(sum(1 for i in h if balls[i] == "R") for h in hands), len(hands))
    return _frac(e)


def rv_free_throws_exactly(item: dict) -> tuple[int, int]:
    """q3: hit rate 2/3, 5 independent shots; P(exactly 3 hits)."""
    return _frac(_successes_dist(R(2, 3), 5)[3])


def rv_at_least_two_sixes(item: dict) -> list[bool]:
    """q4: fair die 4 times; P(at least two sixes). Options: 1/6, 25/216, 671/1296, 1/144, 19/144."""
    space = list(product(range(1, 7), repeat=4))
    p = R(sum(1 for w in space if w.count(6) >= 2), len(space))
    return _die_options(p, [R(1, 6), R(25, 216), R(671, 1296), R(1, 144), R(19, 144)])


def rv_binomial_statements(item: dict) -> list[bool]:
    """q5: X = successes in 10 independent trials with p = 0.3. Statements: E(X)=3; SD(X)=2.1;
    P(X=0)=0.7^10; P(X=3)=P(X=7); E(2X-1)=5."""
    d = _successes_dist(R(3, 10), 10)
    m, v = _mean(d), _var(d)
    e_lin = sp.nsimplify(sum((2 * k - 1) * pr for k, pr in d.items()))
    return [
        m == 3,
        sp.sqrt(v) == R(21, 10),
        d[0] == R(7, 10) ** 10,
        d[3] == d[7],
        e_lin == 5,
    ]


def rv_round_table_pairs(item: dict) -> tuple[int, int]:
    """q6: 4 boys and 4 girls sit at random round a table with 8 seats; expected number of neighbouring
    boy–girl pairs. Every assignment of genders to the 8 labelled seats is equally likely (C(8,4) = 70)."""
    seatings = list(combinations(range(8), 4))  # seats taken by boys
    total = 0
    for boys in seatings:
        g = [1 if s in boys else 0 for s in range(8)]
        total += sum(1 for s in range(8) if g[s] != g[(s + 1) % 8])
    return _frac(R(total, len(seatings)))


def rv_coin_tail(item: dict) -> tuple[int, int]:
    """q7: a fair coin tossed 8 times; P(at least 7 heads), counted over all 2^8 sequences."""
    seqs = list(product("HT", repeat=8))
    return _frac(R(sum(1 for s in seqs if s.count("H") >= 7), len(seqs)))


def rv_first_win_third(item: dict) -> tuple[int, int]:
    """q8: each draw wins with probability 1/4, independently; P(first win is on draw 3).
    Looks only at the first three draws: the pattern lose, lose, win."""
    t = _trials(R(1, 4), 3)
    return _frac(t[(False, False, True)])


# ---------------------------------------------------------------- worked examples in the chapter


def chapter_examples() -> None:
    # Two fair coins, X = number of heads: 1/4, 1/2, 1/4; E = 1; Var = 1/2 two ways.
    d = _successes_dist(R(1, 2), 2)
    assert d == {0: R(1, 4), 1: R(1, 2), 2: R(1, 4)}
    assert _mean(d) == 1 and _var(d) == R(1, 2)
    assert sum(k**2 * v for k, v in d.items()) - _mean(d) ** 2 == R(1, 2)

    # 4 red, 6 white, take 3 at once: expected reds 6/5, three ways.
    balls = ["R"] * 4 + ["W"] * 6
    hands = list(combinations(range(10), 3))
    assert len(hands) == 120
    reds = [sum(1 for i in h if balls[i] == "R") for h in hands]
    counts = {k: reds.count(k) for k in range(4)}
    assert counts == {0: 20, 1: 60, 2: 36, 3: 4}
    assert counts[0] == sp.binomial(6, 3) and counts[1] == 4 * sp.binomial(6, 2) and counts[2] == sp.binomial(4, 2) * 6
    way_table = R(sum(k * c for k, c in counts.items()), 120)
    way_linearity = 3 * R(4, 10)
    way_double_count = R(4 * sp.binomial(9, 2), 120)  # each red ball lies in C(9,2) = 36 hands
    assert sum(reds) == 144 and sp.binomial(9, 2) == 36
    assert way_table == way_linearity == way_double_count == R(6, 5)

    # 4 hats returned at random: number of people with their own hat.
    perms = list(permutations(range(4)))
    fixed = [sum(1 for i in range(4) if p[i] == i) for p in perms]
    fc = {k: fixed.count(k) for k in range(5)}
    assert fc == {0: 9, 1: 8, 2: 6, 3: 0, 4: 1}
    assert R(sum(k * c for k, c in fc.items()), 24) == 1 == 4 * R(1, 4)
    assert 1 * 8 + 2 * 6 + 4 * 1 == 24

    # q-turn worked in the binomial section: C(3,2)(1/6)^2(5/6) = 15/216 = 5/72.
    assert sp.binomial(3, 2) * R(1, 6) ** 2 * R(5, 6) == R(15, 216) == R(5, 72)
    assert R(1, 6) ** 2 * R(5, 6) == R(5, 216)

    # Hit rate 0.6, 4 shots: distribution, P(at least 3) = 0.4752, by sequences and by formula; E = 2.4, Var = 0.96.
    p = R(6, 10)
    d = _successes_dist(p, 4)
    assert d == {0: R(256, 10000), 1: R(1536, 10000), 2: R(3456, 10000), 3: R(3456, 10000), 4: R(1296, 10000)}
    seq3 = [w for w in _trials(p, 4) if sum(w) == 3]
    assert len(seq3) == 4 and all(_trials(p, 4)[w] == R(864, 10000) for w in seq3)
    assert 4 * R(864, 10000) == R(3456, 10000)
    assert d[3] + d[4] == R(4752, 10000)
    assert sp.expand((R(4, 10) + R(6, 10)) ** 4) == 1 and sum(d.values()) == 1
    for k in range(5):
        assert d[k] == sp.binomial(4, k) * p**k * (1 - p) ** (4 - k)
    assert _mean(d) == R(24, 10) == 4 * p
    # E from the table: 0.1536 + 2(0.3456) + 3(0.3456) + 4(0.1296)
    assert R(1536, 10000) + 2 * R(3456, 10000) + 3 * R(3456, 10000) + 4 * R(1296, 10000) == R(24, 10)
    assert R(1536, 10000) == R(1536, 10000) and 2 * R(3456, 10000) == R(6912, 10000)
    assert 3 * R(3456, 10000) == R(10368, 10000) and 4 * R(1296, 10000) == R(5184, 10000)
    assert _var(d) == R(96, 100) == 4 * p * (1 - p)
    # Bernoulli variance p - p^2 = p(1-p)
    q = sp.symbols("q")
    assert sp.expand((0 - q) ** 2 * (1 - q) + (1 - q) ** 2 * q - q * (1 - q)) == 0

    # Multi-select guessing (s116-fill-and-multi): wrong judgements among 5, each wrong with prob 1/2.
    d5 = _successes_dist(R(1, 2), 5)
    assert [d5[k] * 32 for k in range(6)] == [1, 5, 10, 10, 5, 1]

    # Geometric (數甲): first six on roll k is (5/6)^(k-1)(1/6); P(first six by roll 3) = 91/216 three ways.
    first_by_3_complement = 1 - R(5, 6) ** 3
    first_by_3_sum = sum(R(5, 6) ** (k - 1) * R(1, 6) for k in range(1, 4))
    first_by_3_series = R(1, 6) * (1 - R(5, 6) ** 3) / (1 - R(5, 6))  # finite geometric series
    space = list(product(range(1, 7), repeat=3))
    first_by_3_count = R(sum(1 for w in space if 6 in w), len(space))
    assert first_by_3_complement == first_by_3_sum == first_by_3_series == first_by_3_count == R(91, 216)
    assert R(1, 6) * (1 + R(5, 6) + R(25, 36)) == R(1, 6) * R(91, 36) == R(91, 216)
    # mean 1/p from E = p*1 + (1-p)(1+E)
    E, pp = sp.symbols("E p", positive=True)
    assert sp.solve(sp.Eq(E, pp * 1 + (1 - pp) * (1 + E)), E) == [1 / pp]
    assert sp.summation(sp.Symbol("k") * (R(5, 6)) ** (sp.Symbol("k") - 1) * R(1, 6), (sp.Symbol("k"), 1, sp.oo)) == 6

    # 合理性檢定: fair coin, 10 tosses, at least 9 heads: 11/1024 ≈ 0.0107.
    seqs = list(product("HT", repeat=10))
    tail = R(sum(1 for s in seqs if s.count("H") >= 9), len(seqs))
    assert tail == R(11, 1024) == R(sp.binomial(10, 9) + sp.binomial(10, 10), 2**10)
    assert abs(float(tail) - 0.0107) < 0.00005
    d10 = _successes_dist(R(1, 2), 10)
    assert [d10[k] * 1024 for k in range(11)] == [1, 10, 45, 120, 210, 252, 210, 120, 45, 10, 1]
    # "8 or more heads" for comparison in the text: 56/1024 ≈ 0.0547
    assert sum(d10[k] for k in (8, 9, 10)) == R(56, 1024) and abs(56 / 1024 - 0.0547) < 0.00005


chapter_examples()
