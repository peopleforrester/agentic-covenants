# Charter — Supply chain / Organizational

**Structural question.** Does the org maintain an allowlist of approved foundation models, an MCP server approval policy, a third-party dependency approval policy, and integrate AI vendor risk into procurement?

**Owner.** AI Governance Council with Procurement and Security.

## Template fragment

§6 (Approved foundation models) and §7 (Vendor risk assessment) of [`../../templates/organizational-policy.md`](../../templates/organizational-policy.md).

## Audit prompts

- What foundation models are on the approved list? When were they last reviewed?
- Does procurement integrate AI vendor risk? Is SOC 2 Type II required for production agents?
- Are subprocessors of approved vendors reviewed annually?

## Operational tie-in

The approved-models list is the upper bound on every agent charter's `dependencies.foundation_model`. PR review must reject any charter that names a model not on the org list.

## Citation

NIST CSF 2.0 GV.SC-01 through GV.SC-10 (cybersecurity supply chain risk management). NIST AI RMF GOVERN 6.1, GOVERN 6.2 (third-party risk), MAP 4.1. ISO/IEC 42001 §A.10 (third party). EU AI Act Art. 25 (relationships along the AI value chain). NIST SP 800-161 Rev. 1. NIST SP 800-218A.
