"""Checks for src/data/items/physics/s116-em-waves.yaml (116 sprint: Maxwell, EM waves and light,
the EM spectrum, light Doppler, electrical safety and the induction cooker).

Each function recomputes its item's answer from the physics (exact SymPy numbers, or the rule written
as code); none reads item["answer"]. Fact tables carry a source comment per fact.
"""

from __future__ import annotations

import sympy as sp

# ---------------------------------------------------------------------------
# Constants. c is exact (SI definition). eps0 and mu0 are the values a textbook quotes; they are only
# used to show that 1/sqrt(eps0*mu0) lands on c (within 0.1 %), so three significant figures suffice.
# ---------------------------------------------------------------------------
C_EXACT = sp.Integer(299792458)  # m/s, SI definition of the metre
C_STEM = sp.Integer(3) * sp.Integer(10) ** 8  # the approximation the stems state
EPS0 = sp.Rational(885, 100) * sp.Integer(10) ** -12  # C^2/(N m^2)
MU0 = 4 * sp.pi * sp.Integer(10) ** -7  # T m/A


def _close(a, b, rel=sp.Rational(1, 100)) -> bool:
    """|a − b| ≤ rel·|b|, decided exactly (pi is evaluated to 30 digits only for the comparison)."""
    return bool(sp.N(sp.Abs(a - b) - rel * sp.Abs(b), 30) <= 0)


# Representative wavelengths (m) for each band, inside the usual band ranges (band edges are fuzzy):
# radio 10 m, microwave 3 cm, infrared 10 μm, visible 500 nm (400–700 nm), ultraviolet 25 nm
# (10–400 nm), X-ray 0.3 nm, gamma 2 pm. The lesson's NumberLine uses the same points.
BAND_LAMBDA = {
    "radio": sp.Integer(10),
    "microwave": sp.Rational(3, 100),
    "infrared": sp.Integer(10) ** -5,
    "visible": 5 * sp.Integer(10) ** -7,
    "ultraviolet": sp.Rational(25, 1) * sp.Integer(10) ** -9,
    "xray": sp.Rational(3, 10) * sp.Integer(10) ** -9,
    "gamma": 2 * sp.Integer(10) ** -12,
}
VISIBLE_RANGE = (4 * sp.Integer(10) ** -7, 7 * sp.Integer(10) ** -7)  # m, violet to red (approx.)


def _freq(band: str):
    """f = c / λ: every EM wave travels at c in vacuum."""
    return C_EXACT / BAND_LAMBDA[band]


def em_turn_speed_match(item: dict) -> list[bool]:
    """q-turn: Maxwell's predicted EM-wave speed matches which speed?
    Options: sound in air (~340), light in vacuum, Earth's orbital speed (~3e4), ISS (~7.7e3), sound in water (~1500).
    The prediction is 1/sqrt(eps0*mu0) from lab constants; only light in vacuum is within 1 %."""
    v_pred = 1 / sp.sqrt(EPS0 * MU0)
    speeds = [sp.Integer(340), C_EXACT, 3 * sp.Integer(10) ** 4, sp.Rational(77, 10) * 10**3, sp.Integer(1500)]
    return [_close(v_pred, s) for s in speeds]


def em_spectrum_order(item: dict) -> list[bool]:
    """q1: which list runs from low to high frequency?"""
    options = [
        ["radio", "infrared", "visible", "xray", "gamma"],
        ["gamma", "xray", "visible", "infrared", "radio"],
        ["radio", "visible", "infrared", "xray", "gamma"],
        ["microwave", "radio", "visible", "ultraviolet", "xray"],
        ["radio", "microwave", "ultraviolet", "visible", "gamma"],
    ]
    def increasing(bands):
        fs = [_freq(b) for b in bands]
        return all(bool(fs[i] < fs[i + 1]) for i in range(len(fs) - 1))
    return [increasing(o) for o in options]


def em_am_wavelength(item: dict) -> sp.Integer:
    """q2: AM station at 1.0×10^6 Hz, c = 3×10^8 m/s (stated in the stem); λ = c / f in metres."""
    lam = C_STEM / sp.Integer(10) ** 6
    assert lam.is_integer
    return sp.Integer(lam)


def em_wave_statements(item: dict) -> list[bool]:
    """q3: statements about EM waves.
    (1) travel through vacuum; (2) in vacuum X-rays travel faster than radio waves;
    (3) in vacuum higher frequency means shorter wavelength; (4) visible light is a small part of the
    spectrum; (5) ultraviolet has a lower frequency than infrared."""
    # (1) EM waves are self-sustaining field disturbances (nat:PKc-Vc-5 keyConcepts: they
    # "propagate through space"); no medium is in the model.
    needs_medium = False
    s1 = not needs_medium
    # (2) one speed c for every band in vacuum
    speed = {b: C_EXACT for b in BAND_LAMBDA}
    s2 = bool(speed["xray"] > speed["radio"])
    # (3) λ = c/f with c fixed: compare two frequencies
    f_lo, f_hi = sp.Integer(10) ** 6, sp.Integer(10) ** 9
    s3 = bool(C_EXACT / f_hi < C_EXACT / f_lo)
    # (4) on a log scale the visible band (400–700 nm) is a small fraction of the radio-to-gamma span
    width = lambda a, b: sp.log(b / a, 10)
    vis = width(*VISIBLE_RANGE)
    whole = width(BAND_LAMBDA["gamma"], BAND_LAMBDA["radio"])
    s4 = bool(sp.N(vis / whole, 30) < sp.Rational(1, 10))
    # (5)
    s5 = bool(_freq("ultraviolet") < _freq("infrared"))
    return [s1, s2, s3, s4, s5]


def em_light_doppler(item: dict) -> list[bool]:
    """q4: a galaxy moves away from Earth; the observed wavelength of a spectral line compared with the lab.
    Options: longer (redshift); shorter (blueshift); unchanged; first longer then shorter; cannot tell.
    Receding source at speed u: each crest is emitted u·T farther away, so the crest spacing seen is
    λ' = (c + u)·T = λ0·(1 + u/c) (u ≪ c here)."""
    lam0 = 5 * sp.Integer(10) ** -7
    T = lam0 / C_EXACT
    u = sp.Integer(10) ** 6  # any receding speed u > 0 gives the same sign
    lam_obs = (C_EXACT + u) * T
    longer = bool(lam_obs > lam0)
    shorter = bool(lam_obs < lam0)
    same = bool(sp.Eq(lam_obs, lam0))
    # (4) the galaxy keeps receding (u > 0 throughout), so the shift cannot change sign
    u_path = [u, u]
    reverses = any(bool(a * b < 0) for a, b in zip(u_path, u_path[1:]))
    # (5) the model above needs no medium and gives a definite answer
    undecidable = not (longer or shorter or same)
    return [longer, shorter, same, reverses, undecidable]


def em_induction_cooker(item: dict) -> list[bool]:
    """q5: statements about an induction cooker.
    Rule (Faraday, qualitative): an induced current flows in a conductor only while the magnetic field
    through it changes; the heat appears where the induced current flows (the conductor's resistance)."""
    def induced_current(field_changing: bool, conductor: bool) -> bool:
        return field_changing and conductor

    ac_coil = True  # the coil is driven by high-frequency AC, so its field keeps changing
    # (1) coil carries high-frequency alternating current
    s1 = ac_coil
    # (2) steady DC: the field is constant after switch-on, so no lasting induced current
    s2 = induced_current(field_changing=False, conductor=True)
    # (3) heat comes from induced currents in the pot base (an iron pot conducts)
    s3 = induced_current(field_changing=ac_coil, conductor=True)
    # (4) a ceramic pot does not conduct: no induced current, no heating
    s4 = induced_current(field_changing=ac_coil, conductor=False)
    # (5) the glass top is an insulator: no induced current in it, so it is not the heat source
    s5 = induced_current(field_changing=ac_coil, conductor=False)
    return [s1, s2, s3, s4, s5]


def em_overload_current(item: dict) -> sp.Integer:
    """q6: 1100 W rice cooker + 660 W hair dryer on one 110 V cord: total current I = ΣP / V (國中 P = IV)."""
    total = (sp.Integer(1100) + sp.Integer(660)) / sp.Integer(110)
    assert total.is_integer
    assert total > 15  # exceeds the cord's 15 A rating, as the explanation says
    return sp.Integer(total)


def em_lightning_safety(item: dict) -> list[bool]:
    """q7: safest place in a thunderstorm.
    Rule: lightning tends to strike the tallest or most isolated point and you are at risk when you are
    (or hold) that point, stand beside it, or are in water/open ground; inside a closed metal car body
    the current is carried around the outside of the occupants."""
    places = [
        {"open_ground": True, "near_tall_isolated": False, "in_water": False, "metal_shell": False, "hold_raised_metal": False},  # open sports field
        {"open_ground": True, "near_tall_isolated": True, "in_water": False, "metal_shell": False, "hold_raised_metal": False},  # under a lone tall tree
        {"open_ground": False, "near_tall_isolated": False, "in_water": False, "metal_shell": True, "hold_raised_metal": False},  # in a closed car
        {"open_ground": True, "near_tall_isolated": False, "in_water": False, "metal_shell": False, "hold_raised_metal": True},  # metal-shaft umbrella in the open
        {"open_ground": True, "near_tall_isolated": False, "in_water": True, "metal_shell": False, "hold_raised_metal": False},  # swimming outdoors
    ]
    def safe(p):
        exposed = p["open_ground"] or p["near_tall_isolated"] or p["in_water"] or p["hold_raised_metal"]
        return p["metal_shell"] and not exposed
    return [safe(p) for p in places]


# Facts from src/data/registry/codes/nat.json, nat:PKc-Vc-4 keyConcepts (same text on PKc-Vc-5/6, PKa-Vc-7).
FACTS = {
    # "Maxwell unified all EM laws into one set of equations; their mathematical form is not needed"
    "maxwell_unifies_electric_and_magnetic": True,
    "math_form_required": False,
    # "Predicted EM-wave speed equals the measured speed of light, so light is an EM wave; later confirmed by experiment"
    "prediction_before_experimental_confirmation": True,
    "light_is_em_wave_because_predicted_speed_matches": True,
    # "Electromagnetic disturbances propagate through space as EM waves" (no medium: through vacuum)
    "em_waves_cross_vacuum": True,
}


def em_history_method(item: dict) -> list[bool]:
    """q8: how light was identified as an EM wave.
    (1) theory predicted EM-wave speed = measured light speed, so light is EM; later confirmed by experiment;
    (2) Maxwell first made EM waves in the lab, then derived the equations;
    (3) it was found because light cannot travel through vacuum;
    (4) Maxwell's equations describe only magnetism, not electricity;
    (5) the 學測 requires the mathematical form of the equations."""
    s1 = FACTS["light_is_em_wave_because_predicted_speed_matches"] and FACTS["prediction_before_experimental_confirmation"]
    s2 = not FACTS["prediction_before_experimental_confirmation"]
    s3 = not FACTS["em_waves_cross_vacuum"]
    s4 = not FACTS["maxwell_unifies_electric_and_magnetic"]
    s5 = FACTS["math_form_required"]
    return [s1, s2, s3, s4, s5]
