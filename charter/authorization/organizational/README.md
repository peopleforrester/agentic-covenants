# Charter, Authorization / Organizational

**Structural question.** Does the org have an AI Risk Appetite Statement that names hard prohibitions every agent must obey, and a change-control process for evolving scope policy?

**Owner.** AI Governance Council.

## Template fragment

§2.2 (Hard prohibitions), §2.3 (Agents requiring elevated approval), and §3 (Risk Appetite) of [`../../templates/organizational-policy.md`](../../templates/organizational-policy.md).

## Audit prompts

- What are the org's hard prohibitions for agents? Are they enforced at runtime via Covenants L3-C2?
- How does the org change scope policy? PR-with-Council-approval, or hand-edit?
- When was the policy last amended? Was the amendment recorded in Council minutes?

## Operational tie-in

Hard prohibitions are codified in the Kyverno policies under [`../../../controls/authorization/server-side/`](../../../controls/authorization/server-side/). If your AUP says "no agent has direct prod-database write," the corresponding `agents-no-cluster-roles` policy must include a deny rule for that specific resource.

## Citation

NIST CSF 2.0 GV.RM-01, GV.RM-02 (risk management objectives, risk appetite); GV.PO-01. NIST AI RMF GOVERN 1.2 (transparency), GOVERN 1.5 (ongoing monitoring). ISO/IEC 42001 §A.6.1 (risk management). EU AI Act Art. 9(2) (risk management as continuous iterative process).
