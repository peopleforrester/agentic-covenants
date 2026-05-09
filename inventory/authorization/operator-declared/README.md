# Inventory — Authorization / Operator-declared

**What this cell records.** The operator's intent for what each agent is authorized to do, linked back to source manifests.

## Fields

- `rbac_role_ref` — name of the source-of-truth Role committed under `manifests/rbac/`.
- `iam_policy_arns[]`
- `mcp_servers_allowlist_ref` — file path to the canonical `mcp-allowlist.json`.
- `last_audited_at` — when the operator last verified runtime matches intent.

## Cross-layer

Should equal the agent charter's `authorized_scope` block. Should match discovered effective permissions. Either disagreement = audit.

## Citation

NIST CSF 2.0 ID.AM-02, ID.AM-08. NIST AI RMF MAP 1.5, MAP 4.1.
