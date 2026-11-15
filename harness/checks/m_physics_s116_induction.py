"""Checks for src/data/items/physics/s116-induction.yaml (116 sprint: PKc-Ⅴc-3, magnetic effect of
current and electromagnetic induction).

必修物理 is qualitative here, so most checks encode a rule as code instead of computing a number:
- Ampère's right-hand rule as a direction-only cross product, B ∝ (current direction) × r̂, with
  x = east, y = north, z = up. Only directions are compared, never magnitudes.
- Faraday (qualitative): an induced current exists exactly when the field through the coil changes,
  i.e. dΦ/dt ≠ 0 for a model Φ(t) of the situation.
- Lenz (exam skill): the induced current's own field inside the coil points against dΦ/dt.
Each function recomputes its item's answer from the situation in the stem; none reads item["answer"].
"""

from __future__ import annotations

import sympy as sp
from sympy import Matrix

EAST = Matrix([1, 0, 0])
NORTH = Matrix([0, 1, 0])
UP = Matrix([0, 0, 1])
t = sp.Symbol("t", nonnegative=True)
k = sp.Symbol("k", positive=True)  # field strength scale; only signs and comparisons are used


def _same_direction(a: Matrix, b: Matrix) -> bool:
    """True when a and b are non-zero and point the same way."""
    if a.norm() == 0 or b.norm() == 0:
        return False
    return a.cross(b) == Matrix([0, 0, 0]) and a.dot(b) > 0


def _wire_field(current: Matrix, r_from_wire: Matrix) -> Matrix:
    """Ampère's right-hand rule for a long straight wire: thumb along the current, fingers curl the way
    the field goes. As a direction this is current × r̂ (r̂ from the wire to the point)."""
    return current.cross(r_from_wire)


def _loop_center_field(view: Matrix, up: Matrix, sense: str) -> Matrix:
    """Field direction at the centre of a loop seen by a viewer looking along `view` with head along `up`,
    when the current goes 'cw' (clockwise) or 'ccw' as that viewer sees it. Built from the straight-wire
    rule applied to the top piece of the loop: clockwise means the top piece carries current to the
    viewer's right, and the centre lies in direction −up from it."""
    right = view.cross(up)
    dl = right if sense == "cw" else -right
    return _wire_field(dl, -up)


def _sense_seen(field: Matrix, view: Matrix, up: Matrix) -> str | None:
    """Which circulation ('cw'/'ccw') produces `field` at the loop centre for this viewer, or None."""
    for s in ("cw", "ccw"):
        if _same_direction(_loop_center_field(view, up, s), field):
            return s
    return None


def _induced_axis_field(phi_x: sp.Expr, at: sp.Expr = sp.Integer(0)) -> Matrix:
    """Lenz: phi_x(t) is the x-component of the external field through a coil whose axis is x.
    The induced field inside the coil points against the change: −sign(dΦ/dt) along x."""
    rate = sp.simplify(sp.diff(phi_x, t).subs(t, at))
    sign = sp.sign(rate)
    return -sign * EAST


# ---------------------------------------------------------------------------------------------------


def ind_turn_static_magnet(item: dict) -> list[bool]:
    """q-turn: the magnet has been pushed into the coil and now rests inside it. Model: the magnet's
    position is fixed, so the field through the coil is a constant Φ0 and dΦ/dt = 0 → no induced
    current, the galvanometer returns to zero.
    Options: keeps the deflection; returns to zero; deflects the other way and stays; grows; swings
    back and forth without stopping."""
    phi0 = sp.Symbol("Phi0", positive=True)
    rate = sp.diff(phi0 + 0 * t, t)
    outcome = "zero" if rate == 0 else "nonzero"
    labels = ["keeps", "zero", "reverse-steady", "grows", "oscillates"]
    return [lab == outcome for lab in labels]


def ind_wire_compass(item: dict) -> list[bool]:
    """q1: vertical wire, current upward, compass due SOUTH of the wire, Earth's field ignored.
    The compass N pole points along B. Options: east, west, south, north, vertically up."""
    b = _wire_field(UP, -NORTH)
    opts = [EAST, -EAST, -NORTH, NORTH, UP]
    return [_same_direction(b, o) for o in opts]


def ind_solenoid_pole(item: dict) -> list[bool]:
    """q2: a horizontal solenoid along the x axis (left end at −x, right end at +x). Seen from the left
    end (viewer looks along +x, head up +z) the current is clockwise. Field lines leave a magnet at its
    N pole, so the N end is the end the inside field points to.
    Options: left end is N; right end is N; both ends are N; no field inside; field points radially out."""
    b = _loop_center_field(EAST, UP, "cw")
    n_end = "right" if b.dot(EAST) > 0 else ("left" if b.dot(EAST) < 0 else None)
    no_field = b.norm() == 0
    radial = b.norm() != 0 and b.dot(EAST) == 0  # a radial field would be perpendicular to the axis
    # (3) "both ends N" is never true for a coil: field lines leave at one end and return at the other.
    return [n_end == "left", n_end == "right", False, no_field, radial]


def ind_lenz_n_leaving(item: dict) -> list[bool]:
    """q4: coil axis along x, coil at the origin; magnet on the right (+x) with its N pole facing the coil,
    moving away to the right. Near an N pole the field points away from it, so at the coil it points −x:
    Φx(t) = −k/d², d = 2 + t (any growing distance). Viewer on the magnet side looks along −x, head up z.
    Options: clockwise seen from the magnet; counter-clockwise; no induced current; keeps flipping; cannot tell."""
    d = 2 + t
    phi_x = -k / d**2
    b_ind = _induced_axis_field(phi_x)
    sense = _sense_seen(b_ind, -EAST, UP)
    rate = sp.diff(phi_x, t)
    no_current = sp.simplify(rate) == 0
    flips = not (sp.simplify(rate).is_positive or sp.simplify(rate).is_negative)  # sign fixed for all t ≥ 0
    return [sense == "cw", sense == "ccw", no_current, flips, False]


def ind_lenz_s_approach_pole(item: dict) -> list[bool]:
    """q5: coil axis along x; magnet on the right with its S pole facing the coil, moving toward it.
    Near an S pole the field points toward it, so at the coil it points +x: Φx = k/d², d = 3 − t (t < 3).
    The induced field inside the coil gives the coil's poles: field lines leave the coil at its N end.
    The end facing the magnet is the +x end. Like poles repel, unlike poles attract.
    Options (facing end, force): (N, attract), (N, repel), (S, attract), (S, repel), (no poles, no force)."""
    d = 3 - t
    phi_x = k / d**2
    b_ind = _induced_axis_field(phi_x)
    if b_ind.norm() == 0:
        facing = None
    else:
        facing = "N" if b_ind.dot(EAST) > 0 else "S"  # field inside points toward the N end
    magnet_facing = "S"
    force = None if facing is None else ("repel" if facing == magnet_facing else "attract")
    opts = [("N", "attract"), ("N", "repel"), ("S", "attract"), ("S", "repel"), (None, None)]
    return [(facing, force) == o for o in opts]


def ind_situations(item: dict) -> list[bool]:
    """q3: which situations make an induced current in the closed coil (at the instant described)?
    Each is modelled by Φ(t) through the coil and checked for dΦ/dt ≠ 0 at t = 0.
    (1) magnet resting inside the coil: Φ = Φ0.
    (2) magnet pushed in: distance x = 3 − t, Φ = k/(1 + x²).
    (3) coil moved toward a resting magnet: same relative distance 3 − t (only relative motion matters).
    (4) the switch of a neighbouring coil has just been closed: its current rises, i = 1 − e^(−t), Φ ∝ i.
    (5) the neighbouring coil carries a steady direct current: i = i0, Φ ∝ i."""
    phi0, i0 = sp.Symbol("Phi0", positive=True), sp.Symbol("i0", positive=True)
    x = 3 - t
    models = [
        phi0 + 0 * t,
        k / (1 + x**2),
        k / (1 + x**2),
        k * (1 - sp.exp(-t)),
        k * i0 + 0 * t,
    ]
    return [sp.simplify(sp.diff(m, t).subs(t, 0)) != 0 for m in models]


def ind_pass_through(item: dict) -> list[bool]:
    """q6: a bar magnet is held fixed and a coil moves at constant speed v along its axis, sliding on over
    the N-pole end and off at the S-pole end. Only the relative position matters, so model (qualitative
    shape): Φ(t) = p·exp(−(v(t − t0))²), t0 = the instant the coil's centre passes the magnet's centre,
    p = +1 for this pole order, p = −1 with the poles swapped (same entry end); induced current
    I = −dΦ/dt (sign convention fixed; only signs and comparisons matter).
    (1) current while sliding on and while coming off has opposite signs;
    (2) the current is largest at the instant the coil's centre passes the magnet's centre;
    (3) a faster coil gives a larger peak current;
    (4) a coil resting at the middle of the magnet gives no current;
    (5) with the poles swapped, the current while sliding on flows the same way."""
    v, t0 = sp.symbols("v t0", positive=True)
    tt = sp.Symbol("tt", real=True)

    def current(p, speed):
        phi = p * sp.exp(-((speed * (tt - t0)) ** 2))
        return -sp.diff(phi, tt)

    def peak(speed):
        i = current(1, speed)
        crit = sp.solve(sp.diff(i, tt), tt)
        return sp.Max(*[sp.Abs(sp.simplify(i.subs(tt, c))) for c in crit])

    i_n = current(1, v)
    entering, leaving = t0 - 1 / (2 * v), t0 + 1 / (2 * v)
    s1 = bool(sp.simplify(i_n.subs(tt, entering) * i_n.subs(tt, leaving)) < 0)
    at_centre = sp.simplify(i_n.subs(tt, t0))
    s2 = bool(sp.simplify(sp.Abs(at_centre) - peak(v)) >= 0)
    s3 = bool(sp.simplify(peak(2) - peak(1)) > 0)
    s4 = sp.diff(sp.Symbol("Phi0") + 0 * tt, tt) == 0
    i_s = current(-1, v)
    s5 = bool(sp.simplify(i_n.subs(tt, entering) * i_s.subs(tt, entering)) > 0)
    return [s1, s2, s3, s4, s5]


# Facts table for q7. Each fact cites where it is stated in the project's sources.
FACTS = {
    # nat:PKc-Vc-3 keyConcepts: "Review from 國中: current produces a magnetic field; Ampère's right-hand rule"
    "ampere-rule-gives-current-field-direction": True,
    # nat:PKc-Vc-3 keyConcepts: Faraday's law is about induction; the magnetic effect of a current is the
    # separate first item ("current produces a magnetic field"), not Faraday's law.
    "faraday-law-says-every-current-has-field": False,
    # research physics common_misconceptions[6].correct_idea: the induced current's field OPPOSES THE CHANGE
    # in flux, so when the flux decreases it points the same way as the original field: not "always opposite".
    "lenz-induced-field-always-opposite": False,
    # nat:PKc-Vc-4 keyConcepts: "Maxwell unified all EM laws into one set of equations"; nat:PKc-Vc-3:
    # "a changing electric field produces a magnetic field" (moving/changing fields, not only charges at rest).
    "maxwell-only-static-charges": False,
    # research physics verification.corrections[5]: "冷次 does not appear anywhere in the 自然領綱".
    "lenz-named-in-required-curriculum": False,
}


def ind_history_laws(item: dict) -> list[bool]:
    """q7: which pairing of a law or person with its content is correct? Options in order:
    Faraday's law — every current has a magnetic field; Ampère's right-hand rule — direction of the field
    made by a current; Lenz's law — induced field always opposite to the magnet's field; Maxwell — studied
    only forces between charges at rest; Lenz's law — listed in the 必修物理 learning content."""
    keys = [
        "faraday-law-says-every-current-has-field",
        "ampere-rule-gives-current-field-direction",
        "lenz-induced-field-always-opposite",
        "maxwell-only-static-charges",
        "lenz-named-in-required-curriculum",
    ]
    return [FACTS[key] for key in keys]
