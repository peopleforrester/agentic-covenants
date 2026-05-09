# Inventory — Authorization / Discovered

**What this cell records.** The runtime-effective permissions, regardless of declared scope.

## Sources

- `kubectl auth can-i --list --as=system:serviceaccount:agent-X:claude-code` for every agent SA.
- `aws accessanalyzer list-findings` for unused permissions per principal.
- `kubectl get policyreports -A` for which Kyverno policies are actually applying to which agents.

## Cross-layer

Discovered effective permissions > operator-declared scope = scope creep. Audit and either tighten or amend the charter.

## Citation

NIST CSF 2.0 ID.RA-09, ID.RA-01. NIST AI RMF MAP 5.1. NIST SP 800-207.
