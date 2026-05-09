#!/usr/bin/env bash
# ABOUTME: Pre-staged emergency PreToolUse hook. Always denies. Applied during incident response.
# ABOUTME: Pre-stage at /etc/agents/emergency/deny-all-hook.sh; agent-deny-all-local copies it into place.

# Read stdin to drain the hook input even though we are not using it. Some
# agent runtimes block on stdin not being consumed.
cat >/dev/null

echo "BLOCKED: agent in emergency lockdown" >&2
exit 2
