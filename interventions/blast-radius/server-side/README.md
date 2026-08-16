# Interventions, Blast radius / Server-side

**Trigger.** Falco alert from cluster, NetworkPolicy violation spike, ResourceQuota near-limit emergency, cross-namespace operations from an agent SA.

**Authority.** On-call, no second approval.

**Speed target.** Under 5 seconds for namespace freeze, under 60 seconds for full drain.

## Tooling

- `kubectl` with permission to apply NetworkPolicies, scale Deployments, and (for cordon-and-drain) cordon nodes.
- AWS CLI (or GCP/Azure equivalent) with permission to update Security Group egress rules.

## Files in this directory

- [`agent-contain-server`](./agent-contain-server), runbook script. Applies emergency NetworkPolicy default-deny, scales agent Deployments to zero, force-deletes pods, optionally cordons and drains nodes, and blocks egress at the cloud firewall.
- [`networkpolicy-emergency-deny.yaml`](./networkpolicy-emergency-deny.yaml), pre-staged default-deny NetworkPolicy with no allow rules. Applied to the agent namespace. **Pre-stage** at `/etc/agents/emergency/networkpolicy-emergency-deny.yaml`.
- [`sg-deny-all-egress.json`](./sg-deny-all-egress.json), pre-staged AWS Security Group egress-rule descriptions used by the runbook to update the agent's SG. **Pre-stage** at `/etc/agents/emergency/sg-deny-all-egress.json`.

## Verification

```bash
# 1. NetworkPolicy in effect
kubectl get networkpolicy -n agent-claude-code-prod emergency-deny-everything

# 2. Egress blocked
kubectl exec -n agent-claude-code-prod $(kubectl get pods -n agent-claude-code-prod -o name | head -1) -- \
  curl -sS --max-time 3 https://example.com 2>&1 || echo "OK: egress blocked"

# 3. Deployment scaled to zero
kubectl get deployments -n agent-claude-code-prod -o jsonpath='{.items[*].spec.replicas}'
# expected: 0 0 0...

# 4. No pods running
kubectl get pods -n agent-claude-code-prod
# expected: empty
```

## Common mistakes

- `kubectl drain` without `--grace-period=0` honors `terminationGracePeriodSeconds: 300`, the pod runs for 5 minutes. Use `--force --grace-period=0`.
- Existing TCP connections survive NetworkPolicy changes (CNI-dependent). Verify by attempting a fresh connection after applying.
- Cordoning the wrong node, verify the pods' actual node placement before draining.
- Cloud firewall rule modification fails silently if the security group is referenced by other resources. Verify rule before declaring contained.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02; PR.IR-01 (response dimension). NIST SP 800-61 Rev. 2. NISTIR 8596. OWASP ASI05, ASI08. NIST AI RMF MANAGE 4.1.
