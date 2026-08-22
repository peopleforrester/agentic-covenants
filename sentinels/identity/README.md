# Sentinels, Identity

**Intent.** Identity used outside expected hours, source IP, or by an unexpected principal. Identity reuse across agents. Stale credential reuse within the TTL window.

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent) | Forensic only. Tool-call logs to a remote sink, with credential fingerprint (hash, not token) included. |
| Client-side | [`client-side/`](./client-side) | PreToolUse hook emits structured identity events; auditd watches agent process startup; Vector ships to SIEM. |
| Server-side | [`server-side/`](./server-side) | K8s audit policy capturing every agent SA action; CloudTrail with Object Lock; Sigma-style SIEM rules on out-of-hours and unexpected source IP. |

Detects what [`../../controls/identity/`](../../controls/identity) prevents.
