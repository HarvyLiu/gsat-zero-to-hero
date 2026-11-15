"""Checks for src/data/items/math/s116-logic-toolbox.yaml (116 sprint, N-10-7 logic toolbox).

Each function recomputes its item's answer from the mathematics; none reads item["answer"].
"If P then Q" over the reals is judged as set inclusion: it is true exactly when every real x that
makes P true also makes Q true, i.e. solveset(P) is a subset of solveset(Q) (an empty P is vacuously true).
"""

from __future__ import annotations

from itertools import product

import sympy as sp

x = sp.Symbol("x", real=True)
R = sp.S.Reals


def _sol(cond) -> sp.Set:
    return sp.solveset(cond, x, domain=R)


def _implies(p, q) -> bool:
    """Is "if p then q" true for every real x?"""
    return bool(_sol(p).is_subset(_sol(q)))


# ---------- s116-logic-toolbox ----------

def lg_turn_counterexample(item: dict) -> list[bool]:
    """q-turn: which x is a counterexample to "if x² > 4 then x > 2"?
    A counterexample makes the hypothesis true and the conclusion false. Options: 3, −3, 1, 2, 0."""
    options = [sp.Integer(3), sp.Integer(-3), sp.Integer(1), sp.Integer(2), sp.Integer(0)]
    return [bool(v**2 > 4) and not bool(v > 2) for v in options]


def _all_predicates(domain: tuple) -> list[dict]:
    """Every predicate on a finite domain, as {element: truth}."""
    return [dict(zip(domain, bits)) for bits in product([False, True], repeat=len(domain))]


def lg_negate_forall(item: dict) -> list[bool]:
    """q1: the negation of "every real x satisfies x² ≥ x".
    Write A(x) for "x² ≥ x"; "x² < x" is then "not A(x)". The options, as formulas in A:
      (1) for all x, not A(x)   (2) there is x with not A(x)   (3) there is x with A(x)
      (4) for no x, A(x)        (5) for all x, not (not A(x))  ("no real x has x² < x")
    An option is the negation exactly when it agrees with "not (for all x, A(x))" for every predicate A;
    we enumerate every predicate on a 3-element domain, which already separates all five forms."""
    dom = (0, 1, 2)
    verdicts = [True] * 5
    for A in _all_predicates(dom):
        neg = not all(A[d] for d in dom)
        opts = [
            all(not A[d] for d in dom),
            any(not A[d] for d in dom),
            any(A[d] for d in dom),
            not any(A[d] for d in dom),
            all(not (not A[d]) for d in dom),
        ]
        for i, o in enumerate(opts):
            if o != neg:
                verdicts[i] = False
    # The statement itself is false (x = 1/2 gives x² < x), so its negation is the true one.
    assert _sol(x**2 >= x) != R
    return verdicts


def lg_and_or_truth(item: dict) -> list[bool]:
    """q2: which compound statement is true?
      (1) √4 is irrational or 3 is even       (2) 2 is prime and 2 is odd
      (3) π is irrational or π > 4            (4) 5 is prime and 5² < 20
      (5) −3 > −2 or (−3)² < (−2)²"""
    s4 = sp.sqrt(4)
    atoms = [
        (bool(s4.is_irrational), sp.Integer(3) % 2 == 0, "or"),
        (sp.isprime(2), sp.Integer(2) % 2 == 1, "and"),
        (bool(sp.pi.is_irrational), bool(sp.pi > 4), "or"),
        (sp.isprime(5), bool(sp.Integer(5) ** 2 < 20), "and"),
        (bool(sp.Integer(-3) > -2), bool(sp.Integer(-3) ** 2 < sp.Integer(-2) ** 2), "or"),
    ]
    return [(a or b) if op == "or" else (a and b) for a, b, op in atoms]


def lg_count_even_or_mult3(item: dict) -> sp.Integer:
    """q3: how many integers n with 1 ≤ n ≤ 30 make "n is even or n is a multiple of 3" true (inclusive or)."""
    return sp.Integer(sum(1 for n in range(1, 31) if n % 2 == 0 or n % 3 == 0))


def lg_which_implications(item: dict) -> list[bool]:
    """q4: which "if … then …" statements hold for every real x?
      (1) x > 3 ⇒ x² > 9     (2) x² > 9 ⇒ x > 3     (3) |x| < 1 ⇒ x < 1
      (4) x < 1 ⇒ |x| < 1    (5) x² < 0 ⇒ x > 5 (vacuously true: no real x has x² < 0)"""
    pairs = [
        (x > 3, x**2 > 9),
        (x**2 > 9, x > 3),
        (sp.Abs(x) < 1, x < 1),
        (x < 1, sp.Abs(x) < 1),
        (x**2 < 0, x > 5),
    ]
    return [_implies(p, q) for p, q in pairs]


def lg_condition_kind(item: dict) -> list[bool]:
    """q5: for real x, p: "x² − 5x + 6 = 0" and q: "x = 2". What kind of condition is p for q?
    Options: (1) sufficient, not necessary (2) necessary, not sufficient (3) necessary and sufficient
    (4) neither. p is sufficient for q when p ⇒ q, necessary when q ⇒ p."""
    P = _sol(sp.Eq(x**2 - 5 * x + 6, 0))
    Q = _sol(sp.Eq(x, 2))
    suff = bool(P.is_subset(Q))
    nec = bool(Q.is_subset(P))
    return [suff and not nec, nec and not suff, suff and nec, not suff and not nec]


def lg_negate_or(item: dict) -> list[bool]:
    """q6: for given reals a, b, the negation of "a ≥ 1 or b < 0".
    Options: (1) a<1 or b≥0  (2) a<1 and b≥0  (3) a≤1 and b>0  (4) a≥1 and b<0  (5) a<1 and b>0.
    An option is the negation exactly when it has the opposite truth value to "a ≥ 1 or b < 0" for
    every (a, b). Each condition only compares a with 1 and b with 0, so its truth value is constant on
    each of the regions a<1, a=1, a>1 (and b<0, b=0, b>0); a grid that samples every region is exhaustive."""
    half = sp.Rational(1, 2)
    grid_a = [sp.Integer(0), sp.Integer(1), sp.Integer(2), half, sp.Integer(-3)]
    grid_b = [sp.Integer(-1), sp.Integer(0), sp.Integer(1), -half, sp.Integer(3)]
    opts = [
        lambda a, b: bool(a < 1) or bool(b >= 0),
        lambda a, b: bool(a < 1) and bool(b >= 0),
        lambda a, b: bool(a <= 1) and bool(b > 0),
        lambda a, b: bool(a >= 1) and bool(b < 0),
        lambda a, b: bool(a < 1) and bool(b > 0),
    ]
    verdicts = [True] * len(opts)
    for a in grid_a:
        for b in grid_b:
            original = bool(a >= 1) or bool(b < 0)
            for i, f in enumerate(opts):
                if f(a, b) == original:
                    verdicts[i] = False
    return verdicts


def lg_condition_abs(item: dict) -> list[bool]:
    """q7: for real x, p: "|x| = x" and q: "x ≥ 0". What kind of condition is p for q?
    Options as in q5. p is sufficient for q when p ⇒ q, necessary when q ⇒ p."""
    P = _sol(sp.Eq(sp.Abs(x), x))
    Q = _sol(x >= 0)
    suff = bool(P.is_subset(Q))
    nec = bool(Q.is_subset(P))
    return [suff and not nec, nec and not suff, suff and nec, not suff and not nec]
