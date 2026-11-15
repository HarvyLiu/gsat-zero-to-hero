"""Checks for src/data/items/physics/s116-energy-conservation.yaml (116 sprint: PBa-Vc-1, PBa-Vc-2).

Each function recomputes its item's answer from the physics (SymPy for the numbers, explicit rules or a
facts table for the qualitative items); none reads item["answer"].

Physics encoded here (standard high-school physics, kept within the 必修 depth of the chapter):
- near the ground, gravitational potential energy is proportional to height (U = m g h; the formula is
  used only inside the check, the items reason with "proportional to height");
- without friction or air resistance, mechanical energy K + U is constant;
- in Joule's experiment, the work of the falling weights is proportional to the total drop distance and,
  for the same water, the temperature rise is proportional to the heat received;
- total energy is conserved: energy in = energy stored + energy out;
- energy radiated evenly from a small source spreads over a sphere of area 4 pi r^2.
"""

from __future__ import annotations

import sympy as sp

m, g = sp.symbols("m g", positive=True)


def _U(h):
    """Gravitational potential energy near the ground, zero at ground level."""
    return m * g * h


def _mech_height_where(H, condition):
    """Heights h in [0, H] of a ball released from rest at H (no air resistance) where condition(K, U)."""
    h = sp.symbols("h", real=True)
    K = _U(H) - _U(h)  # mechanical energy conserved: K + U(h) = U(H)
    sols = sp.solve(condition(K, _U(h)), h)
    return [s for s in sols if 0 <= s <= H]


def en_turn_pendulum(item: dict) -> list[bool]:
    """q-turn: a pendulum released from rest at height h0 (no air resistance); how high on the other side?
    Options: higher; same height; lower; depends on the bob's mass; the heavier, the higher."""
    h0 = sp.symbols("h0", positive=True)
    h = sp.symbols("h", positive=True)
    # at the highest point on the other side K = 0, so U(h) = U(h0)
    (hf,) = sp.solve(sp.Eq(_U(h), _U(h0)), h)
    depends_on_mass = m in hf.free_symbols
    return [
        bool(sp.simplify(hf - h0) > 0),
        sp.simplify(hf - h0) == 0,
        bool(sp.simplify(hf - h0) < 0),
        depends_on_mass,
        depends_on_mass,  # "heavier goes higher" would need a mass dependence
    ]


def en_equal_k_u_height(item: dict) -> list[bool]:
    """q1: released from rest at 8 m; at what height is K = U? Options (m): 8, 6, 4, 2, 0."""
    (hk,) = _mech_height_where(sp.Integer(8), lambda K, U: sp.Eq(K, U))
    return [hk == o for o in (8, 6, 4, 2, 0)]


def en_kinetic_fraction(item: dict) -> tuple:
    """q2: released from rest at 12 m; at 3 m, kinetic energy as a fraction of the mechanical energy."""
    H, h = sp.Integer(12), sp.Integer(3)
    frac = sp.simplify((_U(H) - _U(h)) / _U(H))  # m and g cancel
    p, q = sp.fraction(frac)
    return (int(p), int(q))


# Facts table for q3: the main energy conversion in each process.
# Source: nat.json nat:PBa-Vc-1/2 keyConcepts (energy forms and conversions; biological and chemical
# examples) and standard 國中/高中 physics: photosynthesis stores light energy as chemical energy; a lamp
# turns electrical energy into light and heat; hydropower turns the water's gravitational potential energy
# (through kinetic energy) into electrical energy; a battery discharging turns chemical energy into
# electrical energy (charging is the reverse); friction turns mechanical energy into thermal energy.
CONVERSIONS = {
    "photosynthesis": ("light", "chemical"),
    "lamp": ("electrical", "light+thermal"),
    "hydropower": ("gravitational-potential", "electrical"),
    "battery-discharge": ("chemical", "electrical"),
    "friction": ("mechanical", "thermal"),
}


def en_conversions(item: dict) -> list[bool]:
    """q3: which pairings are right?
    (1) photosynthesis light → chemical; (2) lamp electrical → light + thermal;
    (3) hydropower gravitational PE → electrical; (4) battery discharge electrical → chemical;
    (5) friction thermal → mechanical."""
    claims = [
        ("photosynthesis", ("light", "chemical")),
        ("lamp", ("electrical", "light+thermal")),
        ("hydropower", ("gravitational-potential", "electrical")),
        ("battery-discharge", ("electrical", "chemical")),
        ("friction", ("thermal", "mechanical")),
    ]
    return [CONVERSIONS[p] == c for p, c in claims]


# Facts table for q4: what Joule's experiment showed.
# Source: nat.json nat:PBa-Vc-1/2 keyConcepts ("Joule's experiment links mechanical energy and heat";
# "Total energy is conserved") and the research physics unit 14 key concepts; standard history of physics
# (James Prescott Joule, 1840s, falling weights turning a paddle wheel in water).
JOULE = {
    "heat-is-a-substance": False,          # the experiment argued against a heat fluid
    "mass-moves-into-water": False,        # the weights' mass does not enter the water
    "fixed-work-fixed-heat": True,         # a given amount of mechanical energy always gives the same heat
    "faster-stirring-less-heat": False,    # the heat depends on the energy delivered, not less when faster
    "energy-created-from-nothing": False,  # energy is converted, never created
}


def en_joule_conclusion(item: dict) -> list[bool]:
    """q4: statements about Joule's experiment, in option order."""
    order = ["heat-is-a-substance", "mass-moves-into-water", "fixed-work-fixed-heat",
             "faster-stirring-less-heat", "energy-created-from-nothing"]
    return [JOULE[k] for k in order]


def en_joule_ratio(item: dict) -> sp.Integer:
    """q5: same water, weights dropped through the same height 5 times vs 20 times; all mechanical
    energy becomes heat in the water; ratio of the temperature rises."""
    d = sp.symbols("d", positive=True)  # one drop height
    W = lambda n: n * _U(d)  # work of n drops
    c_m = sp.symbols("C", positive=True)  # heat capacity of the water
    dT = lambda n: W(n) / c_m
    return sp.Integer(sp.simplify(dT(20) / dT(5)))


# Facts table for q6: energy seen at different scales, and fields carrying energy.
# Source: nat.json nat:PBa-Vc-1/2 keyConcepts ("how it appears depends on the observation scale";
# "battery chemical energy is really atomic EM and kinetic energy"; "Electric and magnetic fields carry
# energy (phone signals as EM waves)") and research physics unit 15 ("Thermal energy = atomic kinetic
# energy + interaction energy"). Sunlight reaching Earth through near-vacuum is standard physics.
SCALE_FACTS = {
    "battery-chemical-is-atomic-em-and-kinetic": True,
    "thermal-is-random-atomic-motion": True,
    "energy-looks-the-same-at-every-scale": False,
    "phone-signal-fields-carry-energy": True,
    "sunlight-needs-air": False,
}


def en_scale_view(item: dict) -> list[bool]:
    """q6: statements, in option order."""
    order = ["battery-chemical-is-atomic-em-and-kinetic", "thermal-is-random-atomic-motion",
             "energy-looks-the-same-at-every-scale", "phone-signal-fields-carry-energy", "sunlight-needs-air"]
    return [SCALE_FACTS[k] for k in order]


def en_charger_heat(item: dict) -> sp.Integer:
    """q7: the charger takes 20 units of electrical energy, the battery gains 17 units of chemical energy,
    the rest becomes heat. Energy in = stored + out."""
    heat = sp.symbols("Q")
    (q,) = sp.solve(sp.Eq(sp.Integer(20), sp.Integer(17) + heat), heat)
    return sp.Integer(q)


def en_signal_spread(item: dict) -> list[bool]:
    """q8: energy per second per unit area at 3r compared with r (even spreading over spheres).
    Options: 3, 1/3, 1/6, 1/9, 9."""
    r, P = sp.symbols("r P", positive=True)
    per_area = lambda d: P / (4 * sp.pi * d**2)
    ratio = sp.simplify(per_area(3 * r) / per_area(r))
    return [ratio == o for o in (3, sp.Rational(1, 3), sp.Rational(1, 6), sp.Rational(1, 9), 9)]
