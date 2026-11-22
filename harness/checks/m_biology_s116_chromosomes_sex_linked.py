"""Checks for src/data/items/biology/s116-chromosomes-sex-linked.yaml (116 sprint: BMb-Ⅴc-3, BGa-Ⅴc-3,
BGa-Ⅴc-4: the chromosome theory of inheritance, the discovery of sex chromosomes, sex-linked inheritance
with red-green colour blindness, pedigrees that rule sex-linkage in or out).

How the keys are recomputed (never from item["answer"]):
- X-linked crosses enumerate gametes with exact Fractions. A female is a pair of X alleles, a male is
  (X allele, 'Y'). Each parent passes one of its two sex chromosomes with probability 1/2; a child that
  gets the father's Y is male and its only X comes from the mother. Y carries no allele of the gene.
- Autosomal crosses use the same segregation rule (each allele to half the gametes).
- Phenotypes come from a dominance rule: the capital allele 'A' is dominant. Under a "dominant trait"
  hypothesis the trait shows when 'A' is present; under a "recessive trait" hypothesis it shows when
  'A' is absent.
- Pedigrees test every genotype assignment of every person under each of four hypotheses (autosomal
  dominant / recessive, X-linked dominant / recessive); a hypothesis survives when some assignment fits
  every phenotype and every child can come from its parents.
- Chromosome counts follow the rule 2n = 46 with one pair of sex chromosomes (國中 Ga-Ⅳ-2, chapter
  s116-cell-division).
- History and qualitative statements come from explicit tables, each fact with its source.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import product

# --- genetics engine ------------------------------------------------------------------------------

Y = "Y"


def _gam(geno: tuple[str, str]) -> dict[str, F]:
    """Segregation: each of the two (sex) chromosomes / alleles goes to half the gametes."""
    out: dict[str, F] = {}
    for a in geno:
        out[a] = out.get(a, F(0)) + F(1, 2)
    return out


def x_cross(mother: tuple[str, str], father: tuple[str, str]) -> dict[tuple[str, tuple[str, str]], F]:
    """X-linked cross. mother = (x1, x2); father = (x, 'Y'). Returns {(sex, genotype): probability};
    a daughter's pair is sorted (Aa == aA), a son is (x from the mother, 'Y')."""
    assert Y not in mother and father[1] == Y and father[0] != Y
    out: dict = {}
    for egg, pe in _gam(mother).items():
        for sperm, ps in _gam(father).items():
            if sperm == Y:
                child = ("M", (egg, Y))
            else:
                child = ("F", tuple(sorted((egg, sperm))))
            out[child] = out.get(child, F(0)) + pe * ps
    assert sum(out.values()) == 1
    return out


def x_cross_with_origin(mother, father):
    """Like x_cross but also records which parent gave each 'a' allele: {(sex, geno, origins): p}."""
    out: dict = {}
    for egg, pe in _gam(mother).items():
        for sperm, ps in _gam(father).items():
            origins = tuple(sorted(({"mother"} if egg == "a" else set()) | ({"father"} if sperm == "a" else set())))
            if sperm == Y:
                child = ("M", (egg, Y), origins)
            else:
                child = ("F", tuple(sorted((egg, sperm))), origins)
            out[child] = out.get(child, F(0)) + pe * ps
    return out


def auto_cross(mother: tuple[str, str], father: tuple[str, str]) -> dict[tuple[str, tuple[str, str]], F]:
    """Autosomal cross; sex is decided independently by the sex chromosomes (half sons, half daughters)."""
    out: dict = {}
    for a, pa in _gam(mother).items():
        for b, pb in _gam(father).items():
            for sex in ("F", "M"):
                child = (sex, tuple(sorted((a, b))))
                out[child] = out.get(child, F(0)) + pa * pb * F(1, 2)
    assert sum(out.values()) == 1
    return out


FEMALE_X = [("A", "A"), ("A", "a"), ("a", "a")]
MALE_X = [("A", Y), ("a", Y)]
AUTO = [("A", "A"), ("A", "a"), ("a", "a")]

HYPOTHESES = ["auto_dom", "auto_rec", "x_dom", "x_rec"]


def shows(hyp: str, geno: tuple[str, str]) -> bool:
    """Does an individual with this genotype show the trait under the hypothesis? 'A' is dominant."""
    has_dominant = "A" in geno
    return has_dominant if hyp.endswith("dom") else not has_dominant


def genotypes_for(hyp: str, sex: str):
    if hyp.startswith("auto"):
        return AUTO
    return FEMALE_X if sex == "F" else MALE_X


def cross_for(hyp: str, mother, father):
    return auto_cross(mother, father) if hyp.startswith("auto") else x_cross(mother, father)


def consistent(hyp: str, people: dict[str, tuple[str, bool]], families: list[tuple[str, str, list[str]]]) -> bool:
    """people: name -> (sex 'F'/'M', shows trait); families: (mother, father, children).
    True when some genotype assignment fits every phenotype and every child is possible."""
    names = list(people)
    choices = [[g for g in genotypes_for(hyp, people[n][0]) if shows(hyp, g) == people[n][1]] for n in names]
    for combo in product(*choices):
        assign = dict(zip(names, combo))
        ok = True
        for m, f, kids in families:
            dist = cross_for(hyp, assign[m], assign[f])
            for k in kids:
                if dist.get((people[k][0], assign[k]), F(0)) == 0:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def surviving(people, families) -> list[bool]:
    return [consistent(h, people, families) for h in HYPOTHESES]


# Red-green colour blindness: X-linked recessive (領綱 BGa-Ⅴc-4 說明 4-1 uses it as the example of
# sex-linked inheritance; 考試說明 生物 試題示例1 writes carriers as XAXa). In the engine 'a' = colour-blind.
CB = "x_rec"


def cb_affected(sex: str, geno) -> bool:
    return shows(CB, geno)


# --- opening and mid-chapter turns ---------------------------------------------------------------


def m_turn_source(item: dict) -> list[bool]:
    """q-turn: a colour-normal couple has a colour-blind son. Who gave the son his colour-blind allele?
    Enumerate every genotype pair with normal colour vision and every route to an affected son.
    Options: father; mother; one from each; neither parent (it appeared later); either, can't tell."""
    routes = set()
    for m in FEMALE_X:
        for f in MALE_X:
            if cb_affected("F", m) or cb_affected("M", f):
                continue
            for (sex, geno, origins), p in x_cross_with_origin(m, f).items():
                if sex == "M" and cb_affected(sex, geno) and p > 0:
                    routes.add(origins)
    assert routes  # an affected son is possible
    return [
        routes == {("father",)},
        routes == {("mother",)},
        routes == {("father", "mother")},
        () in routes,  # no parental colour-blind allele (no mutation in this model)
        len(routes) > 1,
    ]


def m_turn_white(item: dict) -> list[bool]:
    """q-white: Morgan's cross. White-eyed male (X^w Y) x red-eyed female (X^W X^W), F1 x F1.
    Eye colour gene on X, red (W -> 'A') dominant. Which sex are the white-eyed F2 flies?
    Options: all male; all female; half and half; more females than males; unrelated to sex."""
    f1 = x_cross(("A", "A"), ("a", Y))
    f1_female = [g for (s, g), p in f1.items() if s == "F"]
    f1_male = [g for (s, g), p in f1.items() if s == "M"]
    assert f1_female == [("A", "a")] and f1_male == [("A", Y)]
    assert not any(shows("x_rec", g) for (_, g) in f1)  # F1 all red-eyed
    f2 = x_cross(f1_female[0], f1_male[0])
    white_f = sum(p for (s, g), p in f2.items() if s == "F" and shows("x_rec", g))
    white_m = sum(p for (s, g), p in f2.items() if s == "M" and shows("x_rec", g))
    assert white_f + white_m == F(1, 4)  # red : white = 3 : 1 overall
    return [
        white_m > 0 and white_f == 0,
        white_f > 0 and white_m == 0,
        white_f == white_m and white_f > 0,
        white_f > white_m,
        white_f == white_m,  # "unrelated to sex" would mean equal shares in both sexes
    ]


def m_turn_ruleout(item: dict) -> list[bool]:
    """q-ruleout: father and mother without the trait; a daughter with it, a son without it.
    Which mode fits? Options: autosomal dominant; autosomal recessive; X dominant; X recessive;
    none of the four."""
    people = {"father": ("M", False), "mother": ("F", False), "daughter": ("F", True), "son": ("M", False)}
    fam = [("mother", "father", ["daughter", "son"])]
    s = surviving(people, fam)
    return s + [not any(s)]


# --- Check yourself ------------------------------------------------------------------------------

# Chromosome theory: how hereditary factors and chromosomes behave (factors: 領綱 BGa-Ⅴc-1, chapter
# s116-mendel; chromosomes in meiosis and fertilisation: 領綱 BDa-Ⅴc, chapter s116-cell-division).
FACTOR_BEHAVIOUR = {
    "paired_in_body_cells": True,
    "pair_separates_into_gametes": True,
    "one_per_gamete": True,
    "pair_restored_at_fertilisation": True,
}
HOMOLOGOUS_CHROMOSOME_BEHAVIOUR = {
    "paired_in_body_cells": True,
    "pair_separates_into_gametes": True,
    "one_per_gamete": True,
    "pair_restored_at_fertilisation": True,
}
HISTORY_FACTS = {
    # chapter s116-mendel / nat.json BGa-Ⅴc-1: the factor was an abstract term inferred from ratios;
    # Mendel never saw factors under a microscope.
    "mendel_saw_factors_in_microscope": False,
    # Standard biology (s116-cell-division: humans 46; other species differ): chromosome numbers
    # differ between species.
    "all_species_same_chromosome_number": False,
    # 國中 Ga-Ⅳ-2 (sex is mainly set by sex chromosomes): women XX, men XY, so the sets differ.
    "male_and_female_chromosomes_all_identical": False,
}


def m_chromosome_theory(item: dict) -> list[bool]:
    """q1: which observation led scientists to put hereditary factors on chromosomes?
    Options: (1) homologous chromosomes separate into different gametes in meiosis, just as paired
    factors separate; (2) Mendel saw the factors in a microscope; (3) every species has the same number
    of chromosomes; (4) mitosis halves the chromosome number; (5) the chromosomes of males and females
    are all identical."""
    parallel = all(FACTOR_BEHAVIOUR[k] == HOMOLOGOUS_CHROMOSOME_BEHAVIOUR[k] for k in FACTOR_BEHAVIOUR)
    # Option 4 by the division rule taught in chapter s116-cell-division: mitosis gives two cells with
    # the parent's chromosome number (2n -> 2n); only meiosis halves it (2n -> n).
    def after_division(kind: str, two_n: int) -> int:
        return two_n if kind == "mitosis" else two_n // 2

    mitosis_halves = any(after_division("mitosis", c) * 2 == c for c in (4, 8, 46))
    return [
        parallel,
        HISTORY_FACTS["mendel_saw_factors_in_microscope"],
        HISTORY_FACTS["all_species_same_chromosome_number"],
        mitosis_halves,
        HISTORY_FACTS["male_and_female_chromosomes_all_identical"],
    ]


def m_daughter_cb_share(item: dict) -> tuple[int, int]:
    """q2: carrier mother (X^A X^a) x colour-blind father (X^a Y): share of daughters colour-blind."""
    dist = x_cross(("A", "a"), ("a", Y))
    daughters = sum(p for (s, g), p in dist.items() if s == "F")
    cb = sum(p for (s, g), p in dist.items() if s == "F" and cb_affected(s, g))
    share = cb / daughters
    return share.numerator, share.denominator


def m_cb_mother_children(item: dict) -> list[bool]:
    """q3: colour-blind mother (X^a X^a) x colour-normal father (X^A Y).
    Options: sons all colour-blind and daughters all carriers; sons all normal and daughters all
    colour-blind; half of sons and of daughters colour-blind; all children normal; all colour-blind."""
    dist = x_cross(("a", "a"), ("A", Y))

    def share(sex, pred):
        tot = sum(p for (s, g), p in dist.items() if s == sex)
        return sum(p for (s, g), p in dist.items() if s == sex and pred(g)) / tot

    sons_cb = share("M", lambda g: cb_affected("M", g))
    dau_cb = share("F", lambda g: cb_affected("F", g))
    dau_carrier = share("F", lambda g: not cb_affected("F", g) and "a" in g)
    return [
        sons_cb == 1 and dau_carrier == 1,
        sons_cb == 0 and dau_cb == 1,
        sons_cb == F(1, 2) and dau_cb == F(1, 2),
        sons_cb == 0 and dau_cb == 0,
        sons_cb == 1 and dau_cb == 1,
    ]


def m_male_autosomes(item: dict) -> int:
    """q4: number of autosomes in a body cell of a man. Humans: 2n = 46, i.e. 23 pairs, one of which
    is the sex-chromosome pair (XY in males)."""
    n = 46 // 2
    sex_pairs = 1
    return 2 * (n - sex_pairs)


def m_sex_linked_statements(item: dict) -> list[bool]:
    """q5: (1) a man's X always comes from his mother; (2) a woman's two X chromosomes come one from
    each parent; (3) a colour-normal woman never carries the colour-blind allele; (4) a colour-blind
    woman's father is always colour-blind; (5) the Y chromosome carries an allele of the colour-blindness
    gene. Every statement is tested over every possible pair of parents."""
    son_x_from_mother = True
    daughter_one_each = True
    cb_daughter_fathers = set()
    for m in FEMALE_X:
        for f in MALE_X:
            for (sex, geno, origins), p in x_cross_with_origin(m, f).items():
                if p == 0:
                    continue
                if sex == "M":
                    # a son's only X is the egg's: its allele must be one of the mother's
                    son_x_from_mother &= geno[0] in m
                else:
                    # a daughter gets the father's single X plus one of the mother's
                    rest = list(geno)
                    if f[0] in rest:
                        rest.remove(f[0])
                        daughter_one_each &= rest[0] in m
                    else:
                        daughter_one_each = False
                    if cb_affected("F", geno):
                        cb_daughter_fathers.add(f)
    normal_women_carry = any(not cb_affected("F", g) and "a" in g for g in FEMALE_X)
    y_carries_allele = any(a in ("A", "a") for _, g in MALE_X for a in g[1:])
    return [
        son_x_from_mother,
        daughter_one_each,
        not normal_women_carry,
        all(cb_affected("M", f) for f in cb_daughter_fathers) and bool(cb_daughter_fathers),
        y_carries_allele,
    ]


def m_pedigree_ruleout(item: dict) -> list[bool]:
    """q6: mother shows the trait, father does not; their son does not, their daughter does.
    Which mode can be ruled out? Options: autosomal dominant; autosomal recessive; X dominant;
    X recessive; none of the four can be ruled out."""
    people = {"father": ("M", False), "mother": ("F", True), "son": ("M", False), "daughter": ("F", True)}
    fam = [("mother", "father", ["son", "daughter"])]
    s = surviving(people, fam)
    ruled_out = [not x for x in s]
    return ruled_out + [not any(ruled_out)]


def m_insect_f2_recessive(item: dict) -> int:
    """q7: an insect with XX females and XY males, wing-colour gene on X, B dominant.
    Recessive female (X^b X^b) x dominant male (X^B Y) -> F1; F1 x F1 -> F2.
    Percentage of F2 showing the recessive trait."""
    f1 = x_cross(("a", "a"), ("A", Y))
    (fem,) = {g for (s, g) in f1 if s == "F"}
    (mal,) = {g for (s, g) in f1 if s == "M"}
    f2 = x_cross(fem, mal)
    rec = sum(p for (s, g), p in f2.items() if shows("x_rec", g))
    pct = rec * 100
    assert pct.denominator == 1
    return int(pct)


def m_next_child_son(item: dict) -> list[bool]:
    """q8: a couple already has three daughters. Probability that the fourth child is a son.
    Each child comes from a new egg and a new sperm; eggs all carry X, half the sperm carry Y, and
    earlier children do not change the sperm. Options: 1/2; more than 1/2; 1/4; 1/16; 1."""
    egg = {"X": F(1)}
    sperm = {"X": F(1, 2), "Y": F(1, 2)}
    p_son = sum(pe * ps for e, pe in egg.items() for s, ps in sperm.items() if s == "Y")
    # independence: conditioning on three earlier daughters leaves the fourth child's sperm unchanged
    p_three_daughters_then_son = (1 - p_son) ** 3 * p_son
    p_three_daughters = (1 - p_son) ** 3
    p_cond = p_three_daughters_then_son / p_three_daughters
    return [p_cond == F(1, 2), p_cond > F(1, 2), p_cond == F(1, 4), p_cond == F(1, 16), p_cond == 1]
