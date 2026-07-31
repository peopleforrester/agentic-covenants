# Organizational AI Policy Template

**Org Name.** [Company / Organization]
**Effective Date.** [YYYY-MM-DD]
**Next Review.** [YYYY-MM-DD] (annual minimum)
**Policy Version.** [X.Y]
**Approving Body.** AI Governance Council

---

## 1. Purpose and scope

This policy governs every autonomous AI agent operated by [Org Name], regardless of department, vendor, or use case. It satisfies our obligations under EU AI Act Article 9, ISO/IEC 42001, and NIST AI RMF GOVERN.

## 2. AI Acceptable Use Policy

### 2.1 Agents permitted to exist

Agents are permitted only when authorized by an Agent Charter that inherits from a Domain Charter that inherits from this policy.

### 2.2 Agents not permitted

Hard prohibitions. No agent may, under any circumstance:

- Process customer Personally Identifiable Information without dual-control supervision.
- Issue financial transactions exceeding [USD threshold] without explicit per-transaction human approval.
- Modify production database schema or content without out-of-band confirmation.
- Modify branch protection, CI/CD configuration, or this policy itself.
- Use a foundation model not on the approved-models list (see §6).
- Use an MCP server not on a domain-approved allowlist.

### 2.3 Agents requiring elevated approval

[List specific use classes that require Council-level approval before a domain or agent charter is granted.]

## 3. AI Risk Appetite Statement

[Org Name] accepts the following risk appetite for autonomous agents:

| Tier | Description | Damage cap | Required controls |
|---|---|---|---|
| 1 | Read-only diagnostics | None (read does not cause damage) | Charter + Identity + Authorization (read-only) |
| 2 | Scoped writes | [N records / session, $X / day] | Tier 1 + Approval gating + Blast radius |
| 3 | Destructive operations | [Scope-limited] | Tier 2 + Sentinels + Interventions runbooks |
| 4 | Production-critical | [Per-agent declared] | Tier 3 + multi-party approval, off-cluster identity, immutable backups |

### 3.1 Risks not accepted

[List of risk classes that no charter may grant. Examples: customer-data exfiltration, unbounded cloud spend, autonomous code deployment to customer-facing prod without human approval.]

## 4. Roles and authorities

### 4.1 AI Governance Council

**Members:**

- Chief Information Security Officer (chair)
- Chief AI Officer
- General Counsel
- Privacy Officer
- Domain Leads (Platform Engineering, Customer Engineering, Research, [others])

**Quorum:** [N of M members]
**Decision rule:** [e.g. unanimous for Tier 3+, majority for Tier 1-2]
**Cadence:** [Monthly working session, quarterly review]
**Minutes:** Recorded and retained per ISO/IEC 42001 §A.4.

### 4.2 Director of AI Workforce Transformation (or equivalent)

Named org-wide owner of the agent program. [Name, role, contact]

### 4.3 Domain leads

[Named per-domain authorities. Each authorized to sign domain charters.]

## 5. Approval and review processes

### 5.1 New agent class

Council-level approval. Vote recorded in minutes.

### 5.2 New agent within an existing class

Domain-level approval per domain charter.

### 5.3 Charter amendment

Same process as original approval. PR review with signed approvals.

### 5.4 Annual program review

Council reviews:
- Number of agents per tier
- Sentinels alert volume per agent
- Interventions invocations
- Charter amendments per agent
- Retirement criteria fired
- Pending audit findings

## 6. Approved foundation models

| Model | Vendor | Approved version range | Approved by | Approved date | Next review |
|---|---|---|---|---|---|
| claude-opus-4-8 | Anthropic | latest | Council | YYYY-MM-DD | YYYY-MM-DD |
| claude-sonnet-4-6 | Anthropic | latest | Council | YYYY-MM-DD | YYYY-MM-DD |

## 7. Vendor risk assessment

Per NIST SP 800-161 Rev. 1, NIST SP 800-218A. Procurement integrates AI vendor risk:

- SOC 2 Type II required for all production agents.
- Data-handling clause required (vendor may not train on customer data).
- Incident-disclosure clause required.
- Subprocessor list required and reviewed annually.

## 8. Training and awareness

[Per ISO/IEC 42001 §A.7: training requirements for personnel involved in AI lifecycle.]

## 9. Incident-disclosure standard

[How and when the org discloses agent-caused incidents internally and externally. Mapped to EU AI Act Art. 73 serious-incident reporting where applicable.]

## 10. Retirement of this policy

This policy is reviewed annually. Material changes require Council vote with full minute record.

---

## Approval signatures

- **AI Governance Council Chair (CISO):** [Name, date, signature]
- **Chief AI Officer:** [Name, date, signature]
- **General Counsel:** [Name, date, signature]
- **Board acknowledgement:** [Name, date]
