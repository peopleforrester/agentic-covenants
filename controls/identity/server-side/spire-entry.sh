#!/usr/bin/env bash
# ABOUTME: Registers an agent's SPIFFE identity for cross-cluster workload attestation via SPIRE.
# ABOUTME: Optional. Use only when the agent operates across more than one cluster or off-cluster components.

set -euo pipefail

TRUST_DOMAIN="${TRUST_DOMAIN:-example.com}"
AGENT_NAME="${1:-claude-code-prod}"
NAMESPACE="${NAMESPACE:-agent-${AGENT_NAME}}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-claude-code}"
TTL_SECONDS="${TTL_SECONDS:-900}"

if ! command -v spire-server >/dev/null 2>&1; then
  echo "spire-server CLI not found in PATH." >&2
  echo "Install: https://spiffe.io/docs/latest/spire-about/getting-started/" >&2
  exit 1
fi

# Register the agent's SPIFFE ID. The selectors pin the identity to a
# specific Kubernetes ServiceAccount in a specific namespace; SPIRE will only
# issue an SVID to a workload that matches every selector.
spire-server entry create \
  -spiffeID "spiffe://${TRUST_DOMAIN}/agent/${AGENT_NAME}" \
  -parentID "spiffe://${TRUST_DOMAIN}/k8s_workload/${NAMESPACE}" \
  -selector "k8s:ns:${NAMESPACE}" \
  -selector "k8s:sa:${SERVICE_ACCOUNT}" \
  -selector "k8s:pod-label:app:${SERVICE_ACCOUNT}" \
  -ttl "$TTL_SECONDS"

echo "Registered spiffe://${TRUST_DOMAIN}/agent/${AGENT_NAME}"
echo "TTL: ${TTL_SECONDS}s. The agent must request fresh SVIDs from the SPIRE Workload API."
