# Identity / Client-side

**Control.** Per-agent credentials in operator-owned config; no shared keys; filesystem ACLs preventing cross-agent credential access.

**Strength.** Deterministic when the operator-owned config is uncompromised. Bypassable through token theft from logs, process listings, or world-readable env files; through credential reuse if the operator copies the config; through agent processes that run as a privileged user.

## Tooling

- A secrets manager (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, 1Password CLI, or `pass` for solo work).
- `setfacl` (Linux) or `chmod` plus dedicated user accounts (macOS).
- An OIDC-issuing IdP (Okta, Auth0, Azure AD, Keycloak) for token-based credentials.
- `systemd` (Linux) or `launchd` (macOS) to bind the credential to the agent process.

## Files in this directory

- [`provision-credential.sh`](./provision-credential.sh) — creates a per-agent credential directory, locks down ownership, applies an ACL so the agent's own user cannot read the file at rest. Run as root.
- [`claude-code-prod.service`](./claude-code-prod.service) — systemd unit that loads the per-agent env file and runs the agent as a dedicated user. Drop in `/etc/systemd/system/`.
- [`verify.sh`](./verify.sh) — three checks: credential not in process listing, agent cannot read its own credential file at rest, every agent has a unique credential hash.

## Verification

Run `verify.sh`. All three checks must pass.

```bash
sudo ./verify.sh
```

## Common mistakes

- Using a single `~/.anthropic/credentials` for every agent on the box.
- Putting the token in a `.env` file checked into the repo.
- Setting the env var in `/etc/profile`, where every process inherits it.
- Logging the credential into the agent's own log file at startup.
- Granting the agent's own user write permission on `/etc/agents/` so the agent can rotate its own key — that ability lets the agent change its identity at will.

## Citation

NIST CSF 2.0 PR.AA-01, PR.AA-03. NIST SP 800-207 (Zero Trust Architecture). NIST SP 800-63 Rev. 4 (Digital Identity Guidelines).
