"""Verify practice item banks: schema shape, then answer keys recomputed with SymPy.

Usage (from the repo root):
    harness/.venv/Scripts/python harness/verify_items.py              # src/data/items/**/*.yaml
    harness/.venv/Scripts/python harness/verify_items.py --fixtures   # ... plus tests/fixtures/items/*.yaml
    harness/.venv/Scripts/python harness/verify_items.py FILE.yaml    # just these files
    add --strict to require a `verify:` check on every machine-checkable math/science item

The banks are the same YAML files the site loads (src/lib/items.ts validates them with Zod); this
script mirrors that schema in plain Python so a malformed bank fails here too, then runs each item's
`verify: <module>:<function>` check from harness/checks/<module>.py. A check recomputes the answer from
the stem on its own and returns it in the shape described in harness/README.md; the harness compares
that with the stored key. Exit status: 0 when every file passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
import traceback
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import sympy as sp
import yaml

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parent
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))  # so `checks.<module>` imports however the script is started

BANK_GLOB = "src/data/items/**/*.yaml"
FIXTURE_GLOB = "tests/fixtures/items/*.yaml"  # not recursive: tests/fixtures/items/bad/ is deliberately broken
MINUS = "−"
LOCALES = ("zh-tw", "en")
CHECKED_SUBJECTS = ("math", "physics", "chemistry", "biology", "earth")  # subjects whose keys the harness must recompute (--strict)

# Patterns copied from src/data/schema.ts and src/lib/items.ts; keep them in sync.
ITEM_ID_RE = re.compile(r"^[a-z0-9-]+(@\d+)?$")
CHAPTER_RE = re.compile(r"^(site|math|physics|chemistry|biology|earth|inquiry|history|geography|civics|chinese)/[a-z0-9-]+$")
CODE_KEY_RE = re.compile(r"^(math|nat|soc-elem|hist|geo|civ|chi|inq|exam):[A-Za-z0-9.\-/]+$")
VERIFY_RE = re.compile(r"^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*:[a-z_][a-z0-9_]*$")
CELL_RE = re.compile(r"^[0-9−]$")
BANK_PATH_RE = re.compile(r"/src/data/items/([a-z]+)/([a-z0-9-]+)\.ya?ml$")

BASE_KEYS = {"id", "type", "codes", "origin", "modelledOn", "skills", "review", "text", "verify"}
TYPE_KEYS = {
    "single": {"answer"},
    "multi": {"answer"},
    "fill": {"answer"},
    "numeric": {"accept", "answer"},
    "mixed": {"rubric", "model"},
}
TEXT_KEYS = {"stem", "options", "explain", "hint"}


# ---------------------------------------------------------------------------
# YAML 1.2 core schema, as the `yaml` npm package reads it. PyYAML speaks YAML 1.1, where `no` is false,
# `010` is octal 8 and `2026-11-15` is a date; in 1.2 those are the string "no", 10 and a string.
# Without this the two loaders could disagree about a key.
# ---------------------------------------------------------------------------
class Yaml12Loader(yaml.SafeLoader):
    """SafeLoader with YAML 1.2 core-schema scalars and duplicate keys rejected (as `uniqueKeys` does in TS)."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


_DROP = {"tag:yaml.org,2002:bool", "tag:yaml.org,2002:int", "tag:yaml.org,2002:float", "tag:yaml.org,2002:timestamp"}
Yaml12Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag not in _DROP] for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
Yaml12Loader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"), list("tTfF"))
Yaml12Loader.add_implicit_resolver("tag:yaml.org,2002:int", re.compile(r"^(?:[-+]?[0-9]+|0o[0-7]+|0x[0-9a-fA-F]+)$"), list("-+0123456789"))
Yaml12Loader.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(r"^(?:[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$"),
    list("-+0123456789."),
)


def _int12(loader: yaml.SafeLoader, node: yaml.Node) -> int:
    s = loader.construct_scalar(node)
    if s.startswith("0o"):
        return int(s[2:], 8)
    if s.startswith("0x"):
        return int(s[2:], 16)
    return int(s, 10)


def _bool12(loader: yaml.SafeLoader, node: yaml.Node) -> bool:
    return loader.construct_scalar(node).lower() == "true"


Yaml12Loader.add_constructor("tag:yaml.org,2002:int", _int12)
Yaml12Loader.add_constructor("tag:yaml.org,2002:bool", _bool12)


def load_yaml(text: str) -> Any:
    return yaml.load(text, Loader=Yaml12Loader)  # noqa: S506 -- a SafeLoader subclass


# ---------------------------------------------------------------------------
# results
# ---------------------------------------------------------------------------
@dataclass
class FileReport:
    path: str
    items: int = 0
    verified: int = 0
    problems: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


@dataclass
class Report:
    files: list[FileReport] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(f.ok for f in self.files)

    def render(self) -> str:
        items = sum(f.items for f in self.files)
        verified = sum(f.verified for f in self.files)
        bad = [f for f in self.files if not f.ok]
        lines = [f"verify_items: {len(self.files)} file(s), {items} item(s), {verified} recomputed by SymPy checks"]
        for f in self.files:
            if f.problems:
                lines.append(f"FAIL {f.path}")
                lines.extend(f"  - {p}" for p in f.problems)
            for w in f.warnings:
                lines.append(f"warn {f.path}: {w}")
        lines.append("OK" if not bad else f"FAILED: {len(bad)} file(s) with problems")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# schema (mirror of schema.ItemBank plus the cross-field rules in src/lib/items.ts)
# ---------------------------------------------------------------------------
def _is_int(x: Any) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _is_num(x: Any) -> bool:
    return (isinstance(x, (int, float)) and not isinstance(x, bool)) and x == x and x not in (float("inf"), float("-inf"))


def _nonempty_str(x: Any) -> bool:
    return isinstance(x, str) and len(x) > 0


def _l10n(x: Any, where: str, out: list[str]) -> None:
    if not isinstance(x, dict) or set(x) != set(LOCALES):
        out.append(f"{where}: must have exactly the keys zh-tw and en")
        return
    for loc in LOCALES:
        if not _nonempty_str(x[loc]):
            out.append(f"{where}.{loc}: must be a non-empty string")


def base_id(item_id: str) -> str:
    return re.sub(r"@\d+$", "", item_id)


def parse_fraction(s: str) -> Fraction | None:
    """A numeric key as an exact Fraction, the way src/lib/scoring.ts reads it (None if unreadable)."""
    t = s.strip().replace(MINUS, "-")
    if re.fullmatch(r"[+-]?\d+", t):
        return Fraction(int(t))
    m = re.fullmatch(r"([+-]?\d+)\s*/\s*(\d+)", t)
    if m:
        return None if int(m.group(2)) == 0 else Fraction(int(m.group(1)), int(m.group(2)))
    if re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?", t):
        return Fraction(t)
    return None


def numeric_key(answer: Any, accept: str) -> Fraction | None:
    if _is_int(answer):
        return Fraction(answer)
    if isinstance(answer, float):
        return Fraction(repr(answer))  # shortest repr, like String(n) in JS: 0.1 → 1/10 exactly
    if isinstance(answer, str):
        v = parse_fraction(answer)
        if v is None:
            return None
        if accept == "int" and "/" in answer:
            return None
        if accept == "fraction" and re.search(r"[.eE]", answer):
            return None
        if accept == "decimal" and "/" in answer:
            return None
        return v
    return None


def item_problems(item: Any, idx: int) -> list[str]:
    out: list[str] = []
    if not isinstance(item, dict):
        return [f"items[{idx}]: must be a mapping"]
    iid = item.get("id")
    tag = iid if isinstance(iid, str) else f"items[{idx}]"
    at = lambda msg: out.append(f"{tag}: {msg}")  # noqa: E731

    if not isinstance(iid, str) or not ITEM_ID_RE.match(iid):
        at(f"id {iid!r} must match {ITEM_ID_RE.pattern}")
    typ = item.get("type")
    if typ not in TYPE_KEYS:
        at(f"type {typ!r} must be one of {', '.join(TYPE_KEYS)}")
        return out
    allowed = BASE_KEYS | TYPE_KEYS[typ]
    for k in sorted(set(item) - allowed):
        at(f"unknown key {k!r} for a {typ} item")
    for k in sorted({"id", "origin", "text"} | TYPE_KEYS[typ]):
        if k not in item:
            at(f"missing {k!r}")
    if "origin" in item and item["origin"] != "original":
        at("origin must be 'original' (official items are linked, never copied)")
    codes = item.get("codes", [])
    if not isinstance(codes, list) or not all(isinstance(c, str) and CODE_KEY_RE.match(c) for c in codes):
        at("codes must be a list of '<domain>:<code>' keys")
    if "modelledOn" in item and not isinstance(item["modelledOn"], str):
        at("modelledOn must be a string")
    if not isinstance(item.get("skills", []), list) or not all(isinstance(s, str) for s in item.get("skills", [])):
        at("skills must be a list of strings")
    if "review" in item and not isinstance(item["review"], bool):
        at("review must be true or false")
    if "verify" in item and (not isinstance(item["verify"], str) or not VERIFY_RE.match(item["verify"])):
        at(f"verify {item['verify']!r} must look like '<module>:<function>'")

    # text: both locales, the same fields
    text = item.get("text")
    texts: dict[str, dict] = {}
    if not isinstance(text, dict) or set(text) != set(LOCALES):
        if "text" in item:
            at("text must have exactly the locales zh-tw and en")
    if isinstance(text, dict):
        for loc in LOCALES:
            t = text.get(loc)
            if not isinstance(t, dict):
                continue
            texts[loc] = t
            for k in sorted(set(t) - TEXT_KEYS):
                at(f"text.{loc}: unknown key {k!r}")
            for k in ("stem", "explain"):
                if not _nonempty_str(t.get(k)):
                    at(f"text.{loc}.{k} must be a non-empty string")
            if "options" in t and (not isinstance(t["options"], list) or not all(isinstance(o, str) and o.strip() for o in t["options"])):
                at(f"text.{loc}.options must be a list of non-empty strings")
            if "hint" in t and not isinstance(t["hint"], str):
                at(f"text.{loc}.hint must be a string")
    if len(texts) == 2 and bool(texts["zh-tw"].get("hint")) != bool(texts["en"].get("hint")):
        at("hint must exist in both locales or in neither")

    opts = {loc: t.get("options") for loc, t in texts.items()}
    answer = item.get("answer")
    if typ in ("single", "multi"):
        lists = [o for o in opts.values() if isinstance(o, list)]
        n = len(lists[0]) if lists else 0
        if len(lists) < 2:
            at("a choice item needs options in both locales")
        elif len(lists[0]) != len(lists[1]):
            at(f"zh-tw has {len(lists[0])} options but en has {len(lists[1])}")
        if n < 2:
            at("a choice item needs at least 2 options")
        if typ == "single":
            keys = [answer] if _is_int(answer) and answer >= 0 else None
            if keys is None:
                at("a single answer must be a non-negative integer (0-based option index)")
        else:
            keys = answer if isinstance(answer, list) and answer and all(_is_int(a) and a >= 0 for a in answer) else None
            if keys is None:
                at("a multi answer must be a non-empty list of non-negative integers (0-based option indices)")
        for k in keys or []:
            if k >= n:
                at(f"answer index {k} is outside the {n} options (indices are 0-based)")
        if keys and len(set(keys)) != len(keys):
            at("answer lists an option twice")
    elif any(o is not None for o in opts.values()):
        at(f"a {typ} item has no options")

    if typ == "fill" and not (isinstance(answer, list) and answer and all(isinstance(c, str) and CELL_RE.match(c) for c in answer)):
        at("a fill answer must be a non-empty list of single cells '0'–'9' or '−' (U+2212), quoted in YAML")
    if typ == "numeric":
        accept = item.get("accept")
        if accept not in ("int", "decimal", "fraction"):
            at("accept must be int, decimal or fraction")
        elif not (_is_num(answer) or isinstance(answer, str)):
            at("a numeric answer must be a number or a string")
        else:
            v = numeric_key(answer, accept)
            if v is None:
                at(f"answer {answer!r} is not a valid {accept}")
            elif accept == "int" and v.denominator != 1:
                at(f"answer {answer!r} is not an integer")
    if typ == "mixed":
        rubric = item.get("rubric")
        crit = rubric.get("criteria") if isinstance(rubric, dict) else None
        if not isinstance(rubric, dict) or set(rubric) != {"criteria"} or not isinstance(crit, list) or not crit:
            at("rubric must be { criteria: [ ... ] } with at least one criterion")
        else:
            for j, c in enumerate(crit):
                if not isinstance(c, dict) or set(c) != {"id", "points", "text"}:
                    at(f"rubric.criteria[{j}] must have exactly id, points and text")
                    continue
                if not isinstance(c["id"], str):
                    at(f"rubric.criteria[{j}].id must be a string")
                if not _is_num(c["points"]) or c["points"] <= 0:
                    at(f"rubric.criteria[{j}].points must be a positive number")
                _l10n(c["text"], f"{tag}: rubric.criteria[{j}].text", out)
            ids = [c.get("id") for c in crit if isinstance(c, dict)]
            if len(set(ids)) != len(ids):
                at("rubric criteria ids must be unique")
        if "model" in item:
            _l10n(item["model"], f"{tag}: model", out)
    return out


def bank_problems(data: Any, path: str) -> list[str]:
    if not isinstance(data, dict):
        return ["a bank must be a mapping with chapter and items"]
    out = [f"unknown top-level key {k!r}" for k in sorted(set(data) - {"chapter", "items"})]
    chapter = data.get("chapter")
    if not isinstance(chapter, str) or not CHAPTER_RE.match(chapter):
        out.append(f"chapter {chapter!r} must look like '<subject>/<slug>'")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        out.append("items must be a non-empty list")
        return out
    seen: set[str] = set()
    for i, it in enumerate(items):
        out.extend(item_problems(it, i))
        if isinstance(it, dict) and isinstance(it.get("id"), str):
            b = base_id(it["id"])
            if b in seen:
                out.append(f"{it['id']}: another item in this bank has the id {b!r} (ids are unique ignoring @version)")
            seen.add(b)
    m = BANK_PATH_RE.search(path.replace("\\", "/"))
    if m and chapter != f"{m.group(1)}/{m.group(2)}":
        out.append(f"chapter {chapter!r} does not match the file path (expected '{m.group(1)}/{m.group(2)}')")
    return out


# ---------------------------------------------------------------------------
# SymPy checks
# ---------------------------------------------------------------------------
def resolve_check(spec: str) -> Callable[[dict], Any]:
    module, func = spec.split(":")
    mod = importlib.import_module(f"checks.{module}")
    fn = getattr(mod, func, None)
    if not callable(fn):
        raise LookupError(f"harness/checks/{module.replace('.', '/')}.py has no function {func!r}")
    return fn


def _truth(x: Any) -> bool:
    """A Python bool or a decided SymPy boolean; anything undecided is an error."""
    if isinstance(x, bool):
        return x
    if x is sp.true or x is sp.false:
        return bool(x)
    raise TypeError(f"option verdict {x!r} is not a decided boolean (simplify it, or give the symbols assumptions)")


def _exact(x: Any) -> sp.Rational:
    """An exact rational from an int, Fraction or SymPy number; floats are refused."""
    if isinstance(x, bool):
        raise TypeError(f"{x!r} is a boolean, not a number")
    if isinstance(x, int):
        return sp.Integer(x)
    if isinstance(x, Fraction):
        return sp.Rational(x.numerator, x.denominator)
    if isinstance(x, (float, sp.Float)):
        raise TypeError(f"{x!r} is a float: return an exact SymPy number (Rational, Integer) instead")
    if not isinstance(x, sp.Basic):
        raise TypeError(f"{x!r} is not a number")
    v = x if x.is_Rational else sp.simplify(x)
    if not v.is_Rational or v.has(sp.Float):
        raise TypeError(f"{x!r} is not an exact rational number")
    return v


def cells_to_int(cells: list[str]) -> int | None:
    """['−', '1', '2'] → −12; None when the cells do not spell one integer."""
    s = "".join(cells).replace(MINUS, "-")
    return int(s) if re.fullmatch(r"-?\d+", s) else None


def expected_cells(result: Any) -> str:
    """A check's fill result as the string of cells it implies (see harness/README.md)."""
    if isinstance(result, (list, tuple)):
        parts = []
        for r in result:
            if isinstance(r, str):
                if not all(CELL_RE.match(c) for c in r.replace("-", MINUS)):
                    raise TypeError(f"fill part {r!r} has characters that are not cells")
                parts.append(r.replace("-", MINUS))
            else:
                v = _exact(r)
                if v.q != 1:
                    raise TypeError(f"fill part {r!r} is not an integer: return (p, q) for a fraction p/q")
                parts.append(str(v.p).replace("-", MINUS))
        return "".join(parts)
    v = _exact(result)
    if v.q != 1:
        raise TypeError(f"fill result {result!r} is not an integer: return (p, q) for a fraction p/q")
    return str(v.p).replace("-", MINUS)


def compare(item: dict, result: Any) -> str | None:
    """None when the check's result agrees with the stored key, else a message."""
    typ = item["type"]
    if typ in ("single", "multi"):
        n = len(item["text"]["zh-tw"]["options"])
        if not isinstance(result, (list, tuple)):
            return f"a {typ} check must return one truth value per option, got {result!r}"
        if len(result) != n:
            return f"the check judged {len(result)} options but the item has {n}"
        truths = [i for i, r in enumerate(result) if _truth(r)]
        opts = ", ".join(f"({i + 1})" for i in truths) or "none"
        if typ == "single":
            if len(truths) != 1:
                return f"a 單選 item needs exactly one true option; the check finds {opts}"
            if truths[0] != item["answer"]:
                return f"the check finds option ({truths[0] + 1}) true but the key is ({item['answer'] + 1})"
            return None
        if not truths:
            return "a 多選 item needs at least one true option; the check finds none"
        if sorted(truths) != sorted(item["answer"]):
            key = ", ".join(f"({i + 1})" for i in sorted(item["answer"]))
            return f"the check finds {opts} true but the key is {key}"
        return None
    if typ == "fill":
        key = "".join(item["answer"])
        if isinstance(result, (list, tuple)):
            want = expected_cells(result)
            return None if want == key else f"the check gives cells {want!r} but the key is {key!r}"
        v = _exact(result)
        got = cells_to_int(item["answer"])
        if v.q != 1:
            raise TypeError(f"fill result {result!r} is not an integer: return (p, q) for a fraction p/q")
        if got is None:
            return f"the key cells {key!r} do not spell one integer; return a tuple of parts instead"
        return None if got == v.p else f"the check computes {str(v.p).replace('-', MINUS)} but the key cells {key!r} spell {str(got).replace('-', MINUS)}"
    if typ == "numeric":
        want = _exact(result)
        stored = numeric_key(item["answer"], item["accept"])
        got = sp.Rational(stored.numerator, stored.denominator)
        return None if got == want else f"the check computes {want} but the key is {item['answer']!r} (= {got})"
    if typ == "mixed":
        return None if result is True else f"a check on a mixed item must return True (its identities hold), got {result!r}"
    return f"no comparison for type {typ!r}"


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------
def verify_file(path: Path, strict: bool = False) -> FileReport:
    rel = path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else path.as_posix()
    rep = FileReport(path=rel)
    try:
        data = load_yaml(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        rep.problems.append(f"YAML: {e}")
        return rep
    rep.problems.extend(bank_problems(data, "/" + rel))
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        return rep
    rep.items = len(items)
    if rep.problems:
        return rep  # never run checks against a malformed item
    subject = str(data.get("chapter", "")).split("/")[0]
    for it in items:
        spec = it.get("verify")
        if not spec:
            if it["type"] != "mixed" and subject in CHECKED_SUBJECTS:
                msg = f"{it['id']}: no verify check (the key is not machine-recomputed)"
                (rep.problems if strict else rep.warnings).append(msg)
            continue
        try:
            fn = resolve_check(spec)
            result = fn(it)
            msg = compare(it, result)
        except Exception as e:  # a broken check is a failure of the item, with the reason
            tb = traceback.extract_tb(e.__traceback__)[-1]
            msg = f"check {spec} raised {type(e).__name__}: {e} ({Path(tb.filename).name}:{tb.lineno})"
        if msg:
            rep.problems.append(f"{it['id']}: verify {spec}: {msg}")
        else:
            rep.verified += 1
    return rep


def collect(paths: list[str], fixtures: bool) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    found = sorted(ROOT.glob(BANK_GLOB))
    if fixtures:
        found += sorted(ROOT.glob(FIXTURE_GLOB))
    return found


def run(paths: list[str] | None = None, fixtures: bool = False, strict: bool = False) -> Report:
    return Report(files=[verify_file(p, strict=strict) for p in collect(paths or [], fixtures)])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify practice item banks (schema + SymPy answer checks).")
    ap.add_argument("paths", nargs="*", help="bank files to check (default: src/data/items/**/*.yaml)")
    ap.add_argument("--fixtures", action="store_true", help="also check tests/fixtures/items/*.yaml")
    ap.add_argument("--strict", action="store_true", help="fail math/physics/chemistry/biology items that have no verify check")
    args = ap.parse_args(argv)
    report = run(args.paths, fixtures=args.fixtures, strict=args.strict)
    out = report.render()
    try:
        print(out)
    except UnicodeEncodeError:  # a legacy Windows console code page
        sys.stdout.buffer.write((out + "\n").encode("utf-8", "replace"))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
