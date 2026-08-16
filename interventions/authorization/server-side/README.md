# Interventions, Authorization / Server-side

**Trigger.** RBAC denial spike, Kyverno PolicyReport failures from agent SAs, IAM Access Analyzer findings, Git pre-receive rejection spike.

**Authority.** On-call, no second approval.

**Speed target.** Under 10 seconds.

## Tooling

- `kubectl` with permission to apply ClusterPolicies and Roles in agent namespaces.
- AWS CLI with permission to attach IAM policies.
- Kyverno 1.18+ in `Enforce` mode (audit-only does not block).

## Files in this directory

- [`agent-deny-all-server`](./agent-deny-all-server), runbook script. Applies the emergency Kyverno ClusterPolicy, overwrites the agent's Role with empty rules, attaches IAM `Deny *` policy.
- [`kyverno-deny-all-agents.yaml`](./kyverno-deny-all-agents.yaml), pre-staged ClusterPolicy denying every operation from any `system:serviceaccount:agent-*`. Excludes the break-glass operator. **Pre-stage** at `/etc/agents/emergency/kyverno-deny-all-agents.yaml`.
- [`empty-role.yaml`](./empty-role.yaml), pre-staged Role with `rules: []` and the same name as the original agent Role. Overwriting it removes every permission. **Pre-stage** at `/etc/agents/emergency/empty-role.yaml`.

The IAM `Deny *` policy is at [`../../identity/server-side/iam-deny-all.json`](../../identity/server-side/iam-deny-all.json) (shared with identity revocation).

## Verification

```bash
# 1. Kyverno deny-all in effect
kubectl get clusterpolicy emergency-deny-all-agents
kubectl --as=system:serviceaccount:agent-claude-code-prod:claude-code get pods
# expected: failure with "Emergency lockdown: agent operations denied"

# 2. Role is empty
kubectl get role -n agent-claude-code-prod claude-code -o jsonpath='{.rules}'
# expected: [] or null

# 3. IAM deny-all attached
aws iam get-role-policy --role-name claude-code-prod --policy-name EmergencyDenyAll
```

## Common mistakes

- Kyverno deny-all rule that does not exclude break-glass identities, locks out the operator who needs to remediate.
- Kyverno installed in audit-only mode org-wide, emergency `Enforce` policy still does not block.
- Empty Role applied with `kubectl apply` but a stale RoleBinding still references a different (non-empty) Role.
- IAM deny-all that interacts badly with explicit allow policies in the same role's permission boundary.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02; PR.AA-05 (response dimension). NIST SP 800-207 (Zero Trust). OWASP ASI02, ASI03, ASI05. NIST AI RMF MANAGE 4.1.
