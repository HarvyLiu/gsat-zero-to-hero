"""Checks for src/data/items/physics/s116-waves-light.yaml (116 sprint: waves, Doppler, light; PKa-Ⅴc-1~6).

Each function recomputes its item's answer from the physics (or from an explicit, sourced facts table for
history items); none reads item["answer"]. Numbers are exact SymPy Rationals.
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational


# ---------------------------------------------------------------- wave and Doppler models

def _observed_period(T, v, u_src, u_obs, d0=R(1000)):
    """Period heard by an observer, from arrival times (no Doppler formula is assumed).

    1-D model: the source starts at x = 0 and moves with velocity u_src (+ = towards the observer);
    the observer starts at x = d0 > 0 and moves with velocity u_obs (+ = away from the source).
    Crest k leaves the source at time kT from x = u_src·kT and travels at v (the medium's wave speed);
    it reaches the observer when v(t − kT) = (d0 + u_obs·t) − u_src·kT. The heard period is the gap
    between the arrivals of crests 0 and 1 (all gaps are equal in this model)."""
    t = sp.symbols("t", real=True)

    def arrival(k):
        (sol,) = sp.solve(sp.Eq(v * (t - k * T), d0 + u_obs * t - u_src * k * T), t)
        return sol

    gaps = {sp.simplify(arrival(k + 1) - arrival(k)) for k in range(3)}
    assert len(gaps) == 1  # steady motion: every crest gap is the same
    return gaps.pop()


def _wavelength_ahead(T, v, u_src):
    """Spacing of crests in front of a source moving at u_src towards the front: in one period the
    previous crest moves vT while the source moves u_src·T after it."""
    return v * T - u_src * T


def dl_turn_ambulance(item: dict) -> list[bool]:
    """q-turn: an ambulance (siren f) drives towards a standing listener. Options: heard pitch higher;
    lower; the same; first lower then higher while approaching; depends on how loud the siren is."""
    f, v, u = R(700), R(340), R(20)  # any f > 0, any 0 < u < v gives the same comparison
    fo = 1 / _observed_period(1 / f, v, u, 0)
    # the heard period is the same for every crest gap (asserted in the model), so it does not change
    # while the ambulance approaches; the model has no amplitude input, so loudness does not enter.
    changes_while_approaching = False
    depends_on_loudness = False
    return [fo > f, fo < f, fo == f, changes_while_approaching, depends_on_loudness]


def wv_sonar_wavelength(item: dict) -> sp.Integer:
    """q1: sonar wave f = 7.5×10^4 Hz in water with v = 1500 m/s; wavelength in mm (λ = v/f)."""
    f = R(75, 10) * 10**4
    v = R(1500)
    lam_m = v / f
    lam_mm = lam_m * 1000
    assert lam_mm.is_integer
    return sp.Integer(lam_mm)


def rf_reflection_angle(item: dict) -> list[bool]:
    """q2: a ray makes 30° with a plane mirror. Options for the angle of reflection: 30°, 60°, 90°, 120°, 150°.
    Reflect the ray's direction in the mirror (y = 0) and measure the angle from the normal (0, 1)."""
    a = sp.pi / 6  # 30° between the ray and the mirror surface
    d_in = sp.Matrix([sp.cos(a), -sp.sin(a)])  # heading down onto the mirror
    d_out = sp.Matrix([d_in[0], -d_in[1]])  # mirror flips the normal component
    n = sp.Matrix([0, 1])
    refl = sp.acos(d_out.dot(n) / d_out.norm())  # angle between reflected ray and the normal
    deg = sp.nsimplify(sp.simplify(refl * 180 / sp.pi))
    return [deg == o for o in (30, 60, 90, 120, 150)]


def dl_statements(item: dict) -> list[bool]:
    """q3: Doppler statements for sound in still air (v = 340 m/s, source f = 500 Hz, speeds 20 m/s).
    (1) source approaching a still listener: heard f higher; (2) listener walking towards a still source:
    heard f higher; (3) source moving away: the wavelength reaching the listener is shorter;
    (4) the Doppler effect changes the frequency the source itself emits; (5) source and listener moving
    the same way at the same speed (no relative motion): heard f higher."""
    f, v, u = R(500), R(340), R(20)
    T = 1 / f
    s1 = 1 / _observed_period(T, v, u, 0) > f
    s2 = 1 / _observed_period(T, v, 0, -u) > f  # observer velocity −u = moving towards the source
    lam_rest = v * T
    lam_behind = _wavelength_ahead(T, v, -u)  # the listener is behind a receding source
    s3 = lam_behind < lam_rest
    s4 = False  # in the model the emission interval is T whatever the motion: the source's f is unchanged
    s5 = 1 / _observed_period(T, v, u, u) > f  # both move +x at u: source chases, observer recedes
    return [s1, s2, s3, s4, s5]


def rf_air_to_water(item: dict) -> list[bool]:
    """q4: light from air into water, slower in water (v_water = 3/4 v_air, stated qualitatively).
    (1) frequency unchanged; (2) wavelength shorter; (3) speed larger; (4) an oblique ray bends towards
    the normal; (5) at normal incidence the wavelength in water is unchanged."""
    c = R(3) * 10**8
    v1, v2 = c, R(3, 4) * c
    f1 = R(6) * 10**14  # any visible-light frequency; the source sets it
    f2 = f1  # the frequency is set by the source, so it is the same on both sides of the boundary
    lam1, lam2 = v1 / f1, v2 / f2
    # diagram method: distances from the normal on a circle round the point of incidence scale as speed
    d1 = R(3)
    d2 = d1 * v2 / v1
    return [f2 == f1, lam2 < lam1, v2 > v1, d2 < d1, lam2 == lam1]  # (5): λ = v/f does not involve the angle


def rf_snell_diagram(item: dict) -> list[bool]:
    """q5: air → glass with v_air : v_glass = 3 : 2. On a circle of radius 10 squares round the point of
    incidence, the incident ray crosses 6 squares from the normal. Options for the refracted ray: 2, 3, 4, 6, 9."""
    r = R(10)
    d1 = R(6)
    v1, v2 = R(3), R(2)
    # the crossing points sit at r·(distance-to-normal ratio); the ratio d1 : d2 equals v1 : v2
    d2 = d1 * v2 / v1
    assert 0 < d2 <= r
    # cross-check with the incident and refracted directions (sin θ = d / r): sin θ1 / sin θ2 = v1 / v2
    assert sp.simplify((d1 / r) / (d2 / r) - v1 / v2) == 0
    return [d2 == o for o in (2, 3, 4, 6, 9)]


# ---------------------------------------------------------------- particle vs wave evidence

# phenomenon -> (Newton's corpuscular prediction, wave-theory prediction, what is observed).
# Sources: nat.json PKa-Ⅴc-3 (corpuscular vs wave, qualitative), PKa-Ⅴc-4 (refraction from different wave
# speeds), PKa-Ⅴc-5 (interference, diffraction, double-slit demonstration); standard history of optics
# (the corpuscular account of refraction needs light to speed up in water; measurement found it slower).
EVIDENCE = {
    "double_slit": ("two bright bands", "alternating bright and dark fringes", "alternating bright and dark fringes"),
    "speed_in_water": ("faster than in air", "slower than in air", "slower than in air"),
    "reflection_law": ("equal angles", "equal angles", "equal angles"),
    "straight_line": ("straight", "straight", "straight"),
    "narrow_slit": ("sharp shadow", "spreads into the shadow", "spreads into the shadow"),
}


def lt_wave_evidence(item: dict) -> list[bool]:
    """q6: which observations support the wave theory AND differ from Newton's corpuscular prediction?
    Options: double-slit fringes; speed in water; reflection law; straight-line travel; spreading past a narrow slit."""
    order = ["double_slit", "speed_in_water", "reflection_law", "straight_line", "narrow_slit"]
    out = []
    for k in order:
        particle, wave, seen = EVIDENCE[k]
        out.append(wave == seen and particle != seen)
    return out


def df_most_spreading(item: dict) -> list[bool]:
    """q7: water waves through a gap; which (wavelength, gap width) in cm diffracts most noticeably?
    Rule (Huygens): the spreading grows as the wavelength becomes large compared with the gap, so the
    largest λ / a wins."""
    opts = [(R(1), R(4)), (R(2), R(10)), (R(3, 2), R(3, 2)), (R(1, 2), R(3)), (R(2), R(3))]
    ratios = [lam / a for lam, a in opts]
    best = max(ratios)
    assert ratios.count(best) == 1
    return [q == best for q in ratios]


# person / event -> fact. Sources: nat.json PKa-Ⅴc-3, PKa-Ⅴc-5 keyConcepts and research physics
# pedagogy_notes ("corpuscle vs wave → Maxwell → photon"); the attributions are standard history of physics:
# Newton favoured corpuscles (Opticks), Huygens proposed the wave picture and his principle, Young's
# double-slit interference supported waves, the Doppler effect is named after the Austrian physicist
# Christian Doppler, Foucault (France, mid-19th century) found light slower in water than in air.
HISTORY = {
    "newton_theory": "corpuscular",
    "huygens_theory": "wave",
    "young_double_slit_supports": "wave",
    "doppler_effect_proposed_by": "Doppler",
    "foucault_light_in_water": "slower",
}


def hs_light_debate(item: dict) -> list[bool]:
    """q8: which statement is correct? (1) Newton favoured the corpuscular theory; (2) Huygens favoured the
    corpuscular theory; (3) Young's double slit supported the corpuscular theory; (4) the Doppler effect was
    proposed by Snell; (5) Foucault found light faster in water than in air."""
    return [
        HISTORY["newton_theory"] == "corpuscular",
        HISTORY["huygens_theory"] == "corpuscular",
        HISTORY["young_double_slit_supports"] == "corpuscular",
        HISTORY["doppler_effect_proposed_by"] == "Snell",
        HISTORY["foucault_light_in_water"] == "faster",
    ]
