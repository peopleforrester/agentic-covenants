# Inventory, Supply chain

**Question.** Foundation model. MCP servers. Base images. Tool versions. Dependency tree.

| Layer | Cell |
|---|---|
| Self-declared | [`in-agent/`](./in-agent), agent reports current dependency manifest on registration. |
| Operator-declared | [`client-side/`](./client-side), registry of authorized-dependency manifests linked to Covenants L2-C5/L3-C5 allowlists. |
| Discovered | [`server-side/`](./server-side), image registry pull events, package-manager logs, SBOM diff over time, runtime introspection. |

Per OWASP MCP Top 10 (MCP04, MCP09), supply chain inventory is a charter property, not a runtime property, but the discovered layer is what surfaces drift between charter and reality.
