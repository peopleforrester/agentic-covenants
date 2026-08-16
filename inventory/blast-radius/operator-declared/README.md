# Inventory, Blast radius / Operator-declared

**What this cell records.** The operator's worst-case impact statement and theoretical blast envelope.

## Fields

- `environments[]`
- `data_classes[]`
- `worst_case_impact`, quantitative or scoped statement (e.g., "Q4 revenue forecasting outage up to 4 hours" or "limited to internal CI/CD tooling").
- `recovery_time_objective_hours`
- `recovery_point_objective_hours`

## Cross-layer

Drives Charter risk tier choice. Drives which Covenants cells are mandatory for this agent.

## Common failure mode

Worst-case impact written as boilerplate ("low impact"). Vague impact statements cannot drive tiering. Force quantitative entries.

## Citation

NIST CSF 2.0 ID.RA-01, ID.RA-04. NIST AI RMF MAP 5.1, MAP 5.2. CSA MAESTRO Layer 4, Layer 6. NIST AI 600-1 (GAI risks taxonomy). EU AI Act Art. 9(2).
