"""Checks for src/data/items/math/x-complex-numbers.yaml (分科 advanced tool: complex numbers and ω).

Each function recomputes its item's answer from the mathematics with SymPy; none reads item["answer"].
Every remainder found "by ω" (or by i) is cross-checked against exact polynomial division (sp.div),
so a check never trusts the shortcut it is testing. `chapter_examples` asserts every number the lesson
pages state in their worked examples, figures and dialogues; it runs on import, so a wrong number in
the lesson text fails the harness even though no item points at it.
"""

from __future__ import annotations

import sympy as sp

x = sp.Symbol("x")
I = sp.I
W = (-1 + sp.sqrt(3) * I) / 2  # ω


def _eq(a, b) -> bool:
    return sp.simplify(sp.expand(a - b)) == 0


def _rem(f, g):
    _, r = sp.div(sp.Poly(f, x), sp.Poly(g, x))
    return sp.expand(r.as_expr())


def _rem_by_root(f, root):
    """Remainder of f ÷ (x² + px + q) for the non-real root `root`: write f(root) = a·root + b with a, b real.
    Since root is not real, a = Im f(root) / Im root and b = Re f(root) − a·Re root."""
    v = sp.expand(f.subs(x, root))
    re_v, im_v = sp.re(v), sp.im(v)
    a = sp.nsimplify(sp.simplify(im_v / sp.im(root)))
    b = sp.nsimplify(sp.simplify(re_v - a * sp.re(root)))
    return sp.expand(a * x + b)


def chapter_examples() -> None:
    # opening dialogue: x^2026 ÷ (x² + x + 1) leaves x; 2026 = 3·675 + 1
    assert 2026 == 3 * 675 + 1
    assert _rem(x**2026, x**2 + x + 1) == x
    # i: i² = −1, i³ = −i, i⁴ = 1, powers repeat every 4
    assert I**2 == -1 and I**3 == -I and I**4 == 1
    # worked example: (2 + 3i)(1 − 2i) = 8 − i ; (2 + 3i)/(1 − 2i) = (−4 + 7i)/5
    assert _eq((2 + 3 * I) * (1 - 2 * I), 8 - I)
    q = (2 + 3 * I) / (1 - 2 * I)
    assert _eq(q, (-4 + 7 * I) / 5)
    assert _eq((1 - 2 * I) * (1 + 2 * I), 5)
    assert _eq((2 + 3 * I) * (1 + 2 * I), -4 + 7 * I)
    # alternative: (1 − 2i)(x + yi) = 2 + 3i ⇔ x + 2y = 2, −2x + y = 3
    u, v = sp.symbols("u v", real=True)
    prod = sp.expand((1 - 2 * I) * (u + v * I))
    assert _eq(sp.re(prod), u + 2 * v) and _eq(sp.im(prod), v - 2 * u)
    sol = sp.solve([u + 2 * v - 2, v - 2 * u - 3], [u, v])
    assert sol == {u: sp.Rational(-4, 5), v: sp.Rational(7, 5)}
    # addition example: (2 + 3i) + (1 − 2i) = 3 + i, as vectors (2, 3) + (1, −2) = (3, 1)
    assert _eq((2 + 3 * I) + (1 - 2 * I), 3 + I)
    # later perspective: i(a + bi) = −b + ai; same length, slopes b/a and −a/b multiply to −1
    ar, br = sp.symbols("a_r b_r", real=True, nonzero=True)
    assert _eq(I * (ar + br * I), -br + ar * I)
    assert _eq((br / ar) * (-ar / br), -1)
    assert _eq(sp.Abs(-br + ar * I) ** 2, ar**2 + br**2)
    # roots check in the text: (−1 + 2i)² + 2(−1 + 2i) + 5 = (1 − 4i − 4) + (−2 + 4i) + 5 = 0
    assert _eq((-1 + 2 * I) ** 2, 1 - 4 * I - 4) and _eq((1 - 4 * I - 4) + (-2 + 4 * I) + 5, 0)
    # absolute value and conjugate of 2 + 3i
    assert sp.Abs(2 + 3 * I) == sp.sqrt(13)
    assert sp.conjugate(2 + 3 * I) == 2 - 3 * I
    assert _eq((2 + 3 * I) * (2 - 3 * I), 13)
    # |z − w| as distance: |(2 + 3i) − (1 − 2i)| = |1 + 5i| = √26
    assert sp.Abs((2 + 3 * I) - (1 - 2 * I)) == sp.sqrt(26)
    # roots of x² + 2x + 5: discriminant −16, roots −1 ± 2i, product 5 = |root|²
    assert sp.discriminant(x**2 + 2 * x + 5, x) == -16
    assert set(sp.solve(x**2 + 2 * x + 5, x)) == {-1 + 2 * I, -1 - 2 * I}
    assert sp.Abs(-1 + 2 * I) ** 2 == 5
    # figure: x² + 2x + c (c ≥ 1) has roots −1 ± i√(c − 1) and |root|² = c
    c = sp.Symbol("c", positive=True)
    for r in (-1 + I * sp.sqrt(c - 1), -1 - I * sp.sqrt(c - 1)):
        assert _eq(r**2 + 2 * r + c, 0)
    assert _eq((-1) ** 2 + (c - 1), c)
    # conjugate-root example: x³ − x² + 2 has the root 1 + i; x² − 2x + 2 is a factor, the real root is −1
    f3 = x**3 - x**2 + 2
    assert _eq(f3.subs(x, 1 + I), 0) and _eq(f3.subs(x, 1 - I), 0)
    assert _eq(sp.expand((x - (1 + I)) * (x - (1 - I))), x**2 - 2 * x + 2)
    assert _eq(sp.expand((x**2 - 2 * x + 2) * (x + 1)), f3)
    # ω facts
    assert _eq(W**2 + W + 1, 0)
    assert _eq(W**3, 1)
    assert _eq(W**2, sp.conjugate(W)) and _eq(W**2, (-1 - sp.sqrt(3) * I) / 2)
    assert sp.simplify(sp.Abs(W)) == 1
    assert sp.discriminant(x**2 + x + 1, x) == -3
    assert _eq(sp.expand((x - 1) * (x**2 + x + 1)), x**3 - 1)
    # figure: 1, ω, ω² are the vertices of an equilateral triangle with side √3 on the unit circle
    assert all(sp.simplify(sp.Abs(p - q)) == sp.sqrt(3) for p, q in ((1, W), (W, W**2), (W**2, 1)))
    assert _eq(sp.re(W), sp.Rational(-1, 2)) and _eq(sp.im(W), sp.sqrt(3) / 2)
    # figure (parabola view): x² + 2x + c = (x + 1)² + (c − 1), vertex (−1, c − 1)
    assert _eq((x + 1) ** 2 + (c - 1), x**2 + 2 * x + c)
    # √−16 = 4i under the convention √(−k) = √k·i for k > 0; −1 + 2i = (−2 + 4i)/2
    assert _eq(sp.sqrt(-16), 4 * I) and _eq((-2 + 4 * I) / 2, -1 + 2 * I)
    # StudentAsks: i·i = −1, while √(−1)·√(−1) "=" √1 = 1 would be wrong
    assert _eq(sp.sqrt(-1) * sp.sqrt(-1), -1) and sp.sqrt(1) == 1
    # ω powers cycle 1, ω, ω² (figure slider n = 0..8); ω^2026 = ω
    assert _eq(W**2026, W)
    for n in range(9):
        assert _eq(W**n, W ** (n % 3))
    # worked example: x^20 + 3x^10 + 2 ÷ (x² + x + 1) leaves 2x + 1
    f = x**20 + 3 * x**10 + 2
    assert 20 % 3 == 2 and 10 % 3 == 1
    assert _eq(f.subs(x, W), 2 * W + 1)
    assert _eq(W**2 + 3 * W + 2, 2 * W + 1)
    assert _rem(f, x**2 + x + 1) == 2 * x + 1
    assert _rem_by_root(f, W) == 2 * x + 1
    # 10年級 way: x^20 − x² and x^10 − x are multiples of x³ − 1, hence of x² + x + 1
    assert _rem(x**20 - x**2, x**3 - 1) == 0 and _rem(x**10 - x, x**3 - 1) == 0
    assert _rem(x**2 + 3 * x + 2, x**2 + x + 1) == 2 * x + 1
    assert _eq((x**2 + 3 * x + 2) - (x**2 + x + 1), 2 * x + 1)
    # worked example with i: x^10 + x^7 + 1 ÷ (x² + 1) leaves −x
    g = x**10 + x**7 + 1
    assert I**10 == -1 and I**7 == -I
    assert _eq(g.subs(x, I), -I)
    assert _rem(g, x**2 + 1) == -x
    assert _rem_by_root(g, I) == -x
    # 10年級 way for it: x² ≡ −1, so x^10 = (x²)^5 ≡ −1 and x^7 = x·(x²)^3 ≡ −x
    assert _rem(x**10 + 1, x**2 + 1) == 0 and _rem(x**7 + x, x**2 + 1) == 0


chapter_examples()


def cx_turn_i_fourth(item: dict) -> list[bool]:
    """q-turn: i² = −1, so i⁴ = ? Options −1, 1, i, −i, 0."""
    v = (I**2) ** 2
    return [_eq(v, o) for o in (-1, 1, I, -I, 0)]


def cx_product(item: dict) -> list[bool]:
    """q1: (3 − i)(2 + i). Options 7 + i, 5 + i, 7 − i, 5 + 5i, 6 − i."""
    v = sp.expand((3 - I) * (2 + I))
    return [_eq(v, o) for o in (7 + I, 5 + I, 7 - I, 5 + 5 * I, 6 - I)]


def cx_quotient(item: dict) -> tuple:
    """q2: (4 + 7i)/(2 + i) = a + bi → (a, b)."""
    v = sp.simplify((4 + 7 * I) / (2 + I))
    a, b = sp.re(v), sp.im(v)
    assert _eq((a + b * I) * (2 + I), 4 + 7 * I)
    return (sp.Integer(a), sp.Integer(b))


def cx_plane_facts(item: dict) -> list[bool]:
    """q3: z = 3 − 4i. (1) |z| = 5 (2) z̄ = −3 + 4i (3) z·z̄ = 25 (4) z is in quadrant II (5) z² = −7 − 24i."""
    z = 3 - 4 * I
    re_z, im_z = sp.re(z), sp.im(z)
    return [
        sp.Abs(z) == 5,
        _eq(sp.conjugate(z), -3 + 4 * I),
        _eq(z * sp.conjugate(z), 25),
        bool(re_z < 0 and im_z > 0),
        _eq(z**2, -7 - 24 * I),
    ]


def cx_conjugate_coefficients(item: dict) -> tuple:
    """q4: real b, c and x² + bx + c = 0 has the root 3 + 2i → (b, c), solved from real and imaginary parts."""
    b, c = sp.symbols("b c", real=True)
    val = sp.expand((3 + 2 * I) ** 2 + b * (3 + 2 * I) + c)
    sol = sp.solve([sp.re(val), sp.im(val)], [b, c], dict=True)[0]
    poly = x**2 + sol[b] * x + sol[c]
    assert _eq(poly.subs(x, 3 - 2 * I), 0)  # the conjugate is the other root
    return (sol[b], sol[c])


def cx_real_cubic_root(item: dict) -> list[bool]:
    """q5: a real-coefficient cubic f with leading coefficient 1 has f(2 + i) = 0. Which must hold?
    (1) f(2 − i) = 0 (2) x² − 4x + 5 is a factor (3) f has at least one real root
    (4) f has three distinct real roots (5) f(x) = 0 has exactly two real roots.
    General f = x³ + ax² + bx + c with a real and b, c forced real by Re f(2+i) = Im f(2+i) = 0."""
    a, b, c = sp.symbols("a b c", real=True)
    f = x**3 + a * x**2 + b * x + c
    val = sp.expand(f.subs(x, 2 + I))
    sol = sp.solve([sp.re(val), sp.im(val)], [b, c], dict=True)[0]
    F = sp.expand(f.subs(sol))  # every such cubic, parametrised by the real a
    s1 = _eq(F.subs(x, 2 - I), 0)
    q, r = sp.div(sp.Poly(F, x), sp.Poly(x**2 - 4 * x + 5, x))
    s2 = r.is_zero
    lin = q.as_expr()  # the cofactor is linear with real coefficients: one real root
    s3 = sp.Poly(lin, x).degree() == 1 and all(co.is_real for co in sp.Poly(lin, x).all_coeffs())
    # the quadratic factor has discriminant 16 − 20 < 0, so the cubic has exactly one real root (counted with multiplicity)
    assert sp.discriminant(x**2 - 4 * x + 5, x) < 0
    real_root_count = len(sp.solveset(x**2 - 4 * x + 5, x, domain=sp.S.Reals)) + 1  # + the linear factor's root
    s4 = real_root_count == 3
    s5 = real_root_count == 2
    return [s1, s2, s3, s4, s5]


def cx_omega_remainder(item: dict) -> tuple:
    """q6: remainder of x³¹ + 2x¹⁴ + x³ ÷ (x² + x + 1), written ax + b → (a, b)."""
    f = x**31 + 2 * x**14 + x**3
    r = _rem(f, x**2 + x + 1)
    assert _rem_by_root(f, W) == r
    return (r.coeff(x, 1), r.coeff(x, 0))


def cx_i_remainder(item: dict) -> list[bool]:
    """q7: remainder of x¹³ + 3x⁶ + x ÷ (x² + 1). Options 2x − 3, 2x + 3, −3, x − 3, 3x − 2."""
    f = x**13 + 3 * x**6 + x
    r = _rem(f, x**2 + 1)
    assert _rem_by_root(f, I) == r
    return [_eq(r, o) for o in (2 * x - 3, 2 * x + 3, sp.Integer(-3), x - 3, 3 * x - 2)]


def cx_omega_power(item: dict) -> list[bool]:
    """q8: ω = (−1 + √3 i)/2. (1 + ω²)⁴ = ? Options 1, −1, ω, ω², −ω."""
    v = sp.expand((1 + W**2) ** 4)
    return [_eq(v, o) for o in (1, -1, W, W**2, -W)]
