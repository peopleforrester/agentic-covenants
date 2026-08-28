# Inventory, Identity

**Question.** Which agents exist, with what credentials, mapped to which charter, owned by which named human?

| Layer | Cell |
|---|---|
| Self-declared | [`in-agent/`](./in-agent), agent registration daemon: name, charter ref, owner, instance ID, heartbeat. |
| Operator-declared | [`client-side/`](./client-side), GitOps registry: `agents.yaml` per agent, owner-confirmed. |
| Discovered | [`server-side/`](./server-side), cloud audit log queries; K8s controller watching SA + RoleBinding by naming pattern. |

Cross-layer disagreements feed back into [`../../sentinels/`](../../sentinels).
