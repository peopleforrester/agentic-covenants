# Interventions — Blast radius

**Intent.** Contain the in-flight damage.

**Target time-to-response: 5 seconds.** *The one you cannot afford to lose.*

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-isolate-host`: process-group kill of the agent tree, sandbox teardown, `docker stop` / `kubectl delete pod` for container variants, last-resort network isolation. |
| Server-side | [`server-side/`](./server-side/) | `agent-contain-server`: emergency NetworkPolicy default-deny, scale Deployment to zero, force-delete pods, optional cordon-and-drain, block egress at cloud firewall. |

Stops what [`../../controls/blast-radius/`](../../controls/blast-radius/) prevented and [`../../sentinels/blast-radius/`](../../sentinels/blast-radius/) detected.
