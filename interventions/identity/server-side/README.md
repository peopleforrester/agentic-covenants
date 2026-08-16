# Interventions, Identity / Server-side

**Trigger.** Same as client-side, plus indicators that the agent has cluster or cloud reach.

**Authority.** On-call, no second approval. Reversible.

**Speed target.** Under 30 seconds plus token TTL window.

## Tooling

- `kubectl` with permission to patch ServiceAccounts and delete Pods in agent namespaces.
- AWS CLI (or GCP/Azure equivalent) with permission to attach IAM policies.
- IdP API access for OIDC session revocation (Okta/Auth0/Keycloak/Dex).

## Files in this directory

- [`agent-revoke-server`](./agent-revoke-server), runbook script. Disables ServiceAccount automount, force-deletes pods to break token mounts, attaches an IAM `Deny *` policy to the agent role, terminates active OIDC sessions.
- [`iam-deny-all.json`](./iam-deny-all.json), pre-staged IAM policy document used by the runbook. `Deny *` on `*`. **Pre-stage this file** at `/etc/agents/emergency/iam-deny-all.json`.

## Verification

```bash
# 1. SA automount disabled
kubectl get sa -n agent-claude-code-prod claude-code -o jsonpath='{.automountServiceAccountToken}'
# expected: false

# 2. Pods recreated and failing to mount token
kubectl get pods -n agent-claude-code-prod
# expected: error/CrashLoopBackOff state, unable to start

# 3. IAM deny-all attached
aws iam list-role-policies --role-name claude-code-prod | grep EmergencyDenyAll

# 4. OIDC sessions terminated (provider-specific verification)
```

## Common mistakes

- Forgetting that existing pods retain their mounted tokens until restart. Step 2 (pod deletion) is mandatory.
- Token TTL of 1 hour means deny-policy is the only fast cutoff; revocation alone leaves a window.
- Deleting the IAM role instead of attaching a deny policy. Deletion can fail if other resources reference the role; deny policy is faster and reversible.
- Not testing the IdP API path before the incident. The emergency is the wrong time to learn that your Okta API token expired.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02; PR.AA-01 (response dimension). NIST SP 800-63B Rev. 4 (credential lifecycle). NIST SP 800-207 (Zero Trust). OWASP ASI03, ASI10. NIST AI RMF MANAGE 4.1.
