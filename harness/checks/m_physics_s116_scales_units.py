"""Checks for src/data/items/physics/s116-scales-units.yaml (116 sprint: scales of nature and units,
PEa-Ⅴc-1~3).

Each function recomputes its item's answer from the physics; none reads item["answer"].
Numeric items use SymPy with exact Rationals and powers of ten; unit conversions go through
sympy.physics.units, so the conversion factors are SymPy's, not typed here. Rule-based items encode
the rule (the seven SI base quantities, base-quantity dimensions, the method steps) as data below,
with a source comment per fact.
"""

from __future__ import annotations

import sympy as sp
from sympy.physics import units as u

TEN = sp.Integer(10)

# Sizes the 課綱 gives (nat.json nat:PEa-Vc-3 keyConcepts: "Atom is about 10^-10 m; nucleus is about 10^-15 m").
ATOM_M = TEN**-10
NUCLEUS_M = TEN**-15

# The seven SI base units (BIPM SI Brochure; standard high-school physics): m, kg, s, A, K, mol, cd.
# The base unit of mass is the kilogram, not the gram; km is a multiple of the base unit m, not a base unit.
SI_BASE_UNITS = {"m", "kg", "s", "A", "K", "mol", "cd"}

# Dimensions as exponents of the base quantities (L length, M mass, T time); standard definitions:
# density = mass / volume, speed = distance / time, area = length × length.
DIMENSIONS = {
    "density": {"M": 1, "L": -3},
    "speed": {"L": 1, "T": -1},
    "mass": {"M": 1},
    "time": {"T": 1},
    "area": {"L": 2},
}

# The scientific-method steps in order, as the Ea 說明 bullet lists them
# (nat.json nat:PEa-Vc-1 keyConcepts: "identify a problem, form a hypothesis, analyse and verify by
# experiment, build theory, predict").
METHOD_ORDER = ["problem", "hypothesis", "experiment", "theory", "predict"]

# How the kilogram is defined today: by fixing the Planck constant (SI revision in force since 2019),
# no longer by a physical prototype. Source: research/verified-2026-11-15.json physics key_facts
# (111學測 Q58–60: "the new SI mass definition via Planck constant").
KILOGRAM_DEFINED_BY_PROTOTYPE_TODAY = False


def _is_base_quantity(dims: dict) -> bool:
    """A base quantity is exactly one base dimension to the first power; anything else is derived."""
    nonzero = {k: v for k, v in dims.items() if v != 0}
    return len(nonzero) == 1 and list(nonzero.values())[0] == 1


def _to(q, unit) -> sp.Expr:
    """The number in front of `unit` after converting q (exact)."""
    return sp.nsimplify(sp.simplify(u.convert_to(q, unit) / unit))


def su_turn_ratio(item: dict) -> list[bool]:
    """q-turn: the atom (10^-10 m) is how many times the nucleus (10^-15 m)?
    Options: 10^5, 10^-5, 10^25, 5, 10^150."""
    ratio = ATOM_M / NUCLEUS_M
    return [ratio == o for o in (TEN**5, TEN**-5, TEN**25, sp.Integer(5), TEN**150)]


def su_base_unit(item: dict) -> list[bool]:
    """q1: which is an SI base unit? Options: N, J, kg, g, km."""
    return [o in SI_BASE_UNITS for o in ("N", "J", "kg", "g", "km")]


def su_derived_quantities(item: dict) -> list[bool]:
    """q2: which quantities are derived (calculated from base quantities)?
    Options: density, speed, mass, time, area."""
    return [not _is_base_quantity(DIMENSIONS[k]) for k in ("density", "speed", "mass", "time", "area")]


def su_density_fill(item: dict) -> sp.Integer:
    """q3: a 4 cm × 5 cm × 2 cm block of mass 316 g; its density in kg/m³."""
    volume = 4 * u.centimeter * 5 * u.centimeter * 2 * u.centimeter
    mass = 316 * u.gram
    value = _to(mass / volume, u.kilogram / u.meter**3)
    assert value.is_integer
    return sp.Integer(value)


def su_atoms_per_cm(item: dict) -> sp.Integer:
    """q4: how many atoms (diameter 10^-10 m) side by side span 1 cm? The answer is 10^n; return n."""
    count = _to(1 * u.centimeter, u.meter) / ATOM_M
    n = sp.log(count, 10)
    assert n.is_integer
    return sp.Integer(n)


def su_speed_conversion(item: dict) -> list[bool]:
    """q5: 90 km/h in m/s. Options: 25, 90, 9, 250, 324."""
    v = _to(90 * u.kilometer / u.hour, u.meter / u.second)
    return [v == o for o in (25, 90, 9, 250, 324)]


def su_scale_statements(item: dict) -> list[bool]:
    """q6: (1) 1 nm = 10^-9 m; (2) the atom's diameter is about 10^5 times the nucleus's;
    (3) the atom's volume is about 10^5 times the nucleus's; (4) the kilogram is defined today by a
    metal prototype kept near Paris; (5) 1 μm = 10^-3 m."""
    s1 = _to(1 * u.nanometer, u.meter) == TEN**-9
    s2 = ATOM_M / NUCLEUS_M == TEN**5
    s3 = (ATOM_M / NUCLEUS_M) ** 3 == TEN**5  # volume scales as the cube of the length
    s4 = KILOGRAM_DEFINED_BY_PROTOTYPE_TODAY
    s5 = _to(1 * u.micrometer, u.meter) == TEN**-3
    return [s1, s2, s3, s4, s5]


def su_method_order(item: dict) -> list[bool]:
    """q7: the order of the scientific-method steps. Each option is a sequence of the five steps."""
    options = [
        ["hypothesis", "problem", "experiment", "theory", "predict"],
        ["problem", "experiment", "hypothesis", "predict", "theory"],
        ["problem", "hypothesis", "experiment", "theory", "predict"],
        ["experiment", "theory", "problem", "hypothesis", "predict"],
        ["problem", "hypothesis", "theory", "experiment", "predict"],
    ]
    return [o == METHOD_ORDER for o in options]


def su_nearest_power(item: dict) -> list[bool]:
    """q8: Earth–Sun distance 1.5×10^11 m over Earth's diameter 1.3×10^7 m: the closest power of ten.
    Options: 10^2, 10^3, 10^4, 10^5, 10^18."""
    ratio = sp.Rational(15, 10) * TEN**11 / (sp.Rational(13, 10) * TEN**7)
    # closest on the log scale: the integer nearest to log10(ratio); make sure it is not a tie
    lg = sp.log(ratio, 10)
    n = sp.floor(lg + sp.Rational(1, 2))
    assert abs(sp.N(lg - n, 30)) < sp.Rational(1, 2) - sp.Rational(1, 100)
    return [n == k for k in (2, 3, 4, 5, 18)]
