#!/usr/bin/env bash
# ABOUTME: pre-commit hook that fails when the diff touches operator-only paths.
# ABOUTME: This catches operator-machine commits; --no-verify bypasses it. Server-side pre-receive is the backstop.

set -euo pipefail

# Operator may set this env var to bypass the check for legitimate human commits
# performed via a controlled session. Setting it from inside an agent context
# requires write access to the operator's shell profile, which the agent should
# not have.
if [[ "${OPERATOR_OVERRIDE:-}" == "1" ]]; then
  exit 0
fi

cat <<'EOF' >&2
BLOCKED: edits to protected paths are operator-only.

The agent must not commit to:
  - infrastructure/prod/    (production IaC)
  - .github/workflows/      (CI configuration)
  - secrets/                (sealed secrets and key material)
  - .claude/                (agent runtime configuration)
  - /etc/agents/            (system-level agent config)

If you are the operator and need to make this change manually, set
OPERATOR_OVERRIDE=1 in your shell and re-run the commit.

This pre-commit hook is bypassable with `git commit --no-verify`. The
server-side Git pre-receive hook in controls/authorization/server-side/
enforces the same rule and is not bypassable. Try to push with --no-verify
applied locally; the push will fail there too.
EOF
exit 1
