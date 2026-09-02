#!/usr/bin/env bash
# ABOUTME: Proves each control denies what it claims and admits what the agent needs.
# ABOUTME: The admit half is what catches an over-broad policy that quietly breaks the agent.
set -uo pipefail

# Both directions, always. A cluster where the agent can do nothing is not
# governed, it is broken, and the two are indistinguishable from a green check
# that only tested denials. An over-broad NetworkPolicy or a Role that denies
# the agent's actual job is the failure that gets the control switched off next
# quarter, so it is worth failing the check here instead.

AGENT="${1:-}"
[ -n "$AGENT" ] || { echo "usage: verify.sh <agent-name>" >&2; exit 64; }
command -v kubectl >/dev/null 2>&1 || { echo "verify: kubectl not found" >&2; exit 69; }

SA="system:serviceaccount:${AGENT}:${AGENT}"
PASS=0
FAIL=0

# kubectl auth can-i answers from the API server's own authorizer, so this
# tests the real RBAC decision rather than re-reading the Role and hoping.
expect() {
    local want="$1" verb="$2" resource="$3" label="$4"
    shift 4
    local got
    got="$(kubectl auth can-i "$verb" "$resource" --as="$SA" -n "$AGENT" "$@" 2>/dev/null)" || got="no"
    if [ "$got" = "$want" ]; then
        printf '  [%-5s] %s\n' "$([ "$want" = no ] && echo deny || echo admit)" "$label"
        PASS=$((PASS + 1))
    else
        printf '  [FAIL ] %s (wanted %s, got %s)\n' "$label" "$want" "$got"
        FAIL=$((FAIL + 1))
    fi
}

echo "RBAC, as $SA"

# --- must be denied ---
expect no  create deployments.apps "agent cannot create a Deployment in its own namespace"
expect no  get    secrets          "agent cannot read Secrets"
expect no  delete pods             "agent cannot delete Pods"
expect no  create clusterrolebindings.rbac.authorization.k8s.io "agent cannot bind cluster roles"

# --- must be admitted, or the agent cannot do its job ---
expect yes list pods      "agent can list Pods in its own namespace"
expect yes get  pods/log  "agent can read its own Pod logs"
expect yes list configmaps "agent can list ConfigMaps"

echo
echo "Cross-namespace isolation"
OTHER="$(kubectl get ns -l agentic-covenants.io/role=agent -o name 2>/dev/null \
         | grep -v "namespace/${AGENT}$" | head -1 | cut -d/ -f2)"
if [ -n "$OTHER" ]; then
    got="$(kubectl auth can-i list pods --as="$SA" -n "$OTHER" 2>/dev/null)" || got="no"
    if [ "$got" = "no" ]; then
        printf '  [deny ] agent cannot list Pods in %s\n' "$OTHER"; PASS=$((PASS + 1))
    else
        printf '  [FAIL ] agent CAN list Pods in %s\n' "$OTHER"; FAIL=$((FAIL + 1))
    fi
else
    printf '  [skip ] only one agent namespace exists; isolation is untested\n'
    printf '          This check is the reason the example is multi-agent. Create a\n'
    printf '          second agent before claiming tenant isolation holds.\n'
fi

echo
echo "Network policy presence"
for np in default-deny agent-egress-allowlist; do
    if kubectl get networkpolicy "$np" -n "$AGENT" >/dev/null 2>&1; then
        printf '  [ok   ] networkpolicy/%s\n' "$np"; PASS=$((PASS + 1))
    else
        printf '  [FAIL ] networkpolicy/%s missing\n' "$np"; FAIL=$((FAIL + 1))
    fi
done

cat <<'NOTE'

  Presence is not enforcement. NetworkPolicy is inert unless the CNI
  implements it, and a cluster with a non-enforcing CNI accepts these objects
  and drops nothing. Confirm egress is actually blocked from inside:

    kubectl run egress-probe --rm -i --restart=Never -n <agent-ns> \
      --overrides='{"spec":{"serviceAccountName":"<agent-ns>"}}' \
      --image=curlimages/curl:8.11.1 \
      -- curl -s --max-time 5 https://example.invalid \
      && echo "FAIL: egress permitted" || echo "ok: egress denied"
NOTE

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
