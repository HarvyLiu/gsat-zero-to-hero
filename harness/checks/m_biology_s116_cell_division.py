"""Checks for src/data/items/biology/s116-cell-division.yaml (116 sprint: BDa-Ⅴc-5~9: the cell cycle,
chromosome copying, mitosis, meiosis and gamete formation, the zygote and cell differentiation).

How the keys are recomputed (never from item["answer"]):
- A small division engine. A cell is a list of chromosomes; each chromosome records which homologous
  pair it belongs to, which parent it came from, and how many joined copies it has (1 or 2). Copying,
  mitosis and the two divisions of meiosis are functions on cells, so chromosome counts, cell counts and
  relative amounts of genetic material come out of the rules, not out of typed numbers.
- Times from slide counts with exact Rationals: the share of cells in a stage is taken as the share of
  the cycle's time (the chapter's stated assumption: the cells are not in step with one another).
- Qualitative facts are small tables, each with a source comment.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F

import sympy as sp


@dataclass(frozen=True)
class Chrom:
    pair: int  # which homologous pair
    origin: str  # 'father' or 'mother'
    copies: int  # 1 before copying, 2 after (two joined copies still count as one chromosome)


Cell = list[Chrom]


def body_cell(two_n: int) -> Cell:
    """An unreplicated diploid cell: n pairs, one chromosome of each pair from each parent."""
    assert two_n % 2 == 0
    return [Chrom(p, o, 1) for p in range(two_n // 2) for o in ("father", "mother")]


def replicate(cell: Cell) -> Cell:
    """Interphase copying (BDa-Ⅴc-5): every chromosome becomes two joined copies; the count is unchanged."""
    assert all(c.copies == 1 for c in cell)
    return [replace(c, copies=2) for c in cell]


def split_copies(cell: Cell) -> list[Cell]:
    """The two copies of every chromosome separate, one to each daughter (mitosis; meiosis's second division)."""
    assert all(c.copies == 2 for c in cell), "copies can only separate after copying"
    half = [replace(c, copies=1) for c in cell]
    return [list(half), list(half)]


def mitosis(cell: Cell) -> list[Cell]:
    """Copy once, divide once (BDa-Ⅴc-7)."""
    return split_copies(replicate(cell))


def meiosis_first(cell: Cell) -> list[Cell]:
    """First division of meiosis (BDa-Ⅴc-8): the two members of each homologous pair go to different
    cells. Which parent's chromosome goes to which cell may vary; here pair k sends 'father' to cell 0
    when k is even, so both combinations appear."""
    assert all(c.copies == 2 for c in cell)
    a: Cell = []
    b: Cell = []
    for c in cell:
        first = (c.origin == "father") == (c.pair % 2 == 0)
        (a if first else b).append(c)
    return [a, b]


def meiosis(cell: Cell) -> list[Cell]:
    """Copy once, then divide twice in a row: four cells."""
    out: list[Cell] = []
    for half in meiosis_first(replicate(cell)):
        out.extend(split_copies(half))
    return out


def n_sets(cell: Cell) -> F:
    """Chromosome sets in a cell, counting chromosomes (not copies): 2 for 2n, 1 for n."""
    pairs = {c.pair for c in cell}
    return F(len(cell), len(pairs))


def has_full_set(cell: Cell, n: int) -> bool:
    return {c.pair for c in cell} == set(range(n))


def has_homologous_pair(cell: Cell) -> bool:
    pairs = [c.pair for c in cell]
    return len(pairs) != len(set(pairs))


def relative_amount(cell: Cell, n: int) -> F:
    """Relative amount of genetic material, scaled so that a just-divided 2n body cell has 2."""
    return F(sum(c.copies for c in cell), n)


# --- opening turn ---------------------------------------------------------------------------------

# Stage shares of the cell cycle as a table of time fractions. The only fact used is that interphase
# is longer than the division phase (standard 必修 content of BDa-Ⅴc-5: the cycle is 間期 + 細胞分裂期;
# the chapter states it). So the interphase share s lies in the open interval (1/2, 1): more than half,
# and less than all, because the division phase also takes time. No number from outside the sources.
# Sub-steps of the division phase (chromosomes lined up in the middle, cytokinesis) are parts of the
# division phase, so each has a share in (0, 1 - s].
# Chromosomes are visible as separate threads only in the division phase (long, thin and spread out in
# interphase): standard 必修 content of BDa-Ⅴc-7 (observing chromosome changes on mitosis slides).
SEPARATE_CHROMOSOMES_VISIBLE = {"interphase": False, "division": True}


def _for_all_shares(pred) -> bool:
    """Decide a claim about the interphase share s for every s in (1/2, 1); refuse if it depends on s.
    pred(s) returns a SymPy relation; the set where it holds is compared with the whole interval."""
    s = sp.Symbol("s", real=True)
    domain = sp.Interval.open(sp.Rational(1, 2), 1)
    holds = sp.solveset(pred(s), s, domain)
    if holds == domain:
        return True
    assert holds == sp.S.EmptySet, f"claim depends on the exact share: {holds}"
    return False


def cd_turn_root_tip(item: dict) -> list[bool]:
    """q-turn: share of cells in a stage = share of time. Options: most cells in interphase with no
    separate chromosomes; most with chromosomes lined up in the middle (a part of the division phase);
    most in cytokinesis (also part of the division phase); about half and half; all dividing."""
    majority_interphase = _for_all_shares(lambda s: s > sp.Rational(1, 2))
    # a sub-step's largest possible share is the whole division phase, 1 - s
    majority_substep = _for_all_shares(lambda s: (1 - s) > sp.Rational(1, 2))
    half_and_half = _for_all_shares(lambda s: sp.Eq(s, 1 - s))
    all_dividing = _for_all_shares(lambda s: sp.Eq(1 - s, 1))
    return [
        majority_interphase and not SEPARATE_CHROMOSOMES_VISIBLE["interphase"],
        majority_substep,
        majority_substep,
        half_and_half,
        all_dividing,
    ]


# --- Check yourself ------------------------------------------------------------------------------


def cd_interphase_hours(item: dict) -> int:
    """q1: 300 cells counted, 275 in interphase; cycle 24 h. Interphase time = 24 × 275/300."""
    hours = F(24) * F(275, 300)
    assert hours.denominator == 1
    return int(hours)


def cd_which_has_eight(item: dict) -> list[bool]:
    """q2: an animal with 2n = 16. Options: zygote; skin cell just after mitosis; sperm; muscle cell;
    body cell just after copying, before dividing. Which has 8 chromosomes?"""
    two_n = 16
    body = body_cell(two_n)
    # fertilisation: a sperm and an egg from meiosis join
    sperm = meiosis(body)[0]
    egg = meiosis(body)[1]
    zygote = [replace(c) for c in sperm + egg]
    skin = mitosis(zygote)[0]
    muscle = mitosis(mitosis(zygote)[1])[0]
    copied = replicate(body)
    cells = [zygote, skin, sperm, muscle, copied]
    return [len(c) == 8 for c in cells]


# Where each kind of division happens (BDa-Ⅴc-8 說明 8-1: human reproductive cells; 國中 Db-Ⅳ-4: the
# testes make sperm and the ovaries make eggs).
MEIOSIS_SITES_HUMAN = {"testis", "ovary"}


def cd_compare_divisions(item: dict) -> list[bool]:
    """q3 (multi): (1) mitosis daughters have the parent's chromosome number; (2) no copying is needed
    before meiosis; (3) meiosis gives four cells from one; (4) meiosis products still have homologous
    pairs; (5) in humans meiosis happens only in the testes, never in the ovaries."""
    n = 3
    parent = body_cell(2 * n)
    mito = mitosis(parent)
    meio = meiosis(parent)
    s1 = all(len(d) == len(parent) for d in mito)

    # (2) without copying, divide the material twice: each cell gets a quarter of the chromosomes,
    # which cannot be one full set
    per_cell_without_copy = F(len(parent), 4)
    s2 = per_cell_without_copy == n  # true only if every cell would still get a full set of n
    s3 = len(meio) == 4
    s4 = any(has_homologous_pair(c) for c in meio)
    s5 = MEIOSIS_SITES_HUMAN == {"testis"}
    assert all(has_full_set(c, n) for c in meio)
    return [s1, s2, s3, s4, s5]


def cd_after_first_division(item: dict) -> int:
    """q4: 2n = 20; chromosomes per cell after the first division of meiosis."""
    first = meiosis_first(replicate(body_cell(20)))
    counts = {len(c) for c in first}
    assert len(counts) == 1
    return counts.pop()


def cd_interphase_amounts(item: dict) -> list[bool]:
    """q5 (multi): a just-divided body cell has relative amount 2. Cells have 1, 2, 3, 4. Which could be
    a body cell in interphase? In interphase the amount runs from 2 (before copying) up to 4 (after),
    passing through the values in between while copying goes on (the chapter's graph). Option 5: none."""
    n = 4
    start = relative_amount(body_cell(2 * n), n)
    end = relative_amount(replicate(body_cell(2 * n)), n)
    assert (start, end) == (2, 4)
    amounts = [F(1), F(2), F(3), F(4)]
    possible = [start <= a <= end for a in amounts]
    # the gamete value is outside the interphase range, as a cross-check
    assert relative_amount(meiosis(body_cell(2 * n))[0], n) == 1
    return possible + [not any(possible)]


def cd_rounds_for_128(item: dict) -> int:
    """q6: every cell divides once per round by mitosis; how many rounds from 1 cell to 128 cells?"""
    cells = [body_cell(4)]
    rounds = 0
    while len(cells) < 128:
        cells = [d for c in cells for d in mitosis(c)]
        rounds += 1
    assert len(cells) == 128
    assert all(len(c) == 4 for c in cells)  # the chromosome number never changes by mitosis
    return rounds


# Cell differentiation, introductory only (BDa-Ⅴc-9 說明 9-1): cells become different in shape,
# structure and function; the body's cells come from the zygote by mitosis (BDa-Ⅴc-9 title).
DIFFERENTIATION_CHANGES = {"shape", "structure", "function"}
BODY_CELLS_FROM_ZYGOTE_BY = "mitosis"


def cd_differentiation(item: dict) -> list[bool]:
    """q7 (multi): (1) one person's nerve and muscle cells have the same chromosome number; (2)
    differentiation makes cells differ in shape, structure and function; (3) differentiating cells drop
    half their chromosomes by meiosis; (4) the body's cells form from the zygote by meiosis; (5)
    differentiated cells have more chromosomes than the zygote."""
    zygote = body_cell(46)
    # body cells: some rounds of mitosis; any two of them stand for a nerve cell and a muscle cell
    cells = [zygote]
    for _ in range(3):
        cells = [d for c in cells for d in mitosis(c)]
    nerve, muscle = cells[0], cells[-1]
    s1 = len(nerve) == len(muscle)
    s2 = {"shape", "structure", "function"} <= DIFFERENTIATION_CHANGES  # the claim, against the table
    s3 = any(len(c) == len(zygote) // 2 for c in cells)
    s4 = BODY_CELLS_FROM_ZYGOTE_BY == "meiosis"
    assert not s3
    s5 = any(len(c) > len(zygote) for c in cells)
    return [s1, s2, s3, s4, s5]


def cd_sperm_from_one(item: dict) -> list[bool]:
    """q8: a male animal with 2n = 12; one reproductive cell goes through meiosis and all the products
    become sperm (the chapter: in a male all four develop into sperm). Options: (cells, chromosomes each)."""
    products = meiosis(body_cell(12))
    got = (len(products), len(products[0]))
    assert len({len(c) for c in products}) == 1
    options = [(2, 12), (2, 6), (4, 6), (4, 12), (1, 6)]
    return [got == o for o in options]
