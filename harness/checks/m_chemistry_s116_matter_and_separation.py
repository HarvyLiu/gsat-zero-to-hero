"""Checks for src/data/items/chemistry/s116-matter-and-separation.yaml (116 sprint: CAb-Ⅴc-1 classifying
matter, states and phase diagrams; CEc-Ⅴc-1 gas pressure from molecular collisions; CCa-Ⅴc-1 separating
and purifying mixtures).

必修化學 is qualitative here, so most checks encode a rule as code instead of computing a number:
- Classification: a sample is a pure substance exactly when its component table has one entry.
- Phase diagrams (H2O and CO2 only, 課綱 limit): a substance is modelled by its triple point and the
  tilt of its solid–liquid line. Heating at a fixed pressure P is a walk along a level line: below the
  triple-point pressure it crosses only the solid–gas line; above it, solid–liquid then liquid–gas.
  Only these qualitative features are used, never a full equation of state (gas laws are 選修).
- Gas pressure: pressure rises with more hits on the walls per second, which needs more molecules in
  the same volume or faster molecules (higher temperature).
- Separation: each method is a rule on the property difference it uses (volatility, dissolved or not,
  immiscible solvent that dissolves the solute better, different adsorption).
Each function recomputes its item's answer from the situation in the stem; none reads item["answer"].
Sources for the data tables: the triple-point values are the ones stated in each stem; the method rules
are the 課綱 CCa-Ⅴc-1 key concepts (ink distillation, pigment extraction, TLC, hard water) as given in
src/data/registry/codes/nat.json.
"""

from __future__ import annotations

from sympy import Rational

# ---- phase-diagram model ---------------------------------------------------------------------------

# Data stated in the stems (pressures in atmospheres, temperatures in °C).
# sl_tilt: which way the solid–liquid line leans going up; lg_tilt: the liquid–gas line rises to the
# right (stated in the q2 stem for water). bp_1atm / mp_1atm: water's normal boiling and melting points
# (standard values, the 1 atm crossings drawn in the chapter's figure).
WATER = {"tp_T": Rational("0.01"), "tp_P": Rational("0.006"), "sl_tilt": "left", "lg_tilt": "right",
         "bp_1atm": 100, "mp_1atm": 0}
CO2 = {"tp_T": Rational("-56.6"), "tp_P": Rational("5.1"), "sl_tilt": "right", "lg_tilt": "right"}


def _isobar_states(sub: dict, p: Rational) -> list[str]:
    """States met in order when the solid is heated at fixed pressure p (below the critical point,
    which the 必修 diagrams don't use). Below the triple-point pressure there is no liquid region."""
    if p < sub["tp_P"]:
        return ["solid", "gas"]
    if p == sub["tp_P"]:
        return ["solid", "solid+liquid+gas", "gas"]
    return ["solid", "liquid", "gas"]


def _plateaus(sub: dict, p: Rational) -> int:
    """Level parts of the heating curve = phase-boundary lines crossed along the isobar."""
    return len(_isobar_states(sub, p)) - 1


def _boiling_point_rises_with_pressure(sub: dict) -> bool:
    """A liquid–gas line rising to the right: a higher-pressure level line meets it further right."""
    return sub["lg_tilt"] == "right"


def _melting_point_falls_with_pressure(sub: dict) -> bool:
    """A solid–liquid line tilted left means the melting temperature decreases as pressure rises."""
    return sub["sl_tilt"] == "left"


# ---- items -----------------------------------------------------------------------------------------


def sep_turn_dry_ice(item: dict) -> list[bool]:
    """q-turn: CO2 (triple point 5.1 atm) heated from −100 °C at 1 atm.
    Options: melts then boils; sublimes straight to gas; melts and stays liquid; stays solid;
    gas then condenses to liquid."""
    seq = _isobar_states(CO2, Rational(1))
    outcomes = [
        ["solid", "liquid", "gas"],
        ["solid", "gas"],
        ["solid", "liquid"],
        ["solid"],
        ["solid", "gas", "liquid"],
    ]
    return [o == seq for o in outcomes]


# Separation methods as rules on the mixture. A mixture is described by its parts; each part has
# 'dissolved' (in the liquid), 'volatile', and for extraction a solvent table.
SEAWATER = {"liquid": {"name": "water", "volatile": True}, "solute": {"name": "salt", "dissolved": True, "volatile": False}}


def _gives_pure_liquid(method: str, mix: dict) -> bool:
    """Does `method` collect the liquid itself, free of the solute?"""
    liq, sol = mix["liquid"], mix["solute"]
    if method == "filtration" or method == "settling":
        # only undissolved grains stay on the paper or sink; a dissolved solute passes / never settles
        return not sol["dissolved"]
    if method == "distillation":
        # the volatile liquid boils off and condenses; a non-volatile solute stays behind
        return liq["volatile"] and not sol["volatile"]
    # extraction moves the solute into another solvent; chromatography separates small samples on a
    # plate for analysis. Neither collects the original liquid as a product.
    return False


def sep_method_seawater(item: dict) -> list[bool]:
    """q-method: the most direct way to get drinking water from seawater.
    Options: filtration; distillation; extraction; chromatography; settling."""
    methods = ["filtration", "distillation", "extraction", "chromatography", "settling"]
    return [_gives_pure_liquid(m, SEAWATER) for m in methods]


# Composition table (standard 國中/高中 classification facts; brass is the copper–zinc alloy named in
# the option).
COMPOSITION = {
    "dry ice": ["CO2"],
    "salt water": ["H2O", "NaCl"],
    "brass": ["Cu", "Zn"],
    "oxygen gas": ["O2"],
    "air": ["N2", "O2", "Ar", "CO2", "H2O"],
}


def sep_pure_substances(item: dict) -> list[bool]:
    """q1: which are pure substances? Pure ⇔ exactly one substance in the composition table.
    Options: dry ice; salt water; brass; oxygen gas; air."""
    order = ["dry ice", "salt water", "brass", "oxygen gas", "air"]
    return [len(COMPOSITION[s]) == 1 for s in order]


def sep_water_diagram(item: dict) -> list[bool]:
    """q2: statements about water's phase diagram (triple point 0.01 °C, 0.006 atm; solid–liquid line
    tilted left; liquid–gas line rising to the right, i.e. the boiling point rises with pressure)."""
    claimed_bp_1atm = 100  # the value option (1) claims, compared with the data table
    s1 = WATER["bp_1atm"] == claimed_bp_1atm and _isobar_states(WATER, Rational(1)) == ["solid", "liquid", "gas"]
    s2 = "solid+liquid+gas" in _isobar_states(WATER, WATER["tp_P"])
    s3 = _isobar_states(WATER, WATER["tp_P"] / 2)[1] == "liquid"
    s4 = _boiling_point_rises_with_pressure(WATER)  # so lower pressure → lower boiling point
    # (5) ice just below 0 °C: if the melting point falls as pressure rises, enough pressure melts it
    s5 = not _melting_point_falls_with_pressure(WATER)
    return [s1, s2, s3, s4, s5]


def sep_low_pressure_plateaus(item: dict) -> int:
    """q3: ice at −20 °C heated at a fixed 0.5 atm until it has all become vapour.
    0.5 atm lies between the triple-point pressure (0.006 atm) and 1 atm. Start: with the solid–liquid
    line tilted left, the melting point at 0.5 atm is at least the 1 atm value (0 °C), so −20 °C is ice.
    End: the stem says all vapour. Count the lines crossed along the level line."""
    p = Rational(1, 2)
    assert WATER["tp_P"] < p < 1
    assert _melting_point_falls_with_pressure(WATER)  # so mp(0.5 atm) >= mp(1 atm)
    assert Rational(-20) < WATER["mp_1atm"]
    states = _isobar_states(WATER, p)
    assert states[0] == "solid" and states[-1] == "gas"
    return _plateaus(WATER, p)


def sep_gas_heated(item: dict) -> list[bool]:
    """q4: sealed rigid cylinder heated → pressure rises. Collision model: at a fixed volume, pressure
    grows with hits per second, i.e. with the number of molecules N and with molecular speed; nothing
    else (molecular size, attraction) is a factor in this 必修 picture.
    Each option names a mechanism and a direction; it is the explanation exactly when the mechanism is
    a factor of the model AND it changes that way in this situation AND that direction raises pressure.
    Options: molecules grow; faster, more and harder hits; more molecules; stronger attraction;
    molecules stop moving."""
    state = {"sealed": True, "rigid": True, "heated": True}
    change = {
        "N": 0 if state["sealed"] else None,  # sealed: no molecules enter or leave
        "V": 0 if state["rigid"] else None,  # rigid: the volume can't change
        "speed": +1 if state["heated"] else 0,  # heating makes the molecules move faster
    }
    assert change["V"] == 0
    factors = {"N", "speed"}  # what raises pressure in the collision model at fixed volume
    options = [
        ("size", +1),  # molecules get bigger
        ("speed", +1),  # molecules move faster
        ("N", +1),  # more molecules
        ("attraction", +1),  # stronger attraction
        ("speed", -1),  # molecules stop: speed falls
    ]
    return [m in factors and change[m] == d and d > 0 for m, d in options]


# Property tables for q5 (as the chapter states them: iodine dissolves only a little in water and
# well in hexane; water and hexane don't mix). Solubility as a rank: higher = dissolves more.
IODINE_SOLUBILITY_RANK = {"water": 0, "hexane": 1}
MISCIBLE = {frozenset({"water", "hexane"}): False}


def _extraction_works(new: str, original: str) -> bool:
    """Conditions 1–2 for an extraction solvent: it dissolves the solute better than the original
    solvent does, and it doesn't mix with the original solvent (so two layers form)."""
    better = IODINE_SOLUBILITY_RANK[new] > IODINE_SOLUBILITY_RANK[original]
    return better and not MISCIBLE[frozenset({new, original})]


def sep_methods_check(item: dict) -> list[bool]:
    """q5: which procedures work?
    (1) distil ink for water: water volatile, pigment not.
    (2) filter salt out of salt water: salt dissolved → passes the paper.
    (3) extract iodine from iodine water with hexane;
    (4) use water to extract the iodine out of a solution of iodine in hexane.
    (5) chromatography shows how many pigments ink has: pigments are held to different extents."""
    ink = {"liquid": {"name": "water", "volatile": True}, "solute": {"name": "pigment", "dissolved": True, "volatile": False}}
    saltwater = {"liquid": {"name": "water", "volatile": True}, "solute": {"name": "salt", "dissolved": True, "volatile": False}}
    pigments_differ_in_adsorption = True  # the TLC / paper-chromatography demo of the 課綱
    return [
        _gives_pure_liquid("distillation", ink),
        _gives_pure_liquid("filtration", saltwater),
        _extraction_works("hexane", "water"),
        _extraction_works("water", "hexane"),
        pigments_differ_in_adsorption,
    ]


def sep_rf_distance(item: dict) -> int:
    """q6: spot distance = Rf × solvent-front distance = 0.35 × 80 mm."""
    d = Rational("0.35") * 80
    assert d.is_integer
    return int(d)


# q7 data: solubility of the compounds involved (CaCO3 is the precipitate / scale the chapter names;
# Na2CO3 is added as a dissolved salt) and ion charges.
INSOLUBLE = {"CaCO3": True, "Na2CO3": False}
CHARGE = {"Ca": 2, "Na": 1}


def sep_hard_water_method(item: dict) -> list[bool]:
    """q7: which method CANNOT remove dissolved Ca²⁺? Each method is a rule on the dissolved,
    non-volatile ion:
    - add Na2CO3, then filter: removes it if the product CaCO3 is insoluble (a solid the paper holds);
    - ion-exchange resin carrying Na⁺: removes it if a whole number of Na⁺ balances one Ca²⁺'s charge;
    - plain filtration: the paper holds only undissolved solids;
    - distillation: only volatile parts reach the distillate.
    Options: Na2CO3 then filter; ion-exchange resin; filter directly; distil and collect."""
    ion = {"dissolved": True, "volatile": False}
    na_per_ca = Rational(CHARGE["Ca"], CHARGE["Na"])
    removes = [
        INSOLUBLE["CaCO3"] and not INSOLUBLE["Na2CO3"],
        na_per_ca.is_integer and na_per_ca * CHARGE["Na"] == CHARGE["Ca"],
        not ion["dissolved"],
        not ion["volatile"],
    ]
    return [not r for r in removes]
