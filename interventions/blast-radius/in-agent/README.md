# Interventions, Blast radius / In-agent

**Empty by design.** An agent breaching its blast-radius envelope cannot be reliably told to stop. Real intervention lives in [`../client-side/`](../client-side/) (process-group kill, sandbox teardown) and [`../server-side/`](../server-side/) (emergency NetworkPolicy, scale to zero).
