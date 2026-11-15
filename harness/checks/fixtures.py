"""Checks for the TEST FIXTURES in tests/fixtures/items/ (not lesson content).

Each function recomputes its item's answer from the stem with SymPy; none reads item["answer"].
"""

from __future__ import annotations

import re

import sympy as sp

x = sp.Symbol("x")


def sqrt_product(item: dict) -> list[bool]:
    """fx-sqrt: the value of √2 × √8, against options 2, 4, √10, 8, 16."""
    value = sp.sqrt(2) * sp.sqrt(8)
    options = [sp.Integer(2), sp.Integer(4), sp.sqrt(10), sp.Integer(8), sp.Integer(16)]
    return [sp.simplify(value - o) == 0 for o in options]


def irrational_options(item: dict) -> list[bool | None]:
    """fx-irrational: which of √4, √5, 0.(3), π, 22/7 are irrational.

    Returned raw: if SymPy could not decide one (None), the harness reports it instead of reading it as False.
    """
    options = [sp.sqrt(4), sp.sqrt(5), sp.Rational(1, 3), sp.pi, sp.Rational(22, 7)]
    return [o.is_irrational for o in options]


def solve_linear_fill(item: dict) -> sp.Integer:
    """fx-linear: x from 2x + 30 = 6."""
    (root,) = sp.solve(sp.Eq(2 * x + 30, 6), x)
    return root


def fraction_sum_fill(item: dict) -> tuple[int, int]:
    """fx-fraction-sum: 1/2 + 1/3 = a/b in lowest terms → (a, b)."""
    r = sp.Rational(1, 2) + sp.Rational(1, 3)
    return (int(r.p), int(r.q))


def fraction_product(item: dict) -> sp.Rational:
    """fx-frac-product: 2/3 × 9/4."""
    return sp.Rational(2, 3) * sp.Rational(9, 4)


def half_squared(item: dict) -> sp.Rational:
    """fx-half-squared: 0.5², computed exactly as (1/2)²."""
    return sp.Rational(1, 2) ** 2


def divisor_count(item: dict) -> int:
    """fx-divisors: the number of positive divisors of 12."""
    return len(sp.divisors(12))


def odd_sum_identity(item: dict) -> bool:
    """fx-odd-sum: (2m+1) + (2n+1) = 2(m+n+1), and m+n+1 is an integer when m, n are."""
    m, n = sp.symbols("m n", integer=True)
    total = (2 * m + 1) + (2 * n + 1)
    identity = sp.expand(total - 2 * (m + n + 1)) == 0
    half_is_integer = sp.simplify(total / 2).is_integer is True
    return identity and half_is_integer


_ATOM = re.compile(r"([A-Z][a-z]?)(\d*)")


def _atoms(formula: str) -> sp.Integer:
    """Atoms in one molecule of a simple formula without brackets, e.g. 'CO2' → 3."""
    if not re.fullmatch(r"(?:[A-Z][a-z]?\d*)+", formula):
        raise ValueError(f"unsupported formula {formula!r}")
    return sum((sp.Integer(int(k) if k else 1) for _, k in _ATOM.findall(formula)), sp.Integer(0))


def three_atom_molecules(item: dict) -> list[bool]:
    """fx-three-atoms: which of H2O, CO2, O3, NH3 have exactly 3 atoms per molecule."""
    return [_atoms(f) == 3 for f in ("H2O", "CO2", "O3", "NH3")]
