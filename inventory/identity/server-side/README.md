# Inventory, Identity / Discovered

**What this cell records.** Independent observation of which agent identities are actually in use, regardless of whether they declared themselves or appear in operator records.

## Sources

- Cloud audit logs: CloudTrail `userIdentity.sessionContext.sessionIssuer` for IAM principals starting with `claude-`, `agent-`, or `bot-`. GCP Audit Logs, Azure Monitor for the equivalent.
- Kubernetes API watches: list `ServiceAccount` and `RoleBinding` matching naming patterns (`*-agent`, `*-bot`, `claude-*`).
- Reverse-lookup: credential fingerprints from [`sentinels/identity/client-side/identity-log-hook.sh`](../../../sentinels/identity/client-side/identity-log-hook.sh) joined by hash.

## Reference tooling

- [`discover-k8s-agents.sh`](./discover-k8s-agents.sh), lists every namespace-scoped ServiceAccount whose namespace matches `agent-*` or whose name matches `*-agent`/`*-bot`/`claude-*`. Feeds the operator-declared cross-reference.
- [`discover-cloudtrail-agents.sql`](./discover-cloudtrail-agents.sql), CloudWatch Logs Insights query listing every distinct AWS principal whose role name starts with the agent prefixes.

## Cross-layer cross-references

- Discovered ∧ ¬operator-declared = **shadow agent**. Investigate ownership; charter or retire.
- Discovered ∧ ¬self-declared = agent runtime did not register. Either older agent that predates the registration protocol, or registration failed silently.

## Common failure modes

- Audit logs have gaps (retention expired, log delivery failed, audit policy missing the resource). Cannot discover agents whose activity fell into a gap.
- Shadow agents in accounts/clusters where discovery has no credentials. Mitigation: org-wide cloud-account inventory and discovery agents in every account.
- Naming pattern misses agents that did not follow convention (e.g., a SA literally named `prod-helper` is an agent in disguise).

## Citation

NIST CSF 2.0 ID.AM-01, ID.AM-02. NIST AI RMF MAP 1.1, MAP 1.5. CSA MAESTRO Layer 4, Layer 7. NIST SP 800-92 (log management). NIST AI Agent Standards Initiative under CAISI (Feb 17, 2026).
