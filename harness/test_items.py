"""pytest for the item harness. Run from the repo root:

    harness/.venv/Scripts/python -m pytest harness
"""

from __future__ import annotations

import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp

import verify_items as vi

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = sorted((ROOT / "tests/fixtures/items").glob("*.yaml"))
BAD = ROOT / "tests/fixtures/items/bad"
SCRIPT = Path(vi.__file__)


def _single(**over):
    item = {
        "id": "q1",
        "type": "single",
        "origin": "original",
        "text": {
            "zh-tw": {"stem": "題目", "options": ["甲", "乙"], "explain": "說明"},
            "en": {"stem": "Stem", "options": ["A", "B"], "explain": "Why"},
        },
        "answer": 0,
    }
    item.update(over)
    return item


# ---------- the fixtures ----------
def test_fixtures_exist_and_cover_every_type():
    assert FIXTURES, "tests/fixtures/items/*.yaml is empty"
    types = set()
    for f in FIXTURES:
        for it in vi.load_yaml(f.read_text(encoding="utf-8"))["items"]:
            types.add(it["type"])
    assert types == {"single", "multi", "fill", "numeric", "mixed"}


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_every_fixture_passes_and_every_item_is_recomputed(path):
    rep = vi.verify_file(path, strict=True)
    assert rep.ok, "\n".join(rep.problems)
    assert rep.items > 0 and rep.verified == rep.items


def test_deliberately_wrong_keys_are_caught():
    rep = vi.verify_file(BAD / "wrong-key.yaml")
    assert not rep.ok
    text = "\n".join(rep.problems)
    assert "fx-linear-wrong@1" in text and "computes −12" in text
    assert "fx-sqrt-wrong@1" in text and "option (2) true but the key is (4)" in text
    assert rep.verified == 0


def test_missing_locale_is_a_schema_failure_and_no_check_runs():
    rep = vi.verify_file(BAD / "missing-en.yaml")
    assert not rep.ok
    assert any("zh-tw and en" in p for p in rep.problems)
    assert rep.verified == 0


def test_real_banks_pass():
    """Every bank the site ships (src/data/items) must pass; zero banks is fine before content exists."""
    report = vi.run()
    assert report.ok, report.render()


# ---------- the command line ----------
def _cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_cli_exit_codes():
    ok = _cli("--fixtures")
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "OK" in ok.stdout
    bad = _cli(str(BAD / "wrong-key.yaml"))
    assert bad.returncode == 1
    assert "FAIL" in bad.stdout and "fx-linear-wrong@1" in bad.stdout


# ---------- schema mirror ----------
def test_schema_accepts_a_minimal_item_and_rejects_shape_errors():
    assert vi.item_problems(_single(), 0) == []
    assert any("unknown key" in p for p in vi.item_problems(_single(extra=1), 0))
    assert any("origin" in p for p in vi.item_problems(_single(origin="ceec"), 0))
    assert any("answer index 2" in p for p in vi.item_problems(_single(answer=2), 0))
    assert any("non-negative integer" in p for p in vi.item_problems(_single(answer=True), 0))  # bool is not an index
    assert any("verify" in p for p in vi.item_problems(_single(verify="checks/x.py::f"), 0))
    assert vi.item_problems(_single(verify="math.real_numbers:ex_03"), 0) == []


def test_schema_cross_field_rules_match_the_ts_loader():
    t = _single()["text"]
    t["zh-tw"]["options"] = ["a", "b", "c"]
    assert any("3 options but en has 2" in p for p in vi.item_problems(_single(text=t), 0))
    t = _single()["text"]
    t["zh-tw"]["hint"] = "提示"
    assert any("both locales or in neither" in p for p in vi.item_problems(_single(text=t), 0))
    fill = _single(type="fill", answer=["-", "1"])
    assert any("a fill item has no options" in p for p in vi.item_problems(fill, 0))
    assert any("U+2212" in p for p in vi.item_problems(fill, 0))
    numeric_text = {"zh-tw": {"stem": "s", "explain": "e"}, "en": {"stem": "s", "explain": "e"}}
    assert any("not an integer" in p for p in vi.item_problems(_single(type="numeric", accept="int", answer=2.5, text=numeric_text), 0))
    assert vi.item_problems(_single(type="numeric", accept="fraction", answer="−3/4", text=numeric_text), 0) == []


def test_bank_rules():
    good = {"chapter": "math/x", "items": [_single()]}
    assert vi.bank_problems(good, "/tests/x.yaml") == []
    assert any("does not match the file path" in p for p in vi.bank_problems(good, "/src/data/items/math/y.yaml"))
    twice = {"chapter": "math/x", "items": [_single(id="q1@1"), _single(id="q1@2")]}
    assert any("unique ignoring @version" in p for p in vi.bank_problems(twice, "/tests/x.yaml"))


# ---------- YAML 1.2, like the `yaml` npm package ----------
def test_yaml_reads_scalars_as_yaml_1_2():
    data = vi.load_yaml("a: no\nb: 010\nc: 2026-11-15\nd: true\ne: 0.25\nf: on\ng: 0o17\nh: 1_000\n")
    assert data == {"a": "no", "b": 10, "c": "2026-11-15", "d": True, "e": 0.25, "f": "on", "g": 15, "h": "1_000"}


def test_yaml_rejects_duplicate_keys():
    with pytest.raises(Exception, match="duplicate key"):
        vi.load_yaml("a: 1\na: 2\n")


# ---------- comparisons ----------
def test_cells_and_numbers():
    assert vi.cells_to_int(["−", "1", "2"]) == -12
    assert vi.cells_to_int(["1", "−"]) is None
    assert vi.expected_cells((5, 6)) == "56"
    assert vi.expected_cells((sp.Integer(-3), "05")) == "−305"
    assert vi.numeric_key(0.1, "decimal") == Fraction(1, 10)
    assert vi.numeric_key("3/4", "fraction") == Fraction(3, 4)
    assert vi.numeric_key("0.5", "fraction") is None
    with pytest.raises(TypeError, match="float"):
        vi._exact(0.5)
    with pytest.raises(TypeError, match="not an exact rational"):
        vi._exact(sp.sqrt(2))


def test_compare_rules():
    single = _single(answer=1)
    assert vi.compare(single, [False, True]) is None
    assert "exactly one true option" in vi.compare(single, [True, True])
    with pytest.raises(TypeError, match="not a decided boolean"):
        vi.compare(single, [None, True])
    multi = _single(type="multi", answer=[0, 1])
    assert vi.compare(multi, [True, True]) is None
    assert "at least one true option" in vi.compare(multi, [False, False])
    fill = {"type": "fill", "answer": ["−", "1", "2"]}
    assert vi.compare(fill, sp.Integer(-12)) is None
    assert "computes −13" in vi.compare(fill, -13)
    with pytest.raises(TypeError, match="return \\(p, q\\)"):
        vi.compare(fill, sp.Rational(1, 2))
    numeric = {"type": "numeric", "accept": "decimal", "answer": 0.25}
    assert vi.compare(numeric, sp.Rational(1, 4)) is None
    assert "the key is 0.25" in vi.compare(numeric, sp.Rational(1, 3))
    assert vi.compare({"type": "mixed"}, True) is None
    assert vi.compare({"type": "mixed"}, 1) is not None
