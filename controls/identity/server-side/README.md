# Identity / Server-side

**Control.** Dedicated ServiceAccount or IAM principal per agent. OIDC federation with workload identity. Short-lived bound tokens (15-minute TTL). Auth provider rejects requests where agent identity is missing or stale. SPIFFE/SPIRE for cross-cluster identity.

**Strength.** Deterministic and external to the agent. Bypass requires IdP compromise, token replay within the TTL window, or a misconfigured trust policy that accepts tokens from unintended issuers.

## Tooling

- Kubernetes 1.28+ (for `expirationSeconds` on projected ServiceAccount tokens, restricted Pod Security Standards).
- AWS IAM Roles for Service Accounts (IRSA), GCP Workload Identity, or Azure Workload Identity.
- SPIFFE/SPIRE if you have multiple clusters or off-cluster components that need a single identity story.
- An OIDC IdP (Okta, Auth0, Keycloak, Dex).

## Files in this directory

- [`namespace.yaml`](./namespace.yaml) — dedicated namespace per agent with restricted Pod Security Standards.
- [`serviceaccount.yaml`](./serviceaccount.yaml) — per-agent ServiceAccount with the IRSA annotation linking to the AWS role.
- [`role-and-binding.yaml`](./role-and-binding.yaml) — namespace-scoped Role and RoleBinding (never ClusterRole). Verbs are explicit; no wildcards.
- [`pod-with-projected-token.yaml`](./pod-with-projected-token.yaml) — Pod that mounts a projected ServiceAccount token with 15-minute TTL and audience binding.
- [`aws-iam-trust-policy.json`](./aws-iam-trust-policy.json) — trust policy with strict OIDC subject condition. The `sub` field pins the role to one specific `system:serviceaccount:<ns>:<sa>` pair.
- [`spire-entry.sh`](./spire-entry.sh) — SPIRE registration command for cross-cluster identity. Optional but recommended if you have agents in more than one cluster.
- [`verify.sh`](./verify.sh) — confirms dedicated identity per agent, short token TTL, identity-bound role assumption, cross-agent isolation.

## Verification

```bash
./verify.sh agent-claude-prod claude-code
```

The script runs four checks against the live cluster:
1. Dedicated SA exists per agent and is not shared.
2. Token TTL is 15 minutes (not 1-hour or unbounded default).
3. AWS role assumption returns the dedicated role ARN.
4. The agent's Pod cannot read another agent's mounted token.

## Common mistakes

- ServiceAccount with cluster-wide scope (the 1.21-and-older default behavior).
- Token TTL set to the default (1 hour) or unbounded.
- Trust policy with `"sub": "system:serviceaccount:*:*"` — any SA in any namespace can assume the role.
- Storing the token in a regular Secret instead of a projected volume; the Secret persists past Pod lifecycle.
- Multiple agents sharing one IAM role with broad permissions, defeating per-agent attribution.
- Forgetting to pin the audience. Without `audience: agent-<name>`, the token is reusable by any service.

## Citation

NIST CSF 2.0 PR.AA-01, PR.AA-02 (identities proofed and bound), PR.AA-03, PR.AA-04 (identity assertions protected, conveyed, verified). NIST SP 800-207 §3.4.1 (per-session authentication). NIST SP 800-63B Rev. 4. NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026).
