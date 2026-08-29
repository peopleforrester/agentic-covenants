#!/usr/bin/env python3
"""ABOUTME: Tests for the Inventory reconciler, which finds shadow, ghost and drifted agents.
ABOUTME: Cross-layer mismatch is the point of the matrix, so the mismatch rules are what is tested.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = REPO_ROOT / "scripts" / "reconcile_inventory.py"
EXAMPLES = REPO_ROOT / "inventory" / "examples"

sys.path.insert(0, str(REPO_ROOT / "scripts"))


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)


def findings_for(agent: str) -> set[str]:
    result = run("--bundle", str(EXAMPLES), "--format", "json")
    payload = json.loads(result.stdout)
    for rec in payload["agents"]:
        if rec["agent_identifier"] == agent:
            return set(rec["mismatches"])
    raise AssertionError(f"{agent} absent from the reconciliation")


def test_tool_exists():
    assert TOOL.is_file()


def test_every_inventory_cell_declares_a_record_contract():
    import reconcile_inventory as ri

    cells = ri.load_cells(REPO_ROOT / "inventory")
    assert len(cells) == 15, f"expected 15 Inventory cells, found {len(cells)}"
    for cell in cells:
        assert cell.records, f"{cell.cell_id} declares no recorded fields"


def test_shadow_agent_is_detected():
    """Discovered running, absent from the operator registry. The CSA number's failure mode."""
    assert "shadow_agent" in findings_for("agent-unregistered-scraper-001")


def test_ghost_agent_is_detected():
    """In the registry, not observed running. Retired-but-not-removed, or failing to start."""
    assert "ghost_agent" in findings_for("agent-retired-etl-001")


def test_dependency_drift_is_detected():
    """What the agent reports it runs differs from what the registry says it should."""
    assert "dependency_drift" in findings_for("agent-drifted-indexer-001")


def test_charter_integrity_failure_is_detected():
    """Self-declared but never entered in the operator registry."""
    assert "charter_integrity" in findings_for("agent-unregistered-scraper-001")


def test_clean_agent_has_no_mismatches():
    assert findings_for("agent-release-bot-001") == set()


def test_exits_non_zero_when_mismatches_exist():
    assert run("--bundle", str(EXAMPLES)).returncode != 0


def test_missing_bundle_is_an_error_not_a_skip():
    result = run("--bundle", str(REPO_ROOT / "inventory" / "nope"))
    assert result.returncode != 0
    assert "not found" in (result.stdout + result.stderr).lower()
