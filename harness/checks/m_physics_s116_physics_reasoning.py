"""Checks for src/data/items/physics/s116-physics-reasoning.yaml (116 sprint, physics exam skills).

The chapter has no curriculum codes (physics.json: codes []): it teaches dimension checks (formally
elective PEa-Va-1, used in the 112 physics group Q37-40), graph reading and written reasoning.
Each function recomputes its item's answer from the physics; none reads item["answer"].

Dimensions are SymPy monomials in M (mass), L (length), T (time), so a dimension check is an exact
equality of expressions. Units come from the SI definitions: 1 N = 1 kg·m/s², 1 J = 1 N·m,
1 W = 1 J/s, 1 Hz = 1/s; Planck's constant h is in J·s because E = hf.
"""

from __future__ import annotations

import sympy as sp

M, L, T = sp.symbols("M L T", positive=True)

# Dimensions of the quantities the items use.
MASS = M
LENGTH = L
TIME = T
SPEED = L / T
ACCEL = L / T**2
FORCE = MASS * ACCEL  # 1 N = 1 kg·m/s²
ENERGY = sp.simplify(FORCE * LENGTH)  # 1 J = 1 N·m
POWER = sp.simplify(ENERGY / TIME)  # 1 W = 1 J/s
FREQ = 1 / T  # 1 Hz = 1/s
PLANCK = sp.simplify(ENERGY / FREQ)  # E = hf, so h is in J·s
MOMENTUM = MASS * SPEED


def _same(a, b) -> bool:
    """Two dimensions are equal when their ratio simplifies to 1."""
    return sp.simplify(a / b) == 1


def rs_turn_energy(item: dict) -> list[bool]:
    """q-turn: m (kg), v (m/s), g (m/s²), h (m). Which could be an energy, ignoring number factors?
    Options: mv, mv², mgh², mv/h, mg."""
    m, v, g, h = MASS, SPEED, ACCEL, LENGTH
    opts = [m * v, m * v**2, m * g * h**2, m * v / h, m * g]
    return [_same(o, ENERGY) for o in opts]


def rs_time_from_speed_accel(item: dict) -> list[bool]:
    """q1: v (m/s) and a (m/s²). Which has the dimension of time?
    Options: a/v, v·a, v/a, v²/a, sqrt(v/a)."""
    v, a = SPEED, ACCEL
    opts = [a / v, v * a, v / a, v**2 / a, sp.sqrt(v / a)]
    return [_same(o, TIME) for o in opts]


def rs_consistent_equations(item: dict) -> list[bool]:
    """q2: which equations have the same dimension on both sides? h in J·s, c and v speeds,
    f frequency, λ wavelength, m mass, E energy.
    (1) E = hf; (2) v = fλ; (3) E = mc; (4) λ = hc/E; (5) f = Eh."""
    E, h, f, lam, c, v, m = ENERGY, PLANCK, FREQ, LENGTH, SPEED, SPEED, MASS
    pairs = [(E, h * f), (v, f * lam), (E, m * c), (lam, h * c / E), (f, E * h)]
    return [_same(lhs, rhs) for lhs, rhs in pairs]


def rs_inverse_square_from_slope(item: dict) -> sp.Integer:
    """q3: point source; I against 1/r² is a straight line through the origin with slope 180 W.
    So I = 180/r²; find I (W/m²) at r = 6 m. The line through the origin means I·r² is constant."""
    slope = sp.Integer(180)
    r = sp.Integer(6)
    intensity = slope * (1 / r**2)
    # cross-check with the inverse-square ratio from a second point on the same line (r = 2 m)
    i2 = slope / sp.Integer(2) ** 2
    assert intensity == i2 * (sp.Integer(2) / r) ** 2
    return sp.Integer(intensity)


def rs_slope_energy_time(item: dict) -> list[bool]:
    """q4: E (J) on the vertical axis, t (s) on the horizontal; unit and meaning of the slope.
    Options: (unit, meaning) pairs; true when the unit equals J/s and the meaning is the rate of
    energy use (power), whose dimension is energy/time."""
    slope_dim = ENERGY / TIME
    meanings = {"power": POWER, "energy": ENERGY, "force": FORCE, "momentum": MOMENTUM}
    units = {"W": POWER, "J·s": ENERGY * TIME, "N": FORCE, "J": ENERGY}
    opts = [("J·s", "energy"), ("W", "power"), ("N", "force"), ("W", "energy"), ("J", "power")]
    return [_same(units[u], slope_dim) and _same(meanings[k], slope_dim) for u, k in opts]


def rs_complete_reasoning(item: dict) -> list[bool]:
    """q5: a magnet's N pole moves away from a coil. Which written answer is a complete reasoning
    chain for the induced-current direction (seen from the magnet side)?
    The rule (CEEC 115 Q53(a) scoring note, research physics verification.confirmed_facts[10]): a bare
    conclusion, or a law named without being applied, scores 0. Complete = states how the flux
    changes, applies 'the induced field opposes that change', and its direction follows from them.
    Each option is described by these features (read off the option text in the bank)."""
    # Field lines leave a north pole, so at the coil B points away from the magnet (-x); it weakens.
    correct = _induced_view(flux_sign=-1, flux_increasing=False)[0]
    # (states_flux_change, applies_opposing_field, stated_direction)
    options = [
        (False, False, "cw"),  # (1) bare direction only
        (False, False, "cw"),  # (2) "by Lenz's law" + direction: law named, not applied
        (True, True, "cw"),  # (3) flux away from the magnet weakens -> induced field keeps it -> cw
        (True, False, "cw"),  # (4) flux weakens, then jumps to the direction
        (True, True, "ccw"),  # (5) full chain, but the conclusion contradicts its own steps
    ]
    return [a and b and d == correct for a, b, d in options]


def _induced_view(flux_sign: int, flux_increasing: bool) -> tuple[str, str]:
    """Lenz's rule as code. x-axis points from the coil toward the magnet; the viewer sits on the
    magnet side. flux_sign is the sign of B_x at the coil. The induced field opposes the change:
    B_ind,x = -sign(dPhi/dt). Seen from +x, a field toward the viewer (+x) needs a counterclockwise
    current (right-hand rule), and that face of the coil acts as a north pole."""
    dphi = flux_sign if flux_increasing else -flux_sign
    b_ind = -dphi
    direction = "ccw" if b_ind > 0 else "cw"
    face = "N" if b_ind > 0 else "S"
    return direction, face


def rs_lenz_s_pole_leaving(item: dict) -> list[bool]:
    """q6: a magnet's S pole is pulled away from a coil. Field lines enter a south pole, so at the
    coil B points toward the magnet (+x) and that flux decreases.
    Options: (ccw, N), (cw, N), (cw, S), (ccw, S), no current."""
    got = _induced_view(flux_sign=+1, flux_increasing=False)
    opts = [("ccw", "N"), ("cw", "N"), ("cw", "S"), ("ccw", "S"), None]
    # consistency: a N face toward a receding S pole attracts it, which opposes the motion
    assert got[1] == "N"
    return [o == got for o in opts]


def rs_watt_exponents(item: dict) -> tuple[int, int]:
    """q7: W = kg·m^a·s^b. From 1 W = 1 J/s, 1 J = 1 N·m and 1 N = 1 kg·m/s²; read the exponents off."""
    e = sp.simplify(POWER / M)
    a = sp.degree(e.subs(T, 1), L)
    b = -sp.degree((1 / e).subs(L, 1), T)
    assert sp.simplify(M * L**a * T**b / POWER) == 1
    return (int(a), int(b))


def _pulse(k):
    """Induced current for a magnet passing at a speed proportional to k: the flux through the coil
    is Phi(t) = exp(-(k t)²) (the centre passes at t = 0), and I is proportional to -dPhi/dt
    (Faraday, with Lenz's sign). Returns (peak |I|, time of the leaving peak)."""
    t = sp.symbols("t", real=True)
    i = -sp.diff(sp.exp(-((k * t) ** 2)), t)
    crit = [c for c in sp.solve(sp.diff(i, t), t) if c > 0]
    (t_peak,) = crit
    # the leaving pulse mirrors the entering one: I(-t) = -I(t)
    assert sp.simplify(i.subs(t, -t) + i) == 0
    return sp.simplify(sp.Abs(i.subs(t, t_peak))), t_peak


def rs_faster_magnet(item: dict) -> list[bool]:
    """q8: the same magnet passes through the same coil at constant speed, then again at twice
    that speed. Options: (1) larger peaks, shorter pulses; (2) same peaks, shorter pulses;
    (3) larger peaks, same duration; (4) smaller peaks, longer pulses; (5) no change."""
    peak1, t1 = _pulse(sp.Integer(1))
    peak2, t2 = _pulse(sp.Integer(2))
    larger = bool(peak2 > peak1)
    same = sp.simplify(peak2 - peak1) == 0
    shorter = bool(t2 < t1)
    same_t = sp.simplify(t2 - t1) == 0
    return [
        larger and shorter,
        same and shorter,
        larger and same_t,
        bool(peak2 < peak1) and bool(t2 > t1),
        same and same_t,
    ]
