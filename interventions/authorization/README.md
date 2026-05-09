# Interventions — Authorization

**Intent.** Shrink permissions to nothing.

**Target time-to-response: 10 seconds.**

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-deny-all-local`: replace hook with deny-all template, `chattr +i` for immutability, replace settings.json with restrictive version, kill in-flight agent. |
| Server-side | [`server-side/`](./server-side/) | `agent-deny-all-server`: apply emergency Kyverno deny-all ClusterPolicy, replace agent Role with empty rules, attach IAM deny-all. |

Stops what [`../../controls/authorization/`](../../controls/authorization/) prevented and [`../../sentinels/authorization/`](../../sentinels/authorization/) detected.
