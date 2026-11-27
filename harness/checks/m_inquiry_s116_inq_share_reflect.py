"""Checks for src/data/items/inquiry/s116-inq-share-reflect.yaml (116 sprint: 表達與分享 — 表達與溝通,
合作與討論, 評價與省思; inq:share/*, nat:pc/tc/ah/an-Ⅴc).

How the keys are recomputed (never from item["answer"]):
- Each stem's design is written out as an explicit table (what is changed, what is measured, what is held
  fixed, how many trials), and the critique rules below are applied to that table.
- Spreads, model predictions and differences use SymPy exact Rationals from the stem's data.
- Statements, claims and actions are tables of features; a rule list (each rule with its source) decides
  which option is correct. Justification lengths are counted from the item's own zh option strings.

Rule sources:
- inq.json inq:share keyConcepts: "Present results with correct terms, symbols and models"; "Critique others'
  processes and models and propose improvements"; "Judge the credibility of information; value
  reproducibility; science is one explanation, not the only one"; "variables and controlled conditions";
  "evidence-based claims and model limits".
- Variables (one manipulated variable, a measurable responding variable, controlled variables held fixed):
  the 發現問題與規劃研究 chapter (inquiry/s116-inq-question-plan) and the slice's 113 Q43 note.
- Short written reasons (problem + consequence, within the word limit): earth/s116-earth-data-items
  (限字說明) and chemistry/s116-chem-written-items (條件、規則、結論); the 20-character limit is 115 Q54's.
- History of science: chemistry/s116-laws-atomic-theory (Dalton's indivisible atom revised).
"""

from __future__ import annotations

from sympy import Rational as R

# --- shared rules ---------------------------------------------------------------------------------------


def _fair_test_problems(design: dict) -> set[str]:
    """Problems found by the chapter's critique checklist.
    - 'extra-variable': a condition other than the manipulated one differs between groups (inq:share
      'variables and controlled conditions'; question-plan chapter: only one manipulated variable).
    - 'no-repeat': one sample and one trial per condition (inq:share 'value reproducibility').
    - 'not-measurable': the responding variable is judged by eye, not a measured quantity (inq:share
      'present results with correct terms'; 113 Q43 note: variables are physical quantities).
    """
    problems = set()
    groups = design["groups"]
    keys = set().union(*(g.keys() for g in groups))
    for k in keys - {design["manipulated"]}:
        if len({str(g.get(k)) for g in groups}) > 1:
            problems.add("extra-variable")
    if design["samples_per_group"] * design["trials"] <= 1:
        problems.add("no-repeat")
    if not design["responding_measurable"]:
        problems.add("not-measurable")
    return problems


def _held_fixed(design: dict) -> set[str]:
    groups = design["groups"]
    keys = set().union(*(g.keys() for g in groups)) - {design["manipulated"]}
    return {k for k in keys if len({str(g.get(k)) for g in groups}) == 1}


# --- opening turn: which conclusion can a reader check -------------------------------------------------

SUGAR = {20: 120, 40: 80, 60: 40}  # water temperature (℃) -> time to dissolve (s), from the stem


def sr_turn_conclusion(item: dict) -> list[bool]:
    """q-turn: a good conclusion names the changed quantity with its unit and values, names the measured
    quantity as a measurable quantity with its unit, and claims nothing beyond the data (range, other
    factors, advice). Option features are coded below; option 3's numbers are checked against the data."""
    t_lo, t_hi = min(SUGAR), max(SUGAR)
    opt3_numbers = {"T": (20, 60), "t": (120, 40)}
    assert opt3_numbers["T"] == (t_lo, t_hi) and opt3_numbers["t"] == (SUGAR[t_lo], SUGAR[t_hi])
    options = [
        # manipulated as quantity+unit, responding as measurable quantity+unit, claims beyond data
        {"manip_unit": False, "resp_measurable": False, "beyond": False},  # 溫度越高，方糖越好溶
        {"manip_unit": False, "resp_measurable": False, "beyond": True},   # ... 泡茶一定要用熱水
        {"manip_unit": True, "resp_measurable": True, "beyond": False},    # 20→60℃, 120→40 s
        {"manip_unit": False, "resp_measurable": False, "beyond": True},   # 唯一因素 (no other factor tested)
        {"manip_unit": False, "resp_measurable": False, "beyond": False},  # 溶得很快，實驗成功
    ]
    return [o["manip_unit"] and o["resp_measurable"] and not o["beyond"] for o in options]


# --- mid-chapter turn: two groups disagree -------------------------------------------------------------


def _acceptable_response(a: dict) -> bool:
    """When results disagree: keep every datum unless a cause is found (evidence-based claims), look for
    the differing condition (variables and controlled conditions), and test by repeating under the same
    conditions (value reproducibility). Hiding the gap (averaging) or settling it socially fails."""
    return a["keeps_data"] and a["seeks_cause"] and a["repeats"] and not a["hides_gap"]


def sr_turn_disagree(item: dict) -> list[bool]:
    """q-disagree: options average; compare and repeat; keep A only; vote; reject B."""
    a, b = 40, 70
    assert abs(b - a) == 30 and R(a + b, 2) == 55  # option 1's 55 s is the mean
    actions = [
        {"keeps_data": True, "seeks_cause": False, "repeats": False, "hides_gap": True},
        {"keeps_data": True, "seeks_cause": True, "repeats": True, "hides_gap": False},
        {"keeps_data": False, "seeks_cause": False, "repeats": False, "hides_gap": True},
        {"keeps_data": True, "seeks_cause": False, "repeats": False, "hides_gap": False},
        {"keeps_data": False, "seeks_cause": False, "repeats": False, "hides_gap": True},
    ]
    return [_acceptable_response(x) for x in actions]


# --- quiz -----------------------------------------------------------------------------------------------


def sr_table_header(item: dict) -> list[bool]:
    """q1 (pendulum length vs time for 10 swings): a column heading must name a measurable quantity AND
    give its unit, for both columns."""
    headers = [
        [("長度", "vague", None), ("擺多快", "vague", None)],
        [("擺長", "quantity", "cm"), ("擺動10次的時間", "quantity", "s")],
        [("擺長", "quantity", None), ("擺動10次的時間", "quantity", None)],
        [("擺長", "quantity", "cm"), ("擺得順不順", "judgement", None)],
        [(None, None, "cm"), (None, None, "s")],
    ]
    return [all(kind == "quantity" and unit is not None for _, kind, unit in cols) for cols in headers]


TOWEL = {
    "manipulated": "kind",
    "groups": [
        {"kind": "甲", "area_cm2": R(10) * 10, "basin": "same", "soak_s": 10},
        {"kind": "乙", "area_cm2": R(5) * 5, "basin": "same", "soak_s": 10},
    ],
    "samples_per_group": 1,
    "trials": 1,
    "responding_measurable": False,  # 看哪一張比較濕
}


def sr_towel_critique(item: dict) -> list[bool]:
    """q2: apply the checklist to the towel design. Options: area differs; only once; 'wetter' not
    measurable; basin/time should differ; no problems."""
    p = _fair_test_problems(TOWEL)
    fixed = _held_fixed(TOWEL)
    opt4 = not ({"basin", "soak_s"} <= fixed)  # true only if these should NOT be held fixed
    return ["extra-variable" in p, "no-repeat" in p, "not-measurable" in p, opt4, not p]


MELTING = {"甲": [52, 55, 58], "乙": [47, 55, 63], "丙": [54, 55, 56]}  # minutes for a 20 g ice cube, from the stem


def sr_cooling_spread(item: dict) -> int:
    """q3: all three means are 55 min (as the stem says); return the largest range (max − min)."""
    assert all(R(sum(v), len(v)) == 55 for v in MELTING.values())
    return max(max(v) - min(v) for v in MELTING.values())


def _credible(c: dict) -> bool:
    """The chapter's four questions for a claim (inq:share 'judging how reliable a source is',
    'evidence-based claims', 'variables and controlled conditions', 'value reproducibility')."""
    return c["method"] and c["data"] and c["fair"] and c["reproduced"]


def sr_grow_light_claims(item: dict) -> list[bool]:
    """q4: claims about a plant lamp. Option 3 has two groups of 20 differing only in the lamp, a
    measured mean difference, and a repeat by another class; option 4 has one sprout and no comparison."""
    claims = [
        {"method": False, "data": False, "fair": False, "reproduced": False},
        {"method": False, "data": False, "fair": False, "reproduced": False},
        {"method": True, "data": True, "fair": True, "reproduced": True},
        {"method": True, "data": True, "fair": False, "reproduced": False},
        {"method": False, "data": False, "fair": False, "reproduced": False},
    ]
    return [_credible(c) for c in claims]


CORD = {50: 2, 100: 4, 150: 6}  # g -> cm, from the stem
K = R(4, 100)  # the student's model x = 0.04 m


def sr_cord_model(item: dict) -> list[bool]:
    """q5: the model fits every original point exactly; at 400 g it predicts 16 cm against 11 cm measured.
    A model that fails outside its tested range is kept within that range and revised with more data;
    discarding data (new or old) to fit a model, or rejecting the model outright, is not acceptable
    (inq:share 'evidence-based claims and model limits'; the chapter's sugar-cube model)."""
    fits_in_range = all(K * m == x for m, x in CORD.items())
    pred, meas = K * 400, 11
    gap = pred - meas
    assert pred == 16 and gap == 5  # option 1's stated 5 cm
    outside_fails = gap != 0 and 400 > max(CORD)
    responses = [
        {"keeps_new": False, "keeps_old": True, "states_range": False, "more_data": False, "keeps_model": True},
        {"keeps_new": True, "keeps_old": True, "states_range": True, "more_data": True, "keeps_model": True},
        {"keeps_new": False, "keeps_old": True, "states_range": False, "more_data": False, "keeps_model": True},
        {"keeps_new": True, "keeps_old": False, "states_range": False, "more_data": False, "keeps_model": False},
        {"keeps_new": True, "keeps_old": True, "states_range": False, "more_data": False, "keeps_model": False},
    ]

    def ok(r: dict) -> bool:
        return (fits_in_range and outside_fails and r["keeps_new"] and r["keeps_old"]
                and r["states_range"] and r["more_data"] and r["keeps_model"])

    return [ok(r) for r in responses]


# Rules about scientific explanations, each with its source. A statement asserts one feature with a
# value; it is true exactly when its value matches the rule.
NOS_RULES = {
    # inq:share keyConcepts and the spec's objective for this chapter: explanations are tested against new
    # evidence and revised when needed; no amount of support makes one final.
    "revisable_by_new_evidence": True,
    # inq:share keyConcepts: "science is one explanation, not the only one".
    "only_explanation": False,
    # inq:share "evidence-based claims and model limits": data are not discarded to protect a model.
    "discard_new_data_to_keep_model": False,
}
# Historical facts, each from the reviewed subject chapter that teaches it.
NOS_FACTS = {
    # chemistry/s116-laws-atomic-theory: atoms were found to contain a nucleus and electrons, so Dalton's
    # 'atoms cannot be divided' was revised.
    "dalton_indivisible_revised": True,
}
NOS_STATEMENTS = [
    ("revisable_by_new_evidence", True),        # 可以被新的證據檢驗，必要時加以修正
    ("revisable_by_new_evidence", False),       # 被幾次實驗支持，就永遠不會再改變
    ("dalton_indivisible_revised", True),       # 「原子不能再分割」後來被修正
    ("only_explanation", False),                # 一種解釋，不是唯一的解釋
    ("discard_new_data_to_keep_model", True),   # 應該優先刪掉新數據，以保住模型
]


def sr_nature_of_science(item: dict) -> list[bool]:
    """q6: judge each statement by the sourced rule or fact it asserts."""
    table = {**NOS_RULES, **NOS_FACTS}
    return [table[feature] == value for feature, value in NOS_STATEMENTS]


FERTILISER = {
    "manipulated": "fertiliser",
    "groups": [{"fertiliser": "甲", "place": "窗邊"}, {"fertiliser": "乙", "place": "走廊"}],
    "samples_per_group": 1,
    "trials": 1,
    "responding_measurable": True,  # 株高 is a measured height
}


def sr_fertiliser_reason(item: dict) -> list[bool]:
    """q7: the design cannot decide (the place differs too). A best answer has the right judgement, names a
    problem the checklist actually finds, states its consequence, and is at most 20 characters (115 Q54's
    limit), counted from the item's zh option strings including punctuation."""
    p = _fair_test_problems(FERTILISER)
    can_decide = "extra-variable" not in p
    opts = item["text"]["zh-tw"]["options"]
    features = [
        # (judgement 'can decide?', names a real problem, states the consequence)
        (False, None, False),
        (False, None, False),
        (False, "extra-variable", True),
        (True, None, True),
        (False, "manipulated-itself", False),  # the fertiliser is what is compared, not a flaw
    ]
    return [judge == can_decide and prob in p and cons and len(text) <= 20
            for (judge, prob, cons), text in zip(features, opts)]


COIL = {
    "manipulated": "turns",
    "groups": [{"turns": 50, "battery": "new"}, {"turns": 100, "battery": "old"}],
    "samples_per_group": 1,
    "trials": 1,
    "responding_measurable": False,  # 憑感覺判斷哪一個吸得比較用力
}
COIL_IMPROVED = {
    "manipulated": "turns",
    "groups": [{"turns": n, "battery": "same", "nail": "same", "wire": "same", "clips": "same"}
               for n in (50, 100)],
    "samples_per_group": 1,
    "trials": 3,
    "responding_measurable": True,  # 吸起的迴紋針數（個）
}


def sr_mixed_electromagnet(item: dict) -> bool:
    """q8: the original design shows all three rubric problems (so any two can be named); the model
    answer's improved design has none, and holds at least two controlled variables fixed."""
    before = _fair_test_problems(COIL)
    after = _fair_test_problems(COIL_IMPROVED)
    return bool(before == {"extra-variable", "no-repeat", "not-measurable"} and not after
                and len(_held_fixed(COIL_IMPROVED)) >= 2)
