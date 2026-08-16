# Sentinels, Authorization

**Intent.** Surface every PreToolUse hook decision (allow/ask/deny/error), every RBAC denial, every IAM Access Analyzer finding, every OPA decision log. Catch hook config edits and `--no-verify` bypass attempts at the operator host.

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Forensic only. Tool descriptions captured with each call. |
| Client-side | [`client-side/`](./client-side/) | Hook decision-event emission; auditd rules on hook config edits and `--no-verify`; SIEM rule for multi-deny patterns in a single session. |
| Server-side | [`server-side/`](./server-side/) | Kyverno PolicyReport ingestion to SIEM; OPA decision-log streaming; AWS IAM Access Analyzer findings via EventBridge; SIEM detection on RBAC denial spikes. |

Detects what [`../../controls/authorization/`](../../controls/authorization/) prevents.
