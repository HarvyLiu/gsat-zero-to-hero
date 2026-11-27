"""Checks for the cross-subject sets (q40-q43 biology + chemistry, q50-q53 earth + physics) and the
q-turn pacing item of src/data/items/inquiry/s116-sci-mock.yaml.

Each function recomputes its item's key from the numbers or the design stated in the stem (exact
Rationals) or from an encoded rule list; none reads item["answer"]. Every rule names the reviewed
sprint chapter (src/content/lessons/zh-tw/<subject>/<slug>.mdx) it comes from. All contexts and
numbers are original; the data in the stems are labelled illustrative.
"""

from __future__ import annotations

import sympy as sp

R = sp.Rational


# ---------- q-turn: pacing the 110 minutes ----------
# source: src/data/registry/exam/papers.json id "science": minutes 110, Part 1 items 1-36.
def x_turn_pacing(item: dict) -> list[bool]:
    """q-turn: 110 minutes, 36 Part 1 items at 1.5 minutes each. Options: 36, 54, 56, 64, 74."""
    left = 110 - 36 * R(3, 2)
    return [left == o for o in (36, 54, 56, 64, 74)]


# ---------- q40-q43: waterweed and bromothymol blue (biology + chemistry) ----------
# The stated design: what is changed in each tube, and the measured pH after 3 h (illustrative).
TUBES = {
    # tube: (waterweed present, light), pH at start, pH after 3 h
    "A": {"weed": True, "light": True, "ph0": R(7), "ph": R(9)},
    "B": {"weed": True, "light": False, "ph0": R(7), "ph": R(58, 10)},
    "C": {"weed": False, "light": True, "ph0": R(7), "ph": R(7)},
    "D": {"weed": False, "light": False, "ph0": R(7), "ph": R(7)},
}
FACTORS = ("weed", "light")

# Bromothymol blue colour bands as given in the stem (chemistry/s116-acids-bases indicator table:
# yellow below about 6.0, green about 6.0-7.6, blue above about 7.6).
BTB = ((R(6), "yellow"), (R(76, 10), "green"), (sp.oo, "blue"))


def _btb_colour(ph) -> str:
    for upper, colour in BTB:
        if ph < upper:
            return colour
    return "blue"


# Facts table:
# - biology/s116-cell-energy: respiration never stops while a cell is alive, by day and by night;
#   photosynthesis needs light and takes up CO2; respiration gives off CO2.
# - chemistry/s116-environment-energy: CO2 + H2O <=> H2CO3, carbonic acid is a WEAK acid (only a
#   small part ionises).
# - chemistry/s116-acids-bases: pH = -log[H+]; a larger [H+] means a lower pH.
FACTS = {
    "respires_in_light": True,
    "respires_in_dark": True,
    "photosynthesis_needs_light": True,
    "carbonic_acid_strong": False,
}


def _differs_only_in(a: str, b: str) -> list[str]:
    """Fair-test rule (inquiry/s116-inq-question-plan, controlled variables: a comparison supports a
    conclusion about one factor only when the two groups differ in that factor alone)."""
    return [f for f in FACTORS if TUBES[a][f] != TUBES[b][f]]


def _change(t: str):
    return TUBES[t]["ph"] - TUBES[t]["ph0"]


def x_tube_h_ratio(item: dict) -> list[bool]:
    """q40: [H+] in tube A after 3 h as a multiple of its start. Options: 100, 2, 7/9, 1/2, 1/100."""
    # the design: all four tubes under the same lamp (B and D foil-wrapped), so the tubes differ only
    # in the two factors of the TUBES table
    assert "和甲、丙放在同一盞燈下" in item["text"]["zh-tw"]["stem"]
    assert "under the same lamp as A and C" in item["text"]["en"]["stem"]
    h0 = sp.Integer(10) ** (-TUBES["A"]["ph0"])
    h1 = sp.Integer(10) ** (-TUBES["A"]["ph"])
    ratio = sp.nsimplify(h1 / h0)
    # consistency: the stated colours follow from the stated pH values
    assert [_btb_colour(TUBES[t]["ph"]) for t in "ABCD"] == ["blue", "yellow", "green", "green"]
    assert _btb_colour(R(7)) == "green"
    return [ratio == o for o in (100, 2, R(7, 9), R(1, 2), R(1, 100))]


def x_tube_conclusions(item: dict) -> list[bool]:
    """q41: (1) A vs C: the change needs the weed; (2) A vs B: light decides the direction;
    (3) B vs C: darkness makes the weed give off CO2; (4) the weed in A did not respire;
    (5) carbonic acid is a strong acid that ionises completely."""
    # (1) A and C differ only in the weed, and their changes differ (C does not change at all)
    diff_ac = _differs_only_in("A", "C")
    s1 = diff_ac == ["weed"] and _change("A") != 0 and _change("C") == 0
    # (2) A and B differ only in the light, and the pH moves in opposite directions
    diff_ab = _differs_only_in("A", "B")
    s2 = diff_ab == ["light"] and sp.sign(_change("A")) == -sp.sign(_change("B")) != 0
    # (3) B and C differ in two factors, so no single-factor conclusion is supported
    s3 = len(_differs_only_in("B", "C")) == 1
    # (4) contradicts the facts table: respiration goes on in the light
    s4 = not FACTS["respires_in_light"]
    # (5) contradicts the facts table: carbonic acid is weak
    s5 = FACTS["carbonic_acid_strong"]
    return [bool(s1), bool(s2), bool(s3), bool(s4), bool(s5)]


def x_mixed_tube_colours(item: dict) -> bool:
    """q42: the model answer's chain. B (dark): no photosynthesis, respiration adds CO2, more H2CO3,
    [H+] up, pH 7.0 -> 5.8 < 6.0, yellow. A (light): net CO2 uptake, less H2CO3, [H+] down,
    pH 7.0 -> 9.0 > 7.6, blue."""
    b_net_co2 = +1 if (FACTS["respires_in_dark"] and TUBES["B"]["weed"]) else 0  # no light: no uptake
    a_net_co2 = -1  # the stated pH rise means the CO2 (and so the carbonic acid) fell
    h_b_up = sp.Integer(10) ** (-TUBES["B"]["ph"]) > sp.Integer(10) ** (-TUBES["B"]["ph0"])
    h_a_down = sp.Integer(10) ** (-TUBES["A"]["ph"]) < sp.Integer(10) ** (-TUBES["A"]["ph0"])
    return bool(
        FACTS["photosynthesis_needs_light"]
        and not TUBES["B"]["light"]
        and b_net_co2 > 0
        and h_b_up
        and _btb_colour(TUBES["B"]["ph"]) == "yellow"
        and a_net_co2 < 0
        and h_a_down
        and _btb_colour(TUBES["A"]["ph"]) == "blue"
        and not FACTS["carbonic_acid_strong"]
    )


def x_mixed_light_design(item: dict) -> bool:
    """q43: (1) the model's design changes ONE factor (light strength, as lamp distance), measures
    the pH after a fixed time, and holds the rest fixed; (2) one tube per treatment cannot show the
    spread between runs, so the model proposes several tubes per treatment."""
    # source: inquiry/s116-inq-question-plan (one manipulated variable, a measurable responding
    # variable, the other conditions controlled)
    manipulated = {"lamp_distance_cm"}
    responding = {"pH_after_3h"}
    controlled = {"weed_size", "water_source_volume", "indicator_drops", "water_temperature", "time_in_light"}
    distances = [10, 20, 40]
    design_ok = (
        len(manipulated) == 1
        and not (manipulated & controlled)
        and not (responding & controlled)
        and len(controlled) >= 2
        and len(set(distances)) == len(distances)
    )
    # (2) source: inquiry/s116-inq-question-plan, 重複測量 and its StudentAsks: even with conditions kept
    # alike, repeated runs differ a little, and repeating is how you see how large that spread is; a
    # single run (one tube per treatment, as the q40 stem's table has) cannot show it.
    tubes_per_treatment = {t: 1 for t in TUBES}  # the q40 table lists one tube per treatment
    needs_repeats = all(n < 2 for n in tubes_per_treatment.values())
    proposed = 3  # the model answer's tubes per treatment
    model = item["model"]["zh-tw"]
    repeat_ok = needs_repeats and proposed >= 2 and f"${proposed}$ 支試管" in model
    return bool(design_ok and repeat_ok)


# ---------- q50-q53: seismic stations (earth + physics) ----------
# Stated table (illustrative): distance to focus (km), P and S arrival clock readings (s).
STATIONS = {
    "A": (R(36), R(8), R(12)),
    "B": (R(54), R(11), R(17)),
    "C": (R(90), R(17), R(27)),
}


def _speed(wave: int):
    """Speed from the extra distance over the extra time between stations (all pairs must agree).
    source: physics/s116-scales-units (speed = distance / time) and earth/s116-plate-boundaries-taiwan
    (arrival time grows linearly with distance, straight lines from the origin of a travel-time graph)."""
    names = list(STATIONS)
    speeds = set()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d1, *t1 = STATIONS[names[i]]
            d2, *t2 = STATIONS[names[j]]
            speeds.add((d2 - d1) / (t2[wave] - t1[wave]))
    assert len(speeds) == 1, speeds
    return speeds.pop()


V_P = _speed(0)
V_S = _speed(1)


def _origin_time():
    """Clock reading of the earthquake; P and S must give the same answer at every station."""
    times = {t - d / v for d, tp, ts in STATIONS.values() for t, v in ((tp, V_P), (ts, V_S))}
    assert len(times) == 1, times
    return times.pop()


T0 = _origin_time()

# Facts table:
# - earth/s116-earth-layers-plates: P waves are longitudinal and faster; S waves are transverse and
#   slower; S waves cannot pass through a liquid (outer core liquid); P and S both speed up from
#   crust into mantle (illustrative 35 km boundary).
# - physics/s116-waves-light: frequency is set by the source and unchanged in a new medium; wave
#   speed is set by the medium (in one medium a higher frequency means a shorter wavelength, same
#   speed); a wave entering a faster medium bends away from the normal; v = f * lambda.
WAVE_FACTS = {
    "P_kind": "longitudinal",
    "S_kind": "transverse",
    "S_through_liquid": False,
    "speed_set_by_frequency_in_one_medium": False,
    "frequency_changes_in_new_medium": False,
}


def x_quake_p_speed(item: dict) -> list[bool]:
    """q50: P speed. Options (km/s): 3.6, 4.5, 5.3, 6.0, 9.0 (5.3 stands for 90/17 = 5.29...)."""
    return [V_P == o for o in (R(36, 10), R(45, 10), R(53, 10), R(6), R(9))]


def x_quake_statements(item: dict) -> list[bool]:
    """q51: (1) quake at clock 2.0 s; (2) P transverse, S longitudinal; (3) S at B at the same
    reading as P at C; (4) P and S speeds differ because of frequency; (5) S crosses a liquid."""
    s1 = T0 == 2
    s2 = WAVE_FACTS["P_kind"] == "transverse" and WAVE_FACTS["S_kind"] == "longitudinal"
    s3 = STATIONS["B"][2] == STATIONS["C"][1]
    s4 = WAVE_FACTS["speed_set_by_frequency_in_one_medium"]
    s5 = WAVE_FACTS["S_through_liquid"]
    return [bool(s1), bool(s2), bool(s3), bool(s4), bool(s5)]


def x_mixed_quake_distance_warning(item: dict) -> bool:
    """q52: S-P difference 14.0 s -> d = 126 km; alert at clock 12.0 s -> S at 37.0 s, 25.0 s."""
    d = sp.symbols("d", positive=True)
    (dist,) = sp.solve(sp.Eq(d / V_S - d / V_P, 14), d)
    s_arrival = T0 + dist / V_S
    warning = s_arrival - 12
    # the model's check: station A's own difference equals 36/9
    a_diff = STATIONS["A"][2] - STATIONS["A"][1]
    return bool(
        V_P == 6
        and V_S == R(36, 10)
        and 1 / V_S - 1 / V_P == R(1, 9)
        and dist == 126
        and dist / V_S == 35
        and s_arrival == 37
        and warning == 25
        and a_diff == STATIONS["A"][0] / 9
    )


def x_mixed_moho_refraction(item: dict) -> bool:
    """q53: f = 4.0 Hz in both media; lambda 1.5 km (crust) and 2.0 km (mantle); away from the
    normal because the wave enters a faster medium."""
    f = R(4)
    v_crust, v_mantle = R(6), R(8)
    lam_crust = v_crust / f
    lam_mantle = v_mantle / f
    f_mantle = f if not WAVE_FACTS["frequency_changes_in_new_medium"] else None
    bends_away = v_mantle > v_crust  # physics/s116-waves-light: faster medium -> away from normal
    return bool(
        f_mantle == 4
        and lam_crust == R(3, 2)
        and lam_mantle == 2
        and lam_mantle > lam_crust
        and bends_away
        and V_P == v_crust  # the set's table gives the same crustal P speed
    )
