# Interventions, Identity

**Intent.** Revoke the credential, kill the session.

**Target time-to-response: 30 seconds** (account for token TTL).

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. The agent that misuses identity will not voluntarily revoke it. |
| Client-side | [`client-side/`](./client-side/) | `agent-revoke-local`: kill process tree, `systemctl stop` if applicable, delete credential file, force re-auth flag. |
| Server-side | [`server-side/`](./server-side/) | `agent-revoke-server`: disable ServiceAccount automount, delete pods to force re-mount, attach IAM deny-all, revoke OIDC sessions at IdP. |

Stops what [`../../controls/identity/`](../../controls/identity/) prevented and [`../../sentinels/identity/`](../../sentinels/identity/) detected.
