"""Checks for src/data/items/physics/s116-photons-spectra.yaml (116 sprint: photons, the
photoelectric effect, atomic spectra and energy levels; nat:PKd-Vc-1~4).

Each function recomputes its item's answer from the physics, never from item["answer"].
Numbers use the approximations stated in the stems: h = 6.6e-34 J s, c = 3e8 m/s, exact Rationals.
Qualitative items encode the rule as code: one photon gives its whole energy hf to one electron;
an electron leaves the metal only if hf exceeds the energy it needs; brightness = number of photons.
"""

from __future__ import annotations

from itertools import combinations

import sympy as sp

H = sp.Rational(66, 10) * sp.Integer(10) ** -34  # J s, as stated in the stems
C = 3 * sp.Integer(10) ** 8  # m/s, as stated in the stems
NM = sp.Integer(10) ** -9  # m


def _photon_energy(f, brightness=1):
    """E = hf for ONE photon. `brightness` (photons per second) is accepted and deliberately unused:
    the energy of each photon depends on frequency alone (PKd-Vc-1)."""
    del brightness
    return H * f


def _freq(wavelength_nm) -> sp.Expr:
    """v = f lambda with v = c."""
    return C / (sp.Integer(wavelength_nm) * NM)


def _photoelectric(f, photons_per_s, need):
    """Photon picture of the photoelectric effect (qualitative; no K = hf - W derivation is taught,
    the leftover energy is only compared). Returns (electrons per second, leftover energy per electron).
    One photon -> at most one electron; nothing comes out when hf <= need, however bright the light."""
    e = _photon_energy(f, photons_per_s)
    if e > need:
        return photons_per_s, e - need
    return 0, sp.Integer(0)


def pe_turn_red_violet(item: dict) -> list[bool]:
    """q-turn: red light (700 nm) vs violet light (400 nm): whose photon has more energy?
    Options: red; violet; equal; depends on brightness; depends on distance to the source."""
    e_red, e_violet = _photon_energy(_freq(700)), _photon_energy(_freq(400))
    # brightness: compare one photon from a dim and from a bright violet lamp
    depends_on_brightness = _photon_energy(_freq(400), 1) != _photon_energy(_freq(400), 1000)
    # distance does not enter E = hf at all (f is unchanged for a source at rest)
    depends_on_distance = False
    return [e_red > e_violet, e_violet > e_red, e_red == e_violet, depends_on_brightness, depends_on_distance]


def pe_frequency_500nm(item: dict) -> tuple[int, int]:
    """q1: frequency of 500 nm light, written a x 10^b with a one digit: return (a, b)."""
    f = _freq(500)
    b = 0
    a = f
    while a >= 10:
        a /= 10
        b += 1
    assert a == int(a), "the mantissa should be an exact single digit"
    return (int(a), b)


def pe_ratio_250_750(item: dict) -> sp.Integer:
    """q2: photon energy of 250 nm UV light over that of 750 nm red light."""
    r = _photon_energy(_freq(250)) / _photon_energy(_freq(750))
    assert r.is_Integer
    return sp.Integer(r)


def pe_statements(item: dict) -> list[bool]:
    """q3: a metal whose electrons need W to escape; light below / above the frequency it takes.
    (1) brighter light below that frequency ejects electrons;
    (2) above it, brighter light ejects more electrons per second;
    (3) above it, brighter light gives a larger maximum leftover (kinetic) energy;
    (4) higher-frequency light gives a larger maximum leftover energy;
    (5) energy reaches each electron one photon at a time (the photon picture used throughout)."""
    W = sp.Rational(4, 1) * sp.Integer(10) ** -19
    f_low = W / H / 2  # half the needed frequency
    f_high = 2 * W / H
    f_higher = 3 * W / H
    dim, bright = 10, 10**6
    s1 = _photoelectric(f_low, bright, W)[0] > 0
    s2 = _photoelectric(f_high, bright, W)[0] > _photoelectric(f_high, dim, W)[0]
    s3 = _photoelectric(f_high, bright, W)[1] > _photoelectric(f_high, dim, W)[1]
    s4 = _photoelectric(f_higher, dim, W)[1] > _photoelectric(f_high, dim, W)[1]
    # (5): in the model one photon gives energy to one electron, so the electron count never exceeds
    # the photon count and depends on single-photon energy, not on the total delivered energy
    total_energy_low = bright * _photon_energy(f_low)
    s5 = total_energy_low > W and _photoelectric(f_low, bright, W)[0] == 0
    return [s1, s2, s3, s4, s5]


def pe_which_wavelengths(item: dict) -> list[bool]:
    """q4: electrons need at least 4.4e-19 J to leave the metal. Which light ejects electrons?
    Options: 700 nm (very bright light); 600 nm; 500 nm; 400 nm; 300 nm."""
    need = sp.Rational(44, 10) * sp.Integer(10) ** -19
    out = []
    for lam, photons in ((700, 10**18), (600, 1), (500, 1), (400, 1), (300, 1)):
        out.append(_photoelectric(_freq(lam), photons, need)[0] > 0)
    return out


LEVELS_Q5 = (-10, -6, -4)  # eV, lowest first (the stem's atom)


def el_absorb_from_ground(item: dict) -> list[bool]:
    """q5: atom in its lowest level (levels -10, -6, -4 eV). Which photon energies can it absorb?
    Options: 2, 4, 5, 6, 8 eV. An absorbed photon must match a gap from the CURRENT level upward."""
    ground = LEVELS_Q5[0]
    gaps = {e - ground for e in LEVELS_Q5[1:]}
    return [o in gaps for o in (2, 4, 5, 6, 8)]


def el_count_lines_5(item: dict) -> sp.Integer:
    """q6: electron excited to the 5th level (5 levels, all gaps different). Maximum number of
    different photon frequencies on the way down. Count all downward jumps between two levels,
    using a concrete level set with distinct gaps (hydrogen-like -13.6/n^2) and counting distinct gaps."""
    levels = [-sp.Rational(136, 10) / n**2 for n in range(1, 6)]
    gaps = {hi - lo for lo, hi in combinations(sorted(levels), 2)}
    assert len(gaps) == len(list(combinations(levels, 2))), "the gaps must all differ, as the stem says"
    return sp.Integer(len(gaps))


Q7_ELEMENTS = {  # bright lines (nm) of the stem's made-up elements 甲, 乙, 丙, 丁, 戊
    "甲": {440, 530},
    "乙": {470, 620},
    "丙": {420, 580, 650},
    "丁": {510, 680},
    "戊": {620, 650},
}
Q7_DARK_LINES = {420, 440, 530, 580, 650}  # dark lines in the star's spectrum (stem)


def sp_identify_elements(item: dict) -> list[bool]:
    """q7: an element is present when ALL of its bright lines appear as dark lines (same wavelengths:
    a gas absorbs exactly the photons it can emit). Options in order 甲 乙 丙 丁 戊."""
    return [lines <= Q7_DARK_LINES for lines in Q7_ELEMENTS.values()]


# Facts table for q8. Source for every row: src/data/registry/codes/nat.json, nat:PKd-Va-1
# keyConcepts[1] ("Thomson cathode-ray tube and Millikan oil drop; X-rays; Planck and black-body
# radiation; Einstein's light quanta; de Broglie matter waves; Rutherford and Bohr models"), the same
# list as research physics verification.final_units[25].key_concepts[1].
WORK_OF = {
    "Planck": "black-body radiation",
    "Einstein": "light quanta",
    "de Broglie": "matter waves",
    "Thomson": "cathode-ray tube",
    "Millikan": "oil drop",
    "Rutherford": "atom model",
    "Bohr": "atom model",
}


def hist_pairs(item: dict) -> list[bool]:
    """q8: which pairing is correct?
    Options: Planck - oil drop; Einstein - light quanta; Bohr - black-body radiation;
    Millikan - cathode-ray tube; Rutherford - light quanta."""
    pairs = [
        ("Planck", "oil drop"),
        ("Einstein", "light quanta"),
        ("Bohr", "black-body radiation"),
        ("Millikan", "cathode-ray tube"),
        ("Rutherford", "light quanta"),
    ]
    return [WORK_OF[p] == w for p, w in pairs]
