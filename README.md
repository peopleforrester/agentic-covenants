# Agentic Covenants

**A prevention framework for autonomous-agent governance.**
Three layers of enforcement, five concerns, fifteen cells.
Every cell answers one question: *if the agent decides to violate this concern, what stops it at this layer?*

---

## TL;DR

Stop trying to prompt your way out of an agent governance problem.

The Agentic Covenants Matrix arranges agent prevention controls by where they actually run. The columns get progressively harder for an agent to bypass. The rows are the five things that go wrong. The cells contain real, working artifacts (Kyverno policies, seccomp profiles, PreToolUse hooks, RBAC roles, branch-protection Terraform, cosign policies) — not principles, not pep talks.

This repo gives you the cells.

| Concern | In-agent (advisory) | Client-side hooks | Server-side enforcement |
|---|---|---|---|
| **Identity** | system-prompt declaration | per-agent credentials, FS ACLs | dedicated SA / IAM, OIDC, short-TTL tokens |
| **Authorization** | scoped tool descriptions | `--allowedTools`, PreToolUse, pre-commit | RBAC, IAM, Kyverno/OPA admission |
| **Blast radius** | refusals (verified-bypassable) | sandbox at launch, seccomp/AppArmor, dry-run | gated IaC apply, ResourceQuota, NetworkPolicy, immutable backups |
| **Approval gating** | "are you sure?" | tiered hooks, judgment-query escalation | branch protection, CODEOWNERS, plan-and-apply split |
| **Supply chain** | warning prompt | MCP allowlist + Sigstore, lockfile pinning | cosign verification, SBOM admission, egress NetworkPolicy |

Full row-by-row text and citations: [`MATRIX.md`](./MATRIX.md).

---

## What this is

A practitioner-layer **Protect** framework for autonomous agents, mapped to NIST CSF 2.0, NIST AI RMF, OWASP LLM Top 10, OWASP Agentic Top 10, NIST SP 800-207, and SP 800-218A.

It is the matrix that tells a platform engineer which Kyverno policy to write on Monday morning.

## What this is not

This is **not** a detection framework, not a response framework, not a recovery framework. Those are different matrices that compose with this one. Confusing them is the mistake the existing literature keeps making.

The NIST CSF 2.0 functions are Govern, Identify, Protect, Detect, Respond, Recover. This matrix is **Protect**. Falco rules, OpenTelemetry traces, and Datadog LLM Observability belong in a Detect matrix. Kill switches, credential revocation, and rollback automation belong in Respond. Backup restoration belongs in Recover. Mixing them produces a checklist that pretends after-the-fact logging is the same kind of control as an admission policy. It is not.

## Why prevention-first

Corporate governance (audits, reviews, quarterly access reviews, postmortems) was built for actors that are slow and have internal valence: a homeostatic stake, a pre-action pause, a learning loop. Agents collapse the time gap and have none of the internal machinery. Scaling up post-hoc machinery either becomes a bottleneck or induces alert fatigue.

Engineer the bad outcome out of reach (server-side). Make deterministic checks fail fast at the operator's machine (client-side). Use the in-agent layer as a nudge, not a control. Then attach Detect/Respond/Recover for residual risk.

## How to use this repo

1. **Read [`MATRIX.md`](./MATRIX.md)** for the framework essay — the two axes, the cells, and the row-walking procedure.
2. **Walk a row.** Pick a concern. Open its checklist in [`checklists/`](./checklists/). For each layer, ask: *if the agent decides to violate this concern, what stops it at this layer?* Three outcomes:
   - All three cells populated → defense in depth. Done.
   - Only the in-agent cell populated → the model can be talked out of it. **Audit finding.**
   - Server-side populated, client-side empty → enforced but discovered late. Add the client-side cell to fail fast.
3. **Steal the controls.** Each cell directory under [`controls/`](./controls/) has a README explaining the cell, working artifacts, the bypasses (so you know what you're buying), and the framework citations.
4. **Deploy an example.** [`examples/`](./examples/) ships three opinionated deployments wired end-to-end.

## Layout

```
agentic-covenants/
├── README.md
├── MATRIX.md           # Framework essay
├── BYPASSES.md         # Per-control bypass surface (Appendix A)
├── CITATIONS.md        # Per-cell framework crosswalk (Appendix C)
├── matrix.yaml         # Machine-readable matrix
├── controls/           # 15 cells × working artifacts
├── checklists/         # 5 walkable checklists
└── examples/           # 3 end-to-end deployments
```

## License

Dual-licensed:

- **Code** (shell, Python, Terraform, Rego, YAML policy, hooks) under [Apache 2.0](./LICENSE-CODE).
- **Content** (Markdown, the matrix, the citations, the framework text) under [CC BY-SA 4.0](./LICENSE-CONTENT).

See [`LICENSE`](./LICENSE) for the split rule.

## Contributing

A reviewer who finds an additional citation mapping is welcome to contribute it; a reviewer who finds an incorrect mapping is welcome to flag it. Both improve the document. See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Companion: Sentinels (Detect)

Co-located in this repo. The Covenants Matrix is the **Protect** view; the Sentinels Matrix at [`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md) and [`sentinels/`](./sentinels/) is the **Detect** view — Falco rules, eBPF, audit-log pipelines, SIEM detection rules per cell. Architecturally distinct (Covenants asks "what stops it?"; Sentinels asks "what just happened?") but co-located so a single platform team walks both in one pass.

Response and Recovery (NIST CSF 2.0 RS / RC) live elsewhere.

## Status

This repo is the practitioner layer beneath OWASP (which catalogs the threats), NIST (which governs and structures), CSA MAESTRO (which models the attack surface), and lab-side capability frameworks (which govern what models are released). None of those tells a platform engineer what to commit on Monday morning. This does.
