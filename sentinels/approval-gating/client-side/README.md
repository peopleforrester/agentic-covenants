# Sentinels, Approval gating / Client-side

**Control.** Approval-timing logger captures local think-time on every confirmation. OOB approval channel logger captures decisions joined to session. SIEM rule fires on response under 2s across more than 50 approvals (the alert-fatigue pattern, calibrated against AHRQ PSNet research and Anthropic Auto Mode telemetry).

**Strength.** Deterministic when timings are measured locally and shipped reliably. Failure modes: timing measurement that includes network latency to a remote approval service (measure local think-time only); threshold too aggressive (anything under 5 seconds is "fatigue") yielding false positives; threshold too lenient (anything over 100ms is "real consideration") so the rule never fires; OOB channel log not joined to the original request session, cannot reconstruct the chain.

## Tooling

- The tiered hook from [`../../../controls/approval-gating/client-side/pre_tool_use_tiered.sh`](../../../controls/approval-gating/client-side/pre_tool_use_tiered.sh), extended to emit timing events.
- A SIEM with windowed-aggregate query support.

## Files in this directory

- [`approval-timing-emit.sh`](./approval-timing-emit.sh), appendable snippet that wraps the typed-confirmation read with timing measurement (start/end nanoseconds, response_ms, matched).
- [`oob-decision-log.sh`](./oob-decision-log.sh), script that the out-of-band approval workflow calls when an approver decides; emits a structured event keyed to the original request ID and session.
- [`sigma-approval-fatigue.yaml`](./sigma-approval-fatigue.yaml), SIEM rule firing when a user's mean tier-≥2 response time is under 2s across more than 50 approvals.

## Verification

```bash
# 1. Approval timing captured
# Run a tier-3 command, type the confirmation, check log
journalctl -t agent-sentinel --since "5 minutes ago" | grep approval_timing
# expected: response_ms field present

# 2. Fatigue pattern alert fires (test environment)
# Generate 60 approvals at <1s each
for i in {1..60}; do
  echo '{"session_id":"fatigue-test","tool_name":"Bash","tool_input":{"command":"echo test"}}' \
    | /etc/agents/hooks/pre_tool_use_tiered.sh
done
# Query SIEM for the fatigue rule output
```

## Common mistakes

- Timing measurement that includes network latency to a remote approval service. Measure local think-time only.
- Threshold too aggressive (anything under 5s): false positives on routine approvals.
- Threshold too lenient (anything over 100ms is "real consideration"): never fires.
- OOB channel log not joined to the original session. Cannot reconstruct full chain.

## Citation

NIST CSF 2.0 DE.CM-03, DE.AE-02. AHRQ PSNet alarm-fatigue research. Anthropic Auto Mode (March 2026).
