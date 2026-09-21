#!/usr/bin/env python3
"""ABOUTME: Reconciles the three Inventory layers and reports shadow, ghost and drifted agents.
ABOUTME: Cross-layer disagreement is the signal; agreement across all three is the only clean state.
"""

from __future__ import annotations

import argparse
import datetime
import json
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
LAYER_FILE = {
    "in-agent": "self-declared",
    "client-side": "operator-declared",
    "server-side": "discovered",
}


@dataclass(frozen=True)
class Comparison:
    """One cross-layer test a mismatch rule performs.

    The kind supplies the semantics; the cell declarations supply everything
    else. Four kinds cover the matrix:

    presence
        The agent appears on `subject` and is missing from `reference`.
    agreement
        Every field both layers declare must carry the same value wherever
        both layers reported one. Runs over each pair of declaring layers, so
        a cell that declares a rule is never inert.
    containment
        What `subject` observed must sit inside what `reference` authorized.
        Directional, because an authorized environment nobody used is not drift.
    overdue
        A date field on `subject` has passed.
    """

    kind: str
    subject: str = ""
    reference: str = ""


@dataclass(frozen=True)
class Rule:
    """A named cross-layer mismatch, and the comparisons that detect it."""

    rule_id: str
    explain: str
    comparisons: tuple[Comparison, ...]


# The reconciler owns what each rule *means*; inventory/<concern>/<layer>/record.yaml
# owns whether it runs, on which layers, and over which fields. Splitting it this
# way is the same split validate_charter.py uses: run_check holds the semantics of
# each check type, checks.yaml holds the targets.
RULES: dict[str, Rule] = {
    "shadow_agent": Rule(
        "shadow_agent",
        "running and observed, absent from the operator registry",
        (Comparison("presence", subject="server-side", reference="client-side"),),
    ),
    "ghost_agent": Rule(
        "ghost_agent",
        "in the operator registry, never observed running",
        (Comparison("presence", subject="client-side", reference="server-side"),),
    ),
    "charter_integrity": Rule(
        "charter_integrity",
        "reports itself but is not in the operator registry",
        (Comparison("presence", subject="in-agent", reference="client-side"),),
    ),
    "dependency_drift": Rule(
        "dependency_drift",
        "what it loaded differs from what the registry approved",
        (Comparison("agreement"),),
    ),
    "scope_drift": Rule(
        "scope_drift",
        "effective permissions differ from the authorized scope",
        (Comparison("agreement"),),
    ),
    "tier_drift": Rule(
        "tier_drift",
        "operating outside the environments its tier permits",
        (
            Comparison("agreement"),
            Comparison("containment", subject="server-side", reference="client-side"),
        ),
    ),
    "review_overdue": Rule(
        "review_overdue",
        "charter review date has passed",
        # Only the registry carries a forward-looking review date. The agent's own
        # last-review field is a past date by construction and would always fire.
        (Comparison("overdue", subject="client-side"),),
    ),
}


@dataclass
class Cell:
    """One cell of the Inventory matrix, as declared by its record.yaml."""

    cell_id: str
    concern: str
    layer: str
    authority: str
    records: str
    fields: list[str] = field(default_factory=list)
    feeds_rules: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlannedComparison:
    """A comparison the declarations put in play, with its targets resolved."""

    rule_id: str
    kind: str
    subject: str
    reference: str
    fields: tuple[str, ...]


def load_cells(inventory_dir: Path) -> list[Cell]:
    """Load every cell definition under inventory/<concern>/<layer>/record.yaml.

    Args:
        inventory_dir: Root of the concern/layer tree to read.

    Returns:
        One Cell per record.yaml found. A missing file is a cell that declares
        nothing, not an error, so a partial tree reconciles on what it has.
    """
    cells: list[Cell] = []
    for concern in CONCERNS:
        for layer in LAYERS:
            path = inventory_dir / concern / layer / "record.yaml"
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
                    records=meta["records"],
                    fields=raw.get("fields") or [],
                    feeds_rules=raw.get("feeds_rules") or [],
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


def load_layer(bundle: Path, layer: str) -> dict[str, dict]:
    """Return {agent_identifier: record} for one layer. A missing file is an empty layer."""
    for suffix in (".yaml", ".yml"):
        path = bundle / f"{LAYER_FILE[layer]}{suffix}"
        if path.is_file():
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
            entries = raw.get("agents", []) if isinstance(raw, dict) else raw
            return {e["agent_identifier"]: e for e in entries if e.get("agent_identifier")}
    return {}


def declared_fields(cells: list[Cell], rule_id: str, layer: str) -> list[str]:
    """Fields the cells on one layer declare as feeding one rule.

    Args:
        cells: The loaded cell declarations.
        rule_id: The mismatch rule to collect fields for.
        layer: The layer whose declarations to read.

    Returns:
        The declared field paths in declaration order, without duplicates.
    """
    out: list[str] = []
    for cell in cells:
        if cell.layer == layer and rule_id in cell.feeds_rules:
            for path in cell.fields:
                if path not in out:
                    out.append(path)
    return out


def build_plan(cells: list[Cell]) -> list[PlannedComparison]:
    """Turn the cell declarations into the comparisons the reconciler will run.

    Args:
        cells: The loaded cell declarations.

    Returns:
        Every comparison whose participating layers are all declared.

    Raises:
        ValueError: When a cell feeds a rule the reconciler does not implement.
            A declaration nothing acts on is the defect this tool had, so an
            unknown rule id fails loudly rather than being skipped.
    """
    declaring: dict[str, set[str]] = {}
    for cell in cells:
        for rule_id in cell.feeds_rules:
            if rule_id not in RULES:
                raise ValueError(f"{cell.cell_id} feeds unimplemented rule '{rule_id}'")
            declaring.setdefault(rule_id, set()).add(cell.layer)

    plan: list[PlannedComparison] = []
    for rule_id in sorted(declaring):
        layers = declaring[rule_id]
        for comp in RULES[rule_id].comparisons:
            if comp.kind == "agreement":
                plan.extend(_agreement_pairs(cells, rule_id, layers))
                continue
            needed = {l for l in (comp.subject, comp.reference) if l}
            if not needed <= layers:
                continue
            targets = () if comp.kind == "presence" else tuple(
                declared_fields(cells, rule_id, comp.subject)
            )
            plan.append(
                PlannedComparison(rule_id, comp.kind, comp.subject, comp.reference, targets)
            )
    return plan


def _agreement_pairs(cells: list[Cell], rule_id: str, layers: set[str]) -> list[PlannedComparison]:
    """Pair every two layers that declare the rule, over the fields both declare."""
    ordered = [l for l in LAYERS if l in layers]
    out: list[PlannedComparison] = []
    for i, subject in enumerate(ordered):
        for reference in ordered[i + 1:]:
            ref_fields = set(declared_fields(cells, rule_id, reference))
            shared = tuple(f for f in declared_fields(cells, rule_id, subject) if f in ref_fields)
            if shared:
                out.append(PlannedComparison(rule_id, "agreement", subject, reference, shared))
    return out


def _comparable(value: Any) -> Any:
    """Normalize a value so equality ignores ordering inside lists.

    Two MCP servers listed in a different order are the same dependency set, and
    flagging that as drift would train operators to ignore the finding.
    """
    if isinstance(value, list):
        return frozenset(_comparable(v) for v in value)
    if isinstance(value, dict):
        return frozenset((k, _comparable(v)) for k, v in value.items())
    return value


def _as_date(value: Any) -> datetime.date | None:
    """Read a value as a date, or None when it is not one."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def apply_comparison(planned: PlannedComparison, records: dict[str, dict | None]) -> bool:
    """Run one planned comparison against one agent's per-layer records.

    Args:
        planned: The comparison to run, with its fields already resolved.
        records: The agent's record on each layer, or None where it is absent.

    Returns:
        True when the comparison finds the mismatch it tests for.
    """
    subject = records.get(planned.subject)
    reference = records.get(planned.reference) if planned.reference else None

    if planned.kind == "presence":
        return subject is not None and reference is None

    if planned.kind == "overdue":
        if subject is None:
            return False
        today = datetime.date.today()
        return any(
            (due := _as_date(dig(subject, path))) is not None and due < today
            for path in planned.fields
        )

    if subject is None or reference is None:
        return False

    for path in planned.fields:
        left, right = dig(subject, path), dig(reference, path)
        # A layer that reported nothing supplies no evidence. Silence is the
        # business of the presence rules, not of a value comparison.
        if left is None or right is None:
            continue
        if planned.kind == "agreement":
            if _comparable(left) != _comparable(right):
                return True
        elif planned.kind == "containment":
            if not isinstance(left, list) or not isinstance(right, list):
                continue
            if {_comparable(v) for v in left} - {_comparable(v) for v in right}:
                return True
    return False


def reconcile(plan: list[PlannedComparison], layers: dict[str, dict[str, dict]]) -> list[dict]:
    """Compare the layers agent by agent and name every disagreement.

    Args:
        plan: The comparisons the declarations put in play.
        layers: Each layer's {agent_identifier: record} mapping.

    Returns:
        One result per agent seen on any layer, carrying which layers hold it
        and the sorted set of mismatch rules it tripped.
    """
    results = []
    everyone = set().union(*(set(v) for v in layers.values())) if layers else set()
    for agent in sorted(everyone):
        records: dict[str, dict | None] = {l: layers.get(l, {}).get(agent) for l in LAYERS}
        mismatches = {p.rule_id for p in plan if apply_comparison(p, records)}
        present = {l: records[l] is not None for l in LAYERS}
        results.append(
            {
                "agent_identifier": agent,
                "self_declared": present["in-agent"],
                "operator_declared": present["client-side"],
                "discovered": present["server-side"],
                "mismatches": sorted(mismatches),
                "owner": dig(
                    records["client-side"] or records["in-agent"] or records["server-side"] or {},
                    "ownership.owner",
                ),
            }
        )
    return results


def concern_score(cells: list[Cell], agents: list[dict], concern: str) -> float:
    """Share of agents carrying no mismatch under any rule this concern feeds.

    Args:
        cells: The loaded cell declarations.
        agents: The reconciliation results.
        concern: The concern to score.

    Returns:
        A ratio from 0.0 to 1.0. A concern with no declared rules, or a bundle
        with no agents, scores 1.0 because it has nothing to disprove.
    """
    rules = {r for c in cells if c.concern == concern for r in c.feeds_rules}
    if not rules or not agents:
        return 1.0
    clean = sum(1 for a in agents if not rules & set(a["mismatches"]))
    return clean / len(agents)


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconcile the three Inventory layers.")
    ap.add_argument("--bundle", required=True, help="Directory holding the three layer files.")
    ap.add_argument("--inventory", default=str(REPO_ROOT / "inventory"),
                    help="Inventory cell definitions that declare the mismatch rules.")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"bundle not found: {bundle}", file=sys.stderr)
        return 2

    cells = load_cells(Path(args.inventory))
    if not cells:
        print(f"inventory not found: no cell definitions under {args.inventory}", file=sys.stderr)
        return 2

    try:
        plan = build_plan(cells)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    layers = {l: load_layer(bundle, l) for l in LAYERS}
    if not any(layers.values()):
        print(f"bundle not found: no layer files in {bundle}", file=sys.stderr)
        return 2

    agents = reconcile(plan, layers)
    flagged = [a for a in agents if a["mismatches"]]
    concerns = {c: concern_score(cells, agents, c) for c in CONCERNS}
    rules = sorted({p.rule_id for p in plan})

    if args.format == "json":
        print(json.dumps({
            "bundle": str(bundle),
            "inventory": str(args.inventory),
            "cells": [
                {"id": c.cell_id, "concern": c.concern, "layer": c.layer,
                 "authority": c.authority, "fields": c.fields, "feeds_rules": c.feeds_rules}
                for c in cells
            ],
            "rules": rules,
            "agents": agents,
            "concerns": {k: round(v, 3) for k, v in concerns.items()},
            "posture": round(min(concerns.values()), 3) if concerns else 0.0,
            "flagged": len(flagged),
            "total": len(agents),
        }, indent=2))
    else:
        for a in agents:
            layer_marks = "".join(
                m if a[k] else "-"
                for m, k in (("S", "self_declared"), ("O", "operator_declared"), ("D", "discovered"))
            )
            if a["mismatches"]:
                print(f"FLAG  [{layer_marks}]  {a['agent_identifier']}")
                for m in a["mismatches"]:
                    print(f"          {m}: {RULES[m].explain}")
            else:
                print(f"ok    [{layer_marks}]  {a['agent_identifier']}")
        print(f"\n  {len(flagged)} of {len(agents)} agents carry a cross-layer mismatch.")
        if flagged:
            print("  S=self-declared  O=operator-declared  D=discovered. A missing letter is the finding.")
        print(f"\n  {len(rules)} mismatch rules from {len(cells)} cell declarations")
        print(f"  under {args.inventory}")
        for c, s in concerns.items():
            print(f"  {c:<18} {s:.0%}  (agents clean under the rules this concern feeds)")
        print(f"\n  POSTURE {min(concerns.values()):.0%}" if concerns else "")

    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
