#!/usr/bin/env bash
# ABOUTME: Ships agent session transcripts to a remote sink the agent cannot write to.
# ABOUTME: Run from the operator account via cron or systemd timer; never from the agent's user.

set -euo pipefail

LOCAL_SESSIONS="${LOCAL_SESSIONS:-/home/agent-runner/.claude/sessions}"
REMOTE_SINK="${REMOTE_SINK:-rsync://siem-ingest.example.com/agent-sessions}"
HOST="$(hostname -f)"
LOCK_FILE="/var/lib/agents/.ship-sessions.lock"

# Single-flight lock to prevent overlap on slow runs.
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "ship-sessions: another run in progress; exiting"
  exit 0
fi

if [[ ! -d "$LOCAL_SESSIONS" ]]; then
  echo "ship-sessions: $LOCAL_SESSIONS does not exist; nothing to ship"
  exit 0
fi

# rsync with --append-verify so a partial transfer can resume.
# --remove-source-files would be a destructive option and is deliberately
# omitted; the sink is authoritative and the local copy is the audit trail.
rsync -av --append-verify \
  --include='*.json' --include='*.jsonl' --include='*.log' \
  --exclude='*' \
  "$LOCAL_SESSIONS/" \
  "${REMOTE_SINK}/${HOST}/"
