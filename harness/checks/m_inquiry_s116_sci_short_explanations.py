"""Checks for src/data/items/inquiry/s116-sci-short-explanations.yaml (116 sprint, science exam skills:
tick-and-justify, word-limited explanations, variables and predictions as measurable quantities;
codes exam:nat-2a ... exam:nat-5a).

How the keys are recomputed (never from item["answer"]):
- Numbers (isobar spacings, evaporation and precipitation, percentages, masses) are read from BOTH stems,
  which must agree, and compared with SymPy exact Rationals.
- Each written reason is parsed from its zh option text: what evidence it claims (checked against the
  stem's data), whether it gives a rule or a cause (checked against the facts table below), and its
  length, counted from the string itself (115 Q54 format: at most 20 characters).
- Each design is an explicit table (what is changed, what is measured, what is held fixed); a prediction
  is correct only if it connects the manipulated and responding variables in the direction the facts
  table gives.

Rules, with their sources:
- R1 A reason that earns points gives this item's evidence AND the rule that links it to the conclusion;
  repeating the conclusion is not a reason (general rule shared by physics/s116-physics-reasoning,
  chemistry/s116-chem-written-items, earth/s116-earth-data-items; registry exam:nat-2a keyConcepts:
  "written answers must show working or reasons"; slice verification.confirmed_facts: 115 Q54 tick and
  justify in no more than 20 characters).
- R2 Variables are written as measurable (physical) quantities with units; predictions state the
  relationship between the variables (spec activity and slice: 113 Q43 scoring guide;
  inquiry/s116-inq-question-plan).
- R3 A "why" question asks for a cause (a rule), a "which" question for evidence (the chapter's own
  reading of the question's verb).
Facts used (subject chapters):
- F1 Closer isobars -> larger pressure gradient force -> usually stronger wind (earth/s116-wind-weather-maps).
- F2 Surface salinity rises with evaporation minus precipitation, away from river input
  (earth/s116-ocean-currents-el-nino).
- F3 Natural selection: resistant variants exist before the selecting agent; it kills the non-resistant,
  survivors reproduce and pass the trait on; not "in order to adapt" (biology/s116-natural-selection).
- F4 At a fixed temperature the most solute dissolved is proportional to the amount of solvent
  (chemistry/s116-solutions: solubility per 100 g water; halve the water, halve the amounts).
- F5 Wet-and-dry-bulb: the drier the air, the faster the evaporation and the larger the difference
  (earth/s116-air-vapour-clouds).
- F6 Aa x Aa gives AA:Aa:aa = 1:2:1 (biology/s116-mendel).
- F7 The finer a given mass of solid, the larger its total surface area and the faster it reacts
  (chemistry/s116-rate-and-technology).
- F8 Heat = mass x specific heat x temperature change (junior high, used in physics/s116-heat-energy-quality).
- F9 Reactions in cells need enzymes; below the optimum, the lower the temperature, the slower an enzyme
  works (biology/s116-cell-energy, 酵素 section and its rate-temperature figure). F7's surface-area rule
  applies to dividing a solid, not to a temperature difference.
"""

from __future__ import annotations

import re

from sympy import Rational as R

LIMIT = 20  # 115 Q54: no more than 20 characters


def _zh(item: dict) -> str:
    return item["text"]["zh-tw"]["stem"]


def _en(item: dict) -> str:
    return item["text"]["en"]["stem"]


def _opts(item: dict) -> list[str]:
    zh, en = item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]
    assert len(zh) == len(en), (zh, en)
    return zh


def _glossed(item: dict) -> list[str]:
    """Options whose length matters: the en options carry the zh answer first, then a gloss."""
    zh = _opts(item)
    assert all(e.startswith(z) for z, e in zip(zh, item["text"]["en"]["options"]))
    return zh


# --- opening turn: isobars -------------------------------------------------------------------------------


def se_turn_isobar_reason(item: dict) -> list[bool]:
    """q-turn: which reason for ticking 甲 (strongest wind) is complete (R1, F1) and within 20 characters?"""
    zs = [R(x) for x in re.search(r"間距分別約是(\d+)公里、(\d+)公里、(\d+)公里", _zh(item)).groups()]
    es = [R(x) for x in re.search(r"is about (\d+) km, (\d+) km and (\d+) km", _en(item)).groups()]
    assert zs == es and "勾了甲" in _zh(item) and "ticks A" in _en(item)
    spacing = dict(zip("甲乙丙", zs))
    densest = min(spacing, key=spacing.get)
    assert list(spacing.values()).count(spacing[densest]) == 1 and densest == "甲"  # the tick is right

    def judge(t: str) -> bool:
        # evidence: a claim about 甲's spacing compared with the others
        if re.search(r"甲的等壓線(間距)?(為\d+公里，是三站中)?最小", t):
            claim = "min"
        elif "甲的等壓線最稀疏" in t:
            claim = "max"
        else:
            claim = None  # no evidence about 甲 (a bare rule, or the conclusion repeated)
        evidence_ok = claim == "min" and densest == "甲"
        m = re.search(r"\d+公里", t)
        if m:
            evidence_ok = evidence_ok and R(m.group()[:-2]) == spacing["甲"]
        rule_ok = "氣壓梯度力最大" in t  # F1: closest isobars -> largest pressure gradient force
        return evidence_ok and rule_ok and len(t) <= LIMIT

    return [judge(o) for o in _glossed(item)]


# --- mid-chapter turn: dissolving prediction ---------------------------------------------------------------

DISSOLVE_DESIGN = {"manipulated": "water_mass", "responding": "max_dissolved", "controlled": {"temperature"}}
FACT_DIRECTION = {("water_mass", "max_dissolved"): +1}  # F4


def se_turn_dissolve_prediction(item: dict) -> list[bool]:
    """q-predict: which prediction connects the manipulated and responding variables in the right direction (R2, F4)?"""
    assert "保持25℃" in _zh(item) and "keeping the water at 25 ℃" in _en(item)
    o = _opts(item)
    # (x quantity, y quantity, direction) read from each option; None = not a measurable quantity / no relation
    assert "效果" in o[0]
    assert "水的質量越大" in o[1] and o[1].endswith("越大。") and "最多能溶解的X的質量" in o[1]
    assert "水的質量越大" in o[2] and o[2].endswith("越小。")
    assert o[3].startswith("溫度越高")
    assert re.fullmatch(r"最多會溶解\d+公克的X。", o[4])
    feats = [
        (None, None, +1),  # "the effect": not measurable
        ("water_mass", "max_dissolved", +1),
        ("water_mass", "max_dissolved", -1),
        ("temperature", None, +1),  # temperature is held fixed here
        (None, "max_dissolved", None),  # a number, no relationship
    ]
    d = DISSOLVE_DESIGN
    return [
        x == d["manipulated"] and y == d["responding"] and FACT_DIRECTION.get((x, y)) == s
        for x, y, s in feats
    ]


# --- q1: salinity -------------------------------------------------------------------------------------------


def _seas(item: dict) -> dict[str, tuple[R, R]]:
    zh = {k: (R(e), R(p)) for k, e, p in re.findall(r"([丁戊己])蒸發(\d+)、降水(\d+)", _zh(item))}
    en = {k: (R(e), R(p)) for k, e, p in re.findall(r"([DEF]), evaporation (\d+), precipitation (\d+)", _en(item))}
    assert {"丁": en["D"], "戊": en["E"], "己": en["F"]} == zh and len(zh) == 3
    assert "遠離河口" in _zh(item)  # F2 applies only without river input
    return zh


def se_salinity_reason(item: dict) -> list[bool]:
    """q1: which reason for ticking 丁 (highest surface salinity) gives correct evidence and the rule (R1, F2)?"""
    seas = _seas(item)
    net = {k: e - p for k, (e, p) in seas.items()}
    top = max(net, key=net.get)
    assert list(net.values()).count(net[top]) == 1 and top == "丁" and "勾了丁" in _zh(item)
    most_evap = max(seas, key=lambda k: seas[k][0])

    def judge(t: str) -> bool:
        m = re.search(r"丁的蒸發量比降水量多(\d+)毫米，三者中最多", t)
        if m:
            evidence_ok = R(m.group(1)) == net["丁"] and top == "丁"
            rule_ok = "淡水淨減少" in t  # F2: more water leaves than arrives -> salt concentrated
            return evidence_ok and rule_ok
        # anything else: the conclusion repeated, a bare rule, evaporation alone (which ignores
        # precipitation, and here is false as well), or data not in the table (latitude)
        return False

    assert most_evap != "丁"  # option (4)'s evidence is actually false here
    return [judge(o) for o in _opts(item)]


# --- q2: pesticide resistance -------------------------------------------------------------------------------


def se_pesticide_reason(item: dict) -> list[bool]:
    """q2: a 'why' question (R3): the cause by natural selection (F3), within 20 characters."""
    zp = [R(x) for x in re.findall(r"第\d+年(\d+)%", _zh(item))]
    ep = [R(x) for x in re.findall(r"(\d+)% in year", _en(item))]
    assert zp == ep and zp == sorted(zp) and "為什麼" in _zh(item) and "Why" in _en(item)

    def judge(t: str) -> bool:
        if "為了" in t:  # need-driven change: contradicts F3
            return False
        kills = "殺死" in t and ("不抗藥" in t or "不具抗藥" in t)
        survive = "存活" in t
        passes_on = "繁殖" in t or "遺傳" in t
        return kills and survive and passes_on and len(t) <= LIMIT

    return [judge(o) for o in _glossed(item)]


# --- q3: measurable variables -------------------------------------------------------------------------------

UNITS = {"g", "cm", "kg", "m", "s", "℃", "mL", "W"}


def se_measurable_spring(item: dict) -> list[bool]:
    """q3: an option is a measurable quantity iff it names a unit (R2; the chapter's unit check)."""
    assert "彈簧" in _zh(item) and "spring" in _en(item)
    out = []
    for z, e in zip(_opts(item), item["text"]["en"]["options"]):
        mz = re.search(r"（([^）]+)）$", z)
        me = re.search(r"\(([^)]+)\)$", e)
        assert bool(mz) == bool(me) and (not mz or mz.group(1) == me.group(1)), (z, e)
        out.append(bool(mz) and mz.group(1) in UNITS)
    return out


# --- q4: wet-and-dry-bulb prediction --------------------------------------------------------------------------

BULB_DESIGN = {"x": "relative_humidity", "y": "bulb_difference"}
BULB_FACT = -1  # F5: higher relative humidity (moister air) -> smaller difference


def se_wet_dry_bulb_prediction(item: dict) -> list[bool]:
    """q4: the prediction must connect the two recorded quantities in the direction F5 gives (R2)."""
    assert "相對濕度（%）" in _zh(item) and "讀數差（℃）" in _zh(item)
    # F5 compares air at (about) the same temperature: the stem must hold the air temperature roughly fixed
    assert "氣溫大致相同" in _zh(item) and "air temperature is about the same" in _en(item)

    def feats(t: str):
        m = re.fullmatch(r"相對濕度（%）越(低|高)，乾濕球的讀數差（℃）越(大|小)", t)
        if m:
            s = (-1 if m.group(1) == "低" else 1) * (1 if m.group(2) == "大" else -1)
            return ("relative_humidity", "bulb_difference", s)
        if t.startswith("氣溫越高"):
            return ("air_temperature", "relative_humidity", +1)
        return (None, None, None)  # no measurable quantity, or a single number

    return [
        (x, y) == (BULB_DESIGN["x"], BULB_DESIGN["y"]) and s == BULB_FACT
        for x, y, s in (feats(o) for o in _opts(item))
    ]


# --- q5: pea cross -------------------------------------------------------------------------------------------


def se_pea_prediction(item: dict) -> tuple[str, ...]:
    """q5: predicted white (aa) offspring of Aa x Aa (F6) among the stated total."""
    nz = int(re.search(r"共得到 \$(\d+)\$ 株子代", _zh(item)).group(1))
    ne = int(re.search(r"give \$(\d+)\$ offspring", _en(item)).group(1))
    assert nz == ne
    gametes = {"A": R(1, 2), "a": R(1, 2)}
    p_aa = sum(p * q for g1, p in gametes.items() for g2, q in gametes.items() if g1 == g2 == "a")
    n = nz * p_aa
    assert n.q == 1
    return tuple(str(int(n)).rjust(3, "0"))


# --- q6: why does the cold dough rise less -------------------------------------------------------------------
# Candidate rules a "why" answer may give, and whether each applies to this design (two identical pieces of
# dough that differ only in temperature):
#   F9 enzyme activity vs temperature: applies (the pieces differ in temperature, both below the optimum).
#   F7 surface area: does not apply (identical pieces; temperature does not change the dough's surface area).
RULES_Q6 = {"酵素": True, "接觸面積": False}


def se_dough_why(item: dict) -> list[bool]:
    """q6: a 'why' question (R3) needs the cause that fits the design (F9, not F7), consistent with the stem
    (the cold piece still rose a little, so gas was still made), within 20 characters."""
    z, e = _zh(item), _en(item)
    tz = [R(x) for x in re.findall(r"(\d+)℃", z.split("題目問")[0])]
    te = [R(x) for x in re.findall(r"(\d+) ℃", e.split("The question asks")[0])]
    assert tz == te and set(tz) == {30, 5} and "兩塊相同的麵團" in z and "Two identical pieces" in e
    assert "為什麼" in z and "Why" in e
    still_rose = "只膨脹了一點點" in z and "only a little" in e
    cold, warm = min(tz), max(tz)

    def judge(t: str) -> bool:
        rules = [k for k in RULES_Q6 if k in t]
        if not rules:
            return False  # restates the observation, or explains the conclusion with itself
        if ("全死" in t or "完全不產氣" in t) and still_rose:
            return False  # contradicts the stem: the cold piece still rose a little
        slower_when_cold = "低溫" in t and ("變慢" in t or "較慢" in t) and cold < warm
        return all(RULES_Q6[k] for k in rules) and slower_when_cold and len(t) <= LIMIT

    return [judge(o) for o in _glossed(item)]


# --- q7: written item, heater and water ----------------------------------------------------------------------


def se_heater_written(item: dict) -> bool:
    """q7 (mixed): the model answer's identities hold.
    - the design table: only the water mass changes; heater, time and starting temperature are fixed;
    - F8 with equal heat Q: temperature rise = Q / (m * c), so it falls as m grows, inverse proportion
      (200 g rises half as much as 100 g, as the model says);
    - the rubric is 4 points, one per scoring point (R2), and the model names each variable with a unit."""
    masses = [R(x) for x in re.findall(r"(\d+)公克", _zh(item).split("的水")[0])]
    masses_en = [R(x) for x in re.findall(r"(\d+) g", _en(item))]
    assert masses == masses_en == [100, 200, 300]
    assert "同一個電熱器" in _zh(item) and "3分鐘" in _zh(item) and "20℃" in _zh(item)
    Q, c = R(1), R(1)  # any equal heat and the same liquid
    rise = {m: Q / (m * c) for m in masses}
    assert all(rise[a] > rise[b] for a, b in zip(masses, masses[1:]))
    assert rise[200] / rise[100] == R(1, 2)
    crit = item["rubric"]["criteria"]
    assert sum(c_["points"] for c_ in crit) == 4 and len(crit) == 4
    model = item["model"]["zh-tw"]
    assert "水的質量（公克）" in model and "（℃）" in model and "水的質量越大，水溫上升的量越小" in model
    assert "一半" in model and "half" in item["model"]["en"]
    return True
