# Approval gating / Client-side

**Control.** PreToolUse hooks gating destructive command patterns. Tiered approval matching friction to blast radius. Typed confirmation required for tier-3 commands. Session limits on consecutive destructive ops. Out-of-band confirmation channel for highest-tier actions. Judgment-query escalation for value-laden decisions.

**Strength.** Deterministic for actions that match the tier patterns. The dominant failure mode is **alert fatigue**: reviewers approve reflexively after enough repetitions. Tiering and judgment-query escalation reduce but do not eliminate the failure mode. Equivalent commands not in the pattern list (`kubectl scale --replicas=0`) defeat the gating; document and move to server-side.

## Tooling

- The PreToolUse hook from [`../../authorization/client-side/`](../../authorization/client-side/) extended with tiering.
- A counter or sqlite-backed counter for session limits.
- An out-of-band channel: signed Slack approval, second-terminal confirmation, FIDO2 hardware key prompt, or a phone-side app.

## Files in this directory

- [`pre_tool_use_tiered.sh`](./pre_tool_use_tiered.sh) — the deny-then-ask-then-allow hook from Authorization, plus tier-3 typed verbatim confirmation, tier-4 out-of-band approval flow with timeout-deny default, session destructive-action counter (default cap: 10 per session).
- [`tier-config.yaml`](./tier-config.yaml) — declarative tier definitions consumed by the hook. The hook reads pattern lists from here so operators can update tiers without editing the script.
- [`escalate.py`](./escalate.py) — judgment-query escalation tool. Distinct from approval: the operator supplies the missing input rather than a yes/no.

## Verification

```bash
# 1. Tier 3 typed confirmation
echo '{"tool_name":"Bash","tool_input":{"command":"kubectl delete pod foo"},"session_id":"test"}' \
  | /etc/agents/hooks/pre_tool_use_tiered.sh
# expected: prompt for typed confirmation; mismatched input fails

# 2. Session limit
for i in {1..11}; do
  echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"kubectl delete pod foo$i\"},\"session_id\":\"test2\"}" \
    | /etc/agents/hooks/pre_tool_use_tiered.sh < <(echo "kubectl delete pod foo$i")
done
# expected: the 11th fails with "session destructive-action limit reached"

# 3. Out-of-band approval flow end-to-end
# Issue a tier-4 command. Confirm approval URL appears in Slack. Approve.
# Confirm command runs. Re-issue. Deny. Confirm command does not run.

# 4. Judgment query
echo '{"question":"This action affects 40% of ARR. Should we proceed?","context":{"session_id":"test3","token":"..."}}' \
  | python3 /etc/agents/tools/escalate.py
# expected: round-trips through the operator and returns the operator's input
```

## Common mistakes

- Flat approval workflow with one tier. Approval rate degrades to the 93% Anthropic measured.
- Tier-3 typed confirmation that accepts `y` or `yes` instead of the literal command. The point is friction proportional to risk.
- No session counter, so the agent loops on destructive actions and the operator clicks through.
- Out-of-band channel that defaults to "approve on timeout." Must default to deny.
- Treating judgment-query escalation as the same thing as approval. They are different controls. Approval is yes/no. Escalation is "supply the input I cannot generate."

## Citation

NIST CSF 2.0 PR.AA-05 (separation of duties), PR.PS-01. NIST AI RMF MANAGE 4.1 (post-deployment monitoring, appeal and override mechanisms). OWASP LLM06 (Excessive Agency). OWASP ASI02, ASI09 (Human-Agent Trust Exploitation). OWASP Agentic Least Agency principle. Assistance-games framing (Russell, 2019). EU AI Act Art. 14 (human oversight). Singapore IMDA "meaningful human accountability."
