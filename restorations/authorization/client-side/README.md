# Restorations, Authorization / Client-side

**Precondition.** Interventions L2-C2 has fired (deny-all hook applied, immutable bit set, agent killed). Restorations identity row complete (the agent has a fresh credential to start with after the rebuild).

**Authority.** On-call.

## Tooling

- Git access to the repo containing `.claude/` config in source.
- `chattr` to clear the immutable bit set during Interventions.
- `pre-commit` framework to re-install hooks.

## Files in this directory

- [`agent-restore-authorization-local`](./agent-restore-authorization-local), runbook script. Clears the chattr +i, restores hook config from `git checkout`, verifies file ownership returned to operator account, re-installs pre-commit, checks Claude Code version against the May 2026 patched line.

## Verification

```bash
# 1. Hook is restored (md5 matches source-of-truth)
md5sum /etc/agents/hooks/pre_tool_use.sh
md5sum controls/authorization/client-side/pre_tool_use.sh
# expected: identical

# 2. Hook ownership is operator account, not agent
ls -la /etc/agents/hooks/pre_tool_use.sh
# expected: owner root, group operators

# 3. Immutable bit cleared
lsattr /etc/agents/hooks/pre_tool_use.sh
# expected: 'i' attribute absent

# 4. Pre-commit is installed
cd <repo> && pre-commit run --all-files

# 5. Claude Code is on the patched line
claude --version
# expected: >= 2.1.40 (May 2026 PreToolUse precedence patch)
```

## Common failure modes

- `chattr +i` left over from intervention; restore fails to overwrite. The runbook clears it explicitly.
- Hook ownership returned to agent's user instead of operator. Verify after restore.
- Claude Code on a pre-patch version. The "allow"-bypasses-"deny" regression is back in effect even after recovery.

## Citation

NIST CSF 2.0 RC.RP-01, RC.IM-01. NIST AI RMF MANAGE 4.1. OWASP ASI02, ASI05.
