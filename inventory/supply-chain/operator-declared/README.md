# Inventory — Supply chain / Operator-declared

**What this cell records.** The authorized dependency manifest from the agent charter, version-controlled with audit trail.

## Fields

Mirrors the `dependencies:` block of [`charter/templates/agent-charter.yaml`](../../../charter/templates/agent-charter.yaml). Linked to:

- [`controls/supply-chain/client-side/mcp-allowlist.json`](../../../controls/supply-chain/client-side/mcp-allowlist.json) for runtime enforcement.
- [`controls/supply-chain/server-side/kyverno-verify-image-signatures.yaml`](../../../controls/supply-chain/server-side/kyverno-verify-image-signatures.yaml) for admission-time verification.

## Common failure mode

Manifest is updated in Charter but allowlist hashes in Covenants L2-C5 are not regenerated. Charter and runtime drift. Fix: automation that derives the runtime allowlist from the charter file at deploy time.

## Citation

NIST CSF 2.0 ID.AM-04, ID.RA-09. NIST AI RMF MAP 4.1. CSA MAESTRO Layer 1, Layer 7. NIST SP 800-218A.
