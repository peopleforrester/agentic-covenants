#!/usr/bin/env bash
# ABOUTME: Claude Code PreToolUse hook with deny-then-ask-then-allow precedence.
# ABOUTME: Receives JSON on stdin. Exit 0 = allow. Exit 2 = deny (Claude Code shows the message). Exit other = error.

set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/agents/claude-code}"
mkdir -p "$LOG_DIR" 2>/dev/null || true

# Hook receives JSON on stdin per Claude Code hook spec.
INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"
TOOL_INPUT="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"
SESSION_ID="$(echo "$INPUT" | jq -r '.session_id // "default"')"

# ----- Tier-4 hard-deny patterns -----
# These cannot be confirmed past at the client side. The agent must not even
# be asked to run them. Each pattern is a regex applied to TOOL_INPUT.
DENY_PATTERNS=(
  '\brm\s+-rf\s+/'
  '\brm\s+-rf\s+~'
  '\brm\s+-rf\s+\$HOME'
  '\bterraform\s+destroy'
  '\bterraform\s+apply.*-auto-approve'
  '\bDROP\s+TABLE'
  '\bDROP\s+DATABASE'
  '\bTRUNCATE\s+TABLE'
  '\bkubectl\s+delete\s+ns'
  '\bkubectl\s+delete\s+namespace'
  '\bkubectl\s+scale\s+.*--replicas=0'
  '\baws\s+s3\s+rb'
  '\baws\s+ec2\s+terminate-instances'
  '\baws\s+rds\s+delete-db-instance'
  '\bgh\s+repo\s+delete'
  '\bgit\s+push\s+(--force|-f)'
  '\bgit\s+reset\s+--hard'
  '\bdd\s+if=/dev/zero\s+of='
  '\bmkfs\b'
  ':\(\)\s*\{\s*:\|:&\s*\};:'
)

for pattern in "${DENY_PATTERNS[@]}"; do
  if echo "$TOOL_INPUT" | grep -qE "$pattern"; then
    echo "BLOCKED: command matches deny pattern: ${pattern}" >&2
    echo "$(date -Iseconds) DENY $SESSION_ID $TOOL_NAME pattern=${pattern} input=${TOOL_INPUT}" \
      >> "$LOG_DIR/pre_tool_use.log" 2>/dev/null || true
    exit 2
  fi
done

# ----- Obfuscation defenses -----
# Catches the trivial cases. Not a guarantee. An adversarial agent has more
# obfuscation options than a regex list can enumerate.
OBFUSCATION_PATTERNS=(
  '\bbase64\s+(--decode|-d|-D)\b'
  '\beval\s+\$\('
  '\bbash\s+-c\s+\$\('
  '\bsh\s+-c\s+\$\('
  '\bpython3?\s+-c\s+["\x27]exec\('
  '\bcurl\s+[^|]+\|\s*(bash|sh)\b'
  '\bwget\s+[^|]+\|\s*(bash|sh)\b'
  '\bxargs\s+rm\b'
)

for pattern in "${OBFUSCATION_PATTERNS[@]}"; do
  if echo "$TOOL_INPUT" | grep -qE "$pattern"; then
    echo "BLOCKED: obfuscation pattern detected: ${pattern}" >&2
    echo "$(date -Iseconds) DENY-OBFUSCATION $SESSION_ID $TOOL_NAME pattern=${pattern} input=${TOOL_INPUT}" \
      >> "$LOG_DIR/pre_tool_use.log" 2>/dev/null || true
    exit 2
  fi
done

# ----- Allow with logging -----
echo "$(date -Iseconds) ALLOW $SESSION_ID $TOOL_NAME input=${TOOL_INPUT}" \
  >> "$LOG_DIR/pre_tool_use.log" 2>/dev/null || true

exit 0
