# Inventory — Identity

**Question.** Which agents exist, with what credentials, mapped to which charter, owned by which named human?

| Layer | Cell |
|---|---|
| Self-declared | [`self-declared/`](./self-declared/) — agent registration daemon: name, charter ref, owner, instance ID, heartbeat. |
| Operator-declared | [`operator-declared/`](./operator-declared/) — GitOps registry: `agents.yaml` per agent, owner-confirmed. |
| Discovered | [`discovered/`](./discovered/) — cloud audit log queries; K8s controller watching SA + RoleBinding by naming pattern. |

Cross-layer disagreements feed back into [`../../sentinels/`](../../sentinels/).
