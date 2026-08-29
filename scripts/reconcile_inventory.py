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

EXPLAIN = {
    "shadow_agent": "running and observed, absent from the operator registry",
    "ghost_agent": "in the operator registry, never observed running",
    "charter_integrity": "reports itself but is not in the operator registry",
    "dependency_drift": "what it loaded differs from what the registry approved",
    "scope_drift": "effective permissions differ from the authorized scope",
    "tier_drift": "operating outside the environments its tier permits",
    "review_overdue": "charter review date has passed",
}


@dataclass
class Cell:
    cell_id: str
    concern: str
    layer: str
    authority: str
    records: str
    fields: list[str] = field(default_factory=list)
    feeds_rules: list[str] = field(default_factory=list)


def load_cells(inventory_dir: Path) -> list[Cell]:
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


def _mcp_set(rec: dict) -> set[tuple]:
    servers = dig(rec, "dependencies_runtime.mcp_servers") or []
    out = set()
    for s in servers:
        if isinstance(s, dict):
            out.add((s.get("name"), s.get("hash")))
        else:
            out.add((s, None))
    return out


def reconcile(self_d: dict, op_d: dict, disc: dict) -> list[dict]:
    """Compare the three layers agent by agent and name every disagreement."""
    results = []
    for agent in sorted(set(self_d) | set(op_d) | set(disc)):
        s, o, d = self_d.get(agent), op_d.get(agent), disc.get(agent)
        mismatches: list[str] = []

        if d is not None and o is None:
            mismatches.append("shadow_agent")
        if o is not None and d is None:
            mismatches.append("ghost_agent")
        if s is not None and o is None:
            mismatches.append("charter_integrity")

        if s and o:
            if dig(s, "dependencies_runtime.foundation_model") != dig(o, "dependencies_runtime.foundation_model"):
                mismatches.append("dependency_drift")
            elif _mcp_set(s) != _mcp_set(o):
                mismatches.append("dependency_drift")

            if dig(s, "authorization_runtime.rbac_role_ref") != dig(o, "authorization_runtime.rbac_role_ref"):
                mismatches.append("scope_drift")

            if dig(s, "risk_tier") != dig(o, "risk_tier"):
                mismatches.append("tier_drift")

        if d and o:
            de = set(dig(d, "blast_radius_profile.environments") or [])
            oe = set(dig(o, "blast_radius_profile.environments") or [])
            if de - oe:
                mismatches.append("tier_drift")

        due = dig(o or {}, "next_review_due")
        if isinstance(due, datetime.date) and due < datetime.date.today():
            mismatches.append("review_overdue")
        elif isinstance(due, str):
            try:
                if datetime.date.fromisoformat(due) < datetime.date.today():
                    mismatches.append("review_overdue")
            except ValueError:
                pass

        results.append(
            {
                "agent_identifier": agent,
                "self_declared": s is not None,
                "operator_declared": o is not None,
                "discovered": d is not None,
                "mismatches": sorted(set(mismatches)),
                "owner": dig(o or s or d or {}, "ownership.owner"),
            }
        )
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconcile the three Inventory layers.")
    ap.add_argument("--bundle", required=True, help="Directory holding the three layer files.")
    ap.add_argument("--inventory", default=str(REPO_ROOT / "inventory"))
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"bundle not found: {bundle}", file=sys.stderr)
        return 2

    layers = {l: load_layer(bundle, l) for l in LAYERS}
    if not any(layers.values()):
        print(f"bundle not found: no layer files in {bundle}", file=sys.stderr)
        return 2

    agents = reconcile(layers["in-agent"], layers["client-side"], layers["server-side"])
    flagged = [a for a in agents if a["mismatches"]]

    if args.format == "json":
        print(json.dumps({"bundle": str(bundle), "agents": agents,
                          "flagged": len(flagged), "total": len(agents)}, indent=2))
    else:
        for a in agents:
            layer_marks = "".join(
                m if a[k] else "-"
                for m, k in (("S", "self_declared"), ("O", "operator_declared"), ("D", "discovered"))
            )
            if a["mismatches"]:
                print(f"FLAG  [{layer_marks}]  {a['agent_identifier']}")
                for m in a["mismatches"]:
                    print(f"          {m}: {EXPLAIN.get(m, '')}")
            else:
                print(f"ok    [{layer_marks}]  {a['agent_identifier']}")
        print(f"\n  {len(flagged)} of {len(agents)} agents carry a cross-layer mismatch.")
        if flagged:
            print("  S=self-declared  O=operator-declared  D=discovered. A missing letter is the finding.")

    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
