# Inventory, Authorization

**Question.** What scope each agent has, what RBAC roles or IAM principals it uses, what could it touch.

| Layer | Cell |
|---|---|
| Self-declared | [`in-agent/`](./in-agent), agent reports `tools_allowlist`, `mcp_servers_allowlist`, `effective_scope` on registration. |
| Operator-declared | [`client-side/`](./client-side), registry links agent to RBAC manifest paths and IAM policy ARNs. |
| Discovered | [`server-side/`](./server-side), K8s RBAC API list, AWS IAM Access Analyzer effective permissions, Kyverno PolicyReports. |

Drift between layers feeds [`../../sentinels/authorization/server-side/`](../../sentinels/authorization/server-side).
