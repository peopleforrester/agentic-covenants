#!/usr/bin/env bash
# ABOUTME: Snippet that wraps the typed-confirmation read with timing measurement and emits a structured timing event.
# ABOUTME: Source from pre_tool_use_tiered.sh in place of the bare `read -r confirmation < /dev/tty`.

emit_approval_timing() {
  # Args:
  #   $1 = tier (numeric: 2, 3, 4)
  #   $2 = expected confirmation (the literal command, for typed-verbatim tiers)
  # Reads response from /dev/tty into the global confirmation variable.
  local tier="$1"
  local expected="$2"

  local start_ns end_ns response_ms matched
  start_ns="$(date +%s%N)"
  IFS= read -r confirmation < /dev/tty
  end_ns="$(date +%s%N)"
  response_ms=$(( (end_ns - start_ns) / 1000000 ))

  if [[ "$confirmation" == "$expected" ]]; then
    matched=true
  else
    matched=false
  fi

  local event
  event="$(jq -n \
    --arg session "${SESSION_ID:-default}" \
    --argjson tier "$tier" \
    --argjson response_ms "$response_ms" \
    --argjson matched "$matched" \
    --arg ts "$(date -Iseconds)" \
    '{event: "approval_timing", session: $session, tier: $tier, response_ms: $response_ms, matched: $matched, ts: $ts}')"
  logger -t agent-sentinel -p user.info "$event"
}

# Usage in pre_tool_use_tiered.sh:
#
#   . /etc/agents/hooks/approval-timing-emit.sh
#
#   echo "TIER-3 ACTION: $TOOL_INPUT" >&2
#   echo "Type the command verbatim to confirm:" >&2
#   emit_approval_timing 3 "$TOOL_INPUT"
#   if [[ "$confirmation" != "$TOOL_INPUT" ]]; then
#     ...
#   fi
