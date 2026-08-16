# Restorations, Supply chain / Server-side

**Precondition.** Interventions L3-C5 has fired (poisoned image deleted from registry, Kyverno deny rule on suspect digest applied, FQDN deny in effect, workloads on last-known-good SHA). All four prior recovery rows complete.

**Authority.** On-call plus security review.

## Tooling

- `cosign` for image re-sign and key rotation.
- `syft` for SBOM regeneration.
- `crane` for registry operations.
- KMS or HSM for the new signing key (if rotating).

## Files in this directory

- [`agent-restore-supply-chain-server`](./agent-restore-supply-chain-server), runbook script. Removes the emergency Kyverno deny ClusterPolicies, optionally rotates the cosign signing key (if `--rotate-signing-key` is passed), rebuilds and re-signs every agent image, regenerates SBOMs, force-rolls workloads to the new images, removes the emergency Cilium FQDN deny.

## Verification

```bash
# 1. Emergency Kyverno deny rules removed
kubectl get clusterpolicies | grep -E "emergency-deny-(image-)" || echo "OK: no emergency denies"

# 2. New signed image deploys
kubectl run test --image=ghcr.io/example-org/claude-agent@sha256:NEW_SIGNED_DIGEST -n agent-claude-code-prod
# expected: success

# 3. SBOM attestation present on new image
cosign tree ghcr.io/example-org/claude-agent@sha256:NEW_SIGNED_DIGEST

# 4. Egress to formerly-blocked MCP domain restored (if it was a false-positive)
kubectl exec -n agent-claude-code-prod $(kubectl get pods -n agent-claude-code-prod -o name | head -1) -- \
  curl -sS --max-time 3 https://api.anthropic.com -o /dev/null -w "%{http_code}\n"
```

## Common failure modes

- Signing key rebuild without rotation when key was exposed. **If there's any chance the signing key was on a compromised host, rotate it; rebuild alone keeps the same compromised identity signing.**
- SBOM diff not used; regeneration alone does not surface what changed. Always diff old vs new SBOM.
- Registry-cached compromised images survive on nodes. Force-rollout (covered in the runbook) is mandatory.

## Citation

NIST CSF 2.0 RC.RP-01, RC.IM-01; ID.RA-09 (recovery dimension); GV.SC-07 (recovery dimension). NIST SP 800-218 Rev. 1. NIST SP 800-218A. SLSA framework. NIST AI RMF MAP 4.1, MANAGE 3.1.
