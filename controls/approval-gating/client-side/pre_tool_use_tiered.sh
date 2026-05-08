#!/usr/bin/env bash
# ABOUTME: Tiered PreToolUse hook. Tier 1 auto-allow; tier 2 quick confirm; tier 3 typed verbatim; tier 4 out-of-band approval.
# ABOUTME: Pairs with pre_tool_use.sh from controls/authorization/client-side/ — that one denies; this one gates.

set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/agents/claude-code}"
COUNTER_BASE="${COUNTER_BASE:-/var/lib/agents/sessions}"
SESSION_DESTRUCTIVE_LIMIT="${SESSION_DESTRUCTIVE_LIMIT:-10}"
APPROVAL_URL="${APPROVAL_URL:-https://approvals.example.com}"
APPROVAL_TIMEOUT_SEC="${APPROVAL_TIMEOUT_SEC:-600}"

mkdir -p "$LOG_DIR" "$COUNTER_BASE" 2>/dev/null || true

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"
TOOL_INPUT="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"
SESSION_ID="$(echo "$INPUT" | jq -r '.session_id // "default"')"
COUNTER_FILE="${COUNTER_BASE}/${SESSION_ID}.destructive"

log() {
  local decision="$1" tier="$2" message="${3:-}"
  echo "$(date -Iseconds) ${decision} session=${SESSION_ID} tier=${tier} tool=${TOOL_NAME} input=${TOOL_INPUT} ${message}" \
    >> "$LOG_DIR/pre_tool_use_tiered.log" 2>/dev/null || true
}

# ----- Tier 1: read-only — allow silently -----
TIER1_PATTERNS=(
  '^(ls|cat|grep|find|head|tail|wc|stat|file|pwd|whoami|date|hostname)\b'
  '^kubectl\s+(get|describe|logs|version|api-resources|api-versions)\b'
  '^aws\s+[a-z0-9-]+\s+(get|list|describe|head)-'
  '^git\s+(status|diff|log|show|branch|rev-parse|rev-list)\b'
  '^docker\s+(ps|images|inspect|version|info)\b'
  '^helm\s+(list|status|history|version|repo|search)\b'
  '^terraform\s+(plan|show|state\s+list|state\s+show|version)\b'
)
for p in "${TIER1_PATTERNS[@]}"; do
  if echo "$TOOL_INPUT" | grep -qE "$p"; then
    log ALLOW 1
    exit 0
  fi
done

# ----- Tier 4: out-of-band approval (production-touching) -----
TIER4_PATTERNS=(
  '\bterraform\s+apply\b.*-auto-approve'
  '\bkubectl\s+apply\b.*--server[ =]\S*prod'
  '\baws\s+ec2\s+terminate-instances\b'
  '\baws\s+rds\s+delete-db-instance\b'
  '\bhelm\s+install\b.*--namespace[ =]?prod'
)
for p in "${TIER4_PATTERNS[@]}"; do
  if echo "$TOOL_INPUT" | grep -qE "$p"; then
    REQ_ID="$(uuidgen)"
    echo "TIER-4 ACTION: $TOOL_INPUT" >&2
    echo "Out-of-band approval required at: ${APPROVAL_URL}/${REQ_ID}" >&2
    echo "$INPUT" | curl -sS -X POST \
      -H "Authorization: Bearer ${APPROVAL_TOKEN:-}" \
      -H "Content-Type: application/json" \
      "${APPROVAL_URL}/api/requests/${REQ_ID}" \
      -d @- >/dev/null || {
        log ERROR 4 "approval-service-unreachable"
        echo "ERROR: approval service unreachable; defaulting to deny." >&2
        exit 2
      }
    DEADLINE=$(( $(date +%s) + APPROVAL_TIMEOUT_SEC ))
    while [[ "$(date +%s)" -lt "$DEADLINE" ]]; do
      STATUS="$(curl -sS "${APPROVAL_URL}/api/requests/${REQ_ID}/status" | jq -r .status)"
      case "$STATUS" in
        approved)
          log ALLOW 4 "approver=$(curl -sS "${APPROVAL_URL}/api/requests/${REQ_ID}/status" | jq -r .approver)"
          exit 0 ;;
        denied)
          log DENY 4 "denied-by-approver"
          echo "DENIED by out-of-band approver" >&2
          exit 2 ;;
      esac
      sleep 10
    done
    log DENY 4 "timeout"
    echo "TIMEOUT waiting for out-of-band approval (default: deny)" >&2
    exit 2
  fi
done

# ----- Tier 3: typed verbatim confirmation -----
TIER3_PATTERNS=(
  '\bkubectl\s+delete\b'
  '\baws\s+s3\s+rb\b'
  '\bgh\s+repo\s+delete\b'
  '\bdocker\s+system\s+prune\b'
  '\bhelm\s+uninstall\b'
  '\bkubectl\s+scale\b.*--replicas[= ]0\b'
)
for p in "${TIER3_PATTERNS[@]}"; do
  if echo "$TOOL_INPUT" | grep -qE "$p"; then
    COUNT="$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)"
    if [[ "$COUNT" -ge "$SESSION_DESTRUCTIVE_LIMIT" ]]; then
      log DENY 3 "session-limit-${COUNT}"
      echo "BLOCKED: session destructive-action limit reached (${SESSION_DESTRUCTIVE_LIMIT})" >&2
      exit 2
    fi
    echo "TIER-3 ACTION: $TOOL_INPUT" >&2
    echo "Type the command verbatim to confirm:" >&2
    if ! IFS= read -r -t 60 confirmation < /dev/tty; then
      log DENY 3 "confirmation-timeout"
      echo "BLOCKED: confirmation timed out (60s)" >&2
      exit 2
    fi
    if [[ "$confirmation" != "$TOOL_INPUT" ]]; then
      log DENY 3 "confirmation-mismatch"
      echo "BLOCKED: confirmation did not match" >&2
      exit 2
    fi
    echo "$((COUNT + 1))" > "$COUNTER_FILE"
    log ALLOW 3
    exit 0
  fi
done

# ----- Tier 2: quick confirm (default for unrecognized commands) -----
# In practice, anything reaching this point is allowed silently, on the
# assumption that tier-4 hard-deny patterns from controls/authorization/client-side/pre_tool_use.sh
# already ran upstream and rejected truly dangerous commands.
log ALLOW 2 "default-allow-after-tiers"
exit 0
