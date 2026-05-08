#!/usr/bin/env bash
# ABOUTME: Append-only snippet for the deny-then-ask-then-allow hook. Emits a structured decision event before exit.
# ABOUTME: Source this from pre_tool_use.sh after the decision is reached but before the script exits.

emit_decision() {
  # Args:
  #   $1 = decision (allow|ask|deny|error)
  #   $2 = pattern (the rule that matched, or "default" for no-match)
  local decision="$1"
  local pattern="${2:-default}"

  # SESSION_ID, TOOL_NAME, TOOL_INPUT are set by the calling hook.
  local event
  event="$(jq -n \
    --arg session "${SESSION_ID:-unknown}" \
    --arg tool "${TOOL_NAME:-unknown}" \
    --arg input "${TOOL_INPUT:-}" \
    --arg decision "$decision" \
    --arg pattern "$pattern" \
    --arg ts "$(date -Iseconds)" \
    '{event: "hook_decision", session: $session, tool: $tool, input: $input, decision: $decision, pattern: $pattern, ts: $ts}')"

  logger -t agent-sentinel -p user.info "$event"
}

# Usage in your pre_tool_use.sh:
#
#   . /etc/agents/hooks/hook-decision-emit.sh
#
#   for pattern in "${DENY_PATTERNS[@]}"; do
#     if echo "$TOOL_INPUT" | grep -qE "$pattern"; then
#       emit_decision deny "$pattern"
#       exit 2
#     fi
#   done
#
#   emit_decision allow "default"
#   exit 0
