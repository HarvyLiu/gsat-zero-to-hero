"""Checks for src/data/items/inquiry/s116-sci-exam-toolkit.yaml (116 sprint, 自然 exam toolkit).

The chapter practises three exam-tested tools that are outside the 必修 text; each is taught in a reviewed
subject chapter, which is the source of the rule encoded here:
- Dimension checks (nat:PEa-Va-1, elective; 112 Q37-40 framed with 因次分析, slice extras result[2]
  corrections): the three rules of physics/s116-physics-reasoning ("因次檢查只用三條規則": only like
  dimensions add or compare; units multiply and cancel like symbols; both sides of an equation have the
  same dimensions). Chemistry units (mol, L, g, min) are treated as symbols, as in
  chemistry/s116-rate-and-technology (g/min, mol/min) and chemistry/s116-solutions (mol/L). Hz = s^-1
  (physics/s116-physics-reasoning unit table).
- Ionic equations (nat:CJa-Vc-2 key concept "atom plus charge balance for ionic equations"; nat:CJc-Vc-1):
  atoms of each element and total charge are conserved, smallest whole-number coefficients
  (chemistry/s116-equations-stoichiometry, chemistry/s116-redox, chemistry/s116-chem-written-items).
- Lenz's law (nat:PKc-Vc-3 key concept; 113 Q46(b), 115 Q53(a) scoring guides): the induced current's
  field opposes the CHANGE in the original field; field lines leave an N pole and enter an S pole; right-
  hand grip rule: thumb along the induced field, fingers give the current (physics/s116-induction). Only
  the relative motion matters (moving the coil or the magnet), and a change in a neighbouring coil's or
  electromagnet's current also changes the field (physics/s116-induction, 法拉第電磁感應 section).

Each function recomputes from the stem (both locales, asserted to agree) and never reads item["answer"].
"""

from __future__ import annotations

import re
from fractions import Fraction

import sympy as sp

# --- shared ------------------------------------------------------------------------------------------


def _zh(item: dict) -> str:
    return item["text"]["zh-tw"]["stem"]


def _en(item: dict) -> str:
    return item["text"]["en"]["stem"]


def _opts(item: dict) -> list[str]:
    zh, en = item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]
    assert len(zh) == len(en), (zh, en)
    return zh


# --- dimension checks ----------------------------------------------------------------------------------

# Derived units written in the stems, as powers of the symbols the chapter cancels.
DERIVED = {"Hz": {"s": Fraction(-1)}}
SYM_RE = r"\\Delta\s*[A-Za-z]|\\lambda|[A-Za-z]"


def _unit(text: str) -> dict[str, Fraction]:
    """'mol/(L·min)', 'km/s', 'g/mol', 'Hz', 'L' -> {base: exponent}."""
    text = text.strip()
    num, _, den = text.partition("/")
    out: dict[str, Fraction] = {}

    def add(part: str, sign: int) -> None:
        part = part.strip().strip("()")
        for tok in filter(None, (t.strip() for t in part.split("·"))):
            m = re.fullmatch(r"([A-Za-z]+)(?:\^(-?\d+))?", tok)
            assert m, tok
            base, p = m.group(1), Fraction(int(m.group(2) or 1))
            for b, e in DERIVED.get(base, {base: Fraction(1)}).items():
                out[b] = out.get(b, Fraction(0)) + sign * e * p

    add(num, 1)
    if den:
        add(den, -1)
    return {k: v for k, v in out.items() if v != 0}


def _key(sym: str) -> str:
    return re.sub(r"\s+", "", sym)


def _symbol_units(item: dict) -> dict[str, dict[str, Fraction]]:
    """Every '$X$（單位u）' in the zh stem and '$X$ (in u)' in the en stem; both must agree."""
    zh = {_key(s): _unit(u) for s, u in re.findall(r"\$(" + SYM_RE + r")\$（單位([^）]+)）", _zh(item))}
    en = {_key(s): _unit(u) for s, u in re.findall(r"\$(" + SYM_RE + r")\$ \(in ([^()]+(?:\([^)]*\))?)\)", _en(item))}
    assert zh == en and len(zh) >= 3, (zh, en)
    return zh


def _side_units(tex: str, units: dict) -> dict[str, Fraction]:
    """Units of a product/quotient of the stem's symbols: 'CVM', '\\dfrac{V\\,\\Delta n}{\\Delta t}', 'v^2'."""

    def prod(s: str) -> dict[str, Fraction]:
        out: dict[str, Fraction] = {}
        s = s.replace("\\,", " ")
        for sym, p in re.findall(r"(" + SYM_RE + r")(?:\^\{?(\d+)\}?)?", s):
            for b, e in units[_key(sym)].items():
                out[b] = out.get(b, Fraction(0)) + e * int(p or 1)
        return out

    m = re.fullmatch(r"\\dfrac\{(.*)\}\{(.*)\}", tex.strip())
    if m:
        top, bot = prod(m.group(1)), prod(m.group(2))
        for b, e in bot.items():
            top[b] = top.get(b, Fraction(0)) - e
        return {k: v for k, v in top.items() if v != 0}
    return {k: v for k, v in prod(tex).items() if v != 0}


def tk_dimension_options(item: dict) -> list[bool]:
    """q-turn, q1, q2: each option 'lhs=rhs'; true when rhs has the units the stem gives the lhs."""
    units = _symbol_units(item)
    out = []
    for o in _opts(item):
        assert o == item["text"]["en"]["options"][_opts(item).index(o)]  # identical TeX in both locales
        lhs, rhs = o.strip("$").split("=", 1)
        assert _key(lhs) in units, lhs
        out.append(_side_units(rhs, units) == units[_key(lhs)])
    return out


# --- ionic equations -----------------------------------------------------------------------------------


def _species(term: str) -> tuple[int, dict[str, int], int]:
    """'2Fe^3+' -> (2, {'Fe': 1}, 3); 'H2O' -> (1, {'H': 2, 'O': 1}, 0); '2Cl-' -> (2, {'Cl': 1}, -1)."""
    m = re.fullmatch(r"(\d*)([A-Za-z0-9]+?)(?:\^?(\d*)([+-]))?", term.strip())
    assert m, term
    coef = int(m.group(1) or 1)
    formula, mag, sign = m.group(2), m.group(3), m.group(4)
    charge = 0 if not sign else (int(mag or 1) * (1 if sign == "+" else -1))
    atoms: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        atoms[el] = atoms.get(el, 0) + int(n or 1)
    assert "".join(f"{el}{n}" for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula)) == formula, formula
    return coef, atoms, charge


def _equation(ce: str):
    left, right = ce.split("->")
    side = lambda s: [_species(t) for t in s.split(" + ")]
    return side(left), side(right)


def balanced(ce: str) -> bool:
    """Atoms of every element AND total charge equal on the two sides."""
    left, right = _equation(ce)

    def tally(side):
        atoms: dict[str, int] = {}
        q = 0
        for c, a, z in side:
            for el, n in a.items():
                atoms[el] = atoms.get(el, 0) + c * n
            q += c * z
        return atoms, q

    return tally(left) == tally(right)


def balance(ce: str) -> list[int]:
    """Smallest whole-number coefficients for a skeleton (coefficients written in it are ignored)."""
    left, right = _equation(ce)
    sp_ = [(a, z, 1) for _, a, z in left] + [(a, z, -1) for _, a, z in right]
    elements = sorted({el for a, _, _ in sp_ for el in a})
    rows = [[s * a.get(el, 0) for a, _, s in sp_] for el in elements] + [[s * z for _, z, s in sp_]]
    null = sp.Matrix(rows).nullspace()
    assert len(null) == 1, "the skeleton must have exactly one balanced form"
    v = null[0]
    v = v * sp.ilcm(*[sp.fraction(x)[1] for x in v])
    g = sp.igcd(*[int(x) for x in v])
    v = [int(x) // g for x in v]
    if v[0] < 0:
        v = [-x for x in v]
    assert all(x > 0 for x in v)
    return v


def _ce(s: str) -> str:
    m = re.search(r"\\ce\{([^}]*)\}", s)
    assert m, s
    return m.group(1)


def tk_balanced_options(item: dict) -> list[bool]:
    """q4: which equations already conserve both atoms and charge?"""
    opts = _opts(item)
    assert opts == item["text"]["en"]["options"]
    # each option is two \ce groups (reactants, then "-> products"); join them back into one equation
    return [balanced(" ".join(re.findall(r"\\ce\{([^}]*)\}", o))) for o in opts]


def tk_fill_coefficient(item: dict) -> int:
    """q3: balance the stem's skeleton and return the coefficient of the species the stem asks about."""
    zh, en = _zh(item), _en(item)
    sk_zh, sk_en = _ce(zh), _ce(en)
    assert sk_zh == sk_en
    asked_zh = re.search(r"時，\$\\ce\{([^}]*)\}\$ 的係數是 ①", zh).group(1)
    asked_en = re.search(r"the coefficient of \$\\ce\{([^}]*)\}\$ is ①", en).group(1)
    assert asked_zh == asked_en
    terms = [t.strip() for side in sk_zh.split("->") for t in side.split(" + ")]
    coeffs = balance(sk_zh)
    return coeffs[terms.index(asked_zh)]


# --- Lenz's law ----------------------------------------------------------------------------------------
# One axis through the magnet and the coil's centre. 'side' is where the magnet is (+1: above / right,
# -1: below / left); 'viewer' is where the observer looks from, on the same axis.


def lenz_field(b_orig: int, strengthening: bool, viewer: int) -> str:
    """Direction seen by the viewer from the original field at the coil (+1 / -1 along the axis) and whether
    it is getting stronger. Lenz: the induced field opposes the CHANGE (reversed if strengthening, same way
    if weakening). Right-hand grip: thumb along the induced field; thumb towards the viewer = anticlockwise."""
    b_ind = -b_orig if strengthening else b_orig
    return "ccw" if b_ind == viewer else "cw"


def lenz(side: int, pole_facing: str, approaching: bool, viewer: int) -> str:
    """Magnet and coil on one axis; 'side' is where the magnet is relative to the coil (+1 above/right).
    Field lines leave an N pole and enter an S pole: at the coil, the magnet's field points AWAY from the
    magnet when the N pole faces the coil, TOWARDS it when the S pole does. Getting closer (whichever of the
    two moves) strengthens that field; moving apart weakens it."""
    b_orig = -side if pole_facing == "N" else side
    return lenz_field(b_orig, approaching, viewer)


ZH_DIR = {"cw": "順時針", "ccw": "逆時針"}
EN_DIR = {"cw": "Clockwise", "ccw": "Anticlockwise"}

# Where the magnet is relative to the coil, from the stem's wording (zh, en, side).
MAGNET_SIDE = [
    ("線圈正上方吊著一塊磁鐵", "a magnet hangs directly above it", +1),
    ("線圈拿在磁鐵正上方", "coil is held directly above the magnet", -1),
]


def _lenz_design(item: dict) -> tuple[int, bool, int]:
    """(original field at the coil, strengthening?, viewer), read from both stems, which must agree."""
    zh, en = _zh(item), _en(item).replace("''", "'")
    view_zh = +1 if "從上方" in zh else 0
    view_en = +1 if "from above" in en else 0
    if "電磁鐵" in zh:
        # an electromagnet whose field at the coil is stated; switching it on makes the field grow from 0
        bz = +1 if "在線圈處的磁場向上" in zh else -1 if "在線圈處的磁場向下" in zh else 0
        be = +1 if "its field at the coil points up" in en else -1 if "its field at the coil points down" in en else 0
        sz = "開關接通" in zh and "切斷的瞬間" not in zh
        se = "switch is turned on" in en and "turned off" not in en
        assert "electromagnet" in en
        design_zh, design_en = (bz, sz, view_zh), (be, se, view_en)
    else:
        sides = [(s, kz, ke) for kz, ke, s in MAGNET_SIDE if kz in zh]
        assert len(sides) == 1 and sides[0][2] in en, (sides, en)
        side = sides[0][0]
        # the pole named in the stem points along the axis: towards the coil if it points down from above
        # or up from below
        def facing(text, n_down, n_up, s_down, s_up):
            if (side == +1 and n_down in text) or (side == -1 and n_up in text):
                return "N"
            assert (side == +1 and s_down in text) or (side == -1 and s_up in text), text
            return "S"
        pz = facing(zh, "N極朝下", "N極朝上", "S極朝下", "S極朝上")
        pe = facing(en, "N pole down", "N pole up", "S pole down", "S pole up")
        az = "靠近" in zh and "遠離" not in zh
        ae = "towards the" in en and "away" not in en
        b_orig = -side if pz == "N" else side
        design_zh = (b_orig, az, view_zh)
        b_orig_e = -side if pe == "N" else side
        design_en = (b_orig_e, ae, view_en)
    assert design_zh == design_en and design_zh[0] != 0 and design_zh[2] != 0, (design_zh, design_en)
    return design_zh


def tk_lenz_options(item: dict) -> list[bool]:
    """q-lenz, q5: the one option naming the computed direction is true; the others are false (the motion
    keeps one direction, so the current neither vanishes nor reverses, and the design decides it)."""
    d = lenz_field(*_lenz_design(item))
    zh, en = _opts(item), item["text"]["en"]["options"]
    return [z == ZH_DIR[d] and e == EN_DIR[d] for z, e in zip(zh, en)]


def tk_mixed_lenz(item: dict) -> bool:
    """q7 (written): the model answer and the rubric's conclusion name the computed direction."""
    d = lenz_field(*_lenz_design(item))
    other = "ccw" if d == "cw" else "cw"
    mz, me = item["model"]["zh-tw"], item["model"]["en"]
    assert mz.rstrip("。").endswith(ZH_DIR[d]) and ZH_DIR[other] not in mz
    assert me.rstrip(".").endswith(EN_DIR[d].lower()) and EN_DIR[other].lower() not in me
    concl = next(c for c in item["rubric"]["criteria"] if c["id"] == "answer")
    assert ZH_DIR[d] in concl["text"]["zh-tw"] and EN_DIR[d].lower() in concl["text"]["en"]
    assert sum(c["points"] for c in item["rubric"]["criteria"]) == 4  # the stem says 4 points
    return True


# --- statements about the tools (q6) -------------------------------------------------------------------
# option index -> (keyword in the zh option, keyword in the en option, truth, source)
TOOL_RULES = [
    ("沒有單位的數字", "no unit", True,
     "physics/s116-physics-reasoning StudentAsks: dimension checks cannot catch unitless numbers"),
    ("電荷就一定守恆", "charge is always conserved", False,
     "chapter's own counterexample Cu + Ag+ -> Cu^2+ + Ag (atoms balance, charge +1 vs +2), checked below"),
    ("一定和原磁場方向相反", "always points opposite", False,
     "physics/s116-induction StudentAsks: Lenz opposes the change; a weakening field gives a parallel induced field"),
    ("因次不同的式子，一定是錯的", "different dimensions must be wrong", True,
     "physics/s116-physics-reasoning rule 3: both sides of an equation have the same dimensions"),
    ("磁場正在減弱", "getting weaker", True,
     "physics/s116-induction: a current is induced whenever the field through the coil changes"),
]


def tk_tool_statements(item: dict) -> list[bool]:
    zh, en = _opts(item), item["text"]["en"]["options"]
    assert len(zh) == len(TOOL_RULES)
    # rule 2's counterexample really conserves atoms but not charge
    left, right = _equation("Cu + Ag+ -> Cu^2+ + Ag")
    assert not balanced("Cu + Ag+ -> Cu^2+ + Ag")
    assert sum(z * c for c, _, z in left) != sum(z * c for c, _, z in right)
    # rule 3: a weakening field gives an induced field along the original (lenz with approaching=False)
    assert lenz(+1, "N", False, -1) != lenz(+1, "N", True, -1)
    out = []
    for (kz, ke, truth, _src), oz, oe in zip(TOOL_RULES, zh, en):
        assert kz in oz and ke in oe, (kz, oz, ke, oe)
        out.append(truth)
    return out
