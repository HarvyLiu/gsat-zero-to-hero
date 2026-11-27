"""Checks for src/data/items/inquiry/s116-inq-argue-model.yaml (116 sprint, 探究與實作 論證與建模:
inq:argue-model and its four sub-items, nat:pa-Ⅴc-1/2, tr-Ⅴc-1, tm-Ⅴc-1).

How the keys are recomputed (never from item["answer"]):
- Trends, differences, ratios, correlation signs and model values come from each stem's data table,
  with SymPy exact Rationals.
- Judgements about claims (association vs cause, fair tests, conclusions within the data's scope,
  extrapolation) come from an explicit rule list, RULES, with a source per rule. Each option is
  encoded as a structured claim and judged by those rules.
- Subject facts come from FACTS, each citing the reviewed subject chapter it is taught in.

Subject chapters relied on (grep them for the idea):
- biology/s116-cell-energy: enzymes lose their function when the temperature is too high (page);
  photosynthesis needs light (page, plant context).
- physics/s116-heat-energy-quality: at 1 atm boiling water absorbs heat while staying at 100 ℃
  (page Predict); heat flows from hot to cold until both have the same temperature (q6); the 國中
  relation heat = mass × specific heat × temperature change (page Perspective).
- physics/s116-energy-conservation: near the ground gravitational potential energy is proportional
  to height; mechanical energy is conserved when air resistance is ignored (q3).
- chemistry/s116-rate-and-technology: CaCO3 + 2HCl -> CaCl2 + H2O + CO2; the rate falls as the
  CaCO3 is used up and is zero once it is gone (q4); cutting a cube into n pieces per edge multiplies
  the total area by n, and the initial rate is proportional to the total contact area (q7).
- chemistry/s116-equations-stoichiometry: masses from moles and molar masses (q4).
- math/s116-data-analysis: scatter diagram, correlation coefficient, 「相關不代表因果」.
"""

from __future__ import annotations

import sympy as sp
from sympy import Rational as R

# --- rules for judging claims -------------------------------------------------------------------
# Each rule: id -> (statement, source). The functions below apply them.
RULES = {
    # inq.json inq:argue-model keyConcepts "Infer causes from correlations" (research.units: "Infer
    # possible causes from correlations"); math/s116-data-analysis 「相關不代表因果」.
    "association_only": ("Data from a survey (nothing manipulated) supports an association, and at most a possible cause.",
                         "inq:argue-model; math/s116-data-analysis"),
    # inq.json keyConcepts "variables and controlled conditions", "designing and critiquing experiments"
    # (inq:plan/find-variables is the previous chapter's code for the same idea).
    "fair_test": ("A cause is tested by an experiment that changes only the manipulated variable, holds the others fixed and compares groups.",
                  "inq:argue-model keyConcepts; inq:plan/find-variables"),
    # Same source: more cases of the same uncontrolled design leave the uncontrolled differences in place.
    "more_of_same": ("More cases of the same uncontrolled design do not remove its uncontrolled differences.",
                     "inq:argue-model keyConcepts (variables and controlled conditions)"),
    # math/s116-data-analysis: r measures the direction and closeness to a line, not a cause or a ratio.
    "r_not_cause": ("A correlation coefficient gives direction and strength of a linear association, not a cause or a ratio.",
                    "math/s116-data-analysis (math.correlation-coefficient)"),
    # inq.json keyConcepts "Build models and recognize their limits", "evidence-based claims and model limits".
    "scope": ("A conclusion or prediction is supported only inside the measured range and conditions; a certain claim outside it is not.",
              "inq:argue-model keyConcepts (model limits)"),
    # inq.json keyConcepts "Organize data ...; make charts; find trends and patterns": a claim about the
    # data's direction must match the data.
    "match_data": ("A statement about the data's trend must agree with the data.",
                   "inq:argue-model keyConcepts (find trends and patterns)"),
}

# --- subject facts (each from a reviewed subject chapter) ---------------------------------------
FACTS = {
    "boil_1atm_C": (R(100), "physics/s116-heat-energy-quality: at 1 atm water boils at 100 ℃ and stays there while absorbing heat"),
    "heat_flows_hot_to_cold": (True, "physics/s116-heat-energy-quality: heat flows from hot to cold until both reach the same temperature"),
    "pe_proportional_to_height": (True, "physics/s116-energy-conservation: near the ground, with the ground as zero, PE is proportional to height"),
    "caco3_rate_falls": (True, "chemistry/s116-rate-and-technology: the rate falls as CaCO3 is used up and stops when it is gone"),
    "rate_proportional_to_area": (True, "chemistry/s116-rate-and-technology: initial rate is proportional to total contact area, other conditions equal"),
    "enzyme_fails_when_too_hot": (True, "biology/s116-cell-energy: too high a temperature destroys an enzyme's structure"),
}
MOLAR = {"Ca": R(40), "C": R(12), "O": R(16)}  # stated in the q4 stem


def _diffs(ys):
    return [b - a for a, b in zip(ys, ys[1:])]


def _sxy(xs, ys):
    """Sum of products of deviations: its sign is the sign of the correlation coefficient."""
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys))


def _r(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return _sxy(xs, ys) / sp.sqrt(sxx * syy)


def _line(xs, ys):
    """Exact line through collinear data (equal steps in x and equal differences in y)."""
    slope = (ys[1] - ys[0]) / (xs[1] - xs[0])
    icpt = ys[0] - slope * xs[0]
    assert all(y == icpt + slope * x for x, y in zip(xs, ys)), "data not on one line"
    return slope, icpt


def _judge(claim: dict, design: dict) -> bool:
    """Apply RULES to one structured claim about one design."""
    kind = claim["kind"]
    if kind == "association":  # 'the two quantities are associated' (optionally: other causes possible)
        return design["association_in_data"]  # match_data
    if kind == "no_association":
        return not design["association_in_data"]  # match_data
    if kind == "cause_proven":
        # association_only: a survey cannot prove a cause; fair_test: an experiment can only if fair
        return design["manipulated"] and design["only_one_variable_differs"]
    if kind == "cause_after_more_of_same":
        return False if not design["manipulated"] else design["only_one_variable_differs"]  # more_of_same
    if kind == "nothing_learned":
        return not design["association_in_data"]  # the data do show something
    if kind == "proposed_test":
        # fair_test: investigator changes exactly the variable named, holds the rest, compares groups
        t = claim["test"]
        return t["manipulated"] and t["changed"] == {claim["target"]} and t["compares_groups"]
    if kind == "r_proves_cause":
        return False  # r_not_cause
    raise ValueError(kind)


# --- opening and mid-chapter turns --------------------------------------------------------------

PLANT_SURVEY = {"manipulated": False, "only_one_variable_differs": False, "association_in_data": True}


def am_turn_window_plants(item: dict) -> list[bool]:
    """q-turn: a survey of 12 pots; window pots are generally taller. Options: proven cause; association
    but other differences possible; no relation; 12 more pots prove it; no conclusion at all."""
    claims = [
        {"kind": "cause_proven"},
        {"kind": "association"},
        {"kind": "no_association"},
        {"kind": "cause_after_more_of_same"},
        {"kind": "nothing_learned"},
    ]
    return [_judge(c, PLANT_SURVEY) for c in claims]


def am_turn_confound(item: dict) -> list[bool]:
    """q-confound: window pots get more light AND daily watering. Which next step tests light?
    Options: survey more pots; same pots/water/soil, one group lit, one shaded; r near −1; move window
    pots to the wall and water every two days; measure only the tallest pot."""
    target = "light"
    tests = [
        {"manipulated": False, "changed": {"light", "water"}, "compares_groups": True},  # more survey
        {"manipulated": True, "changed": {"light"}, "compares_groups": True},  # fair test
        None,  # r near -1
        {"manipulated": True, "changed": {"light", "water"}, "compares_groups": True},  # two changes at once
        {"manipulated": False, "changed": set(), "compares_groups": False},  # one pot, no comparison
    ]
    out = []
    for t in tests:
        if t is None:
            out.append(_judge({"kind": "r_proves_cause"}, PLANT_SURVEY))
        else:
            out.append(_judge({"kind": "proposed_test", "target": target, "test": t}, PLANT_SURVEY))
    return out


# --- Check yourself -----------------------------------------------------------------------------


def am_concentration_table(item: dict) -> list[bool]:
    """q1: acid concentration (mol/L) 0.5, 1.0, 1.5, 2.0 vs time to collect 20 mL gas 120, 60, 40, 30 s.
    Options: doubling c halves t; equal decreases per step; positive correlation; at 4.0 mol/L certainly
    15 s; concentration has no effect."""
    c = [R(1, 2), R(1), R(3, 2), R(2)]
    t = [R(120), R(60), R(40), R(30)]
    pairs = [(i, j) for i in range(4) for j in range(4) if c[j] == 2 * c[i]]
    halves = bool(pairs) and all(t[j] == t[i] / 2 for i, j in pairs)
    d = _diffs(t)
    equal_steps = len(set(d)) == 1
    positive = _sxy(c, t) > 0
    certain_outside = R(4) <= max(c)  # 'scope': a certain value outside 0.5–2.0 is not supported
    no_effect = len(set(t)) == 1
    return [halves, equal_steps, positive, certain_outside, no_effect]


def am_jellyfish(item: dict) -> list[bool]:
    """q2: 5 days, sea temperature 24..28 ℃ vs jellyfish counted 12, 15, 14, 20, 22 (a survey).
    Options: positively correlated; data prove temperature causes more jellyfish; a third factor may
    affect both; a lab test changing only temperature can test it; one drop means no relation."""
    temp = [R(24), R(25), R(26), R(27), R(28)]
    count = [R(12), R(15), R(14), R(20), R(22)]
    r = _r(temp, count)
    survey = {"manipulated": False, "only_one_variable_differs": False, "association_in_data": bool(r > R(1, 2))}
    lab = {"manipulated": True, "changed": {"temperature"}, "compares_groups": True}
    one_drop = any(b < a for a, b in zip(count, count[1:]))
    return [
        bool(r > 0),
        _judge({"kind": "cause_proven"}, survey),
        _judge({"kind": "association"}, survey),  # association with other causes possible
        _judge({"kind": "proposed_test", "target": "temperature", "test": lab}, survey),
        one_drop and _judge({"kind": "no_association"}, survey),
    ]


def am_drop_energy(item: dict) -> int:
    """q3: heights 1, 2, 3, 4 m vs kinetic energy at the ground 6, 12, 18, 24 J (air resistance ignored).
    Every measured point satisfies KE = 6 × height (checked point by point by _line); the zero
    intercept agrees with the physics principle (PE ∝ height with the ground as zero) but is not
    itself a measured point. Value at 2.5 m (interpolation)."""
    h = [R(1), R(2), R(3), R(4)]
    k = [R(6), R(12), R(18), R(24)]
    slope, icpt = _line(h, k)
    assert icpt == 0 and FACTS["pe_proportional_to_height"][0]
    x = R(5, 2)
    assert min(h) <= x <= max(h)  # an interpolation, inside the measured range
    v = icpt + slope * x
    assert v.q == 1
    return int(v)


def am_marble_limit(item: dict) -> list[bool]:
    """q4: 10.0 g CaCO3 with plenty of HCl gives 1.32 g CO2 in the first minute; a student's model
    1.32 g/min predicts 13.2 g at 10 min. Options: model right; at most 4.40 g, rate falls, model only
    for the start; rate rises so more than 13.2 g; constant rate because the acid is plentiful;
    26.4 g after 20 min."""
    m_caco3 = MOLAR["Ca"] + MOLAR["C"] + 3 * MOLAR["O"]
    m_co2 = MOLAR["C"] + 2 * MOLAR["O"]
    max_co2 = R(10) / m_caco3 * m_co2  # 1 : 1 in CaCO3 + 2HCl -> CaCl2 + H2O + CO2
    first = R(132, 100)
    model = lambda t: first * t  # noqa: E731
    falls = FACTS["caco3_rate_falls"][0]
    return [
        model(10) <= max_co2,
        max_co2 == R(44, 10) and falls and model(10) > max_co2,
        not falls,
        not falls,
        model(20) <= max_co2,
    ]


def am_germination(item: dict) -> list[bool]:
    """q5: mung beans, 20 per group; NaCl 0 %, 1 %, 2 % -> 18, 14, 6 germinated.
    Options: salt water stops all plant seeds; within 0–2 % higher concentration, lower rate (mung
    beans); at 3 % certainly 10 %; positive correlation; 1 % highest."""
    conc = [R(0), R(1), R(2)]
    rate = [R(n, 20) for n in (18, 14, 6)]
    decreasing = all(b < a for a, b in zip(rate, rate[1:]))
    tested_species = {"mung bean"}
    all_plants_claim = tested_species >= {"mung bean", "other plants"}  # 'scope': only one species tested
    certain_outside = R(3) <= max(conc)  # 'scope'
    positive = _sxy(conc, rate) > 0
    highest_at_1 = max(range(3), key=lambda i: rate[i]) == 1
    return [all_plants_claim, decreasing, certain_outside, positive, highest_at_1]


def am_cooling(item: dict) -> list[bool]:
    """q6: a covered cup of hot water in a 25 ℃ room (the stem says to ignore evaporation),
    0, 2, 4, 6, 8 min -> 80, 64, 52, 43, 37 ℃.
    Options: falls with time; each 2-min drop smaller; a straight line describes it; at 12 min −16 ℃;
    ends near 25 ℃ and not below.
    Evaporation must be excluded for option 5: an open cup in unsaturated air keeps evaporating and can
    settle slightly below room temperature (earth/s116-air-vapour-clouds, the wet-bulb idea)."""
    evaporation_ignored = True  # stated in the stem: 加蓋、忽略蒸發
    t = [R(0), R(2), R(4), R(6), R(8)]
    T = [R(80), R(64), R(52), R(43), R(37)]
    room = R(25)
    d = _diffs(T)
    falls = all(x < 0 for x in d)
    shrinking = all(abs(b) < abs(a) for a, b in zip(d, d[1:]))
    linear = len(set(d)) == 1
    extrapolated = T[0] + d[0] * 6  # 'keep falling 16 ℃ every 2 min' to 12 min
    assert extrapolated == -16
    # heat flows hot -> cold until equal temperatures, so the water cannot fall below the room
    reaches = extrapolated >= room if FACTS["heat_flows_hot_to_cold"][0] else True
    floor_at_room = (FACTS["heat_flows_hot_to_cold"][0] and evaporation_ignored
                     and all(x > room for x in T))
    return [falls, shrinking, linear, reaches, floor_at_room]


def am_mixed_cubes(item: dict) -> bool:
    """q7 (written): a marble cube cut n = 1, 2, 3 pieces per edge, same mass and acid; CO2 in the first
    minute 0.20, 0.40, 0.60 g. The model answer's claims hold: total area is 6L²·n (n times), the CO2
    is also 1 : 2 : 3, so the data agree with 'initial rate ∝ total contact area'."""
    L, n = sp.symbols("L n", positive=True)
    area = sp.simplify(n**3 * 6 * (L / n) ** 2)
    assert sp.simplify(area - 6 * L**2 * n) == 0
    co2 = {1: R(20, 100), 2: R(40, 100), 3: R(60, 100)}
    ratios_area = [sp.simplify(area.subs(n, k) / area.subs(n, 1)) for k in (1, 2, 3)]
    ratios_co2 = [co2[k] / co2[1] for k in (1, 2, 3)]
    return bool(ratios_area == ratios_co2 == [1, 2, 3] and FACTS["rate_proportional_to_area"][0])


# --- page claims (not an item check) ------------------------------------------------------------


def am_page_claims() -> bool:
    """Numbers stated in the chapter text."""
    temp = [R(10), R(20), R(30), R(40), R(50), R(60)]
    rate = [R(3), R(6), R(10), R(13), R(8), R(1)]
    assert _diffs(rate) == [3, 4, 3, -5, -7]
    assert max(range(6), key=lambda i: rate[i]) == 3 and temp[3] == 40
    d = [R(1, 2) * k for k in range(1, 9)]
    h = [R(v) for v in (30, 28, 27, 24, 22, 23, 19, 18)]
    r = _r(d, h)
    assert r < R(-9, 10)  # 'close to −1' in the StudentAsks
    t = [R(k) for k in range(5)]
    T = [R(22), R(34), R(46), R(58), R(70)]
    slope, icpt = _line(t, T)
    assert (slope, icpt) == (12, 22)
    assert icpt + slope * R(5, 2) == 52  # interpolation in the text
    assert icpt + slope * R(3, 2) == 40 and (R(64) - icpt) / slope == R(7, 2)  # TryIt
    assert icpt + slope * 8 == 118  # Predict prompt (the model's value)
    assert icpt + slope * 8 > FACTS["boil_1atm_C"][0]  # Predict answer: the measured water stays at 100 ℃
    assert (FACTS["boil_1atm_C"][0] - icpt) / slope == R(13, 2)
    assert icpt + slope * 8 - FACTS["boil_1atm_C"][0] == 18
    assert icpt + slope / 2 * 4 == 46 and icpt + slope * 4 == 70  # doubled water, t = 4
    return True


assert am_page_claims()
