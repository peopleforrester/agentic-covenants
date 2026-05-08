# The Agentic Covenants Matrix

A prevention framework for autonomous-agent governance. Three layers of enforcement, five concerns, fifteen cells. Every cell populated. Every control mapped to authoritative framework citations in [`CITATIONS.md`](./CITATIONS.md). Designed to be walked left-to-right by a platform engineer asking one question per row: *if the agent decides to violate this concern, what stops it at this layer?*

## What this is not

This is not a detection framework. It is not an anticipation framework. It is not a response framework. Those are different matrices that compose with this one. Confusing them is the mistake the existing literature keeps making.

The NIST Cybersecurity Framework 2.0 names six functions: Govern, Identify, Protect, Detect, Respond, Recover. The Agentic Covenants Matrix is **Protect** applied to autonomous agents. Falco rules, OpenTelemetry traces, and Datadog LLM Observability belong in a Detect matrix. Kill switches, credential revocation, rollback automation, and backup restoration belong in Respond and Recover matrices. Mixing them is how you end up with a checklist that pretends after-the-fact logging is the same kind of control as an admission policy. It is not.

## Why "covenants"

A covenant binds. The agent operates under a set of constraints it cannot unilaterally renegotiate. The infrastructure is the counterparty. Each cell in the matrix is a covenant the agent enters by virtue of running inside the perimeter.

Some covenants are advisory and breakable through language alone. Others sit outside the model's reasoning and require flags, filesystem access, or pattern evasion to break. Others sit outside the agent's operating envelope entirely and require compromise, policy gaps, or operator manipulation. The matrix makes that gradient visible.

No layer is unbypassable. The known bypass paths are catalogued in [`BYPASSES.md`](./BYPASSES.md). Stacking layers is the entire point of the framework. If any single layer were sufficient, the matrix would have one column.

## The two axes

### Vertical: where prevention happens

1. **In-agent.** System prompts, model training, tool descriptions, refusals. The in-agent layer is structurally not the same kind of thing as a human safety check. It has no homeostatic stake (no body that tightens before a destructive action), no pre-action pause (no internal gate that flags "this one needs a second look" before the look happens), and no learning loop between sessions (model weights do not update from yesterday's failure; agentic memory is text reinjected at retrieval, not updated cognition). Telling an agent to "be careful" does not install any of this missing machinery. Bypassable through prompt injection, jailbreak, novel framing, model error, or upstream-content tool-description manipulation. **Treat as the weakest layer. Useful as a nudge. Never as a control.**

2. **Client-side hooks.** Runs on the operator's machine or in the agent's execution context. Deterministic when invoked. Operator-controlled. Examples: Claude Code PreToolUse hooks, MCP server allowlists, sandbox config, pre-commit hooks, tool allowlists. Sits outside the model's reasoning, so it cannot be talked around by prompt manipulation. Bypassable through documented flags (`--no-verify` and equivalents), filesystem tampering when the agent has write access to the hook surface, and pattern evasion when the hook uses string matching. **Strong against language attacks. Weak against an agent with shell access and time. Best treated as the layer that catches casual misuse and known-dangerous commands, not adversarial agents.**

3. **Server-side enforcement.** Runs on the target system, not on the agent. Deterministic. Target-controlled. Examples: Kubernetes admission, IAM, branch protection, IaC pipeline gates, network policies. Bypass requires either compromising the target, finding gaps in policy coverage, or manipulating the operator into changing the policy. None of these are in the agent's normal operating envelope, but all are documented attack patterns. **The strongest layer in the matrix. Still not absolute.**

### Horizontal: what is being protected

1. **Identity.** The agent is distinguishable from any human or other agent.
2. **Authorization.** Least-privilege scoped access. No wildcards, no inherited operator permissions.
3. **Blast radius.** One bad action stays contained.
4. **Approval gating.** Friction scaled to risk.
5. **Supply chain.** Every dependency, MCP server, registry, and tool call verified before trusted.

## The matrix

| Concern | In-agent (no internal valence) | Client-side hooks | Server-side enforcement |
|---|---|---|---|
| **Identity** | System prompt declares "you are an automation agent named X." Advisory only. | Per-agent API keys or OIDC tokens loaded from operator-owned config. No shared credentials across agents. Filesystem ACLs preventing the agent from reading other agents' credentials on the same machine. (User-agent string is spoofable. Treat as logging convenience, not control.) | Dedicated ServiceAccount or IAM principal per agent. OIDC federation with workload identity. Short-lived bound tokens (15-minute TTL). Auth provider rejects requests where agent identity is missing or stale. |
| **Authorization** | Model instructions ("do not modify production resources"). Tool descriptions scoped to safe operations. | `--allowedTools` deny-by-default tool-name allowlist. Capability-based tool restriction at the SDK or wrapper layer (stronger than pattern matching). PreToolUse pattern hooks for known-dangerous commands (catches casual misuse; defeated by obfuscation and equivalent commands). Pre-commit hooks blocking changes to protected paths (effective only when `--no-verify` is not used). Hooks directory and config owned by operator account, not agent. | Scoped RBAC Roles, never ClusterRoles. IAM policies scoped to specific resources with explicit ARN. Kyverno or OPA admission policies. Namespace-scoped permissions. Deny `*` verbs. Deny prod namespaces from agent ServiceAccounts. |
| **Blast radius** | Model declines destructive operations. Verified failure mode in Kiro, Replit, and DataTalks.Club incidents. | Sandbox at process launch with inheritance enforcement (Seatbelt on macOS, bubblewrap on Linux, gVisor for containerized agents). Seccomp or AppArmor profile applied at launch (stronger than pattern denial). `--network none` for non-network tasks. Read-only volume mounts on operator data. Dry-run defaults for destructive commands. Require explicit `--confirm` flag past the first command in a session. | Gated IaC apply pipeline as the actual backstop. (`prevent_destroy` lifecycle is bypassable: agent editing `.tf` can remove the block and run `apply` in the same cycle. Effective only when paired with the gated pipeline.) ResourceQuota and LimitRange per namespace. NetworkPolicy default-deny with explicit allowlist. Physical separation of prod and non-prod clusters. Immutable backups with separate credentials. PodDisruptionBudget on critical workloads. |
| **Approval gating** | Model says "are you sure?" before destructive ops. Silently bypassable. The model can be talked out of asking. | PreToolUse hooks gating destructive command patterns (`rm -rf`, `terraform destroy`, `DROP TABLE`, `kubectl delete`). Tiered approval config matching friction to blast radius (alert fatigue is the failure mode tiering exists to fight; flat approval workflows degrade to reflexive approval). Typed confirmation required for tier-3 commands. Session limits on consecutive destructive ops. Out-of-band confirmation channel (separate terminal, operator phone) for highest-tier actions. **Judgment-query escalation (emerging pattern, limited tooling support):** the agent self-flags actions requiring inputs it cannot generate (value tradeoffs, irreversibility, brand voice, customer concentration risk) and routes to the operator for the missing input, not for yes/no approval. Distinct from rubber-stamp gating; resistant to fatigue because frequency is bounded by genuine novelty rather than by command pattern. (Pattern matching catches obvious destructive verbs; equivalent commands like `kubectl scale --replicas=0` defeat it.) | Branch protection requiring PR review. CODEOWNERS on critical paths. Multi-party approval on prod merges. IaC pipeline runs `plan` only; separate gated job runs `apply`. Deployment freezes during incident windows enforced by pipeline, not policy. |
| **Supply chain** | Model warns about unvetted packages or unfamiliar MCP servers. Unreliable. Frequently wrong. | MCP server allowlist with hash pinning, config owned by operator account. Sigstore signature verification before install. Lockfile pinning (only meaningful when paired with server-side integrity validation in CI; lockfiles alone do not protect against an agent that can edit `package-lock.json` or `requirements.txt`). Pre-commit dependency scan (effective only when `--no-verify` is not used). Reject unsigned MCP servers at handshake. | Image registry restrictions in admission policy. OCI signature verification (cosign). SBOM admission requirements. Egress NetworkPolicy to approved registries only. OPA policy denying images without provenance attestation. Reject MCP server connections from non-allowlisted domains at the network layer. |

## How to use this as a checklist

Pick a concern. Walk the row left to right. For each cell, ask:

> If the agent decides to violate this concern, what stops it at this layer?

Three test outcomes:

- **All three cells populated:** the concern is covered with defense in depth. The in-agent cell catches casual mistakes through prompting. The client-side cell catches deliberate but unsophisticated attempts. The server-side cell is the backstop, requiring compromise or policy gaps to bypass. None of the layers is alone sufficient. The stack is.
- **Only the in-agent cell populated:** the concern is unprotected. The model can be talked out of it. **Audit finding.**
- **Server-side cell populated, others not:** the concern is enforced, but discovery happens late. Add the client-side cell to fail fast, save audit log volume, and reduce noise from blocked attempts.

Some cells legitimately stay empty. Not every concern needs all three layers populated. The choice should be deliberate. Document empty cells in the threat model so a reviewer can see they were considered.

## What sits next to this matrix (deliberately separate)

Three other matrices the audience will eventually need. Calling them out here so the prevention matrix does not get loaded with controls that do not belong in it:

- **Detection matrix.** Falco, eBPF runtime monitoring, OpenTelemetry agent traces, Datadog LLM Observability, audit log analysis, anomaly detection on tool-call patterns. Answers "what just happened?" Does not prevent. Maps to NIST CSF 2.0 Detect (DE).
- **Response matrix.** One-button credential revocation, session termination, kill switches, automatic rollback triggers, incident commander escalation, paging integration. Answers "how do I stop the bleeding?" Activates after detection fires. Maps to NIST CSF 2.0 Respond (RS).
- **Recovery matrix.** Backup restoration, GitOps `git revert`, database point-in-time recovery, infrastructure rebuild from known-good state, postmortem and learning loop. Answers "how do I get back to normal and not repeat this?" Maps to NIST CSF 2.0 Recover (RC).

These three plus the Agentic Covenants Matrix cover Protect, Detect, Respond, and Recover. The Identify (ID) function (asset inventory, threat modeling, agent registry) is upstream of all four and is where MITRE ATLAS and CSA MAESTRO do their best work. The sixth NIST CSF 2.0 function, Govern (GV), wraps them all and is where NIST AI RMF GOVERN subcategories live.

## Why post-hoc governance fails for agents

Corporate governance as it exists in 2026 (audits, reviews, approval workflows, quarterly access reviews, postmortems) was built around two assumptions that are baseline for human actors and absent for agents. First, the actor is slow enough that there is meaningful time between the bad call and the irreversible consequence. Second, the actor has internal machinery (homeostatic stake, pre-action valence, second-order learning) that catches most bad calls before any external control fires. The post-hoc layer is mostly there for the rare cases the internal layer misses.

Agents collapse the time gap (hundreds of actions per minute) and have none of the internal machinery. Scaling up post-hoc machinery (more review, more audit, more approval gates with automation) does not fix this; it tries to install the slow review layer in front of an actor whose entire advantage is speed, and it fails by either becoming a bottleneck or by inducing alert fatigue in the reviewers.

Prevention-first is the response. Engineer the bad outcome out of reach (server-side enforcement). Make deterministic checks fail fast at the operator's machine (client-side hooks). Use the in-agent layer as a nudge, not a control. Then attach Detect, Respond, and Recover matrices for the residual risk that prevention does not cover.

## Reading order

1. This document — framework essay.
2. [`BYPASSES.md`](./BYPASSES.md) — every control, every documented bypass path. Read this before you trust any single layer.
3. [`CITATIONS.md`](./CITATIONS.md) — every cell mapped to NIST CSF 2.0, NIST AI RMF, OWASP LLM Top 10, OWASP Agentic Top 10, plus zero-trust and supply-chain SPs.
4. [`controls/`](./controls/) — pick a cell, copy the artifact.
5. [`checklists/`](./checklists/) — print and walk.
6. [`examples/`](./examples/) — three end-to-end deployments.
