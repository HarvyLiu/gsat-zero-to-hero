"""Checks for src/data/items/biology/s116-classification-biodiversity.yaml (116 sprint: BGb-Ⅴc-3,
BGb-Ⅴc-4, BGb-Ⅴc-5: Linnaeus and binomial naming, common ancestry and classification, homologous and
analogous structures, reading phylogenetic trees, five kingdoms to three domains, where viruses fit,
and biodiversity as species forming and going extinct).

How the keys are recomputed (never from item["answer"]):
- Trees are nested tuples. A tree written in a stem is parsed from the stem itself. "X is more closely
  related to Y than to Z" is decided by the depth of the most recent common ancestor (MRCA): the deeper
  (nearer the tips) the MRCA, the closer the relationship. Branch points are counted as tuples.
- Homologous vs analogous is decided by one stated criterion (the chapter's): same ancestral origin ->
  homologous, whatever the function; different origin -> not homologous.
- Ranks, naming rules, cell types, the five-kingdom -> three-domain map, the virus facts and the
  history are code tables; each row says where the fact comes from.
- Species counts are exact integer bookkeeping: start + sum(formed - extinct).
Sources: nat.json BGb-Vc-3/4/5 keyConcepts (Linnaeus had no idea of kinship; common ancestry changed
classification; birds and reptiles; five kingdoms -> three domains; where viruses fit; homologous vs
analogous, 考試說明 sample 2; species arise and go extinct), 國中 Gc-Ⅳ-1 說明 (scientific naming and the
seven ranks, per the research slice), and standard 必修 biology at the depth the 說明 allows.
"""

from __future__ import annotations

# --- trees ---------------------------------------------------------------------------------------

Tree = object  # a leaf name (str) or a tuple of subtrees


def _parse_tree(text: str) -> Tree:
    """Parse the first balanced '(...)' in text, e.g. '((甲,乙),(丙,(丁,戊)))', into nested tuples."""
    start = text.index("(")
    pos = start

    def node():
        nonlocal pos
        if text[pos] == "(":
            pos += 1
            kids = [node()]
            while text[pos] in ",，":
                pos += 1
                kids.append(node())
            assert text[pos] == ")", f"unbalanced tree at {pos}"
            pos += 1
            return tuple(kids)
        end = pos
        while text[end] not in ",，()":
            end += 1
        name = text[pos:end].strip()
        pos = end
        return name

    return node()


def _paths(tree: Tree, prefix: tuple = ()) -> dict[str, tuple]:
    """Leaf -> path of child indices from the root."""
    if isinstance(tree, str):
        return {tree: prefix}
    out: dict[str, tuple] = {}
    for i, kid in enumerate(tree):
        out.update(_paths(kid, prefix + (i,)))
    return out


def _mrca_depth(tree: Tree, a: str, b: str) -> int:
    """Depth of the most recent common ancestor of leaves a and b (root = 0)."""
    pa, pb = _paths(tree)[a], _paths(tree)[b]
    d = 0
    while d < min(len(pa), len(pb)) and pa[d] == pb[d]:
        d += 1
    return d


def _closer(tree: Tree, x: str, y: str, z: str) -> bool:
    """True when x is more closely related to y than to z."""
    return _mrca_depth(tree, x, y) > _mrca_depth(tree, x, z)


def _branch_points(tree: Tree) -> int:
    return 0 if isinstance(tree, str) else 1 + sum(_branch_points(k) for k in tree)


def _rotate(tree: Tree) -> Tree:
    """Swap the children at every branch point (a picture change only)."""
    return tree if isinstance(tree, str) else tuple(_rotate(k) for k in reversed(tree))


# Birds and reptiles (nat.json BGb-Vc-4 key concept 4-1): fossils and DNA place birds with crocodiles,
# then lizards; mammals and fish further out. The chapter's tree.
AMNIOTE_TREE = ("魚", ("人", ("蜥蜴", ("鱷魚", "鳥"))))


def cbd_turn_croc(item: dict) -> list[bool]:
    """q-croc: is the crocodile closer to the lizard or the bird? Options: lizard; bird; equally close;
    can't compare because birds are not in class Reptilia."""
    t = AMNIOTE_TREE
    to_bird, to_lizard = _mrca_depth(t, "鱷魚", "鳥"), _mrca_depth(t, "鱷魚", "蜥蜴")
    # a tree compares any two pairs, whatever the traditional ranks say
    comparable = all(name in _paths(t) for name in ("鱷魚", "鳥", "蜥蜴"))
    return [to_lizard > to_bird, to_bird > to_lizard, to_bird == to_lizard, not comparable]


def cbd_tree_compare(item: dict) -> list[bool]:
    """q3: tree parsed from the stem; each option claims 'x is more closely related to y than to z'."""
    t = _parse_tree(item["text"]["zh-tw"]["stem"])
    claims = [("乙", "丙", "甲"), ("丁", "丙", "戊"), ("戊", "甲", "丙"), ("丙", "丁", "甲"), ("甲", "丁", "乙")]
    res = [_closer(t, x, y, z) for x, y, z in claims]
    # rotating branch points must not change any answer (the chapter's rule)
    assert res == [_closer(_rotate(t), x, y, z) for x, y, z in claims]
    return res


# --- homologous and analogous structures -----------------------------------------------------------

# structure -> (ancestral origin, function). Origins: vertebrate forelimbs share one origin (the
# chapter's figure; 考試說明 sample 2 context); cactus spines and pea tendrils are both modified leaves
# (stated in the stem); insect wings are outgrowths of the body wall; octopus and human eyes, and the
# streamlined bodies of sharks and dolphins, evolved separately (standard 必修 examples of analogy).
STRUCTURES = {
    "cat_forelimb": ("vertebrate_forelimb", "walk"),
    "bat_wing": ("vertebrate_forelimb", "fly"),
    "sparrow_wing": ("vertebrate_forelimb", "fly"),
    "bee_wing": ("insect_body_wall", "fly"),
    "octopus_eye": ("mollusc_eye", "see"),
    "human_eye": ("vertebrate_eye", "see"),
    "cactus_spine": ("leaf", "defend"),
    "pea_tendril": ("leaf", "climb"),
    "shark_body": ("fish_body", "swim"),
    "dolphin_body": ("mammal_body", "swim"),
    # chapter examples, used by the turn
    "human_arm": ("vertebrate_forelimb", "grasp"),
    "whale_flipper": ("vertebrate_forelimb", "swim"),
}


def _homologous(a: str, b: str) -> bool:
    return STRUCTURES[a][0] == STRUCTURES[b][0]


def cbd_homologous_pairs(item: dict) -> list[bool]:
    """q5 (multi): which pairs are homologous structures?"""
    pairs = [("cat_forelimb", "bat_wing"), ("octopus_eye", "human_eye"), ("cactus_spine", "pea_tendril"),
             ("shark_body", "dolphin_body"), ("bee_wing", "sparrow_wing")]
    return [_homologous(a, b) for a, b in pairs]


# The forelimb skeleton of each animal in the opening turn (chapter figure; standard 必修 account of
# vertebrate forelimbs): one upper-arm bone, two forearm bones, then wrist and finger bones, in that order.
FORELIMB = {
    org: {"upper": 1, "fore": 2, "digits": True, "order": ("upper", "fore", "wrist_digits")}
    for org in ("human", "bat", "whale")
}


def cbd_turn_forelimb(item: dict) -> list[bool]:
    """q-turn: what do the bones of a human arm, a bat wing and a whale flipper look like? Options:
    completely different; same set (1 upper, 2 forearm, wrist and digits); only humans have digits;
    no bones in the flipper; same numbers but a completely different order."""
    limbs = list(FORELIMB.values())
    same_set = all(l["upper"] == 1 and l["fore"] == 2 and l["digits"] for l in limbs)
    same_order = len({l["order"] for l in limbs}) == 1
    return [
        not same_set,
        same_set and same_order,
        FORELIMB["human"]["digits"] and not (FORELIMB["bat"]["digits"] or FORELIMB["whale"]["digits"]),
        FORELIMB["whale"]["upper"] + FORELIMB["whale"]["fore"] == 0,
        same_set and not same_order,
    ]


# --- Linnaeus, naming and ranks ---------------------------------------------------------------------

RANKS = ["界", "門", "綱", "目", "科", "屬", "種"]  # 國中 Gc-Ⅳ-1 說明: the seven ranks, top to bottom

# Binomial nomenclature (國中 Gc-Ⅳ-1 說明 naming rules; 115 Q35 context): two Latin words, genus then
# specific epithet; genus capitalised, epithet lower case.
BINOMIAL = {"parts": ("屬", "種小名"), "language": "Latin", "genus_capital": True, "epithet_capital": False}


def _same_rank_implies(rank: str) -> set[str]:
    """Sharing a rank means sharing every rank above it (the ranks are nested)."""
    return set(RANKS[: RANKS.index(rank) + 1])


def cbd_binomial_rules(item: dict) -> list[bool]:
    """q1: options: family + epithet; each country's own language; genus + epithet, genus first and
    capitalised; epithet capitalised; same genus means same family but different genus."""
    same_genus_shares = _same_rank_implies("屬")
    return [
        BINOMIAL["parts"] == ("科", "種小名"),
        BINOMIAL["language"] != "Latin",
        BINOMIAL["parts"][0] == "屬" and BINOMIAL["genus_capital"],
        BINOMIAL["epithet_capital"],
        "科" in same_genus_shares and "屬" not in same_genus_shares,
    ]


# History (nat.json BGb-Vc-3: Linnaeus's system had no idea of kinship or evolution; common ancestry
# changed classification). Years: binomial naming 1750s (Species Plantarum, 1753); Darwin's On the
# Origin of Species, 1859; five kingdoms late 1960s; three domains 1990 (well-established dates).
HISTORY = {
    "linnaeus": {"basis": "similarity_of_form", "kinship_idea": False, "year": 1753},
    "darwin_origin": {"year": 1859},
    "five_kingdoms": {"year": 1969, "later_revised": True},  # revised into three domains
    "three_domains": {"year": 1990},
}
MODERN_GOAL = "reflect_kinship"  # after common ancestry (BGb-Vc-3 3-2)


def cbd_history(item: dict) -> list[bool]:
    """q2 (multi): Linnaeus grouped by form; Linnaeus built on common ancestry; Origin came before
    binomial naming; after common ancestry classification aims to reflect kinship; classification
    never changes and five kingdoms were never revised."""
    lin = HISTORY["linnaeus"]
    return [
        lin["basis"] == "similarity_of_form",
        lin["kinship_idea"],
        HISTORY["darwin_origin"]["year"] < lin["year"],
        MODERN_GOAL == "reflect_kinship",
        not HISTORY["five_kingdoms"]["later_revised"],
    ]


# --- cells, kingdoms and domains ----------------------------------------------------------------

# Cell type of each organism (standard 國中/必修 examples; the chapter's five-kingdom examples).
CELL_TYPE = {
    "大腸桿菌": "prokaryotic",  # a bacterium
    "藍綠菌": "prokaryotic",    # cyanobacteria are bacteria
    "酵母菌": "eukaryotic",     # a fungus
    "香菇": "eukaryotic",       # a fungus
    "草履蟲": "eukaryotic",     # a protist
    "水綿": "eukaryotic",       # a green alga
    "人": "eukaryotic",
}


def _domain_of_cell(cell_type: str, archaeal: bool = False) -> str:
    if cell_type == "eukaryotic":
        return "真核生物域"
    return "古細菌域" if archaeal else "細菌域"


def cbd_eukaryote_count(item: dict) -> int:
    """q4: how many of the seven organisms belong to domain Eukarya?"""
    listed = ["大腸桿菌", "藍綠菌", "酵母菌", "香菇", "草履蟲", "水綿", "人"]
    return sum(_domain_of_cell(CELL_TYPE[o]) == "真核生物域" for o in listed)


# Five kingdoms -> three domains (nat.json BGb-Vc-4 4-2). The prokaryote kingdom splits in two; the
# four eukaryotic kingdoms all go to Eukarya. Domains were drawn from molecular sequence comparisons.
KINGDOM_TO_DOMAINS = {
    "原核生物界": {"細菌域", "古細菌域"},
    "原生生物界": {"真核生物域"},
    "真菌界": {"真核生物域"},
    "植物界": {"真核生物域"},
    "動物界": {"真核生物域"},
}
DOMAIN_TREE = ("細菌", ("古細菌", "真核生物"))
HAS_NUCLEUS = {"細菌": False, "古細菌": False, "真核生物": True}
THREE_DOMAIN_BASIS = "molecular_sequences"


def cbd_turn_archaea(item: dict) -> list[bool]:
    """q-archaea: bacteria and archaea both lack a nucleus; by molecular sequences, which do archaea share
    the more recent common ancestor with? Decided on DOMAIN_TREE (the three-domain tree, BGb-Vc-4 4-2),
    not on HAS_NUCLEUS. Options: bacteria; eukaryotes; equally; cannot compare (different cell types)."""
    t = DOMAIN_TREE
    to_bac, to_euk = _mrca_depth(t, "古細菌", "細菌"), _mrca_depth(t, "古細菌", "真核生物")
    comparable = all(name in _paths(t) for name in ("古細菌", "細菌", "真核生物"))
    return [to_bac > to_euk, to_euk > to_bac, to_bac == to_euk, not comparable]


def cbd_domains(item: dict) -> list[bool]:
    """q7 (multi): prokaryotes split into Bacteria and Archaea; the four eukaryotic kingdoms all in
    Eukarya; archaea have a nucleus; archaea closer to eukaryotes than to bacteria; domains based on
    form and nutrition."""
    four = ["原生生物界", "真菌界", "植物界", "動物界"]
    return [
        KINGDOM_TO_DOMAINS["原核生物界"] == {"細菌域", "古細菌域"},
        all(KINGDOM_TO_DOMAINS[k] == {"真核生物域"} for k in four),
        HAS_NUCLEUS["古細菌"],
        _closer(DOMAIN_TREE, "古細菌", "真核生物", "細菌"),
        THREE_DOMAIN_BASIS == "form_and_nutrition",
    ]


# A virus (nat.json BGb-Vc-4 4-4; the cell-theory chapter): genetic material in a protein coat, no
# cell structure, copied only inside living cells. Domains group cellular organisms by cell type.
VIRUS = {"is_cell": False, "has_genetic_material": True, "evolves": True, "is_bacterium": False,
         "hosts": {"humans", "animals", "plants", "bacteria"}}


def _can_be_in_a_domain(org: dict) -> bool:
    return org["is_cell"]


def cbd_virus(item: dict) -> list[bool]:
    """q6: the main reason viruses are not placed in the three domains. Options: no genetic material;
    no cell structure while the domains classify cells; viruses do not evolve; viruses are bacteria;
    viruses infect only humans."""
    return [
        not VIRUS["has_genetic_material"],
        not _can_be_in_a_domain(VIRUS) and not VIRUS["is_cell"],
        not VIRUS["evolves"],
        VIRUS["is_bacterium"],
        VIRUS["hosts"] == {"humans"},
    ]


# --- biodiversity bookkeeping ------------------------------------------------------------------------


def _ledger(start: int, periods: list[tuple[int, int]]) -> list[int]:
    """Species count at the end of each period (BGb-Vc-5 5-1: species keep forming and going extinct):
    each period adds the species formed and removes the species gone extinct."""
    out, n = [], start
    for formed, extinct in periods:
        n += formed - extinct
        assert n >= 0
        out.append(n)
    return out


def cbd_species_minimum(item: dict) -> list[bool]:
    """q8: start 30; periods (formed, extinct) = (6, 2), (3, 15) [mass extinction], (8, 5), (2, 9).
    At the end of which period is the count lowest? Options: periods 1-4; all the same."""
    ends = _ledger(30, [(6, 2), (3, 15), (8, 5), (2, 9)])
    low = min(ends)
    return [ends[i] == low and ends.count(low) == 1 for i in range(4)] + [len(set(ends)) == 1]


def _recovery_time(start: int, s: int, e: int, t_extinction: int, d: int) -> int:
    """The chapter's graph model: count = start + (s - e) t, dropping by d at t_extinction. Units of time
    after the extinction until the count is back to its level just before it."""
    before = start + (s - e) * t_extinction
    t = t_extinction
    n = before - d
    while n < before:
        t += 1
        n += s - e
    return t - t_extinction


# --- the chapter's own numbers (Predicts), kept honest here too -------------------------------------
assert _branch_points(AMNIOTE_TREE) == 4  # Predict tree-nodes
assert _recovery_time(40, 4, 2, 5, 20) == 10  # Predict recovery-time
assert 40 + (4 - 2) * 10 - 20 == 40  # its reveal: the line at time 10 with d = 20
