# Charter — Authorization

**Question.** What scope does the charter grant? Under what change-control process can scope be expanded?

| Layer | Cell |
|---|---|
| Organizational | [`organizational/`](./organizational/) — AI Risk Appetite Statement; hard prohibitions; change-control for evolving scope policy. |
| Domain | [`domain/`](./domain/) — Per-class scope; inherits org hard prohibitions plus domain-specific. |
| Agent | [`agent/`](./agent/) — Named tools, MCP servers, environments, max-blast-radius. Scope expansion requires re-signature. |

Feeds [`../../controls/authorization/server-side/`](../../controls/authorization/server-side/). The agent's RBAC Role is the technical implementation of the charter scope.
