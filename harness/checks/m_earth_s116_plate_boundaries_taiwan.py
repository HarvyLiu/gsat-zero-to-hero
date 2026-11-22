"""Checks for src/data/items/earth/s116-plate-boundaries-taiwan.yaml (116 sprint: EIa-Ⅴc-2/3 plate boundary
types and their geologic processes, EIa-Ⅴc-4 evidence that Taiwan lies on a convergent boundary, EMd-Ⅴc-4
earthquakes in Taiwan, magnitude vs intensity, early warning).

How the keys are recomputed (never from item["answer"]):
- Boundary types come from the relative motion of two plates (the component across the boundary), and
  their features (magmatism, metamorphism, structures, focal depths) from one code table with a source
  comment per fact. Feature-to-boundary questions match the stated features against that table.
- A subduction zone is a small geometric model: foci lie along a slab that dips under the overriding
  plate, so the dip direction of the foci points to the overriding plate. Which plate subducts is read
  off the stated (invented) foci by the sign of an exact least-squares slope.
- Early warning: arrival time = distance / wave speed with exact Fractions; lead time = S arrival minus
  the stated warning time; the blind zone is where the lead time is not positive.
- Magnitude and intensity: one magnitude value per earthquake, one intensity value per place.
"""

from __future__ import annotations

from fractions import Fraction as F

# --- boundary types and their features -----------------------------------------------------------
# Source for the three types by relative motion (聚合、張裂、錯動) and for comparing magmatism,
# metamorphism, structures and focal distribution: nat:EIa-Vc-2 / nat:EIa-Vc-3 keyConcepts (108課綱
# 自然領綱 EIa-Ⅴc-2/3 學習內容說明; volcanic eruption styles excluded). The individual feature values are
# standard 必修地科 content (listed in the chapter report as standard facts not quoted in the sources):
# - divergent: mantle material rises and forms magma (new oceanic crust at ridges); tension -> normal
#   faults; shallow foci; metamorphism not prominent.
# - convergent with subduction: magma and volcanoes on the overriding plate (island / volcanic arc);
#   compression and burial -> metamorphism; reverse faults and folds; foci from shallow to deep in a
#   dipping band.
# - convergent by continental collision: compression -> reverse faults, folds, metamorphism, high
#   mountains; little magma; no deep dipping focal band.
# - transform: plates slide past horizontally -> strike-slip faults; almost no magma; metamorphism not
#   prominent; shallow foci.
FEATURES = {
    "divergent": {"magma": True, "metamorphism": False, "structures": {"normal"}, "deep_band": False},
    "subduction": {"magma": True, "metamorphism": True, "structures": {"reverse", "fold"}, "deep_band": True},
    "collision": {"magma": False, "metamorphism": True, "structures": {"reverse", "fold"}, "deep_band": False},
    "transform": {"magma": False, "metamorphism": False, "structures": {"strike-slip"}, "deep_band": False},
}
CONVERGENT = {"subduction", "collision"}


def boundary_from_motion(across: F, along: F) -> str:
    """Relative motion of plate B seen from plate A. across < 0: B approaches A; across > 0: B moves away;
    across = 0 and along != 0: they slide past each other (the chapter's first figure)."""
    if across < 0:
        return "convergent"
    if across > 0:
        return "divergent"
    assert along != 0, "no relative motion: not a boundary"
    return "transform"


def types_matching(**observed) -> set[str]:
    """Boundary types whose table entry agrees with every stated observation."""
    out = set()
    for name, f in FEATURES.items():
        ok = True
        for key, value in observed.items():
            if key == "structure":
                ok &= value in f["structures"]
            else:
                ok &= f[key] == value
        if ok:
            out.add(name)
    return out


# --- subduction geometry -------------------------------------------------------------------------
# A slab dips under the overriding plate, so foci deepen with distance from the trench on the
# overriding-plate side; the overriding plate also has a few shallow foci near the trench. The volcanic
# (island) arc lies on the overriding plate, parallel to the trench (standard 必修 content, see FEATURES).
SHALLOW_LIMIT = 30  # km, only used to call a focus "shallow" in the model below


def model_foci() -> list[tuple[int, F]]:
    """(signed distance from the trench in km, depth in km). Positive = overriding-plate side."""
    dip = F(4, 5)  # depth gained per km of horizontal distance; any positive value gives the same answers
    slab = [(x, dip * x + 10) for x in range(0, 301, 30)]
    overriding_crust = [(40, F(10)), (70, F(15))]
    ocean_side = [(-30, F(10)), (-80, F(8))]  # bending of the incoming plate: shallow only, no deepening
    return slab + overriding_crust + ocean_side


def deepest_by_distance(foci, side: int, bin_km: int = 50) -> list[F]:
    """Deepest focus in each 50 km distance bin on one side (side = +1 overriding, -1 ocean side),
    ordered away from the trench: the lower edge of the focal band."""
    bins: dict[int, F] = {}
    for x, d in foci:
        if x * side > 0 or (x == 0 and side == 1):
            k = abs(x) // bin_km
            bins[k] = max(bins.get(k, F(0)), d)
    return [bins[k] for k in sorted(bins)]


def strictly_increasing(seq) -> bool:
    return len(seq) >= 2 and all(a < b for a, b in zip(seq, seq[1:]))


def ls_slope(points: list[tuple[F, F]]) -> F:
    """Exact least-squares slope of depth on distance."""
    n = len(points)
    mx = sum(F(x) for x, _ in points) / n
    my = sum(F(y) for _, y in points) / n
    sxx = sum((F(x) - mx) ** 2 for x, _ in points)
    sxy = sum((F(x) - mx) * (F(y) - my) for x, y in points)
    return sxy / sxx


def cd_turn_dip_pattern(item: dict) -> list[bool]:
    """q-turn: foci near a trench on a vertical section. Options: (1) scattered with no pattern;
    (2) shallow near the trench, deeper toward one side, in a dipping band; (3) all shallow, right under
    the trench; (4) deepest right under the trench, shallower to both sides; (5) symmetric: deeper to both
    sides."""
    foci = model_foci()
    over = deepest_by_distance(foci, +1)
    ocean = deepest_by_distance(foci, -1)
    one_side_deepens = strictly_increasing(over) and not strictly_increasing(ocean)
    no_pattern = not (strictly_increasing(over) or strictly_increasing(ocean))
    all_shallow = max(d for _, d in foci) < SHALLOW_LIMIT
    deepest_at_trench = max(foci, key=lambda p: p[1])[0] == 0
    symmetric = strictly_increasing(over) and strictly_increasing(ocean)
    return [no_pattern, one_side_deepens, all_shallow, deepest_at_trench, symmetric]


def subduction_from_deepening(sides: dict[str, str], deepening_toward: str) -> tuple[str, str]:
    """Foci deepen toward the overriding plate. sides maps a direction to the plate on that side of the
    trench. Returns (subducting plate, overriding plate)."""
    overriding = sides[deepening_toward]
    (subducting,) = [p for d, p in sides.items() if d != deepening_toward]
    return subducting, overriding


def cd_dip_northeast(item: dict) -> list[bool]:
    """q-dip: a trench off NE Taiwan, Philippine Sea plate to the south, Eurasian plate to the north (as
    stated in the stem); foci deepen northward. Options: PSP under EUR; EUR under PSP; divergent;
    transform; no subduction."""
    sub, over = subduction_from_deepening({"south": "PSP", "north": "EUR"}, "north")
    deep_band = True  # foci reach depth in a band that deepens one way: only subduction has this
    kinds = types_matching(deep_band=deep_band)
    assert kinds == {"subduction"}
    return [
        (sub, over) == ("PSP", "EUR"),
        (sub, over) == ("EUR", "PSP"),
        "divergent" in kinds,
        "transform" in kinds,
        not kinds & {"subduction"},
    ]


# --- Check yourself ------------------------------------------------------------------------------


def cd_features_divergent(item: dict) -> list[bool]:
    """q1: many normal faults, shallow foci only, rising magma forming new oceanic crust. Options:
    divergent; subduction; continental collision; transform; cannot tell."""
    kinds = types_matching(structure="normal", deep_band=False, magma=True)
    options = ["divergent", "subduction", "collision", "transform"]
    return [k in kinds and len(kinds) == 1 for k in options] + [len(kinds) != 1]


def cd_subduction_statements(item: dict) -> list[bool]:
    """q2 (multi) about a subduction zone: (1) foci deepen from the trench toward the overriding plate;
    (2) a trench at the surface; (3) mainly normal faults; (4) volcanoes on the subducting plate, on the
    ocean side of the trench; (5) compression and burial often metamorphose rocks."""
    f = FEATURES["subduction"]
    over = deepest_by_distance(model_foci(), +1)
    s1 = f["deep_band"] and strictly_increasing(over)
    # the subducting plate bends down at the trench: the deep sea trench is its surface expression
    # (standard 必修 content; the chapter's table: 海溝 under 地形例子)
    SURFACE_FEATURE = {"subduction": "trench", "divergent": "ridge or rift", "transform": "offset ridge"}
    s2 = SURFACE_FEATURE["subduction"] == "trench"
    s3 = f["structures"] == {"normal"}
    VOLCANO_SIDE = "overriding"  # the arc forms on the overriding plate (FEATURES source)
    s4 = VOLCANO_SIDE == "subducting"
    s5 = f["metamorphism"]
    return [s1, s2, s3, s4, s5]


def cd_invented_trench(item: dict) -> list[bool]:
    """q3 (invented data): a N-S trench; foci 30 km west at 20 km depth, 100 km west at 80 km, 180 km
    west at 150 km; east of the trench only shallow foci at about 10 km. Options: (subducting side,
    arc side) or a non-subduction type."""
    west = [(F(30), F(20)), (F(100), F(80)), (F(180), F(150))]  # (km west of trench, depth)
    slope = ls_slope(west)
    assert slope > 0  # deeper farther west
    deepening = "west"
    sub, over = subduction_from_deepening({"west": "W", "east": "E"}, deepening)
    arc_side = "west" if over == "W" else "east"
    kinds = types_matching(deep_band=True)
    return [
        (sub, arc_side) == ("E", "west"),
        (sub, arc_side) == ("W", "east"),
        (sub, arc_side) == ("E", "east"),
        "divergent" in kinds,
        "transform" in kinds,
    ]


def cd_taiwan_evidence(item: dict) -> list[bool]:
    """q4 (multi): which observations are evidence that Taiwan lies on a convergent boundary?
    Each option is (is it observed in and around Taiwan?, which feature it is)."""
    # Observed in and around Taiwan (nat:EIa-Vc-4: infer from geologic structures and focal distribution;
    # the specific observations are standard 必修 content listed in the report): folds and reverse faults
    # across the island; wide areas of metamorphic rock in the Central Range; south of Taiwan foci deepen
    # eastward (Eurasian plate subducting under the Philippine Sea plate). Not observed: a mid-ocean ridge
    # in Taiwan; quakes mainly on strike-slip faults with almost no metamorphic rock.
    options = [
        (True, {"structure": "reverse"}),
        (True, {"metamorphism": True}),
        (False, {"structure": "normal", "magma": True}),
        (True, {"deep_band": True}),
        (False, {"structure": "strike-slip", "metamorphism": False}),
    ]
    out = []
    for observed, feature in options:
        kinds = types_matching(**feature)
        out.append(observed and bool(kinds) and kinds <= CONVERGENT)
    return out


# What an earthquake report gives (EMd-Ⅴc-4: 規模 and 震度 have different meanings and uses): one
# magnitude for the earthquake itself, and an intensity for each place. Magnitude is not a count of places.
REPORT_LISTS = {"magnitude": "one per earthquake", "intensity": "one per place"}


def cd_report_table(item: dict) -> list[bool]:
    """q5 (invented report): magnitude 6.0; intensity A 5, B 3, C 1. Options: (1) A shook hardest;
    (2) A had the largest magnitude; (3) C's magnitude was 1; (4) three magnitudes; (5) magnitude 6.0
    means six places felt it."""
    magnitudes = [F(6)]  # one earthquake, one magnitude
    intensity = {"A": 5, "B": 3, "C": 1}  # one value per place; larger = stronger shaking
    hardest = max(intensity, key=intensity.get)
    per_place_magnitude = REPORT_LISTS["magnitude"] == "one per place"
    magnitude_counts_places = False  # magnitude measures the earthquake's own size, not felt places
    return [
        hardest == "A",
        per_place_magnitude,
        per_place_magnitude,
        len(magnitudes) == 3,
        magnitude_counts_places,
    ]


def lead_time(distance: F, v_s: F, warn_at: F) -> F:
    """Seconds between the warning and the S-wave arrival (signal travel time neglected, as stated)."""
    return distance / v_s - warn_at


def cd_lead_time(item: dict) -> int:
    """q6: v_S = 3 km/s, warning 12 s after the quake, city 90 km away. (v_P = 6 km/s is not needed.)"""
    t = lead_time(F(90), F(3), F(12))
    assert t.denominator == 1
    return int(t)


def cd_blind_zone(item: dict) -> int:
    """q7: v_S = 4 km/s, warning 9 s after the quake. Blind zone: lead time <= 0, i.e. distance <= v_S * T."""
    v_s, warn = F(4), F(9)
    radius = v_s * warn
    assert lead_time(radius, v_s, warn) == 0
    assert lead_time(radius - 1, v_s, warn) < 0 < lead_time(radius + 1, v_s, warn)
    assert radius.denominator == 1
    return int(radius)


# Wave and signal speeds (standard facts: P waves are faster than S waves, from the previous chapter's
# EFa-Ⅴc-1; electronic signals travel far faster than seismic waves). Orders of magnitude in km/s.
SPEED = {"P": F(6), "S": F(7, 2), "signal": F(300000)}


def cd_warning_principle(item: dict) -> list[bool]:
    """q8 (multi): (1) uses P faster than S, warns after detecting P; (2) the warning signal is much
    faster than seismic waves; (3) warns before the quake begins; (4) places very near the epicentre may
    feel strong shaking before the warning; (5) the lead time is the same everywhere."""
    warn_at = F(10)  # any positive time after the origin; detection needs the P wave to arrive first
    leads = [lead_time(F(d), SPEED["S"], warn_at) for d in (5, 20, 50, 100)]
    s1 = SPEED["P"] > SPEED["S"]
    s2 = SPEED["signal"] > 1000 * SPEED["P"]
    s3 = warn_at < 0
    s4 = any(t < 0 for t in leads)
    s5 = len(set(leads)) == 1
    return [s1, s2, s3, s4, s5]


def cd_mag_two_cities(item: dict) -> list[bool]:
    """q-mag: one earthquake, reported at Hualien (near the epicentre) and Taipei (far). Options:
    (1) same magnitude, different intensity; (2) both the same; (3) magnitude differs, intensity same;
    (4) both differ; (5) only magnitude is reported, never intensity."""
    magnitude = {"Hualien": F(6), "Taipei": F(6)}  # a property of the earthquake: one value
    # intensity usually falls with distance from the epicentre (the chapter's illustrative curve)
    intensity = {"Hualien": F(270, 10 + 30), "Taipei": F(270, 120 + 30)}
    same_m = len(set(magnitude.values())) == 1
    same_i = len(set(intensity.values())) == 1
    only_magnitude = set(REPORT_LISTS) == {"magnitude"}
    return [same_m and not same_i, same_m and same_i, not same_m and same_i, not same_m and not same_i, only_magnitude]
