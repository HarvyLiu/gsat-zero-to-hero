"""Checks for src/data/items/chemistry/s116-solutions.yaml (116 sprint: CJb-Ⅴc-1 and CJb-Ⅴc-3 types of
solutions and molarity, CJb-Ⅴc-2 and CJe-Ⅴc-1 solubility and the dissolving equilibrium).

Every check recomputes its item's key from the chemistry in the stem, never from item["answer"]:
- dispersions are classified by particle diameter with the chapter's boundaries (about 1e-9 m and
  1e-6 m); the Tyndall effect is shown by colloids only (the one colloid property the 課綱 asks for);
- concentrations (ppm, molarity, dilution) are exact SymPy Rationals with the atomic masses each stem
  states; molarity is moles ÷ litres of SOLUTION, so a recipe that does not fix the solution volume
  (solute added to a volume of water) fixes no molarity;
- crystallised mass is (solubility at the high T − solubility at the low T) × water / 100;
- the saturated-solution item runs a small dissolving–crystallising model: at equilibrium the
  dissolved amount is min(total solute, S(T) × water / 100) and, while solid remains, the dissolving
  and crystallising rates are equal and non-zero.
"""

from __future__ import annotations

from sympy import Integer, Rational

# Particle-size boundaries the chapter uses (approximate, in metres): below 1 nm a true solution,
# 1 nm to 1000 nm a colloid, above that a suspension.
NM = Rational(1, 10**9)
LOW, HIGH = 1 * NM, 1000 * NM


def classify(diameter_m: Rational) -> str:
    if diameter_m < LOW:
        return "solution"
    if diameter_m <= HIGH:
        return "colloid"
    return "suspension"


def shows_tyndall(kind: str) -> bool:
    """Light scattered sideways (a visible path) needs colloid-sized particles. A true solution's
    particles are too small; suspensions are not asked about (they are cloudy and settle)."""
    return kind == "colloid"


# What the dispersed particles are in each liquid the items name, as standard high-school texts
# classify them (the chapter's section 1 and its examples): single molecules or ions dissolved in
# water make true solutions; large protein molecules (egg white), carbon particles (ink) and starch
# give colloids.
KIND = {
    "salt water": "solution",          # Na+ and Cl- ions
    "dilute starch water": "colloid",  # starch: very large molecules
    "glucose solution": "solution",    # single glucose molecules
    "dilute egg white": "colloid",     # large protein molecules
    "copper sulfate solution": "solution",  # Cu2+ and SO4 2- ions
    "dilute ink": "colloid",           # carbon particles (墨汁)
    "alcohol solution": "solution",    # single ethanol molecules
}


def molarity(moles: Rational, litres: Rational) -> Rational:
    return Rational(moles) / Rational(litres)


def decimal_cells(x: Rational) -> tuple[str, str]:
    """A non-negative value with one decimal place → ('integer part', 'tenths digit') for ①.②."""
    whole = int(x)  # floor for x ≥ 0
    tenth = (x - whole) * 10
    assert tenth.is_integer and 0 <= tenth < 10, f"{x} has more than one decimal place"
    return (str(whole), str(int(tenth)))


# ---------------------------------------------------------------------------------------------------


def sol_turn_tyndall(item: dict) -> list[bool]:
    """q-turn: a laser beam through salt water and through dilute starch water, seen from the side.
    Options: only salt water; only starch water; both; neither."""
    salt = shows_tyndall(KIND["salt water"])
    starch = shows_tyndall(KIND["dilute starch water"])
    outcomes = [salt and not starch, starch and not salt, salt and starch, not salt and not starch]
    return outcomes


def sol_tyndall_liquids(item: dict) -> list[bool]:
    """q1 (multi): which liquids show a bright path when a laser passes through?
    Options: glucose solution, dilute egg white, copper sulfate solution, dilute ink, alcohol solution."""
    names = ["glucose solution", "dilute egg white", "copper sulfate solution", "dilute ink", "alcohol solution"]
    return [shows_tyndall(KIND[n]) for n in names]


def sol_size_class(item: dict) -> list[bool]:
    """q2: dispersed particles about 200 nm across (1 nm = 1e-9 m) → 2e-7 m → colloid.
    Options: true solution; colloid; suspension; cannot tell without the concentration (the class
    depends on size only, so that option is false)."""
    kind = classify(200 * NM)
    # 'cannot tell' would be right only if the diameter left the class undecided; classify() needs
    # nothing but the diameter, so it is right only when no class came out.
    undecided = kind not in ("solution", "colloid", "suspension")
    return [kind == "solution", kind == "colloid", kind == "suspension", undecided]


def sol_ppm(item: dict) -> list[bool]:
    """q3: 0.0060 g of a substance in a 2.0 kg water sample → 0.0060 / 2000 × 10^6 = 3 ppm.
    Options: 0.3, 3, 30, 3000, 3 × 10^-6."""
    ppm = Rational(60, 10**4) / Integer(2000) * 10**6
    options = [Rational(3, 10), Integer(3), Integer(30), Integer(3000), 3 * Rational(1, 10**6)]
    return [ppm == o for o in options]


def sol_kcl_molarity(item: dict) -> tuple[str, str]:
    """q4: 14.9 g KCl (K = 39, Cl = 35.5 → 74.5 g/mol) made up to 500 mL → 0.2 mol / 0.5 L = 0.4 M,
    written ①.② → ('0', '4')."""
    molar_mass = Integer(39) + Rational(71, 2)
    n = Rational(149, 10) / molar_mass
    return decimal_cells(molarity(n, Rational(500, 1000)))


def sol_prepare_glucose(item: dict) -> list[bool]:
    """q5: which recipe gives exactly 0.10 M glucose (C6H12O6; H = 1, C = 12, O = 16 → 180 g/mol)?
    Each option is (grams, how the volume is set, litres). 'water' = solute added to that volume of
    water: the solution's volume is not fixed, so no exact molarity follows. 'mark' = dissolved, then
    made up to the mark of a volumetric flask of that volume: C = (g / 180) / litres."""
    molar_mass = 6 * Integer(12) + 12 * Integer(1) + 6 * Integer(16)
    target = Rational(1, 10)
    recipes = [
        (Integer(18), "water", Integer(1)),
        (Integer(18), "mark", Integer(1)),
        (Rational(18, 10), "mark", Integer(1)),
        (Integer(180), "mark", Integer(1)),
        (Integer(18), "mark", Rational(100, 1000)),
    ]
    out = []
    for grams, how, litres in recipes:
        c = molarity(grams / molar_mass, litres) if how == "mark" else None
        out.append(c == target)
    return out


def sol_dilution_volume(item: dict) -> int:
    """q6: 500 mL of 0.20 M NaOH from 4.0 M stock: C1 V1 = C2 V2 → V1 = 0.20 × 500 / 4.0 = 25 mL."""
    v1 = Rational(20, 100) * 500 / Rational(40, 10)
    assert v1.is_integer
    return int(v1)


def sol_crystallised_mass(item: dict) -> int:
    """q7: solubility of X (g per 100 g water) 20 °C 30, 40 °C 45, 60 °C 70, 80 °C 100. A saturated
    solution made with 200 g water at 80 °C, cooled to 40 °C: (100 − 45) × 200 / 100 = 110 g."""
    table = {20: Integer(30), 40: Integer(45), 60: Integer(70), 80: Integer(100)}
    water = Integer(200)
    crystals = (table[80] - table[40]) * water / 100
    assert crystals.is_integer
    return int(crystals)


# Substance 甲 of the chapter: solubility S(T) = 10 + T^2/50 g per 100 g water, rising with T.
def s_jia(t: int) -> Rational:
    return 10 + Rational(t * t, 50)


def equilibrate(water: Rational, total: Rational, t: int) -> dict[str, Rational]:
    """The dissolving–crystallising model at equilibrium. While solid remains, the concentration sits
    at the solubility and the two rates are equal: dissolving rate k (solid present), crystallising
    rate k × (concentration ÷ saturated concentration)."""
    dissolved = min(total, s_jia(t) * water / 100)
    solid = total - dissolved
    conc = dissolved / water
    k = Integer(1)
    r_dissolve = k if solid > 0 else Integer(0)
    r_crystallise = k * conc / (s_jia(t) / 100)
    return {"solid": solid, "conc": conc, "r_dis": r_dissolve, "r_cry": r_crystallise}


def sol_saturated_statements(item: dict) -> list[bool]:
    """q8 (multi): a covered saturated solution of 甲 at 40 °C with a little solid left; S rises with T.
    Options:
    (1) the solid's mass keeps decreasing → d(solid)/dt = r_cry − r_dis < 0?
    (2) dissolving and crystallising both keep happening → both rates > 0;
    (3) adding a little more solid makes the solution more concentrated;
    (4) evaporating some water at 40 °C: more solid, same concentration;
    (5) heating to 60 °C: less solid."""
    water, total = Integer(100), s_jia(40) * 1 + 5  # saturated, plus 5 g of undissolved solid
    now = equilibrate(water, total, 40)
    s1 = now["r_cry"] - now["r_dis"] < 0
    s2 = now["r_dis"] > 0 and now["r_cry"] > 0
    more_solid = equilibrate(water, total + 2, 40)
    s3 = more_solid["conc"] > now["conc"]
    evaporated = equilibrate(water - 20, total, 40)
    s4 = evaporated["solid"] > now["solid"] and evaporated["conc"] == now["conc"]
    heated = equilibrate(water, total, 60)
    s5 = heated["solid"] < now["solid"]
    return [s1, s2, s3, s4, s5]
