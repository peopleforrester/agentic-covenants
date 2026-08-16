# Interventions, Supply chain

**Intent.** Quarantine packages, halt distribution.

**Target time-to-response: 5 minutes** (registry-level operations are slower).

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-quarantine-supply-chain-local`: remove suspect MCP from allowlist, move suspect packages to `/var/quarantine/`, lock lockfile with `chattr +i`, pin runtime to last-known-good, kill agent. |
| Server-side | [`server-side/`](./server-side/) | `agent-quarantine-supply-chain-server`: `crane delete` poisoned image from registry, deploy emergency Kyverno deny rule on the bad digest, block compromised registry/MCP domain via Cilium FQDN deny, force redeploy with last-known-good image SHA. |

Stops what [`../../controls/supply-chain/`](../../controls/supply-chain/) prevented and [`../../sentinels/supply-chain/`](../../sentinels/supply-chain/) detected.
