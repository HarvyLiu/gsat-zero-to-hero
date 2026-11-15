"""Checks for src/data/items/physics/s116-matter-interactions.yaml
(116 sprint: make-up of matter and the four fundamental interactions; PKe-Ⅴc-1~3, PKc-Ⅴc-1~2).

Each function recomputes its item's answer from the physics, never from item["answer"]:
numeric items with exact SymPy ratios, qualitative items by encoding the physical rule as code
(charges and their signs, inverse-square ratios, the dipole field of a bar magnet, ranges as powers
of ten). Facts tables carry a source comment per fact.
"""

from __future__ import annotations

import sympy as sp

# --- Facts tables -------------------------------------------------------------------------------

# Which fundamental interaction is behind a force. Source: 108課綱 PKe-Ⅴc-2~3 / nat.json keyConcepts
# ("Everyday forces (friction, contact, elastic, gas pressure) are electromagnetic at the atomic level";
# "All interactions reduce to gravity, electromagnetism, strong and weak"; weight is universal gravitation).
ORIGIN = {
    "normal": "em",  # contact (正向力): electron clouds of two surfaces repel
    "friction": "em",
    "elastic": "em",
    "gas_pressure": "em",
    "weight": "gravity",
    "nucleon_binding": "strong",  # nat.json: strong force binds p–p, p–n, n–n
    "free_neutron_decay": "weak",  # nat.json: a free neutron decays via the weak interaction
    "electron_held_in_atom": "em",  # nat.json PKc-Ⅴc-2: electron–nucleus electric attraction
}
FOUR = ("gravity", "em", "strong", "weak")

# Charges in units of e. Source: standard physics, as taught in 108課綱 PKe-Ⅴc-1 說明 1-4~1-5
# (neutral atom = positive nucleus + electrons; nucleus = protons + neutrons).
CHARGE = {"proton": 1, "neutron": 0, "electron": -1, "antineutrino": 0}

# Masses relative to the electron (standard values, rounded): m_p ≈ 1836 m_e, m_n ≈ 1839 m_e.
MASS = {"electron": 1, "proton": 1836, "neutron": 1839}

# Ranges in metres, as orders of magnitude. Source: nat.json PKe-Ⅴc-1~3 (strong: range limited to
# nuclear size, about 1e-15 m; weak: even shorter, about 1e-18 m in standard physics);
# gravity and electromagnetism: inverse-square with no cut-off (infinite range).
RANGE = {"strong": sp.Integer(10) ** -15, "weak": sp.Integer(10) ** -18, "gravity": sp.oo, "em": sp.oo}

# Who is affected. Source: nat.json (strong: p–p, p–n, n–n); charged particles feel the EM force.
STRONG_ACTS_ON = {("p", "p"), ("p", "n"), ("n", "n")}

# Can the interaction repel? Gravity: always attraction (mass is never negative);
# electric force: like charges repel (108課綱 PKc-Ⅴc-1, Coulomb).
CAN_REPEL = {"gravity": False, "em": True}

# States of matter from the atomic view. Source: 108課綱 PKe-Ⅴc-1 說明 1-2 (standard particle model).
STATES = {
    "solid": {"spacing": "close", "moves": "vibrate in place", "binding": "strong", "fixed_shape": True, "fixed_volume": True, "compressible": False},
    "liquid": {"spacing": "close", "moves": "slide past", "binding": "medium", "fixed_shape": False, "fixed_volume": True, "compressible": False},
    "gas": {"spacing": "far", "moves": "free", "binding": "weak", "fixed_shape": False, "fixed_volume": False, "compressible": True},
}


def _inverse_square_ratio(q_factor, dist_factor) -> sp.Rational:
    """F'/F for F ∝ (product of charges or masses) / r², without any constant: only ratios matter."""
    return sp.Rational(q_factor) / sp.Rational(dist_factor) ** 2


def _dipole_field(m: sp.Matrix, r: sp.Matrix) -> sp.Matrix:
    """Field of a small magnet (dipole moment m, pointing from S to N) at position r, up to a positive
    constant: B ∝ (3(m·r̂)r̂ − m)/|r|³."""
    rn = sp.sqrt(r.dot(r))
    rh = r / rn
    return (3 * m.dot(rh) * rh - m) / rn**3


# --- Item checks ----------------------------------------------------------------------------------


def mi_turn_contact_force(item: dict) -> list[bool]:
    """q-turn: the push of a table on your hand. Options: gravity, EM, strong, weak,
    'none of the four (a fifth kind of force)'."""
    k = ORIGIN["normal"]
    return [k == "gravity", k == "em", k == "strong", k == "weak", k not in FOUR]


def mi_gas_compressible(item: dict) -> list[bool]:
    """q1: the atomic-view reason a gas is easy to compress. Options:
    (1) gas atoms are smaller; (2) atoms far apart, interactions between them very weak;
    (3) gas atoms do not move; (4) gas atoms are charged; (5) gas atoms are squashed when compressed."""
    g = STATES["gas"]
    reason_is_spacing = g["compressible"] and g["spacing"] == "far" and g["binding"] == "weak"
    # same atoms in every state (a substance keeps its atoms), so 'smaller' and 'squashed' are false;
    # gas atoms move freely; atoms are neutral (CHARGE: Z protons balance Z electrons)
    same_atoms_in_all_states = True
    atoms_neutral = CHARGE["proton"] + CHARGE["electron"] == 0
    return [
        not same_atoms_in_all_states,
        reason_is_spacing,
        g["moves"] == "none",
        not atoms_neutral,
        not same_atoms_in_all_states,
    ]


def mi_atom_statements(item: dict) -> list[bool]:
    """q2 (multi): statements about a carbon-12 atom (6 protons, 6 neutrons, 6 electrons).
    (1) the whole atom is neutral; (2) the nucleus is protons and neutrons; (3) protons and neutrons are
    made of quarks; (4) the neutron is positive; (5) more than half the atom's mass is in its electrons."""
    Z, N = 6, 6
    net = Z * CHARGE["proton"] + N * CHARGE["neutron"] + Z * CHARGE["electron"]
    nucleus_parts = {"proton", "neutron"}  # 說明 1-5
    nucleons_of_quarks = True  # 說明 1-6 (quark types not required)
    m_e = Z * MASS["electron"]
    m_total = Z * MASS["proton"] + N * MASS["neutron"] + m_e
    return [
        net == 0,
        nucleus_parts == {"proton", "neutron"},
        nucleons_of_quarks,
        CHARGE["neutron"] > 0,
        sp.Rational(m_e, m_total) > sp.Rational(1, 2),
    ]


def mi_coulomb_ratio(item: dict) -> tuple[int, int]:
    """q3 (fill p/q): one charge ×2, the other ×3, distance ×2. F'/F = (2·3)/2²."""
    r = _inverse_square_ratio(2 * 3, 2)
    return (int(r.p), int(r.q))


def mi_gravity_height(item: dict) -> sp.Integer:
    """q4 (fill): weight W at the surface (distance R from Earth's centre). Moved to a HEIGHT of 2R above
    the surface, the distance from the centre is 3R. F'/F = 1/3², so the answer is the denominator."""
    R = sp.Symbol("R", positive=True)
    d_new = R + 2 * R
    ratio = sp.simplify((R / d_new) ** 2)
    return sp.Integer(1 / ratio)


def mi_positive_charge_field(item: dict) -> list[bool]:
    """q5: field lines of an isolated positive point charge. Options:
    (1) straight lines radiating outward, sparser farther away; (2) straight lines pointing inward, denser
    farther away; (3) circles around the charge; (4) parallel, equally spaced lines; (5) outward, denser
    farther away.
    Direction: force on a positive test charge from a positive source points along +r̂ (like charges repel).
    Density: N lines through a sphere of area 4πr², so density ∝ 1/r²."""
    r = sp.Symbol("r", positive=True)
    q_src, q_test = CHARGE["proton"], CHARGE["proton"]
    outward = q_src * q_test > 0
    density = 1 / (4 * sp.pi * r**2)
    sparser_far = bool(sp.diff(density, r) < 0)
    radial = True  # a single point charge has no preferred direction except along r̂
    return [
        outward and radial and sparser_far,
        (not outward) and radial and (not sparser_far),
        not radial,
        not radial,  # parallel uniform lines would need a field that does not point along r̂
        outward and radial and (not sparser_far),
    ]


def mi_interaction_statements(item: dict) -> list[bool]:
    """q6 (multi): (1) the strong force acts between proton and proton as well as proton and neutron;
    (2) its range is about the size of a nucleus; (3) the weak interaction reaches farther than the strong
    force; (4) a free neutron turning into a proton is due to the weak interaction; (5) gravity and the
    electric force can only attract."""
    nucleus_size = sp.Integer(10) ** -15
    return [
        ("p", "p") in STRONG_ACTS_ON and ("p", "n") in STRONG_ACTS_ON,
        RANGE["strong"] == nucleus_size,
        bool(RANGE["weak"] > RANGE["strong"]),
        ORIGIN["free_neutron_decay"] == "weak",
        (not CAN_REPEL["gravity"]) and (not CAN_REPEL["em"]),
    ]


def mi_compass_above_magnet(item: dict) -> list[bool]:
    """q7: a small compass directly above the middle of a horizontal bar magnet whose N pole is on the
    right (+x). Which way does the compass's N pole point? Options: toward the magnet's N end (right);
    toward its S end (left); straight up; straight down; nowhere in particular (no force).
    A compass N pole points along the field; the bar magnet is a dipole with m along +x."""
    m = sp.Matrix([1, 0])
    B = _dipole_field(m, sp.Matrix([0, 2]))
    bx, by = sp.simplify(B[0]), sp.simplify(B[1])
    return [
        bool(bx > 0) and by == 0,
        bool(bx < 0) and by == 0,
        bx == 0 and bool(by > 0),
        bx == 0 and bool(by < 0),
        bx == 0 and by == 0,
    ]


def mi_what_holds_electrons(item: dict) -> list[bool]:
    """q8: what keeps the electrons of an atom bound to it. Options: strong force; electric attraction
    between electrons and nucleus; gravity; weak interaction; electrons repelling one another.
    The strong force does not act on electrons (STRONG_ACTS_ON lists only nucleons); electron–electron
    force is repulsive (like charges); PKc-Ⅴc-2: the electric attraction keeps the atom stable."""
    k = ORIGIN["electron_held_in_atom"]
    ee_attract = CHARGE["electron"] * CHARGE["electron"] < 0
    strong_on_electrons = any("e" in pair for pair in STRONG_ACTS_ON)
    return [
        k == "strong" and strong_on_electrons,
        k == "em" and CHARGE["electron"] * CHARGE["proton"] < 0,
        k == "gravity",
        k == "weak",
        ee_attract,
    ]
