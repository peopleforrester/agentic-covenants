#!/usr/bin/env bash
# ABOUTME: Pipes Hubble flow drops to the SIEM as JSON. Run as a long-running systemd service or DaemonSet sidecar.
# ABOUTME: Without flow export wired up, Hubble is visible only in its own UI and provides no SIEM signal.

set -euo pipefail

SIEM_URL="${SIEM_URL:-https://siem.example.com:9200/agent-sentinel-network/_doc}"
SIEM_TOKEN="${SIEM_TOKEN:?Set SIEM_TOKEN in the environment.}"
NAMESPACE_FILTER="${NAMESPACE_FILTER:-agent-}"

# Stream drops only; allowed flows are too noisy. Add --type policy-verdict
# if you want allow flows for forensic baselining.
hubble observe --type drop --output json --follow --namespace "${NAMESPACE_FILTER}" \
| while IFS= read -r line; do
  curl -sS -X POST "$SIEM_URL" \
    -H "Authorization: Bearer ${SIEM_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$line" \
    >/dev/null
done
