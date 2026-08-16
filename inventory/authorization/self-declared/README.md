# Inventory, Authorization / Self-declared

**What this cell records.** The agent's report of its current effective scope at startup and on scope changes.

## Fields

- `tools_allowlist[]`
- `mcp_servers_allowlist[]` (with hashes)
- `rbac_role_ref`
- `iam_role_arn`
- `effective_scope_at_startup` (snapshot of permissions reported by the agent runtime)

The agent's wrapper sends this on each registration. If the agent's runtime cannot enumerate its own scope (some MCP-only agents cannot), this cell becomes a manifest reference rather than a live snapshot.

## Cross-layer

Should match operator-declared scope (charter authoritative). Drift = Sentinels alert.

## Citation

NIST CSF 2.0 ID.AM-02. NIST AI RMF MAP 4.1. CSA MAESTRO Layer 7.
