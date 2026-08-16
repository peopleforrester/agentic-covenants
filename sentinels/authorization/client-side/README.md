# Sentinels, Authorization / Client-side

**Control.** Hook decision events (allow/ask/deny/error) emitted as structured JSON. Auditd watches for hook config edits and `--no-verify`. SIEM rule for multi-deny patterns in a single session.

**Strength.** Deterministic when shipped. Failure modes: decision events not correlated with tool input (counts denies, doesn't reconstruct intent); auditd rule format errors silently disable the rule (verify with `auditctl -l`); `--no-verify` rule misses `git commit -n` short form.

## Tooling

- The PreToolUse hook chain (extends [`../../identity/client-side/identity-log-hook.sh`](../../identity/client-side/identity-log-hook.sh)).
- `auditd` (Linux).
- A SIEM with KQL/Sigma-style query support.

## Files in this directory

- [`hook-decision-emit.sh`](./hook-decision-emit.sh), appendable snippet that extends the deny-then-ask-then-allow hook from [`../../../controls/authorization/client-side/pre_tool_use.sh`](../../../controls/authorization/client-side/pre_tool_use.sh) to emit a structured decision event before exiting.
- [`auditd-auth.rules`](./auditd-auth.rules), auditd rules for hook config edits, allowlist edits, Claude Code settings edits, and `--no-verify` execve.
- [`sigma-multi-deny.yaml`](./sigma-multi-deny.yaml), SIEM rule that fires when a single session accumulates more than 5 deny events; this is a probing pattern indicator.

## Verification

```bash
# 1. Hook decision logged
echo '{"session_id":"test","tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
  | /etc/agents/hooks/pre_tool_use.sh
journalctl -t agent-sentinel --since "1 minute ago" | grep hook_decision
# expected: event with decision: deny

# 2. Auditd catches hook config edit
sudo touch /etc/agents/hooks/test
ausearch -k hook_config_edit --start recent
# expected: write event

# 3. Auditd catches --no-verify
git commit --no-verify -m "test" 2>/dev/null || true
ausearch -k git_no_verify --start recent
# expected: execve with --no-verify in args
```

## Common mistakes

- Decision events not correlated with the underlying tool input (useful for counting denies, not for forensics).
- `auditctl -l` not run after rule install, typo'd rules silently fail.
- `--no-verify` rule misses `git commit -n`. Add both forms.

## Citation

NIST CSF 2.0 DE.CM-01, DE.CM-03, DE.CM-09.
