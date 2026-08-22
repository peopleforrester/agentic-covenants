#!/usr/bin/env python3
# ABOUTME: Client-side validator for this repo. Checks link integrity, YAML/JSON
# ABOUTME: parseability, prose style, and that no real credentials replaced a placeholder.
"""Repository checks that run locally, before a commit, with no CI round trip.

This repo argues that constraints belong outside the layer that can be talked
out of them. Running its own checks client-side rather than only in CI is the
same argument applied to itself: the check fires before the bad commit exists,
not after it has been pushed.

Exit codes:
    0   all checks passed
    1   one or more checks failed
    2   invoked incorrectly

Usage:
    ./scripts/check.py              # check the whole repository
    ./scripts/check.py --staged     # check only git-staged files (pre-commit)
    ./scripts/check.py --only links # run a single check
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories that are never checked. Mirrors the prune list used by the
# repo-discovery tooling: generated and vendored trees are out of scope.
PRUNE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".notes",  # gitignored working notes; docs/ is a reserved public path
    "transcripts",
    "claude-ai-context",
}


@dataclass
class Findings:
    """Accumulates failures for one check."""

    name: str
    problems: list[str] = field(default_factory=list)

    def add(self, path: Path, line: int | None, message: str) -> None:
        location = _relative(path)
        if line is not None:
            location = f"{location}:{line}"
        self.problems.append(f"{location}: {message}")

    @property
    def ok(self) -> bool:
        return not self.problems


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _pruned(path: Path) -> bool:
    return any(part in PRUNE_DIRS for part in path.parts)


def iter_files(patterns: Iterable[str], staged: bool) -> list[Path]:
    """Return repo files matching any glob suffix in `patterns`.

    With `staged`, restrict to files git has staged for commit so a pre-commit
    hook stays fast on a large tree.
    """
    suffixes = tuple(patterns)

    if staged:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        candidates = [REPO_ROOT / line for line in result.stdout.splitlines() if line]
    else:
        # --others --exclude-standard adds untracked files that are not
        # gitignored. Without it a full run silently skips every new file,
        # which is the opposite of useful.
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        candidates = [REPO_ROOT / line for line in result.stdout.splitlines() if line]

    return [
        p
        for p in candidates
        if p.name.endswith(suffixes) and p.is_file() and not _pruned(p)
    ]


# --------------------------------------------------------------------------
# Check: relative links in Markdown resolve to something that exists
# --------------------------------------------------------------------------

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_links(staged: bool) -> Findings:
    """Every relative Markdown link must resolve, relative to its own file.

    Resolving from the repo root instead of the linking file's directory
    produces false positives on every nested cell README, so the base is the
    file's own parent directory.
    """
    findings = Findings("links")

    for path in iter_files((".md",), staged):
        base = path.parent
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            for target in LINK_RE.findall(line):
                target = target.strip()
                if not target or target.startswith(
                    ("http://", "https://", "mailto:", "#", "<")
                ):
                    continue
                # Strip a fragment; anchors within a file are not resolved here.
                filepart = target.split("#", 1)[0]
                if not filepart:
                    continue
                if not (base / filepart).exists():
                    findings.add(path, lineno, f"broken link -> {target}")

    return findings


# --------------------------------------------------------------------------
# Check: YAML and JSON parse
# --------------------------------------------------------------------------


def check_yaml(staged: bool) -> Findings:
    """Every tracked YAML file must parse. Multi-document files are supported."""
    findings = Findings("yaml")
    try:
        import yaml
    except ImportError:
        findings.add(REPO_ROOT, None, "PyYAML not installed; cannot validate YAML")
        return findings

    for path in iter_files((".yaml", ".yml"), staged):
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            list(yaml.safe_load_all(text))
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            line = mark.line + 1 if mark else None
            detail = getattr(exc, "problem", None) or str(exc).splitlines()[0]
            findings.add(path, line, f"YAML parse error: {detail}")

    return findings


def check_json(staged: bool) -> Findings:
    """Every tracked JSON file must parse.

    Settings files in this repo carry `_comment` keys rather than JSONC-style
    comments precisely so they stay valid JSON. This check enforces that.
    """
    findings = Findings("json")

    for path in iter_files((".json",), staged):
        try:
            json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError as exc:
            findings.add(path, exc.lineno, f"JSON parse error: {exc.msg}")

    return findings


# --------------------------------------------------------------------------
# Check: prose style
# --------------------------------------------------------------------------

EM_DASH = "—"
EN_DASH = "–"


def check_prose(staged: bool) -> Findings:
    """No em-dashes in prose. En-dashes are flagged outside numeric ranges.

    Code fences are skipped: a dash inside a shell command or a policy snippet
    is not prose.
    """
    findings = Findings("prose")

    for path in iter_files((".md",), staged):
        in_fence = False
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if EM_DASH in line:
                findings.add(path, lineno, "em-dash (U+2014); rewrite without it")
            # An en-dash is allowed between identifier-shaped tokens, where the
            # format expects it: IL4-IL5, 9(2)(a)-(d), 2026-2027. It is not
            # allowed in running prose, where "to" or "through" is the fix.
            if EN_DASH in line and not re.search(
                r"(?:\w*\d\w*|\([a-z0-9]+\))\s*" + EN_DASH + r"\s*(?:\w*\d\w*|\([a-z0-9]+\))",
                line,
            ):
                findings.add(
                    path, lineno, "en-dash (U+2013) in prose; use 'to' or 'through'"
                )

    return findings


# --------------------------------------------------------------------------
# Check: placeholders were not replaced with something real
# --------------------------------------------------------------------------

# The artifacts here are templates. A real credential appearing in one means a
# substitution leaked back into the repo, which SECURITY.md promises cannot
# happen. These patterns are deliberately narrow to avoid firing on the
# documented placeholder values.
SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"ASIA[0-9A-Z]{16}", "AWS temporary access key id"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub token"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API key"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key block"),
    (r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.", "JWT"),
]

# Documented placeholder account id. Any *other* 12-digit account id in an ARN
# is a real one that leaked.
PLACEHOLDER_ACCOUNTS = {"123456789012", "000000000000", "111122223333"}

# Credential-shaped strings that are published, documented, non-functional
# examples. AWS uses these throughout its own docs precisely so they can appear
# in sample code. Flagging them is a false positive that trains people to
# ignore the check, which is worse than the check not existing.
DOCUMENTED_EXAMPLES = {
    "AKIAIOSFODNN7EXAMPLE",
    "ASIAIOSFODNN7EXAMPLE",
}
ARN_ACCOUNT_RE = re.compile(r"arn:aws[a-z\-]*:[^:]*:[^:]*:(\d{12}):")


def check_placeholders(staged: bool) -> Findings:
    """No real credentials, and no real AWS account ids in example ARNs."""
    findings = Findings("placeholders")
    patterns = [(re.compile(p), label) for p, label in SECRET_PATTERNS]
    exts = (".md", ".yaml", ".yml", ".json", ".sh", ".py", ".tf", ".rego", ".hcl")

    for path in iter_files(exts, staged):
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            for regex, label in patterns:
                match = regex.search(line)
                if match and match.group(0) not in DOCUMENTED_EXAMPLES:
                    findings.add(path, lineno, f"possible {label} in a template")
            for account in ARN_ACCOUNT_RE.findall(line):
                if account not in PLACEHOLDER_ACCOUNTS:
                    findings.add(
                        path,
                        lineno,
                        f"non-placeholder AWS account id {account} in an ARN",
                    )

    return findings


# --------------------------------------------------------------------------
# Check: shell runbooks are executable and syntactically valid
# --------------------------------------------------------------------------


def check_shell(staged: bool) -> Findings:
    """Runbooks must parse under `bash -n` and carry the executable bit.

    A runbook that is not executable is a runbook nobody can run under
    incident pressure, which is the only time these are read.
    """
    findings = Findings("shell")

    for path in iter_files((".sh",), staged):
        result = subprocess.run(
            ["bash", "-n", str(path)], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            detail = result.stderr.strip().splitlines()
            findings.add(path, None, f"bash syntax error: {detail[0] if detail else ''}")

        mode = subprocess.run(
            ["git", "ls-files", "-s", "--", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split()
        if mode and mode[0] == "100644":
            findings.add(path, None, "not executable; run: git update-index --chmod=+x")

    return findings


# --------------------------------------------------------------------------
# Check: shell scripts pass shellcheck
# --------------------------------------------------------------------------


def check_shellcheck(staged: bool) -> Findings:
    """Runbooks must pass shellcheck at error severity.

    Warnings and style notes are not enforced: these are illustrative templates
    that an adopter edits, and style-linting somebody else's starting point is
    noise. Errors are real defects.
    """
    findings = Findings("shellcheck")

    if not _have("shellcheck"):
        findings.problems.append(
            "shellcheck not installed; install it to verify runbooks "
            "(brew install shellcheck / apt install shellcheck)"
        )
        return findings

    files = iter_files((".sh",), staged) + [
        p for p in iter_files(("",), staged) if p.name in {"agent-bwrap", "mcp-launch", "launch-agent"}
    ]
    for path in files:
        result = subprocess.run(
            ["shellcheck", "--severity=error", "--format=gcc", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in result.stdout.splitlines():
            parts = line.split(":", 3)
            if len(parts) >= 4:
                findings.add(path, int(parts[1]) if parts[1].isdigit() else None, parts[3].strip())

    return findings


# --------------------------------------------------------------------------
# Check: Kyverno policies load and enforce what they claim
# --------------------------------------------------------------------------


def check_policies(staged: bool) -> Findings:
    """Run the Kyverno CLI test suite in tests/kyverno/.

    This is the check that distinguishes a verified control from an asserted
    one. It needs no cluster: the Kyverno CLI evaluates policies against
    fixture resources offline, and the suite asserts both that bad manifests
    are denied and that good ones are admitted. The second half matters more.
    A policy that denies everything is an outage, not a control, and that is
    exactly the defect this suite found on its first run.
    """
    findings = Findings("policies")
    suite = REPO_ROOT / "tests" / "kyverno"

    if not suite.is_dir():
        findings.add(REPO_ROOT, None, "tests/kyverno/ is missing")
        return findings

    if not _have("kyverno"):
        findings.problems.append(
            "kyverno CLI not installed; policies are unverified. "
            "Install: https://kyverno.io/docs/kyverno-cli/"
        )
        return findings

    result = subprocess.run(
        ["kyverno", "test", str(suite)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        for line in result.stdout.splitlines():
            if "Want " in line or "Test Summary" in line:
                findings.add(suite, None, line.strip().strip("│").strip())
        if not findings.problems:
            findings.add(suite, None, f"kyverno test failed: {result.stderr.strip()[:200]}")

    return findings


def _have(tool: str) -> bool:
    """True if `tool` is on PATH."""
    return shutil.which(tool) is not None


def check_site(staged: bool) -> Findings:
    """The site generator must still consume the YAML it reads.

    The site is a second surface over the same source, so a schema change in
    any matrix file breaks it silently. This runs the generator's own input
    validation, which writes nothing.
    """
    findings = Findings("site")
    builder = REPO_ROOT / "site" / "build.py"
    if not builder.is_file():
        return findings

    result = subprocess.run(
        [sys.executable, str(builder), "--check"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        for line in (result.stderr or result.stdout).splitlines():
            if line.strip():
                findings.add(builder, None, line.strip().replace("PROBLEM ", ""))
    return findings


def check_diagrams(staged: bool) -> Findings:
    """Committed SVGs must match what assets/build-diagrams.py produces.

    The figures restate claims that also appear in the prose. A diagram that
    has drifted from its generator is the same failure as a README number that
    no longer matches the tree, and it is harder to notice because nobody
    diffs an image.
    """
    findings = Findings("diagrams")
    builder = REPO_ROOT / "assets" / "build-diagrams.py"
    if not builder.is_file():
        return findings

    result = subprocess.run(
        [sys.executable, str(builder), "--check"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        for line in (result.stderr or result.stdout).splitlines():
            if line.strip():
                findings.add(builder, None, line.strip())
    return findings


# Root holds meta only. Measured against the top-starred repos and comparable
# engineering repos: their root file counts are high (Rust 33, Kyverno 32) but
# almost all of it is dotfiles and build config. Every root markdown file in all
# eight comparators is ABOUT the project. None puts the product at root. The
# median document count there is 7; this repo had 20 before the split.
ROOT_ALLOWED = {
    "README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md",
    "CHANGELOG.md", "AGENTS.md", "CLAUDE.md",
    "LICENSE", "LICENSE-CODE", "LICENSE-CONTENT",
}


def check_root(staged: bool) -> Findings:
    """Root may hold meta files only, and docs/ stays a reserved public path."""
    findings = Findings("root")

    tracked = subprocess.run(
        ["git", "ls-files", "--cached"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.split()
    root_files = [f for f in tracked if "/" not in f]

    for name in sorted(root_files):
        if name.startswith("."):
            continue  # dotfiles are infrastructure; every comparator has them
        if name not in ROOT_ALLOWED:
            findings.add(
                REPO_ROOT / name, None,
                "content at repository root. If a visitor would read it for its "
                "own sake it belongs in a directory (framework/, briefing/, data/)",
            )

    # docs/ is what readers and tooling expect to be public documentation.
    # Using it for gitignored working notes puts unpublishable material on the
    # one path everyone assumes is publishable.
    if (REPO_ROOT / "docs").exists():
        findings.add(REPO_ROOT / "docs", None,
                     "docs/ is a reserved public path; private notes belong in .notes/")

    if not (REPO_ROOT / ".github").is_dir():
        findings.add(REPO_ROOT, None, ".github/ is absent; 8 of 8 comparable repos have one")

    return findings


CHECKS: dict[str, Callable[[bool], Findings]] = {
    "root": check_root,
    "diagrams": check_diagrams,
    "site": check_site,
    "links": check_links,
    "yaml": check_yaml,
    "json": check_json,
    "prose": check_prose,
    "placeholders": check_placeholders,
    "shell": check_shell,
    "shellcheck": check_shellcheck,
    "policies": check_policies,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--staged",
        action="store_true",
        help="check only git-staged files (used by the pre-commit hook)",
    )
    parser.add_argument(
        "--only",
        choices=sorted(CHECKS),
        action="append",
        help="run only the named check; repeatable",
    )
    args = parser.parse_args()

    selected = args.only or sorted(CHECKS)
    failed: list[Findings] = []

    for name in selected:
        findings = CHECKS[name](args.staged)
        status = "ok" if findings.ok else f"{len(findings.problems)} problem(s)"
        print(f"[{'PASS' if findings.ok else 'FAIL'}] {name:<13} {status}")
        if not findings.ok:
            failed.append(findings)

    if failed:
        print()
        for findings in failed:
            print(f"--- {findings.name} ---")
            for problem in findings.problems:
                print(f"  {problem}")
        print()
        total = sum(len(f.problems) for f in failed)
        print(f"{total} problem(s) across {len(failed)} check(s).")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
