# Identity

**Intent.** The agent is distinguishable from any human or other agent. Every API call, every commit, every Kubernetes action is attributable to exactly one named agent identity, with no shared credentials and no inheritance from the operator.

## The row, at a glance

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | A non-trivial system prompt that names the agent. Advisory only. |
| Client-side | [`client-side/`](./client-side/) | Per-agent credentials in operator-owned config, filesystem ACLs, systemd unit binding the credential to the agent's process — never a shared shell rc. |
| Server-side | [`server-side/`](./server-side/) | Dedicated ServiceAccount per agent, OIDC federation, projected ServiceAccount token with 15-minute TTL, IAM trust policy with strict subject condition, optional SPIFFE/SPIRE for cross-cluster identity. |

## Why it matters

Identity is the foundation of every other row. Without per-agent identity:

- Authorization cannot be scoped per agent (the next row).
- Blast radius cannot be attributed when something goes wrong.
- Approval gating cannot identify which agent's request to gate.
- Supply chain provenance cannot be traced to which agent pulled the dependency.

When this row is sloppy, the rest of the matrix has nothing to anchor to.

## How to walk it

For each layer ask: *if the agent's identity is forged, stale, or shared, what stops the action at this layer?*

- **In-agent only:** the answer is "nothing." A prompt declaration is documentation, not authentication.
- **Client-side adds:** the credential file is owned by the operator and ACLed away from the agent's own user. The agent can still use it (the operator launches with it in env), but cannot read it at rest.
- **Server-side adds:** even with a stolen credential, the receiving cluster or cloud rejects requests where the OIDC subject does not match `system:serviceaccount:<ns>:<sa>` for this specific agent.

## Citations (per layer)

See [`../../CITATIONS.md`](../../CITATIONS.md). Quick reference:

- **In-agent**: advisory, no direct mapping.
- **Client-side**: NIST CSF 2.0 PR.AA-01, PR.AA-03; NIST SP 800-207; NIST SP 800-63 Rev. 4.
- **Server-side**: NIST CSF 2.0 PR.AA-01 through PR.AA-04; NIST SP 800-207 §3.4.1; NIST SP 800-63B Rev. 4; NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026).
