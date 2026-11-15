"""Checks for src/data/items/math/x-derivative-extrema.yaml (分科 advanced tool: derivatives for
increase/decrease, extrema and root counts; not on the 學測).

Each item check recomputes its answer from the mathematics with SymPy; none reads item["answer"].
Rising/falling sets come from solving f'(x) < 0 or > 0 as inequalities, extrema from where f' changes
sign, root counts from SymPy's real-root isolation. `_worked_examples()` re-derives every number the
chapter's worked examples and dialogues state; it runs at import, so a wrong example fails the harness.
"""

from __future__ import annotations

import sympy as sp

x, t, h, k, s, u = sp.symbols("x t h k s u", real=True)
R = sp.S.Reals


def _d(f: sp.Expr, n: int = 1) -> sp.Expr:
    return sp.expand(sp.diff(f, x, n))


def _where(cond) -> sp.Set:
    return sp.solveset(cond, x, R)


def _distinct_real_roots(f: sp.Expr) -> int:
    return len(set(sp.Poly(f, x).real_roots()))


def _extrema(f: sp.Expr) -> tuple[list, list]:
    """(local maxima, local minima) as (x0, f(x0)) pairs, from the sign of f' on each side of its roots."""
    fp = _d(f)
    crit = sorted(set(sp.Poly(fp, x).real_roots()))
    maxima, minima = [], []
    for c in crit:
        left, right = fp.subs(x, c - sp.Rational(1, 1000)), fp.subs(x, c + sp.Rational(1, 1000))
        # Critical points here are integers far apart, so ±0.001 lies on the correct side of each.
        if left > 0 and right < 0:
            maxima.append((c, f.subs(x, c)))
        elif left < 0 and right > 0:
            minima.append((c, f.subs(x, c)))
    return maxima, minima


def _centre_is(f: sp.Expr, h0, k0) -> bool:
    return sp.expand(f.subs(x, h0 + t) + f.subs(x, h0 - t) - 2 * k0) == 0


def _worked_examples() -> None:
    # Opening dialogue (q-turn): sign changes of x³ − 3x + 1 at −2, −1, 0, 1, 2.
    g = x**3 - 3 * x + 1
    assert [g.subs(x, v) for v in (-2, -1, 0, 1, 2)] == [-1, 3, 1, -1, 3]
    # Closing dialogue: g' = 3(x + 1)(x − 1), local max g(−1) = 3 > 0, local min g(1) = −1 < 0.
    assert sp.expand(_d(g) - 3 * (x - 1) * (x + 1)) == 0
    assert _extrema(g) == ([(-1, 3)], [(1, -1)])

    # The running example f(x) = x³ − 6x² + 9x + 1.
    f = x**3 - 6 * x**2 + 9 * x + 1
    assert _d(f) == 3 * x**2 - 12 * x + 9 and sp.expand(_d(f) - 3 * (x - 3) * (x - 1)) == 0
    assert _d(f).subs(x, 0) == 9 and _d(f).subs(x, 2) == -3
    assert f.subs(x, 2) == 3  # tangent at x = 2 is y = −3(x − 2) + 3
    assert _where(_d(f) > 0) == sp.Union(sp.Interval.open(-sp.oo, 1), sp.Interval.open(3, sp.oo))
    assert _where(_d(f) < 0) == sp.Interval.open(1, 3)
    assert _extrema(f) == ([(1, 5)], [(3, 1)])
    assert f.subs(x, 5) == 21  # the local maximum 5 is not the largest value
    assert _d(f, 2) == 6 * x - 12 and _d(f, 2).subs(x, 1) == -6 and _d(f, 2).subs(x, 3) == 6
    assert _where(_d(f, 2) < 0) == sp.Interval.open(-sp.oo, 2) and _where(_d(f, 2) > 0) == sp.Interval.open(2, sp.oo)
    assert _centre_is(f, 2, 3)
    assert sp.expand((x - 2) ** 3 - 3 * (x - 2) + 3 - f) == 0
    # 10年級 view: the difference identity for t³ − 3t.
    t1, t2 = sp.symbols("t1 t2", real=True)
    assert sp.expand((t2**3 - 3 * t2) - (t1**3 - 3 * t1) - (t2 - t1) * (t1**2 + t1 * t2 + t2**2 - 3)) == 0
    assert (-1) ** 2 + (-1) * 1 + 1**2 == 1  # t1 = −1, t2 = 1 gives 1 < 3
    # Horizontal tangents as double roots.
    assert sp.expand((x - 1) ** 2 * (x - 4) - (f - 5)) == 0
    assert sp.expand(x * (x - 3) ** 2 - (f - 1)) == 0
    # Coefficient comparison x³ − 6x² + 9x + (1 − k) = (x − r)²(x − q).
    r, q = sp.symbols("r q", real=True)
    eqs = sp.Poly(sp.expand((x - r) ** 2 * (x - q) - (f - k)), x).coeffs()
    sols = sp.solve(eqs, [r, q, k], dict=True)
    assert sorted((sl[r], sl[q], sl[k]) for sl in sols) == [(1, 4, 5), (3, 0, 1)]
    assert sp.solve(sp.Eq(r**2 + 2 * r * (6 - 2 * r), 9), r) == [1, 3]
    # Number of solutions of f(x) = k by range of k.
    for kv, n in [(6, 1), (5, 2), (3, 3), (1, 2), (0, 1), (sp.Rational(9, 2), 3), (-4, 1)]:
        assert _distinct_real_roots(f - kv) == n, (kv, n)
    assert [f.subs(x, v) - 3 for v in (0, 1, 3, 4)] == [-2, 2, -2, 2]  # k = 3: three sign changes
    assert _d(f).subs(x, 1) == 0 and f.subs(x, 1) - 5 == 0  # f(1) = f'(1) = 0 for f − 5
    assert f.subs(x, 2) == 8 - 24 + 18 + 1 and _d(f).subs(x, 2) == 12 - 24 + 9

    # TryIt: y = x³ − 3x has local max 2 at x = −1 and local min −2 at x = 1, symmetric about O.
    assert _extrema(x**3 - 3 * x) == ([(-1, 2)], [(1, -2)])
    # q7 counterexample: x³ − (3/2)x² + 10 has α = 0, β = 1, local min 19/2 > 0 and one real root.
    c7 = x**3 - sp.Rational(3, 2) * x**2 + 10
    assert _extrema(c7) == ([(0, 10)], [(1, sp.Rational(19, 2))]) and _distinct_real_roots(c7) == 1
    # q-turn / q2 / q4 / q5 explanation arithmetic.
    assert (2 * x**3 - 3 * x**2 - 12 * x + 4).subs(x, -1) == 11 and (2 * x**3 - 3 * x**2 - 12 * x + 4).subs(x, 2) == -16
    assert (x**3 + 3 * x**2 - 24 * x).subs(x, -4) == 80 and (x**3 + 3 * x**2 - 24 * x).subs(x, 2) == -28
    assert sp.expand(x**3 + 3 * x**2 + 3 * x - 2 - ((x + 1) ** 3 - 3)) == 0

    # Fence: A = x(40 − 2x), 0 < x < 20; max 200 at x = 10; if x ≤ 8, max A(8) = 192.
    A = x * (40 - 2 * x)
    assert _d(A) == 40 - 4 * x and sp.solve(_d(A), x) == [10] and A.subs(x, 10) == 200
    assert sp.expand(-2 * (x - 10) ** 2 + 200 - A) == 0
    assert A.subs(x, 8) == 192 and all(_d(A).subs(x, v) > 0 for v in range(0, 9))

    # Box: V = x(12 − 2x)², 0 < x < 6; V' = 12(x − 2)(x − 6); max V(2) = 128; V − 128 = 4(x − 2)²(x − 8).
    V = x * (12 - 2 * x) ** 2
    assert sp.expand(V) == 4 * x**3 - 48 * x**2 + 144 * x
    assert sp.expand(_d(V) - 12 * (x - 6) * (x - 2)) == 0
    assert V.subs(x, 2) == 128 and 12 - 2 * 2 == 8
    assert sp.expand(4 * (x - 2) ** 2 * (x - 8) - (V - 128)) == 0
    assert sp.expand((x - 2) ** 2 * (x - 8)) == x**3 - 12 * x**2 + 36 * x - 32


_worked_examples()


# ---------- items ----------

def de_turn_root_count(item: dict) -> list[bool]:
    """q-turn: how many real roots does x³ − 3x + 1 = 0 have? Options: 0, 1, 2, 3, cannot tell."""
    n = _distinct_real_roots(x**3 - 3 * x + 1)
    return [n == 0, n == 1, n == 2, n == 3, False]


def de_decreasing_interval(item: dict) -> list[bool]:
    """q1: where is f(x) = x³ − 3x² − 9x + 5 decreasing? Options as open sets."""
    f = x**3 - 3 * x**2 - 9 * x + 5
    dec = _where(_d(f) < 0)
    opts = [
        sp.Interval.open(-sp.oo, -1),
        sp.Interval.open(-1, 3),
        sp.Interval.open(3, sp.oo),
        sp.Interval.open(-3, 1),
        sp.Union(sp.Interval.open(-sp.oo, -1), sp.Interval.open(3, sp.oo)),
    ]
    return [o == dec for o in opts]


def de_max_min_fill(item: dict) -> tuple[int, int]:
    """q2: the local maximum value ①② and the local minimum value ③④⑤ of 2x³ − 3x² − 12x + 4."""
    maxima, minima = _extrema(2 * x**3 - 3 * x**2 - 12 * x + 4)
    assert len(maxima) == 1 and len(minima) == 1
    return (maxima[0][1], minima[0][1])


def de_monotone_cubic(item: dict) -> list[bool]:
    """q3: statements about g(x) = x³ + 3x² + 3x − 2.
    (1) g'(x) ≥ 0 for every real x; (2) g has a local maximum; (3) g(x) = 0 has exactly one real root;
    (4) the graph's point of symmetry is (−1, −3); (5) g''(x) > 0 for every real x."""
    g = x**3 + 3 * x**2 + 3 * x - 2
    maxima, _ = _extrema(g)
    return [
        _where(_d(g) < 0) == sp.S.EmptySet,
        len(maxima) > 0,
        _distinct_real_roots(g) == 1,
        _centre_is(g, -1, -3),
        _where(_d(g, 2) <= 0) == sp.S.EmptySet,
    ]


def de_three_roots_range(item: dict) -> tuple[int, int]:
    """q4: x³ + 3x² − 24x = k has three distinct real roots exactly when −①② < k < ③④."""
    f = x**3 + 3 * x**2 - 24 * x
    maxima, minima = _extrema(f)
    lo, hi = minima[0][1], maxima[0][1]
    # Confirm the range by counting roots just inside and outside each end.
    for kv, n in [(lo - 1, 1), (lo, 2), (lo + 1, 3), (hi - 1, 3), (hi, 2), (hi + 1, 1)]:
        assert _distinct_real_roots(f - kv) == n, (kv, n)
    return (-lo, hi)


def de_rectangle_area(item: dict) -> list[bool]:
    """q5: largest area of a rectangle with base on the x-axis and top corners on y = 12 − x².
    Options: 16, 24, 32, 36, 48."""
    A = 2 * x * (12 - x**2)  # corners (±x, 0), (±x, 12 − x²), 0 < x < 2√3
    crit = [c for c in sp.solve(_d(A), x) if 0 < c < 2 * sp.sqrt(3)]
    assert len(crit) == 1
    best = A.subs(x, crit[0])
    # A → 0 at both ends of the domain, and A − best ≤ 0 there: check A − best = −2(x − c)²(x + 4).
    assert sp.expand(A - best + 2 * (x - crit[0]) ** 2 * (x + 4)) == 0
    return [best == v for v in (16, 24, 32, 36, 48)]


def de_concave_up(item: dict) -> list[bool]:
    """q6: where is the graph of x³ − 9x² + 15x + 2 concave up (f'' > 0)?"""
    f = x**3 - 9 * x**2 + 15 * x + 2
    up = _where(_d(f, 2) > 0)
    opts = [
        sp.Interval.open(3, sp.oo),
        sp.Interval.open(-sp.oo, 3),
        sp.Interval.open(1, 5),
        sp.Union(sp.Interval.open(-sp.oo, 1), sp.Interval.open(5, sp.oo)),
        sp.Interval.open(-3, sp.oo),
    ]
    return [o == up for o in opts]


def de_general_cubic(item: dict) -> list[bool]:
    """q7: f is a cubic with a > 0 whose f'(x) = 0 has two real roots α < β.
    (1) f(α) is a local maximum; (2) f decreases for α < x < β; (3) f''(α) > 0; (4) f(α) > f(β);
    (5) f(x) = 0 always has three real roots."""
    a, dd = sp.symbols("a d", positive=True)
    al, C = sp.symbols("alpha C", real=True)
    be = al + dd
    fp = 3 * a * (x - al) * (x - be)
    f = sp.integrate(sp.expand(fp), x) + C  # every such cubic: leading coefficient a, any constant C
    f2 = sp.diff(fp, x)
    # A point strictly between α and β: α + s·d with s = u/(1 + u), u > 0, so 0 < s < 1.
    up = sp.Symbol("u", positive=True)
    mid = al + up / (1 + up) * dd
    drop = sp.simplify(f.subs(x, al) - f.subs(x, be))
    # (5): one instance (a = 1, α = 0, d = 1, C = 10) has a single real root, so "always" fails.
    inst = f.subs({a: 1, al: 0, dd: 1, C: 10})
    return [
        bool(sp.simplify(f2.subs(x, al)).is_negative),  # f' changes + → − at α (second-derivative test)
        bool(sp.simplify(fp.subs(x, mid)).is_negative),
        bool(sp.simplify(f2.subs(x, al)).is_positive),
        bool(drop.is_positive),
        _distinct_real_roots(inst) == 3,
    ]
