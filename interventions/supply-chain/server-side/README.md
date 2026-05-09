# Interventions — Supply chain / Server-side

**Trigger.** Cosign verification failure, SBOM diff with unauthorized package, image registry pull of unsigned image, FQDN egress denial spike to a suspect MCP domain.

**Authority.** On-call plus security review (registry-level changes affect other workloads).

**Speed target.** Under 5 minutes.

## Tooling

- `crane` (or registry-specific CLI) for image deletion.
- `kubectl` with permission to apply emergency ClusterPolicies and CiliumNetworkPolicies.
- Cilium with Hubble for FQDN-deny logging.

## Files in this directory

- [`agent-quarantine-supply-chain-server`](./agent-quarantine-supply-chain-server) — runbook script. Removes the poisoned image via `crane delete`, deploys an emergency Kyverno deny rule on the bad digest, applies the pre-staged Cilium FQDN deny policy, force-rolls workloads to the last-known-good image SHA.
- [`cilium-deny-suspect-fqdns.yaml`](./cilium-deny-suspect-fqdns.yaml) — pre-staged CiliumNetworkPolicy denying egress to a list of suspect FQDNs. Substitute the `matchName` entries during the incident or pre-stage with a known-malicious list. **Pre-stage** at `/etc/agents/emergency/cilium-deny-suspect-fqdns.yaml`.
- [`last-known-good-image-sha.txt`](./last-known-good-image-sha.txt) — pre-staged digest of the last-known-good agent image. **Audit periodically** (the pre-staged value should not itself be contaminated). **Pre-stage** at `/etc/agents/emergency/last-known-good-image-sha.txt`.

## Verification

```bash
# 1. Image removed from registry
crane manifest "$SUSPECT_IMAGE" 2>&1 | grep -i "not found" || echo "FAIL: image still in registry"

# 2. Kyverno deny in effect
kubectl run test --image="$SUSPECT_IMAGE" -n agent-claude-code-prod 2>&1 | grep -i "quarantined" || echo "FAIL: deny did not fire"

# 3. Egress to suspect domain blocked
kubectl exec -n agent-claude-code-prod $(kubectl get pods -n agent-claude-code-prod -o name | head -1) -- \
  curl -sS --max-time 3 https://suspect-mcp.example.com 2>&1 | grep -iE "couldn.t resolve|connection refused"

# 4. Workloads on last-known-good image
kubectl get deployment -n agent-claude-code-prod claude-code -o jsonpath='{.spec.template.spec.containers[0].image}'
# expected: matches last-known-good
```

## Common mistakes

- Image deletion does not affect already-pulled cached images on nodes. The force-rollout step is mandatory.
- Cosign deny rule by tag instead of digest — attacker pushes a new tag pointing at the same digest.
- DNS block applied at one level (cluster CNP) but not at corporate DNS — agents on operator hosts still resolve.
- Last-known-good SHA file is stale or itself contaminated. Audit the pre-staged value periodically.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02; ID.RA-09 (response dimension); GV.SC-07 (response dimension). NIST SP 800-218A. SLSA framework. OWASP ASI04. NIST AI RMF MANAGE 3.1.
