"""Checks for src/data/items/inquiry/s116x-one-context-four-subjects.yaml (116 sprint, cross-subject:
inq:discover/pose-question, inq:argue-model/explain-reason, inq:argue-model/conclude).

How the keys are recomputed (never from item["answer"]):
- Subject facts come from a facts table; each entry names the reviewed subject chapter it is taught in.
  Energy chains are walked link by link against that table, so a chain is accepted only if every link
  is a fact and the heat links run from hotter to colder.
- "Is this question testable?" and "is this a fair test of the rival explanation?" are decided by small
  encoded rule lists (source per rule: the inq.json key concepts of the chapter's codes).
- Data items recompute differences, averages and the turning point from the stem's table with exact
  Rationals; conclusions are judged by scope (one sample vs all), agreement with the data, and whether
  a claimed cause was actually tested.
"""

from __future__ import annotations

from sympy import Rational as R

# --- subject facts (each is taught in the named reviewed chapter) --------------------------------
# key -> (statement, source chapter)
FACTS = {
    "sun_fusion": ("the Sun's energy comes from nuclear fusion", "physics/s116-mass-energy-nuclear"),
    "photosynthesis_stores_light": (
        "photosynthesis stores light energy as chemical energy in organic matter (glucose etc.)",
        "biology/s116-cell-energy"),
    "wood_is_glucose_chains": ("cellulose is made of many glucose units", "chemistry/s116-organic-life"),
    "respiration_releases_heat": (
        "respiration breaks down organic matter; part of the energy goes to ATP, the rest is lost as heat;"
        " bacteria respire too", "biology/s116-cell-energy"),
    "heat_hot_to_cold": ("heat flows spontaneously from the hotter body to the colder one",
                         "physics/s116-heat-energy-quality"),
    "energy_degrades": ("energy is conserved but each conversion spreads it out (energy degradation)",
                        "physics/s116-heat-energy-quality"),
    "surface_area_rate": ("a solid reacts at its surface: smaller pieces, more contact area, faster reaction",
                          "chemistry/s116-rate-and-technology"),
    "co2_makes_water_acidic": ("CO2 + H2O <=> H2CO3, so dissolved CO2 makes rain (and sea water) acidic",
                               "chemistry/s116-environment-energy"),
    "carbon_cycle": ("photosynthesis fixes atmospheric CO2; respiration and burning return it",
                     "chemistry/s116-environment-energy"),
    "atoms_conserved": ("in a reaction atoms are rearranged, never created, destroyed or changed into"
                        " another element", "chemistry/s116-laws-atomic-theory"),
    "seasons_day_length": ("in the Northern Hemisphere summer days are long and winter days short",
                           "earth/s116-sky-motion"),
    "fossil_fuel_warming": ("burning fossil fuels adds CO2 and strengthens the greenhouse effect; human"
                            " activity is the main factor in recent warming", "earth/s116-climate-change"),
}

# Which subject's reviewed chapter answers each kind of question (from FACTS' source chapters).
SUBJECT_OF = {key: src.split("/")[0] for key, (_, src) in FACTS.items()}


# --- opening and mid-chapter turns ---------------------------------------------------------------

# The campfire's energy, traced backwards: each entry is (form of energy, where it came from, fact).
CAMPFIRE_BACKWARDS = [
    ("heat of the fire", "chemical energy of the wood", "wood_is_glucose_chains"),
    ("chemical energy of the wood", "light absorbed by the tree", "photosynthesis_stores_light"),
    ("light absorbed by the tree", "the Sun", "sun_fusion"),
    ("the Sun", "nuclear fusion", "sun_fusion"),
]


def ocfs_turn_energy_source(item: dict) -> list[bool]:
    """q-turn: how far back does the campfire's energy go? Walk the chain back to its root.
    Options: made by the wood itself, nothing to do with the Sun; the Sun (fusion -> light ->
    photosynthesis -> wood); the match or lighter; heat from inside the Earth; from nothing."""
    assert all(f in FACTS for *_, f in CAMPFIRE_BACKWARDS)
    # the chain must be connected: each 'came from' is the next entry's form
    assert all(a[1] == b[0] for a, b in zip(CAMPFIRE_BACKWARDS, CAMPFIRE_BACKWARDS[1:]))
    route = [form for form, *_ in CAMPFIRE_BACKWARDS] + [CAMPFIRE_BACKWARDS[-1][1]]
    root_is_sun = "the Sun" in route and route[-1] == "nuclear fusion"
    via_tree = "light absorbed by the tree" in route
    match_is_source = "the match" in route  # the match only starts the reaction; it is not on the chain
    earth_interior = "heat from inside the Earth" in route
    from_nothing = route[-1] is None  # energy conservation: every form has a source
    return [not via_tree, root_is_sun and via_tree, match_is_source, earth_interior, from_nothing]


def ocfs_turn_carbon(item: dict) -> list[bool]:
    """q-carbon: where do the wood's carbon atoms go when it burns? Atoms are conserved and keep
    their element (laws-atomic-theory); burning organic matter gives CO2 and H2O, and CO2 is a gas.
    Options: all turned into heat and gone; mostly CO2 into the atmosphere; destroyed by the flame;
    turned into oxygen; all left in the ash."""
    products = {"CO2": "gas", "H2O": "gas"}  # combustion of glucose-based matter (carbon_cycle)
    carbon_goes_to = [p for p in products if "C" in p]
    atoms_can_vanish = False  # atoms_conserved
    element_can_change = False  # atoms_conserved
    to_air = all(products[p] == "gas" for p in carbon_goes_to)
    return [atoms_can_vanish, to_air, atoms_can_vanish, element_can_change, not to_air]


# --- Check yourself ------------------------------------------------------------------------------

# Rule (inq:discover/pose-question, key concept "variables and controlled conditions"): a question is
# testable when it names one thing to change and one thing to measure, and both can be measured.
Q1_OPTIONS = [
    {"changed": None, "measured": None},                                 # why is compost so amazing?
    {"changed": None, "measured": ("microbes' happiness", False)},       # are the microbes happy?
    {"changed": ("leaf piece size", True), "measured": ("highest core temperature in 7 days (°C)", True)},
    {"changed": None, "measured": ("good for the Earth", False)},        # value judgement, no variable
    {"changed": None, "measured": None},                                 # what future will it become?
]


def ocfs_testable_question(item: dict) -> list[bool]:
    """q1: which compost question can be tested by experiment?"""
    def testable(o):
        return bool(o["changed"] and o["measured"] and o["changed"][1] and o["measured"][1])
    return [testable(o) for o in Q1_OPTIONS]


# q2: (question's idea, subject stated in the option). A pairing is right when the subject whose
# reviewed chapter teaches the idea is the one stated.
Q2_PAIRS = [
    ("heat_hot_to_cold", "physics"),
    ("respiration_releases_heat", "biology"),
    ("co2_makes_water_acidic", "chemistry"),
    ("seasons_day_length", "chemistry"),
    ("photosynthesis_stores_light", "earth"),
]


def ocfs_subject_pairs(item: dict) -> list[bool]:
    """q2: which question-subject pairings about the compost bin are right?"""
    return [SUBJECT_OF[idea] == subject for idea, subject in Q2_PAIRS]


# q3: rooftop solar water heater. Each chain is a list of links (from, to, kind); a heat link carries
# the temperatures of its two ends (plate hotter than the water it warms, as in the stem).
T_PLATE, T_WATER = 60, 30  # °C, relative order only: the sunlit plate is hotter than the cold water
Q3_CHAINS = [
    [("fusion", "sunlight", "sun_fusion"), ("sunlight", "plate thermal energy", "absorb"),
     ("plate", "water", ("heat", T_PLATE, T_WATER))],
    [("fusion", "sunlight", "sun_fusion"), ("sunlight", "plate thermal energy", "absorb"),
     ("water", "plate", ("heat", T_WATER, T_PLATE))],
    [("water thermal energy", "sunlight", "absorb"), ("sunlight", "Sun", "emit")],
    [("fission", "sunlight", "sun_fission"), ("sunlight", "plate thermal energy", "absorb"),
     ("plate", "water", ("heat", T_PLATE, T_WATER))],
    [("sunlight", "nuclear energy in the water", "convert")],
]


def ocfs_solar_chain(item: dict) -> list[bool]:
    """q3: which energy chain for the solar water heater is right? Every link must be a known fact:
    the Sun's energy is from fusion (not fission); sunlight absorbed becomes thermal energy; heat
    flows from hotter to colder; and the chain starts at the Sun's source."""
    def ok_link(link):
        a, b, kind = link
        if isinstance(kind, tuple):
            _, t_from, t_to = kind
            return t_from > t_to  # heat_hot_to_cold
        if kind == "sun_fusion":
            return a == "fusion" and b == "sunlight"
        if kind == "absorb":
            return a == "sunlight"  # light is absorbed and becomes thermal energy, not the reverse
        return False  # 'sun_fission', 'emit' from water, 'convert' to nuclear energy: not facts
    return [all(ok_link(l) for l in chain) and chain[0][0] == "fusion" for chain in Q3_CHAINS]


# q4-q5: compost core temperature, days 0-7 (illustrative data), °C.
COMPOST = [R(22), R(30), R(41), R(52), R(62), R(60), R(53), R(45)]


def ocfs_compost_rise(item: dict) -> int:
    """q4: average rise per day from day 0 to day 4."""
    avg = (COMPOST[4] - COMPOST[0]) / 4
    assert avg.q == 1
    return int(avg)


def ocfs_compost_conclusion(item: dict) -> list[bool]:
    """q5: which conclusion do the data support? A conclusion is supported when it agrees with the
    data, keeps to the sample measured (one bin, one week), and claims a cause only if the data
    tested it (inq:argue-model/conclude, key concept "evidence-based claims and model limits").
    Options: this bin peaked on day 4 then cooled; every compost peaks on day 4; the bin warmed
    because of sunlight; the fall proves all microbes died; day 7 was cooler than day 0."""
    peak_day = max(range(len(COMPOST)), key=lambda d: COMPOST[d])
    diffs = [b - a for a, b in zip(COMPOST, COMPOST[1:])]
    falls_after_peak = all(d < 0 for d in diffs[peak_day:])
    claims = [
        {"agrees": peak_day == 4 and falls_after_peak, "scope": "sample", "cause_tested": True},
        {"agrees": peak_day == 4, "scope": "all", "cause_tested": True},
        {"agrees": True, "scope": "sample", "cause_tested": False},  # sunlight was never varied
        {"agrees": True, "scope": "sample", "cause_tested": False},  # microbes were never counted
        {"agrees": COMPOST[7] < COMPOST[0], "scope": "sample", "cause_tested": True},
    ]
    return [c["agrees"] and c["scope"] == "sample" and c["cause_tested"] for c in claims]


# q6: designs to test the rival explanation "sunlight, not the microbes, warms the bin".
# Rule (key concept "designing and critiquing experiments"): a fair test compares groups that differ
# in exactly one variable, and that variable is the one the rival explanation names.
Q6_DESIGNS = [
    {"groups": 2, "changed": {"sunlight"}},
    {"groups": 2, "changed": {"sunlight", "amount of leaves"}},
    {"groups": 1, "changed": set()},
    {"groups": 2, "changed": {"amount of leaves", "water"}},
    {"groups": 0, "changed": set()},  # ask the neighbours: no measurement at all
]


def ocfs_rival_design(item: dict) -> list[bool]:
    """q6: which design best tests the rival explanation?"""
    rival_cause = "sunlight"
    return [d["groups"] >= 2 and d["changed"] == {rival_cause} for d in Q6_DESIGNS]


# q7: statements, each with its source.
CROSS_CUTTING = ["物質與能量", "構造與功能", "系統與尺度", "改變與穩定", "交互作用", "科學與生活", "資源與永續性"]
# slice confirmed_facts[15] / key_concepts: the 領綱 lists these seven cross-cutting concepts
REAL_GROUPS = {  # slice recent_trends[0] and corrections[1]: the official cross-subject 題組 pair two subjects
    "112 Q51-54": {"physics", "earth"}, "113 Q50-53": {"chemistry", "earth"},
    "114 Q40-43": {"biology", "earth"}, "115 Q50-53": {"earth", "physics"},
}
SCOPE_116 = {"physics", "chemistry", "biology", "earth", "inquiry"}  # slice confirmed_facts[1] (簡章)


def ocfs_statements(item: dict) -> list[bool]:
    """q7: which statements are right? Options: the 課綱 lists seven cross-cutting concepts incl.
    物質與能量 and 系統與尺度; energy goes round and back like the carbon atoms; every 112-115
    cross-subject group tested all four subjects; the 116 scope is the four required subjects incl.
    inquiry; burning destroys the carbon atoms, so the mass drops."""
    seven = len(CROSS_CUTTING) == 7 and {"物質與能量", "系統與尺度"} <= set(CROSS_CUTTING)
    energy_cycles = False  # energy_degrades: it flows one way and ends as spread-out heat
    all_four = all(len(s) == 4 for s in REAL_GROUPS.values())
    # option 4: parse the subjects the option names and compare them with the sourced scope
    names = {"物理": "physics", "化學": "chemistry", "生物": "biology", "地球科學": "earth",
             "探究與實作": "inquiry"}
    opt4 = item["text"]["zh-tw"]["options"][3]
    stated = {key for zh, key in names.items() if zh in opt4}
    scope = "必修" in opt4 and stated == SCOPE_116
    atoms_destroyed = False  # atoms_conserved
    return [seven, energy_cycles, all_four, scope, atoms_destroyed]


# q8 (written): the compost chain in the model answer. Each link: (cause, effect, fact).
Q8_CHAIN = [
    ("the Sun", "light", "sun_fusion"),
    ("light", "chemical energy in the leaves", "photosynthesis_stores_light"),
    ("chemical energy in the leaves", "heat in the core", "respiration_releases_heat"),
    ("heat in the core", "heat in the cooler air", "heat_hot_to_cold"),
]
Q8_CARBON = ("carbon in the leaves", "CO2 in the atmosphere", "carbon_cycle")


def ocfs_mixed_compost_chain(item: dict) -> bool:
    """q8: the model answer's chain is connected, every link is a fact from a reviewed chapter, it
    uses at least three subjects, and its heat link runs from hotter to colder: the stem gives the
    core 55 °C and the air 20 °C."""
    t_core, t_air = R(55), R(20)
    links = Q8_CHAIN + [Q8_CARBON]
    connected = all(a[1] == b[0] for a, b in zip(Q8_CHAIN, Q8_CHAIN[1:]))
    facts_ok = all(f in FACTS for *_, f in links)
    subjects = {SUBJECT_OF[f] for *_, f in links}
    hotter_core = t_core > t_air
    return bool(connected and facts_ok and len(subjects) >= 3 and hotter_core)
