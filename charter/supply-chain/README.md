# Charter, Supply chain

**Question.** What models, MCP servers, dependencies, base images is the charter allowed to use? Under what change-control?

| Layer | Cell |
|---|---|
| Organizational | [`organizational/`](./organizational/), Org-wide allowlist of approved foundation models. Vendor risk assessment integrated with procurement. |
| Domain | [`domain/`](./domain/), Inherits org list; adds domain restrictions; approves or denies MCP servers for the domain. |
| Agent | [`agent/`](./agent/), Specific named foundation model + version, MCP servers with hashes, base image digest, runtime version. Dependency changes require charter amendment. |

Feeds [`../../controls/supply-chain/`](../../controls/supply-chain/). Per OWASP MCP Top 10 (MCP04, MCP09), supply chain inventory is a charter property, not a runtime property.
