# Interventions, Authorization / In-agent

**Empty by design.** Telling the agent "you have no permissions now" through prompts is bypassable through every prompt-injection vector that compromised authorization in the first place. Real intervention lives in [`../client-side/`](../client-side/) (deny-all hook, immutable bit) and [`../server-side/`](../server-side/) (Kyverno deny-all, empty Role).
