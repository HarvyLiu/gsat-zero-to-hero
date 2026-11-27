"""Checks for the biology items of inquiry/s116-sci-mock (original science practice paper):
Part 1 q19-q27 and the Part 2 biology set q47-q49.

Every key is recomputed from the data stated in the stem, never read from item["answer"]:
- numbers (micrometer divisions, CO2 rates, chromosome counts, cross fractions) with exact Fractions;
- crosses by enumerating gametes (segregation, independent assortment), sex-linked crosses with X/Y;
- trees by checking every triple of tips against the DNA difference table;
- qualitative statements from facts tables, each fact citing the reviewed biology sprint chapter
  (src/content/lessons/zh-tw/biology/<slug>.mdx) it comes from.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations, product

# --- q19: eyepiece micrometer ---------------------------------------------------------------------
# Source: biology/s116-cell-theory-structure, 測微器 section: the eyepiece micrometer's scale is not
# magnified by the objective; the cell's image is, so divisions scale with the objective's
# magnification, and sizes are compared at one magnification.


def bio_micrometer_two_objectives(item: dict) -> list[bool]:
    """A: 12 divisions at 10x; B: 16 divisions at 40x. Length A / length B.
    Options: 1/3, 3/4, 4/3, 3, 12."""
    a_div, a_obj = 12, 10
    b_div, b_obj = 16, 40
    a_at_b_obj = F(a_div) * F(b_obj, a_obj)  # A's image at B's objective
    ratio = a_at_b_obj / b_div
    return [ratio == o for o in [F(1, 3), F(3, 4), F(4, 3), F(3), F(12)]]


# --- q20: prokaryotic and eukaryotic cells --------------------------------------------------------
# Source: biology/s116-cell-theory-structure, 原核細胞 section and its table: bacteria and cyanobacteria
# are prokaryotes (no nucleus, no membrane-bound organelles such as chloroplasts, but ribosomes;
# most have a cell wall; cyanobacteria photosynthesise without chloroplasts); fungi (yeast) and
# protists (Paramecium) are eukaryotes with a nucleus enclosed by a nuclear membrane.
KINGDOM = {"cyanobacteria": "pro", "E. coli": "pro", "yeast": "eu", "Paramecium": "eu"}
HAS = {
    "pro": {"ribosome": True, "chloroplast": False, "nucleus": False},
    "eu": {"ribosome": True, "nucleus": True},
}
CYANO_PHOTOSYNTHESISES = True
BACTERIA_WALL = "most"  # 大多數有細胞壁


def bio_pro_eu_statements(item: dict) -> list[bool]:
    return [
        CYANO_PHOTOSYNTHESISES and HAS[KINGDOM["cyanobacteria"]]["chloroplast"],
        HAS[KINGDOM["cyanobacteria"]]["ribosome"] and HAS[KINGDOM["E. coli"]]["ribosome"],
        HAS[KINGDOM["yeast"]]["nucleus"],
        BACTERIA_WALL == "none",
        KINGDOM["Paramecium"] == "pro",
    ]


# --- q21: CO2 in a sealed box ---------------------------------------------------------------------
# Source: biology/s116-cell-energy, 讀圖 section: in the dark only respiration (CO2 rises); in light the
# sensor sees respiration released minus photosynthesis taken up; respiration rate assumed constant.
CO2 = {0: 40, 1: 43, 2: 46, 3: 45, 4: 44, 5: 38, 6: 32}


def _rate(t0: int, t1: int) -> F:
    return F(CO2[t1] - CO2[t0], t1 - t0)


def bio_co2_three_phases(item: dict) -> list[bool]:
    """Dark 0-2 h, dim 2-4 h, bright 4-6 h. Gross uptake per hour in bright light.
    Options: 3, 4, 6, 9, 12."""
    resp = _rate(0, 2)
    assert _rate(0, 1) == _rate(1, 2) == resp and _rate(4, 5) == _rate(5, 6)
    uptake_bright = resp - _rate(4, 6)  # seen = resp - uptake
    uptake_dim = resp - _rate(2, 4)
    assert uptake_dim == 4  # distractor (2)
    return [uptake_bright == o for o in [3, 4, 6, 9, 12]]


# --- q22: eggs and the zygote ---------------------------------------------------------------------
# Source: biology/s116-cell-division, 減數分裂 and 受精 sections: one germ cell -> four cells by meiosis;
# in a female only one becomes an egg; gametes are n; zygote n + n = 2n.


def bio_eggs_and_zygote(item: dict) -> list[bool]:
    two_n, cells = 18, 10
    eggs_per_cell = 1
    eggs = cells * eggs_per_cell
    n = two_n // 2
    zygote = n + n
    opts = [(40, 9, 18), (10, 9, 18), (10, 18, 36), (40, 18, 18), (20, 9, 18)]
    return [o == (eggs, n, zygote) for o in opts]


# --- q23: two-gene cross --------------------------------------------------------------------------
# Source: biology/s116-mendel (segregation, independent assortment, complete dominance).


def _gametes(genotype: list[str]) -> dict[tuple[str, ...], F]:
    out: dict = {}
    for choice in product(*[list(pair) for pair in genotype]):
        out[choice] = out.get(choice, F(0)) + F(1, 2 ** len(genotype))
    return out


def bio_dihybrid_rrnn_x_rrnn(item: dict) -> list[bool]:
    """RrNn x Rrnn: fraction red (R_) and round (N_). Options 1/8, 3/16, 1/4, 3/8, 9/16."""
    p = F(0)
    for g1, p1 in _gametes(["Rr", "Nn"]).items():
        for g2, p2 in _gametes(["Rr", "nn"]).items():
            child = list(zip(g1, g2))
            if all(any(a.isupper() for a in pair) for pair in child):
                p += p1 * p2
    return [p == o for o in [F(1, 8), F(3, 16), F(1, 4), F(3, 8), F(9, 16)]]


# --- q24: sex-linked recessive (red-green colour blindness) ---------------------------------------
# Source: biology/s116-chromosomes-sex-linked: gene on X; father passes X to daughters and Y to sons;
# a son's X comes from his mother; colour blind = no dominant X^A.
X_GENOS_F = [("A", "A"), ("A", "a"), ("a", "a")]


def _female_blind(g) -> bool:
    return "A" not in g


def bio_colourblind_grandfather(item: dict) -> list[bool]:
    grandfather_x = "a"  # colour-blind man X^aY
    # daughter: X from father (a) + one X from her mother (any allele); she has normal vision
    daughters = {tuple(sorted((grandfather_x, m))) for m in "Aa"}
    daughters = {d for d in daughters if not _female_blind(d)}
    must_carry = all("a" in d for d in daughters)
    (mother,) = daughters
    husband_x = "A"
    sons = {m: F(1, 2) for m in mother}  # son's X from mother, Y from father
    p_son_blind = sum((p for x, p in sons.items() if x == "a"), F(0))
    daughters2 = [tuple(sorted((m, husband_x))) for m in mother]
    daughter_can_be_blind = any(_female_blind(d) for d in daughters2)
    # the mother's a came from her father (her mother contributed the A she needs for normal vision)
    son_allele_from_grandfather = "a" in mother and grandfather_x == "a" and "A" in mother
    p_child_blind = F(1, 2) * p_son_blind + F(1, 2) * F(sum(_female_blind(d) for d in daughters2), 2)
    return [
        must_carry,
        p_son_blind == F(1, 2),
        daughter_can_be_blind,
        son_allele_from_grandfather,
        p_child_blind == F(1, 2),
    ]


# --- q25: blocking transcription ------------------------------------------------------------------
# Source: biology/s116-molecular-genetics, 中心法則 and 在細胞的哪裡進行 sections: transcription makes RNA
# from DNA, in the nucleus of a eukaryotic cell; translation joins amino acids into protein on
# ribosomes in the cytoplasm; protein is made only by way of RNA; replication is a separate step.
STEP = {
    "transcription": {"makes": "RNA", "where": "nucleus"},
    "translation": {"makes": "protein", "where": "ribosome"},
    "replication": {"makes": "DNA", "where": "nucleus"},
}
DNA_TO_PROTEIN_DIRECT = False


def bio_block_transcription(item: dict) -> list[bool]:
    blocked = "transcription"
    direct = (STEP[blocked]["makes"], STEP[blocked]["where"])
    opts = [
        ("RNA", "nucleus"),
        ("RNA", "ribosome"),
        ("DNA", "nucleus"),  # replication stops
        None,  # protein unaffected because DNA is translated directly
        ("protein", "ribosome"),  # translation blocked directly
    ]
    out = [o == direct for o in opts]
    out[3] = DNA_TO_PROTEIN_DIRECT
    return out


# --- q26: natural selection on beak thickness -----------------------------------------------------
# Source: biology/s116-natural-selection, 天擇 section (four steps: pre-existing heritable variation;
# competition; the fit survive and leave more offspring; accumulation over generations; "fit"
# depends on the environment at the time) and 演化觀念的發展 (Lamarck's use and disuse is not
# natural selection); 天擇與人擇 (artificial selection: people do the selecting).
SELECTION_RULES = {
    "acquired_traits_inherited": False,
    "variation_before_change": True,
    "fit_survive_more_offspring": True,
    "trend_continues_after_environment_changes": False,
    "selector_is_people": False,
}


def bio_beak_selection(item: dict) -> list[bool]:
    keys = [
        "acquired_traits_inherited",
        "variation_before_change",
        "fit_survive_more_offspring",
        "trend_continues_after_environment_changes",
        "selector_is_people",
    ]
    return [SELECTION_RULES[k] for k in keys]


# --- q27: tree from a DNA difference table --------------------------------------------------------
# Source: biology/s116-classification-biodiversity, 證據二 and 讀親緣關係樹 sections: the more similar
# the DNA, the more recent the common ancestor usually is; tips that meet at a branch point nearer
# the tips are more closely related.
D = {
    frozenset("甲乙"): 3,
    frozenset("甲丙"): 8,
    frozenset("乙丙"): 8,
    frozenset("甲丁"): 13,
    frozenset("乙丁"): 13,
    frozenset("丙丁"): 13,
}


def _parse(s: str):
    s = s.replace(" ", "")
    pos = 0

    def node():
        nonlocal pos
        if s[pos] == "(":
            pos += 1
            left = node()
            assert s[pos] == ","
            pos += 1
            right = node()
            assert s[pos] == ")"
            pos += 1
            return (left, right)
        leaf = s[pos]
        pos += 1
        return leaf

    t = node()
    assert pos == len(s)
    return t


def _leaves(t) -> frozenset:
    return frozenset([t]) if isinstance(t, str) else _leaves(t[0]) | _leaves(t[1])


def _clades(t) -> list[frozenset]:
    if isinstance(t, str):
        return []
    return [_leaves(t)] + _clades(t[0]) + _clades(t[1])


def _closest_pair_in_tree(t, trio: frozenset):
    """The pair of the trio inside the smallest clade holding two of them (None if unresolved)."""
    for c in sorted(_clades(t), key=len):
        inside = c & trio
        if len(inside) == 2:
            return inside
    return None


def bio_tree_from_dna(item: dict) -> list[bool]:
    opts = ["(((甲,乙),丙),丁)", "((甲,乙),(丙,丁))", "(((甲,丙),乙),丁)", "(((乙,丙),甲),丁)", "(((甲,丁),乙),丙)"]
    tips = frozenset("甲乙丙丁")

    def fits(tree) -> bool:
        for trio in combinations(sorted(tips), 3):
            trio = frozenset(trio)
            pairs = [frozenset(p) for p in combinations(sorted(trio), 2)]
            best = min(D[p] for p in pairs)
            closest = [p for p in pairs if D[p] == best]
            if len(closest) != 1:
                continue  # the data do not order this trio
            if _closest_pair_in_tree(tree, trio) != closest[0]:
                return False
        return True

    return [fits(_parse(o)) for o in opts]


# --- q47-q49: enzyme and temperature set ----------------------------------------------------------
# Source: biology/s116-cell-energy, 酵素 section: enzymes are biological catalysts, mostly proteins, not
# used up by the reaction; rate rises to an optimum temperature then falls steeply; overheating
# destroys the structure and cooling usually does not restore it.
ENZYME = {"used_up": False, "mostly_protein": True, "heat_damage_reversible": False}
# q47 stem (illustrative): cumulative product (mg) every 2 min at 30 and 50 degC; the stem states that
# the substrate does not run out within 10 min. (This time-course setting differs from the
# rate-against-temperature data of inquiry/s116-inq-argue-model.)
TIMES = [0, 2, 4, 6, 8, 10]
CUM = {30: [0, 4, 8, 12, 16, 20], 50: [0, 7, 11, 13, 14, 14]}
SUBSTRATE_RUNS_OUT = False  # stated in the stem


def _avg_rate(temp: int, t0: int, t1: int) -> F:
    """Average rate over an interval = increase in cumulative product / time (inquiry/s116-sci-plot-and-
    working: a rate is a change divided by the time it took, read from the data, not a total / time)."""
    c = dict(zip(TIMES, CUM[temp]))
    return F(c[t1] - c[t0], t1 - t0)


def bio_enzyme_time_course(item: dict) -> list[bool]:
    intervals = list(zip(TIMES, TIMES[1:]))
    hot_faster_every_interval = all(_avg_rate(50, a, b) > _avg_rate(30, a, b) for a, b in intervals)
    first_rates = (_avg_rate(50, 0, 2), _avg_rate(30, 0, 2))
    s2 = first_rates == (F(7, 2), F(2)) and first_rates[0] > first_rates[1]
    # (3) the plateau is real (increase after 6 min at most 1 mg), but the stated cause contradicts the stem
    plateau = CUM[50][-1] - CUM[50][TIMES.index(6)] <= 1
    s3 = plateau and SUBSTRATE_RUNS_OUT
    # (4) the premise is true (30 degC has more at 10 min) but the conclusion is about the start
    s4 = CUM[30][-1] > CUM[50][-1] and first_rates[1] > first_rates[0]
    # (5) the late rate is the increase, not the total divided by the time
    s5 = _avg_rate(50, 8, 10) == 7
    assert F(CUM[50][-1], 2) == 7  # the distractor's total / time
    return [hot_faster_every_interval, s2, s3, s4, s5]


# q48: a control differs from the experimental tubes in only the factor in doubt.
# Source: inquiry/s116x-cross-subject-data (對照組: same set-up without the one factor, used to
# subtract its effect) and biology/s116-cell-energy (the enzyme set-up).
EXPERIMENT = {"enzyme": True, "substrate": True, "temps": 2, "time_min": 10, "enzyme_source": "same", "enzyme_amount": 1}


def bio_enzyme_control(item: dict) -> list[bool]:
    designs = [
        {**EXPERIMENT, "enzyme": False},  # water instead of enzyme
        {**EXPERIMENT, "temps": 1, "enzyme_amount": 2},
        {**EXPERIMENT, "substrate": False},
        {**EXPERIMENT, "time_min": 20},
        {**EXPERIMENT, "enzyme_source": "other"},
    ]
    doubt = "enzyme"  # does product appear without the enzyme?

    def tests_doubt(d) -> bool:
        changed = {k for k in EXPERIMENT if d[k] != EXPERIMENT[k]}
        return changed == {doubt} and d["substrate"]

    return [tests_doubt(d) for d in designs]


def bio_enzyme_pretreatment(item: dict) -> bool:
    """q49 (written): tube X (10 min at 50 degC first) makes 1 mg in 10 min back at 30 degC, tube Y
    (10 min at 10 degC first) 20 mg; a tube kept at 10 degC makes 5 mg. The rubric compares both with
    the 30 degC tube of q47 (20 mg at 10 min). Heat damage not reversed is a fact from
    biology/s116-cell-energy; the cold result is an inference from these data (the stem says so),
    so the check only confirms the data support it. Four 1-point criteria, as the page states."""
    x_after, y_after, kept_cold = 1, 20, 5
    kept_at_30 = CUM[30][TIMES.index(10)]
    heat_not_recovered = x_after < kept_at_30 and not ENZYME["heat_damage_reversible"]
    cold_slows = kept_cold < kept_at_30
    cold_recovered = y_after == kept_at_30
    crit = item["rubric"]["criteria"]
    four_ones = len(crit) == 4 and all(c["points"] == 1 for c in crit)
    model = item["model"]["zh-tw"]
    quoted = all(f"${n}$ mg" in model for n in (x_after, y_after, kept_cold, kept_at_30))
    return heat_not_recovered and cold_slows and cold_recovered and four_ones and quoted
