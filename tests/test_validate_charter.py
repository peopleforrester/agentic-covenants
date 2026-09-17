#!/usr/bin/env python3
"""ABOUTME: Tests for the Charter validator, which scores a governance bundle cell by cell.
ABOUTME: The checks are the product, so they are the thing under test.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_charter.py"
EXAMPLES = REPO_ROOT / "charter" / "examples"

sys.path.insert(0, str(REPO_ROOT / "scripts"))


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *args], capture_output=True, text=True
    )


def test_validator_exists():
    assert VALIDATOR.is_file(), "scripts/validate_charter.py must exist"


def test_every_govern_cell_declares_checks():
    import validate_charter as vc

    cells = vc.load_cells(REPO_ROOT / "charter")
    assert len(cells) == 15, f"expected 15 Charter cells, found {len(cells)}"
    for cell in cells:
        assert cell.checks, f"{cell.cell_id} declares no checks"
        assert cell.question, f"{cell.cell_id} has no structural question"
        assert cell.owner, f"{cell.cell_id} names no owner"


def test_check_ids_are_unique():
    import validate_charter as vc

    ids = [c.check_id for cell in vc.load_cells(REPO_ROOT / "charter") for c in cell.checks]
    assert len(ids) == len(set(ids)), "check ids must be unique across the matrix"


def test_worked_example_bundle_passes_every_cell():
    result = run("--bundle", str(EXAMPLES))
    assert result.returncode == 0, (
        f"the worked example must satisfy every cell.\n{result.stdout}\n{result.stderr}"
    )


def test_placeholder_bundle_fails():
    """The shipped templates carry intentional placeholders, so they must not score clean."""
    result = run("--bundle", str(REPO_ROOT / "charter" / "templates"))
    assert result.returncode != 0, "templates carry placeholders and must fail validation"


def test_missing_bundle_is_an_error_not_a_skip():
    result = run("--bundle", str(REPO_ROOT / "charter" / "does-not-exist"))
    assert result.returncode != 0
    assert "not found" in (result.stdout + result.stderr).lower()


def test_score_is_reported_and_is_a_minimum_not_a_mean():
    import validate_charter as vc

    scored = [
        vc.CellResult("a", "identity", "in-agent", passed=3, failed=0),
        vc.CellResult("b", "identity", "client-side", passed=0, failed=3),
    ]
    assert vc.concern_score(scored, "identity") == 0.0, (
        "a concern scores as its weakest cell, because an agent takes the open path"
    )


def test_json_output_is_machine_readable():
    import json

    result = run("--bundle", str(EXAMPLES), "--format", "json")
    payload = json.loads(result.stdout)
    assert "cells" in payload and "concerns" in payload
    assert len(payload["cells"]) == 15


# --------------------------------------------------------------------------
# no_wildcard: an allowlist of one entry that permits everything is not clean
# --------------------------------------------------------------------------
# Issue #9. The check caught a bare "*" and anything ending ":*:*", so
# "Bash(*)" scored clean while granting every command. A validator that
# reports a control is in place when it is not is the highest-severity defect
# this repo can ship, per SECURITY.md.

import validate_charter  # noqa: E402


def wildcard(entries: list[str]) -> tuple[bool, str]:
    """Run the no_wildcard check against an allowlist."""
    chk = validate_charter.Check(
        check_id="t", description="t", type="no_wildcard",
        target="allow", document="charter", severity="high", evidence="t",
    )
    return validate_charter.run_check(chk, {"charter": {"allow": entries}})


def test_bare_asterisk_is_unbounded():
    ok, _ = wildcard(["*"])
    assert not ok


def test_tool_wrapped_asterisk_is_unbounded():
    """Bash(*) permits every command. This is the reported bug."""
    ok, msg = wildcard(["Bash(*)"])
    assert not ok, "Bash(*) grants everything and must not score clean"
    assert "Bash(*)" in msg


def test_double_asterisk_is_unbounded():
    assert not wildcard(["**"])[0]
    assert not wildcard(["Read(**)"])[0]


def test_whitespace_does_not_hide_an_unbounded_entry():
    assert not wildcard([" Bash( * ) "])[0]


def test_all_wildcard_segments_are_unbounded():
    assert not wildcard(["Bash(*:*)"])[0]


def test_arn_granting_every_service_is_unbounded():
    assert not wildcard(["arn:aws:*:*:*:*"])[0]


def test_one_unbounded_entry_condemns_the_whole_list():
    """An allowlist is only as tight as its loosest entry."""
    ok, msg = wildcard(["Bash(git:status)", "Read", "Bash(*)"])
    assert not ok
    assert "Bash(*)" in msg


# --- scoped wildcards are legitimate and must not be flagged --------------
# This repo's own settings.json uses Bash(git:add:*) and Bash(kubectl:delete:*).
# Flagging those would break the artifacts the framework ships.


def test_scoped_tool_wildcard_is_bounded():
    assert wildcard(["Bash(git:*)"])[0]
    assert wildcard(["Bash(kubectl:delete:*)"])[0]


def test_fully_literal_entries_are_bounded():
    assert wildcard(["Bash(git:status)", "Read", "Glob"])[0]


def test_wildcard_subdomain_is_bounded():
    assert wildcard(["*.internal.example.com"])[0]


def test_arn_scoped_to_a_bucket_is_bounded():
    assert wildcard(["arn:aws:s3:::my-bucket/*"])[0]


def test_empty_allowlist_is_not_a_wildcard_finding():
    assert wildcard([])[0]
