# Inventory — Blast radius / Self-declared

**What this cell records.** What the agent says about its own scope of damage potential.

## Fields

- `risk_tier` (1–4 from charter)
- `damage_cap` (records-per-session, USD-per-day, forbidden ops)
- `current_environment` (dev / staging / prod)
- `current_data_class` (public / internal / confidential / regulated)

## Cross-layer

Should equal operator-declared. If self-declared current_environment > operator-declared environments = escalation event.

## Citation

NIST CSF 2.0 ID.RA-01. NIST AI RMF MAP 5.1, MAP 5.2.
