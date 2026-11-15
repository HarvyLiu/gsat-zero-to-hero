"""Checks for src/data/items/math/x-limits-steady-state.yaml (分科 advanced tool, 數甲 N-12甲-1: sequence limits
and the steady state of a 2x2 transition matrix, 11A F-11A-3).

Each item function recomputes its answer from the mathematics with SymPy; none reads item["answer"].
- "From which term on" questions are found by walking the exact (rational) sequence term by term.
- A sequence converges exactly when its even-indexed and odd-indexed subsequences have the same finite limit,
  which SymPy finds with an ordinary limit in k (n = 2k or n = 2k + 1); this handles the (-1)^n cases.
- Transition-matrix states are found by repeated exact matrix multiplication, and steady states from the
  null space of T - I, never from the chapter's closed formula s = (1-q)/(2-p-q) (that formula is itself checked).

The module also asserts every number in the chapter's worked examples (both locales use the same numbers),
including each alternative way, so a typo in the lesson's mathematics fails the harness on import.
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational
n, k = sp.symbols("n k", positive=True, integer=True)


def _first_index(term, cond, start: int = 0, stop: int = 100000) -> int:
    """Smallest integer m >= start for which cond(term(m)) holds, walking term by term with exact values."""
    for m in range(start, stop):
        if cond(term(m)):
            return m
    raise AssertionError("no index found")


def _seq_limit(expr):
    """Limit of a sequence a_n as n -> oo, or None if it diverges (including oscillation)."""
    even = sp.limit(expr.subs(n, 2 * k), k, sp.oo)
    odd = sp.limit(expr.subs(n, 2 * k + 1), k, sp.oo)
    if even.is_finite and odd.is_finite and sp.simplify(even - odd) == 0:
        return even
    return None


def _T(p, q) -> sp.Matrix:
    """Column convention of the 11A chapter: column j = this step's state, row i = next step's state."""
    return sp.Matrix([[p, 1 - q], [1 - p, q]])


def _steady(T: sp.Matrix) -> sp.Matrix:
    """The state X with TX = X whose two components add up to 1 (from the null space of T - I)."""
    ns = (T - sp.eye(2)).nullspace()
    assert len(ns) == 1, "steady state not unique"
    v = ns[0]
    return v / sum(v)


def _states(T: sp.Matrix, X0: sp.Matrix, steps: int) -> list[sp.Matrix]:
    out = [X0]
    for _ in range(steps):
        out.append(T * out[-1])
    return out


# ---------------------------------------------------------------------------------------------------------
# Worked examples in the lesson (run on import).
# ---------------------------------------------------------------------------------------------------------
def _worked_examples() -> None:
    # Opening dialogue: the 11A chapter's x_n = 0.6 - 0.1*(0.5)^n gets closer to 1 every step too (it increases
    # and stays below 0.6), but its limit is 0.6.
    xs = [R(6, 10) - R(1, 10) * R(1, 2) ** m for m in range(10)]
    assert xs[:3] == [R(1, 2), R(55, 100), R(575, 1000)]
    assert all(abs(xs[m + 1] - 1) < abs(xs[m] - 1) for m in range(9))
    assert all(x < R(6, 10) for x in xs)
    assert _seq_limit(R(6, 10) - R(1, 10) * R(1, 2) ** n) == R(6, 10)

    # Definition example: a_n = (2n+1)/n = 2 + 1/n; |a_n - 2| < 0.01 from n = 101 on; in the figure, eps = 0.3 -> from n = 4.
    a = lambda m: R(2 * m + 1, m)
    assert all(a(m) == 2 + R(1, m) for m in range(1, 50))
    assert _first_index(lambda m: abs(a(m) - 2), lambda d: d < R(1, 100), start=1) == 101
    assert _first_index(lambda m: abs(a(m) - 2), lambda d: d < R(3, 10), start=1) == 4
    assert _seq_limit((2 * n + 1) / n) == 2

    # r^n: 0.9^n < 0.001 first at n = 66; by logs with log 3 ~ 0.4771: log 0.9 = 2 log 3 - 1 ~ -0.0458, 3/0.0458 ~ 65.5.
    assert _first_index(lambda m: R(9, 10) ** m, lambda v: v < R(1, 1000)) == 66
    lg09 = 2 * R(4771, 10000) - 1
    assert lg09 == R(-458, 10000)
    assert 65 < R(3) / R(458, 10000) < 66
    assert abs(sp.N(sp.log(R(9, 10), 10)) - sp.N(lg09)) < 1e-4
    # table values quoted in the figure description: 0.8^n and (-0.5)^n
    assert R(8, 10) ** 5 == R(32768, 100000)
    assert [R(8, 10) ** m for m in range(5)] == [1, R(8, 10), R(64, 100), R(512, 1000), R(4096, 10000)]
    assert R(12, 10) ** 4 < R(22, 10) < R(12, 10) ** 5  # r = 1.2 leaves the figure (top 2.2) at n = 5
    # number-line view, eps = 0.1: a_10 = 2.1 sits on the edge (not inside), a_11 is the first term inside
    assert a(10) == R(21, 10) and _first_index(lambda m: abs(a(m) - 2), lambda d: d < R(1, 10), start=1) == 11
    # squeeze figure: (-1)^n / n for n = 1..4
    assert [R((-1) ** m, m) for m in range(1, 5)] == [-1, R(1, 2), R(-1, 3), R(1, 4)]
    # figure with p = q = 0.05: s = 0.5, r = -0.9
    assert (1 - R(5, 100)) / (2 - R(10, 100)) == R(1, 2) and R(10, 100) - 1 == R(-9, 10)
    assert [R(-1, 2) ** m for m in range(4)] == [1, R(-1, 2), R(1, 4), R(-1, 8)]
    for r_, lim in [(R(9, 10), 0), (R(-1, 2), 0), (R(1), 1)]:
        assert _seq_limit(sp.Integer(1) * r_ ** n) == lim
    assert _seq_limit((-1) ** n) is None
    assert _seq_limit(R(12, 10) ** n) is None

    # Alternative way (binomial theorem): 1/0.9 = 1 + 1/9, so (10/9)^n >= 1 + n/9 > n/9 and 0.9^n < 9/n.
    h = R(1, 9)
    assert 1 / R(9, 10) == 1 + h
    for m in range(1, 400):
        assert (1 + h) ** m >= 1 + m * h
        assert R(9, 10) ** m < R(9, m)
    assert R(9, 9001) < R(1, 1000) and not R(9, 9000) < R(1, 1000)

    # Limit rules: (3n^2 + n)/(n^2 + 5) -> 3; difference (n - 15)/(n^2 + 5), between 0 and 1/n for n >= 15.
    f = (3 * n**2 + n) / (n**2 + 5)
    assert _seq_limit(f) == 3
    assert sp.simplify(f - 3 - (n - 15) / (n**2 + 5)) == 0
    for m in range(15, 300):
        d = R(m - 15, m**2 + 5)
        assert 0 <= d <= R(1, m)
    assert R(3 * 15**2 + 15, 15**2 + 5) == 3

    # Powers: (3^n + 2^n)/(3^n - 2^n) -> 1 (divide by 3^n).
    g = (3**n + 2**n) / (3**n - 2**n)
    assert sp.simplify(g - (1 + R(2, 3) ** n) / (1 - R(2, 3) ** n)) == 0
    assert _seq_limit(g) == 1

    # Squeeze: (-1)^n / n between -1/n and 1/n -> 0.
    assert _seq_limit((-1) ** n / n) == 0

    # Steady state example: p = 0.7, q = 0.6 -> T = [[0.7, 0.4], [0.3, 0.6]], r = 0.3, s = 4/7.
    p, q = R(7, 10), R(6, 10)
    T = _T(p, q)
    assert T == sp.Matrix([[R(7, 10), R(4, 10)], [R(3, 10), R(6, 10)]])
    r = p + q - 1
    s = (1 - q) / (2 - p - q)
    assert r == R(3, 10) and s == R(4, 7)
    assert _steady(T) == sp.Matrix([R(4, 7), R(3, 7)])
    # recursion x_{n+1} = 0.3 x_n + 0.4 and the gap identity
    x = sp.symbols("x")
    assert sp.expand((T * sp.Matrix([x, 1 - x]))[0] - (r * x + (1 - q))) == 0
    assert sp.expand(r * x + (1 - q) - s - r * (x - s)) == 0
    # x0 = 1: matrix steps vs closed form 4/7 + (3/7)(0.3)^n
    st = _states(T, sp.Matrix([1, 0]), 12)
    for m, X in enumerate(st):
        assert X[0] == s + (1 - s) * r**m
    assert [X[0] for X in st[:4]] == [1, R(7, 10), R(61, 100), R(583, 1000)]
    assert st[2] == sp.Matrix([R(61, 100), R(39, 100)])
    assert R(4, 7) + R(3, 7) * R(27, 1000) == R(583, 1000)
    # x0 = 0 in the figure: 0, 0.4, 0.52, 0.556
    st0 = _states(T, sp.Matrix([0, 1]), 3)
    assert [X[0] for X in st0] == [0, R(4, 10), R(52, 100), R(556, 1000)]
    # T^n closed form and its limit (both columns -> the steady state)
    for m in range(0, 10):
        Tm = T**m
        closed = sp.Matrix([[s + (1 - s) * r**m, s - s * r**m], [(1 - s) - (1 - s) * r**m, (1 - s) + s * r**m]])
        assert Tm == closed
    Tn =sp.Matrix([[s + (1 - s) * r**n, s - s * r**n], [(1 - s) - (1 - s) * r**n, (1 - s) + s * r**n]])
    assert Tn.applyfunc(lambda e: sp.limit(e, n, sp.oo)) == sp.Matrix([[s, s], [1 - s, 1 - s]])
    # the general case: r = p + q - 1 in [-1, 1]; r = 1 only for p = q = 1, r = -1 only for p = q = 0
    P, Q = sp.symbols("P Q")
    assert sp.expand((_T(P, Q) * sp.Matrix([x, 1 - x]))[0] - ((P + Q - 1) * x + (1 - Q))) == 0
    assert sp.simplify((1 - Q) / (1 - (P + Q - 1)) - (1 - Q) / (2 - P - Q)) == 0
    # T sends the direction (1, -1) to r times itself (vector view), so X - S shrinks by r each step
    assert sp.simplify(_T(P, Q) * sp.Matrix([1, -1]) - (P + Q - 1) * sp.Matrix([1, -1])) == sp.zeros(2, 1)
    assert T * sp.Matrix([1, -1]) == R(3, 10) * sp.Matrix([1, -1])
    S = sp.Matrix([s, 1 - s])
    assert sp.Matrix([1, 0]) - S == R(3, 7) * sp.Matrix([1, -1])
    # p = q = 0: always switch, oscillates 1, 0, 1, 0 ...; p = q = 1: never moves
    assert [X[0] for X in _states(_T(0, 0), sp.Matrix([1, 0]), 3)] == [1, 0, 1, 0]
    assert _states(_T(1, 1), sp.Matrix([R(3, 10), R(7, 10)]), 2)[2] == sp.Matrix([R(3, 10), R(7, 10)])
    # series view: x_n = r^n x0 + (1-q)(1 + r + ... + r^(n-1)) -> (1-q)/(1-r) = 0.4/0.7 = 4/7
    for m in range(0, 10):
        assert st[m][0] == r**m * 1 + (1 - q) * sum(r**j for j in range(m))
    assert (1 - q) / (1 - r) == R(4, 7)
    # "computing x_10 directly": 4/7 + (3/7)(0.3)^10, already within 0.00001 of 4/7
    assert st[10][0] == R(4, 7) + R(3, 7) * R(3, 10) ** 10
    assert abs(st[10][0] - R(4, 7)) < R(1, 100000)


_worked_examples()


# ---------------------------------------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------------------------------------
def ls_turn_band(item: dict) -> list[bool]:
    """q-turn: a_n = 3 + 2*(0.5)^n. The smallest n with |a_n - 3| < 0.01. Options: 6, 7, 8, 9, 10."""
    m = _first_index(lambda j: abs(3 + 2 * R(1, 2) ** j - 3), lambda d: d < R(1, 100))
    # and the gap keeps shrinking, so every later term stays inside the band
    assert all(abs(2 * R(1, 2) ** j) < R(1, 100) for j in range(m, m + 50))
    return [m == o for o in [6, 7, 8, 9, 10]]


def ls_which_converge(item: dict) -> list[bool]:
    """q1: which sequences converge? (1) (-0.8)^n  (2) (1.01)^n  (3) (-1)^n * n/(n+1)
    (4) (3n^2 - 1)/(n^2 + n)  (5) (2^n + 5^n)/4^n."""
    seqs = [
        R(-8, 10) ** n,
        R(101, 100) ** n,
        (-1) ** n * n / (n + 1),
        (3 * n**2 - 1) / (n**2 + n),
        (2**n + 5**n) / 4**n,
    ]
    return [_seq_limit(s_) is not None for s_ in seqs]


def ls_power_ratio(item: dict) -> tuple[int, int]:
    """q2: lim (4*3^n + 2^n)/(3^(n+1) - 1) = a/b in lowest terms."""
    L = _seq_limit((4 * 3**n + 2**n) / (3 ** (n + 1) - 1))
    L = sp.Rational(L)
    return (int(L.p), int(L.q))


def ls_power_below(item: dict) -> sp.Integer:
    """q3: smallest positive integer n with 0.8^n < 0.001 (log 2 ~ 0.3010 given)."""
    m = _first_index(lambda j: R(8, 10) ** j, lambda v: v < R(1, 1000), start=1)
    # the stem's route agrees: log 0.8 = 3 log 2 - 1 ~ -0.0970, n > 3/0.0970 ~ 30.9
    lg08 = 3 * R(3010, 10000) - 1
    assert 30 < R(3) / (-lg08) < 31
    return sp.Integer(m)


def ls_steady_statements(item: dict) -> list[bool]:
    """q4: T = [[0.6, 0.2], [0.4, 0.8]] (column = this month's state 甲/乙, row = next month's).
    (1) the steady share of 甲 is 1/3; (2) starting all in 甲, x_n - 1/3 = (2/3)(0.4)^n;
    (3) the long-run share depends on the starting share; (4) each month the gap to the steady share becomes 0.6 times;
    (5) as n grows, both columns of T^n approach (1/3, 2/3)."""
    T = sp.Matrix([[R(6, 10), R(2, 10)], [R(4, 10), R(8, 10)]])
    S = _steady(T)
    s1 = S[0] == R(1, 3)
    st = _states(T, sp.Matrix([1, 0]), 15)
    s2 = all(st[m][0] - R(1, 3) == R(2, 3) * R(4, 10) ** m for m in range(16))
    # (3): two different starts; their long-run limits (from the exact gap ratio) coincide
    x0s = [sp.Integer(0), R(1, 2), sp.Integer(1)]
    limits = set()
    for x0 in x0s:
        seq = _states(T, sp.Matrix([x0, 1 - x0]), 30)
        ratios = {(seq[m + 1][0] - S[0]) / (seq[m][0] - S[0]) for m in range(30) if seq[m][0] != S[0]}
        assert len(ratios) == 1  # the gap is a geometric sequence
        c = ratios.pop()
        # x_n = S + (x0 - S) c^n, checked against the computed terms, then its limit
        assert all(seq[m][0] == S[0] + (x0 - S[0]) * c**m for m in range(31))
        limits.add(sp.limit(S[0] + (x0 - S[0]) * c**n, n, sp.oo))
    s3 = len(limits) > 1
    seq = _states(T, sp.Matrix([0, 1]), 5)
    gap_ratio = {(seq[m + 1][0] - S[0]) / (seq[m][0] - S[0]) for m in range(5)}
    s4 = gap_ratio == {R(6, 10)}
    # (5) T^n entrywise limit, using T = closed form verified against powers
    Tn_lim = None
    r = T[0, 0] - T[0, 1]
    for m in range(8):
        Tm = T**m
        assert Tm[:, 0] - S == (1 - S[0]) * r**m * sp.Matrix([1, -1])
        assert Tm[:, 1] - S == -S[0] * r**m * sp.Matrix([1, -1])
    assert abs(r) < 1
    Tn_lim = sp.Matrix.hstack(S, S)
    s5 = Tn_lim == sp.Matrix([[R(1, 3), R(1, 3)], [R(2, 3), R(2, 3)]])
    return [s1, s2, s3, s4, s5]


def ls_closed_form_x3(item: dict) -> sp.Integer:
    """q5: T = [[0.9, 0.3], [0.1, 0.7]], x_0 = 0.25 (share of 甲). x_3 = 0.①②③ ; return the three digits as 642-style integer."""
    T = sp.Matrix([[R(9, 10), R(3, 10)], [R(1, 10), R(7, 10)]])
    x3 = _states(T, sp.Matrix([R(1, 4), R(3, 4)]), 3)[3][0]
    # the closed form quoted in the explanation agrees: 0.75 - 0.5*(0.6)^3
    assert _steady(T)[0] == R(3, 4)
    assert x3 == R(3, 4) - R(1, 2) * R(6, 10) ** 3
    v = x3 * 1000
    assert v.is_integer and 100 <= v < 1000
    return sp.Integer(v)


def ls_which_not_settle(item: dict) -> list[bool]:
    """q6: T = [[p, 1-q], [1-p, q]]. For which (p, q) is there a starting share x_0 for which x_n does NOT converge?
    Options: (0.5, 0.5), (1, 0.3), (0, 0), (0.9, 0.9), (0.2, 0.1)."""
    opts = [(R(1, 2), R(1, 2)), (1, R(3, 10)), (0, 0), (R(9, 10), R(9, 10)), (R(2, 10), R(1, 10))]
    out = []
    x0 = sp.symbols("x0")
    for p, q in opts:
        T = _T(sp.Rational(p), sp.Rational(q))
        # x_{n+1} = c x_n + d, read off from one multiplication with a symbolic start
        nxt = sp.expand((T * sp.Matrix([x0, 1 - x0]))[0])
        c, d = nxt.coeff(x0, 1), nxt.coeff(x0, 0)
        if c == 1:
            bad = d != 0  # x_n = x_0 + n d: diverges unless d = 0
        elif abs(c) < 1:
            bad = False  # x_n - s = c^n (x_0 - s) -> 0 for every start
        else:
            s_ = d / (1 - c)
            bad = any(x != s_ for x in [0, 1])  # c = -1 (or |c| > 1): the gap never shrinks unless x_0 = s
            # confirm by stepping from x_0 = 1
            seq = _states(T, sp.Matrix([1, 0]), 6)
            assert len({X[0] for X in seq[::2]}) == 1 and seq[0][0] != seq[1][0]
        out.append(bool(bad))
    return out


def ls_steps_within(item: dict) -> sp.Integer:
    """q7: T = [[0.8, 0.5], [0.2, 0.5]], start all in 甲. Smallest n with |x_n - s| < 0.01, s the steady share of 甲."""
    T = sp.Matrix([[R(8, 10), R(5, 10)], [R(2, 10), R(5, 10)]])
    s = _steady(T)[0]
    assert s == R(5, 7)
    st = _states(T, sp.Matrix([1, 0]), 40)
    m = _first_index(lambda j: abs(st[j][0] - s), lambda d_: d_ < R(1, 100))
    assert all(abs(st[j][0] - s) < R(1, 100) for j in range(m, 40))
    return sp.Integer(m)
