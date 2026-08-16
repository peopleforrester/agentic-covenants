# Sentinels, Approval gating

**Intent.** Surface alert-fatigue patterns (response time below threshold = reflexive approval). Catch tier-3 typed-confirmation rejections, branch-protection bypass events, deployment-freeze breach attempts, and changes to branch protection itself.

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Forensic only. Confirmation-prompt usage captured in session logs. |
| Client-side | [`client-side/`](./client-side/) | Approval-timing logger that records local think-time on every confirmation; OOB approval channel logger; SIEM rule for response < 2s across > 50 approvals (the alert-fatigue pattern). |
| Server-side | [`server-side/`](./server-side/) | GitHub webhook for branch-protection bypass and force-push events; hourly drift-detection job comparing live branch protection to a checked-in expected JSON; deployment-freeze breach alert. |

Detects what [`../../controls/approval-gating/`](../../controls/approval-gating/) prevents.
