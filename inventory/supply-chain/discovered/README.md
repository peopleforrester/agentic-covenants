# Inventory, Supply chain / Discovered

**What this cell records.** Independent observation of what the agent actually loads, regardless of declared dependencies.

## Sources

- Image registry pull events with signature verification status (from [`sentinels/supply-chain/server-side/kyverno-log-image-pulls.yaml`](../../../sentinels/supply-chain/server-side/kyverno-log-image-pulls.yaml)).
- Package-manager logs: `npm` postinstall scripts, `pip install` runtime tracking, `cargo` install logs.
- Runtime introspection: which foundation model the agent's wrapper actually points at; which MCP servers it has connected to in this session.
- SBOM scanning ([`sentinels/supply-chain/server-side/sbom-diff-cronjob.yaml`](../../../sentinels/supply-chain/server-side/sbom-diff-cronjob.yaml) is the daily SBOM-diff job).

## Cross-layer

- Discovered MCP server with hash that does not appear in operator-declared `mcp-allowlist.json` = unauthorized MCP. Mitigation: tighten Cilium FQDN policy + remove allowlist tolerance.
- Discovered base image SHA different from operator-declared = tag mutation or unsigned-image admission. Audit Kyverno verification.

## Common failure mode

MCP over unix socket leaves no network trace. Discovery via process introspection only. The agent runtime should emit a structured event on every MCP server attach (the Sentinels mcp-launch wrapper does this).

## Citation

NIST CSF 2.0 ID.RA-09, ID.AM-04. NIST AI RMF MAP 4.1. CSA MAESTRO Layer 1, Layer 3, Layer 7. OWASP MCP Top 10 beta. NIST SP 800-161 Rev. 1.
