#!/usr/bin/env bash
# ABOUTME: Probes GitHub repository SETTINGS, which are invisible in the repo and drift silently.
# ABOUTME: Reading the workflow file cannot tell you any of this; the settings API can.
set -uo pipefail

# Everything in the repository is a proposal. Only the forge's settings are a
# control, and they are exactly what drifts, because changing them leaves no
# diff for anyone to review. This script asks the settings API directly.

REPO="${1:-}"
if [ -z "$REPO" ]; then
    REPO="$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || true)"
fi
[ -n "$REPO" ] || { echo "usage: verify.sh <owner/repo>" >&2; exit 64; }
command -v gh >/dev/null 2>&1 || { echo "verify: gh not found" >&2; exit 69; }

PASS=0; FAIL=0; UNKNOWN=0
ok()   { printf '  [ok     ] %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  [FAIL   ] %s\n' "$1"; FAIL=$((FAIL+1)); }
unk()  { printf '  [unknown] %s\n' "$1"; UNKNOWN=$((UNKNOWN+1)); }

echo "Forge settings for $REPO"
echo

# --- default token scope -------------------------------------------------
# The single highest-value setting. A write-all default means every job that
# omits a permissions: block runs with a token that can push.
perms="$(gh api "repos/$REPO/actions/permissions/workflow" 2>/dev/null)" || perms=""
if [ -z "$perms" ]; then
    unk "default workflow token scope (no access to the settings API)"
else
    scope="$(printf '%s' "$perms" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("default_workflow_permissions",""))')"
    approve="$(printf '%s' "$perms" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("can_approve_pull_request_reviews"))')"
    [ "$scope" = "read" ] \
        && ok "default workflow token is read-scoped" \
        || bad "default workflow token is '$scope'; a job without a permissions: block can push"
    [ "$approve" = "False" ] \
        && ok "Actions cannot approve pull requests" \
        || bad "Actions CAN approve pull requests, so a bot can satisfy its own review gate"
fi

# --- branch protection ---------------------------------------------------
branch="$(gh api "repos/$REPO" --jq .default_branch 2>/dev/null || echo main)"
prot="$(gh api "repos/$REPO/branches/$branch/protection" 2>/dev/null)" || prot=""
if [ -z "$prot" ]; then
    bad "$branch is not protected, so an agent PR can be merged without review"
else
    admins="$(printf '%s' "$prot" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("enforce_admins",{}).get("enabled"))')"
    reviews="$(printf '%s' "$prot" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("required_pull_request_reviews",{}).get("required_approving_review_count",0))')"
    owners="$(printf '%s' "$prot" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("required_pull_request_reviews",{}).get("require_code_owner_reviews"))')"
    [ "$admins" = "True" ] && ok "enforce_admins is on for $branch" \
                           || bad "enforce_admins is off; an admin can push straight to $branch"
    [ "${reviews:-0}" -ge 1 ] 2>/dev/null && ok "$reviews approving review(s) required" \
                                          || bad "no approving review required on $branch"
    [ "$owners" = "True" ] && ok "code owner review required" \
                           || bad "code owner review not required, so CODEOWNERS is advisory"
fi

# --- CODEOWNERS covers its own path -------------------------------------
# The loop this example is about: if CODEOWNERS does not reserve /.github/,
# the agent can propose a change to the rules that bound it.
co=""
for p in .github/CODEOWNERS CODEOWNERS docs/CODEOWNERS; do
    co="$(gh api "repos/$REPO/contents/$p" --jq .content 2>/dev/null | base64 -d 2>/dev/null)" && [ -n "$co" ] && break
done
if [ -z "$co" ]; then
    bad "no CODEOWNERS found, so no path requires a named reviewer"
else
    ok "CODEOWNERS present"
    printf '%s' "$co" | grep -qE '^\s*/?\.github/(workflows/)?\s' \
        && ok "CODEOWNERS reserves /.github/, so workflow changes need a reviewer" \
        || bad "CODEOWNERS does not cover /.github/; the agent can propose changing its own constraints"
fi

# --- environments with reviewers ----------------------------------------
envs="$(gh api "repos/$REPO/environments" 2>/dev/null)" || envs=""
if [ -z "$envs" ]; then
    unk "environments (no access, or none configured)"
else
    gated="$(printf '%s' "$envs" | python3 -c '
import sys, json
d = json.load(sys.stdin)
n = 0
for e in d.get("environments") or []:
    rules = e.get("protection_rules") or []
    if any(r.get("type") == "required_reviewers" for r in rules):
        n += 1
print(n)
')"
    [ "${gated:-0}" -ge 1 ] 2>/dev/null \
        && ok "$gated environment(s) have required reviewers" \
        || bad "no environment has required reviewers, so a gated apply job is not actually gated"
fi

echo
echo "  $PASS ok, $FAIL failed, $UNKNOWN unknown"
cat <<'NOTE'

  Unknown is not pass. It means this token could not read that setting, which
  is common for a fine-grained token or a repo you do not admin. Re-run with a
  token that can read repository administration before treating a clean result
  as a clean posture.
NOTE
[ "$FAIL" -eq 0 ]
