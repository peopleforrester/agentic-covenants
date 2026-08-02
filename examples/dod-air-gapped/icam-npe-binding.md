# Binding an agent charter to a DoD ICAM NPE record

The Charter matrix and DoD ICAM are solving adjacent halves of the same problem. ICAM establishes that a Non-Person Entity exists, is credentialed, and is controlled by a responsible Person Entity. The agent charter establishes what that entity is permitted to do, at what risk tier, with what damage cap, and under what retirement conditions.

In an enclave you should not maintain those as two disconnected records. This is the field mapping.

## The PE-to-NPE control relationship

FICAM requires an NPE to be "under the control of an authorized Person Entity (PE) who has the ability to create, modify, or destroy the NPE account." For an AI agent this is not a formality — it is the accountability anchor that the Five Eyes joint guidance calls out as *accountability opacity* when it is missing.

| ICAM / NPE registry attribute | Agent charter field | Notes |
|---|---|---|
| NPE identifier | `agent.identifier` | Must be the same string in both systems. This is the join key. |
| NPE display name / description | `agent.name`, `agent.description` | |
| **Controlling PE** | `ownership.owner_name` + `ownership.owner_email` | The named human accountable. Not a group mailbox — FICAM wants a person who can destroy the account. |
| Alternate / delegate PE | `ownership.backup_owner_name` | Required, or departure of the owner orphans the NPE. |
| Sponsoring organization | `ownership.domain` (via the parent domain charter) | |
| Credential type and lifecycle | `dependencies` + the identity cell in use | DoD PKI certificate preferred over long-lived secrets; short-lived where the CA supports it. |
| Authorization scope | `authorized_scope` | ICAM records *access*; the charter records *permitted action*. Both are needed; they are not the same field. |
| Assurance / risk categorization | `risk_tier` | Map your tier taxonomy to the system categorization (FIPS 199 Low/Moderate/High) used in the ATO package. |
| Recertification date | `next_review_due` | Aligns the charter review cadence to the account recertification cycle so they cannot drift apart. |
| De-provisioning trigger | `retirement_criteria` | The charter criterion "owner departs and no backup accepts handoff within 30 days" is an NPE de-provisioning event, not just a governance note. |
| Emergency revocation authority | `incident_revocation.authority` | Who may invoke [`interventions/identity/server-side/`](../../interventions/identity/server-side/) without a second approval. |

## Where the charter says more than ICAM does

These charter fields have **no ICAM equivalent**, which is precisely the gap this framework exists to fill. Carry them in the charter and reference the charter from the NPE record:

- `damage_cap` — records-per-session, spend-per-day, forbidden operations. ICAM has no concept of a bounded blast radius for an authenticated entity.
- `risk_tier` driving *which controls are mandatory* — Tier 1 read-only agents do not need every cell; Tier 4 production agents need all fifteen.
- `approvals` — multi-party signature for Tier 3+, which is the Approval gating column expressed as governance rather than runtime.

## Where ICAM says more than the charter does

Do not duplicate these into the charter; reference them:

- Certificate serial numbers, issuing CA, revocation status. These belong in the credential system of record.
- Enterprise IdP group membership and attribute assertions.
- The DD Form 2875 replacement workflow record (the automated access-request workflow required by the September 2026 deadline).

## Practical guidance

1. **Make the charter file the source of truth for behavior, and the NPE registry the source of truth for credential state.** Cross-reference by `agent.identifier`. Do not fork the ownership field into two places that can disagree.
2. **Put the charter under the same change control as the ATO artifacts.** A scope expansion in the charter is a change to the authorization boundary; treat it like one.
3. **Wire retirement to de-provisioning.** The most common failure mode in both systems is the same: nobody removes the thing when it stops being needed. The Inventory matrix's cross-layer reconciliation (self-declared vs operator-declared vs discovered) is what catches orphaned agent NPEs.
4. **Expect the ICAM automated-workflow deadlines to touch this.** Access requests moving to automated workflows means agent access requests are in scope. A charter that already carries structured scope and approvals is far easier to feed into that workflow than a prose memo.
