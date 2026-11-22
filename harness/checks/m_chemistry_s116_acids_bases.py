"""Checks for src/data/items/chemistry/s116-acids-bases.yaml (116 sprint: CJd-Ⅴc-1 to CJd-Ⅴc-4,
acid–base reactions).

Every check recomputes its item's key from the chemistry in the stem, never from item["answer"]:
- concentrations are exact SymPy Rationals; at 25 ℃ [H+][OH-] = KW = 1.00 × 10^-14 (課綱 CJd-Ⅴc 說明);
- pH = -log10[H+], taken exactly (every stem is built so the result is an integer);
- strong electrolytes ionize completely; weak ones only partly (a fraction strictly between 0 and 1);
- the strong/weak/non-electrolyte class of each species comes from one table (standard 必修 chemistry,
  the same lists the chapter teaches);
- indicator colours become pH intervals from the table the stem states, and are intersected;
- neutralization: at exact, complete neutralization the moles of H+ and OH- (n = C × V) are equal.
"""

from __future__ import annotations

from sympy import Integer, Rational, log, nsimplify, sqrt

KW = Integer(10) ** -14  # 25 ℃, as every stem states

# Class of each species in water (standard 必修 chemistry; the chapter's lists):
# strong acid / strong base ionize completely; weak acid / weak base ionize partly; nonelectrolytes not at all.
# "h" / "oh" = how many H+ or OH- one formula unit can release.
SPECIES = {
    "HCl": {"cls": "strong acid", "h": 1},
    "HNO3": {"cls": "strong acid", "h": 1},
    "CH3COOH": {"cls": "weak acid", "h": 1},
    "NaOH": {"cls": "strong base", "oh": 1},
    "KOH": {"cls": "strong base", "oh": 1},
    "Ba(OH)2": {"cls": "strong base", "oh": 2},
    "NH3": {"cls": "weak base", "oh": 1},
    "C12H22O11": {"cls": "nonelectrolyte"},
}
STRONG = {"strong acid", "strong base"}
WEAK = {"weak acid", "weak base"}

# A weak electrolyte's ionized fraction: any value with 0 < f < 1 gives the same comparisons below.
# 1/100 is the chapter's "about 1 %" for 0.10 M acetic acid; the checks only use 0 < f < 1.
WEAK_FRACTION = Rational(1, 100)


def fraction(formula: str) -> Rational:
    cls = SPECIES[formula]["cls"]
    if cls in STRONG:
        return Integer(1)
    if cls in WEAK:
        return WEAK_FRACTION
    return Integer(0)


def ph_of(h) -> int:
    """Exact pH of [H+] = h; the stems are built so that it is an integer."""
    p = nsimplify(-log(h, 10))
    assert p.is_integer, f"pH of {h} is not an integer"
    return int(p)


def h_from_oh(oh) -> Rational:
    return KW / oh


def h_after_diluting_acid(acid_h) -> Rational:
    """[H+] of an acid solution including water's own ions: x(x - a) = KW → x = a/2 + sqrt(a²/4 + KW)."""
    return acid_h / 2 + sqrt(acid_h**2 / 4 + KW)


def nature(h) -> str:
    oh = KW / h
    return "acidic" if h > oh else "basic" if h < oh else "neutral"


# ---------------------------------------------------------------------------------------------------


def ab_turn_pure_water(item: dict) -> list[bool]:
    """q-turn: pure water self-ionizes, H2O <=> H+ + OH-, one H+ for each OH-, so [H+] = [OH-] and
    [H+]² = KW → [H+] = 10^-7 > 0. Options: none; equal to OH-; more than OH-; no H+, only OH-."""
    h = sqrt(KW)
    oh = KW / h
    preds = [
        h == 0,                     # 沒有 H+
        h > 0 and h == oh,          # 有，和 OH- 一樣多
        h > oh,                     # 有，比 OH- 多
        h == 0 and oh > 0,          # 只有 OH-
    ]
    return preds


def ab_mid_bulbs(item: dict) -> list[bool]:
    """q-mid: 0.10 M HCl vs 0.10 M CH3COOH; bulb brightness follows the ion concentration
    (each ionized molecule gives 2 ions). Options: HCl brighter; acetic brighter; equal; neither lights."""
    c = Rational(1, 10)
    ions = {f: 2 * c * fraction(f) for f in ("HCl", "CH3COOH")}
    a, b = ions["HCl"], ions["CH3COOH"]
    return [a > b, b > a, a == b and a > 0, a == 0 and b == 0]


def ab_ph_from_hydroxide(item: dict) -> list[bool]:
    """q1: [OH-] = 1.0 × 10^-4 → [H+] = 10^-10 → pH 10. Options: 4, 7, 10, -4, 14."""
    p = ph_of(h_from_oh(Integer(10) ** -4))
    return [p == o for o in (4, 7, 10, -4, 14)]


def ab_barium_hydroxide_ph(item: dict) -> tuple[int, int]:
    """q2: 0.0050 M Ba(OH)2, strong base with 2 OH- per unit → [OH-] = 0.010 → [H+] = 10^-12 → pH 12."""
    s = SPECIES["Ba(OH)2"]
    oh = Rational(5, 1000) * s["oh"] * fraction("Ba(OH)2")
    p = ph_of(h_from_oh(oh))
    return (p // 10, p % 10)


def ab_kw_statements(item: dict) -> list[bool]:
    """q3: each statement about 25 ℃ solutions recomputed from KW.
    (1) [H+] = 1e-5 → acidic?  (2) [OH-] = 1e-9 → basic?  (3) [H+](pH 3) / [H+](pH 5) = 100?
    (4) pH 6: [OH-] > [H+]?  (5) 0.010 M NaOH has [H+] = 0?"""
    ten = Integer(10)
    s1 = nature(ten**-5) == "acidic"
    s2 = nature(h_from_oh(ten**-9)) == "basic"
    s3 = ten**-3 / ten**-5 == 100
    h6 = ten**-6
    s4 = KW / h6 > h6
    s5 = h_from_oh(Rational(1, 100) * fraction("NaOH")) == 0
    return [s1, s2, s3, s4, s5]


# q4: the indicator table in the stem: colour → open pH interval (lo, hi); None = no bound.
INDICATORS = {
    "methyl orange": {"red": (None, Rational("3.1")), "orange": (Rational("3.1"), Rational("4.4")),
                      "yellow": (Rational("4.4"), None)},
    "bromothymol blue": {"yellow": (None, Rational("6.0")), "green": (Rational("6.0"), Rational("7.6")),
                         "blue": (Rational("7.6"), None)},
    "phenolphthalein": {"colourless": (None, Rational("8.2")), "pale pink": (Rational("8.2"), Rational(10)),
                        "pink": (Rational(10), None)},
}


def ab_indicator_range(item: dict) -> list[bool]:
    """q4: methyl orange yellow, bromothymol blue green, phenolphthalein colourless → intersect the
    three intervals → 6.0 < pH < 7.6. Options: <3.1; 3.1–4.4; 4.4–6.0; 6.0–7.6; 7.6–8.2."""
    seen = {"methyl orange": "yellow", "bromothymol blue": "green", "phenolphthalein": "colourless"}
    lo, hi = Integer(0), Integer(14)
    for ind, colour in seen.items():
        a, b = INDICATORS[ind][colour]
        if a is not None:
            lo = max(lo, a)
        if b is not None:
            hi = min(hi, b)
    assert lo < hi
    options = [(Integer(0), Rational("3.1")), (Rational("3.1"), Rational("4.4")), (Rational("4.4"), Rational("6.0")),
               (Rational("6.0"), Rational("7.6")), (Rational("7.6"), Rational("8.2"))]
    return [(lo, hi) == o for o in options]


def ab_neutralize_volume(item: dict) -> list[bool]:
    """q5: 25.0 mL of 0.20 M HCl; n(H+) = 5.0 mmol = n(OH-) → V = 5.0 / 0.10 = 50.0 mL.
    Options (mL): 5.0, 12.5, 25.0, 50.0, 100."""
    n_h = Rational(20, 100) * 25 * SPECIES["HCl"]["h"]  # mmol
    v = n_h / (Rational(10, 100) * SPECIES["NaOH"]["oh"])
    return [v == o for o in (Integer(5), Rational(25, 2), Integer(25), Integer(50), Integer(100))]


def ab_strong_electrolytes(item: dict) -> list[bool]:
    """q6: which are strong electrolytes? Looked up in SPECIES. Options: HNO3, CH3COOH, KOH, NH3, C12H22O11."""
    return [SPECIES[f]["cls"] in STRONG for f in ("HNO3", "CH3COOH", "KOH", "NH3", "C12H22O11")]


def ab_strength_vs_concentration(item: dict) -> list[bool]:
    """q7: A 0.10 M HCl, B 0.00010 M HCl, C 0.10 M CH3COOH (25 ℃).
    (1) B is weak because dilute?  (2) [H+] of A == [H+] of C?  (3) pH(A) = 1 and pH(B) = 4?
    (4) diluting C enough makes it basic?  (5) A conducts worse than C?"""
    sol = {"A": ("HCl", Rational(1, 10)), "B": ("HCl", Rational(1, 10000)), "C": ("CH3COOH", Rational(1, 10))}
    h = {k: c * fraction(f) for k, (f, c) in sol.items()}
    ions = {k: 2 * v for k, v in h.items()}
    s1 = SPECIES[sol["B"][0]]["cls"] in WEAK
    s2 = h["A"] == h["C"]
    s3 = ph_of(h["A"]) == 1 and ph_of(h["B"]) == 4
    # dilute C a millionfold and a billionfold: the acid's H+ plus water's own ions never leaves it basic
    s4 = any(nature(h_after_diluting_acid(h["C"] / Integer(10) ** k)) == "basic" for k in (3, 6, 9, 12))
    s5 = ions["A"] < ions["C"]
    return [s1, s2, s3, s4, s5]


def ab_exact_neutralization_conc(item: dict) -> tuple[int, int]:
    """q8: 25.0 mL HNO3 of unknown concentration is exactly neutralized by 20.0 mL of 0.050 M Ba(OH)2
    (2 OH- per unit). n(OH-) = 2 × 0.050 × 20.0 = 2.0 mmol = n(H+) → C = 2.0 / 25.0 = 0.080 M.
    The stem writes the answer as 0.0①② M, so the digits are those of 1000 × C."""
    n_oh = Rational(50, 1000) * 20 * SPECIES["Ba(OH)2"]["oh"] * fraction("Ba(OH)2")  # mmol
    c_acid = n_oh / (Integer(25) * SPECIES["HNO3"]["h"] * fraction("HNO3"))  # mol/L
    digits = c_acid * 1000
    assert digits.is_integer and 10 <= digits < 100
    return (int(digits) // 10, int(digits) % 10)
