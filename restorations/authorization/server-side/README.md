# Restorations, Authorization / Server-side

**Precondition.** Interventions L3-C2 has fired (Kyverno deny-all in effect, agent Role empty, IAM deny-all attached). Restorations identity row complete. The declarative source-of-truth has been verified intact (signed commits, signed tags, off-cluster mirror).

**Authority.** On-call plus security review.

## Tooling

- `kubectl` with permission to apply RBAC and Kyverno resources.
- AWS CLI (or GCP/Azure equivalent) for IAM resync.
- `kubectl-neat` or `kubediff` for drift detection (optional).
- Source-of-truth manifests: `manifests/rbac/`, `manifests/kyverno/`, `infrastructure/iam/`.

## Files in this directory

- [`agent-restore-authorization-server`](./agent-restore-authorization-server), runbook script. Removes emergency Kyverno deny ClusterPolicy, reapplies the agent's Role from source, reapplies the operational Kyverno policies, re-removes any EmergencyDenyAll IAM policies, audits cluster drift vs source.
- [`drift-audit.sh`](./drift-audit.sh), drift-detection helper. Lists resources in the agent namespace not present in `manifests/`. Anything in cluster but not in source is suspect.

## Verification

```bash
# 1. Emergency Kyverno deny-all removed
kubectl get clusterpolicy emergency-deny-all-agents 2>&1 | grep -i "not found"

# 2. Agent Role has rules from source
kubectl get role -n agent-claude-code-prod claude-code -o jsonpath='{.rules}'
# expected: matches manifests/rbac/<agent>-role.yaml

# 3. Operational Kyverno policies in effect
kubectl get clusterpolicies | grep -E "(agents-no-cluster-roles|verify-image-signatures)"

# 4. Drift audit clean
./drift-audit.sh agent-claude-code-prod
# expected: no entries (or all entries explained)

# 5. Test action that was denied during incident now succeeds
kubectl --as=system:serviceaccount:agent-claude-code-prod:claude-code get pods
# expected: success
```

## Common failure modes

- Declarative source itself was compromised during incident. Verify source repo integrity (signed commits, signed tags) before reapply.
- Reapply does not delete drift; only adds/updates declared resources. Run drift audit and explicitly delete unknown resources.
- Emergency-deny ClusterPolicy not removed. The agent has its Role back but is still globally denied by the emergency policy.

## Citation

NIST CSF 2.0 RC.RP-01, RC.IM-01; PR.AA-05 (recovery dimension). NIST SP 800-207 (Zero Trust). CIS Kubernetes Benchmark. NIST AI RMF MANAGE 4.1.
