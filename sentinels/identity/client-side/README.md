# Sentinels, Identity / Client-side

**Control.** PreToolUse hook emits structured identity events; auditd watches agent process startup; Vector or Fluent Bit ships to SIEM.

**Strength.** Deterministic when ships actually happen. Tamper-evident only if the SIEM endpoint is owned by the operator account, not the agent's.

## Tooling

- `auditd` (Linux) or `audit_pipe` (macOS).
- Vector 0.40+ or Fluent Bit 3.0+.
- A SIEM (Splunk, Elastic, Loki, Datadog, Sumo Logic).

## Files in this directory

- [`identity-log-hook.sh`](./identity-log-hook.sh), PreToolUse hook that emits a structured JSON event with session ID, tool name, credential fingerprint (hash, never the token), effective UID, hostname, timestamp.
- [`auditd-agent.rules`](./auditd-agent.rules), auditd watch rules for agent process startup. Drop in `/etc/audit/rules.d/`.
- [`vector.toml`](./vector.toml), Vector config that parses syslog, enriches, and ships to Elasticsearch (substitute your SIEM endpoint).

## Verification

```bash
# 1. Hook emits log on tool call
echo '{"session_id":"test","tool_name":"Read"}' | ./identity-log-hook.sh
journalctl -t agent-sentinel --since "1 minute ago"
# expected: structured JSON event with credential fingerprint, no raw token

# 2. Audit rule fires on agent start
sudo -u agent-runner /usr/local/bin/claude --version
ausearch -k agent_exec --start recent
# expected: execve event with UID and command line

# 3. Vector ships to SIEM
curl -sS https://siem.example.com:9200/agent-sentinel-*/_search?q=event:identity \
  -H "Authorization: Bearer $SIEM_TOKEN" | jq '.hits.total.value'
# expected: non-zero count
```

## Common mistakes

- Logging the raw token instead of a hash. Anyone with SIEM access can replay the agent.
- Hook ships logs to local file only. Agent with filesystem access edits the log.
- Auditd rule on the binary path; if the agent moves the binary or runs from a different path, the rule misses. Use `auditctl -l` to confirm rules are loaded.
- Credential fingerprint hash too short and collides across agents. Use at least 16 hex chars.

## Citation

NIST CSF 2.0 DE.CM-01, DE.CM-09. NIST SP 800-92. NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026).
