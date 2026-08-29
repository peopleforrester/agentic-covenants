#!/usr/bin/env python3
"""ABOUTME: Scores a governance bundle against the fifteen Charter cells and exits non-zero on failure.
ABOUTME: Turns the Govern matrix from a documentation discipline into a scorable instrument.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONCERNS = ["identity", "authorization", "blast-radius", "approval-gating", "supply-chain"]
LAYERS = ["in-agent", "client-side", "server-side"]

# A value matching any of these is an unfilled template, not an answer. The repo ships
# templates with deliberate placeholders, so a bundle that still carries them has not
# been filled in and must not score as satisfied.
PLACEHOLDER = re.compile(
    r"REPLACE_WITH|example\.com|^<.*>$|^TODO$|^TBD$|^\.\.\.$", re.IGNORECASE
)


@dataclass
class Check:
    check_id: str
    description: str
    type: str
    target: str
    document: str
    severity: str
    evidence: str


@dataclass
class Cell:
    cell_id: str
    concern: str
    layer: str
    authority: str
    document: str
    owner: str
    question: str
    checks: list[Check] = field(default_factory=list)


@dataclass
class CellResult:
    cell_id: str
    concern: str
    layer: str
    passed: int = 0
    failed: int = 0
    failures: list[dict[str, str]] = field(default_factory=list)

    @property
    def score(self) -> float:
        total = self.passed + self.failed
        return 1.0 if total == 0 else self.passed / total


def load_cells(charter_dir: Path) -> list[Cell]:
    """Load every cell definition under charter/<concern>/<layer>/checks.yaml."""
    cells: list[Cell] = []
    for concern in CONCERNS:
        for layer in LAYERS:
            path = charter_dir / concern / layer / "checks.yaml"
            if not path.is_file():
                continue
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            meta = raw["cell"]
            cells.append(
                Cell(
                    cell_id=meta["id"],
                    concern=meta["concern"],
                    layer=meta["layer"],
                    authority=meta["authority"],
                    document=meta["document"],
                    owner=meta["owner"],
                    question=meta["question"],
                    checks=[Check(check_id=c.pop("id"), **c) for c in raw["checks"]],
                )
            )
    return cells


def dig(doc: Any, dotted: str) -> Any:
    """Walk a dotted path. Returns None when any segment is absent."""
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and bool(PLACEHOLDER.search(value.strip()))


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and not is_placeholder(value)
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def run_check(chk: Check, docs: dict[str, Any]) -> tuple[bool, str]:
    """Return (passed, reason). Reason is empty when the check passes."""
    doc = docs.get(chk.document)
    if doc is None:
        return False, f"document '{chk.document}' missing from the bundle"

    t, target = chk.type, chk.target

    if t == "required_field":
        return (True, "") if _nonempty(dig(doc, target)) else (False, f"{target} is missing, empty, or a placeholder")

    if t == "field_present":
        cur, *rest = [doc], target.split(".")
        return (True, "") if dig(doc, target) is not None else (False, f"{target} key is absent")

    if t == "no_placeholder":
        block = dig(doc, target)
        if block is None:
            return False, f"{target} is absent"
        found = [k for k, v in (block.items() if isinstance(block, dict) else []) if is_placeholder(v)]
        return (True, "") if not found else (False, f"placeholders remain in {target}: {', '.join(found)}")

    if t == "distinct_from":
        a, b = target.split("|")
        va, vb = dig(doc, a), dig(doc, b)
        if not _nonempty(va):
            return False, f"{a} is missing or a placeholder"
        return (True, "") if va != vb else (False, f"{a} and {b} name the same person")

    if t == "min_items":
        path, _, n = target.partition(":")
        need = int(n or 1)
        val = dig(doc, path)
        if val is None:
            return False, f"{path} is absent"
        size = len(val) if isinstance(val, (list, dict)) else 0
        return (True, "") if size >= need else (False, f"{path} has {size} entries, needs {need}")

    if t == "enum":
        path, _, allowed = target.partition(":")
        opts = {o.strip() for o in allowed.split(",")}
        val = dig(doc, path)
        return (True, "") if str(val) in opts else (False, f"{path} is {val!r}, expected one of {sorted(opts)}")

    if t == "no_wildcard":
        val = dig(doc, target) or []
        bad = [v for v in val if isinstance(v, str) and (v.strip() == "*" or v.strip().endswith(":*:*"))]
        return (True, "") if not bad else (False, f"wildcard entries in {target}: {bad}")

    if t == "every_has_key":
        path, _, key = target.partition("|")
        val = dig(doc, path)
        if not isinstance(val, (list, dict)) or not val:
            return False, f"{path} is absent or empty"
        items = val.values() if isinstance(val, dict) else val
        missing = [i for i, item in enumerate(items) if not (isinstance(item, dict) and _nonempty(item.get(key)))]
        return (True, "") if not missing else (False, f"{len(missing)} entries under {path} lack '{key}'")

    if t == "every_value_matches":
        path, _, pattern = target.partition(":")
        rx = re.compile(pattern)
        val = dig(doc, path)
        if not isinstance(val, dict) or not val:
            return False, f"{path} is absent or empty"
        bad = [k for k, v in val.items() if not (isinstance(v, str) and rx.match(v))]
        return (True, "") if not bad else (False, f"{path} entries do not match {pattern}: {bad}")

    if t == "matches":
        path, _, pattern = target.partition(":")
        val = dig(doc, path)
        ok = isinstance(val, str) and re.match(pattern, val)
        return (True, "") if ok else (False, f"{path} does not match {pattern}")

    if t == "date_future":
        val = dig(doc, target)
        d = _as_date(val)
        if d is None:
            return False, f"{target} is missing or not a date"
        return (True, "") if d >= datetime.date.today() else (False, f"{target} was due {d.isoformat()}, which is past")

    if t == "date_within_days":
        path, _, n = target.partition(":")
        d = _as_date(dig(doc, path))
        if d is None:
            return False, f"{path} is missing or not a date"
        age = (datetime.date.today() - d).days
        return (True, "") if age <= int(n) else (False, f"{path} was {age} days ago, limit is {n}")

    return False, f"unknown check type '{t}'"


def _as_date(val: Any) -> datetime.date | None:
    if isinstance(val, datetime.date):
        return val
    if isinstance(val, str):
        try:
            return datetime.date.fromisoformat(val.strip())
        except ValueError:
            return None
    return None


def load_bundle(bundle: Path) -> dict[str, Any]:
    """Load the three governance documents. A document that cannot be read is absent."""
    docs: dict[str, Any] = {}
    for name in ("agent-charter", "domain-charter", "organizational-policy"):
        for suffix in (".yaml", ".yml"):
            path = bundle / f"{name}{suffix}"
            if path.is_file():
                loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    docs[name] = loaded
                break
    return docs


def concern_score(results: list[CellResult], concern: str) -> float:
    """A concern scores as its weakest cell. An agent takes the open path, not the mean one."""
    scores = [r.score for r in results if r.concern == concern]
    return min(scores) if scores else 0.0


def evaluate(cells: list[Cell], docs: dict[str, Any]) -> list[CellResult]:
    results = []
    for cell in cells:
        res = CellResult(cell.cell_id, cell.concern, cell.layer)
        for chk in cell.checks:
            ok, reason = run_check(chk, docs)
            if ok:
                res.passed += 1
            else:
                res.failed += 1
                res.failures.append(
                    {"id": chk.check_id, "reason": reason, "severity": chk.severity,
                     "evidence": chk.evidence}
                )
        results.append(res)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a governance bundle against the Charter matrix.")
    ap.add_argument("--bundle", required=True, help="Directory holding the three governance documents.")
    ap.add_argument("--charter", default=str(REPO_ROOT / "charter"), help="Charter cell definitions.")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"bundle not found: {bundle}", file=sys.stderr)
        return 2

    cells = load_cells(Path(args.charter))
    docs = load_bundle(bundle)
    if not docs:
        print(f"bundle not found: no governance documents in {bundle}", file=sys.stderr)
        return 2

    results = evaluate(cells, docs)
    concerns = {c: concern_score(results, c) for c in CONCERNS}
    failed_cells = [r for r in results if r.failed]

    if args.format == "json":
        print(json.dumps({
            "bundle": str(bundle),
            "cells": [
                {"id": r.cell_id, "concern": r.concern, "layer": r.layer,
                 "passed": r.passed, "failed": r.failed, "score": round(r.score, 3),
                 "failures": r.failures}
                for r in results
            ],
            "concerns": {k: round(v, 3) for k, v in concerns.items()},
            "posture": round(min(concerns.values()), 3) if concerns else 0.0,
        }, indent=2))
    else:
        for r in results:
            mark = "PASS" if not r.failed else "FAIL"
            print(f"{mark}  {r.cell_id:<32} {r.passed}/{r.passed + r.failed}")
            for f in r.failures:
                print(f"        {f['id']}: {f['reason']}")
        print()
        for c, s in concerns.items():
            print(f"  {c:<18} {s:.0%}  (weakest cell in the concern)")
        print(f"\n  POSTURE {min(concerns.values()):.0%}" if concerns else "")

    return 1 if failed_cells else 0


if __name__ == "__main__":
    sys.exit(main())
