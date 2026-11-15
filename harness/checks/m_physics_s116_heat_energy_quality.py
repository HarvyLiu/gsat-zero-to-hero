"""Checks for src/data/items/physics/s116-heat-energy-quality.yaml
(116 sprint: temperature, heat and the quality of energy; nat:PBb-Vc-1~4, nat:PNc-Vc-3~4).

Each function recomputes its item's answer from the physics; none reads item["answer"].
Numeric items use exact SymPy Rationals. Qualitative items encode the physical rule as code:
  - the Kelvin scale: T(K) = t(°C) + 273.15 (the items state the rounded rule T = t + 273 where they use it);
  - average molecular kinetic energy grows with absolute temperature (for an ideal gas it is (3/2)kT,
    which we use only as a model that is increasing in T);
  - energy bookkeeping: thermal energy = kinetic part + interaction part, and the change in thermal
    energy equals heat in plus work done on the body (energy conservation);
  - heat flows spontaneously from the higher temperature to the lower one, whatever the amounts of
    thermal energy;
  - work can turn wholly into thermal energy; a cyclic heat engine cannot turn all absorbed heat into work.
"""

from __future__ import annotations

import sympy as sp

KELVIN_OFFSET = sp.Rational(27315, 100)  # 0 °C = 273.15 K (definition of the Celsius scale)
k_B = sp.Symbol("k_B", positive=True)


def _to_kelvin(t_c, offset=KELVIN_OFFSET):
    return sp.nsimplify(t_c) + offset


def _avg_ke(T):
    """Average translational kinetic energy of an ideal-gas molecule; only its monotonicity is relied on."""
    return sp.Rational(3, 2) * k_B * T


def _is_increasing_in_T() -> bool:
    T = sp.Symbol("T", positive=True)
    return bool(sp.diff(_avg_ke(T), T).is_positive)


# ---------- the dialogue turn ----------

def he_turn_kelvin(item: dict) -> list[bool]:
    """q-turn: 27 °C in kelvin with T = t + 273. Options: 27, 246, 273, 300, 327 K."""
    T = _to_kelvin(27, offset=273)
    return [T == o for o in (27, 246, 273, 300, 327)]


# ---------- quiz ----------

def he_kelvin_ratio(item: dict) -> list[bool]:
    """q1: a gas goes from 7 °C to 287 °C (T = t + 273); the factor on its absolute temperature.
    Options: 41, 40, 4, 2, √2."""
    ratio = _to_kelvin(287, offset=273) / _to_kelvin(7, offset=273)
    return [sp.simplify(ratio - o) == 0 for o in (41, 40, 4, 2, sp.sqrt(2))]


def he_temperature_statements(item: dict) -> list[bool]:
    """q2: (1) 0 K is about −273 °C and is the lowest temperature; (2) a change of 10 °C is a change of 10 K;
    (3) all molecules in one bottle of gas have the same speed; (4) higher absolute temperature means a
    greater average molecular kinetic energy; (5) a gas at 30 °C has twice the absolute temperature it has
    at 15 °C."""
    zero_k_in_c = -KELVIN_OFFSET
    s1 = sp.Abs(zero_k_in_c - (-273)) < 1  # "about −273 °C"; 0 K is the bottom of the Kelvin scale (T ≥ 0)
    s2 = (_to_kelvin(30) - _to_kelvin(20)) == 10  # the two scales have the same degree size
    # (3) Molecules collide constantly and exchange energy, so their speeds spread over a range; the
    # temperature fixes only the average. Encoded as a fact of kinetic theory: a single common speed is false.
    speeds_spread = True
    s3 = not speeds_spread
    s4 = _is_increasing_in_T()
    s5 = _to_kelvin(30) / _to_kelvin(15) == 2
    return [bool(s1), bool(s2), s3, s4, bool(s5)]


def he_melting_ice(item: dict) -> list[bool]:
    """q3: ice at 0 °C, 1 atm, partly melted, keeps absorbing heat (no work done on it).
    Bookkeeping: ΔU = Q + W with Q > 0, W = 0; ΔU = ΔK + ΔI (kinetic + interaction parts);
    the temperature stays at the melting point, so ΔT = 0 and ΔK = 0 (K depends on T).
    Options: (A) T up, KE up; (B) T same so thermal energy same; (C) T same, thermal energy up, mostly
    interaction energy; (D) the heat disappears; (E) KE down, interaction energy up."""
    Q, W, dT = sp.Integer(1), sp.Integer(0), sp.Integer(0)  # any positive Q; the melting point is fixed
    dU = Q + W
    T0 = KELVIN_OFFSET
    dK = sp.simplify(_avg_ke(T0 + dT) - _avg_ke(T0))
    dI = dU - dK
    return [
        bool(dT > 0 and dK > 0),
        bool(dT == 0 and dU == 0),
        bool(dT == 0 and dU > 0 and dI > 0 and dK == 0),
        bool(dU == 0),  # the heat would have vanished only if U did not change
        bool(dK < 0 and dI > 0),
    ]


def _heat_direction(T_a, T_b) -> int:
    """+1: heat flows a → b; −1: b → a; 0: no net flow. Depends only on the temperatures."""
    return int(sp.sign(T_a - T_b))


def he_heat_statements(item: dict) -> list[bool]:
    """q4: (1) heat is energy transferred because of a temperature difference; (2) a hotter body 'contains'
    more heat; (3) with no outside work, heat flows by itself from the hotter body to the colder one;
    (4) bodies at the same temperature have no net heat flow; (5) heat always flows from the body with
    more thermal energy to the one with less."""
    # Heat is a transfer (a process quantity), not something stored: a body has thermal energy, not heat.
    heat_is_transfer = True
    s1 = heat_is_transfer
    s2 = not heat_is_transfer
    s3 = _heat_direction(350, 300) == 1
    s4 = _heat_direction(300, 300) == 0
    # (5) counterexample: a bathtub (large thermal energy, 313 K) beside a cup of tea (small, 363 K).
    bath = {"T": 313, "U": 10**8}
    tea = {"T": 363, "U": 10**5}
    more_U_first = _heat_direction(bath["T"], tea["T"]) == (1 if bath["U"] > tea["U"] else -1)
    s5 = more_U_first
    return [s1, s2, s3, s4, s5]


def he_mixing_water(item: dict) -> sp.Integer:
    """q5: 150 g of water at 90 °C mixed with 450 g at 10 °C, no heat lost; the final temperature (°C).
    Heat lost by the hot water = heat gained by the cold water."""
    T = sp.Symbol("T")
    c = sp.Symbol("c", positive=True)
    (sol,) = sp.solve(sp.Eq(150 * c * (90 - T), 450 * c * (T - 10)), T)
    return sp.Integer(sol)


def he_sliding_block(item: dict) -> list[bool]:
    """q6: a block slides on a rough floor and stops.
    Total energy is conserved; the block's kinetic energy (ordered: all atoms share one velocity) becomes
    thermal energy of block and floor (disordered); the reverse never happens by itself; friction warms,
    never cools, the surfaces. Options: (A) mechanical energy vanishes, total decreases; (B) KE → thermal
    energy of block and floor, total conserved, ordered → disordered; (C) friction creates energy;
    (D) the warm block and floor turn thermal energy back into motion by themselves; (E) the block's
    temperature must drop."""
    K0 = sp.Integer(1)  # any initial kinetic energy
    K1 = sp.Integer(0)
    thermal_gain = K0 - K1  # energy conservation: what the block loses appears as thermal energy
    total_before, total_after = K0, K1 + thermal_gain
    spontaneous_reverse = False  # disordered → ordered does not happen by itself
    block_dT_sign = sp.sign(thermal_gain)  # friction heats the surfaces
    return [
        bool(total_after < total_before),
        bool(total_after == total_before and thermal_gain == K0),
        bool(total_after > total_before),
        spontaneous_reverse,
        bool(block_dT_sign < 0),
    ]


def he_energy_quality(item: dict) -> list[bool]:
    """q7: (1) in conversions total energy is conserved but the ability to do work usually drops;
    (2) two systems with the same energy can always do the same work; (3) a heat engine cannot turn all the
    heat it absorbs into work; (4) work can turn wholly into heat, e.g. by friction; (5) since energy is
    conserved, saving energy is pointless.
    Counterexample for (2): equal energy as a moving cart (ordered) vs as thermal energy of water at the
    surrounding temperature (no temperature difference, so no engine can run on it)."""
    E = sp.Integer(1000)
    work_from_cart = E  # ideally all of it can lift a load
    T_env = sp.Integer(300)
    max_fraction_from_lake = 1 - T_env / T_env  # no colder side: an engine extracts nothing
    work_from_lake = E * max_fraction_from_lake
    s2 = work_from_cart == work_from_lake
    # (3): the best any engine between T_h and T_c can do is 1 − T_c/T_h, which is < 1 whenever T_c > 0.
    Th, Tc = sp.symbols("T_h T_c", positive=True)
    s3 = bool(sp.simplify(1 - Tc / Th < 1))
    s4 = True  # friction dissipates the whole of the work done against it as thermal energy
    s1 = True  # conservation (law) + degradation (PNc-Vc-4: 能量轉換通常使作功能力降低)
    # (5): what is used up is the ability to do work, not the amount of energy, so saving still matters.
    s5 = not s1
    return [s1, bool(s2), s3, s4, s5]


def he_bounce_dissipated(item: dict) -> sp.Integer:
    """q8: a ball starts with 50 J of mechanical energy and keeps 60 % of it at each bounce.
    After 2 bounces, the energy that has become thermal energy and sound (J)."""
    E0 = sp.Integer(50)
    keep = sp.Rational(60, 100)
    E2 = E0 * keep**2
    return sp.Integer(E0 - E2)
