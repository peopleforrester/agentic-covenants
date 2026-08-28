# Inventory, Approval gating

**Question.** Who approved this agent, when last reviewed, when next review due, when does retirement fire.

| Layer | Cell |
|---|---|
| Self-declared | [`in-agent/`](./in-agent), agent reports `last_charter_review`, `next_review_due`, `current_charter_version`. **Refuses to start if charter is expired.** |
| Operator-declared | [`client-side/`](./client-side), review calendar with quarterly attestation, pending and overdue reviews tracked. |
| Discovered | [`server-side/`](./server-side), registry of charter files in source control, last-modified, last-PR-merged. |
