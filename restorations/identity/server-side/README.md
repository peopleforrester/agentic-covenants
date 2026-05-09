# Restorations — Identity / Server-side

**Precondition.** Interventions L3-C1 has fired (ServiceAccount automount disabled, IAM deny-all attached, OIDC sessions revoked). Restorations L2-C1 has completed (new local credentials are in place).

**Authority.** On-call plus security review.

## Tooling

- `kubectl` with permission to delete and create ServiceAccounts in agent namespaces.
- AWS CLI (or GCP/Azure equivalent) with permission to manage IAM access keys and update trust policies.
- `spire-server` CLI if SPIFFE is in use.
- Source-of-truth manifests for the agent's RBAC under `manifests/rbac/`.

## Files in this directory

- [`agent-restore-identity-server`](./agent-restore-identity-server) — runbook script. Deletes old SA, recreates from declarative source, removes EmergencyDenyAll IAM policy, rotates IAM access keys (if any), checks OIDC trust-policy drift and restores from declarative source if drifted, re-issues SPIFFE identity.

## Verification

```bash
# 1. ServiceAccount exists and is the new instance
kubectl get sa -n agent-claude-code-prod claude-code -o jsonpath='{.metadata.creationTimestamp}'
# expected: recent timestamp

# 2. Emergency deny policy removed
aws iam list-role-policies --role-name claude-code-prod --query 'PolicyNames'
# expected: does not include EmergencyDenyAll

# 3. Old token rejected (test with a kubectl call using a captured-pre-incident token; expect 401)

# 4. New pods can mount tokens successfully
kubectl run identity-test --image=alpine --rm -it -n agent-claude-code-prod \
  --serviceaccount=claude-code -- sleep 10
# expected: clean start, no auth errors
```

## Common failure modes

- Deleting the SA but failing to recreate it because the YAML in source has drifted. The cluster has no SA; new pods cannot start.
- Trust policy drift not checked. The trust policy was the attack surface; restoring without verifying leaves it compromised.
- Forgetting to remove the EmergencyDenyAll IAM policy — the agent has identity but cannot do anything.
- Old IAM access keys not deleted — old credentials remain valid alongside new ones.

## Citation

NIST CSF 2.0 RC.RP-01, RC.IM-01; PR.AA-01 (recovery dimension). NIST SP 800-207. NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026).
