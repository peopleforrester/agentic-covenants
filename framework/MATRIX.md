# The Agentic Covenants Matrix

A prevention framework for agent governance. Three layers of enforcement, six concerns, eighteen cells, every cell populated honestly. Every control mapped to authoritative governmental and standards-body citations in [`CITATIONS.md`](./CITATIONS.md), with known bypass paths catalogued in [`BYPASSES.md`](./BYPASSES.md). Designed to be walked left-to-right by a platform engineer asking one question per row: *if the agent decides to violate this concern, what stops it at this layer?*

## What this is not

This is not a detection framework. It is not an anticipation framework. It is not a response framework. Those are different matrices that compose with this one. Confusing them is the mistake the existing literature keeps making.

The NIST Cybersecurity Framework 2.0 names six functions: Govern, Identify, Protect, Detect, Respond, Recover. The Agentic Covenants Matrix is **Protect** applied to autonomous agents. Falco rules, OpenTelemetry traces, and Datadog LLM Observability belong in a Detect matrix. Kill switches, credential revocation, rollback automation, and backup restoration belong in Respond and Recover matrices. Mixing them is how you end up with a checklist that pretends after-the-fact logging is the same kind of control as an admission policy. It is not.

The companion **Detect** matrix is co-located in this repo at [`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md). The remaining four functions of NIST CSF 2.0 (Identify, Respond, Recover, Govern) are tracked elsewhere.

## Why "covenants"

A covenant binds. The agent operates under a set of constraints it cannot unilaterally renegotiate. The infrastructure is the counterparty. Each cell in the matrix is a covenant the agent enters by virtue of running inside the perimeter.

Some covenants are advisory and breakable through language alone. Others sit outside the model's reasoning and require flags, filesystem access, or pattern evasion to break. Others sit outside the agent's operating envelope entirely and require compromise, policy gaps, or operator manipulation. The matrix makes that gradient visible.

No layer is unbypassable. The known bypass paths are catalogued in [`BYPASSES.md`](./BYPASSES.md), including 2026 incidents and disclosed CVEs. Stacking layers is the entire point of the framework. If any single layer were sufficient, the matrix would have one column.

## The two axes

### Vertical: where prevention happens

1. **In-agent.** System prompts, model training, tool descriptions, refusals. The in-agent layer is structurally not the same kind of thing as a human safety check. It has no homeostatic stake (no body that tightens before a destructive action), no pre-action pause (no internal gate that flags "this one needs a second look" before the look happens), and no learning loop between sessions (model weights do not update from yesterday's failure; agentic memory is text reinjected at retrieval, not updated cognition). Telling an agent to "be careful" does not install any of this missing machinery. Anthropic's own published data on Claude Code Auto Mode (March 25, 2026) reports that users approve **93%** of permission prompts, which is the strongest available evidence that human-in-the-loop on top of in-agent gates degrades to a rubber stamp at scale. Bypassable through prompt injection, jailbreak, novel framing, model error, or upstream-content tool-description manipulation. **Treat as the weakest layer. Useful as a nudge. Never as a control.**

2. **Client-side hooks.** Runs on the operator's machine or in the agent's execution context. Deterministic when invoked. Operator-controlled. Examples: Claude Code PreToolUse hooks following the deny-then-ask-then-allow precedence model, MCP server allowlists, sandbox config built on Linux bubblewrap or macOS Seatbelt, pre-commit hooks, `--allowedTools` allowlists, capability-based tool restriction at the SDK or wrapper layer. Sits outside the model's reasoning, so it cannot be talked around by prompt manipulation. Bypassable through documented flags (`--no-verify`, `--dangerously-skip-permissions` and equivalents), filesystem tampering when the agent has write access to the hook surface, and pattern evasion when the hook uses string matching. **Strong against language attacks. Weak against an agent with shell access and time. Best treated as the layer that catches casual misuse and known-dangerous commands, not adversarial agents.**

3. **Server-side enforcement.** Runs on the target system, not on the agent. Deterministic. Target-controlled. Examples: Kubernetes admission, IAM, branch protection (with admin bypass disabled), IaC pipeline gates, network policies, OCI signature verification with cosign, SBOM admission, SLSA build provenance attestation. Bypass requires either compromising the target, finding gaps in policy coverage, or manipulating the operator into changing the policy. None of these are in the agent's normal operating envelope, but all are documented attack patterns. **The strongest layer in the matrix. Still not absolute.**

### Horizontal: what is being protected

1. **Identity.** The agent is distinguishable from any human or other agent. Identity is established outside the agent and carried by the agent, never declared by the agent itself.
2. **Authorization.** Least-privilege scoped access. No wildcards, no inherited operator permissions. OWASP's Least Agency principle, applied.
3. **Blast radius.** One bad action stays contained.
4. **Approval gating.** Friction scaled to risk.
5. **Supply chain.** Every dependency, MCP server, registry, and tool call verified before trusted. The lethal trifecta (private data plus untrusted content plus external communication) is treated as a forbidden state.

## The matrix

| Concern | In-agent (no internal valence) | Client-side hooks | Server-side enforcement |
|---|---|---|---|
| **Identity** | System prompt declares "you are an automation agent named X." Identity is *carried*, not *established*. The cell is advisory. Identity claims made in a system prompt have no cryptographic weight; the agent cannot prove its own identity to the target. | Per-agent API keys or OIDC tokens loaded from operator-owned config. No shared credentials across agents. Filesystem ACLs preventing the agent from reading other agents' credentials on the same machine. (User-agent string is spoofable. Treat as logging convenience, not control.) | Dedicated ServiceAccount or IAM principal per agent. OIDC federation with workload identity. Short-lived bound tokens (15-minute TTL). Auth provider rejects requests where agent identity is missing or stale. SPIFFE/SPIRE for cross-cluster identity. Per the NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (February 5, 2026), identity must be established by an external IdP via OAuth 2.0 or equivalent, with metadata recording supervising agent or user, never asserted by the agent itself. |
| **Authorization** | Model instructions ("do not modify production resources"). Tool descriptions scoped to safe operations. | `--allowedTools` deny-by-default tool-name allowlist. Capability-based tool restriction at the SDK or wrapper layer (stronger than pattern matching). PreToolUse pattern hooks for known-dangerous commands (catches casual misuse; defeated by obfuscation and equivalent commands). Pre-commit hooks blocking changes to protected paths (effective only when `--no-verify` is not used). Hooks directory and config owned by operator account, not agent. Deny-then-ask-then-allow precedence; PreToolUse hooks returning "allow" must not bypass deny rules (Claude Code patched this regression in May 2026; pre-patch deployments are vulnerable). | Scoped RBAC Roles, never ClusterRoles. IAM policies scoped to specific resources with explicit ARN. Kyverno or OPA admission policies. Namespace-scoped permissions. Deny `*` verbs. Deny prod namespaces from agent ServiceAccounts. |
| **Blast radius** | Model declines destructive operations. Verified failure mode in Kiro, Replit, DataTalks.Club, and Amazon Q (CVE-2025-8217) incidents. **No enforcement at this layer; advisory only.** Prevention lives in columns 2 and 3. | Sandbox at process launch with inheritance enforcement. Linux: bubblewrap (Anthropic's reference implementation for Claude Code, May 2026). macOS: Seatbelt. Containerized: gVisor. Network isolation via unix-domain-socket proxy outside the sandbox enforcing egress allowlists. Seccomp or AppArmor profile applied at launch (stronger than pattern denial). `--network none` for non-network tasks. Read-only volume mounts on operator data. Dry-run defaults for destructive commands. Require explicit `--confirm` flag past the first command in a session. Anthropic's published data shows the sandbox approach reduces permission prompts by 84%, which is the only evidence-based way to fight the 93% rubber-stamp problem. | Gated IaC apply pipeline as the actual backstop. Terraform `prevent_destroy` lifecycle is bypassable: `terraform state rm` removes the resource from state, removing the resource block from configuration plus `terraform apply` deletes it, direct state edits go around it entirely. Effective only when paired with the gated pipeline. ResourceQuota and LimitRange per namespace. NetworkPolicy default-deny with explicit allowlist. Physical separation of prod and non-prod clusters. Immutable backups with separate credentials. PodDisruptionBudget on critical workloads. |
| **Approval gating** | Model says "are you sure?" before destructive ops. Silently bypassable. The model can be talked out of asking. Anthropic Auto Mode data: **93% approval rate** on permission prompts. Treat any approval prompt that fires often as already broken. | PreToolUse hooks gating destructive command patterns (`rm -rf`, `terraform destroy`, `DROP TABLE`, `kubectl delete`). Tiered approval config matching friction to blast radius (the failure mode tiering exists to fight is the same alarm fatigue documented in clinical alerting per AHRQ PSNet, MFA prompt fatigue, and GDPR consent fatigue; flat approval workflows degrade to reflexive approval). Typed confirmation required for tier-3 commands. Session limits on consecutive destructive ops. Out-of-band confirmation channel (separate terminal, operator phone) for highest-tier actions. **Judgment-query escalation:** the agent self-flags actions requiring inputs it cannot generate (value tradeoffs, irreversibility, brand voice, customer concentration risk) and routes to the operator for the missing input, not for yes/no approval. Distinct from rubber-stamp gating; resistant to fatigue because frequency is bounded by genuine novelty rather than by command pattern. Anthropic's Auto Mode classifier (Sonnet 4.6, two-stage filter, 8.5% first-stage false positive, 0.4% second-stage false positive, 17% false negative) is the reference probabilistic implementation. (Pattern matching catches obvious destructive verbs; equivalent commands like `kubectl scale --replicas=0` defeat it.) | Branch protection requiring PR review. CODEOWNERS on critical paths. Multi-party approval on prod merges. IaC pipeline runs `plan` only; separate gated job runs `apply`. Deployment freezes during incident windows enforced by pipeline, not policy. **"Do not allow bypassing the above settings"** must be enabled or admins and roles with bypass permission walk through every gate. |
| **Supply chain** | Model warns about unvetted packages or unfamiliar MCP servers. **No enforcement at this layer; advisory only.** Prevention lives in columns 2 and 3. | MCP server allowlist with manifest hash pinning, config owned by operator account. Tool descriptions hashed on first approval and re-prompted on change (defends against tool-poisoning rug-pulls). Sigstore signature verification before install. Lockfile pinning (only meaningful when paired with server-side integrity validation in CI; lockfiles alone do not protect against an agent that can edit `package-lock.json` or `requirements.txt`). Pre-commit dependency scan (effective only when `--no-verify` is not used). Reject unsigned MCP servers at handshake. Skill or extension allowlist tooling for agent platform marketplaces (SkillCheck, ToxicSkills, SecureClaw, Snyk agent-scan, Cisco mcp-scanner) given the ClawHavoc campaign demonstrated marketplaces are part of the supply chain. | Image registry restrictions in admission policy. OCI signature verification with cosign. SBOM admission requirements. Egress NetworkPolicy to approved registries only. OPA policy denying images without provenance attestation. SLSA build-provenance attestation gates. MCP domain allowlist enforced at the network layer, not just the agent. Per NIST CSF 2.0 ID.RA-09: authenticity and integrity of hardware and software assessed prior to acquisition and use. |
| **Content integrity** | System-prompt hardening, instruction hierarchy, provenance framing of untrusted content (see `controls/content-integrity/in-agent/untrusted-content-framing.md`). **Advisory, and weaker here than anywhere else in this matrix: prompt injection is an attack aimed precisely at this layer, so it is the one surface the adversary is directly optimizing against.** Reduces low-effort attacks so downstream scanners have less to score. Never cite it as a mitigation in a risk register. | Input scanning before the model sees fetched content, output scanning before a response or tool argument leaves, tool-result sanitization (zero-width and bidi codepoint stripping, delimiter-spoof removal), provenance tagging with a per-fetch nonce. Tooling to evaluate rather than endorse: LLM Guard, NeMo Guardrails (NVIDIA states it is not production-ready in its current beta), Llama Guard and Prompt Guard 2, Presidio for PII. **Probabilistic, not deterministic: these score and threshold rather than admit and deny, so false positives and false negatives are inherent and a determined adversary evades them by encoding, translation, indirection, or multi-turn setup.** Never block on input scores; that is how a control gets switched off next quarter. Block on output, where a false positive costs a retry and a false negative costs a secret. | Egress NetworkPolicy so exfiltration has nowhere to post, DLP at the boundary, send-side audit written outside the agent's reach (`controls/content-integrity/server-side/`). **This is deliberately the weakest server-side cell in the framework: nothing on the server side can distinguish a prompt injection from the document it arrived in, because it is well-formed text on an authorized channel from an approved source. It catches the consequence, not the manipulation.** The control that actually works is not a content control at all: a scoped credential, deny-by-default RBAC, and a default-deny egress policy make a successful injection worthless. Injection is an authorization and blast-radius problem wearing a content costume. |

## How to use this as a checklist

Pick a concern. Walk the row left to right. For each cell, ask:

> If the agent decides to violate this concern, what stops it at this layer?

Three test outcomes:

- **All three cells populated:** the concern is covered with defense in depth. The in-agent cell catches casual mistakes through prompting. The client-side cell catches deliberate but unsophisticated attempts. The server-side cell is the backstop, requiring compromise or policy gaps to bypass. None of the layers is alone sufficient. The stack is.
- **Only the in-agent cell populated:** the concern is unprotected. The model can be talked out of it. **Audit finding.**
- **Server-side cell populated, others not:** the concern is enforced, but discovery happens late. Add the client-side cell to fail fast, save audit log volume, and reduce noise from blocked attempts.

Some cells legitimately stay empty. The L1-C3 (Blast radius / In-agent) and L1-C5 (Supply chain / In-agent) cells are explicitly empty in this matrix because the in-agent layer cannot enforce these concerns. **That is the correct state, not a gap.** Document empty cells in the threat model so a reviewer can see they were considered.

## What sits next to this matrix (deliberately separate)

Three other matrices the audience will eventually need. Calling them out here so the prevention matrix does not get loaded with controls that do not belong in it:

- **Detection matrix** ([`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md), co-located in this repo). Falco, eBPF runtime monitoring, OpenTelemetry agent traces, Datadog LLM Observability, audit log analysis, anomaly detection on tool-call patterns, cross-tool call-chain correlation. Answers "what just happened?" Does not prevent. Maps to NIST CSF 2.0 Detect (DE).
- **Response matrix** (Interventions; tracked separately). One-button credential revocation, session termination, kill switches, automatic rollback triggers, incident commander escalation, paging integration. Answers "how do I stop the bleeding?" Activates after detection fires. Maps to NIST CSF 2.0 Respond (RS).
- **Recovery matrix** (Restorations; tracked separately). Backup restoration, GitOps `git revert`, database point-in-time recovery, infrastructure rebuild from known-good state, postmortem and learning loop. Answers "how do I get back to normal and not repeat this?" Maps to NIST CSF 2.0 Recover (RC).

These three plus the Agentic Covenants Matrix cover Protect, Detect, Respond, and Recover. The Identify (ID) function (asset inventory, threat modeling, agent registry) is upstream of all four and is where MITRE ATLAS, CSA MAESTRO, and NISTIR 8596 (Cyber AI Profile, December 2025) do their best work. The Govern (GV) function wraps them all and is where NIST AI RMF GOVERN subcategories, ISO/IEC 42001:2023, and the EU AI Act Article 9 (risk management system) live.

## Why post-hoc governance fails for agents

Corporate governance as it exists in 2026 (audits, reviews, approval workflows, quarterly access reviews, postmortems) was built around two assumptions that are baseline for human actors and absent for agents. First, the actor is slow enough that there is meaningful time between the bad call and the irreversible consequence. Second, the actor has internal machinery (homeostatic stake, pre-action valence, second-order learning) that catches most bad calls before any external control fires. The post-hoc layer is mostly there for the rare cases the internal layer misses.

Agents collapse the time gap (hundreds of actions per minute) and have none of the internal machinery. Scaling up post-hoc machinery (more review, more audit, more approval gates with automation) does not fix this; it tries to install the slow review layer in front of an actor whose entire advantage is speed, and it fails by either becoming a bottleneck or by inducing alert fatigue in the reviewers. Anthropic's own data on Claude Code Auto Mode (March 25, 2026) reports a **93%** approval rate on permission prompts, which is the empirical ceiling for human-in-the-loop on top of in-agent gates.

Prevention-first is the response. Engineer the bad outcome out of reach (server-side enforcement). Make deterministic checks fail fast at the operator's machine (client-side hooks). Use the in-agent layer as a nudge, not a control. Then attach Detect, Respond, and Recover matrices for the residual risk that prevention does not cover.

## How the original eight map into the matrix

For continuity with the devopsdays Atlanta talk, KubeCon EU material, and the March 10 article:

| Original guardrail | New location |
|---|---|
| 1. Treat agent as untrusted workload | Identity column + Authorization column |
| 2. Sandbox by default | Blast radius / client-side cell |
| 3. Never give an agent your permissions | Identity column + Authorization column |
| 4. Tiered approval | Approval gating column (entire column) |
| 5. Cluster-level policy enforcement | Authorization + Blast radius / server-side cells |
| 6. IaC behind a gate | Approval gating / server-side cell |
| 7. Audit the MCP attack surface | Supply chain column (entire column) |
| 8. Monitor agents like production | Belongs in the Detection matrix, not here |

Old 1 and 3 were one idea said twice. Old 2, 4, and 6 were three mechanisms answering the same blast-radius and approval-friction concern. Old 8 was a category error: a detection control inside a list called guardrails. The matrix surfaces the duplicates and pushes the detection control to the matrix where it belongs.

## The five concerns are not idiosyncratic

On April 30, 2026, six allied cyber agencies (CISA, NSA, ACSC, Canadian Centre for Cyber Security, NZ NCSC, UK NCSC) published **"Careful Adoption of Agentic AI Services"**, the first multi-nation joint guidance dedicated to agentic AI. It names five risk categories, and they map almost one-to-one onto the five concerns of this matrix:

| Five Eyes risk category | Concern in this matrix |
|---|---|
| Privilege escalation | Identity + Authorization |
| Design and configuration flaws | Authorization |
| Behavioral misalignment | Blast radius + Approval gating |
| Structural cascading failures | Blast radius |
| Accountability opacity | Charter + Inventory |

The guidance's posture, adopt incrementally starting with low-risk tasks, and treat governance, human oversight, monitoring, and explicit accountability as requirements rather than options, is this framework's argument with artifacts attached. Full crosswalk, plus the US DoD / federal control mapping (NIST SP 800-53 families, DoD Zero Trust pillars, RMF/cATO/CSRMC, DoD RAI principles), is in [`CITATIONS.md`](./CITATIONS.md#us-dod--federal-crosswalk).

## Reading order

1. This document: the framework essay.
2. [`BYPASSES.md`](./BYPASSES.md), every control, every documented bypass path, including 2026 incidents and disclosed CVEs. Read this before you trust any single layer.
3. [`CITATIONS.md`](./CITATIONS.md), every cell mapped to NIST CSF 2.0, NIST AI RMF, OWASP LLM Top 10, OWASP Agentic Top 10, OWASP MCP Top 10, EU AI Act, ISO/IEC 42001, plus zero-trust and supply-chain SPs, **and a US DoD / federal crosswalk** (800-53, DoD ZT, RMF/cATO/CSRMC, RAI).
4. [`controls/`](../controls), pick a cell, copy the artifact.
5. [`checklists/`](../checklists), print and walk.
6. [`examples/`](../examples), end-to-end deployments, including an [air-gapped / DoD IL4-IL5 variant](../examples/dod-air-gapped).

## Companion: Sentinels (Detect)

For detection of what this matrix prevents, see [`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md) and [`sentinels/`](../sentinels). Architecturally distinct from this matrix; co-located so a single platform team can walk both in one pass.
