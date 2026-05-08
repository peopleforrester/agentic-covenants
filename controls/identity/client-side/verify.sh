#!/usr/bin/env bash
# ABOUTME: Verifies per-agent credential hygiene: not in process listing, not readable by agent, unique per agent.
# ABOUTME: Run as root. Exits non-zero on any failed check.

set -euo pipefail

AGENT_USER="${AGENT_USER:-agent-runner}"
AGENTS_DIR="${AGENTS_DIR:-/etc/agents}"
PASS=0
FAIL=0

check() {
  local name="$1"
  local result="$2"
  if [[ "$result" == "ok" ]]; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name -- $result"
    FAIL=$((FAIL + 1))
  fi
}

# 1. Credential not in process listing
if ps -eo args | grep -E 'ANTHROPIC_API_KEY=[^ ]+' | grep -v grep >/dev/null; then
  check "credential not in process listing" "found ANTHROPIC_API_KEY=... in args"
else
  check "credential not in process listing" "ok"
fi

# 2. Agent cannot read its own credential file at rest
shopt -s nullglob
for cred in "$AGENTS_DIR"/*/token; do
  if sudo -u "$AGENT_USER" cat "$cred" >/dev/null 2>&1; then
    check "agent cannot read $cred" "agent user $AGENT_USER read it successfully"
  else
    check "agent cannot read $cred" "ok"
  fi
done

# 3. Unique credential per agent
TOKENS=$(find "$AGENTS_DIR" -maxdepth 2 -name token -type f 2>/dev/null)
if [[ -z "$TOKENS" ]]; then
  check "per-agent credentials provisioned" "no tokens found in $AGENTS_DIR"
else
  HASHES=$(echo "$TOKENS" | xargs -r md5sum | awk '{print $1}' | sort)
  UNIQUE=$(echo "$HASHES" | uniq | wc -l)
  TOTAL=$(echo "$HASHES" | wc -l)
  if [[ "$UNIQUE" -eq "$TOTAL" ]]; then
    check "per-agent credentials are unique ($TOTAL agents)" "ok"
  else
    check "per-agent credentials are unique" "$((TOTAL - UNIQUE)) duplicate(s) detected"
  fi
fi

echo ""
echo "Summary: $PASS passed, $FAIL failed"
exit "$FAIL"
