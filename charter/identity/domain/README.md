# Charter, Identity / Domain

**Structural question.** Does each domain that operates agents have a signed domain charter naming who in the domain is permitted to create agents, what the escalation path is, and what audit trail location records charter signatures?

**Owner.** Domain authority (Platform Engineering Director, Security Director, Customer Engineering Director, etc.). Counter-signed by the AI Governance Council.

## Template fragment

This cell is satisfied by §4 (Identity) and §1 (Scope) of [`../../templates/domain-charter.md`](../../templates/domain-charter.md). Specifically:

- §1 names the agent classes the domain authorizes.
- §4 names the roles in this domain authorized to create agents and the escalation path.

## Audit prompts

- Which domains operate agents? Is there a domain charter for each?
- Who in [domain] is allowed to create agents? Is that role-based or named-individual-based?
- Where is the audit trail of charter signatures for this domain?

## Operational tie-in

The domain charter constrains who in the domain can sign new agent charters. When a [Domain] employee proposes a new agent, the named role here is who reviews and signs.

## Citation

NIST CSF 2.0 GV.RR-02 (roles, responsibilities, and authorities); GV.OV-01 (oversight). NIST AI RMF GOVERN 2.1, GOVERN 5.1 (engaging stakeholders). ISO/IEC 42001 §A.6.2 (AI objectives). EU AI Act Art. 26 (deployer obligations).
