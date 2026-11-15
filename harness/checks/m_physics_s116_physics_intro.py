"""Checks for src/data/items/physics/s116-physics-intro.yaml (116 sprint: PMc-Ⅴc-3, PMc-Ⅴc-4).

Each function recomputes its item's answer and never reads item["answer"]:
- numeric items with SymPy (exact Rationals and square roots);
- attitude items by encoding the scientific-attitude rules of the 課綱 說明 3-1 as code
  (nat.json, nat:PMc-Vc-3 keyConcepts: rational, objective, curious, avoid hasty conclusions;
  experiment and theory support each other);
- history items against the explicit FACTS table below.
"""

from __future__ import annotations

import sympy as sp

# --- History facts -------------------------------------------------------------------------------
# Only well-established history of physics (who, what, roughly when): the people are on the authoring
# brief's list of safe examples, and PMc-Ⅴc-3 (nat.json keyConcepts) asks for physics history through key
# physicists with experiment and theory supporting each other. No registry entry gives these dates; years are given to the decade where the exact year is not needed.
# kind: "experiment" or "theory"; each story is (first step, second step).
FACTS = {
    # Faraday discovered electromagnetic induction by experiment in 1831 (standard history).
    "faraday_induction": {"who": "Faraday", "kind": "experiment", "decade": 1830},
    # Faraday had little formal schooling and began as a bookbinder's apprentice (standard biography).
    "faraday_formal_university_math": False,
    # Maxwell's theory unifying electricity and magnetism, predicting EM waves: 1860s (standard history).
    "maxwell_theory": {"who": "Maxwell", "kind": "theory", "decade": 1860},
    # Hertz produced and detected EM waves by experiment in the late 1880s (standard history).
    "hertz_waves": {"who": "Hertz", "kind": "experiment", "decade": 1880},
    # Who first predicted EM waves: Maxwell (theory), not Hertz (standard history).
    "first_predicted_em_waves": "Maxwell",
    # Lee and Yang proposed in 1956 that mirror symmetry (parity) may fail in some decays (theory).
    "lee_yang_parity": {"who": "Lee, Yang", "kind": "theory", "decade": 1950},
    # Wu led the experiment (1956–57) that confirmed the prediction (standard history).
    "wu_experiment": {"who": "Wu", "kind": "experiment", "decade": 1950},
    # Hahn and Strassmann (late 1938) found barium after bombarding uranium with neutrons (experiment).
    "hahn_strassmann_barium": {"who": "Hahn, Strassmann", "kind": "experiment", "decade": 1930},
    # Meitner and Frisch (early 1939) explained it as the nucleus splitting: fission (theory).
    "meitner_frisch_fission": {"who": "Meitner, Frisch", "kind": "theory", "decade": 1930},
    # Black-body radiation had been measured before Planck's 1900 quantum hypothesis explained it.
    "blackbody_measurements": {"who": "experimenters", "kind": "experiment", "decade": 1890},
    "planck_quantum": {"who": "Planck", "kind": "theory", "decade": 1900},
    # Marie Curie: first woman to receive a Nobel Prize (1903, physics) and Nobel in chemistry 1911.
    "curie_first_woman_nobel": True,
    "curie_nobel_fields": {"physics", "chemistry"},
    # Meitner is known for the explanation of nuclear fission, not for electromagnetic induction.
    "meitner_known_for": "fission",
    "induction_discovered_by": "Faraday",
}

STORIES = {
    "faraday_maxwell": ("faraday_induction", "maxwell_theory"),
    "maxwell_hertz": ("maxwell_theory", "hertz_waves"),
    "leeyang_wu": ("lee_yang_parity", "wu_experiment"),
    "hahn_meitner": ("hahn_strassmann_barium", "meitner_frisch_fission"),
    "blackbody_planck": ("blackbody_measurements", "planck_quantum"),
}


def _experiment_first(story: str) -> bool:
    first, second = (FACTS[k] for k in STORIES[story])
    assert first["decade"] <= second["decade"], story  # the table itself must be in time order
    return first["kind"] == "experiment" and second["kind"] == "theory"


# --- Attitude rules (課綱 說明 3-1) ----------------------------------------------------------------
def _sound_response(r: dict) -> bool:
    """A response is scientific when it settles the claim by new evidence on the variable the claim is
    about, keeps every recorded result, and rests on neither authority nor intuition alone."""
    return (
        r.get("new_evidence_on_claim", False)
        and not r.get("alters_or_hides_data", False)
        and not r.get("appeals_to_authority", False)
        and not r.get("trusts_intuition_or_form_only", False)
    )


def it_turn_hasty_line(item: dict) -> list[bool]:
    """q-turn: a straight line drawn through two pendulum measurements, extrapolated to L = 4.00 m.
    Options: (1) two points always make a line, so it is right; (2) measure more lengths and see if the
    data stay on one line; (3) redo the same two lengths with a heavier bob; (4) intuitive, no check;
    (5) right if the teacher says so."""
    responses = [
        {"trusts_intuition_or_form_only": True},
        {"new_evidence_on_claim": True},  # new lengths: tests the claim about L
        {"new_evidence_on_claim": False},  # changes mass, not L: the claim about L = 4 m stays untested
        {"trusts_intuition_or_form_only": True},
        {"appeals_to_authority": True},
    ]
    # the numbers behind the claim: the line through (0.25, 1) and (1, 2) does give 6 s at 4 m,
    # while T = 2√L (which fits these data) gives 4 s, so the extra data really would decide it
    L = sp.Symbol("L")
    line = sp.interpolate([(sp.Rational(1, 4), 1), (1, 2)], L)
    assert line.subs(L, 4) == 6 and 2 * sp.sqrt(4) == 4
    return [_sound_response(r) for r in responses]


def it_objective_outlier(item: dict) -> list[bool]:
    """q1: one data point does not follow the trend; the objective way to handle it."""
    responses = [
        {"alters_or_hides_data": True},  # delete it
        {"alters_or_hides_data": True},  # change it to the expected value
        {"new_evidence_on_claim": True},  # keep and record it, check the procedure, re-measure
        {"alters_or_hides_data": True},  # report only the matching data
        {"trusts_intuition_or_form_only": True},  # blame the instrument without checking
    ]
    return [_sound_response(r) for r in responses]


def it_extrapolate_vs_pattern(item: dict) -> tuple:
    """q2: data (1, 3), (4, 6), (9, 9). Straight line through the first two, evaluated at x = 16;
    then the common pattern y = k√x of all three, evaluated at x = 16."""
    x = sp.Symbol("x")
    data = [(1, 3), (4, 6), (9, 9)]
    line = sp.interpolate(data[:2], x)
    y_line = line.subs(x, 16)
    ks = {sp.Rational(yv) / sp.sqrt(xv) for xv, yv in data}
    assert len(ks) == 1, "the three data points must share one k in y = k√x"
    (k,) = ks
    y_pattern = k * sp.sqrt(16)
    assert y_line.is_Integer and y_pattern.is_Integer
    return (sp.Integer(y_line), sp.Integer(y_pattern))


def it_experiment_first(item: dict) -> list[bool]:
    """q3: which stories went experiment first, then theory?
    Options: Faraday→Maxwell, Maxwell→Hertz, Lee–Yang→Wu, Hahn–Strassmann→Meitner–Frisch,
    black-body measurements→Planck."""
    order = ["faraday_maxwell", "maxwell_hertz", "leeyang_wu", "hahn_meitner", "blackbody_planck"]
    return [_experiment_first(s) for s in order]


def it_physicist_facts(item: dict) -> list[bool]:
    """q4: statements about physicists, checked against FACTS.
    (1) Wu proposed the theory and Lee–Yang did the experiment; (2) Marie Curie was the first woman
    Nobel laureate and won in physics and chemistry; (3) Hertz first predicted EM waves by theory;
    (4) Meitner is known for discovering EM induction; (5) Faraday had full university mathematical
    training and was known for mathematical theory."""
    s1 = FACTS["wu_experiment"]["kind"] == "theory" and FACTS["lee_yang_parity"]["kind"] == "experiment"
    s2 = FACTS["curie_first_woman_nobel"] and FACTS["curie_nobel_fields"] == {"physics", "chemistry"}
    s3 = FACTS["first_predicted_em_waves"] == "Hertz"
    s4 = FACTS["meitner_known_for"] == "induction" or FACTS["induction_discovered_by"] == "Meitner"
    s5 = FACTS["faraday_formal_university_math"]
    return [bool(s1), bool(s2), bool(s3), bool(s4), bool(s5)]


def it_control_variables(item: dict) -> list[bool]:
    """q5: to test whether the bob's mass affects the period, pick the pair of trials that differ in
    mass and in nothing else. Trials (length m, mass g, angle °): 甲 (0.5, 50, 5), 乙 (0.5, 100, 5),
    丙 (1.0, 100, 5), 丁 (1.0, 50, 10). Options: 甲乙, 乙丙, 甲丙, 甲丁, 丙丁."""
    trials = {
        "甲": (sp.Rational(1, 2), 50, 5),
        "乙": (sp.Rational(1, 2), 100, 5),
        "丙": (sp.Integer(1), 100, 5),
        "丁": (sp.Integer(1), 50, 10),
    }
    MASS = 1

    def only_mass_differs(a: str, b: str) -> bool:
        diff = [i for i in range(3) if trials[a][i] != trials[b][i]]
        return diff == [MASS]

    return [only_mass_differs(a, b) for a, b in (("甲", "乙"), ("乙", "丙"), ("甲", "丙"), ("甲", "丁"), ("丙", "丁"))]


def it_scientific_practices(item: dict) -> list[bool]:
    """q6: which practices fit the scientific attitude and method?
    (1) publish methods and data so others can repeat the test; (2) announce a new law after one trial;
    (3) take reliable new results that conflict with a theory seriously enough to revise it;
    (4) stay curious about everyday phenomena and ask testable questions;
    (5) skip testing because a famous scientist proposed the theory."""
    practices = [
        {"open_to_checking": True},
        {"hasty_conclusion": True},
        {"evidence_over_theory": True},
        {"curious_testable": True},
        {"appeals_to_authority": True},
    ]

    def fits(p: dict) -> bool:
        good = p.get("open_to_checking") or p.get("evidence_over_theory") or p.get("curious_testable")
        bad = p.get("hasty_conclusion") or p.get("appeals_to_authority")
        return bool(good) and not bad

    return [fits(p) for p in practices]
