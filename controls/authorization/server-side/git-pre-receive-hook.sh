#!/usr/bin/env bash
# ABOUTME: Git server-side pre-receive hook. Cannot be bypassed by --no-verify. Install on every Git server in the org.
# ABOUTME: Blocks force-pushes to main, edits to protected paths from non-CODEOWNERS, and any diff containing secrets.

set -euo pipefail

PROTECTED_PATHS=(
  'infrastructure/prod/'
  '.github/workflows/'
  'secrets/'
  '.claude/'
)

ZERO_SHA="0000000000000000000000000000000000000000"
EXIT_CODE=0

while read -r oldrev newrev refname; do

  # 1. Reject force-pushes to main / master / release branches.
  case "$refname" in
    refs/heads/main|refs/heads/master|refs/heads/release/*)
      if [[ "$oldrev" != "$ZERO_SHA" && "$newrev" != "$ZERO_SHA" ]]; then
        if ! git merge-base --is-ancestor "$oldrev" "$newrev" 2>/dev/null; then
          echo "BLOCKED: force-push to ${refname} is not permitted" >&2
          EXIT_CODE=1
          continue
        fi
      fi
      ;;
  esac

  # Skip the per-commit checks on branch deletion.
  if [[ "$newrev" == "$ZERO_SHA" ]]; then
    continue
  fi

  # 2. Reject edits to protected paths from authors not listed in CODEOWNERS.
  if [[ "$oldrev" == "$ZERO_SHA" ]]; then
    # New branch: scan all reachable commits.
    CHANGED=$(git diff-tree --no-commit-id --name-only -r "$newrev")
  else
    CHANGED=$(git diff --name-only "$oldrev" "$newrev")
  fi

  AUTHOR_EMAIL=$(git log -1 --pretty=format:%ae "$newrev")

  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    for protected in "${PROTECTED_PATHS[@]}"; do
      if [[ "$path" == "$protected"* ]]; then
        if ! git show "$newrev:CODEOWNERS" 2>/dev/null \
            | grep -E "^\s*${protected}" \
            | grep -q "$AUTHOR_EMAIL"; then
          echo "BLOCKED: ${path} is a protected path; ${AUTHOR_EMAIL} is not in CODEOWNERS for it" >&2
          EXIT_CODE=1
        fi
      fi
    done
  done <<< "$CHANGED"

  # 3. Run gitleaks against the diff. Skipped if gitleaks is not installed
  # so the hook fails closed only on real findings, not infrastructure issues.
  if command -v gitleaks >/dev/null 2>&1; then
    DIFF_OUTPUT=$(git diff "$oldrev..$newrev" 2>/dev/null || true)
    if [[ -n "$DIFF_OUTPUT" ]]; then
      if ! echo "$DIFF_OUTPUT" \
          | gitleaks detect --source - --no-banner --no-color --exit-code 1 >/dev/null 2>&1; then
        echo "BLOCKED: secrets detected by gitleaks in ${refname} (${oldrev:0:8}..${newrev:0:8})" >&2
        EXIT_CODE=1
      fi
    fi
  else
    echo "WARN: gitleaks not installed on server; secret-scan step skipped" >&2
  fi

done

exit "$EXIT_CODE"
