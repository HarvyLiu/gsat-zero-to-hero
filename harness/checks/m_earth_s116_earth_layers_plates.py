"""Checks for src/data/items/earth/s116-earth-layers-plates.yaml (116 sprint: EFa-Ⅴc-1, EFa-Ⅴc-2: Earth's
layers from seismic waves; EIa-Ⅴc-1: continental drift, sea-floor spreading and plate tectonics as history
of science).

How the keys are recomputed (never from item["answer"]):
- A wave-propagation rule table (which wave passes which state of matter) applied to small Earth models:
  each hypothesis in an item is encoded as a model, and the model either reproduces the stated
  observations or not.
- A speed-profile reader: boundaries are found from the stem's (invented) speed data, not typed in.
- A ridge model with exact Fractions: age = distance / rate, sediment = constant rate × age, stripes from
  an arbitrary reversal history, so symmetry and age trends come out of the model.
- History items from an explicit facts table with a source comment per fact.

Sources: research slice for this chapter (verification.final_units key_concepts: wave-speed vs depth graph
gives 地殼/地函/地核/岩石圈/軟流圈; S waves cannot pass through liquid, so the outer core is liquid;
wave-speed changes distinguish 岩石圈 from 軟流圈; physical layering emphasised, chemical layering
mentioned; EIa-Ⅴc-1 told as history of science, models built as evidence accumulates; plate tectonics
explains observed phenomena). Facts marked STANDARD are standard 必修 textbook content not found in the
slice or nat.json; they are listed in the writer's report for the owner.
"""

from __future__ import annotations

from fractions import Fraction as F

# --- wave propagation ------------------------------------------------------------------------------

# Slice (EFa-Ⅴc-1/2 key_concepts): S waves cannot pass through liquid.
# STANDARD: P waves travel through solids and liquids; neither travels through empty space.
PASSES = {
    ("P", "solid"): True,
    ("P", "liquid"): True,
    ("P", "vacuum"): False,
    ("S", "solid"): True,
    ("S", "liquid"): False,
    ("S", "vacuum"): False,
}


def arrives(wave: str, path_states: list[str], absorbed_in: set[str] | None = None, layers: list[str] | None = None) -> bool:
    """A wave arrives (eventually) iff every material on its path lets it through and no layer on the path
    is assumed to absorb it."""
    if absorbed_in and layers and any(l in absorbed_in for l in layers):
        return False
    return all(PASSES[(wave, s)] for s in path_states)


def lp_turn_far_side(item: dict) -> list[bool]:
    """q-turn: near stations get P then S; a far-side station gets P only, even after a long wait.
    Each option is an Earth model; it is right iff it reproduces both observations.
    Near path: crust + mantle. Far-side path: crust + mantle + deep interior (+ mantle + crust)."""
    observed = {"near": {"P": True, "S": True}, "far": {"P": True, "S": False}}

    def predict(deep_state: str, *, s_passes_solid: bool = True, crust_absorbs_s: bool = False) -> dict:
        table = dict(PASSES)
        if not s_passes_solid:
            table[("S", "solid")] = False
        near_states, near_layers = ["solid", "solid"], ["crust", "mantle"]
        far_states, far_layers = ["solid", "solid", deep_state, "solid", "solid"], ["crust", "mantle", "deep", "mantle", "crust"]
        out = {}
        for name, states, layers in (("near", near_states, near_layers), ("far", far_states, far_layers)):
            out[name] = {}
            for w in ("P", "S"):
                ok = all(table[(w, s)] for s in states)
                if w == "S" and crust_absorbs_s and "crust" in layers:
                    ok = False
                out[name][w] = ok
        return out

    models = [
        predict("liquid"),                       # (1) a liquid layer deep inside
        predict("solid"),                        # (2) "S is just late": an all-solid Earth, where S does arrive in the end
        predict("solid", crust_absorbs_s=True),  # (3) the crust absorbs S waves
        predict("vacuum"),                       # (4) a hollow centre
        predict("solid", s_passes_solid=False),  # (5) the core is solid and S cannot cross solids
    ]
    return [m == observed for m in models]


# --- history facts ---------------------------------------------------------------------------------

# STANDARD (history of science, EIa-Ⅴc-1): Wegener's evidence for continental drift, 1910s.
WEGENER_EVIDENCE = {"coastline fit", "same fossils on both sides", "matching rock belts", "ancient glacier traces"}
# STANDARD: the coastlines and fossils on the two sides of the Atlantic do match (that is his evidence).
COASTLINES_MATCH = True
FOSSILS_MATCH = True
# STANDARD: the main objection was that he could not give a convincing force/mechanism to move continents.
MECHANISM_CONVINCING = False
# STANDARD: sea-floor rock ages came from sea-floor surveys after the mid-20th century, not in the 1910s.
DATA_AVAILABLE_FROM = {"sea-floor rock ages": 1950, "magnetic stripes": 1950}  # decade, roughly
WEGENER_DECADE = 1910


def lp_drift_rejected(item: dict) -> list[bool]:
    """q-drift: why was continental drift not accepted at first?"""
    return [
        not MECHANISM_CONVINCING,
        not COASTLINES_MATCH,
        not FOSSILS_MATCH,
        DATA_AVAILABLE_FROM["sea-floor rock ages"] <= WEGENER_DECADE,
        len(WEGENER_EVIDENCE) == 1,
    ]


# --- seismic layers --------------------------------------------------------------------------------


def state_from_speeds(p: float, s: float) -> str:
    """Slice: S waves cannot pass through liquid. A layer where P gets through and S does not is liquid;
    where both get through it is solid."""
    if p > 0 and s == 0:
        return "liquid"
    if p > 0 and s > 0:
        return "solid"
    raise ValueError("no wave at all: not a case in these items")


def lp_liquid_depths(item: dict) -> list[bool]:
    """q1: (depth km, P km/s, S km/s) from the stem (illustrative data)."""
    rows = [(500, F("9.5"), F("5.2")), (2000, F("12.8"), F("6.9")), (3200, F("8.2"), F(0)), (4800, F("10.1"), F(0)), (5800, F("11.2"), F("3.6"))]
    return [state_from_speeds(p, s) == "liquid" for _, p, s in rows]


def read_profile(segments: list[tuple[int, int, str]]) -> dict:
    """Read layer boundaries from a qualitative speed profile. Each segment is (top km, bottom km, change)
    with change one of 'start', 'jump up', 'slower', 'faster'. Slice: the 地殼/地函 boundary is where
    both waves suddenly speed up; the 軟流圈 is the low-speed stretch; the 岩石圈 is everything above it."""
    crust_bottom = next(top for top, _, ch in segments if ch == "jump up")
    lvz = next((top, bot) for top, bot, ch in segments if ch == "slower")
    return {
        "crust": (0, crust_bottom),
        "asthenosphere": lvz,
        "lithosphere": (0, lvz[0]),
        "uppermost mantle": (crust_bottom, lvz[0]),
    }


def union(*ivs: tuple[int, int]) -> tuple[int, int] | None:
    """Union of touching intervals; None if they leave a gap."""
    ivs = sorted(ivs)
    lo, hi = ivs[0]
    for a, b in ivs[1:]:
        if a != hi:
            return None
        hi = b
    return (lo, hi)


MANTLE_BOTTOM = 2900  # STANDARD (illustrative depth of the core-mantle boundary; only its order matters here)


def lp_lithosphere_extent(item: dict) -> list[bool]:
    """q2: speeds jump up at 28 km; slower from 80 to 180 km; faster below 180 km (illustrative data)."""
    prof = read_profile([(0, 28, "start"), (28, 80, "jump up"), (80, 180, "slower"), (180, 400, "faster")])
    whole_mantle = (prof["crust"][1], MANTLE_BOTTOM)
    options = [
        prof["crust"],
        union(prof["crust"], prof["uppermost mantle"]),
        union(prof["crust"], whole_mantle),
        prof["asthenosphere"],
        union(prof["crust"], prof["asthenosphere"]),  # leaves a gap, so it is not one layer at all
    ]
    return [o == prof["lithosphere"] for o in options]


# Layer model. Slice: outer core liquid (S cannot pass); asthenosphere told apart from lithosphere by wave
# speeds (S slower but not zero, so not liquid); physical vs chemical layering.
# STANDARD: inner core solid; lithosphere = crust + uppermost mantle, rigid; asthenosphere softer and able
# to flow slowly; crust/mantle/core is the compositional division.
LAYERS = {
    "lithosphere": {"state": "solid", "S": "passes", "chem": {"crust", "mantle"}},
    "asthenosphere": {"state": "solid", "S": "slower", "chem": {"mantle"}},
    "outer core": {"state": "liquid", "S": "stops", "chem": {"core"}},
    "inner core": {"state": "solid", "S": "passes", "chem": {"core"}},
}
DIVIDED_BY = {"crust": "composition", "mantle": "composition", "core": "composition", "lithosphere": "physical", "asthenosphere": "physical"}


def lp_layer_statements(item: dict) -> list[bool]:
    """q7 (multi)."""
    for name, layer in LAYERS.items():  # internal consistency with the propagation table
        assert (layer["S"] == "stops") == (not PASSES[("S", layer["state"])]), name
    s1 = LAYERS["outer core"]["state"] == "liquid"
    s2 = LAYERS["inner core"]["state"] == "solid"
    s3 = LAYERS["asthenosphere"]["state"] == "liquid"
    # the bottom of the crust equals the bottom of the lithosphere only if the lithosphere is crust alone
    s4 = LAYERS["lithosphere"]["chem"] == {"crust"}
    s5 = all(DIVIDED_BY[k] == "composition" for k in ("crust", "mantle", "core")) and all(
        DIVIDED_BY[k] == "physical" for k in ("lithosphere", "asthenosphere")
    )
    return [s1, s2, s3, s4, s5]


# Plate tectonics (slice: plate tectonics explains the observed phenomena; STANDARD: plates are pieces of
# the lithosphere moving on the asthenosphere).
PLATES_ARE = "lithosphere"
PLATES_MOVE_ON = "asthenosphere"


def lp_plate_layers(item: dict) -> list[bool]:
    """q6: (plates are made of, they move on)."""
    options = [("lithosphere", "asthenosphere"), ("crust", "mantle"), ("crust", "outer core"), ("asthenosphere", "outer core"), ("lithosphere", "inner core")]
    return [o == (PLATES_ARE, PLATES_MOVE_ON) for o in options]


# --- sea-floor spreading ---------------------------------------------------------------------------

CM_PER_KM = 100_000


def lp_separation_rate(item: dict) -> int:
    """q3: rock 72 km east of the ridge, 1.2 million years old; both sides move away at the same rate.
    Separation rate of the two sides = 2 × one side's rate (cm per year)."""
    one_side = F(72 * CM_PER_KM) / F(1_200_000)
    total = 2 * one_side
    assert total.denominator == 1
    return int(total)


def ridge_model(rate_cm_yr: F, sediment_rate: F, reversals_ma: list[F]):
    """Return functions of signed distance x (km; negative = west) for age (Ma), sediment and polarity.
    reversals_ma: ages (Ma) at which the field flipped; polarity is +1 today (STANDARD: the field has
    reversed many times; new rock records the field of the time it formed)."""

    def age(x: F) -> F:
        return F(abs(x) * CM_PER_KM, 1) / rate_cm_yr / 1_000_000

    def sediment(x: F) -> F:
        return sediment_rate * age(x)

    def polarity(x: F) -> int:
        flips = sum(1 for r in reversals_ma if r < age(x))
        return 1 if flips % 2 == 0 else -1

    return age, sediment, polarity


def lp_ridge_model(item: dict) -> list[bool]:
    """q4 (multi). Sampled over several arbitrary rates and reversal histories: a claim is true only if it
    holds in every run."""
    runs = [
        (F(2), F(1), [F(1), F("2.5"), F("3.6")]),
        (F(5), F(3), [F("0.7"), F(2), F("4.1"), F(6)]),
        (F("1.5"), F("0.5"), [F(3)]),
    ]
    xs = [F(k * 7) for k in range(1, 40)]
    res = [True, True, True, True, True]
    for rate, sed, rev in runs:
        age, sediment, pol = ridge_model(rate, sed, rev)
        res[0] &= all(pol(x) == pol(-x) for x in xs)
        res[1] &= all(age(a) < age(b) for a, b in zip(xs, xs[1:]))
        res[2] &= all(sediment(F(0)) < sediment(x) for x in xs)
        res[3] &= all(age(F(0)) > age(x) for x in xs)
        res[4] &= all(age(x) != age(-x) for x in xs)
    return res


def lp_stripes_support(item: dict) -> list[bool]:
    """q5: which idea do mirror-image stripes most directly support? Each idea is turned into what it
    predicts about stripes; it is supported iff it predicts symmetric stripes."""
    age, _, pol = ridge_model(F(3), F(1), [F(1), F(2)])
    xs = [F(k * 5) for k in range(1, 30)]
    spreading_predicts = all(pol(x) == pol(-x) for x in xs) and len({pol(x) for x in xs}) == 2
    _, _, pol_none = ridge_model(F(3), F(1), [])  # a field that never reversed
    never_reversed_predicts = len({pol_none(x) for x in xs}) == 2  # one polarity only: no stripes
    predicts_symmetric_stripes = [
        spreading_predicts,
        never_reversed_predicts,
        False,  # outer core liquid: inferred from S waves, says nothing about sea-floor stripes
        False,  # asthenosphere as magma: wrong (S waves pass) and says nothing about stripes
        False,  # continents ploughing through the sea floor: makes no prediction of mirror stripes
    ]
    return predicts_symmetric_stripes
