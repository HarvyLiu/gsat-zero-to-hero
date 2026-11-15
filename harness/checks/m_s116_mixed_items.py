"""Checks for src/data/items/math/s116-mixed-items.yaml (116 sprint, exam skills: writing mixed items).

Each function recomputes its item's answer from the mathematics; none reads item["answer"].
The chapter is about complete reasoning, so most items hinge on a step a weak answer skips:
dividing by an expression that may be 0, squaring both sides without checking the roots,
cancelling a factor outside the domain, or comparing values without citing monotonicity.
"""

from __future__ import annotations

from itertools import product

import sympy as sp

x = sp.Symbol("x", real=True)
R = sp.S.Reals


def _real_solutions(expr) -> sp.Set:
    return sp.solveset(expr, x, domain=R)


def _sqrt_equation_roots(inside, rhs) -> tuple[set, set]:
    """sqrt(inside) = rhs: (candidates after squaring, candidates that satisfy the original)."""
    squared = sp.Poly(sp.expand(rhs**2 - inside), x)
    candidates = {r for r in sp.roots(squared, filter="R")}
    kept = {r for r in candidates if sp.simplify(inside.subs(x, r)) >= 0 and sp.simplify(sp.sqrt(inside.subs(x, r)) - rhs.subs(x, r)) == 0}
    # cross-check with SymPy's own solver on the unsquared equation
    assert _real_solutions(sp.sqrt(inside) - rhs) == sp.FiniteSet(*kept)
    return candidates, kept


# ---------- s116-mixed-items ----------

def mx_turn_divide_by_x(item: dict) -> list[bool]:
    """q-turn: real solutions of x² = 3x (dividing both sides by x loses x = 0).
    Options as solution sets: {0, 3}, {3}, {−3, 3}, ∅, {0}."""
    sol = _real_solutions(x**2 - 3 * x)
    options = [
        sp.FiniteSet(0, 3),
        sp.FiniteSet(3),
        sp.FiniteSet(-3, 3),
        sp.S.EmptySet,
        sp.FiniteSet(0),
    ]
    return [sol == o for o in options]


def mx_sqrt_check_roots(item: dict) -> list[bool]:
    """q1: sqrt(x+3) = x − 3. Squaring gives x² − 7x + 6 = 0, i.e. x = 1 or 6; only 6 survives the check.
    Options: {1, 6}, {6}, {1}, ∅, {−6}."""
    candidates, kept = _sqrt_equation_roots(x + 3, x - 3)
    assert candidates == {1, 6}
    sol = sp.FiniteSet(*kept)
    options = [sp.FiniteSet(1, 6), sp.FiniteSet(6), sp.FiniteSet(1), sp.S.EmptySet, sp.FiniteSet(-6)]
    return [sol == o for o in options]


def mx_valid_inferences(item: dict) -> list[bool]:
    """q2: which inferences hold for all real a, b, c?
      (1) a² = b² ⇒ a = b          (2) ab = 0 ⇒ a = 0 or b = 0     (3) a > b ⇒ a² > b²
      (4) a > b > 0 ⇒ 1/a < 1/b    (5) ac = bc ⇒ a = b
    A finite grid of rationals is searched for a counterexample; an option with none found is then
    proved symbolically, so a True verdict never rests on the grid alone."""
    grid = [sp.Rational(n, 2) for n in range(-6, 7)]
    claims = [
        (lambda a, b, c: a**2 == b**2, lambda a, b, c: a == b),
        (lambda a, b, c: a * b == 0, lambda a, b, c: a == 0 or b == 0),
        (lambda a, b, c: a > b, lambda a, b, c: a**2 > b**2),
        (lambda a, b, c: a > b > 0, lambda a, b, c: 1 / a < 1 / b),
        (lambda a, b, c: a * c == b * c, lambda a, b, c: a == b),
    ]
    verdicts = []
    for hyp, concl in claims:
        counter = any(hyp(a, b, c) and not concl(a, b, c) for a, b, c in product(grid, repeat=3))
        verdicts.append(not counter)

    # symbolic proofs for the options the grid could not refute
    b = sp.Symbol("b", real=True)
    # (2): if a = 0 the conclusion holds at once; if a ≠ 0, ab = 0 forces b = 0
    a_nonzero = sp.Symbol("a", real=True, nonzero=True)
    proof2 = sp.solveset(a_nonzero * b, b, domain=R) == sp.FiniteSet(0)
    # (4): 1/b − 1/a = (a − b)/(ab) with a − b > 0 and ab > 0
    p, q = sp.symbols("p q", positive=True)  # b = q > 0, a = q + p > q
    proof4 = sp.simplify(1 / q - 1 / (q + p) - p / (q * (q + p))) == 0 and (p / (q * (q + p))).is_positive is True
    proofs = {1: proof2, 3: proof4}
    for i, v in enumerate(verdicts):
        if v:
            if i not in proofs or not proofs[i]:
                raise AssertionError(f"option ({i + 1}) has no counterexample on the grid but no proof either")
    return verdicts


def mx_am_gm_minimum(item: dict) -> tuple:
    """q3: for x > 0, the minimum of 4x + 25/x and where it is attained.
    AM–GM: 4x + 25/x ≥ 2·sqrt(100) = 20, equal when 4x = 25/x, i.e. x = 5/2. Cells ①② = 20, ③/④ = 5/2."""
    t = sp.Symbol("t", positive=True)
    f = 4 * t + 25 / t
    bound = 2 * sp.sqrt(4 * 25)
    eq_pts = sp.solve(sp.Eq(4 * t, 25 / t), t)
    assert len(eq_pts) == 1
    x0 = eq_pts[0]
    assert sp.simplify(f.subs(t, x0) - bound) == 0
    # f − bound = (2√t − 5/√t)² ≥ 0 confirms bound is the minimum for every t > 0
    assert sp.simplify(f - bound - (2 * sp.sqrt(t) - 5 / sp.sqrt(t)) ** 2) == 0
    x0 = sp.Rational(x0)
    return (bound, x0.p, x0.q)


def mx_cite_monotonicity(item: dict) -> list[bool]:
    """q4: which property justifies (1/2)^0.3 > (1/2)^0.7?
    Options: (1) y=(1/2)^x is strictly increasing on R, (2) strictly decreasing on R,
    (3) its graph is symmetric about the y-axis, (4) (1/2)^x < 1 for every real x, (5) its graph passes (1, 0).
    Only a true statement that also yields the inequality from 0.3 < 0.7 counts."""
    f = sp.Rational(1, 2) ** x
    inc = bool(sp.is_strictly_increasing(f, R))
    dec = bool(sp.is_strictly_decreasing(f, R))
    sym = sp.simplify(f.subs(x, -x) - f) == 0
    always_lt_1 = bool(f.subs(x, -1) < 1)  # x = −1 gives 2, so the claim fails
    through_1_0 = f.subs(x, 1) == 0
    truths = [inc, dec, sym, always_lt_1, through_1_0]
    # the claim to be justified is itself true, and decreasing is what turns 0.3 < 0.7 into it
    assert sp.Rational(3, 10) < sp.Rational(7, 10)
    assert bool(f.subs(x, sp.Rational(3, 10)) > f.subs(x, sp.Rational(7, 10)))
    justifies = [False, True, False, False, False]  # (1) would give the opposite inequality
    return [t and j for t, j in zip(truths, justifies)]


def mx_written_sqrt_equation(item: dict) -> bool:
    """q5 (written): sqrt(2x+7) = x + 2. Squaring: x² + 2x − 3 = (x + 3)(x − 1) = 0;
    x = 1 checks (√9 = 3), x = −3 does not (√1 = 1 ≠ −1). The only solution is x = 1."""
    square_step = sp.expand((x + 2) ** 2 - (2 * x + 7)) == sp.expand(x**2 + 2 * x - 3)
    factor_step = sp.expand((x + 3) * (x - 1)) == sp.expand(x**2 + 2 * x - 3)
    candidates, kept = _sqrt_equation_roots(2 * x + 7, x + 2)
    check_1 = sp.sqrt(9) == 3 and (2 * 1 + 7) == 9
    check_m3 = (2 * (-3) + 7) == 1 and (-3 + 2) == -1
    return square_step and factor_step and candidates == {1, -3} and kept == {1} and check_1 and check_m3


def mx_written_n3_minus_n(item: dict) -> bool:
    """q6 (written): n³ − n is a multiple of 6 for every positive integer n.
    n³ − n = (n − 1)n(n + 1); among three consecutive integers one is even and one is a multiple of 3,
    and 2, 3 are coprime. Checked: the factorisation, and n³ − n ≡ 0 (mod 6) for every residue of n mod 6
    (n³ − n mod 6 depends only on n mod 6, so this covers every integer)."""
    n = sp.Symbol("n", integer=True)
    identity = sp.expand((n - 1) * n * (n + 1) - (n**3 - n)) == 0
    residues = all(((r**3 - r) % 6) == 0 for r in range(6))
    consecutive = all(any(k % 2 == 0 for k in (r - 1, r, r + 1)) and any(k % 3 == 0 for k in (r - 1, r, r + 1)) for r in range(6))
    return identity and residues and consecutive and sp.gcd(2, 3) == 1


def mx_cancel_outside_domain(item: dict) -> list[bool]:
    """q7: real solutions of (x² − 4)/(x − 2) = 4. Cancelling gives x + 2 = 4, x = 2, but x = 2 makes
    the denominator 0, so there is no solution. Options: {2}, {−2}, {2, −2}, ∅, {4}."""
    numer_roots = _real_solutions(sp.expand(x**2 - 4 - 4 * (x - 2)))  # x² − 4x + 4 = 0 → {2}
    domain_bad = _real_solutions(x - 2)
    sol = numer_roots - domain_bad
    assert sol == _real_solutions((x**2 - 4) / (x - 2) - 4)
    options = [sp.FiniteSet(2), sp.FiniteSet(-2), sp.FiniteSet(2, -2), sp.S.EmptySet, sp.FiniteSet(4)]
    return [sol == o for o in options]
