"""Checks for src/data/items/earth/s116-sustainability.yaml (116 sprint: ENa-Ⅴc-1, ENa-Ⅴc-2, ENa-Ⅴc-3
sustainable development and resource use).

How the keys are recomputed (never from item["answer"]):
- Stocks and rates: a stock S changes each year by (replenishment - use); years are found by stepping
  year by year with exact Rationals, or symbolically for every positive growth (sympy, positive
  symbols), never from one chosen number.
- "Years it lasts" = reserves / annual use under constant use; with growing use the first year in which
  cumulative use reaches the reserves is found by adding the stem's yearly amounts.
- The stem's numbers are read from the zh-tw stem and asserted to appear in the en stem too.
- Definition, impact and aspect items: fact tables with a source comment per fact.

Facts used, with their sources:
- Sustainable development = meeting present needs without harming future generations' ability to meet
  theirs; understanding the Earth supports economic, ecological, cultural and policy sustainability;
  resources are finite (energy-consumption and reserve statistics) and their use has environmental and
  ecological impacts (nat.json ENa-Ⅴc-1/2/3 keyConcepts; slice verification.final_units order 25).
- Burning coal releases CO2 and SO2; solar power burns no fuel while generating; SO2 -> acid rain
  (chemistry/s116-environment-energy, already reviewed; standard 國中 Na-Ⅳ content).
- Over-pumping groundwater -> falling water table -> land subsidence; mining changes the land surface and
  habitats; renewable-energy equipment uses mined materials: standard textbook facts, NOT in the
  sources; listed for the owner.
"""

from __future__ import annotations

import re

import sympy as sp
from sympy import Rational as Q


def _nums(text: str) -> list[Q]:
    return [Q(n) for n in re.findall(r"\d+(?:\.\d+)?", text)]


def _stem_numbers(item: dict, expected: list[int]) -> list[Q]:
    """The stem's numbers, in order, from the zh-tw stem; the en stem must carry the same ones."""
    zh = _nums(item["text"]["zh-tw"]["stem"])
    en = _nums(item["text"]["en"]["stem"])
    want = [Q(x) for x in expected]
    # the given numbers must be in both stems (guards against editing one language only)
    for w in want:
        assert w in zh and w in en, (w, zh, en)
    return want


# --- stocks, rates and years ---------------------------------------------------------------------------


def years_constant(reserves: Q, use: Q) -> Q:
    """Years a stock lasts at a constant use, no replenishment."""
    return Q(reserves) / Q(use)


def years_net(stock: Q, replenish: Q, use: Q):
    """Years until the stock is gone with constant replenishment and use; None if it never shrinks."""
    net = Q(use) - Q(replenish)
    if net <= 0:
        return None
    return Q(stock) / net


def run_out_year(reserves: Q, yearly_uses) -> int:
    """The first year n (1-based) in which cumulative use reaches or passes the reserves."""
    total = Q(0)
    for n, u in enumerate(yearly_uses, start=1):
        total += Q(u)
        if total >= reserves:
            return n
    raise AssertionError("does not run out within the listed years")


def excess_after_100_years():
    """Reserves R = 100 P (lasts 100 years at this year's use P). With use P + k g in year k+1 (g > 0),
    return cumulative use over 100 years minus R, symbolically in P, g > 0."""
    P, g = sp.symbols("P g", positive=True)
    R = 100 * P
    k = sp.symbols("k", integer=True, nonnegative=True)
    cumulative_100 = sp.summation(P + k * g, (k, 0, 99))
    return sp.simplify(cumulative_100 - R)  # = 4950 g


def growing_runs_out_sooner() -> bool:
    """Cumulative use passes R before 100 years are over, for every P, g > 0."""
    return bool(excess_after_100_years().is_positive)


def digits(n: Q, width: int) -> tuple[str, ...]:
    assert n.q == 1, n
    s = str(int(n))
    assert len(s) == width, (n, width)
    return tuple(s)


# --- items ---------------------------------------------------------------------------------------------


def su_turn_growing_use(item: dict) -> list[bool]:
    """q-turn: lasts exactly 100 years at this year's use; use grows each year."""
    d = excess_after_100_years()
    sooner, exactly, longer = bool(d.is_positive), bool(d.is_zero), bool(d.is_negative)
    # the sign of d holds for every P > 0 (reserves are 100 P): it does not depend on the reserve size
    depends_on_size = d.is_positive is None
    oil_replenished = False  # fossil fuels: replenishment almost zero on human timescales (ENa-Ⅴc-2)
    return [sooner, exactly, longer, depends_on_size, oil_replenished]


# Definition (nat.json ENa-Ⅴc-1/3 keyConcepts): present needs met, future ability not harmed, all four
# aspects considered.
DEF_OPTIONS = [
    {"present": True, "future": True, "all_aspects": True},  # (1) the definition
    {"present": False, "future": True, "all_aspects": True},  # (2) stop using everything
    {"present": True, "future": False, "all_aspects": True},  # (3) later generations fend for themselves
    {"present": True, "future": True, "all_aspects": False},  # (4) economic growth only
    {"present": True, "future": True, "all_aspects": False},  # (5) ecology only
]


def su_definition(item: dict) -> list[bool]:
    return [all(o.values()) for o in DEF_OPTIONS]


def _exact_stem_numbers(item: dict, expected: list[int]) -> list[Q]:
    """Like _stem_numbers, but the SET of numbers in each stem must be exactly the expected ones, so an
    edit to any stem number (in either language) breaks the check instead of passing on old data."""
    want = _stem_numbers(item, expected)
    zh = set(_nums(item["text"]["zh-tw"]["stem"]))
    en = set(_nums(item["text"]["en"]["stem"]))
    assert zh == en == set(want), (zh, en, want)
    return want


def su_iron_max_use(item: dict) -> tuple[str, ...]:
    """Largest constant annual use u with reserves / u >= the required years."""
    reserves, need = _exact_stem_numbers(item, [4800, 60])
    u = sp.symbols("u", positive=True)
    sol = sp.solve_univariate_inequality(reserves / u >= need, u, relational=False)
    u_max = sol.sup
    assert not bool(sol.right_open) and u_max == reserves / need, sol  # the bound itself is allowed
    assert years_constant(reserves, u_max) == need and years_constant(reserves, u_max + 1) < need
    return digits(Q(u_max), 2)


def su_gas_falling_left(item: dict) -> tuple[str, ...]:
    """Use falls by a fixed amount each year: what is left after n years (summed year by year)."""
    reserves, year_one, first, step, n = _exact_stem_numbers(item, [450, 1, 60, 4, 5])
    assert year_one == 1  # "第1年" / "year 1": the first year's use is the given 60
    uses = [first - step * k for k in range(int(n))]
    assert all(x > 0 for x in uses)
    left = reserves - sum(uses)
    assert left > 0
    # falling use lasts longer than the constant-use estimate: more is left than at a constant first-year use
    assert left > reserves - first * n
    return digits(left, 3)


# Impacts of extracting / using resources (sources in the module docstring).
IMPACTS = {
    "coal_co2_so2": True,  # chemistry/s116-environment-energy: coal burning releases CO2; sulfur -> SO2
    "groundwater_subsidence": True,  # standard (not in sources): over-pumping -> land subsidence
    "solar_burns_fuel": False,  # chemistry/s116-environment-energy: solar power burns nothing in use
    "mining_land_habitat": True,  # standard (not in sources): mining changes land surface and habitats
    "renewables_zero_impact": False,  # equipment uses mined materials and must be recycled (standard)
}


def su_impacts(item: dict) -> list[bool]:
    keys = ["coal_co2_so2", "groundwater_subsidence", "solar_burns_fuel", "mining_land_habitat", "renewables_zero_impact"]
    return [IMPACTS[k] for k in keys]


def su_fish_stock(item: dict) -> tuple[str, ...]:
    """A stock with constant natural increase; the catch changes after the first n1 years. Step year by year."""
    stock, grow, n1, catch1, catch2, n_end = _exact_stem_numbers(item, [800, 60, 5, 100, 40, 10])
    s = Q(stock)
    for year in range(1, int(n_end) + 1):
        s += grow - (catch1 if year <= n1 else catch2)
        assert s > 0
    # a catch no larger than the natural increase never shrinks the stock
    assert years_net(stock, grow, catch2) is None and years_net(stock, grow, catch1) is not None
    return digits(s, 3)


def su_first_to_run_out(item: dict) -> list[bool]:
    data = {"甲": (300, 20), "乙": (600, 50), "丙": (1000, 40)}
    _stem_numbers(item, [v for pair in data.values() for v in pair])
    years = {k: years_constant(Q(r), Q(u)) for k, (r, u) in data.items()}
    best = min(years.values())
    first = [k for k, y in years.items() if y == best]
    assert len(first) == 1
    smallest_reserve = min(data, key=lambda k: data[k][0])
    assert smallest_reserve != first[0]  # the trap: smallest reserves is not first to run out
    return [
        first == ["甲"],
        first == ["乙"],
        first == ["丙"],
        years["甲"] == years["丙"] and first == ["甲", "丙"],
        False,  # the data are enough: both numbers are given for each resource
    ]


# Aspect of each reservoir consideration (nat.json ENa-Ⅴc-3: economic, ecological, cultural, policy).
RESERVOIR_ASPECT = ["economic", "cultural", "ecological", "policy", "economic"]


def su_reservoir_aspect(item: dict) -> list[bool]:
    return [a == "ecological" for a in RESERVOIR_ASPECT]


def su_indicator_statements(item: dict) -> list[bool]:
    R, P = sp.symbols("R P", positive=True)
    ratio = R / P
    # (1) the ratio is reserves over ONE annual use: it assumes that use is the same every year
    o1 = True
    # (2) growing use runs out sooner (shown for every positive growth)
    o2 = growing_runs_out_sooner()
    # (3) a counterexample: longer-lasting resource with smaller reserves
    a, b = (Q(100), Q(2)), (Q(300), Q(30))
    o3 = not (years_constant(*a) > years_constant(*b) and a[0] < b[0])
    # (4) same reserves, larger use -> fewer years: d(ratio)/dP < 0 for all R, P > 0
    o4 = bool(sp.diff(ratio, P).is_negative)
    # (5) the ratio is an indicator: with growing use the actual year differs from R/P, so "sure to run
    # out after exactly 30 years" is false
    o5 = not growing_runs_out_sooner()
    return [o1, o2, o3, o4, o5]
