"""Checks for src/data/items/inquiry/s116-inq-question-plan.yaml (116 sprint, inquiry strands
發現問題 and 規劃與研究: inq:discover/*, inq:plan/*, nat:po-Ⅴc-1/2, ti-Ⅴc-1, pe-Ⅴc-1/2).

How the keys are recomputed (never from item["answer"]):
- Each stem's design is written out as an explicit table: which quantity is changed, which is
  measured, which are held fixed. Variable roles are read off that table.
- Judgements (researchable question, testable prediction, fair comparison, reliable source,
  quantitative datum, which strand a step belongs to) come from rule lists; each rule names its
  source: an inq.json key concept, the chapter's research slice, the spec's activity note, or the
  course's own criterion where no source states it (those are flagged in the chapter report).
- Counts and times use exact Rationals.

No subject science is needed by any item: the contexts (cooling cups, a ramp, salt and stirring, balls,
leaves) are only settings for method questions, and no option's truth depends on a science fact.
"""

from __future__ import annotations

import re

from sympy import Rational as R

# --- rules ---------------------------------------------------------------------------------------
# A researchable (experimentally testable) question names a quantity the experimenter can change
# and a quantity that can be measured, and does not ask for a value judgement.
# Source: inq:discover/pose-question key concept "Pick a priority, researchable question"; the
# spec's activity note on 113 Q43 (variables must be physical quantities).


def _researchable(q: dict) -> bool:
    return q["changeable"] and q["measurable"] and not q["value_judgement"]


# A testable prediction for "does X affect Y" states a relation: it names the manipulated quantity,
# names the responding quantity and says which way one changes with the other.
# Source: spec activity note, 113 Q43 scoring guide: "predictions must relate them [the variables]".


def _testable_prediction(p: dict) -> bool:
    return p["names_manipulated"] and p["names_responding"] and p["states_direction"]


# A comparison can attribute a difference to one factor only when that factor is the ONLY one
# that differs between the groups (otherwise the factors are confounded).
# Source: inq:plan key concept "variables and controlled conditions"; inq:discover/observe
# "guess possible causes".


def _differing(a: dict, b: dict) -> list[str]:
    return [k for k in a if a[k] != b[k]]


# A source is worth relying on when (1) it gives evidence (its method and data), (2) whoever gives
# it has nothing to gain from the claim, and (3) it can be checked: its raw data or method are
# available to look up, or another independent source has found the same result. These are the
# chapter's three questions (有沒有證據、有沒有利益關係、能不能查證).
# Source: inq:discover/gather-info key concept "judging how reliable a source is"; the three
# criteria themselves are the course's own (no source in the slice lists them).


def _reliable(src: dict) -> bool:
    checkable = src["raw_data_or_method_available"] or src["independently_confirmed"]
    return src["method_and_data"] and not src["stake"] and checkable


# Quantitative data are a number with a unit; qualitative data are descriptions in words.
# Source: inq:plan key concept "collect qualitative or quantitative data".
UNIT_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:mL|g|cm|m|s|℃|秒|公克|毫升)")


# --- opening and mid-chapter turns ---------------------------------------------------------------

TURN_QUESTIONS = [
    # 為什麼颳風的日子讓人心情不好？ mood is not a measured quantity in the stem
    {"changeable": False, "measurable": False, "value_judgement": False},
    # 毛巾乾得快是好事還是壞事？ a value judgement
    {"changeable": False, "measurable": False, "value_judgement": True},
    # 風速越大，濕毛巾在30分鐘內減少的質量是否越多？ wind speed (set with a fan), mass (balance)
    {"changeable": True, "measurable": True, "value_judgement": False},
    # 哪一種布料最好？ "best" is undefined: no measurable response, and it asks for a judgement
    {"changeable": True, "measurable": False, "value_judgement": True},
    # 明年夏天的毛巾會不會乾得比今年快？ next year's weather cannot be set by the experimenter
    {"changeable": False, "measurable": True, "value_judgement": False},
]


def iqp_turn_researchable(item: dict) -> list[bool]:
    """q-turn: which question is best suited to an experiment?"""
    return [_researchable(q) for q in TURN_QUESTIONS]


# q-mid: the two days of the stem (illustrative weather-station record).
DAY_1 = {"wind_m_s": R(1, 2), "humidity_pct": 80, "temp_c": 24}
DAY_2 = {"wind_m_s": 3, "humidity_pct": 60, "temp_c": 28}
RESULT_DIFFERED = True  # the stem says the towel dried faster on Day 2


def iqp_mid_two_days(item: dict) -> list[bool]:
    """q-mid: the towel dried faster on Day 2; which statement fits the record?
    Options: (1) proves wind causes it; (2) proves low humidity causes it; (3) wind, humidity and
    temperature all differ, so the record cannot tell which; (4) proves temperature is unrelated;
    (5) the difference must be a balance error."""
    diff = _differing(DAY_1, DAY_2)
    proves = lambda k: diff == [k]  # a single factor is shown only when it alone differs
    # (4) "unrelated" would need temperature to differ with no change in the result, or to be the
    # only factor and show no effect; here the result did change and temperature is confounded.
    temp_shown_unrelated = diff == ["temp_c"] and not RESULT_DIFFERED
    # (5) the stem says nothing about the balance's accuracy, so a "must be" claim has no evidence.
    stem_has_balance_evidence = False
    return [proves("wind_m_s"), proves("humidity_pct"), len(diff) > 1, temp_shown_unrelated,
            stem_has_balance_evidence]


# --- Check yourself ------------------------------------------------------------------------------

# q1: four cups (ceramic, glass, steel, paper), 200 mL of 80 ℃ water each, same table, temperature
# read every 5 min for 30 min.
CUPS = {
    "changed": {"cup_material"},
    "measured": {"water_temperature"},
    "fixed": {"water_volume", "start_temperature", "place", "reading_interval"},
}
Q1_OPTIONS = ["cup_material", "water_temperature", "water_volume", "start_temperature", "reading_interval"]


def iqp_cups_responding(item: dict) -> list[bool]:
    """q1: which is the responding variable? It is the quantity the design measures."""
    assert not (CUPS["changed"] & CUPS["fixed"]) and not (CUPS["measured"] & CUPS["fixed"])
    return [o in CUPS["measured"] for o in Q1_OPTIONS]


# q2: a ramp; the angle is changed, the time to reach the bottom is measured. The setup quantities
# the stem lists are the car's mass, the ramp's length, its angle and its surface material.
RAMP_SETUP = {"car_mass", "ramp_length", "ramp_angle", "surface_material"}
RAMP_CHANGED = {"ramp_angle"}
RAMP_MEASURED = {"time_to_bottom"}
Q2_OPTIONS = ["car_mass", "ramp_length", "ramp_angle", "surface_material", "time_to_bottom"]


def iqp_ramp_controlled(item: dict) -> list[bool]:
    """q2: which must be kept the same? In a fair test every setup quantity except the manipulated
    one is held fixed; the responding variable is measured, not held."""
    controlled = RAMP_SETUP - RAMP_CHANGED - RAMP_MEASURED
    return [o in controlled for o in Q2_OPTIONS]


# q3: question "每分鐘攪拌的圈數越多，5 g食鹽完全溶解所需的時間是否越短？"; candidate predictions.
Q3_PREDICTIONS = [
    # 食鹽放進水裡會溶解: an event, no quantity named
    {"names_manipulated": False, "names_responding": False, "states_direction": False},
    # 每分鐘攪拌的圈數越多，食鹽完全溶解所需的時間越短
    {"names_manipulated": True, "names_responding": True, "states_direction": True},
    # 食鹽會溶解是因為鹽很鹹: a reason unrelated to the variables
    {"names_manipulated": False, "names_responding": False, "states_direction": False},
    # 用力攪拌比較好: names the stirring loosely, no measured quantity, a judgement
    {"names_manipulated": True, "names_responding": False, "states_direction": False},
    # 攪拌會影響實驗: names the manipulated quantity only, no responding quantity or direction
    {"names_manipulated": True, "names_responding": False, "states_direction": False},
]


def iqp_sugar_prediction(item: dict) -> list[bool]:
    """q3: which prediction is written as a testable relation between the variables?"""
    return [_testable_prediction(p) for p in Q3_PREDICTIONS]


# q4: five sources on whether using a phone before bed changes the time to fall asleep.
Q4_SOURCES = [
    # unsigned article, no data
    {"method_and_data": False, "stake": False, "raw_data_or_method_available": False,
     "independently_confirmed": False},
    # report with method and data for 30 participants; "raw data that can be looked up"
    {"method_and_data": True, "stake": False, "raw_data_or_method_available": True,
     "independently_confirmed": False},
    # advert from a company selling sleep pillows
    {"method_and_data": False, "stake": True, "raw_data_or_method_available": False,
     "independently_confirmed": False},
    # two studies by different teams, clear methods, agreeing results
    {"method_and_data": True, "stake": False, "raw_data_or_method_available": True,
     "independently_confirmed": True},
    # a friend tried it for one night: no data, nothing to look up
    {"method_and_data": False, "stake": False, "raw_data_or_method_available": False,
     "independently_confirmed": False},
]


def iqp_sleep_sources(item: dict) -> list[bool]:
    """q4: which sources are more worth relying on? (the chapter's three questions)"""
    return [_reliable(s) for s in Q4_SOURCES]


def iqp_balls_minutes(item: dict) -> int:
    """q5: 3 kinds of ball × 4 drop heights × 5 repeats, 2 minutes per drop and record."""
    kinds, heights, repeats, minutes_each = 3, 4, 5, R(2)
    total = kinds * heights * repeats * minutes_each
    assert total.q == 1
    return int(total)


# q6: which strand each step belongs to. Sub-items and strands from the slice's confirmed facts
# (領綱 「自然科學探究與實作」課程內容 table); record formats and equipment/procedure are listed
# under 規劃與研究 in inq:plan's key concepts.
STRAND_OF_STEP = {
    "design a record table": "plan",          # inq:plan "design record formats"
    "list equipment and procedure": "plan",   # inq:plan "Plan methods, materials, equipment and procedure"
    "look up and judge sources": "discover",  # inq:discover "Gather information and judge source reliability"
    "present a report": "share",              # 表達與分享－表達與溝通
    "plot data to find a trend": "argue",     # 論證與建模－分析資料和呈現證據
}
Q6_OPTIONS = ["design a record table", "list equipment and procedure", "look up and judge sources",
              "present a report", "plot data to find a trend"]


def iqp_plan_steps(item: dict) -> list[bool]:
    """q6: which steps belong to 規劃與研究?"""
    return [STRAND_OF_STEP[o] == "plan" for o in Q6_OPTIONS]


def iqp_quantitative(item: dict) -> list[bool]:
    """q7: which record is quantitative? Read each option's own text: a number with a unit.
    The zh and en options must agree."""
    zh = [bool(UNIT_RE.search(o)) for o in item["text"]["zh-tw"]["options"]]
    en = [bool(UNIT_RE.search(o)) for o in item["text"]["en"]["options"]]
    assert zh == en, (zh, en)
    return zh
