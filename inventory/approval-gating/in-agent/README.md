# Inventory, Approval gating / Self-declared

**What this cell records.** The agent's report of its charter freshness and its refusal to operate beyond the review window.

## Fields

- `last_charter_review_date`
- `next_review_due`
- `current_charter_version`
- `refuses_to_start_when_expired: true`

The agent runtime checks `next_review_due` at startup. If the date is in the past, registration aborts. The reference daemon at [`../../identity/in-agent/agent-register.py`](../../identity/in-agent/agent-register.py) implements this check.

## Citation

NIST CSF 2.0 ID.IM-01. NIST AI RMF GOVERN 1.5, MAP 4.1.
