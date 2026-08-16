# Inventory, Identity / Self-declared

**What this cell records.** The agent's own report of its identity, charter binding, and liveness.

## Fields captured at registration

- `agent_identifier` (must match the Charter `agent.identifier`)
- `charter_ref` (path to the charter file in source control)
- `charter_version` (version on the charter at startup)
- `owner_email` (named owner from the charter)
- `instance_id` (per-process or per-pod identifier)
- `pid`, `hostname`, `started_at`
- `heartbeat_interval_seconds`

## Reference tooling

- [`agent-register.py`](./agent-register.py), minimal registration daemon. Sends a `POST /api/v1/agents/register` on startup, then heartbeats every N seconds, then `POST /api/v1/agents/deregister` on shutdown. Refuses to start if `charter_ref` is missing or charter is expired.

## Cross-layer cross-references

- Should appear in operator-declared (`inventory/identity/operator-declared/`). Mismatch = charter-integrity failure.
- Should match a discovered identity (`inventory/identity/discovered/`). Heartbeat lapse without deregister = dead-mans-switch alert.

## Common failure modes

- Agent never implements the registration protocol. Treat as a runtime requirement, not optional.
- Heartbeat dropped silently on network failure. Use exponential backoff with explicit logging.
- Registration is best-effort and the agent runs even if registration fails. Refuse to start without a successful registration ack.

## Citation

NIST CSF 2.0 ID.AM-01, ID.AM-02. NIST AI RMF MAP 1.1, MAP 4.1. CSA MAESTRO Layer 7. NIST NCCoE Concept Paper on AI Agent Identity (Feb 5, 2026).
