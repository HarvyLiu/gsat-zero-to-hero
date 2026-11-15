"""Checks for src/data/items/math/x-polar-form-rotation.yaml (分科 advanced tool, 數A path: polar form,
De Moivre's theorem and rotation by multiplication; N-12甲-3, not on the 學測).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Every rotation found by complex multiplication is cross-checked with the 11A rotation matrix, and every
De Moivre power with plain repeated multiplication (expand), so the two routes the chapter shows side by
side are both machine-checked. Angles are exact: degrees are converted with sp.pi / 180.
"""

from __future__ import annotations

import sympy as sp

DEG = sp.pi / 180
I = sp.I
th = sp.symbols("theta", real=True)


def _same(a, b) -> bool:
    """Exact when SymPy can simplify the difference to 0; otherwise (powers of cos 48° and the like,
    which SymPy leaves unsimplified) the difference must vanish to 50 significant digits."""
    d = sp.expand(sp.sympify(a) - sp.sympify(b))
    if abs(sp.N(d, 60)) > sp.Float("1e-50"):
        return False
    if sp.count_ops(d) > 80:  # too large for simplify in reasonable time: the 50-digit test stands
        return True
    return sp.simplify(d) == 0


def _cis(deg) -> sp.Expr:
    return sp.cos(deg * DEG) + I * sp.sin(deg * DEG)


def _rot_matrix(deg) -> sp.Matrix:
    t = deg * DEG
    return sp.Matrix([[sp.cos(t), -sp.sin(t)], [sp.sin(t), sp.cos(t)]])


def _rotate(p: tuple, deg, center: tuple = (0, 0)) -> tuple[sp.Expr, sp.Expr]:
    """Rotate point p about center counterclockwise by deg degrees: by complex multiplication,
    asserted equal to the rotation-matrix route."""
    z, c = p[0] + I * p[1], center[0] + I * center[1]
    w = sp.expand((z - c) * _cis(deg) + c)
    by_complex = (sp.simplify(sp.re(w)), sp.simplify(sp.im(w)))
    v = _rot_matrix(deg) * sp.Matrix([p[0] - center[0], p[1] - center[1]]) + sp.Matrix(center)
    assert _same(v[0], by_complex[0]) and _same(v[1], by_complex[1])
    return by_complex


def _de_moivre(r, deg, n) -> sp.Expr:
    """[r cis(deg)]^n by De Moivre, asserted equal to expanding the n-th power directly."""
    by_dm = sp.expand(r**n * _cis(n * deg))
    direct = sp.expand((r * _cis(deg)) ** n)
    assert _same(by_dm, direct)
    return by_dm


def _worked_examples() -> None:
    """The chapter's worked examples, every way shown (both locales use the same numbers)."""
    # polar forms: 1 + √3 i = 2 cis 60°, −2 + 2i = 2√2 cis 135°
    assert _same(2 * _cis(60), 1 + sp.sqrt(3) * I)
    assert _same(2 * sp.sqrt(2) * _cis(135), -2 + 2 * I)
    assert _same(sp.Abs(-2 + 2 * I), 2 * sp.sqrt(2)) and _same(sp.arg(-2 + 2 * I), 135 * DEG)
    # product rule: lengths multiply, angles add (2 cis 60° · 2√2 cis 135° = 4√2 cis 195°)
    assert _same(sp.expand((1 + sp.sqrt(3) * I) * (-2 + 2 * I)), 4 * sp.sqrt(2) * _cis(195))
    # multiplying by i is a 90° turn: (3 + 2i)i = −2 + 3i
    assert sp.expand((3 + 2 * I) * I) == -2 + 3 * I
    # rotate P(2, 3) by 60°: ((2 − 3√3)/2, (2√3 + 3)/2), by complex number and by matrix
    x, y = _rotate((2, 3), 60)
    assert _same(x, (2 - 3 * sp.sqrt(3)) / 2) and _same(y, (2 * sp.sqrt(3) + 3) / 2)
    # equilateral triangle on A(1, 1), B(4, 2), counterclockwise: C = A + (B − A) cis 60°
    cx, cy = _rotate((4, 2), 60, center=(1, 1))
    assert _same(cx, (5 - sp.sqrt(3)) / 2) and _same(cy, (3 * sp.sqrt(3) + 3) / 2)
    A, B, C = sp.Matrix([1, 1]), sp.Matrix([4, 2]), sp.Matrix([cx, cy])
    d = lambda P, Q: sp.simplify((P - Q).dot(P - Q))
    assert _same(d(A, B), 10) and _same(d(B, C), 10) and _same(d(A, C), 10)
    # De Moivre: (1 + i)^8 = 16 and (1 + √3 i)^6 = 64, each also by direct expansion
    assert _same(_de_moivre(sp.sqrt(2), 45, 8), 16)
    assert _same(_de_moivre(2, 60, 6), 64)
    assert sp.expand((1 + I) ** 8) == 16 and sp.expand((1 + sp.sqrt(3) * I) ** 6) == 64
    # n = 2 recovers the double angle formulas
    sq = sp.expand((sp.cos(th) + I * sp.sin(th)) ** 2)
    assert sp.simplify(sp.re(sq) - sp.cos(2 * th)) == 0 and sp.simplify(sp.im(sq) - sp.sin(2 * th)) == 0
    # n = 3: real part = 4cos³θ − 3cosθ, imaginary part = 3sinθ − 4sin³θ, three ways:
    cube = sp.expand((sp.cos(th) + I * sp.sin(th)) ** 3)
    re3 = sp.expand(sp.re(cube).subs(sp.sin(th) ** 2, 1 - sp.cos(th) ** 2))
    im3 = sp.expand(sp.im(cube).subs(sp.cos(th) ** 2, 1 - sp.sin(th) ** 2))
    assert sp.simplify(re3 - (4 * sp.cos(th) ** 3 - 3 * sp.cos(th))) == 0
    assert sp.simplify(im3 - (3 * sp.sin(th) - 4 * sp.sin(th) ** 3)) == 0
    #   (a) De Moivre says these are cos 3θ and sin 3θ
    assert sp.simplify(sp.expand_trig(sp.cos(3 * th)) - re3) == 0
    assert sp.simplify(sp.expand_trig(sp.sin(3 * th)) - im3) == 0
    #   (b) the 11A route cos(2θ + θ) = cos2θ cosθ − sin2θ sinθ gives the same
    via_sum = (2 * sp.cos(th) ** 2 - 1) * sp.cos(th) - 2 * sp.sin(th) * sp.cos(th) * sp.sin(th)
    assert sp.simplify(via_sum - re3) == 0
    #   (c) spot check at θ = 30°: 4cos³30° − 3cos30° = 0 = cos 90°
    assert _same(4 * sp.cos(30 * DEG) ** 3 - 3 * sp.cos(30 * DEG), 0)
    # product of cis α and cis β, compared part by part, is the sum formulas (memory aid)
    a, b = sp.symbols("alpha beta", real=True)
    prod = sp.expand((sp.cos(a) + I * sp.sin(a)) * (sp.cos(b) + I * sp.sin(b)))
    assert sp.simplify(sp.re(prod) - sp.expand_trig(sp.cos(a + b))) == 0
    assert sp.simplify(sp.im(prod) - sp.expand_trig(sp.sin(a + b))) == 0
    # rotations about the origin commute: R(α)R(β) = R(β)R(α) = R(α + β), for symbolic α, β
    R = lambda t: sp.Matrix([[sp.cos(t), -sp.sin(t)], [sp.sin(t), sp.cos(t)]])
    target = R(a + b).applyfunc(sp.expand_trig)
    assert (R(a) * R(b) - target).applyfunc(sp.simplify) == sp.zeros(2)
    assert (R(b) * R(a) - target).applyfunc(sp.simplify) == sp.zeros(2)


def pr_turn_rotate_90(item: dict) -> list[bool]:
    """q-turn: P(3, 2) rotated 90° counterclockwise about the origin.
    Options (−2, 3), (2, −3), (−3, −2), (3, −2), (−3, 2)."""
    _worked_examples()
    img = _rotate((3, 2), 90)
    options = [(-2, 3), (2, -3), (-3, -2), (3, -2), (-3, 2)]
    return [_same(img[0], o[0]) and _same(img[1], o[1]) for o in options]


def pr_polar_form(item: dict) -> list[bool]:
    """q1: the polar form of −√3 + i. Options 2cis30°, 2cis150°, 2cis120°, √2 cis150°, 4cis150°."""
    z = -sp.sqrt(3) + I
    r, ang = sp.simplify(sp.Abs(z)), sp.simplify(sp.arg(z))
    assert r == 2 and _same(ang, 150 * DEG)
    options = [2 * _cis(30), 2 * _cis(150), 2 * _cis(120), sp.sqrt(2) * _cis(150), 4 * _cis(150)]
    return [_same(z, o) for o in options]


def pr_power_one_minus_i(item: dict) -> int:
    """q2: (1 − i)^10 = k i: k. 1 − i = √2 cis(−45°), so the power is 32 cis(−450°) = −32i."""
    by_dm = _de_moivre(sp.sqrt(2), -45, 10)
    assert sp.re(by_dm) == 0
    k = sp.im(by_dm)
    assert sp.expand((1 - I) ** 10) == k * I
    return int(k)


def pr_rotate_45(item: dict) -> tuple[int, int, int, int]:
    """q3: P(5, 1) rotated 45° about the origin is (a√b, c√d) = (2√2, 3√2) → (a, b, c, d)."""
    x, y = _rotate((5, 1), 45)
    # read the simplest-radical form a√b, c√d off the computed coordinates (2 is square-free)
    a, c = sp.nsimplify(sp.simplify(x / sp.sqrt(2))), sp.nsimplify(sp.simplify(y / sp.sqrt(2)))
    assert a.is_Integer and c.is_Integer and _same(a * sp.sqrt(2), x) and _same(c * sp.sqrt(2), y)
    assert _same(x, 2 * sp.sqrt(2)) and _same(y, 3 * sp.sqrt(2))
    return (int(a), 2, int(c), 2)


def pr_square_vertex(item: dict) -> tuple[int, int]:
    """q4: square ABCD, vertices counterclockwise, A(1, −2), B(5, 1): C = B + (B − A)·i."""
    cx, cy = _rotate((1, -2), -90, center=(5, 1))  # C is A turned −90° about B
    via_i = sp.expand((5 + I) + ((5 + I) - (1 - 2 * I)) * I)
    assert _same(cx, sp.re(via_i)) and _same(cy, sp.im(via_i))
    A, B, C = sp.Matrix([1, -2]), sp.Matrix([5, 1]), sp.Matrix([cx, cy])
    D = A + (C - B)
    sides = [(B - A), (C - B), (D - C), (A - D)]
    assert all(_same(s.dot(s), 25) for s in sides)
    assert all(_same(sides[k].dot(sides[k + 1]), 0) for k in range(3))
    # counterclockwise: the cross product of AB and BC is positive
    assert (sides[0][0] * sides[1][1] - sides[0][1] * sides[1][0]) > 0
    return (int(cx), int(cy))


def pr_cos_triple(item: dict) -> tuple[int, int]:
    """q5: cos θ = 2/3: cos 3θ = 4cos³θ − 3cos θ as p/q → (p, q); cross-checked with cos(3·acos(2/3))."""
    c = sp.Rational(2, 3)
    v = 4 * c**3 - 3 * c
    assert sp.simplify(sp.expand_trig(sp.cos(3 * sp.acos(c))) - v) == 0
    v = sp.Rational(v)  # a SymPy Rational is stored in lowest terms, as the stem asks
    assert sp.igcd(v.p, v.q) == 1
    return (int(v.p), int(v.q))


def pr_product_statements(item: dict) -> list[bool]:
    """q6: z = 2cis20°, w = cis40°. Statements: |zw| = 2; zw = 1 + √3 i; z³ = 6cis60°; z⁹ = 512; w⁹ = 1."""
    z, w = 2 * _cis(20), _cis(40)
    zw = sp.expand(z * w)
    z3 = _de_moivre(2, 20, 3)
    z9 = _de_moivre(2, 20, 9)
    w9 = _de_moivre(1, 40, 9)
    return [
        _same(sp.Abs(zw), 2),
        _same(zw, 1 + sp.sqrt(3) * I),
        _same(z3, 6 * _cis(60)),
        _same(z9, 512),
        _same(w9, 1),
    ]


def pr_return_count(item: dict) -> int:
    """q7: the least n ≥ 1 with (cis 48°)^n = 1, i.e. 48n a multiple of 360; also by brute force."""
    n = 360 // sp.igcd(48, 360)
    first = next(k for k in range(1, 400) if abs(sp.N(_cis(48) ** k - 1, 60)) < sp.Float("1e-50"))
    assert _same(_de_moivre(1, 48, n), 1)
    assert first == n
    return int(n)
