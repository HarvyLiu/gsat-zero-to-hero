"""Checks for src/data/items/inquiry/s116x-cross-subject-data.yaml (116 sprint, cross-subject data
groups: inq:argue-model/analyse-evidence, inq:argue-model/build-model, inq:share/evaluate-reflect).

How the keys are recomputed (never from item["answer"]):
- Subject facts come from a facts table; each entry names the reviewed subject chapter that teaches it.
  "Which subject does this sub-item need?" is answered from the fact the sub-item's question needs.
- "Which inquiry strand does this sub-item test?" is decided by an encoded verb -> strand rule list
  (source per rule: the key concepts of inq.json's argue-model and share codes, as in the slice).
- Data items recompute differences, ranges and orderings from the stem's table with exact Rationals.
- Model, confounding and fair-test judgements use small encoded rule lists, each with a source comment.
- GSAT statements are checked against the slice's verified exam facts (cited per entry).

The chapter's own worked numbers (the soda 題組) are recomputed at import time, so a change to the
chapter's illustrative data that breaks them fails the harness.
"""

from __future__ import annotations

import re

from sympy import Rational as R

# --- subject facts (each is taught in the named reviewed chapter) --------------------------------
# key -> (statement, source chapter)
FACTS = {
    "heat_hot_to_cold": ("heat flows spontaneously from the hotter body to the colder one until both are"
                         " at the same temperature", "physics/s116-heat-energy-quality"),
    "gas_solubility_falls": ("the solubility of a gas in water gets smaller as the temperature rises"
                             " (unlike most solids)", "chemistry/s116-solutions"),
    "open_container_gas": ("in an open container, gas leaving makes the balance reading fall; total mass"
                           " is still conserved", "chemistry/s116-laws-atomic-theory"),
    "isobars_dense_wind": ("the closer the isobars, the larger the pressure-gradient force and usually the"
                           " stronger the wind", "earth/s116-wind-weather-maps"),
    "faster_change_larger_current": ("the faster the magnetic field through a coil changes, the larger the"
                                     " induced current (qualitative)", "physics/s116-induction"),
    "generator_mech_to_elec": ("a generator turns mechanical energy (a turning turbine) into electrical"
                               " energy", "physics/s116-mass-energy-nuclear"),
    "summer_days_long": ("in the Northern Hemisphere summer days are long and winter days short",
                         "earth/s116-sky-motion"),
    "photosynthesis_needs_light": ("photosynthesis needs light and stores light energy in organic matter",
                                   "biology/s116-cell-energy"),
    "enzyme_temperature": ("enzyme activity depends on temperature (rises to an optimum, then falls)",
                           "biology/s116-cell-energy"),
}
SUBJECT_OF = {key: src.split("/")[0] for key, (_, src) in FACTS.items()}

# Standard fact not in the subject chapters' sources, used only for the control-group turn:
# an open container of water loses mass by evaporation (junior-high level; listed in the report).
WATER_EVAPORATES_FROM_OPEN_CONTAINER = True

# --- strand rules: what a sub-item asks you to do -> inquiry strand sub-item ---------------------
# Sources (slice, registry entries of this chapter's codes and final_units 30/31 key concepts):
#   argue-model: "Organize data ... find trends and patterns" -> 分析資料和呈現證據
#                "Infer causes ... form explanations"        -> 解釋和推理
#                "Build models and recognize their limits"   -> 建立模型
#   share:       "Critique others' processes and models"; "Judge the credibility of information"
#                                                            -> 評價與省思
#   plan-research (confirmed_facts[15] sub-items): 擬定研究計畫
STRAND_OF_TASK = {
    "compute_or_read": "論證與建模－分析資料和呈現證據",
    "explain_why": "論證與建模－解釋和推理",
    "model_or_predict": "論證與建模－建立模型",
    "judge_claim_or_credibility": "表達與分享－評價與省思",
    "design_improvement": "規劃與研究－擬定研究計畫",
}

# --- the chapter's worked 題組 (soda, illustrative data) ------------------------------------------
T_MIN = [R(t) for t in (0, 10, 20, 30, 40, 50, 60)]
SODA_T = [R(t) for t in (5, 13, 18, 21, 23, 24, 24)]          # ℃, room 24 ℃
ROOM = R(24)
SODA_LOSS = [R(x, 10) for x in (0, 13, 22, 27, 31, 34, 36)]  # g, whole opened bottle on the desk
WATER_LOSS = [R(x, 10) for x in (0, 1, 2, 3, 4, 5, 6)]       # g, control: identical opened bottle of plain water
BATH_NET_60 = R(2)  # g, second bottle in a water bath held at 5 ℃, net of its own plain-water bottle
BALANCE_READS_TO = R(1, 10)                                  # g, stated in the item-set setup


def _diffs(ys):
    return [b - a for a, b in zip(ys, ys[1:])]


def _chapter_numbers() -> None:
    rises = _diffs(SODA_T)
    assert rises == [8, 5, 3, 2, 1, 0]                       # 'rises smaller and smaller'
    assert SODA_T[-1] == ROOM and all(t <= ROOM for t in SODA_T)  # heat_hot_to_cold: stops at room
    net = [s - w for s, w in zip(SODA_LOSS, WATER_LOSS)]
    assert net[3] == R(24, 10)                               # sub-item 2: first 30 min, 2.4 g
    per = _diffs(net)
    assert per == [R(12, 10), R(8, 10), R(4, 10), R(3, 10), R(2, 10), R(1, 10)]
    k = sum(per[:3]) / sum(rises[:3])                        # model fitted on 0-30 min
    assert k == R(15, 100)                                   # 0.15 g per ℃
    assert k * 0 == 0                                        # Predict: 5 ℃ bath, no warming -> 0 g
    assert k * sum(rises) == R(285, 100) and net[-1] == 3    # TryIt: 2.85 g predicted vs 3.0 g
    assert net[-1] - BATH_NET_60 == 1                        # warming adds about 1.0 g
    assert per[-1] == BALANCE_READS_TO                       # StudentAsks: 0.1 g, the balance's smallest reading
    ratios = [p / r for p, r in zip(per, rises) if r != 0]
    assert ratios[0] == R(15, 100) and per[-1] > 0 and rises[-1] == 0  # last interval: no warming, gas still out


_chapter_numbers()


# --- opening and mid-chapter turns ---------------------------------------------------------------

def csd_turn_solubility(item: dict) -> list[bool]:
    """q-turn: as the soda warms, what happens to the solubility of carbon dioxide in it?
    Options: larger, like sugar; smaller; unchanged; larger then smaller; depends only on the bottle size."""
    gas_falls = "gas_solubility_falls" in FACTS  # chemistry/s116-solutions: gases are the exception
    return [not gas_falls, gas_falls, False, False, False]


def csd_turn_control(item: dict) -> list[bool]:
    """q-control: the open bottle's reading fell by 3.6 g in an hour. Is all of it escaped CO2?
    Options: yes, only CO2 leaves an open container; no, water evaporates too, so an identical opened bottle of
    plain water is needed to subtract it; no, mass is destroyed as the soda warms; yes, and the bottle
    gets heavier as it warms; no, a balance can only weigh solids."""
    any_gas_or_vapour_lowers_reading = "open_container_gas" in FACTS
    other_loss = WATER_EVAPORATES_FROM_OPEN_CONTAINER and any_gas_or_vapour_lowers_reading
    mass_destroyed = False  # open_container_gas: total mass is conserved
    return [not other_loss, other_loss, mass_destroyed, False, False]


# --- Check yourself: wind turbine (earth/physics), illustrative data ------------------------------
# day -> (spacing of neighbouring isobars, km; mean current, mA)
TURBINE = {"一": (R(400), R(20)), "二": (R(300), R(30)), "三": (R(200), R(60)),
           "四": (R(250), R(40)), "五": (R(100), R(110))}

# q1: (question asked, fact it needs or None for pure data reading, subject the option names)
Q1_PAIRS = [
    ("why closer isobars give stronger wind", "isobars_dense_wind", "earth"),
    ("why stronger wind gives a larger current", "faster_change_larger_current", "physics"),
    ("which day had the largest current", None, "chemistry"),
    ("why closer isobars give stronger wind", "isobars_dense_wind", "biology"),
    ("why stronger wind gives a larger current", "faster_change_larger_current", "earth"),
]


def csd_q1_subject_pairs(item: dict) -> list[bool]:
    """q1: which sub-item -> subject pairings are right? A pairing is right when the subject whose
    reviewed chapter teaches the needed fact is the one named; a pure data-reading sub-item needs no
    subject idea, so naming any subject for it is wrong."""
    return [fact is not None and SUBJECT_OF[fact] == subj for _, fact, subj in Q1_PAIRS]


# What the quoted sub-item's wording asks -> task (the chapter's "the verb decides the skill" rule).
# Checked in order; the first entry whose zh (resp. en) verbs all occur in the quoted sub-item decides.
VERB_TASK = [
    (("能不能證明", "說明你的判斷"), ("Can ", "prove", "Explain your judgement"), "judge_claim_or_credibility"),
    (("提出改進",), ("propose an improve",), "design_improvement"),
    (("建立", "模型"), ("build", "model"), "model_or_predict"),
    (("說明原因",), ("Explain why",), "explain_why"),
    (("算出",), ("work out",), "compute_or_read"),
]


def csd_q2_strand(item: dict) -> list[bool]:
    """q2: which inquiry skill does the quoted sub-item test? The task is read from the quoted sub-item's
    verbs through VERB_TASK (zh and en must agree), then mapped to a strand by STRAND_OF_TASK."""
    zh, en = item["text"]["zh-tw"]["stem"], item["text"]["en"]["stem"]
    qz = zh[zh.index("「") + 1: zh.index("」")]
    qe = en[en.index('"') + 1: en.rindex('"')]
    task_zh = next(t for kz, _, t in VERB_TASK if all(k in qz for k in kz))
    task_en = next(t for _, ke, t in VERB_TASK if all(k in qe for k in ke))
    assert task_zh == task_en, (task_zh, task_en)
    target = STRAND_OF_TASK[task_zh]
    options = item["text"]["zh-tw"]["options"]
    assert len(options) == len(item["text"]["en"]["options"]) and options.count(target) == 1
    return [o == target for o in options]


def csd_q3_current_difference(item: dict) -> int:
    """q3: how many mA larger was the current on the day with the narrowest isobar spacing than on the
    day with the widest spacing?"""
    widest = max(TURBINE.values(), key=lambda v: v[0])
    narrowest = min(TURBINE.values(), key=lambda v: v[0])
    d = narrowest[1] - widest[1]
    assert d.q == 1
    return int(d)


def csd_q4_model_range(item: dict) -> list[bool]:
    """q4: the model 'the smaller the spacing, the larger the current' was built from 100-400 km. Using it
    at 20 km. Rule (inq:argue-model/build-model, key concept 'evidence-based claims and model limits'):
    a model is supported only inside the range of the data it was built from; outside it, a prediction
    needs a measurement, and inside it the model may be used with care.
    Options: 20 km is outside, needs measuring; valid at every spacing; infinite current; extend the
    straight line for an exact value; cannot be used even inside 100-400 km."""
    lo = min(v[0] for v in TURBINE.values())
    hi = max(v[0] for v in TURBINE.values())
    target = R(20)
    outside = not (lo <= target <= hi)
    # the data are not on one straight line, so 'extend the line for an exact value' has no basis
    pts = sorted(TURBINE.values())
    slopes = {(b[1] - a[1]) / (b[0] - a[0]) for a, b in zip(pts, pts[1:])}
    straight = len(slopes) == 1
    # (2) 'must hold at every spacing': a model is never established beyond its data range -> always False.
    # (3) 'infinite current': no evidence anywhere supports it -> False.
    # (4) 'extend the line for an exact value': the points are not on one line here, and even a straight
    #     fit gives no exact value outside the data range -> always False.
    # (5) 'cannot be used even inside the range': inside it the model may be used with care -> False.
    assert not straight
    return [outside, False, False, False, False]


# --- Check yourself: greenhouse vegetables (biology/earth), illustrative data ---------------------
# season -> (day length h, air temperature ℃, dry mass gained per plant in a week g)
GREENHOUSE = {"冬": (R(11), R(16), R(2)), "春": (R(125, 10), R(22), R(35, 10)),
              "夏": (R(135, 10), R(28), R(5))}


def _order(idx):
    return sorted(GREENHOUSE, key=lambda s: GREENHOUSE[s][idx])


def csd_q5_confounded(item: dict) -> list[bool]:
    """q5: claim 'summer growth is faster entirely because the days are longer'. Rule (inq:argue-model
    key concept 'variables and controlled conditions'; enzyme_temperature and photosynthesis_needs_light
    make both candidates plausible): when two candidate causes change together across every sample,
    the data cannot pick one; an association is still an association.
    Options: supports 'longer days, faster growth' but temperature rose too, so the data can't tell;
    entirely right; wrong, growth has nothing to do with light; one more summer would prove it;
    the units differ, so they can't be compared."""
    by_day = _order(0)
    growth_rises_with_day = all(GREENHOUSE[a][2] < GREENHOUSE[b][2] for a, b in zip(by_day, by_day[1:]))
    temp_rises_with_day = all(GREENHOUSE[a][1] < GREENHOUSE[b][1] for a, b in zip(by_day, by_day[1:]))
    confounded = growth_rises_with_day and temp_rises_with_day
    one_more_summer_separates = False  # in another summer days are long AND warm again (summer_days_long)
    units_block_comparison = False  # different units never stop two quantities from varying together
    return [growth_rises_with_day and confounded, growth_rises_with_day and not confounded,
            not growth_rises_with_day, one_more_summer_separates, units_block_comparison]


Q6_DESIGNS = [
    {"groups": 2, "changed": {"hours of light"}},                      # same greenhouse, lamps
    {"groups": 2, "changed": {"hours of light", "temperature"}},       # winter vs summer
    {"groups": 2, "changed": {"temperature"}},                         # both 14 h, one warmer
    {"groups": 2, "changed": {"hours of light", "water"}},
    {"groups": 1, "changed": set()},                                   # one plant only
]


def csd_q6_fair_test(item: dict) -> list[bool]:
    """q6: which design tests day length on its own? Rule (key concept 'designing and critiquing
    experiments'): at least two groups that differ in exactly the variable under test."""
    target = "hours of light"
    return [d["groups"] >= 2 and d["changed"] == {target} for d in Q6_DESIGNS]


# --- q7: statements about the GSAT, each checked against the slice ---------------------------------
# slice confirmed_facts[10] / exam_format_verified (CEEC FAQ Q5): a 混合題 is a 題組 of generally
# 2-4 小題 that moves from choice items to non-choice items.
MIXED_GROUP = {"min": 2, "max": 4, "starts_with": "choice"}
# slice corrections[1] / confirmed_facts[24]: official 115 Part 2 groups
PART2_115 = {"37-39": {"biology"}, "40-43": {"biology", "chemistry"}, "44-46": {"chemistry"},
             "47-49": {"physics"}, "50-53": {"earth", "physics"}, "54-56": {"earth"}}
# slice confirmed_facts[20]: 115 non-choice items by subject (Q50 earth, Q53 physics)
NONCHOICE_115 = {50: "earth", 53: "physics"}
# slice confirmed_facts[22]: 113 Part 2 化/地 Q50-53
GROUP_113_50 = {"chemistry", "earth"}
# slice corrections[6] / confirmed_facts[8]: sample items carry subject codes AND inquiry sub-items;
# some (外傘頂洲 Part 2 Q1) carry inquiry sub-items only
SAMPLES_TAG_INQUIRY = True


SUBJ_ZH = {"化學": "chemistry", "地科": "earth", "物理": "physics", "生物": "biology"}


def csd_q7_statements(item: dict) -> list[bool]:
    """q7: each option is matched to its fact entry by keywords in the zh option text; its numbers or
    subjects are read from the option and compared with that entry (the en option must carry the same
    numbers)."""
    zh, en = item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]
    assert len(zh) == len(en)
    out = []
    for oz, oe in zip(zh, en):
        nums = [int(x) for x in re.findall(r"\d+", oz)]
        # same numbers in both locales (en may repeat one, e.g. the '2' of 'Part 2')
        assert set(nums) == {int(x) for x in re.findall(r"\d+", oe)}, (oz, oe)
        if "混合題" in oz:  # a 混合題 is a 題組 of lo-hi 小題, starting with choice items
            out.append(tuple(nums[:2]) == (MIXED_GROUP["min"], MIXED_GROUP["max"])
                       and "由選擇題開始" in oz and MIXED_GROUP["starts_with"] == "choice")
        elif "115學年度第貳部分" in oz:  # 'of the N groups, n were two-subject sets'
            total, n_cross = nums[-2], nums[-1]
            cross = [g for g, subj in PART2_115.items() if len(subj) == 2]
            out.append(total == len(PART2_115) and n_cross == len(cross) and "兩科" in oz)
        elif "試題舉例" in oz:  # the option claims the samples never tag inquiry sub-items
            out.append(("從不標" in oz) != SAMPLES_TAG_INQUIRY)
        elif "每一小題都同時算" in oz:  # claims every sub-item counts for two subjects
            out.append(all(not isinstance(s, str) and len(s) == 2 for s in NONCHOICE_115.values()))
        elif "113學年度第50–53題" in oz:
            out.append({v for k, v in SUBJ_ZH.items() if k in oz} == GROUP_113_50)
        else:
            raise AssertionError(f"no fact entry for option: {oz}")
    return out


# --- q8 (written): the turbine argument ----------------------------------------------------------
# The model answer's reasoning chain: (cause, effect, fact)
Q8_CHAIN = [
    ("closer isobars", "stronger wind", "isobars_dense_wind"),
    ("stronger wind", "turbine turns faster", None),  # the stem states the turbine is wind-driven
    ("turbine turns faster", "field through the coil changes faster", "generator_mech_to_elec"),
    ("field through the coil changes faster", "larger induced current", "faster_change_larger_current"),
]


def csd_q8_mixed_turbine(item: dict) -> bool:
    """q8: the model answer's evidence (400 km -> 20 mA, 100 km -> 110 mA) is in the table; over the five
    days the current rises strictly as the spacing shrinks; the chain is connected, its facts come from
    reviewed earth and physics chapters; and its stated limit (5 days, 100-400 km, other factors not
    controlled) matches the data."""
    pts = sorted(TURBINE.values(), key=lambda v: -v[0])  # widest spacing first
    monotone = all(a[1] < b[1] for a, b in zip(pts, pts[1:]))
    evidence = (R(400), R(20)) in TURBINE.values() and (R(100), R(110)) in TURBINE.values()
    connected = all(a[1] == b[0] for a, b in zip(Q8_CHAIN, Q8_CHAIN[1:]))
    facts = [f for *_, f in Q8_CHAIN if f]
    subjects = {SUBJECT_OF[f] for f in facts}
    limit_ok = len(TURBINE) == 5 and min(v[0] for v in TURBINE.values()) == 100 \
        and max(v[0] for v in TURBINE.values()) == 400
    return bool(monotone and evidence and connected and subjects == {"earth", "physics"} and limit_ok)
