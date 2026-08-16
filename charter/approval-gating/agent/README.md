# Charter, Approval gating / Agent

**Structural question.** Does the agent charter carry the required approval signatures, an annual review cadence, conditions for emergency revocation, and a clear identifier of the approver of every subsequent change?

**Owner.** Named human owner. Counter-signed by domain authority and (Tier 3+) security review.

## Template fragment

The `approvals:`, `review_cadence:`, `next_review_due:`, and `incident_revocation:` blocks of [`../../templates/agent-charter.yaml`](../../templates/agent-charter.yaml):

```yaml
approvals:
  - approver_name: Steven Heckler
    approver_role: Managing Director
    approval_date: 2026-04-15
    approval_signature: <PGP signature or commit SHA of approval PR>
  - approver_name: Tapas Banerjee
    approver_role: Security Review
    approval_date: 2026-04-15
    approval_signature: <PGP signature or commit SHA of approval PR>

review_cadence: quarterly
next_review_due: 2026-07-15

incident_revocation:
  conditions:
    - "Detected lethal-trifecta pattern in agent context"
    - "Two or more Sentinels alerts at severity ERROR within 24h"
    - "Owner judgment"
  authority: owner_or_domain_lead
```

## Audit prompts

- For [agent X], are all required approvers signed? Are signatures verifiable (PGP, signed-commit SHA)?
- When is the next review due? Has it been scheduled?
- What conditions trigger emergency revocation? Has the runbook for emergency revocation been drilled?

## Operational tie-in

- The charter file lives under branch protection from [`../../../controls/approval-gating/server-side/`](../../../controls/approval-gating/server-side/). Tampering with the charter is detected by [`../../../sentinels/approval-gating/server-side/audit-branch-protection.yml`](../../../sentinels/approval-gating/server-side/audit-branch-protection.yml).
- `incident_revocation` conditions feed the on-call's authority to invoke [`../../../interventions/identity/server-side/agent-revoke-server`](../../../interventions/identity/server-side/agent-revoke-server) without a second approval.

## Common failure mode

Approval signatures become reflexive, alert fatigue at the governance layer. Tiered approval (more rigorous review for Tier 3+) is the same cure used in [Covenants L2-C4](../../../controls/approval-gating/client-side/).

## Citation

NIST CSF 2.0 GV.RR-02; GV.OV-02, GV.OV-03 (oversight reviews; organization adjusts). NIST AI RMF GOVERN 4.1, MANAGE 4.1. ISO/IEC 42001 §A.4.2, §A.9 (performance evaluation). EU AI Act Art. 14, Art. 26.
