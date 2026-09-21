#!/usr/bin/env python3
"""ABOUTME: Tests for the Inventory reconciler, which finds shadow, ghost and drifted agents.
ABOUTME: Cross-layer mismatch is the point of the matrix, so the mismatch rules are what is tested.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL = REPO_ROOT / "scripts" / "reconcile_inventory.py"
EXAMPLES = REPO_ROOT / "inventory" / "examples"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

# The layer names the matrix uses, paired with the authority each one carries.
AUTHORITY = {
    "in-agent": "self-declared",
    "client-side": "operator-declared",
    "server-side": "discovered",
}
BUNDLE_FILE = {
    "in-agent": "self-declared",
    "client-side": "operator-declared",
    "server-side": "discovered",
}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)


def findings_for(agent: str) -> set[str]:
    result = run("--bundle", str(EXAMPLES), "--format", "json")
    payload = json.loads(result.stdout)
    for rec in payload["agents"]:
        if rec["agent_identifier"] == agent:
            return set(rec["mismatches"])
    raise AssertionError(f"{agent} absent from the reconciliation")


# --------------------------------------------------------------------------
# Synthetic fixtures
# --------------------------------------------------------------------------
# The declarations are the thing under test, so most tests build a small
# inventory tree and a small bundle rather than leaning on the worked example.
# A synthetic tree isolates one rule, which the fifteen real cells cannot.


def write_inventory(root: Path, specs: list[dict[str, Any]]) -> Path:
    """Write a synthetic inventory tree of per-cell record.yaml files.

    Args:
        root: Directory to write the concern/layer tree under.
        specs: One mapping per cell, each carrying concern, layer, and the
            optional fields and feeds_rules lists the reconciler reads.

    Returns:
        The inventory root that was written, ready to pass to --inventory.
    """
    for spec in specs:
        concern, layer = spec["concern"], spec["layer"]
        cell_dir = root / concern / layer
        cell_dir.mkdir(parents=True, exist_ok=True)
        doc = {
            "cell": {
                "id": f"{concern}.{layer}",
                "concern": concern,
                "layer": layer,
                "authority": AUTHORITY[layer],
                "records": spec.get("records", "synthetic cell for the test suite"),
            },
            "fields": spec.get("fields", []),
            "feeds_rules": spec.get("feeds_rules", []),
        }
        (cell_dir / "record.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
    return root


def write_bundle(root: Path, layers: dict[str, list[dict[str, Any]]]) -> Path:
    """Write a synthetic three-layer bundle.

    Args:
        root: Directory to write the layer files into.
        layers: Agent records keyed by layer name. An omitted layer is absent.

    Returns:
        The bundle root, ready to pass to --bundle.
    """
    root.mkdir(parents=True, exist_ok=True)
    for layer, agents in layers.items():
        path = root / f"{BUNDLE_FILE[layer]}.yaml"
        path.write_text(yaml.safe_dump({"agents": agents}), encoding="utf-8")
    return root


def clone_inventory(dest: Path, drop_rule: str) -> Path:
    """Copy the repo's fifteen declarations, removing one rule from every cell.

    Args:
        dest: Directory to write the copy under.
        drop_rule: The rule id to strip from every feeds_rules list.

    Returns:
        The inventory root that was written.
    """
    for src in sorted((REPO_ROOT / "inventory").glob("*/*/record.yaml")):
        doc = yaml.safe_load(src.read_text(encoding="utf-8"))
        doc["feeds_rules"] = [r for r in doc.get("feeds_rules") or [] if r != drop_rule]
        cell_dir = dest / src.parent.parent.name / src.parent.name
        cell_dir.mkdir(parents=True, exist_ok=True)
        (cell_dir / "record.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
    return dest


def mismatches(bundle: Path, inventory: Path, agent: str = "agent-under-test") -> set[str]:
    """Reconcile a bundle against an inventory tree and return one agent's findings."""
    result = run("--bundle", str(bundle), "--inventory", str(inventory), "--format", "json")
    assert result.returncode in (0, 1), f"unexpected exit {result.returncode}: {result.stderr}"
    payload = json.loads(result.stdout)
    for rec in payload["agents"]:
        if rec["agent_identifier"] == agent:
            return set(rec["mismatches"])
    raise AssertionError(f"{agent} absent from the reconciliation")


# --------------------------------------------------------------------------
# The worked example still reconciles the way the matrix documents
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# The declarations are load-bearing
# --------------------------------------------------------------------------
# Issue #13. load_cells was defined and never called, --inventory was parsed
# and never used, and the three mismatch rules were hardcoded. Every cell
# record.yaml asserted on line 2 that this tool reads it. These tests hold the
# tool to that claim: a tool that reports a control is in place when it is not
# is the defect this repo exists to argue against.


def test_every_declared_rule_has_an_implementation():
    import reconcile_inventory as ri

    cells = ri.load_cells(REPO_ROOT / "inventory")
    for cell in cells:
        for rule_id in cell.feeds_rules:
            assert rule_id in ri.RULES, f"{cell.cell_id} feeds unimplemented rule '{rule_id}'"


def test_every_inventory_cell_declares_fields_and_rules():
    import reconcile_inventory as ri

    for cell in ri.load_cells(REPO_ROOT / "inventory"):
        assert cell.fields, f"{cell.cell_id} declares no fields"
        assert cell.feeds_rules, f"{cell.cell_id} feeds no mismatch rule"


def test_evaluated_rules_come_from_the_declarations():
    import reconcile_inventory as ri

    declared = {r for c in ri.load_cells(REPO_ROOT / "inventory") for r in c.feeds_rules}
    payload = json.loads(run("--bundle", str(EXAMPLES), "--format", "json").stdout)
    assert set(payload["rules"]) == declared


def test_json_reports_the_cells_it_read():
    payload = json.loads(run("--bundle", str(EXAMPLES), "--format", "json").stdout)
    assert len(payload["cells"]) == 15
    assert {c["id"] for c in payload["cells"]} >= {"identity.in-agent", "supply-chain.server-side"}


def test_inventory_flag_changes_behavior(tmp_path):
    """A bogus --inventory once produced byte-identical output. That was the bug."""
    baseline = run("--bundle", str(EXAMPLES))
    bogus = run("--bundle", str(EXAMPLES), "--inventory", str(tmp_path / "absent"))
    assert (bogus.returncode, bogus.stdout) != (baseline.returncode, baseline.stdout)


def test_bogus_inventory_path_is_an_error_not_a_silent_pass(tmp_path):
    result = run("--bundle", str(EXAMPLES), "--inventory", str(tmp_path / "absent"))
    assert result.returncode == 2
    combined = (result.stdout + result.stderr).lower()
    assert "not found" in combined and "cell" in combined


def test_dropping_a_rule_declaration_stops_it_firing(tmp_path):
    """feeds_rules decides which rules run, so removing one must silence it."""
    inventory = clone_inventory(tmp_path / "inv", drop_rule="shadow_agent")
    result = run("--bundle", str(EXAMPLES), "--inventory", str(inventory), "--format", "json")
    payload = json.loads(result.stdout)
    found = {m for rec in payload["agents"] for m in rec["mismatches"]}
    assert "shadow_agent" not in found
    assert "ghost_agent" in found, "dropping one rule must not disable the others"


def test_an_undefined_rule_in_a_declaration_is_an_error(tmp_path):
    inventory = write_inventory(
        tmp_path / "inv",
        [{"concern": "identity", "layer": "client-side",
          "fields": ["agent_identifier"], "feeds_rules": ["not_a_real_rule"]}],
    )
    result = run("--bundle", str(EXAMPLES), "--inventory", str(inventory))
    assert result.returncode == 2
    assert "not_a_real_rule" in result.stdout + result.stderr


# --- fields drive which values are compared -------------------------------


def _drift_bundle(root: Path) -> Path:
    """A bundle whose two layers agree on risk_tier and disagree on the model."""
    return write_bundle(
        root,
        {
            "in-agent": [{"agent_identifier": "agent-under-test", "risk_tier": 2,
                          "dependencies_runtime": {"foundation_model": "claude-opus-5"}}],
            "client-side": [{"agent_identifier": "agent-under-test", "risk_tier": 2,
                             "dependencies_runtime": {"foundation_model": "claude-sonnet-5"}}],
        },
    )


def test_an_undeclared_field_is_not_compared(tmp_path):
    inventory = write_inventory(
        tmp_path / "inv",
        [
            {"concern": "blast-radius", "layer": "in-agent",
             "fields": ["risk_tier"], "feeds_rules": ["tier_drift"]},
            {"concern": "blast-radius", "layer": "client-side",
             "fields": ["risk_tier"], "feeds_rules": ["tier_drift"]},
        ],
    )
    assert mismatches(_drift_bundle(tmp_path / "bundle"), inventory) == set()


def test_declaring_a_field_on_both_layers_makes_it_compared(tmp_path):
    """Same bundle as above. Only the declaration changed, and now it is drift."""
    inventory = write_inventory(
        tmp_path / "inv",
        [
            {"concern": "blast-radius", "layer": "in-agent",
             "fields": ["risk_tier", "dependencies_runtime.foundation_model"],
             "feeds_rules": ["tier_drift"]},
            {"concern": "blast-radius", "layer": "client-side",
             "fields": ["risk_tier", "dependencies_runtime.foundation_model"],
             "feeds_rules": ["tier_drift"]},
        ],
    )
    assert "tier_drift" in mismatches(_drift_bundle(tmp_path / "bundle"), inventory)


def test_a_field_declared_on_only_one_layer_is_not_compared(tmp_path):
    """Agreement needs both layers to claim they record the field."""
    inventory = write_inventory(
        tmp_path / "inv",
        [
            {"concern": "blast-radius", "layer": "in-agent",
             "fields": ["risk_tier", "dependencies_runtime.foundation_model"],
             "feeds_rules": ["tier_drift"]},
            {"concern": "blast-radius", "layer": "client-side",
             "fields": ["risk_tier"], "feeds_rules": ["tier_drift"]},
        ],
    )
    assert mismatches(_drift_bundle(tmp_path / "bundle"), inventory) == set()


def test_a_field_absent_from_one_layer_is_not_drift(tmp_path):
    """A layer that reported nothing supplies no evidence. Silence is not disagreement."""
    inventory = write_inventory(
        tmp_path / "inv",
        [
            {"concern": "supply-chain", "layer": "in-agent",
             "fields": ["dependencies_runtime.foundation_model"],
             "feeds_rules": ["dependency_drift"]},
            {"concern": "supply-chain", "layer": "client-side",
             "fields": ["dependencies_runtime.foundation_model"],
             "feeds_rules": ["dependency_drift"]},
        ],
    )
    bundle = write_bundle(
        tmp_path / "bundle",
        {
            "in-agent": [{"agent_identifier": "agent-under-test",
                          "dependencies_runtime": {"foundation_model": "claude-sonnet-5"}}],
            "client-side": [{"agent_identifier": "agent-under-test"}],
        },
    )
    assert mismatches(bundle, inventory) == set()


def test_list_comparison_ignores_order(tmp_path):
    """Two MCP servers in a different order are the same dependency set."""
    inventory = write_inventory(
        tmp_path / "inv",
        [
            {"concern": "supply-chain", "layer": "in-agent",
             "fields": ["dependencies_runtime.mcp_servers"], "feeds_rules": ["dependency_drift"]},
            {"concern": "supply-chain", "layer": "client-side",
             "fields": ["dependencies_runtime.mcp_servers"], "feeds_rules": ["dependency_drift"]},
        ],
    )
    servers = [{"name": "filesystem", "hash": "sha256:aaaa"},
               {"name": "github", "hash": "sha256:bbbb"}]
    bundle = write_bundle(
        tmp_path / "bundle",
        {
            "in-agent": [{"agent_identifier": "agent-under-test",
                          "dependencies_runtime": {"mcp_servers": list(reversed(servers))}}],
            "client-side": [{"agent_identifier": "agent-under-test",
                             "dependencies_runtime": {"mcp_servers": servers}}],
        },
    )
    assert mismatches(bundle, inventory) == set()


# --- containment: what was observed must sit inside what was authorized ---


def _environment_inventory(root: Path) -> Path:
    return write_inventory(
        root,
        [
            {"concern": "blast-radius", "layer": "client-side",
             "fields": ["risk_tier"], "feeds_rules": ["tier_drift"]},
            {"concern": "blast-radius", "layer": "server-side",
             "fields": ["blast_radius_profile.environments"], "feeds_rules": ["tier_drift"]},
        ],
    )


def _environment_bundle(root: Path, discovered: list[str]) -> Path:
    return write_bundle(
        root,
        {
            "client-side": [{"agent_identifier": "agent-under-test",
                             "blast_radius_profile": {"environments": ["dev"]}}],
            "server-side": [{"agent_identifier": "agent-under-test",
                             "blast_radius_profile": {"environments": discovered}}],
        },
    )


def test_discovered_environment_outside_the_authorized_set_is_tier_drift(tmp_path):
    inventory = _environment_inventory(tmp_path / "inv")
    bundle = _environment_bundle(tmp_path / "bundle", ["dev", "prod"])
    assert "tier_drift" in mismatches(bundle, inventory)


def test_discovered_environment_inside_the_authorized_set_is_clean(tmp_path):
    """Containment is one-directional. An authorized environment nobody used is not drift."""
    inventory = _environment_inventory(tmp_path / "inv")
    bundle = _environment_bundle(tmp_path / "bundle", ["dev"])
    assert mismatches(bundle, inventory) == set()


# --- the overdue rule reads the declared date field -----------------------


def _review_inventory(root: Path) -> Path:
    return write_inventory(
        root,
        [
            {"concern": "approval-gating", "layer": "client-side",
             "fields": ["charter_version", "next_review_due"], "feeds_rules": ["review_overdue"]},
            {"concern": "approval-gating", "layer": "in-agent",
             "fields": ["charter_version"], "feeds_rules": ["review_overdue"]},
        ],
    )


def test_a_past_review_date_is_overdue(tmp_path):
    bundle = write_bundle(
        tmp_path / "bundle",
        {"client-side": [{"agent_identifier": "agent-under-test", "charter_version": 1.0,
                          "next_review_due": "2020-01-01"}]},
    )
    assert "review_overdue" in mismatches(bundle, _review_inventory(tmp_path / "inv"))


def test_a_future_review_date_is_clean(tmp_path):
    bundle = write_bundle(
        tmp_path / "bundle",
        {"client-side": [{"agent_identifier": "agent-under-test", "charter_version": 1.0,
                          "next_review_due": "2099-01-01"}]},
    )
    assert mismatches(bundle, _review_inventory(tmp_path / "inv")) == set()


def test_a_non_date_field_declared_alongside_the_date_is_skipped(tmp_path):
    """charter_version sits in the same declaration and must not be read as a date."""
    bundle = write_bundle(
        tmp_path / "bundle",
        {"client-side": [{"agent_identifier": "agent-under-test", "charter_version": 1.0,
                          "next_review_due": "2099-01-01"}]},
    )
    result = run("--bundle", str(bundle), "--inventory", str(_review_inventory(tmp_path / "inv")))
    assert result.returncode == 0, result.stderr


# --- presence rules are declared, not assumed -----------------------------


def test_presence_rule_runs_only_when_both_layers_declare_it(tmp_path):
    """shadow_agent needs a discovered cell and an operator cell that both feed it."""
    bundle = write_bundle(
        tmp_path / "bundle",
        {"server-side": [{"agent_identifier": "agent-under-test"}]},
    )
    one_sided = write_inventory(
        tmp_path / "one-sided",
        [{"concern": "identity", "layer": "server-side",
          "fields": ["agent_identifier"], "feeds_rules": ["shadow_agent"]}],
    )
    assert mismatches(bundle, one_sided) == set()

    both = write_inventory(
        tmp_path / "both",
        [
            {"concern": "identity", "layer": "server-side",
             "fields": ["agent_identifier"], "feeds_rules": ["shadow_agent"]},
            {"concern": "identity", "layer": "client-side",
             "fields": ["agent_identifier"], "feeds_rules": ["shadow_agent"]},
        ],
    )
    assert "shadow_agent" in mismatches(bundle, both)


# --- scoring mirrors the Charter validator --------------------------------


def test_a_concern_scores_as_the_share_of_agents_clean_under_its_rules():
    import reconcile_inventory as ri

    cells = ri.load_cells(REPO_ROOT / "inventory")
    agents = [
        {"agent_identifier": "a", "mismatches": ["shadow_agent"]},
        {"agent_identifier": "b", "mismatches": []},
    ]
    assert ri.concern_score(cells, agents, "identity") == 0.5


def test_posture_is_reported_and_is_a_minimum_not_a_mean():
    payload = json.loads(run("--bundle", str(EXAMPLES), "--format", "json").stdout)
    concerns = payload["concerns"]
    assert set(concerns) == set(
        ["identity", "authorization", "blast-radius", "approval-gating", "supply-chain"]
    )
    assert payload["posture"] == min(concerns.values())
