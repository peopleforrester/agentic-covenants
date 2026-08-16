#!/usr/bin/env bash
# ABOUTME: PreToolUse hook that emits a structured JSON identity event to local syslog. Designed to chain ahead of pre_tool_use.sh.
# ABOUTME: Hashes the credential before logging; never logs the raw token.

set -euo pipefail

INPUT="$(cat)"
SESSION_ID="$(echo "$INPUT" | jq -r '.session_id // "unknown"')"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // "unknown"')"
TOOL_INPUT="$(echo "$INPUT" | jq -r '.tool_input.command // ""')"

# Hash the credential. Truncate to 16 hex chars (64 bits) -- long enough that
# collisions across the agent population are negligible, short enough not to
# reveal the full hash in logs.
CRED_HASH="$(printf '%s' "${ANTHROPIC_API_KEY:-}" | sha256sum | cut -d' ' -f1 | head -c 16)"
EFFECTIVE_UID="$(id -u)"
HOSTNAME="$(hostname -f 2>/dev/null || hostname)"
TIMESTAMP="$(date -Iseconds)"

EVENT="$(jq -n \
  --arg session "$SESSION_ID" \
  --arg tool "$TOOL_NAME" \
  --arg input "$TOOL_INPUT" \
  --arg cred "$CRED_HASH" \
  --argjson uid "$EFFECTIVE_UID" \
  --arg host "$HOSTNAME" \
  --arg ts "$TIMESTAMP" \
  '{event: "identity", session: $session, tool: $tool, input: $input, cred_fingerprint: $cred, uid: $uid, host: $host, ts: $ts}')"

logger -t agent-sentinel -p user.info "$EVENT"

# Pass the original input through to the next hook in the chain. PreToolUse
# hooks are expected to echo the input for downstream consumers.
echo "$INPUT"
exit 0
