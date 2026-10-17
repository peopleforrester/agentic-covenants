#!/usr/bin/env python3
"""ABOUTME: Tests for scripts/check.py, the repo's own pre-commit validator.
ABOUTME: Covers check selection on the command line and the prose and placeholder rules on a scratch tree.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECK = REPO_ROOT / "scripts" / "check.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check  # noqa: E402

EM_DASH = "—"
EN_DASH = "–"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK), *args], capture_output=True, text=True
    )


@pytest.fixture
def scratch(tmp_path, monkeypatch):
    """A throwaway git tree that check.py treats as the repository root."""
    root = tmp_path.resolve()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    monkeypatch.setattr(check, "REPO_ROOT", root)
    return root


# --- selection -------------------------------------------------------------


def test_skip_runs_every_check_except_the_named_ones():
    skipped = [name for name in check.CHECKS if name != "root"]
    args = [arg for name in skipped for arg in ("--skip", name)]
    result = run(*args)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[PASS] root" in result.stdout
    for name in skipped:
        assert f"] {name} " not in result.stdout


def test_only_and_skip_together_is_a_usage_error():
    result = run("--only", "root", "--skip", "policies")
    assert result.returncode == 2
    assert "not allowed with" in result.stderr


def test_skip_rejects_an_unknown_check():
    result = run("--skip", "no-such-check")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_a_failing_check_exits_one(scratch, monkeypatch, capsys):
    (scratch / "note.md").write_text(f"one {EM_DASH} two\n")
    monkeypatch.setattr(sys, "argv", ["check.py", "--only", "prose"])
    assert check.main() == 1
    assert "[FAIL] prose" in capsys.readouterr().out


def test_a_clean_tree_exits_zero(scratch, monkeypatch, capsys):
    (scratch / "note.md").write_text("one, then two\n")
    monkeypatch.setattr(sys, "argv", ["check.py", "--only", "prose"])
    assert check.main() == 0
    assert "All checks passed." in capsys.readouterr().out


# --- prose -----------------------------------------------------------------


def test_prose_flags_an_em_dash_in_markdown(scratch):
    (scratch / "note.md").write_text(f"clean line\nthe gate {EM_DASH} which fails\n")
    findings = check.check_prose(staged=False)
    assert findings.problems == ["note.md:2: em-dash (U+2014); rewrite without it"]


def test_prose_ignores_dashes_inside_code_fences(scratch):
    (scratch / "note.md").write_text(f"```\necho a {EM_DASH} b\n```\n")
    assert check.check_prose(staged=False).ok


def test_prose_allows_an_en_dash_between_identifiers_only(scratch):
    (scratch / "note.md").write_text(
        f"Covers IL4{EN_DASH}IL5 and Art. 9(2)(a){EN_DASH}(d).\nfirst {EN_DASH} second\n"
    )
    findings = check.check_prose(staged=False)
    assert findings.problems == [
        "note.md:2: en-dash (U+2013) in prose; use 'to' or 'through'"
    ]


def test_prose_reads_only_comment_lines_in_scripts(scratch):
    (scratch / "tool.sh").write_text(f'#!/bin/bash\necho "a {EM_DASH} b"\n# c {EM_DASH} d\n')
    findings = check.check_prose(staged=False)
    assert findings.problems == ["tool.sh:3: em-dash (U+2014); rewrite without it"]


# --- placeholders ----------------------------------------------------------

# Built by concatenation so this file does not itself trip the check it tests.
REAL_LOOKING_KEY = "AKIA" + "Q" * 16
REAL_ACCOUNT_ARN = "arn:aws:iam::" + "987654321098" + ":role/agent"
PLACEHOLDER_ARN = "arn:aws:iam::" + "123456789012" + ":role/agent"


def test_placeholders_flags_a_credential_shaped_key(scratch):
    (scratch / "policy.yaml").write_text(f"key: {REAL_LOOKING_KEY}\n")
    findings = check.check_placeholders(staged=False)
    assert findings.problems == ["policy.yaml:1: possible AWS access key id in a template"]


def test_placeholders_allows_the_documented_aws_example_key(scratch):
    (scratch / "policy.yaml").write_text("key: AKIAIOSFODNN7EXAMPLE\n")
    assert check.check_placeholders(staged=False).ok


def test_placeholders_flags_a_non_placeholder_account_in_an_arn(scratch):
    (scratch / "main.tf").write_text(f'role = "{REAL_ACCOUNT_ARN}"\n')
    findings = check.check_placeholders(staged=False)
    assert findings.problems == [
        "main.tf:1: non-placeholder AWS account id 987654321098 in an ARN"
    ]


def test_placeholders_allows_the_placeholder_account(scratch):
    (scratch / "main.tf").write_text(f'role = "{PLACEHOLDER_ARN}"\n')
    assert check.check_placeholders(staged=False).ok
