# Restorations, Approval gating / Client-side

**Precondition.** Interventions L2-C4 has fired (deny-all hook, Auto Mode disabled, escalation channel disabled). Restorations identity and authorization rows complete.

**Authority.** On-call.

## Files in this directory

- [`agent-restore-approval-local`](./agent-restore-approval-local), runbook script. Restores the tiered hook from VCS, reapplies tier-config.yaml, sets `autoMode: true` and `requireOutOfBand: false` in `settings.json`, re-enables the judgment-query escalation channel via service API.

## Verification

```bash
# 1. Auto Mode enabled
jq '.permissions.autoMode' /etc/agents/claude-code-prod/settings.json
# expected: true

# 2. Hook is the operational tiered version
md5sum /etc/agents/hooks/pre_tool_use.sh
md5sum controls/approval-gating/client-side/pre_tool_use_tiered.sh
# expected: identical

# 3. Escalation channel enabled
curl -sS https://escalate.example.com/api/status?agent=claude-code-prod
# expected: disabled: false
```

## Citation

NIST CSF 2.0 RC.RP-01. NIST AI RMF MANAGE 4.1. OWASP ASI09. EU AI Act Art. 14 (recovery dimension).
