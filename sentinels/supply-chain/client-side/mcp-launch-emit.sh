#!/usr/bin/env bash
# ABOUTME: Snippet that the mcp-launch wrapper sources to emit a structured per-connection event with status and hash.
# ABOUTME: Source from controls/supply-chain/client-side/mcp-launch immediately after the hash check.

emit_mcp_connect() {
  # Args:
  #   $1 = server name
  #   $2 = status (ok | hash_mismatch | not_in_allowlist | signature_failed)
  #   $3 = actual sha256 (or "" if not computed)
  local name="$1" status="$2" sha="${3:-}"

  local event
  event="$(jq -n \
    --arg server "$name" \
    --arg status "$status" \
    --arg sha "$sha" \
    --arg ts "$(date -Iseconds)" \
    '{event: "mcp_connect", server: $server, status: $status, hash: $sha, ts: $ts}')"
  logger -t agent-sentinel -p user.info "$event"
}

# Usage in mcp-launch:
#
#   . /etc/agents/hooks/mcp-launch-emit.sh
#
#   if [[ -z "$EXPECTED_SHA" || ... ]]; then
#     emit_mcp_connect "$SERVER_NAME" "not_in_allowlist" ""
#     exit 2
#   fi
#   if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
#     emit_mcp_connect "$SERVER_NAME" "hash_mismatch" "$ACTUAL_SHA"
#     exit 2
#   fi
#   emit_mcp_connect "$SERVER_NAME" "ok" "$ACTUAL_SHA"
