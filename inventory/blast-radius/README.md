# Inventory, Blast radius

**Question.** Worst-case damage if compromised. Environments. Data classes. Revenue or customer impact.

| Layer | Cell |
|---|---|
| Self-declared | [`in-agent/`](./in-agent), agent reports its own declared risk tier, damage cap, current environment, current data class access. |
| Operator-declared | [`client-side/`](./client-side), operator records blast-radius profile and worst-case impact statement. |
| Discovered | [`server-side/`](./server-side), threat-modeling output (MAESTRO Layer 7, MITRE ATLAS), behavioral observation. |

The discovered layer for blast radius is essentially threat modeling. CSA Agentic AI Red Teaming Guide and MITRE ATLAS feed it.
