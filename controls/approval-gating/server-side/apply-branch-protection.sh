#!/usr/bin/env bash
# ABOUTME: Applies the desired branch-protection state via gh api. Asserts enforce_admins=true and refuses without it.
# ABOUTME: Run once per repo. UI clicks are not auditable; this script is.

set -euo pipefail

REPO="${1:-}"
BRANCH="${2:-main}"
EXPECTED_JSON="${3:-$(dirname "$0")/branch-protection-expected.json}"

if [[ -z "$REPO" ]]; then
  cat <<'USAGE' >&2
Usage: apply-branch-protection.sh <owner/repo> [branch] [expected-json-path]

Example:
  apply-branch-protection.sh peopleforrester/agentic-covenants main ./branch-protection-expected.json

The script reads the expected JSON, asserts enforce_admins=true (refuses
otherwise), and applies the configuration via gh api. After applying it
re-reads the live state and diffs it against the expected JSON.
USAGE
  exit 64
fi

if [[ ! -r "$EXPECTED_JSON" ]]; then
  echo "Cannot read expected JSON at $EXPECTED_JSON" >&2
  exit 1
fi

ENFORCE_ADMINS="$(jq -r '.enforce_admins' "$EXPECTED_JSON")"
if [[ "$ENFORCE_ADMINS" != "true" ]]; then
  echo "REFUSING: expected JSON has enforce_admins=$ENFORCE_ADMINS." >&2
  echo "enforce_admins=true is the load-bearing flag for branch protection." >&2
  echo "Edit $EXPECTED_JSON to set it true before applying." >&2
  exit 1
fi

REQ_REVIEWERS="$(jq -r '.required_pull_request_reviews.required_approving_review_count // 0' "$EXPECTED_JSON")"
if [[ "$REQ_REVIEWERS" -lt 2 ]]; then
  echo "REFUSING: required_approving_review_count=$REQ_REVIEWERS." >&2
  echo "One reviewer plus the agent operating the keyboard equals zero adversarial review." >&2
  echo "Set required_approving_review_count to at least 2." >&2
  exit 1
fi

echo "Applying branch protection on $REPO@$BRANCH from $EXPECTED_JSON ..."

# gh api PUT on the protection endpoint accepts the full JSON body.
gh api -X PUT \
  "repos/$REPO/branches/$BRANCH/protection" \
  --input "$EXPECTED_JSON"

echo "Applied. Re-reading live state for verification..."

LIVE="$(gh api "repos/$REPO/branches/$BRANCH/protection")"

# Verify a small set of critical fields.
LIVE_ENFORCE_ADMINS="$(echo "$LIVE" | jq -r '.enforce_admins.enabled')"
LIVE_REQ_REVIEWERS="$(echo "$LIVE" | jq -r '.required_pull_request_reviews.required_approving_review_count')"
LIVE_CODEOWNERS="$(echo "$LIVE" | jq -r '.required_pull_request_reviews.require_code_owner_reviews')"

PASS=0
FAIL=0
check() { if [[ "$2" == "$3" ]]; then echo "PASS: $1 = $2"; PASS=$((PASS+1)); else echo "FAIL: $1: expected $3, got $2"; FAIL=$((FAIL+1)); fi; }

check "enforce_admins.enabled"                                    "$LIVE_ENFORCE_ADMINS" "true"
check "required_pull_request_reviews.required_approving_review_count" "$LIVE_REQ_REVIEWERS"  "$REQ_REVIEWERS"
check "required_pull_request_reviews.require_code_owner_reviews"  "$LIVE_CODEOWNERS"     "true"

echo ""
echo "Summary: $PASS passed, $FAIL failed"
exit "$FAIL"
