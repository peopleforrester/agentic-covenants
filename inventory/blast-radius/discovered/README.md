# Inventory, Blast radius / Discovered

**What this cell records.** Threat-modeled and behaviorally-observed actual blast surface, regardless of declared envelope.

## Sources

- **CSA MAESTRO Layer 7** (Agent Ecosystem) analysis per agent. The CSA "Applying MAESTRO" doc (Feb 11, 2026) walks the per-layer threat enumeration.
- **MITRE ATLAS techniques** mapped to each agent: which adversarial techniques apply given the agent's identity, deps, and scope.
- **Lateral-movement path analysis**: from the agent's identity, what high-value targets are reachable via 0/1/2 hops in IAM trust + RBAC + network reachability?
- **Behavioral observation**: what has the agent actually touched in the last N days? Cross-reference with declared scope.

## Reference tooling

These analyses are usually performed by security engineering (CSA Red Team Guide playbook) and not committed scripts. Output should land in the inventory record under `discovered.blast_radius_assessment`.

## Citation

NIST CSF 2.0 ID.RA-01, ID.RA-04, ID.AM-05. NIST AI RMF MAP 5.1, MAP 5.2, MAP 3.1. CSA MAESTRO Layer 4, Layer 7. MITRE ATLAS. CSA Agentic AI Red Teaming Guide.
