# Sentinels — Identity / In-agent

**Control.** Tool-call logs include credential fingerprint (hash of token, never the token); session correlation; logs ship to a remote sink.

**Strength.** Forensic. Useful after the fact, not in real time.

## Tooling

- Claude Code (or your agent runtime) configured to emit transcript and tool-call logs.
- A remote sink the agent's user cannot write to. Without this, the agent edits its own forensic record.

## Files in this directory

- [`ship-sessions.sh`](./ship-sessions.sh) — cron-style script that tails `~/.claude/sessions/` for new entries and ships them to a remote sink. Run from the operator account, not the agent's.

## Verification

```bash
# 1. Confirm session shipping
ls -la /var/log/agents/sessions/   # remote sink local mirror
# expected: recent files
```

## Common mistakes

- Logs ship to a sink the agent has write access to.
- Session correlation drops because the session ID is not propagated through hook events.

## Citation

NIST CSF 2.0 DE.CM-09. NIST SP 800-92 (Computer Security Log Management).
