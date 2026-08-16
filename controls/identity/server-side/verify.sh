#!/usr/bin/env bash
# ABOUTME: Verifies server-side identity controls: dedicated SA, short TTL, identity-bound IAM, cross-agent isolation.
# ABOUTME: Run with kubectl context targeting the cluster. Exits non-zero on any failed check.

set -euo pipefail

NAMESPACE="${1:-agent-claude-prod}"
SA_NAME="${2:-claude-code}"
PASS=0
FAIL=0

check() {
  local name="$1" result="$2"
  if [[ "$result" == "ok" ]]; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name -- $result"
    FAIL=$((FAIL + 1))
  fi
}

# 1. Dedicated identity per agent
SA_COUNT=$(kubectl get sa -A -o jsonpath='{.items[*].metadata.name}' \
  | tr ' ' '\n' | grep -cx "$SA_NAME" || true)
if [[ "$SA_COUNT" -eq 1 ]]; then
  check "ServiceAccount $SA_NAME exists exactly once cluster-wide" "ok"
else
  check "ServiceAccount $SA_NAME exists exactly once cluster-wide" "found in $SA_COUNT namespaces (must be 1)"
fi

# 2. Token TTL is 15 minutes (900s) or shorter
POD=$(kubectl get pod -n "$NAMESPACE" -l app="$SA_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
if [[ -z "$POD" ]]; then
  check "agent Pod found in $NAMESPACE" "no Pod with label app=$SA_NAME"
else
  TTL=$(kubectl get pod -n "$NAMESPACE" "$POD" -o jsonpath='{.spec.volumes[?(@.projected)].projected.sources[?(@.serviceAccountToken)].serviceAccountToken.expirationSeconds}')
  if [[ -z "$TTL" ]]; then
    check "projected token TTL is set" "no expirationSeconds on the projected ServiceAccountToken"
  elif [[ "$TTL" -le 900 ]]; then
    check "projected token TTL is <= 900s ($TTL)" "ok"
  else
    check "projected token TTL is <= 900s" "TTL is ${TTL}s (must be <= 900)"
  fi
fi

# 3. AWS role assumption is identity-bound (only runs if AWS_PROFILE is set)
if [[ -n "${AWS_PROFILE:-}" ]] && command -v aws >/dev/null 2>&1; then
  ROLE_ARN=$(aws --profile "$AWS_PROFILE" sts get-caller-identity --query Arn --output text 2>/dev/null || true)
  if [[ "$ROLE_ARN" == *":role/${SA_NAME}-"* || "$ROLE_ARN" == *":role/${SA_NAME}/"* || "$ROLE_ARN" == *":assumed-role/${SA_NAME}-"* ]]; then
    check "AWS role assumption returns dedicated role ($ROLE_ARN)" "ok"
  else
    check "AWS role assumption returns dedicated role" "got $ROLE_ARN"
  fi
fi

# 4. Cross-agent isolation: this agent's pod cannot read another agent's token
OTHER_NS=$(kubectl get ns -l agentic-covenants.io/role=agent -o jsonpath='{.items[*].metadata.name}' \
  | tr ' ' '\n' | grep -vx "$NAMESPACE" | head -1 || true)
if [[ -n "$OTHER_NS" && -n "$POD" ]]; then
  if kubectl exec -n "$NAMESPACE" "$POD" -- ls "/var/run/secrets/${OTHER_NS}/" 2>/dev/null | grep -q .; then
    check "agent cannot see another agent's token volume" "found another agent's token mount"
  else
    check "agent cannot see another agent's token volume" "ok"
  fi
fi

echo ""
echo "Summary: $PASS passed, $FAIL failed"
exit "$FAIL"
