# Domain Charter Template — [Domain Name]

**Domain.** [e.g. Platform Engineering / DevOps Automation]

**Domain Authority.** [Named role, e.g. "Director of Platform Engineering"]

**Effective Date.** [YYYY-MM-DD]
**Next Review.** [YYYY-MM-DD] (annual)
**Charter Version.** [n.m]

---

## 1. Scope of this domain

What classes of agents this domain authorizes. What classes it does not.

> Example: This charter authorizes agents that perform **read-only Kubernetes diagnostics, scoped IAM read operations, and CI/CD orchestration**. It does not authorize agents that touch customer-facing services, customer data, or production databases.

## 2. Inheritance from organizational policy

This charter inherits all hard prohibitions, risk-tier taxonomy, and approved-model lists from `charter-organizational-ai-policy.md` version `[X.Y]` dated `[YYYY-MM-DD]`. Domain-specific additions are listed below.

## 3. Authorized risk tiers

This domain is authorized to operate agents at:

- ☐ Tier 1 (read-only)
- ☐ Tier 2 (scoped writes)
- ☐ Tier 3 (destructive ops; multi-party approval required per agent)
- ☐ Tier 4 (production-critical; security review and risk review required per agent)

## 4. Identity

**Roles authorized to create agents in this domain:** [e.g. Platform Engineering Director, Senior Platform Engineer]

**Escalation path for security questions:** [Named role, contact]

**Audit trail location:** [Repo path or document ref where charter signatures are stored]

## 5. Authorization

**Domain-specific scope additions:**

- [e.g. "No agent in this domain may interact with customer PII"]
- [e.g. "All Tier 3 agents must use the gated IaC pipeline"]

**Change-control process for scope expansion:** [Reference to PR review process]

## 6. Blast radius

**Failure-mode review required per tier:**

| Tier | Required review |
|---|---|
| 1 | Owner self-review, annual |
| 2 | Domain lead review, semi-annual |
| 3 | Security + risk review, quarterly |
| 4 | Security + risk + GC review, quarterly + after every incident |

## 7. Approval gating

**Approvers for new agent charters in this domain:**

- Tier 1: Domain lead alone
- Tier 2: Domain lead + named senior engineer
- Tier 3: Domain lead + security review + risk review
- Tier 4: Domain lead + security review + risk review + named executive

**Charter amendment process:** Same as original approval; amendments via PR with signed reviews.

## 8. Supply chain

**Domain-specific model restrictions:**

- [e.g. "May only use models with SOC 2 Type II attestation"]
- [e.g. "May not use models that train on user data"]

**Approved MCP servers for this domain:**

| Server | Approved version | Hash | Approved by | Approved date |
|---|---|---|---|---|
| filesystem | x.y.z | sha256:... | [Name] | YYYY-MM-DD |
| github | x.y.z | sha256:... | [Name] | YYYY-MM-DD |

**Approved foundation models for this domain:**

| Model | Version | Approved by | Approved date |
|---|---|---|---|
| claude-opus-4-7 | latest | [Name] | YYYY-MM-DD |

## 9. Retirement criteria for the domain itself

This domain charter retires when: [conditions]

---

## Approval signatures

- **Domain Authority:** [Name, role, date, signature]
- **Security Review:** [Name, role, date, signature]
- **Risk Review:** [Name, role, date, signature]
