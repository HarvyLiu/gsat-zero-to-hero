"""Checks for the physics items (q1-q9, q37-q39) of src/data/items/inquiry/s116-sci-mock.yaml.

Each function recomputes its item's key from the numbers in the stem (exact Rationals) or from an
encoded rule list; none reads item["answer"]. Every rule names the reviewed physics sprint chapter
(src/content/lessons/zh-tw/physics/<slug>.mdx) it comes from. All contexts and numbers are original.
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational


def _r(x) -> sp.Rational:
    """Exact rational from a decimal string, e.g. '0.85'."""
    return sp.nsimplify(x, rational=True) if not isinstance(x, str) else sp.Rational(x)


# ---------- q1: density by difference ----------
# source: physics/s116-scales-units (density = mass / volume, a derived quantity;
# 1 g = 1e-3 kg, 1 cm^3 = (1e-2 m)^3 = 1e-6 m^3).
G_TO_KG = R(1, 1000)
CM3_TO_M3 = R(1, 10**6)


def ph_density_by_difference(item: dict) -> list[bool]:
    """q1: empty cylinder 52 g, cylinder + liquid 84 g, volume 40.0 cm^3. Options (kg/m^3):
    0.80, 800, 1.3e3, 2.1e3, 8.0e5."""
    mass_liquid = (84 - 52) * G_TO_KG
    volume = 40 * CM3_TO_M3
    rho = mass_liquid / volume
    return [rho == o for o in (R(8, 10), 800, 1300, 2100, 800000)]


# ---------- q2: sled at constant velocity ----------
# source: physics/s116-newton-gravity (first law: no net force <=> velocity unchanged; second law:
# the net force changes the velocity, so a finite force cannot stop a moving body instantly;
# third law: action and reaction are equal in size and opposite).
def ph_sled_constant_speed(item: dict) -> list[bool]:
    """q2: pull 30 N horizontal, constant velocity on level snow. Options: pull > friction;
    friction = 30 N and net force 0; net force forwards; rope-on-sled > sled-on-rope;
    stops instantly if the rope snaps."""
    pull = sp.Integer(30)
    m = sp.symbols("m", positive=True)
    a = sp.Integer(0)  # constant velocity: the velocity does not change
    friction = pull - m * a  # horizontal forces: pull forwards, friction backwards
    net = pull - friction
    rope_on_sled = pull
    sled_on_rope = pull  # third law: equal in size
    # after the rope snaps the only horizontal force is friction: a = -friction/m is finite,
    # so over a vanishing time the change in velocity is zero (no instant stop)
    dt = sp.symbols("dt", positive=True)
    dv = sp.limit(-friction / m * dt, dt, 0)
    stops_instantly = dv != 0
    return [
        bool(pull > friction),
        bool(friction == 30 and net == 0),
        bool(net > 0),
        bool(rope_on_sled > sled_on_rope),
        bool(stops_instantly),
    ]


# ---------- q3: Kepler's third law ----------
# source: physics/s116-galileo-kepler (in AU and years, T^2 = a^3).
def ph_kepler_period(item: dict) -> list[bool]:
    """q3: a = 16 AU. Options (years): 16, 32, 64, 128, 256."""
    T = sp.symbols("T", positive=True)
    (period,) = sp.solve(sp.Eq(T**2, sp.Integer(16) ** 3), T)
    return [period == o for o in (16, 32, 64, 128, 256)]


# ---------- q4: forces in the nucleus ----------
# source: physics/s116-matter-interactions:
# - the strong force attracts p-p, p-n and n-n, and at nuclear distances is much stronger than
#   the electric repulsion; its range is about the size of a nucleus, 1e-15 m;
# - the weak interaction changes the kind of particle (free neutron -> proton, electron,
#   antineutrino); its range is about 1e-18 m;
# - Coulomb's force is inverse-square (proportional reasoning only);
# - atoms are about 1e-10 m across.
STRONG_RANGE_M = R(1, 10**15)
ATOM_SIZE_M = R(1, 10**10)
STRONG_PAIRS = {("p", "p"), ("p", "n"), ("n", "n")}
STRONG_BEATS_ELECTRIC_AT_NUCLEAR_DISTANCE = True
CAUSE_OF_FREE_NEUTRON_DECAY = "weak"


def _inverse_square_ratio(distance_factor) -> sp.Rational:
    return R(1, 1) / sp.Integer(distance_factor) ** 2


def ph_nucleus_forces(item: dict) -> list[bool]:
    """q4: protons and neutrons about 1e-15 m apart. Options: strong beats electric at this
    distance; 1e-15 -> 3e-15 m makes the repulsion 1/9; strong force dominant between atoms
    1e-10 m apart; n-n strong attraction; free-neutron decay caused by the strong force."""
    nuclear_distance = R(1, 10**15)
    return [
        STRONG_BEATS_ELECTRIC_AT_NUCLEAR_DISTANCE and nuclear_distance <= STRONG_RANGE_M,
        _inverse_square_ratio(3) == R(1, 9),
        bool(ATOM_SIZE_M <= STRONG_RANGE_M),
        ("n", "n") in STRONG_PAIRS,
        CAUSE_OF_FREE_NEUTRON_DECAY == "strong",
    ]


# ---------- q5: rope wave speed ----------
# source: physics/s116-waves-light (wave speed = frequency x wavelength; the wavelength is the
# distance between neighbouring crests).
def ph_rope_wave_speed(item: dict) -> list[bool]:
    """q5: 3.0 Hz; 5 crests in a row span 2.0 m. Options (m/s): 0.17, 0.50, 1.2, 1.5, 6.0."""
    crests = 5
    span = sp.Integer(2)
    wavelength = span / (crests - 1)
    v = 3 * wavelength
    return [v == o for o in (_r("0.17"), _r("0.50"), _r("1.2"), _r("1.5"), _r("6.0"))]


# ---------- q6: ring and receding magnet ----------
# source: physics/s116-induction (Lenz's law: the induced current opposes the change; magnet
# approaching -> the coil repels it, magnet receding -> the coil attracts it; repelling means the
# facing end has the same pole, attracting means the opposite pole; induction needs only a
# changing magnetic field, no contact).
OPPOSITE = {"N": "S", "S": "N"}


def _lenz(magnet_pole: str, motion: str) -> tuple[str, str]:
    """Return (how the ring moves, pole of the ring's face towards the magnet)."""
    if motion == "approach":
        return ("away", magnet_pole)  # repel: like poles face each other
    if motion == "recede":
        return ("toward", OPPOSITE[magnet_pole])  # attract: unlike poles face each other
    return ("none", None)


def ph_ring_follows_magnet(item: dict) -> list[bool]:
    """q6: N pole pulled quickly away from a light closed ring."""
    got = _lenz("N", "recede")
    options = [("away", "N"), ("away", "S"), ("toward", "S"), ("toward", "N"), ("none", None)]
    return [got == o for o in options]


# ---------- q7: heated water, temperature scales ----------
# source: physics/s116-heat-energy-quality (T = t + 273 in exam calculations; a degree is the same
# size on both scales; ratios must use absolute temperature; the higher the absolute temperature,
# the larger the average kinetic energy of the molecules).
def ph_water_heated_temperatures(item: dict) -> list[bool]:
    """q7: 15 C -> 65 C. Options: T ratio 65/15; rise 50 K; rise 323 K; 288 K -> 338 K;
    average kinetic energy larger after heating."""
    t1, t2 = sp.Integer(15), sp.Integer(65)
    T1, T2 = t1 + 273, t2 + 273
    rise_K = T2 - T1
    return [
        T2 / T1 == R(65, 15),
        rise_K == 50,
        rise_K == 323,
        (T1, T2) == (288, 338),
        bool(T2 > T1),
    ]


# ---------- q8: hydrogen, longest wavelength ----------
# source: physics/s116-photons-spectra (hydrogen levels about -13.6, -3.40, -1.51, -0.85 eV;
# photon energy hf = E_high - E_low; E = hf = hc/lambda, so lambda is inversely proportional to E).
H_LEVELS_EV = {1: _r("-13.6"), 2: _r("-3.40"), 3: _r("-1.51"), 4: _r("-0.85")}


def ph_hydrogen_longest_wavelength(item: dict) -> list[bool]:
    """q8: options are the jumps 3->2, 2->1, 4->3, 4->2, 3->1."""
    jumps = [(3, 2), (2, 1), (4, 3), (4, 2), (3, 1)]
    energies = [H_LEVELS_EV[hi] - H_LEVELS_EV[lo] for hi, lo in jumps]
    assert all(e > 0 for e in energies)
    wavelengths = [1 / e for e in energies]  # proportional to hc/E
    longest = max(wavelengths)
    return [w == longest for w in wavelengths]


# ---------- q9: a 0.30 m electromagnetic wave ----------
# source: physics/s116-em-waves (all EM waves travel at c in a vacuum; c = f lambda; spectrum table:
# microwaves about 1 mm to 1 m, visible about 400-700 nm, X-rays about 0.01-10 nm) and
# physics/s116-photons-spectra (photon energy E = hf).
C = 3 * sp.Integer(10) ** 8
MICROWAVE_M = (R(1, 1000), sp.Integer(1))
VISIBLE_M = (400 * R(1, 10**9), 700 * R(1, 10**9))
XRAY_MAX_M = 10 * R(1, 10**9)


def ph_em_wave_030m(item: dict) -> list[bool]:
    """q9: lambda = 0.30 m. Options: f = 1.0e9 Hz; faster than visible light; a microwave;
    photon energy less than a visible photon; frequency higher than X-rays."""
    lam = _r("0.30")
    f = C / lam
    speed_this, speed_visible = C, C
    f_visible_min = C / VISIBLE_M[1]
    f_xray_min = C / XRAY_MAX_M
    return [
        f == 10**9,
        bool(speed_this > speed_visible),
        bool(MICROWAVE_M[0] <= lam <= MICROWAVE_M[1]),
        bool(f < f_visible_min),  # E = hf, so a lower frequency means less energy per photon
        bool(f > f_xray_min),
    ]


# ---------- q37-q39: immersion heater set ----------
# source: physics/s116-em-waves (P = IV), physics/s116-energy-conservation (energy in = energy
# stored + energy out; energy is conserved), physics/s116-heat-energy-quality (heat = mass x
# specific heat x temperature change; water about 4.2e3 J/(kg C); energy spreads out and is
# degraded). 1 W = 1 J/s is given in the stem.
P_W, V_V = sp.Integer(550), sp.Integer(110)
T_S = 5 * 60
M_KG, S_WATER = _r("0.50"), 4200
T_START, T_END = 25, 80


def ph_heater_current(item: dict) -> list[bool]:
    """q37: options (A): 0.20, 2.0, 5.0, 50, 6.05e4."""
    current = P_W / V_V
    return [current == o for o in (_r("0.20"), 2, 5, 50, 60500)]


def ph_heater_energy(item: dict) -> list[bool]:
    """q38: options (J): 2.75e3, 1.65e4, 1.65e5, 1.65e6, 9.9e6."""
    energy = P_W * T_S
    return [energy == o for o in (2750, 16500, 165000, 1650000, 9900000)]


def ph_mixed_heater_share(item: dict) -> bool:
    """q39: the model answer's Q = 1.155e5 J, share 70 %, remainder 4.95e4 J, and the energy
    balance electrical = water heat + heat lost."""
    energy = P_W * T_S
    heat = M_KG * S_WATER * (T_END - T_START)
    share = heat / energy
    rest = energy - heat
    return bool(
        energy == 165000
        and heat == 115500
        and share == R(70, 100)
        and rest == 49500
        and heat + rest == energy
        and 0 < share < 1
    )
