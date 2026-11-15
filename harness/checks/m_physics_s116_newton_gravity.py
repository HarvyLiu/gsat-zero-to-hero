"""Checks for src/data/items/physics/s116-newton-gravity.yaml (116 sprint: PEb-Ⅴc-4~5, PKb-Ⅴc-1~2).

必修物理 treats Newton's laws qualitatively, so most checks encode a physical rule as code (a force is
an interaction between two named bodies; the net force sets the change of velocity; static friction
matches the push up to a maximum; inverse-square gravity) and evaluate each option against it.
Numeric items use exact SymPy arithmetic. No check reads item["answer"].
"""

from __future__ import annotations

import sympy as sp

# --------------------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------------------

# A force is (interaction, exerting body, receiving body). Newton's third law: the partner of a force
# is the same interaction with the two bodies swapped (PEb-Ⅴc-4 說明: name who exerts, who receives).
def third_law_partner(force: tuple[str, str, str]) -> tuple[str, str, str]:
    kind, by, on = force
    return (kind, on, by)


def net_force(forces: list[tuple[sp.Expr, sp.Expr]]) -> sp.Matrix:
    return sp.Matrix([sum(f[0] for f in forces), sum(f[1] for f in forces)]) if forces else sp.zeros(2, 1)


def same_direction(u: sp.Matrix, v: sp.Matrix) -> bool:
    """True when u and v are both zero, or both non-zero and point the same way."""
    uz, vz = all(c == 0 for c in u), all(c == 0 for c in v)
    if uz or vz:
        return uz and vz
    cross = sp.simplify(u[0] * v[1] - u[1] * v[0])
    dot = sp.simplify(u.dot(v))
    return bool(cross == 0 and dot > 0)


def static_friction(push: sp.Expr, f_max: sp.Expr) -> sp.Expr | None:
    """Size of the static friction on a resting box pushed horizontally with `push`.
    It equals the push while the push is below the maximum; None means the box starts to slide."""
    return push if bool(push <= f_max) else None


# --------------------------------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------------------------------

def ng_turn_puck(item: dict) -> list[bool]:
    """q-turn: a puck sliding on (almost) frictionless ice keeps going. Which horizontal force does it
    need to keep moving? Options (required net horizontal force): forward (else it stops at once);
    none; a forward force slightly smaller than the kick; backward; a forward push from the ice.
    First law: unchanged velocity means zero net force, so the required horizontal force is none."""
    velocity_changes = False  # it keeps sliding at the same speed in the same direction
    required = "none" if not velocity_changes else "some"
    options = ["forward", "none", "forward", "backward", "forward"]
    return [o == required for o in options]


def ng_weight_partner(item: dict) -> list[bool]:
    """q1: a book rests on a table. The reaction force to the book's weight (Earth's gravity on the book).
    Options: table's normal force on book; book's push on table; book's gravity on Earth;
    Earth's gravity on the table; book's friction on table."""
    weight = ("gravity", "earth", "book")
    options = [
        ("contact", "table", "book"),
        ("contact", "book", "table"),
        ("gravity", "book", "earth"),
        ("gravity", "earth", "table"),
        ("friction", "book", "table"),
    ]
    partner = third_law_partner(weight)
    return [o == partner for o in options]


def ng_box_static(item: dict) -> list[bool]:
    """q2: a box rests on a level floor; a horizontal push P smaller than the maximum static friction.
    (1) friction equals P in size, opposite in direction; (2) to start it sliding the push must exceed
    the box's weight; (3) with no push the friction is zero; (4) weight and normal force are an
    action-reaction pair; (5) a slightly larger push that still fails to move it meets a larger friction."""
    P, fmax, W = sp.symbols("P f_max W", positive=True)
    p_val, fmax_val, w_val = sp.Integer(30), sp.Integer(50), sp.Integer(200)  # any P < f_max works
    subs = {P: p_val, fmax: fmax_val, W: w_val}
    f = static_friction(P.subs(subs), fmax.subs(subs))
    friction_vec = sp.Matrix([-f, 0])
    push_vec = sp.Matrix([P.subs(subs), 0])
    s1 = f == P.subs(subs) and same_direction(friction_vec, -push_vec)
    # (2) the sliding threshold is the maximum static friction, a horizontal quantity; the weight is
    # vertical and balanced by the normal force, so the threshold is not "the weight".
    threshold = fmax
    s2 = threshold == W
    s3 = static_friction(sp.Integer(0), fmax_val) == 0
    # (4) both act on the box: weight (Earth on box) and normal (floor on box); partners swap bodies.
    weight, normal = ("gravity", "earth", "box"), ("contact", "floor", "box")
    s4 = third_law_partner(weight) == normal
    p2 = p_val + 5
    f2 = static_friction(p2, fmax_val)
    s5 = f2 is not None and bool(f2 > f)
    return [bool(s1), bool(s2), bool(s3), bool(s4), bool(s5)]


def ng_top_net_force(item: dict) -> list[bool]:
    """q3: a ball thrown at an angle, air resistance ignored, at the top of its path: direction of the
    net force. Options: up; forward (horizontal); down; zero; forward-and-down."""
    m, g = sp.symbols("m g", positive=True)
    forces = [(sp.Integer(0), -m * g)]  # gravity is the only force once the ball has left the hand
    F = net_force(forces)
    options = [sp.Matrix([0, 1]), sp.Matrix([1, 0]), sp.Matrix([0, -1]), sp.Matrix([0, 0]), sp.Matrix([1, -1])]
    return [same_direction(F, o) for o in options]


def ng_apple_earth(item: dict) -> list[bool]:
    """q8: Earth pulls a falling apple with force F. (1) the apple pulls Earth with a force of size F;
    (2) Earth's velocity changes far less than the apple's; (3) the two forces cancel, being equal and
    opposite; (4) the apple's pull on Earth is zero; (5) both forces belong to the same interaction."""
    F = sp.symbols("F", positive=True)
    m_apple = sp.Rational(2, 10)           # kg, any everyday mass
    m_earth = sp.Integer(6) * 10**24       # kg
    on_apple = ("gravity", "earth", "apple")
    on_earth = third_law_partner(on_apple)
    size_on_earth = F                      # third law: equal size
    s1 = size_on_earth == F
    # second law, qualitatively: the same force changes a larger mass's velocity less (a ∝ 1/m)
    a_earth, a_apple = size_on_earth / m_earth, F / m_apple
    s2 = bool(sp.simplify(a_earth / a_apple) < 1)
    # forces cancel only when they act on the same body
    s3 = on_apple[2] == on_earth[2]
    s4 = size_on_earth == 0
    s5 = on_apple[0] == on_earth[0]
    return [s1, s2, s3, s4, s5]


def ng_inverse_square_alt4r(item: dict) -> sp.Integer:
    """q4: gravity on a satellite 4R above Earth's surface is 1/① of its value at the surface.
    Distances are measured from Earth's centre: r = R + 4R."""
    R = sp.symbols("R", positive=True)
    r = R + 4 * R
    ratio = (R / r) ** 2                    # F ∝ 1/r²
    return sp.Integer(1 / sp.simplify(ratio))


# Planet data (a in AU, T in years) shown in the lesson figure; standard values. The check confirms
# that each one fits T² = a³ (Earth units) to within 1 %, so the figure agrees with the law it shows.
PLANETS = {
    "Mercury": (sp.Rational("0.387"), sp.Rational("0.241")),
    "Venus": (sp.Rational("0.723"), sp.Rational("0.615")),
    "Earth": (sp.Integer(1), sp.Integer(1)),
    "Mars": (sp.Rational("1.524"), sp.Rational("1.881")),
    "Jupiter": (sp.Rational("5.203"), sp.Rational("11.862")),
}


def ng_kepler_third_25au(item: dict) -> sp.Integer:
    """q5: Kepler's third law (T² ∝ a³), Earth a = 1 AU, T = 1 yr. A comet with a = 25 AU: T = ① yr."""
    for a, T in PLANETS.values():
        assert abs(T**2 / a**3 - 1) < sp.Rational(1, 100)
    a = sp.Integer(25)
    T = sp.sqrt(a**3 * (sp.Integer(1) ** 2 / sp.Integer(1) ** 3))
    return sp.Integer(T)


def ng_orbit_qualitative(item: dict) -> list[bool]:
    """q6: a planet on an ellipse around the Sun, acted on by the Sun's gravity only.
    (1) it moves fastest near perihelion; (2) the gravitational force always points at the Sun;
    (3) on the way out from the Sun gravity slows it down; (4) the force always points along the
    velocity; (5) the force is largest at aphelion.
    Model: ellipse x = 5cosθ, y = 4sinθ (counter-clockwise), Sun at the focus (3, 0)."""
    a, b, c = 5, 4, 3
    S = sp.Matrix([c, 0])
    thetas = [k * sp.pi / 6 for k in range(12)]

    def pos(t):
        return sp.Matrix([a * sp.cos(t), b * sp.sin(t)])

    def vel_dir(t):
        return sp.Matrix([-a * sp.sin(t), b * sp.cos(t)])

    def r(t):
        return sp.sqrt((S - pos(t)).dot(S - pos(t)))

    def speed_sq(t):  # vis-viva, up to a constant: v² ∝ 2/r − 1/a
        return 2 / r(t) - sp.Rational(1, a)

    def force(t):  # inverse-square attraction toward the Sun, up to a constant
        d = S - pos(t)
        return d / r(t) ** 3

    speeds = [sp.nsimplify(sp.simplify(speed_sq(t))) for t in thetas]
    perihelion = 0  # θ = 0 is (5, 0), the point nearest the focus (3, 0)
    s1 = all(bool(speeds[perihelion] > s) for i, s in enumerate(speeds) if i != perihelion)
    s2 = all(same_direction(force(t), S - pos(t)) for t in thetas)
    outbound = [t for t in thetas if 0 < t < sp.pi]  # r grows from perihelion to aphelion
    assert all(bool(sp.simplify(r(t2) - r(t1)) > 0) for t1, t2 in zip(outbound, outbound[1:]))
    s3 = all(bool(sp.simplify(force(t).dot(vel_dir(t))) < 0) for t in outbound)
    s4 = all(same_direction(force(t), vel_dir(t)) for t in thetas)
    sizes = [sp.simplify(1 / r(t) ** 2) for t in thetas]
    aphelion = 6  # θ = π is (−5, 0)
    s5 = all(bool(sizes[aphelion] > s) for i, s in enumerate(sizes) if i != aphelion)
    return [s1, s2, s3, s4, s5]


# Facts about how the laws were found, each with its source.
FACTS = {
    # research/verified-2026-11-15.json physics verification.final_units order 5: Kepler's three laws
    # are "an inductive result from accumulated observation data"; nat:PKb-Vc-1 keyConcepts.
    "kepler_method": "induction",
    # nat:PKb-Vc-1 keyConcepts: "Deductive (Newton) vs inductive (Kepler) reasoning".
    "newton_method": "deduction",
    # nat:PKb-Vc-1 keyConcepts: "Newton's laws plus inverse-square gravity explain Kepler's laws".
    "relation": "explains",
}


def ng_deduction_induction(item: dict) -> list[bool]:
    """q7: which best describes how Kepler's laws and Newton's gravitation are related?
    Each option as (Kepler's method, Newton's method, relation of Newton's theory to Kepler's laws)."""
    options = [
        ("induction", "deduction", "explains"),
        ("deduction", "induction", "explains"),
        ("induction", "none", "reorganises"),
        ("induction", "deduction", "overturns"),
        ("induction", "induction", "explains"),
    ]
    truth = (FACTS["kepler_method"], FACTS["newton_method"], FACTS["relation"])
    return [o == truth for o in options]
