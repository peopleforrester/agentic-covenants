# Interventions, Approval gating / Client-side

**Trigger.** Sentinels detected approval bypass, fatigue pattern saturation (mean response under 2s across 50+ approvals), judgment-query escalation channel compromise.

**Authority.** On-call.

**Speed target.** Under 10 seconds.

## Tooling

- The hook layout from [`../../authorization/client-side/`](../../authorization/client-side) (this runbook re-uses the deny-all hook).
- `jq` for editing `settings.json` in place.
- API access to your judgment-query escalation service to disable it.

## Files in this directory

- [`agent-approval-lockdown-local`](./agent-approval-lockdown-local), runbook script. Replaces the approval hook with the deny-all hook (shared with authorization client-side), disables Auto Mode in `settings.json`, sets `requireOutOfBand: true`, disables the judgment-query escalation channel, kills the agent.

## Verification

```bash
# 1. Auto Mode disabled
jq '.permissions.autoMode' /etc/agents/claude-code-prod/settings.json
# expected: false

# 2. Hook is deny-all
md5sum /etc/agents/hooks/pre_tool_use.sh /etc/agents/emergency/deny-all-hook.sh
# expected: identical

# 3. Escalation channel disabled
curl -sS https://escalate.example.com/api/status?agent=claude-code-prod
# expected: disabled: true
```

## Common mistakes

- Disabling Auto Mode but not replacing the hook. Auto Mode disabled means more prompts; the agent still proceeds on the prompts.
- Not disabling the escalation channel, the agent escalates to a compromised channel and gets fake approvals.
- Settings JSON edited in place; if the original was JSON5 (with comments), the standard `jq` rewrite breaks it. Use a JSON-comment-aware tool if your config is JSON5.

## Citation

NIST CSF 2.0 RS.MI-01. NIST AI RMF MANAGE 4.1. OWASP ASI09. EU AI Act Art. 14 (response dimension).
