# Citations

Cell-level mapping. Each control or control cluster cites the most directly applicable framework subcategory. Where multiple subcategories apply, the primary one is listed first.

This file is the line of defense against "you just made this up" reviewer attacks.

## Frameworks referenced

- **NIST Cybersecurity Framework 2.0** (NIST CSWP 29, February 2024). Six functions: Govern, Identify, Protect, Detect, Respond, Recover. The Agentic Covenants Matrix is **Protect** for agents. Protect categories: PR.AA (Identity Management, Authentication, Access Control), PR.AT (Awareness and Training), PR.DS (Data Security), PR.PS (Platform Security), PR.IR (Technology Infrastructure Resilience).
- **NIST AI Risk Management Framework 1.0** (NIST AI 100-1, January 2023). Four functions: Govern, Map, Measure, Manage.
- **NIST AI Generative AI Profile** (NIST AI 600-1, July 2024). Cross-sectoral profile applying AI RMF 1.0 to generative AI.
- **OWASP Top 10 for LLM Applications 2025** (released November 2024). LLM01 Prompt Injection through LLM10 Unbounded Consumption.
- **OWASP Top 10 for Agentic Applications 2026** (released December 2025). ASI01 through ASI10. Foregrounds two design principles: **Least Agency** and **Strong Observability**.
- **NIST SP 800-207** (Zero Trust Architecture, August 2020).
- **NIST SP 800-218** (Secure Software Development Framework, February 2022) **and SP 800-218A** (Generative AI Profile of SSDF, April 2024).
- **NIST SP 800-160 Vol. 1** (Engineering Trustworthy Secure Systems, November 2022). Defense-in-depth conceptual basis.
- **NIST SP 800-161 Rev. 1** (Cybersecurity Supply Chain Risk Management Practices, May 2022).
- **CSA MAESTRO** (2025). Seven-layer threat model for agentic AI.
- **MITRE ATLAS**. Adversarial attack catalog for ML/AI systems.
- **CIS Kubernetes Benchmark** (current version).
- **SLSA Framework** (Supply-chain Levels for Software Artifacts).

Lab capability frameworks (Anthropic Responsible Scaling Policy, OpenAI Preparedness Framework, Google DeepMind Frontier Safety Framework) govern what models are released. This matrix governs what released models are allowed to do inside your perimeter.

Diagnostic for whether full matrix coverage is mandatory: **Simon Willison's Lethal Trifecta** — private data + untrusted content + external communication. If any agent has all three, every cell needs to be populated.

## Identity row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | Other |
|---|---|---|---|---|---|---|
| In-agent | System prompt declares agent identity | (advisory; no direct mapping) | GOVERN 1.5 (ongoing monitoring); MAP 4.1 (third-party risks) | LLM07 (System Prompt Leakage), related risk | ASI03 (Identity & Privilege Abuse), mitigation principle | — |
| Client-side | Per-agent credentials, no shared keys, filesystem ACLs | PR.AA-01 (identities and credentials managed); PR.AA-03 (users, services, hardware authenticated) | MANAGE 2.4 (resources allocated to risk treatment) | LLM02 (Sensitive Information Disclosure) | ASI03 (Identity & Privilege Abuse) | NIST SP 800-207 (Zero Trust); NIST SP 800-63 (Digital Identity) |
| Server-side | Dedicated ServiceAccount, OIDC federation, short-TTL bound tokens | PR.AA-01; PR.AA-02 (identities proofed and bound to credentials); PR.AA-03; PR.AA-04 (identity assertions protected, conveyed, verified) | MANAGE 4.1 (post-deployment monitoring, override mechanisms) | LLM02; LLM06 (Excessive Agency) | ASI03; ASI10 (Rogue Agents) | NIST SP 800-207 §3.4.1 (per-session authentication); NIST SP 800-63B (authenticator assurance) |

## Authorization row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | Other |
|---|---|---|---|---|---|---|
| In-agent | Model instructions, scoped tool descriptions | (advisory; no direct mapping) | MAP 5.1 (likelihood and magnitude of impacts documented) | LLM06 (Excessive Agency), mitigation principle | ASI02 (Tool Misuse), mitigation principle | — |
| Client-side | `--allowedTools` deny-by-default, capability-based tool restriction, PreToolUse hooks, operator-owned hook config | PR.AA-05 (least privilege, separation of duties); PR.PS-01 (configuration management practices) | MANAGE 2.4; MANAGE 4.1 | LLM06 (Excessive Agency); LLM05 (Improper Output Handling) | ASI02 (Tool Misuse); ASI05 (Unexpected Code Execution) | OWASP Agentic Least Agency principle; NIST SP 800-207 §2.1 (least privilege) |
| Server-side | Scoped RBAC Roles, IAM with explicit ARN, Kyverno or OPA admission, namespace scoping | PR.AA-05; PR.PS-01; PR.PS-05 (installation and execution of unauthorized software prevented) | MANAGE 2.4; MANAGE 4.1 | LLM06; LLM05 | ASI02; ASI03; ASI05 | NIST SP 800-207 (Zero Trust); CIS Kubernetes Benchmark |

## Blast radius row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | Other |
|---|---|---|---|---|---|---|
| In-agent | Model declines destructive ops | (advisory; no direct mapping) | MAP 5.1; MEASURE 2.6 (safety risks evaluated) | LLM06 (Excessive Agency) | ASI02; ASI05 | — |
| Client-side | Sandbox at launch, seccomp or AppArmor, `--network none`, read-only mounts, dry-run defaults | PR.PS-01 (configuration management); PR.PS-05; PR.IR-01 (networks protected from unauthorized access); PR.PS-06 (secure software development practices) | MANAGE 2.4 | LLM05 (Improper Output Handling); LLM10 (Unbounded Consumption) | ASI05 (Unexpected Code Execution); ASI02 | NIST SP 800-160 Vol. 1 (defense in depth) |
| Server-side | Gated IaC apply pipeline, ResourceQuota, NetworkPolicy default-deny, prod and non-prod separation, immutable backups | PR.IR-01; PR.IR-02 (technology assets protected from environmental threats); PR.IR-03 (mechanisms achieving resilience requirements); PR.IR-04 (adequate resource capacity); PR.DS-11 (backups created, protected, maintained, tested) | MANAGE 2.4; MANAGE 4.1 | LLM10 (Unbounded Consumption); LLM05 | ASI05; ASI08 (Cascading Failures) | NIST SP 800-160 Vol. 1; NIST SP 800-34 (contingency planning) |

## Approval gating row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | Other |
|---|---|---|---|---|---|---|
| In-agent | Model asks "are you sure?" | (advisory; no direct mapping) | MANAGE 4.1 (override mechanisms) | LLM06 (Excessive Agency) | ASI09 (Human-Agent Trust Exploitation), related risk | — |
| Client-side | PreToolUse pattern hooks, tiered confirmation, session limits, out-of-band channel for tier-3, judgment-query escalation | PR.AA-05 (separation of duties); PR.PS-01 | MANAGE 4.1 (post-deployment monitoring, appeal and override mechanisms) | LLM06 (Excessive Agency) | ASI02; ASI09 | OWASP Agentic Least Agency principle; assistance-games framing (Russell, 2019) |
| Server-side | Branch protection plus PR review, CODEOWNERS, multi-party prod approval, plan-and-apply separation, deployment freezes | PR.AA-05 (least privilege, separation of duties); PR.PS-01; GV.RR-04 (responsibilities for cybersecurity, privacy) | GOVERN 4.1 (organizational practices supporting AI risk management); MANAGE 4.1 | LLM06 | ASI02; ASI03 | NIST SP 800-160 Vol. 1 (separation of duties as a security principle) |

## Supply chain row

| Layer | Control | NIST CSF 2.0 | NIST AI RMF | OWASP LLM | OWASP Agentic | Other |
|---|---|---|---|---|---|---|
| In-agent | Model warns about unvetted packages | (advisory; no direct mapping) | MAP 4.1 (third-party risks identified) | LLM03 (Supply Chain), related risk | ASI04 (Agentic Supply Chain Vulnerabilities), mitigation principle | — |
| Client-side | MCP server allowlist with hash pinning, Sigstore verification, lockfile pinning, pre-commit dependency scan | PR.PS-02 (software maintained, replaced, removed commensurate with risk); PR.PS-01 (configuration management); ID.SC-04 (supplier integrity verified) | MAP 4.1; MANAGE 3.1 (third-party risk treatment) | LLM03 (Supply Chain); LLM04 (Data and Model Poisoning) | ASI04 (Agentic Supply Chain); ASI06 (Memory & Context Poisoning) | NIST SP 800-218 SSDF PS.2 (provide a mechanism for verifying software integrity); NIST SP 800-218A (Generative AI Profile) |
| Server-side | OCI signature verification (cosign), SBOM admission, egress NetworkPolicy, OPA attestation policy, MCP domain allowlist at network layer | PR.PS-02; PR.PS-05 (unauthorized software prevented); PR.IR-01; ID.SC-04 (supplier integrity); ID.RA-09 (vulnerability disclosure processes) | MAP 4.1; MANAGE 3.1 | LLM03; LLM04 | ASI04 | NIST SP 800-218 PS.3 (archive and protect each software release); NIST SP 800-161 (supply chain risk management); SLSA framework (build provenance) |

## Citation legend and notes

Subcategory identifiers follow each framework's published format:

- **NIST CSF 2.0**: `Function.Category-Number` (PR.AA-01).
- **NIST AI RMF**: `FUNCTION Category.Number` (MANAGE 2.4).
- **OWASP LLM**: `LLMnn:2025`.
- **OWASP Agentic**: `ASInn`.

Cells marked "(advisory; no direct mapping)" reflect that in-agent controls are nudges rather than enforceable controls and consequently do not have a counterpart in frameworks that catalogue technical safeguards.

The OWASP Agentic Top 10 identifiers are from the December 2025 release (OWASP Top 10 for Agentic Applications 2026). The OWASP LLM Top 10 identifiers are from the November 2024 release (2025 edition).

This file is intentionally conservative. Where a control could be mapped to a category at a high level but the linkage is indirect, the citation is omitted rather than overstretched. A reviewer who finds an additional mapping is welcome to contribute it; a reviewer who finds an incorrect mapping is welcome to flag it. Both improve the document.
