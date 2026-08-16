# The Agentic Inventory Matrix

An identification framework for autonomous-agent discovery, registration, and threat modeling. Three layers of discovery, five concerns, fifteen cells. The second upstream strategic matrix in the Agentic Matrix family. Maps to NIST CSF 2.0 **Identify (ID)** function, NIST AI RMF **MAP** function, and CSA MAESTRO Layer 7 (Agent Ecosystem).

## What this is

Inventory is the matrix that answers *what agents exist, what they touch, what threats they face.* [Charter](./CHARTER_MATRIX.md) authorizes agents to exist. Inventory tracks the agents that actually do. **Without Inventory, every other matrix has unclear scope:** Covenants protects an undefined population, Sentinels alerts on an undefined baseline, and post-incident response has to start by figuring out which agent did what.

The matrix recognizes a hard truth about real environments: not every agent shows up where you expect. Some agents declare themselves. Some are catalogued by an operator who took the time. Some are running in the corner of an account or cluster that no one knew about. **A defensible Inventory accounts for all three.**

## Why discovery matters

Three failure modes when Inventory is absent or incomplete:

1. **Shadow agents.** A team prototyped a Claude Code workflow, it shipped to production by accident, and now there is an unowned agent running with credentials that no central registry tracks. The 90-day corpus includes multiple incidents (Cline 2.3.0, postmark-mcp, ClawHavoc skill ecosystem) where shadow agents and shadow MCP servers were the breach vector. **The fix is not policy. The fix is discovery tooling.**

2. **Stale inventory.** A spreadsheet existed at one point. It has not been updated in nine months. Half the agents in it are retired; new agents are not in it. **The inventory is worse than no inventory because it gives false confidence.**

3. **Inventory without threat exposure.** The registry knows the agent exists but not what it depends on, what attack surface it presents, or what the worst case looks like. Cannot drive Charter risk-tiering. Cannot drive Covenants control selection. The data is there but useless.

## The two axes

### Vertical: where the inventory comes from

1. **Self-declared.** Agent registers itself with a central registry on startup. Sends heartbeats. Reports its identity, owner, charter reference, dependency manifest, and current state. Strong signal when present, but missing entirely for agents that do not implement the registration protocol or that are deliberately hidden.
2. **Operator-declared.** Human-maintained inventory: spreadsheet, internal portal, ServiceNow CMDB, GitOps repo. The operator commits to keeping it current. Strong source of intent and ownership, weak source of liveness. Almost always drifts from reality.
3. **Discovered.** Passive discovery from cloud audit logs, Kubernetes API watches, network telemetry, and behavioral analysis. Finds agents that did not declare themselves and were not catalogued. **The truth source for "what is actually running," weakest source for "what was supposed to be running."**

The three layers are complementary and partially overlapping. A complete Inventory cross-references all three: an agent that self-declares should also appear in operator-declared (intent) and discovered (liveness). **Mismatches across layers are themselves Sentinels-level alerts.**

### Horizontal: what is being inventoried

1. **Identity.** Which agents exist, with what credentials, mapped to which charter, owned by which named human.
2. **Authorization.** What scope each agent has, what RBAC roles or IAM principals it uses, what could it touch.
3. **Blast radius.** What is the worst-case damage if this agent is compromised. What environments. What data classes. What revenue or customer impact.
4. **Approval gating.** Who approved this agent, when was it last reviewed, when is the next review due, when does retirement fire.
5. **Supply chain.** What foundation model, what MCP servers, what base images, what tool versions, what dependency tree.

## The matrix

| Concern | Self-declared | Operator-declared | Discovered |
|---|---|---|---|
| **Identity** | Agent registers on startup with name, charter reference, owner email, instance ID. Sends heartbeats every N minutes. Deregisters on shutdown. Backstop: dead-mans-switch alerts if heartbeat lapses. | Operator-maintained registry: `agents.yaml` in a GitOps repo, ServiceNow CMDB entry, internal AI inventory tool. Owner-confirmed. Updated on charter signature. | Discovery from cloud-side audit logs (CloudTrail, GCP Audit Logs) of ServiceAccount and IAM principal usage. K8s controller watches ServiceAccount + RoleBinding pairs matching naming patterns (`*-agent`, `*-bot`, `claude-*`). Reverse-lookup from credential fingerprints in Sentinels. |
| **Authorization** | Agent reports its current allowed-tools list, MCP allowlist hashes, and effective scope on registration. Updates registration when scope changes. | Operator records authorized scope in registry, linked to RBAC manifest paths in source control and IAM policy ARNs. | Discovery from K8s RBAC API (list all RoleBindings to agent SAs, sum their permissions), AWS IAM Access Analyzer (effective permissions per principal), Kyverno PolicyReports (which policies actually applied to which agents). |
| **Blast radius** | Agent reports its declared risk tier, damage cap, and forbidden operations from its charter. Reports current environment (dev/staging/prod) and current data class access. | Operator records blast-radius profile per agent: which environments, which data classes, which destructive verbs are theoretically permitted. Includes blast-radius worst-case impact statement (e.g., "could affect Q4 revenue forecasting" or "limited to internal tooling"). | Discovery via threat-modeling output: CSA MAESTRO Layer 7 (agent ecosystem) analysis, MITRE ATLAS techniques mapped to each discovered agent, automated lateral-movement path analysis from agent identity to high-value targets. Behavioral observation: what has this agent actually touched in the last N days? |
| **Approval gating** | Agent reports last charter signature date, next review due date, and current charter version on registration. **Refuses to start if charter is expired.** | Operator-maintained review calendar. Quarterly attestation that owner re-reviews and re-signs the charter. Tracks pending approvals and overdue reviews. | Discovery: registry of charter files in source control, last-modified timestamps, last-PR-merged dates. Cross-reference with self-declared and operator-declared records to surface drift. |
| **Supply chain** | Agent reports its current dependency manifest on registration: foundation model name and version, MCP server names and hashes, base image SHA, lockfile fingerprint. Updates on dependency change. | Operator records the authorized-dependency manifest from the agent charter. Linked to allowlist hashes used by Covenants L2-C5 and L3-C5. Maintains a version-controlled audit trail of approved dependency changes. | Discovery from image registry pull events, package manager logs (npm, pip, cargo), runtime introspection of loaded models and connected MCP servers, SBOM scanning. Cross-reference: what is actually loaded versus what the charter authorized. **Drift = alert.** |

## How to use this as a discipline

Pick a concern. Walk the row left to right. For each cell, ask:

> Do I know this fact about every agent the org operates?

Three test outcomes:

- **All three cells populated:** the inventory is defensible. Agents that exist are recorded by intent, by self-report, and by passive observation. Mismatches across cells are themselves alerts.
- **Only operator-declared cell populated:** the inventory is a spreadsheet. Drift is guaranteed within months.
- **Only discovered cell populated:** the inventory is reactive. You know what is running but not whether it should be. Cannot tier risk; cannot drive control selection.

### Cross-layer mismatch as a signal

- **Discovered but not operator-declared = shadow agent.** Investigate ownership. If real, charter and register it. If unauthorized, retire it.
- **Operator-declared but not discovered = ghost agent.** Either it was retired and the registry was not updated, or it is failing to start and no one noticed.
- **Self-declared but not in operator-declared** = an agent that thinks it has a charter but the org has no record of approving it. Charter integrity failure. Audit.
- **Operator-declared but self-declared dependencies do not match** = scope drift or dependency drift. Re-review the charter.

## Inventory powers the rest of the matrix family

Without Inventory:
- Charter cannot enforce retirement criteria because nothing tracks running agents against criteria.
- Covenants cannot scale because per-agent control selection requires per-agent tier identification.
- Sentinels has no baseline to alert against drift from.
- Interventions runbooks cannot find the right kill switches because the inventory of identity-to-credential-to-runtime mapping is missing.
- Restorations cannot rebuild what it does not know existed.

With Inventory:
- Charter becomes operational (each agent has a discoverable charter file).
- Covenants becomes per-agent (Tier 1 read-only agents get the lighter cell selection; Tier 4 production agents get full coverage).
- Sentinels alerts on inventory drift directly.
- Interventions has named credentials, named ServiceAccounts, named environments per agent in the registry.
- Restorations rebuilds toward the registry's last-known-good state.

## Templates

- [`inventory/templates/inventory-record.yaml`](./inventory/templates/inventory-record.yaml), canonical YAML for one agent's inventory entry. Generated by combining outputs of all three layers. Self-declared layer pushes registration; operator-declared layer is committed YAML in source control; discovered layer is tooling output joined to the other two.

## Where this matrix sits

Inventory is the second of two upstream strategic matrices and the last of the six in the Agentic Matrix family:

- [Charter](./CHARTER_MATRIX.md) (Govern, NIST CSF 2.0 GV): the rules that authorize agents to exist
- **Inventory (Identify, NIST CSF 2.0 ID): the registry of agents that do exist ← this document**
- [Covenants](./MATRIX.md) (Protect, NIST CSF 2.0 PR): what binds the running agent
- [Sentinels](./SENTINELS_MATRIX.md) (Detect, NIST CSF 2.0 DE): what watches the running agent
- [Interventions](./INTERVENTIONS_MATRIX.md) (Respond, NIST CSF 2.0 RS): what stops the running agent
- [Restorations](./RESTORATIONS_MATRIX.md) (Recover, NIST CSF 2.0 RC): what fixes after the agent

**Charter authorizes. Inventory tracks. The four operational matrices govern.** Restorations feeds back into Charter when retirement criteria fire and into Inventory when state changes.

A complete agent governance posture has all six matrices populated, cross-referenced, and current. A defensible posture has at minimum Charter, Inventory, and Covenants populated, with Sentinels in flight. Interventions and Restorations come online when the org has the operational maturity to handle the runbook complexity.

## Reading order

1. This document: the framework essay.
2. [`docs/walkthrough-agentic-inventory-matrix-v5.md`](./docs/walkthrough-agentic-inventory-matrix-v5.md), companion walkthrough (gitignored).
3. [`inventory/`](./inventory/), per-cell discovery guidance and reference scripts.

## Citations

NIST CSF 2.0 ID.AM-* (asset management), ID.RA-* (risk assessment), ID.IM-* (improvement). NIST AI RMF MAP 1.1, 1.5, 4.1, 5.1, 5.2; GOVERN 1.5, MANAGE 4.1. CSA MAESTRO Layer 7 (Agent Ecosystem). NIST SP 800-92 (log management). NIST SP 800-207 (Zero Trust). MITRE ATLAS. CSA Agentic AI Red Teaming Guide. NIST AI Agent Standards Initiative under CAISI (Feb 17, 2026). EU AI Act Art. 12 (record-keeping for high-risk systems).
