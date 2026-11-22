"""Checks for src/data/items/biology/s116-molecular-genetics.yaml (116 sprint: BGa-Ⅴc-5, BGa-Ⅴc-6,
BGa-Ⅴc-7, BMc-Ⅴc-1: nucleic acids as the genetic material and crude DNA extraction, the central dogma and
where its steps happen, genetic variation and environment in trait expression, transgenic technology).

How the keys are recomputed (never from item["answer"]):
- Extraction items look each step up in a step -> purpose table.
- Nucleic-acid items look components up in a DNA/RNA composition table.
- Counts of DNA molecules follow chromosomes through replication and division by rule: one DNA molecule per
  chromosome before replication, replication doubles DNA molecules but not chromosomes, mitosis gives each
  daughter the parent's count, meiosis halves the chromosomes and ends with one DNA molecule per chromosome.
- Locations come from a cell model: replication and transcription happen where the DNA is (the nucleus if
  the cell has one, else the cytoplasm); translation happens at ribosomes in the cytoplasm.
- Data-reading items test each statement against the data table (monotonic trends, rank agreement, what was
  held constant, whether any intervention on the gene was made).
- Trait-difference items apply the one-difference rule to stated genotype and environment conditions.
- Transgenic items apply the definition to the procedure each option describes.
Each fact table has a source comment; facts are only from the chapter's sources at 必修 depth.
"""

from __future__ import annotations

# --- nucleic acids and crude DNA extraction (BGa-Vc-5) -------------------------------------------

# Step -> purpose. The step list (detergent, salt water, pineapple juice, alcohol, kiwi) is from nat.json
# BGa-Vc-5 (115 Q33) and the 領綱 說明 5-1 activity (DNA crude extraction, avoid chicken blood); the
# purpose of each step is the standard 必修 探討活動 account taught in the chapter's step table.
PURPOSE = {
    "mash": "break_tissue",            # break up tissue and cell walls
    "detergent": "dissolve_membranes",  # cell membrane and nuclear envelope contain lipids
    "salt": "dissolve_dna",            # DNA dissolves in the salt solution
    "filter": "remove_debris",
    "pineapple": "digest_protein",     # its enzyme breaks down protein wrapped around DNA
    "cold_alcohol": "precipitate_dna",  # DNA does not dissolve in alcohol
}

# What is seen at the alcohol layer: many DNA molecules clumped with other substances (a crude extract).
EXTRACT = {"single_molecule": False, "many_molecules_clumped": True, "pure_dna": False}

# 領綱 BGa-Vc-5 說明 5-1: the activity should avoid chicken blood.
AVOID_CHICKEN_BLOOD = True


def mg_turn_pineapple(item: dict) -> list[bool]:
    """q-turn: why pineapple juice? Options: break down protein wrapped around DNA; dissolve membranes;
    make DNA precipitate; break down DNA so it is easier to see; sweeten the solution."""
    claims = ["digest_protein", "dissolve_membranes", "precipitate_dna", "digest_dna", "flavour"]
    return [PURPOSE["pineapple"] == c for c in claims]


def mg_strawberry_steps(item: dict) -> list[bool]:
    """q1 (strawberry): (1) mash (2) detergent salt water (3) filter (4) pineapple juice (5) cold alcohol.
    Options: (2) detergent dissolves membranes; (4) pineapple juice breaks down protein; (5) alcohol is added
    to dissolve DNA; the white strands are one DNA molecule; (3) filtering removes debris."""
    return [
        PURPOSE["detergent"] == "dissolve_membranes",
        PURPOSE["pineapple"] == "digest_protein",
        PURPOSE["cold_alcohol"] == "dissolve_dna",
        EXTRACT["single_molecule"],
        PURPOSE["filter"] == "remove_debris",
    ]


# DNA / RNA composition (chemistry.nucleic-acid glossary and chemistry/s116-organic-life: phosphate, a
# five-carbon sugar and a nitrogen-containing base; deoxyribose in DNA, ribose in RNA; bases A T C G in DNA,
# A U C G in RNA, the chapter's table at 必修 depth).
NUCLEIC = {
    "DNA": {"phosphate", "deoxyribose", "base_A", "base_T", "base_C", "base_G", "nitrogenous_base"},
    "RNA": {"phosphate", "ribose", "base_A", "base_U", "base_C", "base_G", "nitrogenous_base"},
}


def mg_rna_only(item: dict) -> list[bool]:
    """q2: which component does RNA have but DNA not? Options: ribose; deoxyribose; base T; phosphate;
    nitrogenous base."""
    comps = ["ribose", "deoxyribose", "base_T", "phosphate", "nitrogenous_base"]
    return [c in NUCLEIC["RNA"] and c not in NUCLEIC["DNA"] for c in comps]


# --- DNA molecules through replication and division (BGa-Vc-6, with BDa-Vc-5/7 rules) ------------

class Nucleus:
    """Chromosome count and DNA molecules in one nucleus (nuclear DNA only)."""

    def __init__(self, chromosomes: int):
        self.chromosomes = chromosomes
        self.dna = chromosomes  # before replication: one DNA molecule per chromosome

    def replicate(self) -> None:
        # each DNA molecule becomes two identical ones, still joined: chromosome count unchanged
        assert self.dna == self.chromosomes
        self.dna *= 2

    def mitosis(self) -> list["Nucleus"]:
        # the two joined copies separate, one to each daughter
        assert self.dna == 2 * self.chromosomes
        return [Nucleus(self.chromosomes), Nucleus(self.chromosomes)]

    def meiosis(self) -> list["Nucleus"]:
        # one replication, then two divisions: four cells with one set (n), one DNA molecule per chromosome
        assert self.dna == 2 * self.chromosomes and self.chromosomes % 2 == 0
        return [Nucleus(self.chromosomes // 2) for _ in range(4)]


def _check_chapter_predict() -> None:
    # the chapter's Predict: 46 chromosomes -> 92 DNA molecules after replication, still 46 chromosomes
    c = Nucleus(46)
    c.replicate()
    assert (c.chromosomes, c.dna) == (46, 92)
    assert all((d.chromosomes, d.dna) == (46, 46) for d in c.mitosis())


def mg_gamete_dna(item: dict) -> int:
    """q3: a plant with 2n = 16; DNA molecules in the nucleus of each gamete made by meiosis."""
    _check_chapter_predict()
    cell = Nucleus(16)
    cell.replicate()
    gametes = cell.meiosis()
    counts = {g.dna for g in gametes}
    assert len(counts) == 1
    return counts.pop()


# --- where the central dogma happens (BGa-Vc-6; 115 Q37) ----------------------------------------

# Cell structures by cell type (as harness/checks/m_biology_s116_cell_theory_structure.py STRUCTURES:
# nat.json BDa-Vc-2; prokaryotes have ribosomes but no nucleus). Ribosomes make protein and sit in the
# cytoplasm, free or attached to the ER (cell theory chapter table).
CELL = {
    "eukaryote": {"nucleus": True, "ribosome": True},
    "prokaryote": {"nucleus": False, "ribosome": True},
}
PROTEIN_SYNTHESIS_SITE = "cytoplasm_ribosome"

# Central dogma (領綱 BGa-Vc-6 說明 6-1~6-3, overview only): template -> product, and the polymerase named.
PROCESS = {
    "replication": {"from": "DNA", "to": "DNA", "polymerase": "DNA_polymerase"},
    "transcription": {"from": "DNA", "to": "RNA", "polymerase": "RNA_polymerase"},
    "translation": {"from": "RNA", "to": "protein", "polymerase": None},
}


def location(process: str, cell_type: str) -> str:
    cell = CELL[cell_type]
    if process in ("replication", "transcription"):  # follows the DNA (nuclear DNA)
        return "nucleus" if cell["nucleus"] else "cytoplasm"
    assert process == "translation" and cell["ribosome"]
    return PROTEIN_SYNTHESIS_SITE


def mg_turn_translation_site(item: dict) -> list[bool]:
    """q-where: in a eukaryotic cell, where does translation happen? Options: ribosomes in the cytoplasm;
    nucleus; mitochondrion; Golgi apparatus; cell membrane."""
    sites = ["cytoplasm_ribosome", "nucleus", "mitochondrion", "golgi", "cell_membrane"]
    return [location("translation", "eukaryote") == s for s in sites]


def mg_bacterium_sites(item: dict) -> list[bool]:
    """q4: in a bacterium, (transcription, translation) happen where? Options: (nucleus, cytoplasm);
    (cytoplasm, ribosomes in the cytoplasm); (nucleus, nucleus); (mitochondrion, ribosome);
    (cytoplasm, nucleus)."""
    actual = (location("transcription", "prokaryote"), location("translation", "prokaryote"))
    options = [
        ("nucleus", "cytoplasm"),
        ("cytoplasm", "cytoplasm_ribosome"),
        ("nucleus", "nucleus"),
        ("mitochondrion", "cytoplasm_ribosome"),
        ("cytoplasm", "nucleus"),
    ]
    return [o == actual for o in options]


def _named(frm: str, to: str) -> str | None:
    for name, p in PROCESS.items():
        if (p["from"], p["to"]) == (frm, to):
            return name
    return None


def mg_central_dogma(item: dict) -> list[bool]:
    """q5: options: making RNA from DNA is called translation; the product of translation is protein;
    eukaryotic DNA replication happens mainly in the nucleus; transcription needs RNA polymerase;
    by the central dogma, information flows from protein to RNA."""
    return [
        _named("DNA", "RNA") == "translation",
        PROCESS["translation"]["to"] == "protein",
        location("replication", "eukaryote") == "nucleus",
        PROCESS["transcription"]["polymerase"] == "RNA_polymerase",
        _named("protein", "RNA") is not None,
    ]


# --- trait expression: genetic variation and environment (BGa-Vc-7) ----------------------------

# q6's stated data (hypothetical plants, all cuttings of one plant, so one genotype; temperature is the
# only condition changed; nothing was done to gene K itself).
Q6_DATA = [  # (temperature °C, relative RNA of gene K, flowering %)
    (12, 9, 85),
    (16, 6, 60),
    (20, 3, 30),
    (24, 1, 10),
]
Q6_SAME_GENOTYPE = True
Q6_INTERVENTION_ON_K = False


def _strictly_decreasing(xs: list[int]) -> bool:
    return all(a > b for a, b in zip(xs, xs[1:]))


def _same_order(xs: list[int], ys: list[int]) -> bool:
    """Every pair of groups ranks the same way on xs and ys (perfect rank agreement)."""
    n = len(xs)
    return all((xs[i] - xs[j]) * (ys[i] - ys[j]) > 0 for i in range(n) for j in range(i + 1, n))


def mg_cuttings_data(item: dict) -> list[bool]:
    """q6: options: higher temperature, less K RNA; groups with more K RNA flower more; the flowering
    differences come from different genotypes; the data show an environmental factor changing a gene's
    expression; the data prove that K protein directly causes flowering."""
    temps = [t for t, _, _ in Q6_DATA]
    k = [r for _, r, _ in Q6_DATA]
    flower = [f for _, _, f in Q6_DATA]
    assert temps == sorted(temps)
    env_changes_expression = Q6_SAME_GENOTYPE and len(set(k)) > 1  # only temperature differed
    return [
        _strictly_decreasing(k),
        _same_order(k, flower),
        not Q6_SAME_GENOTYPE,
        env_changes_expression,
        Q6_INTERVENTION_ON_K,  # a direct causal claim about K needs an experiment that changes K itself
    ]


# One-difference rule (領綱 BGa-Vc-7 說明 7-1, 7-2: different expressions come from genetic variation;
# environment affects expression). Plants from cuttings or from the tubers of one potato are offspring
# of asexual reproduction and keep the genotype (國中 asexual reproduction; mitosis 2n -> 2n:
# biology/s116-cell-division).
# genotype: 'same' / 'different' / 'unknown'; env: 'same' / 'different'.
Q7_CASES = [
    ("same", "different"),       # cuttings of one hydrangea in two soils, flower colour differs
    ("different", "same"),       # two peas from different seeds, same field and care, purple vs white
    ("unknown", "different"),    # two dogs of different parents in different homes, size differs
    ("same", "different"),       # two plants from tubers of one potato, full light vs shade, height differs
    ("unknown", "same"),         # two mice of one litter, genotypes unknown, same food, coat differs
]


def cause(genotype: str, env: str) -> str:
    if genotype == "same" and env == "different":
        return "environment"
    if genotype == "different" and env == "same":
        return "genetic"
    if genotype == "same" and env == "same":
        return "none_expected"
    return "undecided"


def mg_environment_only(item: dict) -> list[bool]:
    """q7: in which cases must the difference be caused by the environment?"""
    return [cause(gt, env) == "environment" for gt, env in Q7_CASES]


# --- transgenic technology (BMc-Vc-1) ---------------------------------------------------------

# 領綱 BMc-Vc-1 (1-1 recombinant DNA and transgenic applications, no mechanism): a gene of one kind of
# organism is put into the cells of another kind, which then shows the trait. Each option's procedure as
# stated in its text: (method, donor organism, receiving organism).
# All five are hypothetical (the stem says so); none reuses the chapter's examples.
Q8_OPTIONS = [
    ("insert_gene", "another plant species", "rice"),  # a drought-tolerance gene into rice cells
    ("cross", "pea", "pea"),                           # tall x short peas, select offspring
    ("insert_gene", "soil bacterium", "yeast"),        # a soil-bacterium gene into yeast
    ("cutting", "fruit tree", "fruit tree"),           # propagate branches by cutting
    ("feed_pigment", None, "fish"),                    # pigment in the food; no gene is moved
]


def is_transgenic(method: str, donor, receiver: str) -> bool:
    return method == "insert_gene" and donor is not None and donor != receiver


def mg_transgenic_cases(item: dict) -> list[bool]:
    """q8: which procedures are transgenic technology?"""
    return [is_transgenic(*o) for o in Q8_OPTIONS]
