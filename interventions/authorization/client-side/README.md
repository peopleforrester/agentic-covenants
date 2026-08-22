# Interventions, Authorization / Client-side

**Trigger.** Sentinels alert: hook decision spike (multiple denies in short window suggesting probing); hook config tampering detected; auditd watch fires on `/etc/agents/hooks/`.

**Authority.** On-call, no second approval.

**Speed target.** Under 5 seconds.

## Tooling

- The hook layout from [`../../../controls/authorization/client-side/`](../../../controls/authorization/client-side) (the runbook overwrites it).
- `chattr` (Linux ext4/xfs); not all filesystems support it. Verify your `/etc/agents/` mount.

## Files in this directory

- [`agent-deny-all-local`](./agent-deny-all-local), runbook script. Replaces the hook with the deny-all template, sets `chattr +i`, replaces `settings.json` with the deny-all version, kills any in-flight agent so the new state applies.
- [`deny-all-hook.sh`](./deny-all-hook.sh), pre-staged hook template. Always returns exit code 2 with a "BLOCKED: agent in emergency lockdown" message. **Pre-stage** at `/etc/agents/emergency/deny-all-hook.sh`.
- [`settings-deny-all.json`](./settings-deny-all.json), pre-staged Claude Code settings with `defaultMode: deny`, empty allow/ask, deny `*`. **Pre-stage** at `/etc/agents/emergency/settings-deny-all.json`.

## Verification

```bash
# 1. Hook is the deny-all version (md5 must match)
md5sum /etc/agents/hooks/pre_tool_use.sh /etc/agents/emergency/deny-all-hook.sh

# 2. Immutable bit set
lsattr /etc/agents/hooks/pre_tool_use.sh
# expected: 'i' attribute present

# 3. New agent launch is blocked
sudo -u agent-runner /usr/local/bin/claude --print "test" 2>&1 | grep "emergency lockdown"
```

## Common mistakes

- `chattr +i` does not work on every filesystem (tmpfs, NFS, FAT). Verify your `/etc/agents/` mount.
- Pre-staged emergency template not in source control means you discover the typo during the incident.
- Forgetting to kill the running agent, the new hook applies only to new sessions.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02. NIST AI RMF MANAGE 4.1. OWASP ASI02, ASI05.
