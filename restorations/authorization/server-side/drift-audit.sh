#!/usr/bin/env bash
# ABOUTME: Drift-detection helper. Lists Kubernetes resources in a namespace not present in the declarative source-of-truth.
# ABOUTME: Anything in cluster but not in source is suspect after a recovery; review and decide delete or capture.

set -euo pipefail

NAMESPACE="${1:-}"
MANIFESTS_DIR="${MANIFESTS_DIR:-./manifests}"

if [[ -z "$NAMESPACE" ]]; then
  echo "Usage: drift-audit.sh <NAMESPACE>" >&2
  exit 64
fi

# Resource kinds worth auditing. Add or remove for your environment.
KINDS=(
  configmaps secrets serviceaccounts
  roles rolebindings
  deployments daemonsets statefulsets
  services networkpolicies
  pods
)

echo "Drift audit for namespace: $NAMESPACE"
echo "Source manifests: $MANIFESTS_DIR"
echo

for kind in "${KINDS[@]}"; do
  mapfile -t CLUSTER_NAMES < <(
    kubectl get "$kind" -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null \
      | tr ' ' '\n' | sort -u
  )

  for name in "${CLUSTER_NAMES[@]}"; do
    [[ -z "$name" ]] && continue
    # Heuristic: assume manifest filename pattern is <name>-<kind>.yaml or <kind>/<name>.yaml.
    # Drift detection here is a starter; tighten for your repo layout.
    if ! grep -rqE "^\s*name:\s*$name\s*$" "$MANIFESTS_DIR" 2>/dev/null; then
      echo "DRIFT: $kind/$name in cluster but not referenced in $MANIFESTS_DIR/"
    fi
  done
done

echo
echo "Review each DRIFT line. Anything not deliberate during recovery should be deleted."
