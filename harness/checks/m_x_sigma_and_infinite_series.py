"""Checks for src/data/items/math/x-sigma-and-infinite-series.yaml (分科 advanced tool: Σ notation and
infinite geometric series, N-12甲-2 / N-12乙-2; not on 學測).

Each item check recomputes its answer from the mathematics with SymPy and never reads item["answer"].
Finite sums are added term by term (sp.summation or a plain loop), not by the formulas the chapter
teaches; infinite geometric sums are taken as SymPy limits of the partial sums, so the a/(1−r) formula
is checked rather than assumed (convergence = even and odd partial sums tend to the same finite limit). Repeating decimals are rebuilt digit by digit from long division.

The worked examples on the page are asserted at import time (`_worked_examples`), so a wrong number in
the prose fails the harness too.
"""

from __future__ import annotations

import sympy as sp

k = sp.Symbol("k", integer=True, positive=True)
n = sp.Symbol("n", integer=True, positive=True)
N = sp.Symbol("N", integer=True, positive=True)


def _finite(expr, lo: int, hi: int) -> sp.Rational:
    """Σ_{k=lo}^{hi} expr, added one term at a time."""
    return sp.Integer(0) + sum((expr.subs(k, j) for j in range(lo, hi + 1)), sp.Integer(0))


def _even_odd_limits(a, r):
    """Limits of the even partial sums S_{2N} and the odd partial sums S_{2N−1} of a + ar + ar² + ….

    S_{2N} = Σ_{j=1}^{N} a(1 + r)(r²)^{j−1} and S_{2N−1} = S_{2N} − a·r·(r²)^{N−1}, written with the
    non-negative base r² so SymPy's limit never meets a negative base (r = −1 makes the two differ)."""
    a, r = sp.sympify(a), sp.sympify(r)
    q = r**2
    j = sp.Symbol("j", integer=True, positive=True)
    even = sp.summation(a * (1 + r) * q ** (j - 1), (j, 1, N))
    odd = even - a * r * q ** (N - 1)
    return sp.limit(even, N, sp.oo), sp.limit(odd, N, sp.oo)


def _converges(a, r) -> bool:
    """True when the partial sums of a + ar + ar² + … approach one finite number."""
    even, odd = _even_odd_limits(a, r)
    return bool(even.is_finite and odd.is_finite and sp.simplify(even - odd) == 0)


def _infinite_geometric(a, r):
    """The sum a + ar + ar² + …, as the limit of its partial sums (AssertionError if it diverges)."""
    assert _converges(a, r), f"{a} + {a}·{r} + … has no sum"
    return sp.nsimplify(_even_odd_limits(a, r)[0])


def _decimal_digits(p: int, q: int, count: int) -> list[int]:
    """The first `count` digits after the decimal point of p/q (0 < p/q < 1), by long division."""
    digits, rem = [], p % q
    for _ in range(count):
        rem *= 10
        digits.append(rem // q)
        rem %= q
    return digits


def _worked_examples() -> None:
    """Every number in the chapter's prose examples, recomputed (raises AssertionError if one is off)."""
    # Σ section: Σ_{k=1}^{5}(2k−1) = 25, the picture with five bars; Σ_{k=3}^{7} has 5 terms
    assert _finite(2 * k - 1, 1, 5) == 25
    assert len(range(3, 8)) == 5
    assert _finite(k**2, 3, 7) == 9 + 16 + 25 + 36 + 49 == 135
    # stacked-bar picture: Σ_{k=1}^{4}(k+2) = Σk + Σ2 = 10 + 8 = 18
    assert _finite(k + 2, 1, 4) == 18 and _finite(k, 1, 4) == 10 and _finite(sp.Integer(2) + 0 * k, 1, 4) == 8
    # 2 + 4 + … + 40 is Σ_{k=1}^{20} 2k
    assert [2 * j for j in range(1, 21)] == list(range(2, 41, 2))
    # linearity example: Σ_{k=1}^{10}(3k² − 2k + 1) = 3·385 − 2·55 + 10 = 1055
    assert _finite(k**2, 1, 10) == 385 and _finite(k, 1, 10) == 55
    assert _finite(3 * k**2 - 2 * k + 1, 1, 10) == 3 * 385 - 2 * 55 + 10 == 1055
    # the closed form in n, and its n = 1 and n = 2 spot checks
    closed = sp.expand(sp.summation(3 * k**2 - 2 * k + 1, (k, 1, n)))
    assert sp.expand(closed - (n * (n + 1) * (2 * n + 1) / 2 - n * (n + 1) + n)) == 0
    assert closed.subs(n, 1) == 2 and closed.subs(n, 2) == 2 + 9 and closed.subs(n, 10) == 1055
    assert sp.Rational(10 * 11 * 21, 2) == 1155 and sp.Rational(2 * 3 * 5, 2) - 6 + 2 == 11
    # telescoping: Σ_{k=1}^{n}[(k+1)² − k²] = (n+1)² − 1, so 2Σk + n = n² + 2n, Σk = n(n+1)/2
    assert sp.expand(sp.summation((k + 1) ** 2 - k**2, (k, 1, n)) - ((n + 1) ** 2 - 1)) == 0
    assert sp.expand(sp.summation(k, (k, 1, n)) - n * (n + 1) / 2) == 0
    # the warning: Σ a_k b_k ≠ (Σ a_k)(Σ b_k), e.g. a_k = b_k = k, n = 3: 14 vs 36
    assert _finite(k * k, 1, 3) == 14 and _finite(k, 1, 3) ** 2 == 36

    # infinite series: 1 + 1/2 + 1/4 + … = 2; partial sums S_n = 2 − (1/2)^{n−1}
    assert _infinite_geometric(1, sp.Rational(1, 2)) == 2
    assert all(_finite(sp.Rational(1, 2) ** (k - 1), 1, j) == 2 - sp.Rational(1, 2) ** (j - 1) for j in range(1, 9))
    assert [_finite(sp.Rational(1, 2) ** (k - 1), 1, j) for j in (1, 2, 3, 4)] == [1, sp.Rational(3, 2), sp.Rational(7, 4), sp.Rational(15, 8)]
    # later perspective: 1/0.9 = 1 + 1/9, (1 + h)^n ≥ 1 + nh, so 0.9^n ≤ 9/(9 + n); n = 81 gives ≤ 1/10
    h = sp.Rational(1, 9)
    assert 1 / sp.Rational(9, 10) == 1 + h
    assert all((1 + h) ** j >= 1 + j * h for j in range(1, 200))
    assert sp.Rational(9, 10) ** 81 <= sp.Rational(9, 90) == sp.Rational(1, 10)
    # example: 8 − 4 + 2 − 1 + … = 16/3
    assert _infinite_geometric(8, sp.Rational(-1, 2)) == sp.Rational(16, 3)
    # the figure's slider: at r = 0.8 the dashed line is at 5 and S_8 ≈ 4.16 (inside y ≤ 5.5)
    assert 1 / (1 - sp.Rational(4, 5)) == 5 and _finite(sp.Rational(4, 5) ** (k - 1), 1, 8) < sp.Rational(11, 2)
    # the number line: S_2 = 0.3636 is within 0.000036 of 4/11
    assert sp.Rational(4, 11) - sp.Rational(3636, 10000) == sp.Rational(36, 990000) < sp.Rational(37, 1000000)
    # divergent cases in the table: r = 1, r = −1 (1, 0, 1, 0, …), r = 2
    assert not _converges(1, 1) and not _converges(1, -1) and not _converges(1, 2)
    assert [_finite((-1) ** (k - 1), 1, j) for j in range(1, 5)] == [1, 0, 1, 0]
    # the bogus "S = 1 + 2S ⇒ S = −1" for 1 + 2 + 4 + …
    S = sp.Symbol("S")
    assert sp.solve(sp.Eq(S, 1 + 2 * S), S) == [-1]
    # log perspective: 0.9^n < 0.001 first at n = 66 (log 0.9 ≈ −0.0458)
    first = next(j for j in range(1, 200) if sp.Rational(9, 10) ** j < sp.Rational(1, 1000))
    assert first == 66
    assert abs(sp.log(sp.Rational(9, 10), 10).evalf() - (-0.0458)) < 0.0001
    assert sp.floor(3 / sp.Float("0.0458")) + 1 == 66
    # picture: 1/4 + 1/16 + 1/64 + … = 1/3
    assert _infinite_geometric(sp.Rational(1, 4), sp.Rational(1, 4)) == sp.Rational(1, 3)
    assert _finite(sp.Rational(1, 4) ** k, 1, 3) == sp.Rational(21, 64)

    # repeating decimals: 0.\overline{36} = 36/99 = 4/11; 0.1\overline{36} = 3/22; 0.\overline{9} = 1
    assert _infinite_geometric(sp.Rational(36, 100), sp.Rational(1, 100)) == sp.Rational(4, 11)
    assert _decimal_digits(4, 11, 6) == [3, 6, 3, 6, 3, 6]
    assert [_finite(sp.Rational(36, 100) * sp.Rational(1, 100) ** (k - 1), 1, j) for j in (1, 2, 3)] == [
        sp.Rational(36, 100), sp.Rational(3636, 10000), sp.Rational(363636, 1000000)]
    x = sp.Rational(1, 10) + _infinite_geometric(sp.Rational(36, 1000), sp.Rational(1, 100))
    assert x == sp.Rational(1, 10) + sp.Rational(36, 990) == sp.Rational(135, 990) == sp.Rational(3, 22)
    assert _decimal_digits(3, 22, 7) == [1, 3, 6, 3, 6, 3, 6]
    # the 10–11 method for the same number: 1000x − 10x = 136.36… − 1.36… = 135
    assert 1000 * x - 10 * x == 135
    assert _infinite_geometric(sp.Rational(9, 10), sp.Rational(1, 10)) == 1

    # numbers quoted in item explanations
    assert _finite(k**2, 1, 12) == 650 and _finite(k, 1, 12) == 78  # q2
    assert _infinite_geometric(2, sp.Rational(-2, 3)) == sp.Rational(6, 5)  # q4 option (3)
    y = sp.Rational(27, 110)  # q6: 1000y − 10y = 243 and 243/990 = 27/110
    assert 1000 * y - 10 * y == 243 and sp.Rational(243, 990) == y
    assert sp.Rational(2, 10) + sp.Rational(45, 990) == sp.Rational(198 + 45, 990)
    assert _infinite_geometric(36, sp.Rational(1, 4)) == 48  # q7 check line


_worked_examples()


# --------------------------------------------------------------------------- item checks


def xs_turn_sigma(item: dict) -> list[bool]:
    """q-turn: Σ_{k=1}^{4}(2k+1) = ? Options: 16, 20, 24, 25, 30."""
    v = _finite(2 * k + 1, 1, 4)
    return [v == o for o in (16, 20, 24, 25, 30)]


def xs_constant_terms(item: dict) -> list[bool]:
    """q1: Σ_{k=5}^{20} 3 = ? (k runs over 5, 6, …, 20). Options: 45, 48, 51, 57, 60."""
    v = sum(sp.Integer(3) for _ in range(5, 21))
    return [v == o for o in (45, 48, 51, 57, 60)]


def xs_linearity_sum(item: dict) -> sp.Integer:
    """q2: Σ_{k=1}^{12}(2k² − k)."""
    return _finite(2 * k**2 - k, 1, 12)


def xs_linearity_statements(item: dict) -> list[bool]:
    """q3: which identities hold for every n and all sequences ⟨a_k⟩, ⟨b_k⟩?
    (1) Σ(a_k+b_k) = Σa_k + Σb_k; (2) Σ 5a_k = 5Σa_k; (3) Σ a_k b_k = (Σa_k)(Σb_k);
    (4) Σ(a_k+2) = Σa_k + 2; (5) Σ_{k=1}^{n} a_k = Σ_{j=1}^{n} a_j.
    Each is tested with symbolic terms a_1…a_m, b_1…b_m for m = 1…6: true means zero difference for all m."""
    results = [True] * 5
    for m in range(1, 7):
        a = sp.symbols(f"a1:{m + 1}")
        b = sp.symbols(f"b1:{m + 1}")
        sa, sb = sum(a), sum(b)
        diffs = [
            sum(x + y for x, y in zip(a, b)) - (sa + sb),
            sum(5 * x for x in a) - 5 * sa,
            sum(x * y for x, y in zip(a, b)) - sa * sb,
            sum(x + 2 for x in a) - (sa + 2),
            sum(a[j - 1] for j in range(1, m + 1)) - sa,  # renaming the index j
        ]
        for i, d in enumerate(diffs):
            if sp.expand(d) != 0:
                results[i] = False
    return results


def xs_which_converges(item: dict) -> list[bool]:
    """q4: which infinite geometric series has a sum?
    (1) 1+2+4+…; (2) 1−1+1−1+…; (3) 2 − 4/3 + 8/9 − …; (4) 1 + 1.01 + 1.01² + …; (5) 3+3+3+…"""
    series = [(1, 2), (1, -1), (2, sp.Rational(-2, 3)), (1, sp.Rational(101, 100)), (3, 1)]
    return [_converges(a, r) for a, r in series]


def xs_sum_alternating(item: dict) -> tuple[int, int]:
    """q5: 6 − 2 + 2/3 − 2/9 + … as a fraction p/q in lowest terms."""
    a, r = sp.Integer(6), sp.Rational(-2, 6)
    assert a * r**2 == sp.Rational(2, 3) and a * r**3 == sp.Rational(-2, 9)
    s = sp.Rational(_infinite_geometric(a, r))
    return (int(s.p), int(s.q))


def xs_repeating_decimal(item: dict) -> tuple[int, int]:
    """q6: 0.2\\overline{45} = 0.24545… as p/q in lowest terms (two-digit numerator, three-digit denominator).
    Built as 2/10 + (45/1000)(1 + 1/100 + 1/100² + …), then the digits are checked by long division."""
    s = sp.Rational(2, 10) + _infinite_geometric(sp.Rational(45, 1000), sp.Rational(1, 100))
    s = sp.Rational(s)
    assert _decimal_digits(int(s.p), int(s.q), 9) == [2, 4, 5, 4, 5, 4, 5, 4, 5]
    return (int(s.p), int(s.q))


def xs_first_term_from_two_sums(item: dict) -> list[bool]:
    """q7: an infinite geometric series has sum 12; the series of the squares of its terms has sum 48.
    First term a = ? Options: 2, 4, 6, 8, 9. Solved from the two limits, keeping only −1 < r < 1."""
    a, r = sp.symbols("a r", real=True)
    sols = sp.solve([sp.Eq(a / (1 - r), 12), sp.Eq(a**2 / (1 - r**2), 48)], [a, r], dict=True)
    good = [s for s in sols if -1 < s[r] < 1 and s[r] != 0]
    assert len(good) == 1
    a0, r0 = good[0][a], good[0][r]
    # confirm both sums as genuine limits of partial sums
    assert _infinite_geometric(a0, r0) == 12 and _infinite_geometric(a0**2, r0**2) == 48
    return [a0 == o for o in (2, 4, 6, 8, 9)]


def xs_convergence_range(item: dict) -> list[bool]:
    """q8: for which x does 1 + (x−1) + (x−1)² + … have a sum? Options: x = −0.5, 0.5, 1.5, 1.99, 2."""
    xs = [sp.Rational(-1, 2), sp.Rational(1, 2), sp.Rational(3, 2), sp.Rational(199, 100), sp.Integer(2)]
    return [_converges(1, x - 1) for x in xs]
