"""Checks for src/data/items/math/s116-logarithms.yaml (116 sprint: common logarithms, numerical error).

Each function recomputes its item's answer from the mathematics; none reads item["answer"].
Digit counts and leading digits are taken from the exact integers (or exact rationals), so the checks
do not depend on the rounded log values the explanations use.
"""

from __future__ import annotations

import sympy as sp


def _log10(v) -> sp.Expr:
    return sp.log(v, 10)


def _digits(n: int) -> int:
    return len(str(n))


def _first_nonzero_place(r: sp.Rational) -> tuple[int, int]:
    """For 0 < r < 1: (decimal place of the first non-zero digit, that digit)."""
    assert 0 < r < 1
    place = 0
    while True:
        place += 1
        d = int(sp.floor(r * 10**place)) % 10
        if d:
            return place, d


def lg_turn_digits(item: dict) -> list[bool]:
    """q-turn: how many digits has 3.2 × 10^5? Options: 4, 5, 6, 7, 8."""
    n = sp.Rational(32, 10) * 10**5
    assert n.is_Integer
    k = _digits(int(n))
    return [k == o for o in (4, 5, 6, 7, 8)]


def lg_log_thousandth(item: dict) -> list[bool]:
    """q1: log 0.001. Options: −3, 3, −2, 1/1000, −1/3."""
    v = sp.simplify(_log10(sp.Rational(1, 1000)))
    options = [sp.Integer(-3), sp.Integer(3), sp.Integer(-2), sp.Rational(1, 1000), sp.Rational(-1, 3)]
    return [bool(sp.simplify(v - o) == 0) for o in options]


def lg_true_statements(item: dict) -> list[bool]:
    """q4: (1) log 1 = 0; (2) log 200 = 2 log 2; (3) 10^(log 7) = 7; (4) 1 < log 50 < 2;
    (5) every 5-digit positive integer a has 4 < log a < 5."""
    s1 = sp.simplify(_log10(1)) == 0
    s2 = sp.simplify(_log10(200) - 2 * _log10(2)) == 0
    s3 = sp.simplify(sp.Integer(10) ** _log10(7) - 7) == 0
    l50 = _log10(50)
    s4 = bool(l50 > 1) and bool(l50 < 2)
    # log is increasing, so the smallest and largest 5-digit integers decide it.
    s5 = all(bool(_log10(a) > 4) and bool(_log10(a) < 5) for a in (10**4, 10**5 - 1))
    return [bool(s1), bool(s2), bool(s3), s4, s5]


def lg_five_pow_40(item: dict) -> tuple[int, int]:
    """q2: 5^40 has ①② digits and leading digit ③."""
    n = 5**40
    return (_digits(n), int(str(n)[0]))


def lg_twelve_pow_20_leading(item: dict) -> list[bool]:
    """q7: leading digit of 12^20. Options: 1, 2, 3, 4, 5."""
    d = int(str(12**20)[0])
    return [d == o for o in (1, 2, 3, 4, 5)]


def lg_three_pow_twenty_digits(item: dict) -> int:
    """q6: the largest positive integer n with 3^n a 20-digit number.
    3^n grows, so once it has more than 20 digits no larger n can work."""
    best = None
    n = 1
    while _digits(3**n) <= 20:
        if _digits(3**n) == 20:
            best = n
        n += 1
    assert best is not None
    return best


def lg_point3_pow_10(item: dict) -> list[bool]:
    """q3: 0.3^10 written as a decimal: in which decimal place is the first non-zero digit?
    Options: 4th, 5th, 6th, 7th, 10th."""
    place, _ = _first_nonzero_place(sp.Rational(3, 10) ** 10)
    return [place == o for o in (4, 5, 6, 7, 10)]


def lg_two_pow_1000_error(item: dict) -> list[bool]:
    """q5: A estimates the digits of 2^1000 with log 2 ≈ 0.3, B with log 2 ≈ 0.3010
    (digits = floor(1000 × value) + 1). Options:
    (1) both get 301, both right; (2) A 301, B 302, B right; (3) A 302, B 301, A right;
    (4) A 301, B 302, A right; (5) both get 302, both right."""
    true_digits = _digits(2**1000)
    a = int(sp.floor(1000 * sp.Rational(3, 10))) + 1
    b = int(sp.floor(1000 * sp.Rational(3010, 10000))) + 1
    options = [
        a == 301 and b == 301 and true_digits == 301,
        a == 301 and b == 302 and true_digits == b and true_digits != a,
        a == 302 and b == 301 and true_digits == a and true_digits != b,
        a == 301 and b == 302 and true_digits == a and true_digits != b,
        a == 302 and b == 302 and true_digits == 302,
    ]
    return options
