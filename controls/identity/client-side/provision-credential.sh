#!/usr/bin/env bash
# ABOUTME: Provisions a per-agent credential file with operator-owned ACLs.
# ABOUTME: The agent's own user cannot read the file at rest; the operator launches with it in env.

set -euo pipefail

AGENT_NAME="${1:-}"
AGENT_USER="${2:-agent-runner}"
OPERATOR_GROUP="${3:-operators}"

if [[ -z "$AGENT_NAME" ]]; then
  cat <<'USAGE' >&2
Usage: provision-credential.sh <agent-name> [agent-user] [operator-group]

Example:
  AGENT_TOKEN="$(vault read -field=token agents/claude-code-prod)" \
    provision-credential.sh claude-code-prod agent-runner operators
USAGE
  exit 64
fi

if [[ "$EUID" -ne 0 ]]; then
  echo "Must run as root (uses chown and setfacl)." >&2
  exit 1
fi

if [[ -z "${AGENT_TOKEN:-}" ]]; then
  echo "AGENT_TOKEN must be set in the environment." >&2
  exit 1
fi

CRED_DIR="/etc/agents/${AGENT_NAME}"
CRED_FILE="${CRED_DIR}/token"
ENV_FILE="${CRED_DIR}/env"

mkdir -p "$CRED_DIR"
chown "root:${OPERATOR_GROUP}" "$CRED_DIR"
chmod 0750 "$CRED_DIR"

umask 0177
printf '%s\n' "$AGENT_TOKEN" > "$CRED_FILE"
chown "root:${OPERATOR_GROUP}" "$CRED_FILE"
chmod 0640 "$CRED_FILE"

# Render env file consumed by the systemd unit. The systemd unit reads this
# at agent launch and exports ANTHROPIC_API_KEY into the agent's environment.
# The agent process itself cannot read /etc/agents/<name>/env at rest.
cat > "$ENV_FILE" <<EOF
ANTHROPIC_API_KEY=${AGENT_TOKEN}
AGENT_NAME=${AGENT_NAME}
EOF
chown "root:${OPERATOR_GROUP}" "$ENV_FILE"
chmod 0640 "$ENV_FILE"

# ACL: the agent's own user is denied read on the credential file. The
# operator (or systemd, running as root) reads it at launch. A compromised
# agent process cannot re-read the file from disk.
if command -v setfacl >/dev/null 2>&1; then
  setfacl -m "u:${AGENT_USER}:---" "$CRED_FILE"
  setfacl -m "u:${AGENT_USER}:---" "$ENV_FILE"
else
  echo "WARN: setfacl not available; relying on group-based denial only." >&2
fi

echo "Provisioned ${CRED_DIR}"
echo "Credential fingerprint: $(printf '%s' "$AGENT_TOKEN" | sha256sum | cut -d' ' -f1 | head -c 16)"
unset AGENT_TOKEN
