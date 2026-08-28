# Charter, Blast radius / Organizational

**Structural question.** Does the org have a written risk tier taxonomy with explicit damage caps and the matching control requirements per tier?

**Owner.** AI Governance Council.

## Template fragment

§3 (AI Risk Appetite Statement) of [`../../templates/organizational-policy.md`](../../templates/organizational-policy.md), specifically the tier table:

| Tier | Description | Damage cap | Required controls |
|---|---|---|---|
| 1 | Read-only diagnostics | None | Charter + Identity + Authorization (read-only) |
| 2 | Scoped writes | N records / session, $X / day | Tier 1 + Approval gating + Blast radius |
| 3 | Destructive operations | Scope-limited | Tier 2 + Sentinels + Interventions runbooks |
| 4 | Production-critical | Per-agent declared | Tier 3 + multi-party approval, off-cluster identity, immutable backups |

## Audit prompts

- Does the org have a tier taxonomy? Or is "every agent is treated the same"?
- Are damage caps quantitative? "Acceptable risk for innovation" is not a damage cap.
- Is the control matrix per tier enforced at PR review? An agent charter that claims Tier 1 but requests destructive scope must be rejected.

## Operational tie-in

The tier table is the input to which Covenants cells must be populated for an agent. The PR-review checklist for new agent charters includes "tier ↔ controls" verification.

## Citation

NIST CSF 2.0 GV.RM-01, GV.RM-02 (risk management objectives, risk appetite). NIST AI RMF GOVERN 1.3 (risks identified are managed), MAP 5.1. ISO/IEC 42001 §A.6. EU AI Act Art. 9(3), 9(4) (risk-based approach).
