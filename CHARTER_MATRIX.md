# The Agentic Charter Matrix

A governance framework for autonomous agent authorization. Three layers of authority, five concerns, fifteen cells. The upstream strategic companion to the four operational matrices ([Covenants](./MATRIX.md), [Sentinels](./SENTINELS_MATRIX.md), [Interventions](./INTERVENTIONS_MATRIX.md), [Restorations](./RESTORATIONS_MATRIX.md)). Maps to NIST CSF 2.0 **Govern (GV)** function, NIST AI RMF **GOVERN** function, ISO/IEC 42001, and EU AI Act Article 9.

## What this is

Charter is the matrix that exists *before* any agent runs. The four operational matrices answer questions about a running agent. Charter answers a different question: **who is allowed to put an agent into the world in the first place, under what authority, accountable to what policy, with what retirement criteria?** Without Charter, every other matrix is reactive. The agent already exists; you are figuring out how to govern it after the fact.

A complete Charter for an agent is a *document* (markdown, YAML, JSON, or whatever your governance tooling speaks) that records: who owns this agent, what risk tier it falls under, what scope its authorization grants, what dependencies and models it is allowed to use, who approved its creation, when it must be reviewed, and under what conditions it must be retired. **The Charter is signed by the parties whose authority creates and binds the agent.**

## Why governance is not optional and not separate

Two failure modes when Charter is absent:

1. **Agents proliferate without ownership.** Six months in, you have forty agents in production, half built by people who have left the company, no one is sure which dependency tree any given agent uses, and a security incident requires identifying who can speak for an agent before you can stop it. ClawHavoc-style supply-chain incidents become unrecoverable because no one knows the ownership chain.

2. **Risk tiering is implicit.** Without an explicit charter, every agent is treated the same. The customer-facing summarization agent and the production-database-modifying agent get the same controls, which means one is over-controlled (slow to ship) and the other is under-controlled (catastrophic). Tiering is what allows Covenants and Sentinels to pick proportional controls per agent.

Governance is also the function that absorbs regulatory load. EU AI Act Articles 9 (risk management system), 17 (quality management system), and 26–29 (deployer obligations) all require organizational structures that map to Charter cells, not to operational matrix cells. **A platform-engineering posture without Charter cannot pass an EU AI Act conformity assessment.**

## The two axes

### Vertical: where authority lives

1. **Organizational charter.** Top-of-house policy. AI Acceptable Use Policy, AI Risk Appetite Statement, regulatory commitments, training requirements, incident-disclosure standards. Applies to every agent the org operates. Owned by board, executive, or AI Governance Council.
2. **Domain charter.** Per-domain or per-agent-class governance. DevOps agents, customer-facing agents, internal automation, research agents. Different risk profiles get different baseline controls. Owned by domain leadership (Platform Engineering Director, Security Director, etc.).
3. **Agent charter.** The specific authorization document for a single agent. Names the agent, names the owner, declares risk tier, defines allowed scope, lists dependencies, records approval signatures, specifies review cadence and retirement criteria. Owned by the agent's named operator, signed by domain authority.

### Horizontal: what is being governed

1. **Identity.** Who can authorize creation? Who is the named human owner accountable for this agent's actions?
2. **Authorization.** What scope does the charter grant? Under what change-control process can scope be expanded?
3. **Blast radius.** What risk tier? What damage cap is acceptable? Under what conditions does the charter permit production access?
4. **Approval gating.** Who must approve the charter itself? Who approves changes to it? Who approves retirement?
5. **Supply chain.** What models, MCP servers, dependencies, base images is the charter allowed to use? Under what change-control?

## The matrix

| Concern | Organizational charter | Domain charter | Agent charter |
|---|---|---|---|
| **Identity** | AI Acceptable Use Policy names categories of agents allowed to exist. AI Governance Council holds authority to create new agent classes. Director of AI Workforce Transformation (or equivalent) is the named org-wide owner of the agent program. Audit trail of charter signatures retained per ISO/IEC 42001 §A.4. | Domain leadership (Platform Engineering Director, Security Director) signs domain charter that authorizes a class of agents (e.g., "DevOps automation agents"). Domain charter names the human roles permitted to create agents in this class and names the escalation path. | Specific agent has a named human owner, listed by name and role, accountable for the agent's actions. Named owner signs the charter. Backup owner identified. Identity claims the agent makes at runtime are tied back to the charter via a registered agent identifier (NIST NCCoE Concept Paper Feb 5, 2026 framing). |
| **Authorization** | Org-wide AI Risk Appetite Statement defines what classes of operations any agent is allowed to be authorized for. Defines hard prohibitions (e.g., "no agent ever has direct customer-PII write access without dual-control"). Defines change-control process for evolving scope policy. | Domain charter defines the per-class scope: which APIs, which data classes, which environments (dev/staging/prod), which destructive verbs. Domain charter inherits org-wide hard prohibitions and adds domain-specific ones. | Agent charter declares its specific authorized scope: named tools, named MCP servers, named environments, named max-blast-radius operations. **Scope expansion requires re-signature.** Scope is the contract that Covenants L3-C2 and L3-C5 enforce in production. |
| **Blast radius** | Org-wide risk tier taxonomy (Tier 1 = read-only, Tier 2 = scoped writes, Tier 3 = destructive ops, Tier 4 = production-critical). Org-wide damage caps and the matching control requirements per tier. | Domain charter inherits the org tier taxonomy and defines which tiers the domain is authorized to operate. (Customer-facing domain may forbid Tier 3+ entirely. DevOps domain may permit Tier 4 with extra controls.) Domain defines failure-mode reviews required per tier. | Agent charter declares the specific risk tier this agent operates at, the specific damage cap (e.g., "may modify up to N records per session, may not delete production resources, may not exceed M USD in cloud spend per day"), and the conditions that trigger automatic tier downgrade or retirement. |
| **Approval gating** | Org-wide AI Governance Council is the authority that approves new agent classes, ratifies risk-tier policy changes, and reviews annual agent-program report. Member roles named (CISO, Chief AI Officer, GC, Privacy, Domain Leads). Quorum and voting rules defined per ISO/IEC 42001 §A.4. | Domain authority approves agent charters within its domain. Multi-party signature required for Tier 3+ agents (typically domain lead plus security review plus risk review). Approval process documented and auditable. Charter amendments require the same process as original approval. | Agent charter signed by named owner, domain authority, and (for Tier 3+) security review. Charter identifies the approver of every subsequent scope change. Annual review cadence specified. Conditions for emergency revocation specified. **The charter is the artifact that Covenants L3-C4 protects** (branch protection prevents tampering with the charter file itself). |
| **Supply chain** | Org-wide allowlist of approved foundation models. Org-wide policy on MCP server approval, third-party dependency approval, vendor risk assessment. Procurement process integrates AI vendor risk per NIST SP 800-161 Rev. 1 and NIST SP 800-218A. | Domain charter inherits org-wide approved-model list and adds domain-specific restrictions (e.g., "this domain may not use models that train on user data" or "this domain may only use SOC 2 Type II vendors"). Domain charter approves or denies MCP servers for the domain. | Agent charter declares specific dependencies: named foundation model and version, named MCP servers (with allowlist hashes referenced from L2-C5 of Covenants), named base container images, named tool versions. Dependency changes require charter amendment. Per OWASP MCP Top 10 (MCP04, MCP09), supply chain inventory is a charter property, not a runtime property. |

## How to use this as governance

The Charter Matrix is not a runbook; it is a **documentation discipline**. Each cell answers a structural question that the org's governance documents must answer. Walk the cells and ask: *does our org actually have this written down somewhere, with named owners, signed and dated?* If the answer is "we know this but it is not written," the cell is empty.

Three test outcomes:

- **All three cells populated and current:** the agent is governed. There is an audit trail. There is a named human accountable for every concern. Regulatory reviewers (EU AI Act, ISO/IEC 42001 auditors) can find what they need.
- **Only org-wide cell populated:** the org has a policy but it is not operationalized per domain or per agent. Every agent inherits the same generic controls. Tiering is not happening.
- **Only agent-charter cell populated:** the agent is documented but the org has no policy framework. The charter exists in a vacuum and any change to the org's risk appetite cannot be propagated systematically.

## Charter is the contract for the operational matrices

The Charter constraints are what Covenants enforces, what Sentinels watches for, what Interventions stops on, and what Restorations rebuilds toward. Specifically:

- The agent's authorized scope (Charter Authorization row) is the input to [Covenants L3-C2](./controls/authorization/server-side/) (server-side authorization). The agent's RBAC Role is the technical implementation of the charter scope.
- The agent's risk tier (Charter Blast Radius row) determines which Covenants cells must be populated for that agent. A Tier 1 read-only agent does not need every cell. A Tier 4 production agent needs all of them.
- The agent's named owner (Charter Identity row) is the human paged when Sentinels alerts and the human authorized to sign Interventions runbooks.
- The agent's dependency manifest (Charter Supply Chain row) is the input to [Covenants L2-C5](./controls/supply-chain/client-side/) and [L3-C5](./controls/supply-chain/server-side/) allowlists.
- The charter's review cadence (Charter Approval Gating row) drives the periodic re-attestation that Sentinels reports against (drift detection).

**If the Charter is missing for an agent, the operational matrices have no anchor.** Covenants enforces a scope you have not defined. Sentinels alerts on a baseline you have not declared. Interventions pages a human you have not named. Restorations rebuilds toward a state you have not committed to.

## Templates

- [`charter/templates/agent-charter.yaml`](./charter/templates/agent-charter.yaml), operational template for a single agent's charter. Version-controlled, under branch protection, PR-reviewed.
- [`charter/templates/domain-charter.md`](./charter/templates/domain-charter.md), markdown template for a domain governance document.
- [`charter/templates/organizational-policy.md`](./charter/templates/organizational-policy.md), markdown template for org-wide AI policy and risk appetite.

## Where this matrix sits

Charter is the first of two upstream strategic matrices. Inventory (Identify) is the other. Together they wrap the four operational matrices:

- **Charter (Govern, NIST CSF 2.0 GV): the rules that authorize agents to exist ← this document**
- Inventory (Identify, NIST CSF 2.0 ID): the registry of agents that do exist
- Covenants (Protect, NIST CSF 2.0 PR): what binds the running agent
- Sentinels (Detect, NIST CSF 2.0 DE): what watches the running agent
- Interventions (Respond, NIST CSF 2.0 RS): what stops the running agent
- Restorations (Recover, NIST CSF 2.0 RC): what fixes after the agent

Charter feeds Inventory (every chartered agent should be in inventory). Inventory feeds the operational matrices (Covenants protects what Inventory has identified, etc.). The flow is: **Charter authorizes → Inventory registers → operational matrices govern at runtime → Restorations feeds back into Charter when retirement criteria fire or when post-incident review changes the charter.**

## Reading order

1. This document: the framework essay.
2. [`docs/walkthrough-agentic-charter-matrix-v5.md`](./docs/walkthrough-agentic-charter-matrix-v5.md), companion walkthrough (gitignored).
3. [`charter/templates/`](./charter/templates/), copy and fill in for your environment.
4. [`charter/`](./charter/), per-cell governance guidance.

## Citations

NIST CSF 2.0 GV.OC-*, GV.PO-*, GV.RM-*, GV.RR-*, GV.OV-*, GV.SC-*. NIST AI RMF GOVERN 1.1–1.7, GOVERN 2.1–2.2, GOVERN 4.1, GOVERN 5.1, GOVERN 6.1–6.2. ISO/IEC 42001:2023 §A.2–A.10. EU AI Act Articles 9, 17, 25, 26. NIST SP 800-161 Rev. 1. NIST SP 800-218A. Singapore IMDA Model AI Governance Framework for Agentic AI (Jan 22, 2026). NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026).
