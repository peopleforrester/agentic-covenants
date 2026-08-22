# Checklists

One walkable checklist per concern. Print it, sit with the agent's owner, and walk the row left to right.

| Concern | Checklist | The question it answers |
|---|---|---|
| Identity | [`identity.md`](./identity.md) | Is this agent distinguishable from every human and every other agent? |
| Authorization | [`authorization.md`](./authorization.md) | Can it only do what it was scoped for? |
| Blast radius | [`blast-radius.md`](./blast-radius.md) | When it does the wrong thing, how much breaks? |
| Approval gating | [`approval-gating.md`](./approval-gating.md) | Is the friction proportional to the risk, and does anyone still read the prompts? |
| Supply chain | [`supply-chain.md`](./supply-chain.md) | Is everything it loads verified before it is trusted? |

## How to score a row

For each of the three layers, mark one:

- **`[x]` Present and tested**: the control exists and you ran the verification command in this session. Not "we configured that once."
- **`[~]` Present, untested**: it exists, nobody has verified it recently. **This is where a hostile reviewer will catch you.**
- **`[ ]` Absent**: not implemented.
- **`[N/A]` Deliberately skipped**: with a reason written down. A skipped cell in a threat model is a decision. A skipped cell nobody recorded is a gap.

Then read the row:

| Pattern | Verdict |
|---|---|
| All three present | Defense in depth. Done. |
| Only in-agent | **Audit finding.** The model can be talked out of it. |
| Server-side only, no client-side | Enforced, but discovered late. Add client-side to fail fast and cut audit-log noise. |
| Client-side only | Sufficient only if the agent is confined to one operator machine. Insufficient the moment it has cloud or cluster reach. |

Note that some in-agent cells are **empty by design**: Blast radius and Supply chain in Covenants, and every in-agent cell in Interventions and Restorations. `[N/A]` is the correct mark there, not `[ ]`.

## Scope

These checklists cover the **Covenants (Protect)** matrix. Detection, response, and recovery have their own matrices with their own verification steps in [`sentinels/`](../sentinels), [`interventions/`](../interventions), and [`restorations/`](../restorations). A Covenants row that scores clean tells you the control is in place; it tells you nothing about whether you would notice or could stop it when the control fails.

## Before you start

Two facts to establish up front, because they change what "good" looks like:

- **Risk tier** (1 read-only, 2 scoped writes, 3 destructive, 4 production-critical), from the agent's charter. A Tier 1 agent does not need every cell populated. A Tier 4 agent needs all fifteen.
- **Reach**: operator laptop only, or cloud/cluster? Client-side-only postures are defensible for the former and not the latter.

If the agent has no charter, stop and write one first ([`charter/templates/agent-charter.yaml`](../charter/templates/agent-charter.yaml)). You cannot audit scope against an intent nobody recorded.
