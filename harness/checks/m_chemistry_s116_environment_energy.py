"""Checks for src/data/items/chemistry/s116-environment-energy.yaml (116 sprint: CMe-Ⅴc-1 to CMe-Ⅴc-4,
CNa-Ⅴc-1 to CNa-Ⅴc-4, CNc-Ⅴc-1; pollution, sustainability and energy).

Every check recomputes its item's key from the chemistry in the stem, never from item["answer"]:
- equations are balanced by solving the atom-count linear system (SymPy nullspace, smallest integers);
- masses use exact Rationals with the atomic masses each stem states;
- heats scale with the coefficients of the thermochemical equation the stem states (reversing flips ΔH);
- pH ratios are exact powers of ten;
- qualitative rules (which gas forms which acid, which reagent precipitates Cu2+, which process moves carbon
  where, which problem has which cause and remedy) are small tables of standard 必修 chemistry, the same
  facts the chapter teaches, and every option is decided by looking it up in them.
"""

from __future__ import annotations

import re

from sympy import Integer, Matrix, Rational, ilcm, log, sqrt

# ----------------------------------------------------------------------------------------- helpers

ATOMIC_MASS = {"H": 1, "C": 12, "O": 16, "Na": 23, "S": 32, "Ca": 40}  # as the stems state


def atoms(formula: str) -> dict[str, int]:
    """Element counts of a formula such as 'Ca(OH)2' or 'CaSO4' (no charges, no hydrates)."""

    def parse(s: str, i: int = 0) -> tuple[dict[str, int], int]:
        out: dict[str, int] = {}
        while i < len(s) and s[i] != ")":
            if s[i] == "(":
                inner, i = parse(s, i + 1)
                i += 1  # skip ')'
                m = re.match(r"\d+", s[i:])
                k = int(m.group()) if m else 1
                i += len(m.group()) if m else 0
                for el, n in inner.items():
                    out[el] = out.get(el, 0) + n * k
                continue
            m = re.match(r"([A-Z][a-z]?)(\d*)", s[i:])
            assert m, f"cannot parse {s!r} at {i}"
            el, n = m.group(1), int(m.group(2) or 1)
            out[el] = out.get(el, 0) + n
            i += len(m.group())
        return out, i

    return parse(formula)[0]


def molar_mass(formula: str) -> Integer:
    return sum((Integer(ATOMIC_MASS[el]) * n for el, n in atoms(formula).items()), Integer(0))


def balance(reactants: list[str], products: list[str]) -> list[int]:
    """Smallest whole-number coefficients from atom conservation: one nullspace vector."""
    species = reactants + products
    elements = sorted({el for f in species for el in atoms(f)})
    rows = [[atoms(f).get(el, 0) * (1 if j < len(reactants) else -1) for j, f in enumerate(species)] for el in elements]
    ns = Matrix(rows).nullspace()
    assert len(ns) == 1, "equation is not uniquely balanceable"
    v = ns[0]
    v = v * ilcm(*[x.q for x in v])
    if v[0] < 0:
        v = -v
    assert all(x > 0 for x in v)
    return [int(x) for x in v]


def ph_of(h) -> Rational:
    return -log(h, 10)


KW = Integer(10) ** -14  # 25 ℃

# Acids formed when a gas dissolves in rain (standard 必修 chemistry, as the chapter teaches):
# SO2 → H2SO3, and after oxidation in air H2SO4; NO2 → HNO3; CO2 → H2CO3; CH4, N2, CFCs form no acid.
ACID_FROM_GAS = {
    "SO2": {"H2SO3", "H2SO4"},
    "NO2": {"HNO3"},
    "CO2": {"H2CO3"},
    "CH4": set(),
    "CFC": set(),
}
# Strength of those acids (acid–base chapter: strong acids ionise almost completely).
STRONG_ACIDS = {"H2SO4", "HNO3", "HCl"}
WEAK_ACIDS = {"H2CO3", "H2SO3", "CH3COOH"}

# ----------------------------------------------------------------------------------------- items


def ee_turn_rain_ph(item: dict) -> list[bool]:
    """q-turn: unpolluted rain dissolves CO2 → H2CO3 (weak acid), so [H+] > [OH-] but only slightly.
    pH from CO2 in equilibrium with air at 25 ℃: [CO2(aq)] = K_H·p, [H+] = sqrt(Ka1·K_H·p + KW).
    Standard general-chemistry data (not taught in the chapter): K_H = 3.4 × 10^-2 M/atm,
    p(CO2) = 4.2 × 10^-4 atm, Ka1 = 4.5 × 10^-7. Gives pH ≈ 5.6, the chapter's clean-rain value.
    Options: equal to 7; about 5.6, slightly acidic; about 8, slightly basic; about 2, strongly acidic."""
    kh, p, ka1 = Rational(34, 1000), Rational(42, 100000), Rational(45, 10**8)
    h = sqrt(ka1 * kh * p + KW)
    ph = ph_of(h).evalf(30)
    acidic = h > KW / h
    return [
        abs(ph - 7) < Rational(1, 20),
        acidic and Rational(54, 10) < ph < Rational(58, 10),
        not acidic and Rational(75, 10) < ph < Rational(85, 10),
        acidic and Rational(15, 10) < ph < Rational(25, 10),
    ]


# Sign of ΔH by reaction class (reaction-energy chapter: every combustion is exothermic, ΔH < 0).
DH_SIGN_BY_CLASS = {"combustion": -1}


def ee_mid_biofuel(item: dict) -> list[bool]:
    """q-mid: ethanol from fermented sugarcane. Carbon bookkeeping over one cycle:
    photosynthesis takes n C out of the air, burning C2H5OH returns the same n C → net change 0.
    Options: (1) ethanol burning makes no CO2; (2) its carbon was recently taken from the air, burning
    returns it; (3) ethanol burning absorbs heat; (4) ethanol contains no carbon."""
    c_in_ethanol = atoms("C2H6O")["C"]  # C2H5OH
    absorbed_from_air = c_in_ethanol      # photosynthesis fixed these C atoms from atmospheric CO2
    returned_by_burning = c_in_ethanol    # C2H5OH + 3O2 → 2CO2 + 3H2O: every C leaves as CO2
    reactants, products = ["C2H6O", "O2"], ["CO2", "H2O"]
    coeffs = balance(reactants, products)
    assert coeffs == [1, 3, 2, 3]
    # A reaction of a carbon compound with O2 giving only CO2 and H2O is a combustion; the sign of ΔH by
    # reaction class comes from the rule table below (reaction-energy chapter: burning releases heat).
    is_combustion = "O2" in reactants and "C" in atoms(reactants[0]) and set(products) <= {"CO2", "H2O"}
    reaction_class = "combustion" if is_combustion else "other"
    dh_sign = DH_SIGN_BY_CLASS[reaction_class]
    return [
        coeffs[2] == 0,
        returned_by_burning - absorbed_from_air == 0 and absorbed_from_air > 0,
        dh_sign > 0,
        c_in_ethanol == 0,
    ]


def ee_rain_ratio(item: dict) -> Integer:
    """q1: pH 5.0 → 3.0; [H+] ratio = 10^-3 / 10^-5 = 100."""
    r = Integer(10) ** -3 / Integer(10) ** -5
    assert ph_of(Integer(10) ** -5) == 5 and ph_of(Integer(10) ** -3) == 3
    return Integer(r)


def ee_acid_rain_gases(item: dict) -> list[bool]:
    """q2: which emitted gases are main causes of acid rain (pH below 5.6)? A gas qualifies when it forms
    a strong acid in rain; CO2 forms only the weak H2CO3, which brings rain down to about 5.6 and no lower.
    Options: SO2, NO2, CO2, CH4, CFCs."""
    gases = ["SO2", "NO2", "CO2", "CH4", "CFC"]
    return [bool(ACID_FROM_GAS[g] & STRONG_ACIDS) for g in gases]


# Main causes and remedies (standard 必修 chemistry; the chapter's sections).
CAUSES = {
    "acid rain": {"SO2", "NOx"},
    "global warming": {"CO2", "CH4"},
    "ozone hole": {"CFC"},
}
REMEDIES = {
    "acid rain": {"flue-gas desulfurisation", "catalytic converter", "low-sulfur fuel"},
    "global warming": {"burn less fossil fuel", "plant forests"},
    "ozone hole": {"stop using CFCs"},
}


def ee_problem_match(item: dict) -> list[bool]:
    """q3: an option is right when its cause is a main cause of that problem AND its remedy fixes it.
    Options: acid rain–SO2–desulfurisation; global warming–CO2–less fossil fuel;
    ozone hole–CO2–less fossil fuel; ozone hole–CFCs–stop CFCs; acid rain–CFCs–stop CFCs."""
    options = [
        ("acid rain", "SO2", "flue-gas desulfurisation"),
        ("global warming", "CO2", "burn less fossil fuel"),
        ("ozone hole", "CO2", "burn less fossil fuel"),
        ("ozone hole", "CFC", "stop using CFCs"),
        ("acid rain", "CFC", "stop using CFCs"),
    ]
    return [c in CAUSES[p] and r in REMEDIES[p] for p, c, r in options]


def ee_desulfurisation_mass(item: dict) -> list[bool]:
    """q4: CaCO3 + SO2 + O2 → CaSO4 + CO2, balanced from atom counts (2, 2, 1 → 2, 2).
    3.2 kg SO2 = 3200/64 = 50 mol → 50 mol CO2 × 44 g/mol = 2200 g = 2.2 kg CO2 given off.
    Options (kg): 1.1, 2.2, 3.2, 4.4, 5.0."""
    c = balance(["CaCO3", "SO2", "O2"], ["CaSO4", "CO2"])
    n_so2 = Integer(3200) / molar_mass("SO2")
    n_co2 = n_so2 * Rational(c[4], c[1])
    kg = n_co2 * molar_mass("CO2") / 1000
    return [kg == Rational(x) for x in ("1.1", "2.2", "3.2", "4.4", "5.0")]


def ee_methane_co2_mass(item: dict) -> Integer:
    """q5: CH4 + 2O2 → CO2 + 2H2O, ΔH = −890 kJ (per 1 mol CH4, 1 mol CO2).
    4450 kJ released → 4450/890 = 5 mol CO2 × 44 g/mol = 220 g."""
    c = balance(["CH4", "O2"], ["CO2", "H2O"])
    assert c == [1, 2, 1, 2]
    heat_per_equation = Integer(890)
    n_co2 = Integer(4450) / heat_per_equation * c[2]
    g = n_co2 * molar_mass("CO2")
    assert g.is_integer
    return Integer(g)


# Solubility in water of the compounds the stem can form (standard 必修 chemistry):
# Cu(OH)2 is insoluble; CuCl2, CuSO4, NaCl, Na2SO4 are soluble. Sucrose is a nonelectrolyte (forms no ions).
INSOLUBLE = {"Cu(OH)2"}
ANION_OF_REAGENT = {"NaOH": "OH", "NaCl": "Cl", "sucrose": None, None: None}


def ee_heavy_metal_removal(item: dict) -> list[bool]:
    """q6: removing dissolved Cu2+ from wastewater. Filter paper keeps only solids; dissolved ions pass.
    Cu2+ becomes a solid only if the added reagent supplies an anion that forms an insoluble compound.
    Options: filter directly; add NaOH(aq) then filter; add NaCl(aq) then filter; add sucrose then filter."""
    def removed(reagent):
        anion = ANION_OF_REAGENT[reagent]
        if anion is None:
            return False  # nothing to precipitate Cu2+, so it stays dissolved and passes the filter
        product = f"Cu({anion})2"
        return product in INSOLUBLE
    return [removed(r) for r in (None, "NaOH", "NaCl", "sucrose")]


# Carbon flows (from, to) in the carbon cycle (the chapter's figure).
CARBON_FLOW = {
    "photosynthesis": ("air", "organisms"),
    "respiration": ("organisms", "air"),
    "burning fossil fuels": ("fossil fuels", "air"),
    "ocean dissolving CO2": ("air", "ocean"),
    "burning cleared forests": ("organisms", "air"),
}


def ee_carbon_sinks(item: dict) -> list[bool]:
    """q7: which processes take carbon OUT of the atmosphere? Options: photosynthesis; respiration;
    burning fossil fuels; seawater dissolving CO2; clearing and burning forests."""
    order = ["photosynthesis", "respiration", "burning fossil fuels", "ocean dissolving CO2", "burning cleared forests"]
    return [CARBON_FLOW[p][0] == "air" for p in order]


def ee_hydrogen_energy(item: dict) -> list[bool]:
    """q8: 2H2O(l) → 2H2(g) + O2(g), ΔH = +572 kJ (reverse of burning hydrogen, ΔH = −572 kJ).
    10 g H2 (H = 1) = 5 mol; heat = 572 × 5/2 = 1430 kJ absorbed. Options (kJ): 286, 572, 1430, 2860, 715."""
    c = balance(["H2O"], ["H2", "O2"])
    assert c == [2, 2, 1]
    dh_burn = Integer(-572)          # 2H2 + O2 → 2H2O
    dh_split = -dh_burn              # reversed equation flips the sign
    n_h2 = Integer(10) / molar_mass("H2")
    q = dh_split * n_h2 / c[1]
    return [q == x for x in (286, 572, 1430, 2860, 715)]
