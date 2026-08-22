# Sentinels, Supply chain

**Intent.** Surface every MCP allowlist violation, every lockfile diff, every tool-description hash mismatch (rug-pull), every cosign verification failure, and every egress NetworkPolicy denial to a non-allowlisted MCP domain.

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent) | Forensic only. "Where did this dependency come from" traceable through the tool-call log. |
| Client-side | [`client-side/`](./client-side) | mcp-launch logger emitting per-connection events with hash-status; tool-description mismatch alert; lockfile-diff CI extension shipping diffs to SIEM. |
| Server-side | [`server-side/`](./server-side) | Image-pull events captured via Kyverno mutate; daily SBOM-diff CronJob; cosign verification failures via PolicyReport; Cilium FQDN denial flow events. |

Detects what [`../../controls/supply-chain/`](../../controls/supply-chain) prevents.
