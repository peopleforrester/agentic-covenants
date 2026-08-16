#!/usr/bin/env bash
# ABOUTME: Logs out-of-band approval decisions with the original request ID and session, so SIEM can reconstruct the chain.
# ABOUTME: Called by the OOB approval workflow (Slack approver action, FIDO2 prompt result, etc.) when a decision is made.

set -euo pipefail

REQ_ID="${1:?Missing request ID}"
DECISION="${2:?Missing decision (approved|denied|timeout)}"
APPROVER="${3:-unknown}"
SESSION_ID="${4:-unknown}"

case "$DECISION" in
  approved|denied|timeout) ;;
  *)
    echo "oob-decision-log: invalid decision '$DECISION' (must be approved|denied|timeout)" >&2
    exit 64
    ;;
esac

event="$(jq -n \
  --arg req "$REQ_ID" \
  --arg decision "$DECISION" \
  --arg approver "$APPROVER" \
  --arg session "$SESSION_ID" \
  --arg ts "$(date -Iseconds)" \
  '{event: "oob_approval", req_id: $req, decision: $decision, approver: $approver, session: $session, ts: $ts}')"

logger -t agent-sentinel -p user.info "$event"
