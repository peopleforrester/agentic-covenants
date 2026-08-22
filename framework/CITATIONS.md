# Citations

Cell-level mapping. Each control or control cluster cites the most directly applicable framework subcategory. Where multiple subcategories apply, the primary one is listed first.

This file is the line of defense against "you just made this up" reviewer attacks.

## Frameworks referenced

### United States authoritative frameworks

- **NIST Cybersecurity Framework 2.0** (NIST CSWP 29, February 26, 2024). Six functions: Govern, Identify, Protect, Detect, Respond, Recover. The Agentic Covenants Matrix is **Protect**. Subcategory IDs use the format `PR.AA-01` (hyphen, not period). **Note that ID.SC was withdrawn in CSF 2.0 final and supply-chain risk management moved entirely to GV.SC.**
- **NISTIR 8596** (Cybersecurity Framework Profile for Artificial Intelligence, "Cyber AI Profile," preliminary draft December 16, 2025). Overlays AI-specific considerations on every CSF 2.0 subcategory with High, Moderate, or Foundational priority assignments. Comment period closed January 30, 2026. The most current US-government overlay of CSF onto AI-system context.
- **NIST AI Risk Management Framework 1.0** (NIST AI 100-1, January 26, 2023). Four functions: Govern, Map, Measure, Manage.
- **NIST AI 600-1** (Generative AI Profile, July 26, 2024). Cross-sectoral profile.
- **NIST AI 100-2 E2025** (Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations, March 24, 2025). **Extends taxonomy to autonomous AI agents**, including indirect prompt injection. Replaces the 2023 edition.
- **NIST NCCoE Concept Paper, "Accelerating the Adoption of Software and Artificial Intelligence Agent Identity and Authorization"** (February 5, 2026). Comments closed April 2, 2026. Treats agent identity as established by an external IdP via OAuth 2.0 or equivalent, with metadata recording supervising agents or users. **Direct grounding for the Identity column.**
- **NIST AI Agent Standards Initiative** under CAISI (Center for AI Standards and Innovation, which replaced the AI Safety Institute). Launched February 17, 2026. RFI on AI Agent Security closed March 9, 2026.
- **NIST SP 800-207** (Zero Trust Architecture, August 2020).
- **NIST SP 800-218** (SSDF v1.1, February 2022) and **NIST SP 800-218 Rev. 1 draft** (December 17, 2025).
- **NIST SP 800-218A** (Generative AI Profile of SSDF, July 26, 2024, final).
- **NIST SP 800-160 Vol. 1** (Engineering Trustworthy Secure Systems, Rev. 1, November 2022).
- **NIST SP 800-63 Revision 4** (Digital Identity Guidelines, July 2025, all four volumes final).
- **NIST SP 800-161 Rev. 1** (Cybersecurity Supply Chain Risk Management Practices, May 2022).
- **NIST SP 800-34 Rev. 1** (Contingency Planning Guide, May 2010).
- **CISA / NSA / FBI / international partners, "AI Data Security" Cybersecurity Information Sheet** (May 22, 2025).
- **CISA / NSA / ACSC / Canadian Centre for Cyber Security / NZ NCSC / UK NCSC, "Careful Adoption of Agentic AI Services"** (April 30, 2026). **The first multi-nation joint guidance dedicated to agentic AI**, and the closest thing to authoritative doctrine this framework maps to. Thirty pages covering the full adoption lifecycle. Its five named risk categories map almost one-to-one onto this matrix's five concerns, see [Five Eyes crosswalk](#five-eyes-risk-categories-mapped-to-the-five-concerns) below.
- **CISA / Australian Signals Directorate ACSC, "Principles for the Secure Integration of AI in Operational Technology"** (December 3, 2025).
- **CISA, "Deploying AI Systems Securely"** (joint guidance, April 2024).
- **EO 14179 and the AI Action Plan** (January and July 2025). EO 14110 (October 30, 2023) was **rescinded January 23, 2025**; the operative executive document is now the AI Action Plan, which drives ongoing NIST work.

### US Department of Defense and federal control frameworks

The rest of this file speaks the language of NIST CSF 2.0, OWASP, and ISO. A US federal or DoD program office does not authorize systems against those. It authorizes against **NIST SP 800-53 control families**, the **DoD Zero Trust capability activities**, and an **RMF/cATO** (now CSRMC) authorization process. This section is the translation layer.

- **NIST SP 800-53 Rev. 5** (Rev. 5.2.0 finalized August 2025 per EO 14306). 1,196 controls across 20 families. Baselines: Low ~77, Moderate ~323, High ~421 controls, then tailored. Rev. 5 is **outcome-based rather than prescriptive**, which is precisely what lets an admission policy or a PreToolUse hook satisfy a control: any technology that demonstrably achieves the outcome can be the implementation. Families this matrix touches most: **AC** (Access Control), **AU** (Audit and Accountability), **CA** (Assessment, Authorization, and Monitoring), **CM** (Configuration Management), **CP** (Contingency Planning), **IA** (Identification and Authentication), **IR** (Incident Response), **RA** (Risk Assessment), **SA** (System and Services Acquisition), **SC** (System and Communications Protection), **SI** (System and Information Integrity), **SR** (Supply Chain Risk Management), **PM** (Program Management).
- **DoD Risk Management Framework** (DoDI 8510.01; NIST SP 800-37 Rev. 2). Seven steps: Prepare, Categorize, Select, Implement, Assess, Authorize, Monitor. **CNSSI 1253** supplies the DoD-specific baselines and National Security System overlays on top of 800-53.
- **Continuous Authorization to Operate (cATO)** (DoD CIO cATO Evaluation Criteria). Three pillars: **Continuous Monitoring (ConMon)**, **Active Cyber Defense (ACD)**, **Secure Software Supply Chain (SSSC)**. cATO is this framework's structural precedent: it moved assurance out of a periodic review layer and into the infrastructure, continuously. The Agentic Covenants argument is the same move applied to agent behavior rather than system configuration.
- **Cybersecurity Risk Management Construct (CSRMC)** (announced September 24, 2025). DoD's replacement for RMF as the primary cybersecurity framework for its own systems. Five phases (Design, Build, Test, Onboard, Operations) and ten principles including **Automation**, **Continuous Monitoring and ATO**, **DevSecOps**, and **Cyber Survivability**. CSRMC is DoD formally accepting at the framework level that static, checklist-driven compliance cannot keep pace, which makes an infrastructure-enforced behavioral framework an extension of accepted doctrine rather than a novel claim. (CSRMC governs DoD's own systems; **CMMC** remains the regime for defense contractors handling FCI/CUI.)
- **DoD Zero Trust Strategy** (DoD CIO, October 2022) and **DoD Zero Trust Reference Architecture v2.0** (DISA/NSA, September 2022). Seven pillars: **User, Devices, Network/Environment, Application & Workload, Data, Visibility & Analytics, Automation & Orchestration**. **152 capability activities**: 91 at Target Level (mandated end of FY2027) and 61 more at Advanced Level (FY2032). A **Zero Trust Strategy 2.0** adding OT, weapon-systems, and defense-critical-infrastructure guidance was expected around March 2026. **DTM 25-003** ("Implementing the DoD Zero Trust Strategy," July 2025) establishes the ZT Portfolio Management Office and the conditional-access-depends-on-enterprise-ICAM requirement.
- **Department of the Air Force Zero Trust Strategy v1.0** (DAF CIO, July 2024) and the **DAF Enterprise ICAM Roadmap**. DAF targets **Intermediate maturity by end of FY2028**, one year beyond the DoD Target mandate. The ICAM roadmap explicitly calls out an **ICAM solution for Non-Person Entities (NPEs)** as a deliverable.
- **DoD ICAM** (DoD ICAM Strategy; DoD Enterprise ICAM Reference Design; DoDI 8520.03; NIST SP 800-63 for IAL/AAL). Four domains: Identity Management, Credential Management, Access Management, Governance. **Non-Person Entities (NPEs)**, devices, service accounts, applications, RPA workers, and now AI agents, must each be **under the control of an authorized Person Entity (PE)** who can create, modify, or destroy the NPE account. Live deadlines: automated access workflows available to system owners by **June 2026**; all access requests through automated workflows by **September 2026** (retiring the DD Form 2875 SAAR); financial systems on automated ICAM provisioning by **end of FY2026**.
- **DoD Responsible AI (RAI)** (DoD AI Ethical Principles, February 2020; RAI Strategy and Implementation Pathway, June 2022, updated October 2024). Five principles: **Responsible, Equitable, Traceable, Reliable, Governable**. **"Governable"** is the principle this framework operationalizes: systems must have the ability to detect and avoid unintended consequences, and the ability to disengage or deactivate systems that demonstrate unintended behavior. The **Warfighter Trust** tenet requires traceable feedback on system status and clear operator procedures to activate and deactivate system functions, which is, in this matrix's terms, Sentinels plus Interventions.
- **DoD Cloud Computing SRG Impact Levels** (DISA). **IL2** (non-CUI, FedRAMP Moderate), **IL4** (CUI, FedRAMP Moderate + DoD overlay), **IL5** (CUI + unclassified NSS, FedRAMP High + DoD overlay), **IL6** (SECRET, DISA-authorized separately). FedRAMP authorization is **not** automatic DoD authorization. The Impact Level determines which cells in this matrix can use public infrastructure at all, see [`examples/dod-air-gapped/`](../examples/dod-air-gapped).
- **DISA STIGs** (~500 Security Technical Implementation Guides). Prescriptive configuration standards; open STIG findings become POA&M items. Relevant to the Blast radius client-side and server-side cells, where a STIG for the container platform or OS is the DoD-specific expression of the same hardening.
- **DoDI 5400.19** (Public Affairs Use of Artificial Intelligence). Narrow scope, but a live example of DoD issuing AI-use policy by function.

**Standing caveat for federal readers:** as of July 2026, the Congressional Research Service reports there is **no official US government guidance or policy specifically on agentic AI** (CRS IF13151, updated July 6, 2026). The Five Eyes joint guidance is advisory, not directive. The mappings below are therefore *crosswalks a program can defend to an AO*, not compliance claims. Nothing here substitutes for your AO's determination.

### International and standards-body frameworks

- **ISO/IEC 42001:2023** (AI Management System, December 2023). The only certifiable AI management system standard.
- **ISO/IEC 23894:2023** (AI Risk Management Guidance, February 2023).
- **EU AI Act, Regulation (EU) 2024/1689** (entered force August 1, 2024). Phased applicability: prohibitions and AI literacy from February 2, 2025; GPAI obligations from August 2, 2025 (Commission GPAI enforcement powers activating August 2, 2026). **The "Digital Omnibus on AI" (provisional agreement, May 7, 2026) defers the high-risk Annex III obligations from August 2, 2026 to December 2, 2027, and pushes synthetic-content marking to December 2, 2026.** (The original August 2, 2026 high-risk date is what this framework was first written against; the deferral was still provisional and pending formal adoption and Official Journal publication as of mid-2026, so verify the operative dates before relying on them.) Maximum fines: EUR 35M or 7% of global turnover. Articles directly relevant: **Article 9** (risk management system), **Article 13** (transparency), **Article 14** (human oversight), **Article 15** (accuracy, robustness, cybersecurity), **Articles 26–29** (deployer obligations), and **Articles 72–73** (post-market monitoring and serious-incident reporting).
- **EU AI Act Article 73, serious-incident reporting.** **In force since 2 August 2026**, the same date the high-risk obligations took effect. (The Commission's own final guidance and reporting template, consulted on in late 2025, were expected to apply from that date; verify whether the final text has published before relying on its detail.) Providers must notify the relevant national authority without undue delay: **15 days** in the general case, **10 days** where a death may have been caused, and **2 days** for a widespread infringement or a serious and irreversible disruption of critical infrastructure. *(Verify how the Digital Omnibus deferral of the high-risk obligations interacts with this timeline for your specific system class before relying on it.)* This is the clearest external deadline the Detect and Respond matrices answer to: **a two-day reporting clock is unmeetable without automated detection.** See [`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md) and [`INTERVENTIONS_MATRIX.md`](./INTERVENTIONS_MATRIX.md).
- **Singapore IMDA Model AI Governance Framework for Agentic AI** (January 22, 2026, launched at Davos). **The first governmental framework dedicated to agentic AI.** Four dimensions: assess and bound risk; meaningful human accountability; technical controls and processes; end-user responsibility.
- **UK AI Security Institute (AISI)** "AI scheming" research (early 2026). Documented approximately 700 real-world cases with a 5x rise October 2025 through March 2026.
- **Japan AI Guidelines for Business v1.0** (METI/MIC, April 19, 2024).
- **Australia Voluntary AI Safety Standard** (September 2024).

### OWASP and CSA frameworks

- **OWASP Top 10 for LLM Applications 2025** (released November 2024). LLM01 Prompt Injection through LLM10 Unbounded Consumption.
- **OWASP Top 10 for Agentic Applications 2026** (released December 9, 2025 by OWASP GenAI Security Project). ASI01 through ASI10. Foregrounds two design principles: **Least Agency** and **Strong Observability**.
- **OWASP AIVSS v0.8** (March 2026, ahead of RSAC). Scoring system for agentic risks; provides severity language for the Approval Gating column.
- **OWASP MCP Top 10** (beta 2026, Vandana Verma Sehgal). MCP01 Token mismanagement, MCP02 Privilege escalation via scope creep, MCP03 Tool poisoning, MCP04 Supply chain attacks, MCP05 Command injection and execution, MCP06 Intent flow subversion, MCP07 Insufficient authentication, MCP08 Lack of audit telemetry, MCP09 Shadow MCP servers, MCP10 Context injection and over-sharing.
- **CSA MAESTRO** (Ken Huang, Cloud Security Alliance, February 6, 2025). Seven-layer threat model for agentic AI.
- **CSA, "Applying MAESTRO to Real-World Agentic AI Threat Models"** (February 11, 2026).
- **CSA Agentic AI Red Teaming Guide** (May 2025). Twelve threat categories for the companion Detect matrix.

### Vendor and lab frameworks

- **Anthropic, "Claude Code auto mode: a safer way to skip permissions"** (March 26, 2026). Source for the **93% permission-prompt approval rate**, the Sonnet 4.6 two-stage classifier architecture, and the 8.5% / 0.4% / 17% rate measurements.
- **Anthropic, "Making Claude Code more secure and autonomous"**. Sandbox runtime built on Linux bubblewrap and macOS Seatbelt; **84% reduction in permission prompts**.
- **Anthropic Responsible Scaling Policy, OpenAI Preparedness Framework, Google DeepMind Frontier Safety Framework**. Lab-side capability frameworks governing what models are released. This matrix governs what released models are allowed to do inside the perimeter.
- **Google SAIF** (Secure AI Framework). Six elements with a detection-and-response extension.
- **MITRE ATLAS**. Adversarial attack catalog for ML and AI systems. Use for threat-modeling each cell.

### Supporting analyses and operational definitions

- **Stephane Derosiaux, "Work only works because humans are slow"** (The Technical Executive, May 4, 2026). Articulates why post-hoc governance assumptions fail for agents.
- **Simon Willison, "the lethal trifecta for AI agents"** (June 2025, repeatedly cited through April 2026). Private data plus untrusted content plus external communication. Operational definition of forbidden state.
- **Stuart Russell, "Human Compatible"** (2019). Assistance games, conceptual ancestor to the judgment-query escalation pattern.
- **Capability-based security** (1970s onward). "Ask before doing the irreversible thing" predates LLMs by decades.
- **AHRQ PSNet alarm-fatigue research**. Documented failure mode of high-frequency alerting; analog for human-in-the-loop fatigue.

## Identity row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | EU AI Act / ISO | Other |
|---|---|---|---|---|---|---|---|
| In-agent | System prompt declares agent identity (advisory; no enforcement) | (advisory; no direct mapping) | GOVERN 1.5; MAP 4.1 | LLM07 (related risk) | ASI03 (mitigation principle) | ISO/IEC 42001 §8.2 | NISTIR 8596 (overlay) |
| Client-side | Per-agent credentials, no shared keys, filesystem ACLs | PR.AA-01; PR.AA-03 | MANAGE 2.4 | LLM02 | ASI03 | ISO/IEC 42001 §A.7 | NIST SP 800-207 (Zero Trust); NIST SP 800-63 Rev. 4 |
| Server-side | Dedicated ServiceAccount, OIDC federation, short-TTL bound tokens, SPIFFE/SPIRE | PR.AA-01; PR.AA-02; PR.AA-03; PR.AA-04 | MANAGE 4.1 | LLM02; LLM06 | ASI03; ASI10 | EU AI Act Art. 14; ISO/IEC 42001 §A.7 | NIST SP 800-207 §3.4.1; NIST SP 800-63B Rev. 4; **NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026); Singapore IMDA Agentic AI Framework (Jan 22, 2026)** |

## Authorization row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | EU AI Act / ISO | Other |
|---|---|---|---|---|---|---|---|
| In-agent | Model instructions, scoped tool descriptions | (advisory; no direct mapping) | MAP 5.1; MAP 5.2 | LLM06 (mitigation principle) | ASI02 (mitigation principle) | ISO/IEC 23894 | NIST AI 100-2 E2025 (adversarial ML) |
| Client-side | `--allowedTools` deny-by-default, capability-based tool restriction, PreToolUse hooks (deny-then-ask-then-allow), operator-owned hook config | PR.AA-05; PR.PS-01 | MANAGE 2.4; MANAGE 4.1 | LLM06; LLM05 | ASI02; ASI05; OWASP Least Agency principle | EU AI Act Art. 14, Art. 15 | NIST SP 800-207 §2.1; OWASP MCP02, MCP05 |
| Server-side | Scoped RBAC Roles, IAM with explicit ARN, Kyverno or OPA admission, namespace scoping | PR.AA-05; PR.PS-01; PR.PS-05 | MANAGE 2.4; MANAGE 4.1 | LLM06; LLM05 | ASI02; ASI03; ASI05 | EU AI Act Art. 15; ISO/IEC 42001 §A.6 | NIST SP 800-207 (Zero Trust); CIS Kubernetes Benchmark; NISTIR 8596 |

## Blast radius row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | EU AI Act / ISO | Other |
|---|---|---|---|---|---|---|---|
| In-agent | (no enforcement; advisory only) | (no mapping) | MAP 5.1; MEASURE 2.6, 2.7 | LLM06 | ASI02; ASI05 |, |, |
| Client-side | Sandbox at launch (bubblewrap, Seatbelt, gVisor), unix-domain-socket egress proxy, seccomp or AppArmor, `--network none`, read-only mounts, dry-run defaults | PR.PS-01; PR.PS-05; PR.IR-01; PR.PS-06 | MANAGE 2.4 | LLM05; LLM10 | ASI05; ASI02 | EU AI Act Art. 15 | NIST SP 800-160 Vol. 1 (defense in depth); **Anthropic Auto Mode and Sandbox publications (March 2026)** |
| Server-side | Gated IaC apply pipeline, ResourceQuota, NetworkPolicy default-deny, prod and non-prod separation, immutable backups | PR.IR-01; PR.IR-02; PR.IR-03; PR.IR-04; PR.DS-11 | MANAGE 2.4; MANAGE 4.1 | LLM10; LLM05 | ASI05; ASI08 | EU AI Act Art. 15 | NIST SP 800-160 Vol. 1; NIST SP 800-34 Rev. 1; NISTIR 8596 |

## Approval gating row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | EU AI Act / ISO | Other |
|---|---|---|---|---|---|---|---|
| In-agent | Model self-pause ("are you sure?") | (advisory; no direct mapping) | MANAGE 4.1 | LLM06 | ASI09 (related risk) | EU AI Act Art. 14 | **Anthropic Auto Mode (March 2026): 93% approval rate is the empirical ceiling** |
| Client-side | PreToolUse pattern hooks, tiered confirmation, session limits, out-of-band channel for tier-3, judgment-query escalation | PR.AA-05; PR.PS-01 | MANAGE 4.1 | LLM06 | ASI02; ASI09 | EU AI Act Art. 14; **Singapore IMDA "meaningful human accountability" dimension** | OWASP Least Agency principle; assistance-games framing (Russell, 2019); AHRQ PSNet alarm-fatigue research |
| Server-side | Branch protection plus PR review (with admin bypass disabled), CODEOWNERS, multi-party prod approval, plan-and-apply separation, deployment freezes | PR.AA-05; PR.PS-01; **GV.RR-02** (roles, responsibilities, and authorities established, communicated, understood, and enforced); **GV.SC-04** (suppliers known and prioritized) | GOVERN 4.1; MANAGE 4.1 | LLM06 | ASI02; ASI03 | EU AI Act Art. 14, Art. 26; ISO/IEC 42001 §A.4 | NIST SP 800-160 Vol. 1 |

## Supply chain row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | EU AI Act / ISO | Other |
|---|---|---|---|---|---|---|---|
| In-agent | (no enforcement; advisory only) | (no mapping) | MAP 4.1 | LLM03 (related risk) | ASI04 (mitigation principle) |, |, |
| Client-side | MCP server allowlist with manifest hash pinning, **tool-description hashing**, Sigstore verification, lockfile pinning, pre-commit dependency scan, skill or extension allowlist | PR.PS-02; PR.PS-01; **GV.SC-07** (risks from suppliers, products, services, and other third parties identified, recorded, prioritized, assessed, responded to, monitored) | MAP 4.1; MANAGE 3.1 | LLM03; LLM04 | ASI04; ASI06 | EU AI Act Art. 15; ISO/IEC 42001 §A.10 | NIST SP 800-218 v1.1 PS.2; **NIST SP 800-218 Rev. 1 draft (Dec 17, 2025)**; NIST SP 800-218A; OWASP MCP01, MCP03, MCP04 |
| Server-side | OCI signature verification (cosign), SBOM admission, egress NetworkPolicy, OPA attestation policy, MCP domain allowlist at network layer, SLSA build-provenance attestation gates | PR.PS-02; PR.PS-05; PR.IR-01; **GV.SC-07**; ID.RA-09 (authenticity and integrity of hardware and software assessed prior to acquisition and use) | MAP 4.1; MANAGE 3.1 | LLM03; LLM04 | ASI04 | EU AI Act Art. 15; ISO/IEC 42001 §A.10 | NIST SP 800-218 v1.1 PS.3; NIST SP 800-161 Rev. 1; SLSA framework; **CISA/NSA/FBI "AI Data Security" CSI (May 2025)**; **CISA/ASD ACSC "Principles for Secure Integration of AI in OT" (Dec 2025)**; OWASP MCP04, MCP09 |

## US DoD / federal crosswalk

For program offices, ISSMs, ISSOs, and AOs. Same cells, expressed in 800-53 families, DoD Zero Trust pillars, and the RAI principles. **These are defensible crosswalks, not compliance claims**, your AO makes the determination.

### Five Eyes risk categories mapped to the five concerns

The joint guidance ("Careful Adoption of Agentic AI Services," April 30, 2026) names five risk categories. They map almost one-to-one onto this matrix's five concerns, which is the strongest external validation the framework has:

| Five Eyes risk category | This matrix's concern | Where it is enforced |
|---|---|---|
| Privilege escalation | Identity + Authorization | [`controls/identity/`](../controls/identity), [`controls/authorization/`](../controls/authorization) |
| Design and configuration flaws | Authorization | [`controls/authorization/server-side/`](../controls/authorization/server-side) |
| Behavioral misalignment | Blast radius + Approval gating | [`controls/blast-radius/`](../controls/blast-radius), [`controls/approval-gating/`](../controls/approval-gating) |
| Structural cascading failures | Blast radius | [`controls/blast-radius/server-side/`](../controls/blast-radius/server-side) |
| Accountability opacity | Charter + Inventory (+ Sentinels) | [`charter/`](../charter), [`inventory/`](../inventory), [`sentinels/`](../sentinels) |

The joint guidance's core posture, adopt incrementally starting with low-risk tasks; treat governance, human oversight, monitoring, and explicit accountability as requirements rather than options, is the same argument this framework makes with artifacts attached.

### Per-concern DoD control crosswalk

| Concern | NIST SP 800-53 Rev. 5 families | DoD Zero Trust pillar | RMF / cATO / CSRMC | DoD RAI |
|---|---|---|---|---|
| **Identity** | AC-2 (account management), IA-2, IA-5 (authenticator management), IA-8, IA-9 (service identification and authentication) | **User** (and Devices for NPE device identity) | RMF Implement/Assess; cATO ConMon | Traceable |
| **Authorization** | AC-3 (access enforcement), AC-6 (least privilege), AC-6(9) (log use of privileged functions), CM-7 (least functionality), AC-24 (access control decisions) | **User**, **Application & Workload** | RMF Select/Implement; CSRMC Critical Controls | Governable, Responsible |
| **Blast radius** | SC-7 (boundary protection), SC-39 (process isolation), SI-4 (system monitoring), CP-9/CP-10 (backup, recovery), SC-5 (denial-of-service protection) | **Network/Environment**, **Application & Workload**, **Data** | cATO ACD; CSRMC Cyber Survivability | Reliable, Governable |
| **Approval gating** | AC-3(2) (dual authorization), CM-3 (configuration change control), CM-5 (access restrictions for change), PM-10 (authorization process) | **Automation & Orchestration**, **User** | RMF Authorize; cATO ConMon | Governable, Responsible |
| **Supply chain** | **SR** family (SR-3, SR-4 provenance, SR-5, SR-11 component authenticity), SA-11, SA-12, CM-14 (signed components), SI-7 (software/firmware integrity) | **Application & Workload**, **Data** | cATO SSSC; CSRMC DevSecOps | Reliable, Traceable |

### How the matrices map to DoD constructs

| This framework | DoD equivalent it extends |
|---|---|
| Charter (Govern) | RMF Prepare/Categorize; the ATO package and AO risk acceptance; RAI governance |
| Inventory (Identify) | ICAM NPE registry; the PE-to-NPE control relationship; system boundary definition |
| Covenants (Protect) | ZT capability activities; 800-53 control implementation; STIG hardening |
| Sentinels (Detect) | cATO **Continuous Monitoring (ConMon)**; ZT **Visibility & Analytics** |
| Interventions (Respond) | cATO **Active Cyber Defense (ACD)**; ZT **Automation & Orchestration**; IR family |
| Restorations (Recover) | CP family (contingency planning); RMF Monitor feeding re-authorization |

### The gap this framework fills, in DoD terms

ICAM answers *who the agent is* and *what it may reach*. Zero Trust conditional access answers *whether this access request is permitted right now*. Neither answers **what an authenticated, authorized agent is permitted to do once it is inside**, an agent can hold a valid NPE credential, be correctly authorized for a data store, and still exfiltrate within scope, delegate beyond its intent, or take an irreversible action no one approved.

The DoD ZT reference architecture states the end state as all PEs and NPEs holding validated, verified digital identities tracked at the enterprise level. That is necessary and not sufficient for agents. Extending "never trust, always verify" from the **access layer** into the **action layer** is the open problem, and it is what the eighteen cells of the Covenants matrix enforce.

The precedent for the move already exists in DoD doctrine: RMF to cATO relocated assurance from a periodic review layer into the infrastructure, continuously. CSRMC then made that the framework-level default. Agentic Covenants applies the identical relocation to agent behavior.

## Citation legend and notes

Subcategory identifiers follow each framework's published format. NIST CSF 2.0 uses `Function.Category-Number` (PR.AA-01) with a hyphen, never a period. NIST AI RMF uses `FUNCTION Category.Number` (MANAGE 2.4). OWASP LLM uses `LLMnn:2025`. OWASP Agentic uses `ASInn`. OWASP MCP uses `MCPnn`. EU AI Act citations are by Article number from Regulation (EU) 2024/1689. ISO/IEC standards cite section number where relevant.

Cells marked "(advisory; no enforcement)" or "(no enforcement; advisory only)" in the in-agent column reflect the matrix's central thesis: in-agent controls are nudges, not enforceable controls. They do not have a counterpart in frameworks that catalogue technical safeguards because frameworks correctly treat in-model instructions as design hints, not security boundaries.

### Notes on framework subcategories that have changed

- **ID.SC-04** was withdrawn in CSF 2.0 final and supply-chain risk management moved to GV.SC. The current subcategory for supplier integrity assessment is **GV.SC-07**. Older documents citing ID.SC-04 should be updated.
- **GV.RR-04** in CSF 2.0 final reads "Cybersecurity is included in human resources practices," which is unrelated to agent governance. The closest applicable governance subcategory for agent-action authorization is **GV.RR-02** (roles, responsibilities, and authorities established, communicated, understood, and enforced).
- **NIST AI 100-2 E2025** (March 24, 2025) supersedes the 2023 edition. The 2025 edition extends taxonomy to autonomous AI agents.
- **NIST SP 800-63 Revision 4** (July 2025) is the current final version. All four volumes are final.
- **EO 14110** (October 30, 2023) was rescinded January 23, 2025. The current operative executive document driving NIST AI work is the AI Action Plan (July 2025), under which CAISI replaced the AI Safety Institute and the AI Agent Standards Initiative was launched February 17, 2026.

This file is intentionally conservative. Where a control could be mapped to a category at a high level but the linkage is indirect, the citation is omitted rather than overstretched. A reviewer who finds an additional mapping is welcome to contribute it; a reviewer who finds an incorrect mapping is welcome to flag it. Both improve the document.

The framing for talks and the lead-magnet PDF: OWASP catalogs the threats. NIST governs and structures controls. CSA MAESTRO models the attack surface. ISO/IEC 42001 gives the management system. The EU AI Act sets the regulatory floor. None of them tells a platform engineer which Kyverno policy to write on Monday morning. The Agentic Covenants Matrix does, with [`BYPASSES.md`](./BYPASSES.md) naming the limits of every recommendation and this file grounding every recommendation in an authoritative source.
