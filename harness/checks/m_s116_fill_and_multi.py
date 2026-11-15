"""Checks for src/data/items/math/s116-fill-and-multi.yaml (116 sprint, exam skills).

Each function recomputes its item's answer with SymPy from the mathematics or from the 多選 scoring
rule (registry fact exam.multi-select-scoring: k wrongly judged options out of n earn (n − 2k)/n of the
points, a negative result or a blank scores 0). None reads item["answer"].

The text_* functions recompute the numbers the chapter states in prose; run them with
    harness/.venv/Scripts/python -c "import sys; sys.path.insert(0, 'harness'); from checks import m_s116_fill_and_multi as m; m.check_text_claims()"
"""

from __future__ import annotations

from itertools import combinations

import sympy as sp

N = 5  # every 多選 item in this chapter has 5 options
POINTS = 5  # and is worth 5 points (the stems say so)


def multi_points(selected: set[int], key: set[int], n: int = N, points: int = POINTS) -> sp.Rational:
    """Points for one 多選 answer under the (n − 2k)/n rule, floored at 0; a blank answer is 0."""
    if not selected:
        return sp.Integer(0)
    k = len(selected ^ key)  # options marked but not in the key, plus key options left unmarked
    return sp.Integer(points) * sp.Max(0, sp.Rational(n - 2 * k, n))


def _expected_with_unsure(sure_right: int, unsure: int, p_right: sp.Rational) -> sp.Rational:
    """Expected points when `sure_right` options are judged right for certain and each of `unsure`
    options is judged right with probability p_right, independently (k counts the wrong judgements)."""
    total = sp.Integer(0)
    for k in range(unsure + 1):
        prob = sp.binomial(unsure, k) * (1 - p_right) ** k * p_right ** (unsure - k)
        total += prob * sp.Integer(POINTS) * sp.Max(0, sp.Rational(N - 2 * k, N))
    return sp.nsimplify(total)


# ---------- items ----------

def fm_turn_one_extra(item: dict) -> list[bool]:
    """q-turn: 5-point item, key (1)(3), marked (1)(2)(3). Options: 5, 4, 3, 1, 0 points."""
    got = multi_points({1, 2, 3}, {1, 3})
    return [got == v for v in (5, 4, 3, 1, 0)]


def fm_fill_negative_fraction(item: dict) -> tuple[int, int]:
    """q1: 1/3 − 7/6 as a fraction in lowest terms, cells ①② / ③ (the minus sign takes cell ①)."""
    r = sp.Rational(1, 3) - sp.Rational(7, 6)
    return (int(r.p), int(r.q))


def fm_fill_radical(item: dict) -> tuple[int, int]:
    """q2: √50 − √8 written as ①√② with ② square-free."""
    v = sp.sqrt(50) - sp.sqrt(8)
    coeff, rad = v.as_coeff_Mul()
    radicand = rad ** 2
    assert radicand.is_integer and sp.sqrt(radicand) == rad  # rad is √(square-free integer)
    assert all(e == 1 for e in sp.factorint(int(radicand)).values())
    return (int(coeff), int(radicand))


def fm_fill_decimal(item: dict) -> tuple[str, str]:
    """q3: 3/8 as a decimal ①.②③④ (exact, so no rounding is involved)."""
    r = sp.Rational(3, 8)
    scaled = r * 1000
    assert scaled.is_integer  # 3/8 has exactly three decimal places
    whole, frac = divmod(int(scaled), 1000)
    return (str(whole), f"{frac:03d}")


def fm_missed_two(item: dict) -> list[bool]:
    """q4: 5-point item, key (2)(4)(5), only (2) marked. Options: 0, 1, 2, 3, 5 points."""
    got = multi_points({2}, {2, 4, 5})
    return [got == v for v in (0, 1, 2, 3, 5)]


def fm_which_score_positive(item: dict) -> list[bool]:
    """q5: key (1)(2); which answers earn at least 1 point?
    Options: (1)(2)(3); (3)(4)(5); (1) only; all five; (1)(3)."""
    key = {1, 2}
    answers = [{1, 2, 3}, {3, 4, 5}, {1}, {1, 2, 3, 4, 5}, {1, 3}]
    return [multi_points(a, key) >= 1 for a in answers]


def fm_expected_mark_or_not(item: dict) -> list[bool]:
    """q6: four options judged right for certain; the fifth is correct with probability 0.3.
    Marking it is right with probability 0.3; leaving it unmarked is right with probability 0.7.
    Options (mark ; leave): 3.6 ; 4.4 | 4.4 ; 3.6 | 4 ; 4 | 3.6 ; 3.5 | 1.5 ; 3.5."""
    p = sp.Rational(3, 10)
    mark = _expected_with_unsure(4, 1, p)
    leave = _expected_with_unsure(4, 1, 1 - p)
    R = sp.Rational
    options = [(R(36, 10), R(44, 10)), (R(44, 10), R(36, 10)), (4, 4), (R(36, 10), R(35, 10)), (R(15, 10), R(35, 10))]
    return [(mark, leave) == (sp.nsimplify(a), sp.nsimplify(b)) for a, b in options]


def fm_expected_two_guesses(item: dict) -> sp.Integer:
    """q7: (1) is surely in the key and marked, (2)(3) surely not and unmarked; (4)(5) are guessed, each
    judgement right with probability 1/2, independently. Enumerates every possible key and every guess
    pattern with the real marked sets (so a blank answer would score 0); the expectation must not depend
    on the key."""
    half = sp.Rational(1, 2)
    values = set()
    for key_extra in [set(), {4}, {5}, {4, 5}]:
        key = {1} | key_extra
        e = sp.Integer(0)
        for right4 in (True, False):
            for right5 in (True, False):
                marked = {1}
                for opt, right in ((4, right4), (5, right5)):
                    if (opt in key) == right:
                        marked.add(opt)
                e += half * half * multi_points(marked, key)
        values.add(sp.nsimplify(e))
    assert len(values) == 1
    e = values.pop()
    assert e.is_integer and e == _expected_with_unsure(3, 2, half)
    return sp.Integer(e)


# ---------- numbers stated in the chapter prose ----------

def text_points_table() -> dict[int, sp.Rational]:
    """The table: a 5-point, 5-option item earns 5, 3, 1, 0, 0, 0 points for k = 0..5."""
    return {k: sp.Integer(POINTS) * sp.Max(0, sp.Rational(N - 2 * k, N)) for k in range(N + 1)}


def text_threshold() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """One unsure option, the other four certain: E(mark) = 3 + 2p, E(leave) = 5 − 2p, equal at p = 1/2."""
    p = sp.Symbol("p", positive=True)
    mark = sp.expand(p * 5 + (1 - p) * 3)
    leave = sp.expand((1 - p) * 5 + p * 3)
    return mark, leave, sp.solve(sp.Eq(mark, leave), p)[0]


def text_all_guessed() -> sp.Rational:
    """All five judgements guessed (each right with probability 1/2, independently): expected 15/16 point."""
    return _expected_with_unsure(0, 5, sp.Rational(1, 2))


def text_all_guessed_exact() -> dict[int, sp.Rational]:
    """All five options guessed (each judgement right with probability 1/2, independently), scored on the
    real marked set, so marking nothing is a blank worth 0. Expected points by the number of key options."""
    opts = list(range(1, N + 1))
    out = {}
    for m in range(1, N + 1):
        key = set(opts[:m])
        e = sp.Integer(0)
        for r in range(N + 1):
            for wrong in combinations(opts, r):
                marked = {o for o in opts if (o in key) != (o in wrong)}
                e += sp.Rational(1, 2 ** N) * multi_points(marked, key)
        out[m] = sp.nsimplify(e)
    return out


def text_never_negative() -> bool:
    """Every non-blank answer scores at least 0, whatever the key: so a blank is never better."""
    opts = range(1, N + 1)
    answers = [set(c) for r in range(1, N + 1) for c in combinations(opts, r)]
    return all(multi_points(a, key) >= 0 for key in answers for a in answers)


def check_text_claims() -> None:
    assert text_points_table() == {0: 5, 1: 3, 2: 1, 3: 0, 4: 0, 5: 0}
    p = sp.Symbol("p", positive=True)
    mark, leave, t = text_threshold()
    assert mark == 2 * p + 3 and leave == 5 - 2 * p and t == sp.Rational(1, 2)
    # the p = 0.8 illustration in the worked example
    assert mark.subs(p, sp.Rational(8, 10)) == sp.Rational(46, 10) and leave.subs(p, sp.Rational(8, 10)) == sp.Rational(34, 10)
    assert text_all_guessed() == sp.Rational(15, 16)
    # with the blank case (all five guessed unmarked) scored 0: 27/32, 29/32, then 15/16 for keys of 3+ options
    assert text_all_guessed_exact() == {1: sp.Rational(27, 32), 2: sp.Rational(29, 32), 3: sp.Rational(15, 16),
                                        4: sp.Rational(15, 16), 5: sp.Rational(15, 16)}
    assert all(0 < v < 1 for v in text_all_guessed_exact().values())
    assert text_never_negative()
    # "every extra sure judgement raises the expected score": 15/16, 23/16, 17/8, 3, 4, 5 for 0..5 sure options
    seq = [_expected_with_unsure(s, N - s, sp.Rational(1, 2)) for s in range(N + 1)]
    assert seq == [sp.Rational(15, 16), sp.Rational(23, 16), sp.Rational(17, 8), 3, 4, 5]
    assert all(a < b for a, b in zip(seq, seq[1:]))
    # worked examples: 1/4 − 1 = −3/4; √12 = 2√3; 1/2 = 0.5
    assert sp.Rational(1, 4) - 1 == sp.Rational(-3, 4)
    assert sp.sqrt(12) == 2 * sp.sqrt(3)
    assert sp.Rational(1, 2) == sp.Rational(5, 10)
    check_perspective_claims()
    print("text claims OK")


def check_perspective_claims() -> None:
    """Numbers stated in the <Perspective> blocks and drawn in their figures."""
    R = sp.Rational
    # number line: 1/4 − 1 lies in (−1, 0); 5/4 > 0 and −5/4 < −1
    v = R(1, 4) - 1
    assert -1 < v < 0 and abs(v.p) < v.q
    assert R(5, 4) > 0 and -R(5, 4) < -1
    # area: √(4a) = 2√a for a = 1..5 (default a = 3 gives √12 = 2√3 ≈ 3.46); √18 = 3√2, 2 square-free
    a = sp.Symbol("a", positive=True)
    assert sp.simplify(sp.sqrt(4 * a) - 2 * sp.sqrt(a)) == 0
    assert round(float(2 * sp.sqrt(3)), 2) == 3.46
    assert sp.sqrt(18) == 3 * sp.sqrt(2)
    # score figure: unfloored line 5 − 2k gives −1, −3, −5 at k = 3, 4, 5; (x + |x|)/2 equals max(0, x)
    assert [5 - 2 * k for k in (3, 4, 5)] == [-1, -3, -5]
    assert all(sp.Rational(5 - 2 * k + abs(5 - 2 * k), 2) == text_points_table()[k] for k in range(N + 1))
    # switches: key (1)(3) vs marks (1)(2)(3) differ only at 2; C(5,k) counts; blank has k = 2 for key {1,3}
    key = {1, 3}
    assert {1, 2, 3} ^ key == {2}
    opts = range(1, N + 1)
    patterns = [set(c) for r in range(N + 1) for c in combinations(opts, r)]
    assert len(patterns) == 32
    by_k = {k: sum(1 for m in patterns if len(m ^ key) == k) for k in range(N + 1)}
    assert by_k == {k: sp.binomial(5, k) for k in range(N + 1)} and by_k[3] + by_k[4] + by_k[5] == 16
    scores = [multi_points(m, key) for m in patterns]
    assert scores.count(5) == 1 and scores.count(3) == 5 and scores.count(1) == 9 and scores.count(0) == 17
    # judging-right view: E = 3 + 2q; difference 4p − 2; best choice 4 + 2|p − 1/2|; p = 0.55 gives 4.1 vs 3.9
    p, q = sp.symbols("p q", real=True)
    assert sp.expand(5 * q + 3 * (1 - q)) == 3 + 2 * q
    assert sp.expand((3 + 2 * p) - (5 - 2 * p)) == 4 * p - 2
    for pv in [R(i, 20) for i in range(21)]:
        assert 4 + 2 * abs(pv - R(1, 2)) == max(3 + 2 * pv, 5 - 2 * pv)
    assert (3 + 2 * R(55, 100), 5 - 2 * R(55, 100)) == (R(41, 10), R(39, 10))
    # balance: unfloored mean 0, floor adds 30/32 = 15/16; with the left bars at −(1−t), −3(1−t), −5(1−t)
    # the mean is 15t/16, and at t = 1 they stack to 16/32
    probs = [R(sp.binomial(5, k), 32) for k in range(N + 1)]
    raw = [5 - 2 * k for k in range(N + 1)]
    assert sum(pr * s for pr, s in zip(probs, raw)) == 0
    assert sum(pr * -s for pr, s in zip(probs, raw) if s < 0) == R(30, 32) == R(15, 16)
    t = sp.Symbol("t")
    mean_t = sum(pr * (s if s > 0 else s * (1 - t)) for pr, s in zip(probs, raw))
    assert sp.expand(mean_t - R(15, 16) * t) == 0
    assert probs[3] + probs[4] + probs[5] == R(16, 32)
    # linearity (later block): E(k) = n/2, so E((n − 2k)/n) = 0 for any n
    n = sp.Symbol("n", positive=True)
    assert sp.simplify((n - 2 * (n / 2)) / n) == 0
    assert sum(k * sp.binomial(5, k) for k in range(N + 1)) / sp.Integer(32) == R(5, 2)
