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
