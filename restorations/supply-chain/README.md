# Restorations, Supply chain

**Intent.** Re-pin dependencies, regenerate SBOMs, re-verify signatures, rebuild from clean source.

**Order.** Last. Rebuilding from a clean source assumes the rest of the stack is ready to receive it.

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-restore-supply-chain-local`: reinstall agent runtime with signature verification, re-pin MCP server hashes from a clean source (not from possibly-tainted local copy), regenerate lockfiles from declared dependencies, run vulnerability scan on rebuilt environment. |
| Server-side | [`server-side/`](./server-side/) | `agent-restore-supply-chain-server`: rebuild and re-sign agent images from source, regenerate SBOMs with current vulnerability data, **rotate signing key entirely if exposure is suspected**, force redeploy with new SHA pins. |

Rebuilds what [`../../interventions/supply-chain/`](../../interventions/supply-chain/) quarantined.
