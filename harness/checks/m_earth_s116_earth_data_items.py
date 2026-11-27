"""Checks for src/data/items/earth/s116-earth-data-items.yaml (116 sprint, Earth science exam skills).

The chapter has no curriculum codes (earth.json: codes []): it practises reading data, plotting,
judging multi-select options and writing word-limited reasons, using content from earlier chapters.
Each function recomputes its item's answer from the data in the stem and the rules below; none reads
item["answer"]. Where an option's wording matters (character counts, option sequences), the function
reads the option TEXT and checks it against the encoded features, so a typo in the bank fails loudly.

Rules used, with their sources:
- Tidal range = high-tide level minus the neighbouring low-tide level (earth.tidal-range glossary entry,
  chapter earth/s116-waves-tides; the 115 Q50 scoring note computes 1.75 - (-1.5), slice
  verification.confirmed_facts).
- Radioactive decay: after r half-lives, (1/2)^r of the parent is left (earth.half-life glossary entry,
  chapter earth/s116-earth-history). The "measurable only between 1% and 99% left" threshold is the
  item's own stated assumption, not a fact about real laboratories.
- Superposition (lower is older in strata not overturned) and cross-cutting (a body that cuts others is
  younger than what it cuts): slice verification.corrections (國中 學習內容說明 appendix, PDF p.158);
  chapter earth/s116-earth-history. A layer that lies over the top of a fault or dyke without being cut
  is younger than it (superposition applied to the cutting body).
- Multi-select scoring: with n options, k of them judged wrong, the item earns (n - 2k)/n of its points,
  floored at 0; every option is judged on its own (facts.json exam.multi-select-scoring; slice
  verification.confirmed_facts, 116 簡章).
- The 115 Q54 format: tick one answer and justify it in no more than 20 characters (slice
  verification.confirmed_facts, 115 非選 scoring guide).
- Plot requirements (axes labelled with quantity and unit, an even scale, every point placed correctly,
  points joined) are the chapter's own checklist; standard practice, not a CEEC rubric text.
"""

from __future__ import annotations

import re
from fractions import Fraction
from itertools import permutations

import sympy as sp
from sympy import Rational as Q

# Every function below reads its item's numbers from BOTH stems (zh-tw and en), asserts that they agree,
# and recomputes from those numbers, so editing a stem number (in either language) changes or breaks the
# check instead of passing on stale data.


def _zh(item: dict) -> str:
    return item["text"]["zh-tw"]["stem"]


def _en(item: dict) -> str:
    return item["text"]["en"]["stem"]


def _num(s: str) -> Q:
    """'1.6', '−0.9' (Unicode minus), '-131', '10,000' -> exact Rational."""
    return Q(s.replace("−", "-").replace(",", ""))


def _frac(s: str) -> Fraction:
    """An option value: '$\\tfrac{4}{5}$', '0', '2.5' -> Fraction."""
    m = re.fullmatch(r"\$\\tfrac\{(\d+)\}\{(\d+)\}\$", s.strip())
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    return Fraction(s.strip().replace("−", "-"))


def _same_options(item: dict) -> list[str]:
    zh, en = item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]
    assert len(zh) == len(en), (zh, en)
    return zh


# --- tides --------------------------------------------------------------------------------------------


def tidal_range(high, low):
    """High-tide level minus the neighbouring low-tide level (a negative low tide adds back)."""
    return high - low


def dx_turn_tidal_range(item: dict) -> list[bool]:
    """q-turn: a high tide, then the low tide after it (illustrative). Options are ranges in m."""
    hz, lz = re.search(r"滿潮是([−\-]?[\d.]+)公尺，接著的乾潮是([−\-]?[\d.]+)公尺", _zh(item)).groups()
    he, le = re.search(r"high tide of ([−\-]?[\d.]+) m, and the low tide after it is ([−\-]?[\d.]+) m", _en(item)).groups()
    high, low = _num(hz), _num(lz)
    assert (high, low) == (_num(he), _num(le)) and low < 0 < high
    got = tidal_range(high, low)
    opts = _same_options(item)
    assert opts == item["text"]["en"]["options"]  # plain numbers, identical in both locales
    return [_num(o) == got for o in opts]


def _tide_events(item: dict) -> list[tuple[int, str, Q]]:
    """(hour, 'high'|'low', level) in time order, parsed from both stems."""
    zh = [(int(h), {"滿潮": "high", "乾潮": "low"}[k], _num(v)) for h, k, v in re.findall(r"(\d+)時(滿潮|乾潮) \$(-?\d+)\$", _zh(item))]
    en = [(int(h), k, _num(v)) for k, h, v in re.findall(r"(high|low) tide at (\d+) h, \$(-?\d+)\$", _en(item))]
    assert zh == en and len(zh) >= 3, (zh, en)
    zh.sort()
    return zh


def dx_largest_tidal_range(item: dict) -> tuple[str, ...]:
    """q2: a day's highs and lows (cm); the largest range between a high and the NEIGHBOURING low."""
    ev = _tide_events(item)
    kinds = [k for _, k, _ in ev]
    assert all(a != b for a, b in zip(kinds, kinds[1:])), "highs and lows must alternate"
    ranges = []
    for (_, k1, v1), (_, k2, v2) in zip(ev, ev[1:]):
        high, low = (v1, v2) if k1 == "high" else (v2, v1)
        r = tidal_range(high, low)
        assert r > 0
        ranges.append(r)
    best = max(ranges)
    assert ranges.count(best) == 1 and best.q == 1
    s = str(int(best))
    assert len(s) == 3
    return tuple(s)


# The chapter's plotting checklist: every one must hold for a correct plot.
PLOT_REQUIREMENTS = ("axes_labelled", "even_scale", "points_correct", "points_joined")


def dx_plot_checklist(item: dict) -> list[bool]:
    """q1: which way of plotting a day's tide data (with negative levels) is right?
    Each option is described by the requirements it meets (read off the option text in the bank)."""
    assert "負值" in _zh(item) and "negative" in _en(item)
    options = [
        # (1) quantities+units on the axes, even scale, negative levels below 0, joined smoothly
        {"axes_labelled": True, "even_scale": True, "points_correct": True, "points_joined": True},
        # (2) vertical axis starts at 0, negative levels drawn on the 0 line: points misplaced
        {"axes_labelled": True, "even_scale": True, "points_correct": False, "points_joined": True},
        # (3) axes carry numbers only, no quantity or unit
        {"axes_labelled": False, "even_scale": True, "points_correct": True, "points_joined": True},
        # (4) the data values themselves written at equal gaps up the axis: uneven scale
        {"axes_labelled": True, "even_scale": False, "points_correct": False, "points_joined": True},
        # (5) only the highest and lowest readings plotted
        {"axes_labelled": True, "even_scale": True, "points_correct": False, "points_joined": False},
    ]
    assert len(_same_options(item)) == len(options)
    return [all(o[r] for r in PLOT_REQUIREMENTS) for o in options]


# --- judging statements against data ------------------------------------------------------------------


def _pressures(item: dict) -> dict[int, int]:
    zh = {int(d): int(p) for d, p in re.findall(r"第(\d+)天(\d+)", _zh(item))}
    en = {int(d): int(p) for d, p in re.findall(r"day (\d+), (\d+)", _en(item))}
    assert zh == en and len(zh) == 6, (zh, en)
    return zh


def dx_typhoon_statements(item: dict) -> list[bool]:
    """q3: which statements are certainly correct from the pressure data alone?
    The days and amounts each statement names are read from its zh option text (and checked against the
    en text). A statement about anything not in the data (here, the typhoon's position) is 'not covered':
    None, and only supported statements (True) are to be chosen."""
    p = _pressures(item)
    zo = _same_options(item)
    eo = item["text"]["en"]["options"]
    d1 = int(re.fullmatch(r"第(\d+)天的中心氣壓最低", zo[0]).group(1))
    a2, b2 = (int(x) for x in re.fullmatch(r"從第(\d+)天到第(\d+)天，中心氣壓每天都下降", zo[1]).groups())
    a3, b3, c3, e3 = (int(x) for x in re.fullmatch(r"第(\d+)天到第(\d+)天中心氣壓下降的幅度，比第(\d+)天到第(\d+)天大", zo[2]).groups())
    assert "臺灣" in zo[3] and "Taiwan" in eo[3]
    x5, y5, diff5 = (int(x) for x in re.fullmatch(r"第(\d+)天和第(\d+)天的中心氣壓相差(\d+) hPa", zo[4]).groups())
    assert re.search(rf"day {d1}\b", eo[0]) and re.search(rf"day {a2} to day {b2}", eo[1])
    assert re.search(rf"day {a3} to day {b3} is larger than from day {c3} to day {e3}", eo[2])
    assert re.search(rf"day {x5} and day {y5} differ by {diff5} hPa", eo[4])
    lowest = [d for d in p if p[d] == min(p.values())]
    s1 = lowest == [d1]
    s2 = all(p[d + 1] < p[d] for d in range(a2, b2))
    s3 = (p[a3] - p[b3]) > (p[c3] - p[e3])
    s4 = None  # "the centre crossed Taiwan": the typhoon's position is not in the data
    s5 = abs(p[x5] - p[y5]) == diff5
    return [s is True for s in (s1, s2, s3, s4, s5)]


def multi_select_fraction(n: int, chosen: set[int], key: set[int]) -> Fraction:
    """facts.json exam.multi-select-scoring: each option judged on its own; k wrong -> (n-2k)/n, floor 0."""
    k = sum(1 for i in range(n) if (i in chosen) != (i in key))
    return max(Fraction(n - 2 * k, n), Fraction(0))


def _choice_set(s: str) -> set[int]:
    """'(1)(2)(3)(4)' -> {0, 1, 2, 3}."""
    return {int(x) - 1 for x in re.findall(r"\((\d)\)", s)}


def dx_scoring_fraction(item: dict) -> list[bool]:
    """q7: n options, a key, and a candidate's choices, all read from the stems; fraction of the points."""
    nz, kz, cz = re.search(r"有(\d+)個選項，正確答案是((?:\(\d\))+)。某考生選了((?:\(\d\))+)", _zh(item)).groups()
    ne, ke, ce = re.search(r"has (\d+) options, and the correct answer is ((?:\(\d\))+)\. A candidate chooses ((?:\(\d\))+)", _en(item)).groups()
    assert (nz, kz, cz) == (ne, ke, ce)
    got = multi_select_fraction(int(nz), _choice_set(cz), _choice_set(kz))
    # cross-check with the chapter's worked example: key (1)(2), chosen (1)(2)(4) -> 3/5
    assert multi_select_fraction(5, {0, 1, 3}, {0, 1}) == Fraction(3, 5)
    opts = [_frac(o) for o in _same_options(item)]
    assert opts == [_frac(o) for o in item["text"]["en"]["options"]]
    return [o == got for o in opts]


# --- radiometric dating -------------------------------------------------------------------------------

LOW, HIGH = Q(1, 100), Q(99, 100)  # the items' stated assumption: reliable only with 1%-99% left
ZH_UNIT = {"萬": 10**4, "億": 10**8, "": 1}
EN_UNIT = {" million": 10**6, " billion": 10**9, "": 1}
ZH_TO_EN = {"丙": "U", "丁": "V", "戊": "W"}  # the en adaptation's names for the imaginary isotopes


def _zh_years(num: str, unit: str) -> Q:
    return _num(num) * ZH_UNIT[unit]


def _en_years(num: str, unit: str) -> Q:
    return _num(num) * EN_UNIT[unit]


def fraction_left(age, half_life):
    return sp.Integer(2) ** (-sp.Rational(age) / sp.Rational(half_life))


def measurable(age, half_life) -> bool:
    f = fraction_left(age, half_life)
    return bool(f >= LOW) and bool(f <= HIGH)


def _rock_and_isotopes(item: dict) -> tuple[Q, dict[str, Q]]:
    """q4: the rock's age and the three half-lives, from both stems."""
    zh, en = _zh(item), _en(item)
    age_z = _zh_years(*re.search(r"約([\d.]+)(萬|億)年前形成", zh).groups())
    age_e = _en_years(*re.search(r"about ([\d.,]+)( million| billion)? years ago", en).groups(default=""))
    iso_z = {k: _zh_years(n, u) for k, n, u in re.findall(r"([丙丁戊])的半衰期([\d.]+)(萬|億)年", zh)}
    iso_e = {k: _en_years(n, u or "") for k, n, u in re.findall(r"\b([UVW]) (?:has )?a half-life of ([\d.,]+)( million| billion)? years", en)}
    assert age_z == age_e, (age_z, age_e)
    assert {ZH_TO_EN[k]: v for k, v in iso_z.items()} == iso_e and len(iso_z) == 3, (iso_z, iso_e)
    return age_z, iso_z


def dx_isotope_choice(item: dict) -> list[bool]:
    """q4: which imaginary isotope suits the rock under the 1%-99% assumption? Options name sets of
    isotopes ('只有丁', '丙和丁都適合', '三種都不適合'), read from the option text."""
    age, iso = _rock_and_isotopes(item)
    ok = {name for name, t in iso.items() if measurable(age, t)}
    # sanity: the worked example (20,000-year ash; 甲 5000 yr usable, 乙 1e9 yr not) follows the same rule
    assert measurable(20000, 5000) and not measurable(20000, 10**9)
    opts = []
    for o in _same_options(item):
        named = set(re.findall(r"[丙丁戊]", o))
        assert named or o == "三種都不適合", o
        opts.append(named)
    return [o == ok for o in opts]


def _direction(age, half_life) -> str:
    """Whether an isotope works: 'short' (parent used up), 'long' (hardly decayed) or 'ok'."""
    f = fraction_left(age, half_life)
    return "short" if f < LOW else "long" if f > HIGH else "ok"


CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def dx_best_reason(item: dict) -> list[bool]:
    """q5: the best reason, in at most 20 characters, why 丁 IS suitable for the rock.
    Complete = gives the evidence (how many half-lives the age is), correctly, and the consequence (how much
    is left, and that it can be measured); and the zh text is at most 20 characters (115 Q54 format).
    Each option's claims are parsed from its zh text and recomputed; its length is counted from the text."""
    zh, en = _zh(item), _en(item)
    age_z = _zh_years(*re.search(r"岩石約([\d.]+)(萬|億)年", zh).groups())
    hl_z = _zh_years(*re.search(r"丁的半衰期([\d.]+)(萬|億)年", zh).groups())
    age_e = _en_years(*re.search(r"about ([\d.,]+)( million| billion)? years old", en).groups(default=""))
    hl_e = _en_years(*re.search(r"half-life of ([\d.,]+)( million| billion)? years", en).groups(default=""))
    assert (age_z, hl_z) == (age_e, hl_e) and "why V is suitable" in en and "為什麼丁適合" in zh
    assert _direction(age_z, hl_z) == "ok"  # the stem's premise: 丁 is suitable
    r = age_z / hl_z
    left = fraction_left(age_z, hl_z)

    def judge(text: str) -> bool:
        # evidence stated as a number of half-lives (digits, or Chinese numerals as in '的三倍')
        m_r = re.search(r"約經([\d/]+)個半衰期", text) or re.search(r"的([一二三四五六七八九十])倍", text)
        # consequence stated as the fraction left ('剩1/8', '剩下八分之一')
        m_f = re.search(r"剩([\d]+/[\d]+)", text) or re.search(r"剩下([一二三四五六七八九十])分之([一二三四五六七八九十])", text)
        wrong_comparison = "遠長於" in text or "遠短於" in text  # the half-life is neither: it is a third of the age
        if not (m_r and m_f) or wrong_comparison:
            return False
        r_claim = Q(m_r.group(1)) if m_r.group(1)[0].isdigit() else Q(CN_DIGIT[m_r.group(1)])
        f_claim = Q(m_f.group(1)) if m_f.lastindex == 1 else Q(CN_DIGIT[m_f.group(2)], CN_DIGIT[m_f.group(1)])
        return r_claim == r and f_claim == left and bool(LOW <= f_claim <= HIGH) and len(text) <= 20

    opts = _same_options(item)
    # the en options carry the zh answer first: they must be the same answers
    assert all(e.startswith(z) for z, e in zip(opts, item["text"]["en"]["options"]))
    # sanity: the long option has the right content, so it fails only on length
    assert any(len(o) > 20 and re.search(r"的三倍", o) for o in opts)
    return [judge(o) for o in opts]


# --- ordering a cross-section -------------------------------------------------------------------------


def _orders(events, older_than):
    """All orders (oldest first) consistent with the 'a is older than b' pairs (a brute-force topological
    sort: the event lists are small)."""
    out = []
    for perm in permutations(events):
        pos = {e: i for i, e in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b in older_than):
            out.append(perm)
    return out


def _seq(text: str) -> tuple[str, ...]:
    """'A、B、F' (zh) or 'A, B, F' (en) -> ('A', 'B', 'F')."""
    return tuple(re.split(r"、|,\s*", text))


def dx_turn_cross_section(item: dict) -> list[bool]:
    """q-order: A, B (bottom to top) cut by fault F; C lies over F's top, not cut; dyke D cuts A, B, C."""
    rel = [
        ("A", "B"), ("B", "C"),  # superposition
        ("A", "F"), ("B", "F"),  # F cuts A and B
        ("F", "C"),  # C covers F's upper end uncut
        ("A", "D"), ("B", "D"), ("C", "D"),  # D cuts A, B, C
    ]
    (only,) = _orders("ABCDF", rel)  # exactly one order
    opts = [_seq(o) for o in item["text"]["zh-tw"]["options"]]
    assert opts == [_seq(o) for o in item["text"]["en"]["options"]]
    return [o == only for o in opts]


def dx_cross_section_words(item: dict) -> list[bool]:
    """q6: P, Q, R bottom to top; dyke S cuts P and Q, and R covers S's top uncut; fault T cuts P, Q, R, S."""
    rel = [
        ("P", "Q"), ("Q", "R"),
        ("P", "S"), ("Q", "S"), ("S", "R"),
        ("P", "T"), ("Q", "T"), ("R", "T"), ("S", "T"),
    ]
    (only,) = _orders("PQRST", rel)
    opts = [_seq(o) for o in item["text"]["zh-tw"]["options"]]
    assert opts == [_seq(o) for o in item["text"]["en"]["options"]]
    return [o == only for o in opts]
