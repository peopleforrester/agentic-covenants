#!/usr/bin/env bash
# ABOUTME: Lists pushes to protected branches during an incident window with forced: true or admin-bypass markers.
# ABOUTME: Output is for human review; any commit that landed via bypass needs to be inspected for malicious change.

set -euo pipefail

REPO="${1:?Usage: audit-bypass-events.sh <REPO> <INCIDENT_ID>}"
INCIDENT_ID="${2:?Usage: audit-bypass-events.sh <REPO> <INCIDENT_ID>}"
SINCE="${INCIDENT_START:-}"
UNTIL="${INCIDENT_END:-}"

if [[ -z "$SINCE" || -z "$UNTIL" ]]; then
  echo "Set INCIDENT_START and INCIDENT_END as ISO-8601 timestamps. The earliest IoC from Sentinels is the right SINCE; the time Interventions completed is the right UNTIL." >&2
  exit 64
fi

echo "Auditing $REPO for bypass events from $SINCE to $UNTIL ..."
echo

# Force-pushes during the window. branch_protection_rule events would also
# show in the GitHub Audit Log API; this script uses the events API as a
# starting point.
gh api "repos/$REPO/events?per_page=100" \
  --jq ".[] | select(.created_at >= \"$SINCE\" and .created_at <= \"$UNTIL\")
        | select(.type == \"PushEvent\" and .payload.forced == true)
        | {created_at, actor: .actor.login, ref: .payload.ref, head: .payload.head}"

echo
echo "Cross-reference each line above with PR review records. Any commit landed via force-push during the incident window must be reviewed."
