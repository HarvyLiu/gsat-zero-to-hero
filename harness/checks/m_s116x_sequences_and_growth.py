"""Checks for src/data/items/math/s116x-sequences-and-growth.yaml (116 sprint, cross-unit chapter:
sequences, exponents and logarithms, many views).

Each item function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
"Smallest n" and digit-count answers come from exact integer / rational comparisons, so they do not depend
on the rounded log values (log 2 ≈ 0.3010, log 3 ≈ 0.4771, log 5 ≈ 0.6990) the explanations use.

check_worked_ways() re-derives every worked problem in the lesson BY EACH WAY the lesson shows and asserts
that the ways agree. It runs when this module is imported, so the harness fails if any stated number drifts.
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational
LOG2, LOG3, LOG5 = R(3010, 10000), R(4771, 10000), R(6990, 10000)  # the 4-place values the paper prints


def _recurse(a1, step, n: int) -> list:
    """The first n terms of a_1 = a1, a_{m+1} = step(a_m, m)."""
    terms = [sp.nsimplify(a1)]
    for m in range(1, n):
        terms.append(sp.nsimplify(step(terms[-1], m)))
    return terms


def _least_n(holds, limit: int = 1000) -> int:
    for k in range(1, limit + 1):
        if holds(k):
            return k
    raise AssertionError("no k found")


def _digits(v: int) -> int:
    return len(str(abs(int(v))))


# ---------------------------------------------------------------------------
# worked problems in the lesson, each way separately
# ---------------------------------------------------------------------------
def check_worked_ways() -> None:
    # Problem 1: a_1 = 2, a_{n+1} = 2a_n − 1; a_10 = ?
    seq = _recurse(2, lambda a, m: 2 * a - 1, 10)
    assert seq == [2, 3, 5, 9, 17, 33, 65, 129, 257, 513]
    way_iterate = seq[-1]
    diffs = [seq[i + 1] - seq[i] for i in range(9)]
    assert diffs == [2**j for j in range(9)]
    way_differences = 2 + sum(2**j for j in range(9))  # 2 + (1 + 2 + … + 2^8) = 2 + (2^9 − 1)
    assert sum(2**j for j in range(9)) == 2**9 - 1 == 511
    c = sp.Symbol("c")
    assert sp.solve(sp.Eq(c, 2 * c - 1), c) == [1]
    way_fixed_point = 1 + (2 - 1) * 2**9
    assert way_iterate == way_differences == way_fixed_point == 513
    # the figure: with first term a the terms are 1 + (a − 1)2^(n−1); slider a = 1 gives the constant sequence
    a = sp.Symbol("a")
    gen = _recurse(a, lambda t, m: sp.expand(2 * t - 1), 5)
    assert [sp.expand(g - (1 + (a - 1) * 2**k)) for k, g in enumerate(gen)] == [0] * 5
    assert gen[1] == 2 * a - 1 and gen[2] == 4 * a - 3 and gen[3] == 8 * a - 7 and gen[4] == 16 * a - 15
    assert all(g.subs(a, 1) == 1 for g in gen)

    # Problem 2: A_n = 30n + 70 (100, 130, …), B_n = 2^(n−1); first month with B_n > A_n, and it stays so
    A = lambda n: 30 * n + 70  # noqa: E731
    B = lambda n: sp.Integer(2) ** (n - 1)  # noqa: E731
    assert [A(n) for n in range(1, 11)] == [100, 130, 160, 190, 220, 250, 280, 310, 340, 370]
    assert [B(n) for n in range(1, 11)] == [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    way_table = _least_n(lambda n: B(n) > A(n))
    # estimate: months 1–6 have B_n ≤ 2^5 = 32 < 100 ≤ A_n; months 7–9 have B_n ≤ 2^8 = 256 < 280 ≤ A_n;
    # at n = 10, 512 > 370
    assert all(B(n) <= 32 < 100 <= A(n) for n in range(1, 7))
    assert all(B(n) <= 256 < 280 <= A(n) for n in range(7, 10)) and B(10) == 512 > A(10) == 370
    way_estimate = 10
    assert way_table == way_estimate == 10
    # it stays: B_{k+1} = 2B_k = B_k + B_k > A_k + 30 = A_{k+1} once B_k > A_k and B_k ≥ 30
    assert all(2 * B(k) == B(k + 1) and A(k) + 30 == A(k + 1) for k in range(1, 60))
    assert B(10) >= 30 and all(B(n) > A(n) for n in range(10, 300))
    # figure: blue points for months 1–6 are at most 32 (they hug the axis on a 0–540 scale)
    assert max(B(n) for n in range(1, 7)) == 32

    # Problem 3: how many digits has 2^50, and its leading digit
    v = sp.Integer(2) ** 50
    assert v == 1125899906842624
    exact_digits, exact_lead = _digits(v), int(str(v)[0])
    way_log = sp.floor(50 * LOG2) + 1
    assert 50 * LOG2 == R(1505, 100) and way_log == 16
    # bounds: 2^10 = 1024 > 10^3, so 2^50 > 10^15; 1.024^2 < 1.05, 1.05^2 < 1.11, 1.11 × 1.024 < 1.14
    assert 2**10 == 1024 and v > 10**15
    assert R(1024, 1000) ** 2 == R(1048576, 10**6) < R(105, 100)
    assert R(105, 100) ** 2 == R(11025, 10000) < R(111, 100)
    assert R(111, 100) * R(1024, 1000) < R(114, 100)
    assert R(1024, 1000) ** 5 < R(114, 100) and v == R(1024, 1000) ** 5 * 10**15 and v < R(114, 100) * 10**15 < 10**16
    way_bounds_digits, way_bounds_lead = 16, 1
    # mantissa: 0 < 0.05 < log 2 ≈ 0.3010, so 10^0.05 is between 1 and 2
    assert 0 < 50 * LOG2 - 15 < LOG2
    way_mantissa_lead = 1
    assert exact_digits == way_log == way_bounds_digits == 16
    assert exact_lead == way_bounds_lead == way_mantissa_lead == 1
    assert sp.floor(50 * sp.log(2, 10)) == 15 and 50 * sp.log(2, 10) - 15 < sp.log(2, 10)

    # Problem 4: area ×1.2 every week; first week with more than 5 times the start
    q = R(12, 10)
    table = [q**n for n in range(1, 10)]
    rounded = [round(float(t), 3) for t in table]
    assert rounded == [1.2, 1.44, 1.728, 2.074, 2.488, 2.986, 3.583, 4.3, 5.16]
    way_table4 = _least_n(lambda n: q**n > 5)
    log12 = 2 * LOG2 + LOG3 - 1
    assert log12 == R(791, 10000)
    bound = LOG5 / log12
    assert round(float(bound), 2) == 8.84 and 8 < bound < 9
    way_log4 = sp.floor(bound) + 1
    # log-scale graph: points (n, n log 1.2) on a line of slope log 1.2 cross y = log 5 between n = 8 and 9
    assert 8 * log12 < LOG5 < 9 * log12
    assert round(float(8 * log12), 3) == 0.633 and round(float(9 * log12), 3) == 0.712
    # the figure plots the exact log: week 8 ≈ 0.633, week 9 ≈ 0.713 (as its description says)
    assert round(float(8 * sp.log(R(6, 5), 10)), 3) == 0.633 and round(float(9 * sp.log(R(6, 5), 10)), 3) == 0.713
    assert way_table4 == way_log4 == 9
    assert round(float(sp.log(5) / sp.log(R(6, 5))), 2) == 8.83  # exact-log crossing (the figure's point)
    # figure slider r = 0.5: crossing ≈ 4.0 and week 4 at ≈ 0.704 is just above log 5 ≈ 0.699
    assert round(float(sp.log(5) / sp.log(R(3, 2))), 1) == 4.0 and R(3, 2) ** 4 > 5 > R(3, 2) ** 3
    assert round(float(4 * sp.log(R(3, 2), 10)), 3) == 0.704 and round(float(sp.log(5, 10)), 3) == 0.699
    # problem 3 upper bound step: 1.11 × 1.024 = 1.13664 < 1.14
    assert R(111, 100) * R(1024, 1000) == R(113664, 100000)

    # Problem 5: 4 years of equal yearly cuts take the emission to 0.4096 of the start
    p = sp.Symbol("p", positive=True)
    sols = [s for s in sp.solve(sp.Eq((1 - p) ** 4, R(4096, 10000)), p) if s.is_real and 0 < s < 1]
    assert sols == [R(1, 5)]
    way_root = 1 - sp.sqrt(sp.sqrt(R(4096, 10000)))
    assert sp.sqrt(R(4096, 10000)) == R(64, 100) and sp.sqrt(R(64, 100)) == R(8, 10)
    log_total = 12 * LOG2 - 4  # 0.4096 = 2^12 / 10^4
    assert R(4096, 10000) == R(2**12, 10**4) and log_total == R(-388, 1000)
    assert log_total / 4 == R(-97, 1000) == 3 * LOG2 - 1  # = log 0.8
    # exactly: (12 log 2 − 4)/4 = 3 log 2 − 1 = log 0.8, for the true log 2 as well
    L2 = sp.Symbol("L2")
    assert sp.expand((12 * L2 - 4) / 4) == 3 * L2 - 1
    assert sp.simplify(sp.log(R(8, 10), 10) - (3 * sp.log(2, 10) - 1)) == 0
    way_log5 = 1 - R(8, 10)
    way_check = [R(8, 10) ** k for k in range(1, 5)]
    assert way_check == [R(8, 10), R(64, 100), R(512, 1000), R(4096, 10000)]
    # guess and check: 15% a year leaves 0.85^4 ≈ 0.522 (too much); 20% leaves exactly 0.4096
    assert round(float(R(85, 100) ** 4), 3) == 0.522 and R(85, 100) ** 4 > R(4096, 10000)
    way_guess = R(1, 5)
    assert way_root == way_log5 == way_guess == R(1, 5)
    # the tempting wrong answer: (1 − 0.4096)/4 = 14.76% a year, which leaves about 0.528, not 0.4096
    wrong = (1 - R(4096, 10000)) / 4
    assert wrong == R(1476, 10000)
    assert round(float((1 - wrong) ** 4), 3) == 0.528
    assert round(float(1 - wrong), 4) == 0.8524
    # number line: log of what is left after 0..4 years is 0, −0.097, −0.194, −0.291, −0.388
    assert [k * (3 * LOG2 - 1) for k in range(5)] == [0, R(-97, 1000), R(-194, 1000), R(-291, 1000), R(-388, 1000)]


check_worked_ways()


# ---------------------------------------------------------------------------
# items
# ---------------------------------------------------------------------------
def sg_turn_recursion(item: dict) -> list[bool]:
    """q-turn: a_1 = 3, a_{n+1} = 2a_n − 2; a_5 = ? Options: 10, 16, 18, 34, 48."""
    a5 = _recurse(3, lambda a, m: 2 * a - 2, 5)[-1]
    # the fixed-point way agrees: c = 2c − 2 gives c = 2, and a_n − 2 doubles from 1
    assert a5 == 2 + (3 - 2) * 2**4
    return [a5 == o for o in (10, 16, 18, 34, 48)]


def sg_recursion_three_times(item: dict) -> sp.Integer:
    """q1: a_1 = 1, a_{n+1} = 3a_n + 2; a_6 = ?"""
    a6 = _recurse(1, lambda a, m: 3 * a + 2, 6)[-1]
    assert a6 == -1 + (1 + 1) * 3**5  # fixed point −1: a_n + 1 = 2·3^(n−1)
    return sp.Integer(a6)


def sg_digits_5_30(item: dict) -> list[bool]:
    """q2: number of digits of 5^30. Options: 20, 21, 22, 30, 31."""
    d = _digits(sp.Integer(5) ** 30)
    assert sp.floor(30 * LOG5) + 1 == d  # the log way with log 5 ≈ 0.6990 gives the same count
    return [d == o for o in (20, 21, 22, 30, 31)]


def sg_decay_half(item: dict) -> sp.Integer:
    """q3: a drug amount falls by 10% each hour; least whole number of hours until less than half is left."""
    n = _least_n(lambda k: R(9, 10) ** k < R(1, 2))
    assert sp.floor(LOG2 / (1 - 2 * LOG3)) + 1 == n  # log 0.9 = 2 log 3 − 1 way agrees
    return sp.Integer(n)


def sg_views_of_b(item: dict) -> list[bool]:
    """q4: b_n = 3·2^n. Statements: points (n, log b_n) are collinear with slope log 2; points (n, b_n)
    are collinear; b_{n+1} − b_n is geometric with ratio 2; b_10 has 4 digits; b_{n+1} = b_n + 6."""
    nn = range(1, 30)
    b = {k: 3 * sp.Integer(2) ** k for k in range(1, 31)}
    logb = {k: sp.log(b[k], 10) for k in b}
    log_line = all(sp.simplify(logb[k + 1] - logb[k] - sp.log(2, 10)) == 0 for k in nn)
    plain_line = all(b[k + 2] - b[k + 1] == b[k + 1] - b[k] for k in nn)
    diffs = {k: b[k + 1] - b[k] for k in nn}
    diff_geometric = all(diffs[k + 1] == 2 * diffs[k] for k in range(1, 29))
    return [log_line, plain_line, diff_geometric, _digits(b[10]) == 4, all(b[k + 1] == b[k] + 6 for k in nn)]


def sg_which_needs_log(item: dict) -> list[bool]:
    """q5: which task involves a number with more than 15 digits (too big to multiply out by hand), so the
    common logarithm suits it best? Tasks: the value of 2^20; the number of digits of 3^40; the value of
    1.2^3; a_8 of a_1 = 2, a_{n+1} = 2a_n − 1; the value of 11^4."""
    involved = [
        sp.Integer(2) ** 20,
        sp.Integer(3) ** 40,
        R(12, 10) ** 3,
        _recurse(2, lambda a, m: 2 * a - 1, 8)[-1],
        sp.Integer(11) ** 4,
    ]
    return [_digits(sp.floor(v)) > 15 for v in involved]


def sg_average_rate(item: dict) -> sp.Integer:
    """q6: an investment grows to 1.331 times in 3 years; equal yearly rate in percent."""
    r = sp.Symbol("r", positive=True)
    sols = [s for s in sp.solve(sp.Eq((1 + r) ** 3, R(1331, 1000)), r) if s.is_real]
    assert sols == [R(1, 10)]
    return sp.Integer(100 * sols[0])


def sg_compare_powers(item: dict) -> list[bool]:
    """q7: statements about 2^40 and 3^25: 2^40 > 3^25; 2^40 has 13 digits; 3^25 has 12 digits;
    2^8 < 3^5; 2^40 / 3^25 > 10."""
    a, b = sp.Integer(2) ** 40, sp.Integer(3) ** 25
    # both ways in the explanation agree with the exact comparison
    assert (40 * LOG2 > 25 * LOG3) == (a > b) and (2**8 > 3**5)
    assert sp.floor(40 * LOG2) + 1 == _digits(a) and sp.floor(25 * LOG3) + 1 == _digits(b)
    return [a > b, _digits(a) == 13, _digits(b) == 12, 2**8 < 3**5, a / b > 10]
