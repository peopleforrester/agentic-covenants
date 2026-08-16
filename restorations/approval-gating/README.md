# Restorations, Approval gating

**Intent.** Re-enable branch protection, audit bypass events for forensics, harden gates that were exploited.

**Order.** Fourth. Re-enabling gates before rebuild is complete blocks legitimate recovery operations.

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-restore-approval-local`: restore PreToolUse config from VCS, reapply tier definitions, re-enable Auto Mode classifier, re-establish out-of-band confirmation channel. |
| Server-side | [`server-side/`](./server-side/) | `agent-restore-approval-server`: re-enable branch protection from saved config (verify `enforce_admins: true`), re-add CODEOWNERS, audit bypass events from incident, unfreeze deployments only after the rest of recovery is verified. |

Rebuilds what [`../../interventions/approval-gating/`](../../interventions/approval-gating/) locked.
