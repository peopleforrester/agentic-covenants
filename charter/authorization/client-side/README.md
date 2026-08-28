# Charter, Authorization / Domain

**Structural question.** Does the domain charter define the per-class scope (which APIs, data classes, environments, destructive verbs are allowed), inherit org-wide hard prohibitions, and add domain-specific ones?

**Owner.** Domain authority.

## Template fragment

§5 (Authorization) of [`../../templates/domain-charter.md`](../../templates/domain-charter.md).

## Audit prompts

- What scope does this domain authorize? Is it more restrictive than the org-wide ceiling?
- Are domain-specific prohibitions documented? Are they enforced at runtime?
- How does the domain change scope policy? Domain-lead-only, or with security-review co-sign?

## Operational tie-in

The domain's scope envelope is the upper bound on every agent charter in the domain. An agent charter that requests scope outside the domain charter must be rejected at PR review.

## Citation

NIST CSF 2.0 GV.PO-01; PR.AA-05 (charter dimension). NIST AI RMF GOVERN 1.4, MANAGE 2.4. ISO/IEC 42001 §A.6.2. EU AI Act Art. 14, Art. 15.
