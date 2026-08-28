# Inventory, Supply chain / Self-declared

**What this cell records.** The agent's report of its current dependency state at registration and on dependency changes.

## Fields

- `foundation_model_name`, `foundation_model_version`
- `mcp_servers[]` (name, hash, version)
- `base_image_digest`
- `lockfile_fingerprint` (hash of the lockfile)
- `agent_runtime_version`

The agent's wrapper computes hashes at startup. Any deviation from charter triggers an out-of-band re-approval (or the agent refuses to start if the wrapper is configured strict).

## Cross-layer

Self-declared dependencies should equal operator-declared (charter-authoritative). Drift is automatic re-review trigger.

## Citation

NIST CSF 2.0 ID.AM-04, ID.RA-09. NIST AI RMF MAP 4.1. CSA MAESTRO Layer 1, Layer 7. OWASP MCP04, MCP09.
