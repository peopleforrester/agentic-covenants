# Inventory, Supply chain

**Question.** Foundation model. MCP servers. Base images. Tool versions. Dependency tree.

| Layer | Cell |
|---|---|
| Self-declared | [`self-declared/`](./self-declared/), agent reports current dependency manifest on registration. |
| Operator-declared | [`operator-declared/`](./operator-declared/), registry of authorized-dependency manifests linked to Covenants L2-C5/L3-C5 allowlists. |
| Discovered | [`discovered/`](./discovered/), image registry pull events, package-manager logs, SBOM diff over time, runtime introspection. |

Per OWASP MCP Top 10 (MCP04, MCP09), supply chain inventory is a charter property, not a runtime property, but the discovered layer is what surfaces drift between charter and reality.
