"""Checks for src/data/items/earth/s116-universe-stars.yaml (116 sprint: EEd-Ⅴc-1~4: the scale and
hierarchy of the universe, its expansion and the big bang theory; brightness, luminosity, apparent and
absolute magnitude; star colour and surface temperature; multi-wavelength observation).

How the keys are recomputed (never from item["answer"]):
- Light travel time from a distance in light-years (a light-year is the distance light travels in one
  year), with exact Rationals.
- Brightness from luminosity and distance by the inverse-square law (light shared over a sphere of
  area 4πd²), and magnitude differences only through the rule "5 magnitudes = a factor of 100 in
  brightness", applied by repeated division by 100 (no logarithms, no decimals). Absolute magnitude is
  the apparent magnitude at the standard distance of 10 parsecs.
- An expansion model: galaxies at positions on a line, every distance multiplied by the same factor;
  recession speeds and "who sees whom receding" come out of the model.
- Qualitative facts are small tables, each with a source comment.
"""

from __future__ import annotations

from fractions import Fraction as F

# --- sources for the fact tables -------------------------------------------------------------------
# nat.json nat:EEd-Vc-1 keyConcepts: hierarchy 恆星→星團→星系→星系群→宇宙 (考試說明 sample item 1);
#   distant galaxies receding means the universe is expanding; 霹靂說 is the mainstream origin theory.
# Slice research.common_misconceptions (考試說明): Andromeda is a separate galaxy, not part of the Milky Way.
# nat.json nat:EEd-Vc-2: 視星等/絕對星等/亮度/光度 explained from principles. The rules "smaller magnitude
#   = brighter; 5 magnitudes = factor 100; absolute magnitude = apparent magnitude at 10 parsecs" are
#   standard 必修地科 content not quoted in the sources (listed in the writer's report).
# nat.json nat:EEd-Vc-3/4: colour indicates surface temperature; astronomy needs bands beyond visible
#   (115 Q3: multi-wavelength observation, 大氣窗). Which bands reach the ground is standard content
#   (listed in the writer's report).

HIERARCHY = ["star", "cluster", "galaxy", "group", "universe"]  # nat:EEd-Vc-1, smallest first

LIGHT_YEAR_IS = "distance"  # 國中 Ea-Ⅳ-2 (光年); a light-year is how far light goes in one year
YEARS_PER_LIGHT_YEAR = F(1)  # light takes one year to cover one light-year

# Galaxy facts for q2 (nat:EEd-Vc-1 and the slice misconception entry)
ANDROMEDA_INSIDE_MILKY_WAY = False
ANDROMEDA_KIND = "galaxy"
DISTANT_GALAXY_LIGHT = "redshift"  # receding (Doppler effect, physics/s116-em-waves)
MAINSTREAM_ORIGIN_THEORY = "big bang"

# Colour → surface-temperature rank, hottest first (nat:EEd-Vc-4: colour indicates surface temperature;
# the order is standard 必修 content, listed in the report)
COLOUR_BY_TEMPERATURE = ["bluish-white", "white", "yellow", "orange", "red"]
TEMPERATURE_FROM_COLOUR_ALONE = True  # colour depends on temperature, not on distance or apparent magnitude

# Which bands reach the ground through the atmosphere (atmospheric windows; standard content)
REACHES_GROUND = {
    "gamma": False,
    "x-ray": False,
    "ultraviolet": False,  # most of it absorbed by ozone
    "visible": True,
    "infrared": False,  # mostly absorbed (water vapour and other gases); only narrow windows
    "radio": True,  # part of the radio band
}

STANDARD_DISTANCE_PC = F(10)  # absolute magnitude: apparent magnitude at 10 parsecs
# nat:EEd-Vc-2 光度: the total energy a star gives off each second, a property of the star itself
# (standard 必修 definition, listed in the writer's report); brightness is what depends on distance
LUMINOSITY_DEPENDS_ON_OBSERVER = False


# --- the physics: brightness and magnitudes -------------------------------------------------------

def brightness(lum: F, d: F) -> F:
    """Inverse-square law: light shared evenly over a sphere of area 4πd² (4π cancels in every ratio)."""
    return F(lum) / F(d) ** 2


def mag_diff_from_ratio(ratio: F) -> int:
    """Magnitude difference m_dim − m_bright for a brightness ratio bright/dim that is a power of 100.
    Uses only "5 magnitudes = a factor of 100"; refuses any other ratio."""
    ratio = F(ratio)
    sign = 1
    if ratio < 1:
        ratio, sign = 1 / ratio, -1
    steps = 0
    while ratio > 1:
        assert ratio % 100 == 0, "only whole factors of 100 are allowed"
        ratio /= 100
        steps += 1
    assert ratio == 1
    return sign * 5 * steps


def ratio_from_mag_diff(diff: int) -> F:
    """Brightness ratio bright/dim for a magnitude difference that is a multiple of 5."""
    assert diff % 5 == 0, "only multiples of 5 magnitudes are allowed"
    return F(100) ** (diff // 5) if diff >= 0 else 1 / F(100) ** (-diff // 5)


def distance_pc(m: int, abs_m: int) -> F:
    """Distance from m − M: moving the star from 10 pc to its real distance d changes its brightness by
    (10/d)²; that change is m − M magnitudes."""
    dim_factor = ratio_from_mag_diff(m - abs_m)  # brightness at 10 pc / brightness where it is
    # (d/10)² = dim_factor, with dim_factor a power of 100, so d/10 is the matching power of 10
    k = 0
    x = dim_factor
    if x >= 1:
        while x > 1:
            x /= 100
            k += 1
    else:
        while x < 1:
            x *= 100
            k -= 1
    assert x == 1
    d = STANDARD_DISTANCE_PC * F(10) ** k if k >= 0 else STANDARD_DISTANCE_PC / F(10) ** (-k)
    # cross-check by the inverse-square law itself
    assert brightness(1, STANDARD_DISTANCE_PC) / brightness(1, d) == dim_factor
    return d


# --- the expansion model --------------------------------------------------------------------------

def expand(positions: list[F], factor: F) -> list[F]:
    """Every distance multiplied by the same factor (the chapter's bread model)."""
    return [p * factor for p in positions]


def recession(positions: list[F], factor: F, observer: int) -> list[F]:
    """How much farther each other galaxy gets from the observer in one step."""
    after = expand(positions, factor)
    o0, o1 = positions[observer], after[observer]
    return [abs(after[i] - o1) - abs(positions[i] - o0) for i in range(len(positions)) if i != observer]


# --- items ----------------------------------------------------------------------------------------

def us_turn_light_years(item: dict) -> list[bool]:
    """q-turn: a star about 100 light-years away; when did the light we see leave it?"""
    years_ago = F(100) * YEARS_PER_LIGHT_YEAR
    options = [F(0), F(100), F(1), F(10000)]
    out = [years_ago == o for o in options]
    # option 5 claims a light-year is a unit of time
    out.append(LIGHT_YEAR_IS == "time")
    return out


def us_turn_colour(item: dict) -> list[bool]:
    """q-colour: A reddish, B bluish-white; which has the higher surface temperature?"""
    rank = COLOUR_BY_TEMPERATURE.index
    a, b = rank("red"), rank("bluish-white")
    a_hotter, b_hotter = a < b, b < a
    return [a_hotter, b_hotter, a == b, not TEMPERATURE_FROM_COLOUR_ALONE, not TEMPERATURE_FROM_COLOUR_ALONE]


def us_hierarchy_order(item: dict) -> list[bool]:
    """q1: which list goes from smallest to largest?"""
    options = [
        ["cluster", "star", "galaxy", "group"],
        ["star", "cluster", "galaxy", "group"],
        ["star", "galaxy", "cluster", "group"],
        ["star", "cluster", "group", "galaxy"],
        ["galaxy", "cluster", "star", "group"],
    ]
    return [[HIERARCHY.index(x) for x in o] == sorted(HIERARCHY.index(x) for x in o) for o in options]


def us_expansion_statements(item: dict) -> list[bool]:
    """q2 (multi): (1) redshift means receding; (2) farther galaxies recede faster; (3) so the Milky Way is
    the centre; (4) Andromeda is a star cluster in the Milky Way; (5) the big bang theory is mainstream."""
    galaxies = [F(0), F(1), F(2), F(3), F(5)]  # Milky Way at index 0
    factor = F(3, 2)
    from_us = recession(galaxies, factor, 0)
    s1 = DISTANT_GALAXY_LIGHT == "redshift" and all(r > 0 for r in from_us)
    dists = [abs(g - galaxies[0]) for g in galaxies[1:]]
    pairs = sorted(zip(dists, from_us))
    s2 = all(pairs[i][1] < pairs[i + 1][1] for i in range(len(pairs) - 1))
    # a unique centre would be the only galaxy that sees every other one receding
    sees_all_receding = [all(r > 0 for r in recession(galaxies, factor, i)) for i in range(len(galaxies))]
    s3 = sees_all_receding[0] and sum(sees_all_receding) == 1
    s4 = ANDROMEDA_INSIDE_MILKY_WAY and ANDROMEDA_KIND == "cluster"
    s5 = MAINSTREAM_ORIGIN_THEORY == "big bang"
    return [s1, s2, s3, s4, s5]


def us_light_travel_time(item: dict) -> int:
    """q3: 4.2 × 10⁷ light-years; how many million years ago did the light leave?"""
    years = F(42, 10) * 10**7 * YEARS_PER_LIGHT_YEAR
    millions = years / 10**6
    assert millions.denominator == 1
    return int(millions)


def us_magnitude_from_distance(item: dict) -> int:
    """q4: equal luminosity, A 100 times as far as B; how many magnitudes larger is A's number?"""
    ratio = brightness(1, 1) / brightness(1, 100)  # B's brightness / A's
    return mag_diff_from_ratio(ratio)


def us_magnitude_table(item: dict) -> list[bool]:
    """q5 (multi): A (7, −3), B (−2, 3), C (5, 5) as (apparent, absolute)."""
    stars = {"A": (7, -3), "B": (-2, 3), "C": (5, 5)}
    brightest = min(stars, key=lambda s: stars[s][0])  # smaller apparent magnitude looks brighter
    most_luminous = min(stars, key=lambda s: stars[s][1])  # smaller absolute magnitude, more luminous
    d = {s: distance_pc(*v) for s, v in stars.items()}
    return [
        brightest == "B",
        most_luminous == "A",
        d["C"] == 10,
        d["B"] > STANDARD_DISTANCE_PC,
        d["A"] == 100,
    ]


def us_space_telescope_bands(item: dict) -> list[bool]:
    """q6 (multi): which bands must be observed from above the atmosphere?"""
    options = ["gamma", "visible", "x-ray", "radio", "ultraviolet"]
    return [not REACHES_GROUND[b] for b in options]


def us_colour_order(item: dict) -> list[bool]:
    """q7: A reddish, B yellowish, C bluish-white; order from hottest to coolest."""
    colour = {"A": "red", "B": "yellow", "C": "bluish-white"}
    hottest_first = sorted(colour, key=lambda s: COLOUR_BY_TEMPERATURE.index(colour[s]))
    options = [list("ABC"), list("CBA"), list("BCA"), list("ACB"), list("CAB")]
    return [o == hottest_first for o in options]


def us_brightness_statements(item: dict) -> list[bool]:
    """q8 (multi): brightness, luminosity and magnitude statements."""
    # (1) luminosity is the star's total output per second, a property of the star alone
    s1 = not LUMINOSITY_DEPENDS_ON_OBSERVER
    # (2) larger apparent magnitude looks brighter? A star 5 magnitudes larger is 100 times dimmer.
    s2 = ratio_from_mag_diff(5) < 1
    # (3) equal absolute magnitude M1 = M2: at the shared 10 pc the brightness ratio is the one for a
    #     0-magnitude difference; L = b·d², and d is the same, so the luminosity ratio equals it
    s3 = all(
        ratio_from_mag_diff(m2 - m1) * (STANDARD_DISTANCE_PC / STANDARD_DISTANCE_PC) ** 2 == 1
        for m1 in range(-5, 11) for m2 in range(-5, 11) if m1 == m2
    )
    # (4) equal brightness forces equal luminosity? Counterexample: 9 L at 3 d vs L at d.
    s4 = not (brightness(9, 3) == brightness(1, 1) and F(9) != F(1))
    # (5) apparent magnitude can be negative: a star 100 times as bright as a magnitude-0 star is
    #     magnitude −5 by the 5-magnitude rule
    s5 = 0 - mag_diff_from_ratio(F(100)) < 0
    return [s1, s2, s3, s4, s5]
