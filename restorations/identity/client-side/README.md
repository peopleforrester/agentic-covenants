# Restorations, Identity / Client-side

**Precondition.** Interventions L2-C1 has fired (local credentials deleted, agent process killed). The IdP user/service account corresponding to this agent has been confirmed clean: no recent privilege grants from compromised admin sessions, no MFA factors added during incident window.

**Authority.** On-call.

## Tooling

- IdP API access (Okta, Auth0, Keycloak, Dex) for credential reissue.
- `setfacl` for the deny-on-self ACL pattern from [`../../../controls/identity/client-side/`](../../../controls/identity/client-side).

## Files in this directory

- [`agent-restore-identity-local`](./agent-restore-identity-local), runbook script. Issues fresh credential from IdP, places in operator-owned config with strict ACLs, removes the `requires_reauth` flag, verifies the deny-on-self ACL survived.

## Verification

```bash
# 1. Credential in place with correct permissions
ls -la /etc/agents/claude-code-prod/token
# expected: -rw-r----- root operators

# 2. Agent can authenticate
sudo -u agent-runner /usr/local/bin/claude --version

# 3. Old credential is invalid (test against IdP)
# Provider-specific: try a request with the old token, expect 401.
```

## Common failure modes

- Issuing the new credential with a long TTL by default. Re-pin to the 15-minute TTL from `controls/identity/server-side/pod-with-projected-token.yaml` to limit exposure.
- Forgetting to remove the `requires_reauth` flag, the agent never restarts.
- ACLs reset to defaults during recovery and not re-applied. The deny-on-self ACL must be reapplied or the agent can read its own credential at rest.

## Citation

NIST CSF 2.0 RC.RP-01 (recovery plan executed), RC.IM-01 (improvements integrated). NIST SP 800-61 Rev. 2. NIST SP 800-63B Rev. 4.
