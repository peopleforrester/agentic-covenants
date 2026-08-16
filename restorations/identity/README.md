# Restorations, Identity

**Intent.** Rotate credentials, re-issue per-agent identities, regenerate trust relationships.

**Order.** First. Every later recovery step authenticates against an identity.

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-restore-identity-local`: regenerate credential file with strict ACLs, rotate OIDC client secret, re-authenticate operator host to SSO, verify ACLs survived. |
| Server-side | [`server-side/`](./server-side/) | `agent-restore-identity-server`: disable old SA, recreate from declarative source, rotate IAM keys, re-establish OIDC trust policy, re-issue SPIFFE identity, verify no inherited permissions. |

Rebuilds what [`../../interventions/identity/`](../../interventions/identity/) revoked.
