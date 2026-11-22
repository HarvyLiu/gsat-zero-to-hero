"""Checks for src/data/items/biology/s116-cell-theory-structure.yaml (116 sprint: BMb-Ⅴc-1, BDa-Ⅴc-1,
BDa-Ⅴc-2: the history of the cell theory, cell shape and function, slide methods and the micrometer,
prokaryotic and eukaryotic cells and their organelles).

How the keys are recomputed (never from item["answer"]):
- Qualitative biology is encoded as code tables (who contributed what; the three points of the cell
  theory; what a virus has; which method gives which kind of thin layer; which structures each cell type
  has; what each organelle does). Each option is turned into a claim and judged against the tables.
- Sources: nat.json (BMb-Vc-1, BDa-Vc-1, BDa-Vc-2 keyConcepts: the five scientists of 115 Q30, the
  four slide methods, the micrometer with no scale conversion, the six organelles) and the 必修 depth
  notes in the chapter's research slice. The facts inside each row (e.g. that Brown described the
  nucleus) are standard 必修/國中 biology at the depth the 說明 allows; each row says which.
- The micrometer item is image scaling: the eyepiece scale is fixed and the objective enlarges only the
  image, so the count of divisions scales with the objective's magnification (exact integers).
"""

from __future__ import annotations

from fractions import Fraction as F

# --- history (BMb-Vc-1) -----------------------------------------------------------------------

# Who did what. nat.json BMb-Vc-1 keyConcepts names Hooke, Leeuwenhoek, Brown, Schleiden and Virchow
# (115 Q30); Schwann is the standard partner of Schleiden in 必修 accounts of the cell theory.
# The contributions are the standard 必修 textbook account (no dates are used by any item).
HISTORY = {
    ("Hooke", "named_cells_from_cork"),          # saw the empty compartments of cork, called them cells
    ("Leeuwenhoek", "saw_living_microorganisms"),  # own ground lenses; living tiny organisms, bacteria
    ("Brown", "described_nucleus"),              # described the nucleus in plant cells
    ("Schleiden", "plants_made_of_cells"),
    ("Schwann", "animals_made_of_cells"),
    ("Virchow", "cells_from_existing_cells"),
}

# The three points of the cell theory (chapter text; 必修 BMb-Vc-1 at review depth).
TENETS = {"organisms_made_of_cells", "cell_is_basic_unit", "cells_from_existing_cells"}

# Cork as Hooke saw it: dead tissue, contents gone, only the cell walls left (standard account).
CORK = {"alive": False, "remaining": {"cell_wall"}}

# A virus (113 Q3 context per nat.json BMb-Vc-1): genetic material in a protein coat, no cell structure,
# no cytoplasm or ribosomes of its own, copied only inside living cells.
VIRUS = {
    "is_cell": False,
    "number_of_cells": 0,
    "has_nuclear_envelope": False,
    "reproduces_only_inside_living_cells": True,
}


def cts_turn_cork(item: dict) -> list[bool]:
    """q-turn: what were Hooke's little boxes? Options: nuclei of living cells; cell walls left by dead
    cells; air bubbles; chloroplasts; bacteria. A claim is right when it names what CORK has left and
    agrees with whether the cells were alive."""
    options = [
        ({"nucleus"}, True),
        ({"cell_wall"}, False),
        ({"air_bubble"}, None),
        ({"chloroplast"}, True),
        ({"bacterium"}, True),
    ]
    return [parts <= CORK["remaining"] and alive == CORK["alive"] for parts, alive in options]


def cts_turn_virus(item: dict) -> list[bool]:
    """q-virus: how does a virus clash with the cell theory? Each option is a set of claims about a
    virus; it is right when every claim matches VIRUS."""
    options = [
        {"is_cell": False, "reproduces_only_inside_living_cells": True},
        {"is_cell": True, "number_of_cells": 1},          # 'a single prokaryotic cell'
        {"has_nuclear_envelope": True},
        {"is_cell": True},                                 # 'its cells are too small to see'
        {"is_cell": True, "number_of_cells": 2},           # 'made of many cells' (any number > 1)
    ]
    return [all(VIRUS[k] == v for k, v in claims.items()) for claims in options]


def cts_history_pairs(item: dict) -> list[bool]:
    """q1: a pairing is right exactly when it is in HISTORY."""
    options = [
        ("Hooke", "described_nucleus"),
        ("Leeuwenhoek", "saw_living_microorganisms"),
        ("Brown", "animals_made_of_cells"),
        ("Schwann", "cells_from_existing_cells"),
        ("Virchow", "named_cells_from_cork"),
    ]
    return [opt in HISTORY for opt in options]


def cts_tenets(item: dict) -> list[bool]:
    """q2: which statements are points of the cell theory? 'Every cell has a nucleus' is false for
    prokaryotic cells (see STRUCTURES below), and 'a virus is the smallest cell' contradicts VIRUS."""
    assert STRUCTURES["nucleus"]["prokaryote"] is False
    assert VIRUS["is_cell"] is False
    options = ["organisms_made_of_cells", "cell_is_basic_unit", "cells_from_existing_cells",
               "every_cell_has_nucleus", "virus_is_smallest_cell"]
    return [o in TENETS for o in options]


# --- slide methods and the micrometer (BDa-Vc-1) -------------------------------------------------

# The four 探討活動 methods (nat.json BDa-Vc-1: 折撕法, 壓片法, 抹片法, 徒手切片), described by what you
# do and what thin layer results. 'whole' (putting the whole piece on the slide) is the non-method.
METHODS = {
    "smear":   {"layer": "loose_cells", "keeps_tissue_arrangement": False, "thin": True},
    "squash":  {"layer": "spread_cells", "keeps_tissue_arrangement": False, "thin": True},
    "fold_tear": {"layer": "surface_epidermis", "keeps_tissue_arrangement": False, "thin": True},
    "section": {"layer": "cross_section", "keeps_tissue_arrangement": True, "thin": True},
    "whole":   {"layer": "thick_piece", "keeps_tissue_arrangement": True, "thin": False},
}


def cts_stem_section(item: dict) -> list[bool]:
    """q3: to see how the vascular bundles are arranged in a stem's cross-section you need a thin layer
    (light must pass) that keeps the tissue arrangement and is a cross-section.
    Options in order: smear; squash; fold and tear; free-hand section; whole piece."""
    order = ["smear", "squash", "fold_tear", "section", "whole"]
    need = lambda m: m["thin"] and m["keeps_tissue_arrangement"] and m["layer"] == "cross_section"
    return [need(METHODS[k]) for k in order]


def _divisions(at_low: int, objective_factor: int) -> int:
    """Divisions covered on a fixed eyepiece scale when the objective magnifies k times more: the image
    length scales by k, the scale does not."""
    image = F(at_low) * objective_factor
    assert image.denominator == 1
    return int(image)


def cts_micrometer(item: dict) -> int:
    """q6: 6 divisions under the first objective; switch to one with 3 times the magnification."""
    # cross-check the chapter's Predict (5 divisions, 4 times) with the same rule
    assert _divisions(5, 4) == 20
    return _divisions(6, 3)


# --- prokaryotic and eukaryotic cells (BDa-Vc-2) -------------------------------------------------

# Which cell types have each structure (nat.json BDa-Vc-2 keyConcepts 2-1~2-3; standard 必修 account).
# 'prokaryote' = bacteria/cyanobacteria; for the cell wall, most prokaryotes have one ('most').
STRUCTURES = {
    "cell_membrane":  {"prokaryote": True,  "eukaryote": True},
    "ribosome":       {"prokaryote": True,  "eukaryote": True},
    "genetic_material": {"prokaryote": True, "eukaryote": True},
    "nucleus":        {"prokaryote": False, "eukaryote": True},   # nucleus wrapped in a nuclear envelope
    "nuclear_envelope": {"prokaryote": False, "eukaryote": True},
    "mitochondrion":  {"prokaryote": False, "eukaryote": True},
    "endoplasmic_reticulum": {"prokaryote": False, "eukaryote": True},
    "golgi":          {"prokaryote": False, "eukaryote": True},
    "vacuole":        {"prokaryote": False, "eukaryote": True},
    "chloroplast":    {"prokaryote": False, "eukaryote": True},   # in some eukaryotes (green plant parts)
}

SIX_CYTOPLASMIC = ["endoplasmic_reticulum", "golgi", "vacuole", "ribosome", "mitochondrion", "chloroplast"]


def cts_shared_structures(item: dict) -> list[bool]:
    """q4: structures found in both prokaryotic and eukaryotic cells.
    Options: cell membrane; ribosome; nuclear envelope; mitochondrion; genetic material."""
    # cross-check the chapter's Predict: of the six cytoplasmic structures, prokaryotes have 1
    assert sum(STRUCTURES[s]["prokaryote"] for s in SIX_CYTOPLASMIC) == 1
    order = ["cell_membrane", "ribosome", "nuclear_envelope", "mitochondrion", "genetic_material"]
    return [STRUCTURES[s]["prokaryote"] and STRUCTURES[s]["eukaryote"] for s in order]


# Organelle roles (nat.json BDa-Vc-2 2-3; chapter table at 必修 depth).
ROLES = {
    "rough_er": {"make_protein", "transport_protein"},   # ER with ribosomes attached
    "golgi": {"package_ship_protein"},
    "chloroplast": {"photosynthesis"},
    "vacuole": {"store"},
    "cell_wall": {"support"},
    "mitochondrion": {"respiration_release_energy"},
}
# The route of a secreted protein (chapter Perspective): made and moved in rough ER, then packed in Golgi.
SECRETION_NEEDS = {"make_protein", "transport_protein", "package_ship_protein"}


def cts_secreting_cell(item: dict) -> list[bool]:
    """q5: which pair is especially well developed in a cell that secretes a lot of protein? A pair is
    right when together its roles cover the secretion route.
    Options: rough ER + Golgi; chloroplast + vacuole; cell wall + vacuole; chloroplast + cell wall;
    mitochondrion + chloroplast."""
    pairs = [("rough_er", "golgi"), ("chloroplast", "vacuole"), ("cell_wall", "vacuole"),
             ("chloroplast", "cell_wall"), ("mitochondrion", "chloroplast")]
    return [SECRETION_NEEDS <= (ROLES[a] | ROLES[b]) for a, b in pairs]


# Function from abundance: a cell with especially many of one structure especially needs that
# structure's work (chapter text, BDa-Vc-1 shape/structure fits function). The roles come from ROLES;
# "needs a lot of energy" is the demand that matches the mitochondrion's role (chapter table: it
# releases the energy in food for the cell to use). Standard 必修: active muscle cells are rich in
# mitochondria.
DEMAND_OF_ROLE = {
    "respiration_release_energy": "much_energy",
    "photosynthesis": "make_own_food",
    "store": "store_water",
    "package_ship_protein": "secrete_protein",
    "support": "rigid_support",
}


def cts_mito_rich_cell(item: dict) -> list[bool]:
    """q8: a human muscle cell packed with mitochondria. Which feature does that structure point to?
    Options: much energy; photosynthesis; storing water; secreting protein; rigid support."""
    abundant = "mitochondrion"
    implied = {DEMAND_OF_ROLE[r] for r in ROLES[abundant]}
    options = ["much_energy", "make_own_food", "store_water", "secrete_protein", "rigid_support"]
    return [o in implied for o in options]


# Features of particular cells (國中 Da-Ⅳ-1 / 必修 BDa-Vc-1~2; standard): wall, large central vacuole,
# chloroplasts. Onion bulb-scale epidermis and root cells are plant cells without chloroplasts; leaf
# mesophyll has chloroplasts; human cells have no wall; mature human red cells also lack a nucleus.
CELLS = {
    "onion_scale_epidermis": {"wall": True,  "large_vacuole": True,  "chloroplast": False},
    "human_cheek":           {"wall": False, "large_vacuole": False, "chloroplast": False},
    "leaf_mesophyll":        {"wall": True,  "large_vacuole": True,  "chloroplast": True},
    "plant_root":            {"wall": True,  "large_vacuole": True,  "chloroplast": False},
    "human_red_cell":        {"wall": False, "large_vacuole": False, "chloroplast": False},
}


def cts_wall_no_chloroplast(item: dict) -> list[bool]:
    """q7: a cell with a cell wall and a large central vacuole but no chloroplasts. Which could it be?
    Options in CELLS order."""
    want = {"wall": True, "large_vacuole": True, "chloroplast": False}
    return [all(CELLS[c][k] == v for k, v in want.items()) for c in CELLS]
