# Interventions, Identity / Client-side

**Trigger.** Sentinels alert: identity used outside expected hours, identity used from unexpected source IP, credential fingerprint mismatch.

**Authority.** On-call, no second approval required. Identity revocation is reversible (rotate again to restore).

**Speed target.** Under 30 seconds.

## Tooling

- Standard Linux process tools: `pkill`, `pgrep`, `systemctl`.
- The per-agent credential layout from [`../../../controls/identity/client-side/`](../../../controls/identity/client-side).

## Files in this directory

- [`agent-revoke-local`](./agent-revoke-local), runbook script. Takes `AGENT_NAME` as the only positional argument. Kills the process tree, optionally `systemctl stop`s, deletes the credential file, sets a re-auth flag, ships an incident event to syslog.

## Verification

```bash
# Confirm no agent processes survive
pgrep -f "claude.*claude-code-prod" && echo "FAIL: process survived" || echo "OK"

# Confirm credential file removed
ls -la /etc/agents/claude-code-prod/ | grep -E "(token|key|env)"
# (must produce no output)

# Confirm log entry shipped to SIEM
journalctl -t agent-incident --since "1 minute ago"
```

## Common mistakes

- `pkill -TERM` instead of `pkill -KILL`. Daemonized agents ignore SIGTERM.
- Forgetting `systemctl stop`. The service manager respawns the agent.
- Deleting the credential file but missing env-var credentials in already-running processes (the kill step handles this; do not skip it).
- Pattern match too narrow: `pkill -f claude-code-prod` misses `pkill -f $AGENT_NAME` when the name has special chars.

## Citation

NIST CSF 2.0 RS.MI-01 (incident contained), RS.MI-02 (incident eradicated). NIST SP 800-61 Rev. 2 (Computer Security Incident Handling Guide). NIST AI RMF MANAGE 4.1. OWASP ASI03, ASI10.
