# Inventory — Identity / Operator-declared

**What this cell records.** The operator's intent: every agent the org has approved, by name, with owner, charter reference, and creation date.

## Where it lives

A GitOps registry: `agents/<agent-identifier>.yaml` per agent, committed to a repo under branch protection (the same protection that [`controls/approval-gating/server-side/`](../../../controls/approval-gating/server-side/) applies). PR-reviewed changes only.

## Reference tooling

This cell is paperwork, not code. The structure is the [`inventory/templates/inventory-record.yaml`](../../templates/inventory-record.yaml) format.

## Cross-layer cross-references

- Every entry here should match a self-declared registration (`../self-declared/`). Operator-declared but not self-declared = ghost agent.
- Every entry here should match a discovered identity (`../discovered/`). Operator-declared but not discovered = same ghost-agent state.
- A self-declared agent without an operator-declared entry = unauthorized agent. Investigate.

## Common failure modes

- Spreadsheet drift: registry hand-edited, not PR-reviewed.
- Stale entries: agent retired, registry not updated.
- Missing fields: owner-email empty or generic ("ai-team@"), backup-owner empty. Fail PR review on missing-required-field.

## Citation

NIST CSF 2.0 ID.AM-01, ID.AM-02, ID.AM-08. NIST AI RMF MAP 1.1, MAP 1.5. ISO/IEC 42001 §A.5. Singapore IMDA Agentic AI Framework (Jan 22, 2026).
