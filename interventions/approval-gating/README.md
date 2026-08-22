# Interventions, Approval gating

**Intent.** Lock down all approval surfaces.

**Target time-to-response: 60 seconds** (lower urgency; the bypass already happened).

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent) | Empty. |
| Client-side | [`client-side/`](./client-side) | `agent-approval-lockdown-local`: replace approval hook with deny-all, disable Auto Mode classifier, disable judgment-query escalation channel, force out-of-band on every action. |
| Server-side | [`server-side/`](./server-side) | `agent-approval-lockdown-server`: lock branch protection (revoke bypass perms, raise reviewers to 4), pause CI/CD via workflow disable, engage `DEPLOY_FREEZE`, lock GitHub environments. |

Stops what [`../../controls/approval-gating/`](../../controls/approval-gating) prevented and [`../../sentinels/approval-gating/`](../../sentinels/approval-gating) detected.
