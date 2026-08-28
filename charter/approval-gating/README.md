# Charter, Approval gating

**Question.** Who must approve the charter itself? Who approves changes to it? Who approves retirement?

| Layer | Cell |
|---|---|
| Organizational | [`server-side/`](./server-side), AI Governance Council. Members named. Quorum and voting rules. |
| Domain | [`client-side/`](./client-side), Domain authority approves agent charters. Multi-party for Tier 3+. |
| Agent | [`in-agent/`](./in-agent), Charter signed by owner + domain authority + (Tier 3+) security review. Annual review cadence. Emergency revocation conditions. |

Feeds [`../../controls/approval-gating/server-side/`](../../controls/approval-gating/server-side), the charter file itself is protected by branch protection.
