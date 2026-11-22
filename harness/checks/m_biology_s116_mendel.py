"""Checks for src/data/items/biology/s116-mendel.yaml (116 sprint: BMb-Ⅴc-2, BGa-Ⅴc-1, BGa-Ⅴc-2:
Mendel's experiments and reasoning, segregation and independent assortment, codominance and multiple
alleles with ABO blood types, pedigrees, polygenic inheritance without calculation).

How the keys are recomputed (never from item["answer"]):
- Crosses enumerate gametes and offspring with exact Fractions. A genotype is a tuple of genes, each gene
  a pair of alleles; segregation gives each allele of a pair to half the gametes, and independent
  assortment multiplies the gamete probabilities of different genes.
- Phenotypes come from a dominance rule per gene: one dominant/recessive gene (capital letter dominant),
  or the ABO rule (IA and IB codominant, i recessive to both).
- Pedigrees test every genotype assignment consistent with the stated phenotypes and children.
- Qualitative statements (history of method, polygenic inheritance) come from explicit facts tables,
  each fact with its source.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import product

# --- genetics engine ------------------------------------------------------------------------------


def gametes(genotype: tuple[tuple[str, str], ...]) -> dict[tuple[str, ...], F]:
    """Segregation (each allele of a pair to half the gametes) and independent assortment (genes
    combine independently, probabilities multiply)."""
    out: dict[tuple[str, ...], F] = {}
    for choice in product(*[[(a, F(1, 2)) for a in pair] for pair in genotype]):
        g = tuple(a for a, _ in choice)
        p = F(1)
        for _, q in choice:
            p *= q
        out[g] = out.get(g, F(0)) + p
    return out


def cross(mother, father) -> dict[tuple[tuple[str, str], ...], F]:
    """Offspring genotype distribution; each gene's pair is stored sorted so Aa == aA."""
    out: dict = {}
    for gm, pm in gametes(mother).items():
        for gf, pf in gametes(father).items():
            child = tuple(tuple(sorted((a, b))) for a, b in zip(gm, gf))
            out[child] = out.get(child, F(0)) + pm * pf
    assert sum(out.values()) == 1
    return out


def g(*pairs: str):
    """g('Aa', 'Bb') -> (('A','a'), ('B','b')). Single-letter alleles only."""
    return tuple(tuple(p) for p in pairs)


def simple_phenotype(pair: tuple[str, str]) -> str:
    """Complete dominance: a capital allele masks the small one. Returns 'D' (dominant) or 'r'."""
    return "D" if any(a.isupper() for a in pair) else "r"


def phenotypes(dist, rule=simple_phenotype) -> dict[tuple[str, ...], F]:
    out: dict = {}
    for geno, p in dist.items():
        ph = tuple(rule(pair) for pair in geno)
        out[ph] = out.get(ph, F(0)) + p
    return out


# ABO: alleles 'A' = IA, 'B' = IB, 'i' = i. IA and IB codominant, i recessive to both
# (領綱 BGa-Ⅴc-2 說明 2-1: codominance and multiple alleles with ABO blood type).
ABO_ALLELES = ["A", "B", "i"]


def abo_type(pair: tuple[str, str]) -> str:
    shown = {a for a in pair if a != "i"}  # every non-recessive allele present is expressed
    if not shown:
        return "O"
    return "".join(sorted(shown))  # 'A', 'B' or 'AB'


ABO_GENOTYPES = sorted({tuple(sorted(p)) for p in product(ABO_ALLELES, repeat=2)})


def abo_children(m: tuple[str, str], f: tuple[str, str]) -> dict[str, F]:
    out: dict[str, F] = {}
    for geno, p in cross((m,), (f,)).items():
        t = abo_type(geno[0])
        out[t] = out.get(t, F(0)) + p
    return out


def _ratio(values: list[F]) -> tuple[int, ...]:
    """Fractions -> smallest whole-number ratio, largest first."""
    from math import gcd, lcm

    den = 1
    for v in values:
        den = lcm(den, v.denominator)
    ints = [int(v * den) for v in values]
    d = 0
    for x in ints:
        d = gcd(d, x)
    return tuple(sorted((x // d for x in ints), reverse=True))


# --- opening and mid-chapter turns ---------------------------------------------------------------


def m_turn_f2(item: dict) -> list[bool]:
    """q-turn: true-breeding purple (AA) x true-breeding white (aa) -> F1 all purple; F1 selfed -> F2.
    Options: all purple; all white; both, about 3:1; both, about 1:1; all an intermediate pale purple."""
    f1 = cross(g("AA"), g("aa"))
    assert set(f1) == {g("Aa")}
    f1_plant = g("Aa")
    f2 = phenotypes(cross(f1_plant, f1_plant))
    purple = f2.get(("D",), F(0))
    white = f2.get(("r",), F(0))
    # complete dominance: every genotype maps to purple or white, never an intermediate colour
    intermediate_exists = any(ph not in {("D",), ("r",)} for ph in f2)
    return [
        purple == 1,
        white == 1,
        purple > 0 and white > 0 and purple / white == 3,
        purple > 0 and white > 0 and purple / white == 1,
        intermediate_exists and purple == 0 and white == 0,
    ]


def m_turn_hidden(item: dict) -> list[bool]:
    """q-hidden: data F1 white fraction 0, F2 white fraction about 1/4 (from the chapter's figure).
    Each option is a model; it is supported when it predicts both observations.
    Options: white factor present but masked in F1; lost in F1 and made anew; blended into a new factor;
    F1 factors identical to the purple parent; environment, not factors."""
    observed = (F(0), F(1, 4))

    def white_fracs(f1_geno) -> tuple[F, F]:
        f1w = phenotypes({f1_geno: F(1)}).get(("r",), F(0))
        f2w = phenotypes(cross(f1_geno, f1_geno)).get(("r",), F(0))
        return f1w, f2w

    models = [
        white_fracs(g("Aa")),  # (1) F1 carries a, masked by A
        white_fracs(g("AA")),  # (2) a lost: F1 carries only purple factors; nothing makes white again
        None,  # (3) blending: F1 would be one new intermediate factor -> F1 not purple, no white in F2
        white_fracs(g("AA")),  # (4) F1 identical to the true-breeding purple parent (AA)
        None,  # (5) environment: predicts no regular inherited fraction at all
    ]
    return [m == observed if m is not None else False for m in models]


def m_turn_pedigree(item: dict) -> list[bool]:
    """q-pedigree: grandfather type A, grandmother type B, their son type O. Which genotype is the
    grandfather? Test every pair of ABO genotypes for the grandparents.
    Options: IAIA; IAi; IAIB; ii; can't tell."""
    possible = set()
    for gf, gm in product(ABO_GENOTYPES, repeat=2):
        if abo_type(gf) != "A" or abo_type(gm) != "B":
            continue
        if abo_children(gm, gf).get("O", F(0)) > 0:
            possible.add(gf)
    opts = [("A", "A"), ("A", "i"), ("A", "B"), ("i", "i")]
    return [possible == {o} for o in opts] + [len(possible) > 1]


# --- Check yourself ------------------------------------------------------------------------------


def m_expected_vestigial(item: dict) -> int:
    """q1: long wing L dominant; two heterozygous long-winged insects (Ll x Ll), 240 offspring:
    expected number of vestigial-winged (ll)."""
    p = phenotypes(cross(g("Ll"), g("Ll"))).get(("r",), F(0))
    n = p * 240
    assert n.denominator == 1
    return int(n)


def m_tall_heterozygous_share(item: dict) -> tuple[int, int]:
    """q2: Tt selfed; among the tall offspring, the share that are heterozygous (Tt)."""
    dist = cross(g("Tt"), g("Tt"))
    tall = sum(p for geno, p in dist.items() if simple_phenotype(geno[0]) == "D")
    het = sum(p for geno, p in dist.items() if len(set(geno[0])) == 2)
    share = het / tall
    return share.numerator, share.denominator


def m_testcross_two_genes(item: dict) -> list[bool]:
    """q3: AaBb x aabb (independent genes); offspring phenotype ratio.
    Options: 9:3:3:1; 3:1; 1:1:1:1; 1:2:1; 3:3:1:1."""
    ph = phenotypes(cross(g("Aa", "Bb"), g("aa", "bb")))
    got = _ratio(list(ph.values()))
    opts = [(9, 3, 3, 1), (3, 1), (1, 1, 1, 1), (1, 2, 1), (3, 3, 1, 1)]
    return [got == tuple(sorted(o, reverse=True)) for o in opts]


def m_double_heterozygote_share(item: dict) -> tuple[int, int]:
    """q4: DdEe x DdEe (independent); probability an offspring is DdEe."""
    dist = cross(g("Dd", "Ee"), g("Dd", "Ee"))
    p = dist[g("Dd", "Ee")]
    return p.numerator, p.denominator


def m_abo_ab_father(item: dict) -> list[bool]:
    """q5: father type AB, mother type A with unknown genotype. Which blood types are possible for the
    children (over every genotype the mother could have)? Options: A; B; AB; O;
    'if the mother is IAIA, the children can only be A or AB'."""
    father = ("A", "B")
    mothers = [m for m in ABO_GENOTYPES if abo_type(m) == "A"]
    possible = set()
    for m in mothers:
        possible |= {t for t, p in abo_children(m, father).items() if p > 0}
    only_if_homo = {t for t, p in abo_children(("A", "A"), father).items() if p > 0}
    return ["A" in possible, "B" in possible, "AB" in possible, "O" in possible, only_if_homo == {"A", "AB"}]


def m_unaffected_parents(item: dict) -> list[bool]:
    """q6: a trait not linked to sex, one gene. Both parents lack the trait; their first child has it.
    Probability that the second child has it. Test both dominance hypotheses and every parental
    genotype pair consistent with the chart. Options: 0; 1/4; 1/2; 3/4; 1."""
    answers = set()
    for affected_is_dominant in (True, False):
        def shows(geno) -> bool:
            ph = simple_phenotype(geno[0])
            return (ph == "D") if affected_is_dominant else (ph == "r")

        for m, f in product([g("AA"), g("Aa"), g("aa")], repeat=2):
            if shows(m) or shows(f):
                continue  # both parents lack the trait
            dist = cross(m, f)
            p_aff = sum(p for geno, p in dist.items() if shows(geno))
            if p_aff > 0:  # the first child having the trait must be possible
                answers.add(p_aff)
    assert len(answers) == 1  # only recessive with Aa x Aa survives
    (p,) = answers
    return [p == o for o in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))]


# Facts for qualitative statements, each with its source.
POLYGENIC_FACTS = {
    # 領綱 BGa-Ⅴc-2 說明 2-2 (nat.json keyConcepts): polygenic inheritance, human skin colour, no calculation;
    # several genes each with a small effect give continuous variation (standard 必修 content within 2-2).
    "skin_colour_many_genes_continuous": True,
    # nat.json BGa-Ⅴc-2: 114 Q4 applied segregation to ABO and to polygenic traits, so each gene of a
    # polygenic trait still segregates.
    "polygenic_breaks_segregation": False,
}


def m_extensions_statements(item: dict) -> list[bool]:
    """q7: Options: (1) AB shows both A and B: codominance; (2) three ABO alleles, so each person
    carries three; (3) ABO has 6 genotypes and 4 phenotypes; (4) skin colour is decided by several
    genes and varies continuously; (5) polygenic traits do not follow segregation."""
    ab = abo_type(("A", "B"))
    both_shown = ab == "AB" and all(abo_type((x, "i")) == x for x in ("A", "B"))  # both alleles expressed
    alleles_per_person = len(ABO_GENOTYPES[0])  # diploid: one allele from each parent
    n_geno = len(ABO_GENOTYPES)
    n_pheno = len({abo_type(x) for x in ABO_GENOTYPES})
    return [
        both_shown,
        alleles_per_person == len(ABO_ALLELES),
        (n_geno, n_pheno) == (6, 4),
        POLYGENIC_FACTS["skin_colour_many_genes_continuous"],
        POLYGENIC_FACTS["polygenic_breaks_segregation"],
    ]


# Mendel's method: each claim with whether it is true and its source.
MENDEL_METHOD = {
    # Standard history (chapter text): true-breeding lines first, then large counts written as ratios;
    # nat.json BMb-Ⅴc-2 keyConcepts: "How Mendel designed his experiments and reasoned to the laws",
    # "Heredity has regularities that a mathematical model explains".
    "pure_lines_then_count_ratios": True,
    # biology.json s116-chromosomes-sex-linked (BMb-Ⅴc-3): linking factors to chromosomes came from
    # later scientists; Mendel did not locate factors on chromosomes.
    "watched_chromosomes_in_meiosis": False,
    # nat.json BMb-Ⅴc-2: regularities explained by a mathematical model, which needs many counts;
    # a few plants described by impression is the opposite.
    "few_plants_by_impression": False,
    # Standard history (chapter text): one pair of traits first, then two pairs.
    "seven_traits_at_once_never_one": False,
    # nat.json BGa-Ⅴc-1 keyConcepts: the 遺傳因子 is an abstract term inferred from traits.
    "saw_factors_directly": False,
}


def m_mendel_method(item: dict) -> list[bool]:
    """q8: which describes Mendel's method best? Options in the order of MENDEL_METHOD."""
    order = ["pure_lines_then_count_ratios", "watched_chromosomes_in_meiosis", "few_plants_by_impression",
             "seven_traits_at_once_never_one", "saw_factors_directly"]
    return [MENDEL_METHOD[k] for k in order]
