# Charter — Authorization / Agent

**Structural question.** Does the agent charter declare a specific authorized scope (named tools, MCP servers, environments, RBAC role reference) that requires re-signature to expand?

**Owner.** Named human owner. Counter-signed by domain authority.

## Template fragment

The `authorized_scope:` block of [`../../templates/agent-charter.yaml`](../../templates/agent-charter.yaml):

```yaml
authorized_scope:
  environments: [dev, staging]
  tools_allowlist:
    - Read
    - Glob
    - Grep
    - "Bash(git:status)"
    - "Bash(git:diff)"
    - "Bash(kubectl:get:*)"
  mcp_servers_allowlist: [filesystem, github]
  rbac_role_ref: agent-claude-code-prod-role
  iam_role_arn: arn:aws:iam::123456789012:role/claude-code-prod
```

## Audit prompts

- For [agent X], does the charter scope match the runtime RBAC Role and IAM policy?
- Is `rbac_role_ref` the actual name of a Role committed to source-of-truth manifests?
- When was scope last expanded? Who signed the expansion?

## Operational tie-in

- `tools_allowlist` → `controls/authorization/client-side/settings.json` allow list.
- `mcp_servers_allowlist` → `controls/supply-chain/client-side/mcp-allowlist.json` server names.
- `rbac_role_ref` → `controls/authorization/server-side/` (the Role with that name must exist and contain only the verbs the charter allows).
- `iam_role_arn` → `controls/identity/server-side/serviceaccount.yaml` IRSA annotation and `controls/authorization/server-side/aws-iam-scoped-policy.json`.

**If the charter scope and the runtime scope drift apart, that is a Sentinels finding** — the drift detection in `sentinels/approval-gating/server-side/audit-branch-protection.yml` is the analogous pattern, but for agent scope it requires a custom drift check that compares charter YAML to live RBAC + IAM.

## Citation

NIST CSF 2.0 GV.PO-01; PR.AA-05 (least privilege; charter dimension). NIST AI RMF GOVERN 1.4, MANAGE 2.4. ISO/IEC 42001 §A.6.2. EU AI Act Art. 14, Art. 15.
