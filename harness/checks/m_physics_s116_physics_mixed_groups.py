"""Checks for src/data/items/physics/s116-physics-mixed-groups.yaml (116 sprint, physics exam skills:
reading-based and cross-subject item groups).

Each function recomputes its item's answer from the physics (or, for the one exam-history item, from
an explicit facts table with a source per fact); none reads item["answer"].

The lesson itself stays qualitative (the 課綱 treats the Doppler effect qualitatively). The checks may
use the standard Doppler formulas, because a check only needs the SIGN or the ORDER of a frequency
change, and the formulas are the most reliable way to get those right.
"""

from __future__ import annotations

import sympy as sp

# ---------- shared physics ----------

def _reflected_frequency(f, v_wave, u):
    """Ultrasound of frequency f sent from a fixed probe, reflected by a red blood cell moving at speed u
    TOWARD the probe (u < 0: away). Sound speed in tissue v_wave. Classical two-step Doppler:
    the moving cell receives f(v+u)/v and re-emits it as a moving source, so the probe hears
    f(v+u)/(v-u)."""
    return f * (v_wave + u) / (v_wave - u)


# typical values, exact: 5 MHz probe, sound in soft tissue about 1540 m/s, blood about 0.5 m/s
F0 = sp.Integer(5 * 10**6)
V_TISSUE = sp.Integer(1540)


def _shift(u):
    return sp.simplify(_reflected_frequency(F0, V_TISSUE, u) - F0)


def _light_received_frequency(f, beta):
    """Light from a source receding at speed beta*c (beta > 0 away). Relativistic longitudinal Doppler."""
    return f * sp.sqrt((1 - beta) / (1 + beta))


# ---------- items ----------

def mg_turn_blood_toward(item: dict) -> list[bool]:
    """q-turn: red cells flow TOWARD the probe; how does the reflected frequency compare with the sent one?
    Options: higher; lower; the same; cannot tell, it depends on the ultrasound's intensity;
    the frequency stays the same, only the loudness changes."""
    u = sp.Rational(1, 2)  # 0.5 m/s toward the probe
    d = _shift(u)
    # the frequency formula has no amplitude in it: intensity cannot decide the answer
    f, v, w, amp = sp.symbols("f v u A", positive=True)
    depends_on_intensity = amp in _reflected_frequency(f, v, w).free_symbols
    return [bool(d > 0), bool(d < 0), bool(d == 0), depends_on_intensity, bool(d == 0)]


def mg_stenosis_speed(item: dict) -> list[bool]:
    """q1: the stem states that the same volume of blood passes every cross-section each second
    (A1 v1 = A2 v2). Upstream speed 20 cm/s; at the narrowing the cross-section is 1/4 as large.
    Options (cm/s): 5, 20, 40, 80, 320."""
    a1, v1 = sp.Integer(1), sp.Integer(20)
    a2 = a1 * sp.Rational(1, 4)
    v2 = sp.solve(sp.Eq(a1 * v1, a2 * sp.Symbol("v2")), sp.Symbol("v2"))[0]
    return [v2 == o for o in (5, 20, 40, 80, 320)]


# What kind of wave each is (standard physics: ultrasound is sound, a mechanical wave that needs a
# medium; light is an electromagnetic wave, nat:PKa-Vc-7 keyConcepts "light is an EM wave").
WAVE_KIND = {"ultrasound": "mechanical", "light": "electromagnetic"}


def mg_blood_flow_statements(item: dict) -> list[bool]:
    """q2 (multi): statements about Doppler ultrasound on blood flow.
      (1) flow toward the probe -> reflected frequency higher than sent
      (2) flow away from the probe -> reflected frequency higher than sent
      (3) where the vessel narrows the flow is faster, so the frequency change is larger
      (4) ultrasound, like light, is an electromagnetic wave
      (5) if the blood stops, the reflected frequency equals the sent one"""
    toward, away = sp.Rational(1, 2), -sp.Rational(1, 2)
    s1 = _shift(toward) > 0
    s2 = _shift(away) > 0
    # (3): |shift| grows with speed for 0 < u < v (derivative of the shift is positive there)
    # d/du of f(v+u)/(v-u) is 2fv/(v-u)^2: positive for every blood speed (u far below v = 1540 m/s)
    u = sp.Symbol("u", positive=True)
    dshift = sp.simplify(sp.diff(_reflected_frequency(F0, V_TISSUE, u), u))
    assert sp.simplify(dshift - 2 * F0 * V_TISSUE / (V_TISSUE - u) ** 2) == 0
    speeds = [sp.Rational(n, 10) for n in range(1, 31)]  # 0.1 to 3 m/s
    s3 = all(_shift(a) < _shift(b) for a, b in zip(speeds, speeds[1:]))
    s4 = WAVE_KIND["ultrasound"] == WAVE_KIND["light"]
    s5 = _shift(sp.Integer(0)) == 0
    return [s1, s2, s3, s4, s5]


# The stem gives the conversion "photon energy (eV) x wavelength (nm) ≈ 1240".
HC_EV_NM = sp.Integer(1240)


def mg_led_wavelength(item: dict) -> int:
    """q3 (fill ①②③): band gap 3.1 eV, photon energy ≈ gap, so λ ≈ 1240/3.1 nm."""
    lam = HC_EV_NM / sp.Rational(31, 10)
    assert lam.is_Integer
    return int(lam)


# Mechanisms of five 必修 ideas, as feature sets (sources: nat.json keyConcepts).
MECHANISMS = {
    # nat:PKd-Vc-3/4: electrons can only have specific energies; moving between levels absorbs or emits
    # a photon of that energy; CEEC says this lets students handle band-theory passages (114 Q50–54)
    "level-transition": {"electron", "drops to lower energy", "emits photon", "photon energy = energy difference"},
    # nat:PKd-Vc-1/2: light of high-enough frequency ejects electrons from some metals
    "photoelectric": {"light absorbed", "electron ejected"},
    # nat:PKa-Vc-1/2: frequency change from relative motion of source and observer
    "doppler": {"relative motion", "frequency change"},
    # nat:PKc-Vc-3: a changing magnetic field produces an electric field / current
    "induction": {"changing magnetic field", "current"},
    # nat:PNc-Vc-1/2, PBa-Vc-3/4: nuclear fission converts mass to energy
    "fission": {"nucleus splits", "mass to energy"},
}
# What the stem's LED passage describes
LED_PASSAGE = {"electron", "drops to lower energy", "emits photon", "photon energy = energy difference"}


def mg_band_to_levels(item: dict) -> list[bool]:
    """q4: which 必修 idea does the LED band passage map onto?
    Options: energy-level transition; photoelectric effect; Doppler effect; induction; fission."""
    order = ["level-transition", "photoelectric", "doppler", "induction", "fission"]
    return [MECHANISMS[k] == LED_PASSAGE for k in order]


def mg_balance_current(item: dict) -> int:
    """q5 (fill ①②): the stem says the coil's magnetic force is proportional to the current and balances
    the weight of the mass. 20 g balances at 50 mA; current for 36 g?"""
    k = sp.Symbol("k", positive=True)  # force per mA
    g = sp.Symbol("g", positive=True)
    m1, i1, m2 = sp.Rational(20, 1000), sp.Integer(50), sp.Rational(36, 1000)
    ksol = sp.solve(sp.Eq(k * i1, m1 * g), k)[0]
    i2 = sp.solve(sp.Eq(ksol * sp.Symbol("I"), m2 * g), sp.Symbol("I"))[0]
    assert i2.is_Integer
    return int(i2)


def mg_unneeded_data(item: dict) -> list[bool]:
    """q6 (multi): to find the LED's wavelength, which of the given data are NOT needed?
    Options: band gap; price; service life; photons emitted per second; factory location.
    λ ≈ 1240 / E_photon and E_photon ≈ E_gap: the wavelength depends on the gap alone."""
    gap, price, life, rate, place = sp.symbols("E_gap price life N place", positive=True)
    lam = HC_EV_NM / gap  # one photon's energy fixes its wavelength; how many photons does not
    needed = lam.free_symbols
    return [s not in needed for s in (gap, price, life, rate, place)]


# Cross-subject item groups that included physics, by sitting (source: research/verified-2026-11-15.json,
# key "physics", research.exam_format and verification.exam_format_verified; key_facts per year:
# 111 Q49–54 physics/biology; 112 Q51–54 physics/earth; 113 Q40–43 biology/physics;
# 114 Q50–54 physics/chemistry; 115 Q50–53 earth/physics).
CROSS_PARTNER = {111: "biology", 112: "earth", 113: "biology", 114: "chemistry", 115: "earth"}


def mg_cross_subject_years(item: dict) -> list[bool]:
    """q7 (multi): which pairings happened? (111, biology); (112, chemistry); (113, biology);
    (114, chemistry); (115, biology)."""
    claims = [(111, "biology"), (112, "chemistry"), (113, "biology"), (114, "chemistry"), (115, "biology")]
    return [CROSS_PARTNER[y] == s for y, s in claims]


def mg_star_receding(item: dict) -> list[bool]:
    """q8: a star moving away from Earth. Options as (wavelength, frequency) received vs emitted:
    (longer, lower); (shorter, higher); (longer, higher); (unchanged, unchanged); (shorter, lower).
    v = fλ with v = c fixed, so λ = c/f."""
    c = sp.Integer(3 * 10**8)
    f0 = sp.Integer(5 * 10**14)
    beta = sp.Rational(1, 10)
    f = _light_received_frequency(f0, beta)
    lam0, lam = c / f0, c / f
    sign = lambda a, b: int(bool(a > b)) - int(bool(a < b))  # noqa: E731
    got = (sign(lam, lam0), sign(f, f0))
    options = [(1, -1), (-1, 1), (1, 1), (0, 0), (-1, -1)]
    return [got == o for o in options]
