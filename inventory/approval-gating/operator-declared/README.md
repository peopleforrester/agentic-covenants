# Inventory, Approval gating / Operator-declared

**What this cell records.** The operator's review calendar and outstanding-review tracking.

## Fields

- `last_owner_attestation`, owner re-signed the charter and confirmed the agent is still needed.
- `next_owner_attestation_due`
- `pending_approvals[]`, charter amendments awaiting signatures.
- `overdue_reviews[]`, agents whose `next_review_due` has passed.

## Operational tie-in

Drives an executive dashboard tracking review compliance per domain. Per-cell escalation when reviews are overdue.

## Common failure mode

Quarterly review process exists on paper, never executed. Reviews become rubber stamps when they happen. Mitigation: automated reminders, escalation if overdue, exec dashboard.

## Citation

NIST CSF 2.0 ID.IM-01, ID.IM-02. NIST AI RMF GOVERN 1.5. ISO/IEC 42001 §A.9.
