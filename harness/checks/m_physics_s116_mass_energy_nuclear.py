"""Checks for src/data/items/physics/s116-mass-energy-nuclear.yaml
(116 sprint: mass–energy equivalence and nuclear energy, PBa-Ⅴc-3/4, PNc-Ⅴc-1/2).

Each function recomputes its item's answer from the physics; none reads item["answer"].
Numbers are exact SymPy Rationals and powers of ten; the stems state the approximation c = 3×10^8 m/s.
Qualitative items encode the physical rule (mass decrease, nucleon conservation, inverse-square spreading,
which absorber stops which radiation, the energy chain of a power plant) as code.
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational
C = 3 * sp.Integer(10) ** 8  # speed of light in m/s, as stated in every stem


def _sci(m, e) -> sp.Expr:
    """m × 10^e as an exact number."""
    return sp.nsimplify(m) * sp.Integer(10) ** e


def _energy(dm) -> sp.Expr:
    """E = Δm c² (J) for a mass decrease Δm (kg)."""
    return dm * C**2


def _mantissa_exponent(v) -> tuple[sp.Expr, int]:
    """Write v > 0 as m × 10^e with 1 ≤ m < 10, exactly."""
    e = int(sp.floor(sp.log(v, 10)))
    m = sp.nsimplify(v / sp.Integer(10) ** e)
    if m >= 10:
        m, e = m / 10, e + 1
    if m < 1:
        m, e = m * 10, e - 1
    assert 1 <= m < 10
    return m, e


# ---------------------------------------------------------------------------
# Reaction data used by q2. Atomic masses in u (AME2020 values, rounded; only the SIGN of the mass change and
# the nucleon counts matter for the item, and they are far from the rounding).
# ---------------------------------------------------------------------------
MASS_U = {
    "n": R("1.008665"),
    "H-2": R("2.014102"),
    "H-3": R("3.016049"),
    "He-4": R("4.002603"),
    "Kr-92": R("91.926156"),
    "Ba-141": R("140.914411"),
    "U-235": R("235.043930"),
}
NUCLEONS = {"n": 1, "H-2": 2, "H-3": 3, "He-4": 4, "Kr-92": 92, "Ba-141": 141, "U-235": 235}
CHARGE = {"n": 0, "H-2": 1, "H-3": 1, "He-4": 2, "Kr-92": 36, "Ba-141": 56, "U-235": 92}

FISSION = (["U-235", "n"], ["Ba-141", "Kr-92", "n", "n", "n"])  # a typical channel of U-235 fission
FUSION = (["H-2", "H-3"], ["He-4", "n"])  # deuterium–tritium fusion


def _mass(side) -> sp.Expr:
    return sum(MASS_U[p] for p in side)


def _count(side, table) -> int:
    return sum(table[p] for p in side)


# Facts the items rely on, with their sources.
# nat.json nat:PBa-Ⅴc-4 keyConcepts: "may mention that solar energy comes from fusion".
SUN_ENERGY_SOURCE = "fusion"
# nat.json nat:PNc-Ⅴc-1 keyConcepts: "Brief account of fission, nuclear power" (nuclear power plants run on
# fission; fusion power is not yet in commercial use).
POWER_PLANT_REACTION = "fission"


def mn_turn_full_conversion(item: dict) -> list[bool]:
    """q-turn: energy if 1 g of mass were converted entirely, c = 3×10^8 m/s.
    Options: 3×10^5, 9×10^10, 9×10^13, 3×10^11, 9×10^16 J."""
    e = _energy(R(1, 1000))  # 1 g = 10^-3 kg
    opts = [_sci(3, 5), _sci(9, 10), _sci(9, 13), _sci(3, 11), _sci(9, 16)]
    return [e == o for o in opts]


def mn_fusion_mass_decrease(item: dict) -> list[bool]:
    """q1: a fusion releases 2.7×10^-12 J; the mass decrease Δm = E/c².
    Options: 9×10^-21, 3×10^-29, 2.4×10^5, 3×10^-20, 8.1×10^-4 kg."""
    e = _sci(R(27, 10), -12)
    dm = e / C**2
    opts = [_sci(9, -21), _sci(3, -29), _sci(R(24, 10), 5), _sci(3, -20), _sci(R(81, 10), -4)]
    return [dm == o for o in opts]


def mn_fission_energy_digits(item: dict) -> tuple[int, int]:
    """q3: one fission loses Δm = 3.0×10^-28 kg; E = ①.② × 10^-11 J."""
    e = _energy(_sci(3, -28))
    m = e / sp.Integer(10) ** -11
    assert (m * 10).is_integer and 1 <= m < 10, m
    tenths = int(m * 10)
    return (tenths // 10, tenths % 10)


def mn_fissions_per_second(item: dict) -> int:
    """q4: a reactor's thermal power is 3.0×10^9 W and each fission gives 3.0×10^-11 J;
    fissions per second = 10^n, n = ①②."""
    n_per_s = _sci(3, 9) / _sci(3, -11)
    m, e = _mantissa_exponent(n_per_s)
    assert m == 1, "the count must be an exact power of ten"
    return e


def mn_fission_fusion_statements(item: dict) -> list[bool]:
    """q2: (1) both fission and fusion end with less total mass, and that mass becomes energy;
    (2) the Sun's energy comes mainly from fission; (3) in fission the number of protons plus neutrons
    drops, and the energy comes from the missing particles; (4) fusion needs a very high temperature because
    the positive nuclei repel and must get very close; (5) today's nuclear power plants use fission."""
    s1 = all(_mass(before) > _mass(after) for before, after in (FISSION, FUSION))
    s2 = SUN_ENERGY_SOURCE == "fission"
    before, after = FISSION
    s3 = _count(after, NUCLEONS) < _count(before, NUCLEONS)  # nucleon number is conserved, so this is False
    # Both fusing nuclei carry positive charge, so they repel (like charges); they must be pushed very
    # close, within the short range of the strong force, which takes a very high temperature.
    a, b = FUSION[0]
    s4 = CHARGE[a] > 0 and CHARGE[b] > 0
    s5 = POWER_PLANT_REACTION == "fission"
    return [s1, s2, s3, s4, s5]


def mn_star_mass_loss(item: dict) -> tuple[int, int]:
    """q5: a star radiates 3.6×10^26 J each second; mass lost per second = ① × 10^② kg."""
    dm = _sci(R(36, 10), 26) / C**2
    m, e = _mantissa_exponent(dm)
    assert m.is_integer, m
    return (int(m), e)


def _dose_ratio(r1, r2) -> sp.Expr:
    """Dose rate at r2 relative to r1 for a point source: the same radiation spreads over a sphere of
    area 4πr², so the rate per area goes as 1/(4πr²)."""
    area = lambda r: 4 * sp.pi * r**2  # noqa: E731
    return sp.simplify(area(r1) / area(r2))


def mn_inverse_square_dose(item: dict) -> list[bool]:
    """q6: dose rate D at 1 m from a point source; at 3 m? Options: D, D/3, D/9, D/27, 3D."""
    k = _dose_ratio(1, 3)
    return [k == o for o in (1, R(1, 3), R(1, 9), R(1, 27), 3)]


# Which absorber stops which radiation (standard physics: α by a sheet of paper, β by a few mm of aluminium,
# γ only weakened by lead or thick concrete, never fully stopped by paper).
STOPPED_BY = {"alpha": {"paper", "aluminium", "lead"}, "beta": {"aluminium", "lead"}, "gamma": set()}
# Natural background sources (cosmic rays, radon in air, radioactive potassium in food): non-empty.
NATURAL_SOURCES = ["cosmic rays", "radon", "potassium-40 in food"]


def _dose(rate_at_1m, r, t, shield=None, kind="gamma") -> sp.Expr:
    """Dose = rate × time, with the rate falling as 1/r² and zero behind an absorber that stops the kind."""
    if shield is not None and shield in STOPPED_BY[kind]:
        return sp.Integer(0)
    return rate_at_1m * _dose_ratio(1, r) * t


def mn_radiation_safety(item: dict) -> list[bool]:
    """q7: (1) farther from the source → less dose; (2) less time near it → less dose; (3) a sheet of paper
    stops α; (4) a sheet of paper stops γ completely; (5) all everyday radiation is man-made."""
    s1 = _dose(1, 4, 1) < _dose(1, 2, 1)
    s2 = _dose(1, 2, 1) < _dose(1, 2, 3)
    s3 = _dose(1, 1, 1, shield="paper", kind="alpha") == 0
    s4 = _dose(1, 1, 1, shield="paper", kind="gamma") == 0
    s5 = len(NATURAL_SOURCES) == 0
    return [s1, s2, s3, s4, s5]


# Stages of a nuclear power plant: (stage, energy in, energy out).
PLANT = [
    ("reactor: fission heats water", "nuclear", "thermal"),
    ("steam turns the turbine", "thermal", "mechanical"),
    ("generator: electromagnetic induction", "mechanical", "electrical"),
]


def mn_plant_energy_chain(item: dict) -> list[bool]:
    """q8: the order of energy forms in a nuclear power plant.
    Options: nuclear→electrical→thermal→mechanical; nuclear→thermal→mechanical→electrical;
    thermal→nuclear→electrical→mechanical; chemical→thermal→mechanical→electrical;
    nuclear→mechanical→thermal→electrical."""
    for (_, _, out), (_, nxt, _) in zip(PLANT, PLANT[1:]):
        assert out == nxt  # each stage hands its output to the next
    chain = [PLANT[0][1]] + [s[2] for s in PLANT]
    opts = [
        ["nuclear", "electrical", "thermal", "mechanical"],
        ["nuclear", "thermal", "mechanical", "electrical"],
        ["thermal", "nuclear", "electrical", "mechanical"],
        ["chemical", "thermal", "mechanical", "electrical"],
        ["nuclear", "mechanical", "thermal", "electrical"],
    ]
    return [chain == o for o in opts]
