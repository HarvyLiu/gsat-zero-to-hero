"""Checks for src/data/items/physics/s116-matter-waves.yaml (116 sprint: PKd-Ⅴc-5~7).

Each function recomputes its item's answer from the physics; none reads item["answer"].
Interference items use the superposition of two waves (exact SymPy); qualitative items encode the
rule as code; history/attitude items read an explicit facts table whose every row names its source.
"""

from __future__ import annotations

import sympy as sp

# ---------------------------------------------------------------- facts table (sources in comments)
FACTS = {
    # nat.json nat:PKd-Vc-5 keyConcepts: "Electron double-slit experiment: same idea as Young's
    # experiment; shows electrons are waves."
    "electron_double_slit_shows_electron_wave": True,
    # nat.json nat:PKd-Vc-5 keyConcepts: "Photons, electrons and all microscopic particles show
    # wave–particle duality."
    "duality_all_microscopic_particles": True,
    # nat.json nat:PKd-Vc-5 keyConcepts: "Newton's laws do not apply below the atomic scale; quantum
    # theory applies."
    "newton_fails_below_atomic_scale": True,
    # nat.json nat:PKd-Vc-1 keyConcepts: "Light of high-enough frequency ejects electrons from some
    # metals" / photon energy E = hν: the photoelectric effect is the particle (photon) evidence.
    "photoelectric_shows_light_particle": True,
    # nat.json nat:PKa-Vc-5 keyConcepts: "light shows interference and diffraction"; demonstration
    # experiment: double-slit interference — the wave evidence for light.
    "double_slit_shows_light_wave": True,
    # research physics verification.final_units[25].key_concepts[1] (elective 電磁現象二與量子現象):
    # "Einstein's light quanta; de Broglie matter waves" — de Broglie proposed matter waves,
    # Einstein proposed light quanta.
    "matter_waves_proposed_by": "de Broglie",
    "light_quanta_proposed_by": "Einstein",
}

# Quantum picture of the electron double slit (PKd-Ⅴc-5, encoded as the rule the chapter teaches):
# each electron is detected at one point; the accumulated points follow the wave intensity, so
# fringes appear; the pattern does not depend on how many electrons are in flight at once.
QUANTUM_DOUBLE_SLIT = {"single_detection": "point", "accumulated": "fringes", "needs_many_at_once": False}


def _young_pattern(lam, d=2, L=8, half_width=6) -> str:
    """Classify the screen pattern of two coherent point sources (slits at y = ±d/2, screen at x = L).

    Path difference Δ(y) = r1 − r2 is odd in y and increases with y, so it runs over (−Δmax, Δmax).
    Bright where Δ/λ is an integer, dark where it is a half-integer (superposition of two waves).
    """
    y = sp.Integer(half_width)
    dmax = sp.sqrt(L**2 + (y + sp.Rational(d, 2)) ** 2) - sp.sqrt(L**2 + (y - sp.Rational(d, 2)) ** 2)
    top = dmax / lam  # exact; Δ/λ ranges over (−top, top)
    n_bright = 2 * int(sp.floor(top)) + 1
    n_dark = 2 * int(sp.floor(top + sp.Rational(1, 2)))
    if n_dark >= 2 and n_bright >= 2:
        return "fringes"
    return "single_line" if n_bright == 1 else "uniform"


def mw_turn_young_pattern(item: dict) -> list[bool]:
    """q-turn: monochromatic light through two slits. Options: two bright bands facing the slits only;
    alternating bright and dark fringes; uniform brightness; one central line only; total darkness."""
    pattern = _young_pattern(sp.Rational(1, 2))
    return [pattern == o for o in ("two_bands", "fringes", "uniform", "single_line", "dark")]


def mw_single_electron_buildup(item: dict) -> list[bool]:
    """q1: electrons sent one at a time. Options as (single detection, accumulated, needs many at once):
    (1) each electron is a faint whole fringe pattern; (2) one point each, fringes after many;
    (3) one point each, only two bands after many; (4) no interference possible one at a time;
    (5) fringes only when many electrons are sent at once."""
    q = QUANTUM_DOUBLE_SLIT
    opts = [
        q["single_detection"] == "whole_pattern",
        q["single_detection"] == "point" and q["accumulated"] == "fringes",
        q["single_detection"] == "point" and q["accumulated"] == "two_bands",
        q["accumulated"] == "none",
        q["needs_many_at_once"] is True,
    ]
    return opts


def mw_duality_statements(item: dict) -> list[bool]:
    """q2 (multi): (1) photoelectric effect shows light's particle side; (2) double-slit interference
    shows light's wave side; (3) the electron double slit shows electrons' wave side; (4) duality is
    only for photons, not for particles with mass; (5) one electron double-slit run shows both sides
    (point hits = particle, fringes = wave)."""
    f = FACTS
    q = QUANTUM_DOUBLE_SLIT
    both_in_one_run = q["single_detection"] == "point" and q["accumulated"] == "fringes"
    return [
        f["photoelectric_shows_light_particle"],
        f["double_slit_shows_light_wave"],
        f["electron_double_slit_shows_electron_wave"],
        not f["duality_all_microscopic_particles"],  # electrons have mass and still show duality
        both_in_one_run,
    ]


def mw_dark_fringe_rate(item: dict) -> list[bool]:
    """q3: slit A alone sends n electrons/min to P, slit B alone also n; with both open P is on a dark
    fringe. Count rate ∝ |amplitude|²; each slit alone gives |1|² = 1 (unit n); at a dark fringe the two
    waves arrive half a wavelength apart (phase π). Options in units of n: 2, 1, 0, 4, 1/2."""
    a = sp.Integer(1)
    rate = sp.simplify(sp.Abs(a + a * sp.exp(sp.I * sp.pi)) ** 2 / sp.Abs(a) ** 2)
    return [sp.simplify(rate - o) == 0 for o in (2, 1, 0, 4, sp.Rational(1, 2))]


# Characteristic sizes in metres (orders of magnitude). Atom ~1e-10 m: physics.json
# s116-scales-units objective "atom (about 10⁻¹⁰ m)"; the others are ordinary everyday/astronomical sizes.
ATOM_SCALE = sp.Rational(1, 10**10)


def mw_newton_scope(item: dict) -> list[bool]:
    """q4: which situation can LEAST be described by Newton's laws alone?
    (1) the Moon orbiting the Earth (~4e8 m); (2) a pitched baseball (~7e-2 m);
    (3) the state of an electron inside an atom (~1e-10 m); (4) a block sliding down a slope (~1e-1 m);
    (5) an artificial satellite (~7e6 m). Rule (PKd-Ⅴc-7): at or below the atomic scale → quantum theory."""
    sizes = [4 * sp.Integer(10) ** 8, sp.Rational(7, 100), ATOM_SCALE, sp.Rational(1, 10), 7 * sp.Integer(10) ** 6]
    assert FACTS["newton_fails_below_atomic_scale"]
    return [bool(s <= ATOM_SCALE) for s in sizes]


def _path_difference(y, d, L):
    """Exact path difference r1 − r2 from a screen point at height y to slits at ±d/2, screen at L."""
    return sp.sqrt(L**2 + (y + d / 2) ** 2) - sp.sqrt(L**2 + (y - d / 2) ** 2)


def _first_bright_offset(lam, d=sp.Rational(1, 10**4), L=sp.Integer(1)):
    """Distance on the screen from the central bright fringe (y = 0) to the next one: the y > 0 where
    the path difference first equals one wavelength (superposition: in step again)."""
    y = sp.symbols("y", positive=True)
    root = sp.nsolve(_path_difference(y, d, L) - lam, y, lam * L / d, prec=40)
    assert abs(_path_difference(root, d, L) - lam) < sp.Float("1e-30")
    return root


def mw_fringe_spacing_colour(item: dict) -> list[bool]:
    """q5: same double slit and screen; red light (longer λ) replaced by blue (shorter λ). Options:
    spacing larger; smaller; unchanged; fringes vanish (even glow); bright/dark swap so the centre is dark.
    The stem only says λ_red > λ_blue; representative values 700 nm and 450 nm (slits 0.1 mm apart,
    screen 1 m away) are used to compute the spacing from the exact two-source geometry."""
    lam_red, lam_blue = sp.Rational(700, 10**9), sp.Rational(450, 10**9)
    assert lam_red > lam_blue  # the stem's only premise
    s_red, s_blue = _first_bright_offset(lam_red), _first_bright_offset(lam_blue)
    d, L = sp.Rational(1, 10**4), sp.Integer(1)
    # centre: path difference 0 → in step → bright for any wavelength, so no swap
    centre_bright = sp.simplify(_path_difference(sp.Integer(0), d, L)) == 0
    # a shorter wavelength still gives many fringes across a 1 cm strip of screen
    blue_has_fringes = _path_difference(sp.Rational(1, 100), d, L) / lam_blue > 2
    return [
        bool(s_blue > s_red),
        bool(s_blue < s_red),
        bool(abs(s_blue - s_red) < sp.Float("1e-12")),
        not blue_has_fringes,
        not centre_bright,
    ]


def mw_hair_atom_power(item: dict) -> sp.Integer:
    """q6: hair width 1e-4 m, atom size 1e-10 m: the hair is 10 to which power times the atom?"""
    hair = sp.Rational(1, 10**4)
    ratio = hair / ATOM_SCALE
    power = sp.log(ratio, 10)
    assert power.is_integer
    assert hair > ATOM_SCALE  # far above the atomic scale: Newtonian, as the explanation says
    return sp.Integer(power)


def mw_history(item: dict) -> list[bool]:
    """q7: (1) de Broglie proposed that matter such as electrons also behaves as a wave;
    (2) Newton proposed that electrons are waves; (3) the wave behaviour of electrons has never been
    confirmed by experiment; (4) Einstein proposed matter waves; (5) the electron double slit shows
    electrons are pure particles that never interfere."""
    f = FACTS
    return [
        f["matter_waves_proposed_by"] == "de Broglie",
        f["matter_waves_proposed_by"] == "Newton",
        not f["electron_double_slit_shows_electron_wave"],
        f["matter_waves_proposed_by"] == "Einstein",  # Einstein's name goes with light quanta instead
        not f["electron_double_slit_shows_electron_wave"],
    ]
