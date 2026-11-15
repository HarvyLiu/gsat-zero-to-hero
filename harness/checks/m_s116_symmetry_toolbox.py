"""Checks for src/data/items/math/s116-symmetry-toolbox.yaml (116 sprint, toolbox: symmetry of graphs).

Each function recomputes its item's answer from the geometry with SymPy; none reads item["answer"].
Point images come from sympy.geometry reflections (not from the swap/sign rules the chapter teaches), and
graph symmetry is decided by `_graph_symmetric` below.
"""

from __future__ import annotations

import sympy as sp
from sympy.geometry import Line, Point

x, y = sp.symbols("x y", real=True)

X_AXIS = Line(Point(0, 0), Point(1, 0))
Y_AXIS = Line(Point(0, 0), Point(0, 1))
DIAG = Line(Point(0, 0), Point(1, 1))  # the line y = x


def _origin(p: Point) -> Point:
    """Point symmetry about the origin: a half-turn about (0, 0)."""
    return p.rotate(sp.pi, Point(0, 0))


def _map(kind: str):
    """The plane map for one of the four symmetries, as (x, y) -> (x', y') built from geometry."""
    def f(px, py):
        p = Point(px, py, evaluate=False)
        q = _origin(p) if kind == "origin" else p.reflect({"x": X_AXIS, "y": Y_AXIS, "diag": DIAG}[kind])
        return sp.simplify(q.x), sp.simplify(q.y)
    return f


def _graph_symmetric(f: sp.Expr, kind: str) -> bool:
    """Is the graph f(x, y) = 0 symmetric under `kind`?

    Symmetric when f∘T equals f or −f identically (same zero set). Otherwise a counterexample is searched:
    a real point (x0, y0) on the graph whose image is off the graph. If neither is found the check fails loudly.
    """
    tx, ty = _map(kind)(x, y)
    g = f.subs({x: tx, y: ty}, simultaneous=True)
    if sp.simplify(g - f) == 0 or sp.simplify(g + f) == 0:
        return True
    for x0 in [sp.Rational(n, 2) for n in range(-12, 13)]:
        for y0 in sp.solveset(sp.Eq(f.subs(x, x0), 0), y, domain=sp.S.Reals):
            if not y0.is_real:
                continue
            ix, iy = _map(kind)(x0, y0)
            if sp.simplify(f.subs({x: ix, y: iy}, simultaneous=True)) != 0:
                return False
    raise AssertionError(f"could not decide {kind}-symmetry of {f} = 0")


def _on_graph(f: sp.Expr, px, py) -> bool:
    return sp.simplify(f.subs({x: px, y: py}, simultaneous=True)) == 0


# ---------- s116-symmetry-toolbox ----------

def sym_turn_y_axis(item: dict) -> list[bool]:
    """q-turn: the point symmetric to P(4, 1) about the y-axis.
    Options: (−4, 1); (4, −1); (−4, −1); (1, 4); (−1, −4)."""
    img = Point(4, 1).reflect(Y_AXIS)
    options = [Point(-4, 1), Point(4, -1), Point(-4, -1), Point(1, 4), Point(-1, -4)]
    return [img.equals(o) for o in options]


def sym_point_about_diag(item: dict) -> list[bool]:
    """q1: the point symmetric to Q(−5, 2) about the line y = x.
    Options: (2, −5); (−2, 5); (5, −2); (5, 2); (−5, −2)."""
    img = Point(-5, 2).reflect(DIAG)
    options = [Point(2, -5), Point(-2, 5), Point(5, -2), Point(5, 2), Point(-5, -2)]
    return [img.equals(o) for o in options]


def sym_abs_diamond(item: dict) -> list[bool]:
    """q2: about the graph |x| + 2|y| = 4. Options: symmetric about the x-axis; about the y-axis; about the
    origin; about the line y = x; the graph passes through (0, 2)."""
    f = sp.Abs(x) + 2 * sp.Abs(y) - 4
    return [
        _graph_symmetric(f, "x"),
        _graph_symmetric(f, "y"),
        _graph_symmetric(f, "origin"),
        _graph_symmetric(f, "diag"),
        _on_graph(f, 0, 2),
    ]


def sym_two_imply_third(item: dict) -> sp.Integer:
    """q3: a graph symmetric about the y-axis and the origin passes through (3, 5); it must also pass
    through (3, ①②). Apply the y-axis reflection, then the half-turn about the origin, and read the image."""
    p = _origin(Point(3, 5).reflect(Y_AXIS))
    assert p.x == 3  # the stem fixes the x-coordinate at 3
    assert not p.equals(Point(3, 5))  # the stem asks for ANOTHER point, not (3, 5) itself
    return sp.Integer(p.y)


def sym_which_origin(item: dict) -> list[bool]:
    """q4: which graph is symmetric about the origin?
    Options: y = x³ + x; y = x² + 1; y = x³ + 1; x = y²; y = |x|."""
    eqs = [y - (x**3 + x), y - (x**2 + 1), y - (x**3 + 1), x - y**2, y - sp.Abs(x)]
    return [_graph_symmetric(f, "origin") for f in eqs]
