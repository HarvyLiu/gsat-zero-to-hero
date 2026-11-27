"""Checks for the chemistry items of inquiry/s116-sci-mock (the original science practice paper):
Part 1 q10–q18 and the Part 2 chemistry set q44–q46.

Every check recomputes its item's key from the stem, never from item["answer"]. Chemistry facts and
rules come only from the reviewed chemistry sprint chapters, named in each source comment
(src/content/lessons/zh-tw/chemistry/<slug>.mdx). Numbers are exact SymPy Rationals with the atomic
masses each stem states.
"""

from __future__ import annotations

import re

from sympy import Integer, Rational, log, simplify

R = Rational


# ---------- shared helpers ----------

def parse(formula: str) -> dict[str, int]:
    """'NaHCO3' → {'Na': 1, 'H': 1, 'C': 1, 'O': 3}. Plain formulas without brackets."""
    counts: dict[str, int] = {}
    pos = 0
    for m in re.finditer(r"([A-Z][a-z]?)(\d*)", formula):
        if m.start() != pos:
            raise ValueError(f"cannot parse {formula!r}")
        pos = m.end()
        counts[m.group(1)] = counts.get(m.group(1), 0) + (int(m.group(2)) if m.group(2) else 1)
    if pos != len(formula):
        raise ValueError(f"cannot parse {formula!r}")
    return counts


def molar_mass(formula: str, aw: dict[str, Rational]) -> Rational:
    return sum((aw[el] * n for el, n in parse(formula).items()), Integer(0))


def atoms(side: list[tuple[int, str]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for k, f in side:
        for el, n in parse(f).items():
            out[el] = out.get(el, 0) + k * n
    return out


def balanced(left: list[tuple[int, str]], right: list[tuple[int, str]]) -> bool:
    return atoms(left) == atoms(right)


def one_true(values: list[bool]) -> list[bool]:
    if sum(bool(v) for v in values) != 1:
        raise ValueError(f"expected exactly one true option, got {values}")
    return values


# ---------- Part 1 ----------

def mc_separation_methods(item: dict) -> list[bool]:
    """q10: which mixture → method pairing works? Source: chemistry/s116-matter-and-separation, the
    table under 分離混合物：看性質選方法: each method needs one difference between the components:
      過濾 – one component is an insoluble particle; 蒸餾 – boiling point / volatility;
      萃取 – solubility in a second solvent that does not mix with the first;
      層析 – adsorption strength / solubility in the moving solvent.
    The stem gives, for each option, whether the needed difference is present."""
    need = {"filtration": "insoluble", "distillation": "volatility", "extraction": "solubility2",
            "chromatography": "adsorption"}
    options = [
        # (1) sugar water → filtration: the sugar is dissolved, nothing insoluble.
        ("filtration", {"insoluble": False, "volatility": True}),
        # (2) water with a dissolved non-volatile dye → distillation: water boils off, dye stays.
        ("distillation", {"volatility": True, "insoluble": False}),
        # (3) two liquids with the same boiling point → distillation: no volatility difference.
        ("distillation", {"volatility": False}),
        # (4) a solute equally soluble in water and in the oil → extraction: no solubility difference.
        ("extraction", {"solubility2": False}),
        # (5) two dyes adsorbed equally and equally soluble → chromatography: no difference.
        ("chromatography", {"adsorption": False}),
    ]
    return one_true([props.get(need[m], False) for m, props in options])


def mc_atom_z16_a34(item: dict) -> list[bool]:
    """q11: a neutral atom with Z = 16, A = 34. Source: chemistry/s116-atomic-structure:
    neutrons = A − Z; electrons = Z for a neutral atom; valence electrons for Z ≤ 18 = Z minus the
    nearest earlier noble gas (He 2, Ne 10), noble gases He 2 / Ne, Ar 8; same valence → similar
    chemistry; the metal / metalloid / non-metal table for Z = 1–18 (S is a non-metal)."""
    Z, A = 16, 34
    noble = [2, 10, 18]

    def valence(z: int) -> int:
        if z in noble:
            return 2 if z == 2 else 8
        prev = max([0] + [n for n in noble if n < z])
        return z - prev

    metals = {3, 4, 11, 12, 13}  # Li, Be, Na, Mg, Al (the chapter's table)
    neutrons, electrons = A - Z, Z
    return one_true([
        neutrons == 16,                   # (1) 16 neutrons
        electrons == 34,                  # (2) 34 electrons
        valence(Z) == 6,                  # (3) 6 valence electrons
        valence(Z) == valence(17),        # (4) most like chlorine (Z = 17)
        Z in metals,                      # (5) a metal
    ])


def mc_glucose_oxygen_atoms(item: dict) -> list[bool]:
    """q12: mass of glucose C6H12O6 with as many O atoms as 9.0 g of water (H 1, C 12, O 16).
    Source: chemistry/s116-formulas-and-mole (mass ÷ molar mass → moles; atoms per formula)."""
    aw = {"H": Integer(1), "C": Integer(12), "O": Integer(16)}
    mol_o = R(90, 10) / molar_mass("H2O", aw) * parse("H2O")["O"]
    glucose = mol_o / parse("C6H12O6")["O"] * molar_mass("C6H12O6", aw)
    options = [R(15, 2), Integer(15), Integer(30), Integer(90), Integer(540)]
    return one_true([glucose == o for o in options])


def mc_mixing_nacl(item: dict) -> list[bool]:
    """q13: 200 mL of 0.30 M + 300 mL of 0.10 M NaCl, volumes additive. Source: chemistry/s116-solutions
    (molarity = moles of solute ÷ litres of solution)."""
    mol = R(200, 1000) * R(30, 100) + R(300, 1000) * R(10, 100)
    conc = mol / (R(200, 1000) + R(300, 1000))
    options = [R(90, 1000), R(18, 100), R(20, 100), R(22, 100), R(40, 100)]
    return one_true([conc == o for o in options])


def mc_ethanol_heat(item: dict) -> list[bool]:
    """q14: C2H5OH(l) + 3O2(g) → 2CO2(g) + 3H2O(l), ΔH = −1367 kJ (given in the stem); burn 4.6 g
    (H 1, C 12, O 16). Source: chemistry/s116-reaction-energy (用反應熱計算：質量、莫耳、熱量)."""
    aw = {"H": Integer(1), "C": Integer(12), "O": Integer(16)}
    assert balanced([(1, "C2H6O"), (3, "O2")], [(2, "CO2"), (3, "H2O")])
    heat = R(46, 10) / molar_mass("C2H6O", aw) * 1367
    options = [R(6835, 100), R(1367, 10), R(2734, 10), Integer(1367), R(46, 10) * 1367]
    return one_true([heat == o for o in options])


def mc_alkane_14h(item: dict) -> list[bool]:
    """q15: an alkane molecule with 14 H atoms; its molecular weight (H 1, C 12). Source:
    chemistry/s116-organic-life: straight-chain alkanes are CnH2n+2 (from 4n bond ends minus 2(n − 1))."""
    h = 14
    n = R(h - 2, 2)
    assert n.q == 1 and 4 * n - 2 * (n - 1) == h
    mw = 12 * n + h
    options = [Integer(72), Integer(78), Integer(84), Integer(86), Integer(100)]
    return one_true([mw == o for o in options])


def mc_bond_statements(item: dict) -> list[bool]:
    """q16 (multi). Source: chemistry/s116-chemical-bonds: metal + non-metal → ionic (solid does not
    conduct; molten or in water it does); metals conduct because the valence electrons move freely
    (electron sea); SiO2 is a covalent network solid (atoms, no separate molecules, very high m.p.);
    Lewis structures: shared pairs = (electrons needed − valence total) ÷ 2, lone pairs are the rest."""
    metal = {"Mg"}
    nonmetal = {"Cl", "N", "H", "C", "O", "Si"}  # Si is a metalloid; it only matters that it is not a metal
    valence = {"H": 1, "C": 4, "N": 5, "O": 6, "Cl": 7, "Mg": 2, "Si": 4}
    network = {"SiO2"}

    def kind(formula: str) -> str:
        els = set(parse(formula))
        if formula in network:
            return "network"
        if els <= metal:
            return "metal"
        if els & metal and els - metal:
            return "ionic"
        return "molecular"

    def lewis(formula: str) -> tuple[int, int]:
        """(shared pairs, lone pairs) for the chapter's molecules; H needs 2 electrons, others 8."""
        c = parse(formula)
        have = sum(valence[e] * n for e, n in c.items())
        need = sum((2 if e == "H" else 8) * n for e, n in c.items())
        shared = (need - have) // 2
        return shared, (have - 2 * shared) // 2

    def central_lone_pairs(formula: str, central: str) -> int:
        """Central atom's valence electrons minus one per shared pair it takes part in, halved
        (all its bonds go to the outer atoms)."""
        shared, _ = lewis(formula)
        return (valence[central] - shared) // 2

    s1 = kind("MgCl2") == "ionic"           # solid does not conduct, molten conducts: the ionic row
    s2 = kind("SiO2") == "molecular"        # claim: high m.p. because made of separate small molecules
    s3 = central_lone_pairs("NH3", "N") == 1
    s4 = kind("Mg") == "metal"              # conducts because valence electrons move freely
    s5 = lewis("CO2")[1] == 2               # claim: CO2 has 2 lone pairs in all
    return [s1, s2, s3, s4, s5]


def mc_acid_statements(item: dict) -> list[bool]:
    """q17 (multi): 100 mL of 0.010 M HCl at 25 ℃. Source: chemistry/s116-acids-bases:
    HCl is a strong acid (fully ionised), acetic acid is weak (partly ionised, so fewer H+ at the same
    concentration); [H+][OH−] = 1.00×10^−14; pH = −log[H+]; at exact neutralisation mol H+ = mol OH−;
    Ba(OH)2 → Ba2+ + 2OH− (stated in the stem)."""
    h = R(1, 100)
    ph = simplify(-log(h, 10))
    oh = R(1, 10**14) / h
    vol = R(100, 1000)
    # (1) acetic acid of the same concentration also has pH 2: weak acid gives [H+] < 0.010 M.
    weak_acid_partly_ionised = True  # acids-bases, 強酸、弱酸與強弱電解質: acetic acid is weak
    s1 = not weak_acid_partly_ionised  # partly ionised → [H+] < 0.010 M → pH > 2, so the claim fails
    s2 = ph == 2
    # (3) 0.010 M Ba(OH)2 needed for exact neutralisation is 100 mL?
    v_base = h * vol / (2 * R(1, 100))
    s3 = v_base == R(100, 1000)
    s4 = oh == R(1, 10**12)
    # (5) diluted with water to 1000 mL: [H+] = 0.0010 M, pH 3
    h_dil = h * vol / R(1000, 1000)
    s5 = h_dil == R(1, 10**3)
    return [s1, s2, s3, s4, s5]


def mc_mg_co2_redox(item: dict) -> list[bool]:
    """q18 (multi): 2Mg + CO2 → 2MgO + C, with O as O2− in MgO. Source: chemistry/s116-redox:
    gaining oxygen = oxidised, losing oxygen = reduced (used for molecules such as CO2); the substance
    reduced is the oxidising agent, the one oxidised is the reducing agent; electrons counted on ions
    (charge of Mg in MgO: x + (−2) = 0)."""
    left, right = [(2, "Mg"), (1, "CO2")], [(2, "MgO"), (1, "C")]
    assert balanced(left, right)
    o_before = {"Mg": parse("Mg").get("O", 0), "CO2": parse("CO2")["O"]}
    o_after = {"Mg": parse("MgO")["O"], "CO2": parse("C").get("O", 0)}
    oxidised = {s for s in o_before if o_after[s] > o_before[s]}
    reduced = {s for s in o_before if o_after[s] < o_before[s]}
    oxidising_agent, reducing_agent = reduced, oxidised
    mg_charge = 0 - (-2)
    return [
        "Mg" in oxidised,            # (1) Mg is oxidised
        "Mg" in oxidising_agent,     # (2) Mg is the oxidising agent
        mg_charge - 0 == 2,          # (3) each Mg atom loses 2 electrons
        "CO2" in oxidised,           # (4) CO2 gains oxygen and is oxidised
        "CO2" in oxidising_agent,    # (5) CO2 is the oxidising agent
    ]


# ---------- Part 2: the antacid set q44–q46 ----------

AW_SET = {"H": Integer(1), "C": Integer(12), "O": Integer(16), "Na": Integer(23)}
# Illustrative data in the q44 stem: powder mass (g) → loss in balance reading (g).
DATA = [(R(50, 100), R(22, 100)), (R(100, 100), R(44, 100)), (R(150, 100), R(66, 100)), (R(200, 100), R(88, 100))]
REACT = ([(1, "NaHCO3"), (1, "HCl")], [(1, "NaCl"), (1, "H2O"), (1, "CO2")])


def mc_set_mass_loss(item: dict) -> list[bool]:
    """q44: why the reading falls in an open beaker. Source: chemistry/s116-laws-atomic-theory
    (拉瓦節: in a closed system the total mass does not change; an open container loses the mass of any
    gas that escapes; atoms are only rearranged); the stem says NaCl and the other ingredients stay
    in the beaker (dissolved) and the products are NaCl, H2O and the gas CO2."""
    left, right = REACT
    assert balanced(left, right)
    gases = {"CO2"}
    stays_in_beaker = {"NaCl", "H2O", "other ingredients"}
    open_container = True
    mass_conserved = True  # Lavoisier's law holds for every reaction, gas or not
    return one_true([
        not mass_conserved,                                    # (1) mass is destroyed
        "NaCl" not in stays_in_beaker,                         # (2) dissolved NaCl no longer counts
        "other ingredients" not in stays_in_beaker,            # (3) the dissolved inert part leaves
        open_container and any(f in gases for _, f in right),  # (4) the CO2 escapes into the air
        sum(atoms(left).values()) != sum(atoms(right).values()),  # (5) atom totals differ
    ])


def mc_set_statements(item: dict) -> list[bool]:
    """q45 (multi), from the q44 data, assuming the whole loss is CO2 and the acid is in excess.
    Sources: chemistry/s116-equations-stoichiometry (coefficients are mole ratios; mass ÷ M → mol);
    chemistry/s116-chemistry-and-society (碳酸氫鈉的水溶液只是弱鹼性)."""
    left, right = REACT
    assert balanced(left, right)
    ratios = {loss / m for m, loss in DATA}
    s1 = len(ratios) == 1                                     # loss ∝ powder mass
    k = {f: c for c, f in left + right}
    s2 = R(k["HCl"], k["CO2"]) == 2                           # mol HCl = 2 × mol CO2?
    per_gram = next(iter(ratios))
    s3 = per_gram * 1 / molar_mass("CO2", AW_SET) == R(1, 100)  # 1.00 g → 0.010 mol CO2
    s4 = per_gram * 3 == R(132, 100)                          # 3.00 g → 1.32 g
    nahco3_aq = "weakly basic"  # chemistry-and-society, 制酸劑 section
    s5 = nahco3_aq == "strongly basic"
    return [s1, s2, s3, s4, s5]


def mc_set_percent(item: dict) -> bool:
    """q46 (written): the model answer's chain holds for every data row: mol CO2 = loss ÷ 44;
    mol NaHCO3 = mol CO2 (1 : 1); mass NaHCO3 = mol × 84; percentage = 84 %.
    Sources: chemistry/s116-equations-stoichiometry, chemistry/s116-formulas-and-mole."""
    left, right = REACT
    k = {f: c for c, f in left + right}
    m_co2, m_nahco3 = molar_mass("CO2", AW_SET), molar_mass("NaHCO3", AW_SET)
    ok = m_co2 == 44 and m_nahco3 == 84 and k["NaHCO3"] == k["CO2"]
    for m, loss in DATA:
        mol = loss / m_co2 * R(k["NaHCO3"], k["CO2"])
        ok = ok and mol * m_nahco3 / m * 100 == 84
    row = DATA[1]
    ok = ok and row[1] / m_co2 == R(1, 100) and R(1, 100) * m_nahco3 == R(84, 100)
    return bool(ok)
