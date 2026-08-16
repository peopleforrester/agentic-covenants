# Inventory, Approval gating / Discovered

**What this cell records.** Independent verification that charter files actually exist and have been touched on cadence.

## Sources

- `git log charters/`, last-modified dates per charter file.
- GitHub Pull Request API, last-PR-merged per charter file.
- Cross-reference against operator-declared `next_review_due` and self-declared `last_charter_review_date`.

## Cross-layer

- charter file last modified before the operator-declared `last_owner_attestation` = stale, attestation may have been ceremonial.
- self-declared `last_charter_review_date` after the file was last modified = self-declared is reporting a review that didn't happen.

## Citation

NIST CSF 2.0 ID.IM-01, ID.IM-03. NIST AI RMF GOVERN 1.5, MANAGE 4.1.
