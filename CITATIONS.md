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
- **CISA / Australian Signals Directorate ACSC, "Principles for the Secure Integration of AI in Operational Technology"** (December 3, 2025).
- **CISA, "Deploying AI Systems Securely"** (joint guidance, April 2024).
- **EO 14179 and the AI Action Plan** (January and July 2025). EO 14110 (October 30, 2023) was **rescinded January 23, 2025**; the operative executive document is now the AI Action Plan, which drives ongoing NIST work.

### International and standards-body frameworks

- **ISO/IEC 42001:2023** (AI Management System, December 2023). The only certifiable AI management system standard.
- **ISO/IEC 23894:2023** (AI Risk Management Guidance, February 2023).
- **EU AI Act, Regulation (EU) 2024/1689** (entered force August 1, 2024). Phased applicability: prohibitions and AI literacy from February 2, 2025; GPAI obligations from August 2, 2025; high-risk AI obligations from August 2, 2026. Articles directly relevant: **Article 9** (risk management system), **Article 13** (transparency), **Article 14** (human oversight), **Article 15** (accuracy, robustness, cybersecurity), **Articles 26–29** (deployer obligations).
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
- **Stuart Russell, "Human Compatible"** (2019). Assistance games — conceptual ancestor to the judgment-query escalation pattern.
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
| In-agent | (no enforcement; advisory only) | (no mapping) | MAP 5.1; MEASURE 2.6, 2.7 | LLM06 | ASI02; ASI05 | — | — |
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
| In-agent | (no enforcement; advisory only) | (no mapping) | MAP 4.1 | LLM03 (related risk) | ASI04 (mitigation principle) | — | — |
| Client-side | MCP server allowlist with manifest hash pinning, **tool-description hashing**, Sigstore verification, lockfile pinning, pre-commit dependency scan, skill or extension allowlist | PR.PS-02; PR.PS-01; **GV.SC-07** (risks from suppliers, products, services, and other third parties identified, recorded, prioritized, assessed, responded to, monitored) | MAP 4.1; MANAGE 3.1 | LLM03; LLM04 | ASI04; ASI06 | EU AI Act Art. 15; ISO/IEC 42001 §A.10 | NIST SP 800-218 v1.1 PS.2; **NIST SP 800-218 Rev. 1 draft (Dec 17, 2025)**; NIST SP 800-218A; OWASP MCP01, MCP03, MCP04 |
| Server-side | OCI signature verification (cosign), SBOM admission, egress NetworkPolicy, OPA attestation policy, MCP domain allowlist at network layer, SLSA build-provenance attestation gates | PR.PS-02; PR.PS-05; PR.IR-01; **GV.SC-07**; ID.RA-09 (authenticity and integrity of hardware and software assessed prior to acquisition and use) | MAP 4.1; MANAGE 3.1 | LLM03; LLM04 | ASI04 | EU AI Act Art. 15; ISO/IEC 42001 §A.10 | NIST SP 800-218 v1.1 PS.3; NIST SP 800-161 Rev. 1; SLSA framework; **CISA/NSA/FBI "AI Data Security" CSI (May 2025)**; **CISA/ASD ACSC "Principles for Secure Integration of AI in OT" (Dec 2025)**; OWASP MCP04, MCP09 |

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
