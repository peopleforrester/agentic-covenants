#!/usr/bin/env bash
# ABOUTME: Applies the per-agent namespace stack in dependency order, idempotently.
# ABOUTME: Refuses to continue when a step did not take, rather than reporting success.
set -euo pipefail

# Order matters and is not cosmetic. The Pod Security label is evaluated at
# admission and not applied retroactively, so it must exist before the first
# pod. The default-deny NetworkPolicy must land before the allowlist, or the
# namespace is permissive in between. Applying the whole file at once hands
# that ordering to the API server, so each step is applied and then checked.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
TEMPLATE="$HERE/agent-namespace.yaml"

VERIFY_ONLY=0
[ "${1:-}" = "--verify" ] && { VERIFY_ONLY=1; shift; }

AGENT="${1:-}"
if [ -z "$AGENT" ]; then
    echo "usage: bootstrap.sh [--verify] <agent-name>" >&2
    exit 64
fi

case "$AGENT" in
    agent-*) ;;
    *)  echo "bootstrap: agent name must start with 'agent-'." >&2
        echo "  The admission policies and the audit policy both select on that" >&2
        echo "  prefix, so an agent named otherwise is silently ungoverned." >&2
        exit 64 ;;
esac

command -v kubectl  >/dev/null 2>&1 || { echo "bootstrap: kubectl not found" >&2; exit 69; }
command -v python3  >/dev/null 2>&1 || { echo "bootstrap: python3 not found" >&2; exit 69; }

# Emit only the documents of one kind, optionally filtered by name, with
# AGENT_NAME substituted. Kept as one helper so the ordering below reads as
# ordering rather than as YAML plumbing.
select_docs() {
    local kind="$1" name="${2:-}"
    sed "s/AGENT_NAME/$AGENT/g" "$TEMPLATE" | python3 -c '
import sys, yaml
kind = sys.argv[1]
name = sys.argv[2] if len(sys.argv) > 2 else ""
docs = [
    d for d in yaml.safe_load_all(sys.stdin)
    if d and d.get("kind") == kind and (not name or d["metadata"]["name"] == name)
]
if not docs:
    sys.exit(f"select_docs: no {kind} {name} in template")
print(yaml.safe_dump_all(docs))
' "$kind" "$name"
}

# Apply, then confirm the object is actually present. A kubectl exit code of 0
# says the request was accepted, not that the object exists and matches, and
# that distinction is the whole point of an ordered install.
apply_step() {
    local kind="$1" name="${2:-$AGENT}" scope="${3:-namespaced}"
    select_docs "$kind" "$name" | kubectl apply -f - >/dev/null
    if [ "$scope" = "cluster" ]; then
        kubectl get "$kind" "$name" >/dev/null 2>&1 || {
            echo "  FAILED: $kind/$name did not appear after apply" >&2; exit 1; }
    else
        kubectl get "$kind" "$name" -n "$AGENT" >/dev/null 2>&1 || {
            echo "  FAILED: $kind/$name did not appear in $AGENT after apply" >&2; exit 1; }
    fi
    echo "  ok  $kind/$name"
}

if [ "$VERIFY_ONLY" -eq 1 ]; then
    exec "$HERE/verify.sh" "$AGENT"
fi

echo "==> 1. namespace (Pod Security label must precede the first pod)"
apply_step Namespace "$AGENT" cluster

echo "==> 2. identity"
apply_step ServiceAccount

echo "==> 3. authorization (namespace-scoped, never a ClusterRole)"
apply_step Role
apply_step RoleBinding

echo "==> 4. resource bounds"
apply_step ResourceQuota
apply_step LimitRange

echo "==> 5. network: deny first, then allow"
apply_step NetworkPolicy default-deny
apply_step NetworkPolicy agent-egress-allowlist

cat <<MSG

==> per-agent stack applied for $AGENT

Cluster-wide, applied once rather than per agent:

  kubectl apply -f $HERE/kyverno-multi-agent.yaml
  kubectl apply -f $REPO/controls/authorization/server-side/kyverno-no-cluster-roles.yaml
  kubectl apply -f $REPO/controls/supply-chain/server-side/kyverno-verify-image-signatures.yaml
  kubectl apply -f $REPO/sentinels/identity/server-side/audit-policy.yaml

Then prove it:

  $HERE/verify.sh $AGENT
MSG
