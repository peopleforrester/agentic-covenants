# Restorations — Blast radius / Server-side

**Precondition.** Interventions L3-C3 has fired (NetworkPolicy default-deny applied, Deployments scaled to zero, pods deleted). Identity and Authorization restorations rows complete. **The earliest indicator of compromise from Sentinels has been identified — pick a backup from before that timestamp.**

**Authority.** On-call plus security review.

## Tooling

- AWS CLI (or GCP/Azure equivalent) with permission to copy from immutable backup buckets.
- `terraform` (or `tofu`) for IaC redeploy.
- `kubectl` for NetworkPolicy and ResourceQuota reapply.
- The point-in-time-recovery tool for your data store: `pg_restore`, RDS PITR, etc.

## Files in this directory

- [`agent-restore-blast-radius-server`](./agent-restore-blast-radius-server) — runbook script. Removes emergency NetworkPolicy, reapplies operational NetworkPolicies + ResourceQuota + LimitRange from source, runs `terraform apply` against fresh state, optionally re-creates the namespace, restores data from a specified pre-incident backup snapshot.

## Verification

```bash
# 1. Emergency NetworkPolicy removed
kubectl get networkpolicy -n agent-claude-code-prod emergency-deny-everything 2>&1 | grep -i "not found"

# 2. Operational NetworkPolicies in effect
kubectl get networkpolicy -n agent-claude-code-prod
# expected: default-deny-all + claude-code-egress

# 3. ResourceQuota in effect
kubectl get resourcequota -n agent-claude-code-prod

# 4. terraform plan is clean
terraform plan -no-color | grep -E "Plan: 0 to add"

# 5. Data restored to expected pre-incident state
# (data-store-specific verification; check row counts / object inventory against pre-incident snapshot)
```

## Common failure modes

- Backup taken after contamination point. **Always pick a backup from before the earliest indicator of compromise from Sentinels**, not the most recent backup.
- Backups stored in same account as production. Immutable backups (S3 Object Lock, GCP Bucket Retention) reduce but do not eliminate this risk if the credentials that wrote them were compromised.
- Emergency NetworkPolicy not removed. Workloads come back up but cannot communicate.
- `terraform apply` against drifted state — the recovery applies the state-of-the-incident, not the desired state. Always `terraform plan` first and review the diff.

## Citation

NIST CSF 2.0 RC.RP-01, RC.IM-01; PR.IR-01 (recovery dimension); PR.DS-11 (backup restoration). NIST SP 800-34 Rev. 1 (contingency planning). NISTIR 8596. NIST AI RMF MANAGE 4.1.
