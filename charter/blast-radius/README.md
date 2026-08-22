# Charter, Blast radius

**Question.** What risk tier? What damage cap is acceptable? Under what conditions does the charter permit production access?

| Layer | Cell |
|---|---|
| Organizational | [`organizational/`](./organizational), risk tier taxonomy; org-wide damage caps and matching control requirements. |
| Domain | [`domain/`](./domain), which tiers the domain is authorized to operate; failure-mode reviews per tier. |
| Agent | [`agent/`](./agent), specific risk tier, specific damage cap, conditions for tier downgrade or retirement. |

Feeds [`../../controls/blast-radius/`](../../controls/blast-radius). The agent's risk tier determines which Covenants cells must be populated.
