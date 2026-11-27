"""Checks for src/data/items/inquiry/s116-sci-plot-and-working.yaml (116 sprint, science exam skills:
plotting and showing working; exam:nat-2a ... exam:nat-5a).

How the keys are recomputed (never from item["answer"]):
- Every function reads its numbers from BOTH stems (zh-tw and en), asserts that they agree, and recomputes
  with SymPy exact Rationals, so editing a stem number changes or breaks the check.
- Options are decided by code: each option is matched to exactly one entry of an encoded table of named
  results (the right one and the common mistakes), and only the right one is marked true.
- Axis placement, plot corrections and the scale choice come from the rule lists below.

Rules used, with their sources:
- Average rate over an interval = (later amount - earlier amount) / (later time - earlier time), unit =
  amount unit / time unit: chemistry/s116-rate-and-technology (反應速率, "從數據算出平均反應速率"; its worked
  example (1.52-0.84)/(4-2)).
- "Plot A against B" puts A on the vertical axis and B on the horizontal: physics/s116-physics-reasoning
  ("I 對 r 畫出來", I on the vertical axis); earth/s116-earth-layers-plates ("海底岩石年齡對距離", age on the
  vertical axis). In an experiment the manipulated variable usually goes on the horizontal axis:
  inquiry/s116-inq-argue-model. Standard convention; not a CEEC rubric text.
- Plot requirements (quantity and unit on each axis, an even scale, every point in the right place, join as
  the question asks; for measured data a line of best fit, not a zigzag): physics/s116-physics-reasoning
  (自己作圖時) and earth/s116-earth-data-items (作圖四件事).
- Scale rule (each large square worth 1, 2 or 5 times a power of 10, the smallest that fits): the chapter's
  own stated rule; standard practice, not a CEEC rubric text.
- Slope unit = vertical unit / horizontal unit: physics/s116-physics-reasoning; speed = distance / time:
  physics/s116-scales-units.
- Unit factors 1 g = 10^-3 kg, 1 cm = 10^-2 m (so 1 cm^3 = 10^-6 m^3), 1 min = 60 s: physics/s116-scales-units.
- Solubility measured against
  temperature: chemistry/s116-solutions.
- Written items must show calculations or reasons (slice verification.exam_format_verified); the q7 rubric
  awards each step of the working, as the chapter's four-step answer does.
"""

from __future__ import annotations

import re

from sympy import Rational as Q

# --- helpers ------------------------------------------------------------------------------------------


def _zh(item: dict) -> str:
    return item["text"]["zh-tw"]["stem"]


def _en(item: dict) -> str:
    return item["text"]["en"]["stem"]


def _opts(item: dict) -> tuple[list[str], list[str]]:
    zh, en = item["text"]["zh-tw"]["options"], item["text"]["en"]["options"]
    assert len(zh) == len(en), (zh, en)
    return zh, en


def _nums(s: str) -> list[Q]:
    """'0、32、48' or '0, 32, 48 and 60' -> exact Rationals."""
    return [Q(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]


def _value_option(zh: str, en: str):
    """'12' / '約18.7' (en 'about 18.7') -> (Rational, approximate?)."""
    approx_zh, approx_en = zh.startswith("約"), en.startswith("about ")
    assert approx_zh == approx_en, (zh, en)
    vz, ve = Q(zh.removeprefix("約")), Q(en.removeprefix("about "))
    assert vz == ve, (zh, en)
    return vz, approx_zh


def _matches(value: Q, opt: tuple[Q, bool]) -> bool:
    """An exact option must equal the value; an 'about' option must be the value rounded to 1 decimal and
    must not be exact."""
    v, approx = opt
    if approx:
        return value != v and abs(value - v) <= Q(1, 20)
    return value == v


def _decide(named: dict[str, Q], options: list[tuple[Q, bool]], right: str) -> list[bool]:
    """Every option must match exactly one named result; only the 'right' one is true."""
    out = []
    for o in options:
        hits = [k for k, v in named.items() if _matches(v, o)]
        assert len(hits) == 1, (o, hits)
        out.append(hits[0] == right)
    assert out.count(True) == 1
    return out


def _interval_results(times: list[Q], amounts: list[Q], a: Q, b: Q) -> dict[str, Q]:
    """The right average rate over [a, b] and the four mistakes the chapter names."""
    amt = dict(zip(times, amounts))
    first, last = times[0], times[-1]
    return {
        "right": (amt[b] - amt[a]) / (b - a),
        "from_zero": amt[b] / b,  # the amount at b divided by the time since 0
        "no_divide": amt[b] - amt[a],  # change in amount, not divided by the time
        "total_over_interval": amt[b] / (b - a),  # total so far over the interval length
        "whole_run": (amt[last] - amt[first]) / (last - first),  # an interval the question did not ask about
    }


# --- opening turn: gas collected, average rate between minute 1 and 3 ---------------------------------


def pw_turn_interval_rate(item: dict) -> list[bool]:
    tz, vz, az, bz = re.search(r"第([\d、]+)分鐘的氣體體積依序是([\d、]+)毫升。第(\d+)分鐘到第(\d+)分鐘", _zh(item)).groups()
    te, ve = re.search(r"at ([\d, and]+) minutes is ([\d, and]+) mL", _en(item)).groups()
    ae, be = re.search(r"Between minute (\d+) and minute (\d+)", _en(item)).groups()
    times, vols = _nums(tz), _nums(vz)
    assert (times, vols, Q(az), Q(bz)) == (_nums(te), _nums(ve), Q(ae), Q(be)) and len(times) == len(vols)
    named = _interval_results(times, vols, Q(az), Q(bz))
    zh, en = _opts(item)
    return _decide(named, [_value_option(z, e) for z, e in zip(zh, en)], "right")


# --- q1: seedling height, average growth per day between day 3 and day 9 -------------------------------


def pw_seedling_rate(item: dict) -> list[bool]:
    tz, hz, az, bz = re.search(r"第([\d、]+)天的高度依序是([\d、]+)公分。第(\d+)天到第(\d+)天", _zh(item)).groups()
    te, he = re.search(r"on days ([\d, and]+) it is ([\d, and]+) cm tall", _en(item)).groups()
    ae, be = re.search(r"Between day (\d+) and day (\d+)", _en(item)).groups()
    times, heights = _nums(tz), _nums(hz)
    assert (times, heights, Q(az), Q(bz)) == (_nums(te), _nums(he), Q(ae), Q(be)) and len(times) == len(heights)
    named = _interval_results(times, heights, Q(az), Q(bz))
    zh, en = _opts(item)
    return _decide(named, [_value_option(z, e) for z, e in zip(zh, en)], "right")


# --- axis placement: "plot A against B" -> A vertical, B horizontal -----------------------------------


def _against(zh_pattern: str, en_pattern: str, item: dict) -> tuple[str, str, str, str]:
    """(A, B) in zh and en from 'A對B' / 'A against B'."""
    a_zh, b_zh = re.search(zh_pattern, _zh(item)).groups()
    a_en, b_en = re.search(en_pattern, _en(item)).groups()
    return a_zh, b_zh, a_en, b_en


def _axes_decide(item: dict, a_zh: str, b_zh: str, table: list[dict]) -> list[bool]:
    """table: one entry per option, with the zh fragments that must appear in it and the placement it
    describes ('x', 'y' quantity names, or a special kind). Right iff x == B and y == A."""
    zh, _ = _opts(item)
    assert len(table) == len(zh)
    out = []
    for opt, t in zip(zh, table):
        for frag in t["must"]:
            assert frag in opt, (frag, opt)
        out.append(t.get("x") == b_zh and t.get("y") == a_zh and t.get("kind") is None)
    assert out.count(True) == 1
    return out


def pw_turn_axes(item: dict) -> list[bool]:
    a_zh, b_zh, a_en, b_en = _against(r"畫出(.+?)對(.+?)的關係圖", r"plot (\w+) against (\w+)", item)
    assert (a_zh, b_zh, a_en, b_en) == ("距離", "年齡", "distance", "age")
    table = [
        {"must": ["年齡（百萬年）放橫軸", "距離（公里）放縱軸"], "x": "年齡", "y": "距離"},
        {"must": ["距離（公里）放橫軸", "年齡（百萬年）放縱軸"], "x": "距離", "y": "年齡"},
        {"must": ["都可以"], "kind": "either"},  # ignores the question's wording
        {"must": ["數值比較大", "放橫軸"], "x": "距離", "y": "年齡", "kind": "by-size"},
        {"must": ["都放縱軸"], "kind": "both-vertical"},
    ]
    return _axes_decide(item, a_zh, b_zh, table)


def pw_solubility_axes(item: dict) -> list[bool]:
    a_zh, b_zh, a_en, b_en = _against(r"畫出(.+?)對(.+?)的關係圖", r"graph of (\w+) against (\w+)", item)
    assert (a_zh, b_zh, a_en, b_en) == ("溶解度", "溫度", "solubility", "temperature")
    table = [
        {"must": ["橫軸是溫度", "縱軸是溶解度"], "x": "溫度", "y": "溶解度"},
        {"must": ["橫軸是溶解度", "縱軸是溫度"], "x": "溶解度", "y": "溫度"},
        {"must": ["都可以"], "kind": "either"},
        {"must": ["同一條縱軸"], "kind": "both-vertical"},
        {"must": ["測量的順序", "縱軸是溫度"], "x": "順序", "y": "溫度"},
    ]
    # Consistency with the design: temperature is the changed quantity, so it is also the manipulated
    # variable that usually goes on the horizontal axis (inquiry/s116-inq-argue-model).
    assert "不同溫度下測量" in _zh(item) and "at different temperatures" in _en(item)
    return _axes_decide(item, a_zh, b_zh, table)


# --- scale rule ---------------------------------------------------------------------------------------

NICE = sorted(m * Q(10) ** k for k in range(-3, 7) for m in (1, 2, 5))


def scale_step(largest: Q, squares: int) -> Q:
    """Smallest 1/2/5 x 10^k per large square such that `squares` squares reach the largest value."""
    step = next(s for s in NICE if s * squares >= largest)
    assert largest / (step * squares) >= Q(1, 2)  # the data use at least half the axis
    return step


def pw_rainfall_scale(item: dict) -> int:
    mz, nz = re.search(r"最大值是(\d+)毫米。答案卷方格紙的縱軸有(\d+)大格", _zh(item)).groups()
    me, ne = re.search(r"largest value is (\d+) mm\. The vertical axis of the answer-sheet grid has (\d+) large squares", _en(item)).groups()
    assert (mz, nz) == (me, ne)
    step = scale_step(Q(mz), int(nz))
    assert step.q == 1 and 10 <= step < 100  # two cells
    return int(step)


# --- q4: what in the student's cart plot needs correcting -----------------------------------------------

PLOT_REQUIREMENTS = ("axes_labelled", "scale_rule", "points_correct", "join_as_asked")


def pw_cart_plot_fixes(item: dict) -> list[bool]:
    largest, squares, per = re.search(r"位置最大是(\d+)公尺.*?縱軸共(\d+)大格，每大格(\d+)公尺", _zh(item)).groups()
    le, se, pe = re.search(r"largest position is (\d+) m.*?vertical axis has (\d+) large squares at (\d+) m each", _en(item)).groups()
    assert (largest, squares, per) == (le, se, pe)
    # The student's plot, as the stem describes it (both locales checked for each feature).
    z, e = _zh(item), _en(item)
    assert "橫軸寫了「時間（s）」，縱軸只寫數字" in z and 'horizontal axis is labelled "time (s)" and the vertical axis has numbers only' in e
    assert "把(3 s, 17 m)描成了(4 s, 17 m)" in z and "(3 s, 17 m) was plotted at (4 s, 17 m)" in e
    assert "用線段把相鄰的點一一連起來" in z and "joined by line segments one after another" in e
    assert "畫出最適合的直線" in z and "the line of best fit" in e
    rule = scale_step(Q(largest), int(squares))
    plot = {
        "y_labelled": False,
        "x_labelled": True,
        "scale_ok": Q(per) == rule,
        "points_correct": False,
        "joined": "segments",
        "asked": "best-fit line",
    }
    alt = Q(3)  # option (2)'s proposed scale
    alt_ok = alt in NICE and alt * int(squares) >= Q(largest)
    zh, _ = _opts(item)
    assert "3公尺" in zh[1] and "刪掉" in zh[4]
    needs_fix = [
        not plot["y_labelled"],  # (1) add a quantity and unit to the vertical axis
        (not plot["scale_ok"]) and alt_ok,  # (2) change to 3 m per square
        not plot["points_correct"],  # (3) re-plot the misplaced point
        plot["joined"] != "best-fit line" and plot["asked"] == "best-fit line",  # (4) draw a line of best fit
        not plot["x_labelled"],  # (5) remove the horizontal label: only a fix if it were wrong, and it is not
    ]
    assert any(needs_fix)
    return needs_fix


# --- q5: slope of a position-time line, with its unit --------------------------------------------------


def pw_slope_with_unit(item: dict) -> list[bool]:
    pts_z = re.findall(r"\((\d+(?:\.\d+)?) s, (\d+(?:\.\d+)?) m\)", _zh(item))
    pts_e = re.findall(r"\((\d+(?:\.\d+)?) s, (\d+(?:\.\d+)?) m\)", _en(item))
    assert pts_z == pts_e and len(pts_z) == 2
    (x1, y1), (x2, y2) = [(Q(a), Q(b)) for a, b in pts_z]
    dx, dy = x2 - x1, y2 - y1
    named = {
        "right": (dy / dx, "m/s"),
        "reciprocal": (dx / dy, "s/m"),
        "no_divide": (dy, "m"),
        "wrong_unit": (dy / dx, "m"),
        "product": (dx * dy, "m·s"),
    }
    zh, en = _opts(item)
    out = []
    for z, e in zip(zh, en):
        mz = re.fullmatch(r"(約)?(\d+(?:\.\d+)?) (\S+)", z)
        me = re.fullmatch(r"(about )?(\d+(?:\.\d+)?) (\S+)", e)
        assert mz and me and Q(mz.group(2)) == Q(me.group(2)) and mz.group(3) == me.group(3) and bool(mz.group(1)) == bool(me.group(1))
        opt = (Q(mz.group(2)), bool(mz.group(1)))
        hits = [k for k, (v, u) in named.items() if u == mz.group(3) and _matches(v, opt)]
        assert len(hits) == 1, (z, hits)
        out.append(hits[0] == "right")
    assert out.count(True) == 1
    return out


# --- q6: density g/cm^3 -> kg/m^3 ----------------------------------------------------------------------

G_TO_KG = Q(1, 1000)
CM_TO_M = Q(1, 100)


def _sci(opt: str) -> Q:
    m = re.fullmatch(r"\$(\d+(?:\.\d+)?)(?:\\times10\^\{(-?\d+)\})?\$", opt)
    assert m, opt
    return Q(m.group(1)) * Q(10) ** int(m.group(2) or 0)


def pw_density_conversion(item: dict) -> list[bool]:
    vz = re.search(r"密度是 \$(\d+(?:\.\d+)?)\\ \\mathrm\{g/cm\^\{3\}\}\$", _zh(item)).group(1)
    ve = re.search(r"density of \$(\d+(?:\.\d+)?)\\ \\mathrm\{g/cm\^\{3\}\}\$", _en(item)).group(1)
    assert vz == ve
    rho = Q(vz)
    named = {
        "right": rho * G_TO_KG / CM_TO_M**3,
        "mass_only": rho * G_TO_KG,
        "no_conversion": rho,
        "forgot_cube": rho * G_TO_KG / CM_TO_M,
        "volume_only": rho / CM_TO_M**3,
    }
    zh, en = _opts(item)
    assert zh == en
    return _decide(named, [(_sci(o), False) for o in zh], "right")


# --- q7 (written): air temperature against height on a mountain; plot, line of best fit, slope, per km -----
# Facts: in the troposphere the air is colder higher up (earth/s116-air-vapour-clouds); 1 km = 1000 m
# (physics/s116-scales-units). Plot rules, scale rule and slope unit as above.


def pw_mixed_mountain_lapse(item: dict) -> bool:
    hz, tz = re.search(r"高度([\d、]+)公尺時，氣溫依序是([\d.、]+)℃", _zh(item)).groups()
    he, te = re.search(r"at heights ([\d, and]+) m the temperature is ([\d., and]+) ℃", _en(item)).groups()
    hs, ts = _nums(hz), _nums(tz)
    assert (hs, ts) == (_nums(he), _nums(te)) and len(hs) == len(ts) == 6
    across, up = re.search(r"橫軸(\d+)大格、縱軸(\d+)大格", _zh(item)).groups()
    assert re.search(rf"{across} large squares across, {up} up", _en(item))
    assert "氣溫對高度" in _zh(item) and "temperature against height" in _en(item)  # temperature vertical
    # scales by the chapter's rule
    sx, sy = scale_step(max(hs), int(across)), scale_step(max(ts), int(up))
    assert (sx, sy) == (200, 5)
    # least-squares line of the stem's data (exact)
    n = len(hs)
    mx, my = sum(hs) / n, sum(ts) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(hs, ts)) / sum((x - mx) ** 2 for x in hs)
    icpt = my - slope * mx
    assert slope == Q(-3, 500) and icpt == 25 and icpt != 0  # the line does not go through the origin
    # the model reads the slope from two far-apart points ON the line, (0, 25) and (2000, 13)
    x1, x2 = min(hs), max(hs)
    y1, y2 = icpt + slope * x1, icpt + slope * x2
    assert (x1, y1, x2, y2) == (0, 25, 2000, 13)
    assert (y2 - y1) / (x2 - x1) == slope
    per_km = slope * 1000
    assert per_km == -6
    mz, me = item["model"]["zh-tw"], item["model"]["en"]
    for m in (mz, me):
        assert f"({y2}-{y1})" in m and f"({x2}-{x1})" in m and "=-0.006$" in m and "=-6$" in m
    assert "(0, 25)" in mz and "(2000, 13)" in mz and "(0, 25)" in me and "(2000, 13)" in me
    assert f"每大格{sx}公尺" in mz and f"每大格{sy}℃" in mz and f"{sx} m per large square" in me
    assert "降低6℃" in mz and "falls by about 6 ℃" in me
    crit = {c["id"]: c for c in item["rubric"]["criteria"]}
    assert set(crit) == {"axes", "line", "slope", "convert"}
    assert sum(c["points"] for c in crit.values()) == 4 and "4分" in _zh(item) and "4 points" in _en(item)
    assert "−0.006" in crit["slope"]["text"]["zh-tw"] and "−6℃／公里" in crit["convert"]["text"]["zh-tw"]
    return True
