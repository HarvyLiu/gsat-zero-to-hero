"""Checks for src/data/items/biology/s116-natural-selection.yaml (116 sprint: BGb-Ⅴc-1, BMb-Ⅴc-4,
BGb-Ⅴc-2: trait frequencies change with environment and time, development of evolutionary ideas,
Darwin's theory, natural vs artificial selection).

How the keys are recomputed (never from item["answer"]):
- Frequency items run a selection model: each phenotype has a survival fraction in a given
  environment (exact Fractions); survivors reproduce and the next generation keeps their phenotype
  shares (body colour treated as fully heritable, as the chapter's simplified model states).
- Explanations are encoded as sets of features; a rule decides whether a set is a natural-selection
  explanation (heritable variation already present + differential survival/reproduction + passing on
  + frequency change across generations, and no Lamarckian or goal-directed element).
- Rubric, history and theory items use explicit facts tables, one source comment per fact.
"""

from __future__ import annotations

from fractions import Fraction as F

# --- selection model ------------------------------------------------------------------------------


def survivors(counts: dict[str, F], survival: dict[str, F]) -> dict[str, F]:
    """Predation/drug step: each phenotype keeps its survival fraction. Nobody changes phenotype."""
    return {ph: n * survival[ph] for ph, n in counts.items()}


def share(counts: dict[str, F], ph: str) -> F:
    return counts[ph] / sum(counts.values())


def next_generation(counts: dict[str, F], size: F) -> dict[str, F]:
    """Survivors reproduce; offspring keep the survivors' phenotype shares (fully heritable trait)."""
    total = sum(counts.values())
    return {ph: size * n / total for ph, n in counts.items()}


def camouflage_survival(env: str, predated_visible: F, predated_hidden: F) -> dict[str, F]:
    """Camouflage rule (chapter, peppered-moth section): the colour that matches the background is
    harder for predators to see, so a smaller fraction of it is eaten."""
    match = {"dark_ground": "dark", "light_ground": "light"}[env]
    other = "light" if match == "dark" else "dark"
    return {match: 1 - predated_hidden, other: 1 - predated_visible}


def run_generations(start: dict[str, F], survival: dict[str, F], gens: int) -> list[dict[str, F]]:
    out = [start]
    cur = start
    size = sum(start.values())
    for _ in range(gens):
        cur = next_generation(survivors(cur, survival), size)
        out.append(cur)
    return out


# --- explanation model ----------------------------------------------------------------------------
# Natural selection (領綱 BGb-Ⅴc-2 說明 2-2; 112 學測 Q57 評分原則 via nat.json): variation already
# present and heritable; differential survival and reproduction (生存競爭、適者生存); survivors pass the
# trait on; the trait's share in the population rises over generations.
NS_REQUIRED = {"heritable_variation_present", "differential_survival", "passed_on", "share_rises_over_generations"}
# Elements that make an explanation non-Darwinian (research.common_misconceptions: 慢慢適應,
# teleological and Lamarckian models; 112 Q57: 慢慢適應 scored 0).
NS_FORBIDDEN = {"individual_adapts", "goal_directed", "environment_induces_variation", "acquired_trait_inherited"}


def is_natural_selection(features: set[str]) -> bool:
    return NS_REQUIRED <= features and not (features & NS_FORBIDDEN)


# --- opening and mid-chapter turns ---------------------------------------------------------------


def m_turn_cockroach(item: dict) -> list[bool]:
    """q-turn: the same insecticide (bought new every year, so its strength is constant per the stem)
    works less well after some years. Which explanation is most likely?"""
    potency_constant = True  # stated in the stem
    options = [
        {"individual_adapts"},  # 慢慢適應，每一隻越來越不怕
        {"environment_induces_variation"},  # 殺蟲劑讓每一隻產生抗藥突變
        set(NS_REQUIRED),  # 原本就有可遺傳的抗藥個體，存活繁殖，比例逐代上升
        {"goal_directed"},  # 為了生存努力變得抗藥
        {"potency_drop"},  # 藥效自己變弱
    ]
    out = []
    for feats in options:
        if "potency_drop" in feats:
            out.append(not potency_constant)
        else:
            out.append(is_natural_selection(feats))
    return out


def m_turn_tail(item: dict) -> list[bool]:
    """q-tail: tails cut at birth for 20 generations; tail length of generation-21 newborns.
    Model: the newborn tail length is set by the genes in the gametes; cutting changes only the body
    (soma) and never the gametes (chapter: acquired changes are not inherited; 領綱 BGa: traits pass
    through gametes)."""
    normal = F(10)  # newborn tail length set by the genotype (any positive unit)
    genotype_length = normal
    for _ in range(20):
        newborn = genotype_length  # phenotype at birth from the genotype
        body_after_cut = newborn * F(3, 10)  # the cut changes the body only
        assert body_after_cut < newborn
        # gametes carry the genotype unchanged, so genotype_length is not updated from body_after_cut
    gen21 = genotype_length
    lengths_vary = False  # one genotype in the model, so newborns do not split into two groups
    return [
        gen21 == normal,  # 和一般老鼠差不多長
        gen21 < normal and gen21 > 0,  # 比一般老鼠短一些
        gen21 == 0,  # 一出生就沒有尾巴
        gen21 > normal,  # 比一般老鼠長
        lengths_vary,  # 一半有尾巴、一半沒有
    ]


# --- quiz -----------------------------------------------------------------------------------------


def m_beetle_share(item: dict) -> int:
    """q1: 300 green + 100 brown beetles; birds eat 3/5 of green and 1/5 of brown. Brown share of the
    survivors, in percent."""
    start = {"green": F(300), "brown": F(100)}
    surv = survivors(start, {"green": 1 - F(3, 5), "brown": 1 - F(1, 5)})
    pct = share(surv, "brown") * 100
    assert pct.denominator == 1
    return int(pct)


def m_lizard_statements(item: dict) -> list[bool]:
    """q2: lizards with heritable dark/light body colour; light sand, then dark lava. Each statement is
    decided from the camouflage selection model, run over a range of predation fractions."""
    start = {"dark": F(20), "light": F(80)}
    fractions = [F(k, 10) for k in range(1, 10)]
    pairs = [(v, h) for v in fractions for h in fractions if v > h]  # visible prey eaten more

    def dark_trend(env: str) -> set[int]:
        signs = set()
        for v, h in pairs:
            gens = run_generations(start, camouflage_survival(env, v, h), 3)
            d = share(gens[-1], "dark") - share(gens[0], "dark")
            signs.add((d > 0) - (d < 0))
        return signs

    on_lava = dark_trend("dark_ground")
    on_sand = dark_trend("light_ground")
    # (A) on lava, dark individuals survive better: survival(dark) > survival(light) for every pair
    a = all(camouflage_survival("dark_ground", v, h)["dark"] > camouflage_survival("dark_ground", v, h)["light"] for v, h in pairs)
    # (B) lava turns light lizards dark: the model never changes an individual's phenotype
    surv = survivors(start, camouflage_survival("dark_ground", F(1, 2), F(1, 4)))
    b = surv["dark"] > start["dark"]  # more dark individuals after the step only if light ones turned dark
    # (C) if sand covers the lava again, the light share can rise again
    c = on_sand == {-1}
    # (D) dark is favoured in every environment
    d = on_lava == {1} and on_sand == {1}
    # (E) the change is in the population's shares across generations, not within one individual
    e = on_lava == {1} and not b
    return [a, b, c, d, e]


# History facts (well-established; BMb-Ⅴc-4 說明 4-1 asks for the history of evolutionary ideas):
# Lamarck proposed use and disuse and the inheritance of acquired traits (1809 book); Darwin published
# On the Origin of Species in 1859 with natural selection and common ancestry; Wallace conceived natural
# selection independently (joint papers 1858). Fixed species was the older view the theory replaced.
HISTORY = {
    "拉馬克": {"use_and_disuse", "acquired_inheritance", "book_1809"},
    "達爾文": {"origin_1859", "natural_selection", "common_ancestry", "beagle_1831_1836"},
    "華萊士": {"natural_selection_independently", "papers_1858"},
}


def m_history_pairs(item: dict) -> list[bool]:
    """q3: which person-contribution pairing is correct?"""
    options = [
        ("拉馬克", {"use_and_disuse", "acquired_inheritance"}),
        ("拉馬克", {"origin_1859", "natural_selection"}),
        ("達爾文", {"fixed_species"}),
        ("華萊士", {"fixed_species"}),
        ("華萊士", {"book_1809", "use_and_disuse"}),
    ]
    return [claims <= HISTORY[who] for who, claims in options]


def m_missing_step(item: dict) -> list[bool]:
    """q4: a student's answer has only differential survival. Which addition completes a
    natural-selection explanation without adding a wrong element?"""
    student = {"differential_survival"}
    options = [
        {"heritable_variation_present", "passed_on", "share_rises_over_generations"},
        {"goal_directed"},
        {"environment_makes_stronger"},
        {"individual_adapts"},
        set(),  # nothing needed
    ]
    forbidden = NS_FORBIDDEN | {"environment_makes_stronger"}
    return [bool(add) and is_natural_selection(student | add) and not (add & forbidden) if add else is_natural_selection(student) for add in options]


def m_complete_explanation(item: dict) -> list[bool]:
    """q5 (hypothetical grazing case): which student explanation of the rise of short plants is a
    complete natural-selection explanation? Each option is encoded by the elements it states and
    decided by is_natural_selection (NS_REQUIRED present, nothing from NS_FORBIDDEN)."""
    options = [
        {"goal_directed", "acquired_trait_inherited", "passed_on"},  # 為了不再被吃而努力變矮，傳給後代
        {"environment_induces_variation", "passed_on"},  # 啃食使植物產生矮小的突變
        set(NS_REQUIRED),  # 原本就有可遺傳的高矮差異；矮株存活、留下較多後代；許多代後比例上升
        {"differential_survival"},  # 只寫矮的比較容易存活
        {"individual_adapts"},  # 每一株慢慢適應、越長越矮
    ]
    return [is_natural_selection(f) for f in options]


def m_artificial(item: dict) -> list[bool]:
    """q6: which cases are artificial selection? Criterion (chapter; 113 Q37–39 broilers): people decide
    which individuals breed, by a trait they want. Otherwise the environment selects (natural
    selection), even when people changed the environment, as with antibiotics (112 Q57 rubric: 天擇)
    and, by the same criterion, a weedkiller."""
    cases = [
        {"selector": "human", "by_desired_trait": True},  # 稻：只留產量最高的種子
        {"selector": "human", "by_desired_trait": True},  # 狗：讓毛色合意的互相交配
        {"selector": "environment", "by_desired_trait": False},  # 除草劑：藥劑留下抗除草劑的雜草
        {"selector": "environment", "by_desired_trait": False},  # 乾旱：深根野草存活
        {"selector": "environment", "by_desired_trait": False},  # 鳥喙隨種子大小改變
    ]
    return [c["selector"] == "human" and c["by_desired_trait"] for c in cases]


# Darwin's theory (領綱 BGb-Ⅴc-2 說明 2-1, 2-2): all organisms descend from common ancestors with change
# over many generations; natural selection acts on existing heritable variation and changes trait shares
# in populations, not individuals within their lifetime; the environment does not create the variation
# it needs (research.common_misconceptions: teleological/Lamarckian models).
DARWIN_CLAIMS = {
    "common_ancestry_change_over_generations": True,
    "selection_changes_individual_in_lifetime": False,
    "unit_is_individual_population_unchanged": False,
    "species_fixed": False,
    "environment_creates_needed_variation": False,
}


def m_darwin_theory(item: dict) -> list[bool]:
    """q7: which statement belongs to Darwin's theory of evolution?"""
    options = [
        "common_ancestry_change_over_generations",
        "selection_changes_individual_in_lifetime",
        "unit_is_individual_population_unchanged",
        "species_fixed",
        "environment_creates_needed_variation",
    ]
    return [DARWIN_CLAIMS[o] for o in options]
