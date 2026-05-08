#!/usr/bin/env bash
# ABOUTME: Pipes Cilium Hubble L7 DNS denials to the SIEM. The egress-FQDN-allowlist denial signal.
# ABOUTME: Requires Cilium with enable-l7-proxy: true. Run as a long-running service.

set -euo pipefail

SIEM_URL="${SIEM_URL:-https://siem.example.com:9200/agent-sentinel-fqdn-deny/_doc}"
SIEM_TOKEN="${SIEM_TOKEN:?Set SIEM_TOKEN.}"
NAMESPACE_FILTER="${NAMESPACE_FILTER:-agent-}"

# Filter for L7 DNS proxy denials. Cilium emits these as drop verdicts on
# flows that hit the FQDN allowlist with no match.
hubble observe --type drop --output json --follow --namespace "${NAMESPACE_FILTER}" \
| jq --unbuffered -c 'select(.flow.l7 != null and .flow.l7.dns != null and .flow.verdict == "DROPPED")' \
| while IFS= read -r line; do
  curl -sS -X POST "$SIEM_URL" \
    -H "Authorization: Bearer ${SIEM_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$line" \
    >/dev/null
done
