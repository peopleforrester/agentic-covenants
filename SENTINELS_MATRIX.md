# The Agentic Sentinels Matrix

A detection framework for autonomous agent governance. Three layers of observation, five concerns, fifteen cells. Companion to the [Agentic Covenants Matrix](./MATRIX.md) (Protect), the Agentic Interventions Matrix (Respond, tracked separately), and the Agentic Restorations Matrix (Recover, tracked separately). Maps to NIST CSF 2.0 **Detect (DE)** function.

## What this is

Where Covenants prevents, Sentinels notices. The Sentinels Matrix is the answer to *what just happened, when did it happen, and how do I know?* It is not the answer to *how do I stop it* (that is Interventions) or *how do I get back to normal* (that is Restorations). **Detection without prevention is a notification service. Prevention without detection is hope.** The matrix needs all four functions; this document covers one of them.

## Why detection matters even when prevention is built

Covenants is not absolute. Appendix A of the Covenants v5 matrix lists eighteen-plus bypass paths per layer. Sentinels exists because every prevention control will fail eventually, and the gap between failure and discovery determines whether you have an incident or a catastrophe. The 90-day Claude Code CVE corpus (CVE-2025-59536, CVE-2026-21852, CVE-2026-39861, CVE-2026-35021, CVE-2026-32025) demonstrates the cost of late detection: every one of those was caught by external researchers, not by victim telemetry.

Sentinels also protects against the prevention layer itself being compromised. If an attacker tampers with a Kyverno policy, the only thing that catches it is a sentinel watching admission policy state.

## The two axes

### Vertical: where observation happens

1. **In-agent (tamperable).** Agent-side self-reports: transcripts, tool-call logs, reasoning traces, claimed identity. Useful for forensics. Tamperable by design (the agent or its operator can suppress, edit, or omit). **Treat as evidence, not proof.**
2. **Client-side telemetry.** Telemetry from the operator's machine: filesystem audit (auditd, fs.notify), command-line history, hook decision logs, sandbox boundary events, network attempts. Outside the model's reasoning. Still on the operator's machine, so still tamperable by an attacker who roots the operator.
3. **Server-side observability.** Telemetry from the target system: cloud audit logs (CloudTrail, GCP Audit, Azure Monitor), Kubernetes audit log, eBPF runtime detection (Falco, Tetragon), admission policy violation events, network-layer flow logs, SIEM correlation. Outside the agent and the operator. **Tamperable only with privileged compromise of the observability infrastructure itself.**

### Horizontal: what is being observed

1. **Identity.** Who acted, whether the claimed identity matches the cryptographically verified one.
2. **Authorization.** What the actor tried to do, whether it was permitted, whether permission was granted.
3. **Blast radius.** How far the action propagated, what containment held, what containment failed.
4. **Approval gating.** Whether approval was sought, granted, or bypassed; whether the bypass was sanctioned.
5. **Supply chain.** What was loaded, from where, with what signatures, against what allowlist.

## The matrix

| Concern | In-agent (tamperable) | Client-side telemetry | Server-side observability |
|---|---|---|---|
| **Identity** | Agent transcript records claimed identity in tool-call metadata. Useful for forensics. The agent that misuses identity will not log honestly about it. | Per-session tool-call logs with credential-fingerprint (hash of token, never the token itself). Hook decision logs include identity. ssh `last`-style record of agent process startup with effective UID. | CloudTrail / Kubernetes audit log attributes every API call to a verified identity. Alert on: identity not in expected set, identity used outside expected hours, identity used from unexpected source IP, identity reuse across agents (each agent should have its own). IdP issues alerts on token mint anomalies. |
| **Authorization** | Agent transcript shows tools requested. Reasoning trace shows intent. The agent may not log denied attempts and may not log obfuscated commands accurately. | Hook decision log: every PreToolUse decision (allow / ask / deny / error). Auditd watches for hook config edits, deny-list tampering, `--no-verify` flag in process args. Filesystem audit on `~/.claude/` and `/etc/agents/`. | RBAC denial events from Kubernetes audit. IAM access analyzer reports unused permissions. Kyverno PolicyReports surface admission failures. OPA decision logs centralized. SIEM rule: agent ServiceAccount tries to escalate verb, alert. |
| **Blast radius** | Agent reasoning trace shows scope of intended operations. Tool-call log shows actual scope. **Lethal trifecta detector** flags when private data, untrusted content, and external communication appear in the same context window. | Sandbox boundary events from bubblewrap or seccomp logging. Network attempts on `--network none` agents. eBPF on the operator host catches escape attempts. Process tree monitoring catches unsandboxed children. | NetworkPolicy violation events. ResourceQuota near-limit alerts. Falco rules on container escape patterns, unexpected process spawns, unexpected file writes outside the workspace. Kubernetes audit captures cross-namespace operations. CSP-side flow logs (VPC Flow Logs, GCP VPC Flow Logs) detect unexpected egress. |
| **Approval gating** | Agent transcript records when "are you sure?" prompts appeared and how they were answered. Anthropic Auto Mode classifier decisions logged with confidence scores. Judgment-query escalation events. | Hook decision log: every approval prompt, response, and timing. Detect alert-fatigue patterns (response time below threshold = reflexive approval). Detect tier-3 confirmations with mismatched typed-input rejections. Out-of-band approval channel logs (separate from the agent). | Branch protection bypass events (every push that bypassed required reviews). CODEOWNERS bypass events. IaC pipeline approval-gate events. Deployment freeze breach alerts. Audit log on changes to branch protection itself (the protection of the protection). |
| **Supply chain** | Agent transcript records which MCP servers it connected to and tools it loaded. Tool-description hash logged on first use; mismatch logged on every subsequent use. | MCP allowlist violation events. Lockfile diff in CI logs for every commit. Pre-commit dependency scan results centralized (even when bypassed locally). Skill-allowlist scanner output for each agent platform marketplace install. | Image registry pull events with signature verification status. SBOM diff over time per workload. Cosign verification failures as alert source. Egress NetworkPolicy denials when agents try to reach non-allowlisted MCP domains. SIEM rule: image deployed without provenance attestation, alert. |

## How to use this as a checklist

Pick a concern. Walk the row left to right. For each cell, ask:

> If a violation of this concern occurs, what tells me, how fast, and how reliably?

Three test outcomes:

- **All three cells populated:** defense in depth for detection. In-agent gives forensic context. Client-side detects local tampering. Server-side is the tamper-resistant truth.
- **Only the in-agent cell populated:** the agent is the only thing reporting on the agent. **Audit finding.**
- **Server-side cell populated, others not:** detection happens but with no context. Add client-side telemetry to enable triage.

The Sentinels Matrix has the same intellectual honesty as Covenants: in-agent is the weakest layer because the agent that violates a concern will not reliably report on its own violation. Server-side is the strongest layer because it sits outside the agent's tampering envelope.

## Why detection cannot be the sole control

Three reasons, all of which the matrix names:

1. **Detection is after the fact.** By the time the SIEM rule fires, the action has happened. Sentinels tells you something occurred; it does not undo it. That is why **Interventions** and **Restorations** exist as separate matrices.
2. **Detection has false negative rates.** Anthropic's Auto Mode classifier reports a **17% false negative rate**. Falco rules miss novel patterns. SIEM correlations miss low-and-slow attacks. The detection layer catches most of what gets through prevention, **not all**.
3. **Detection has false positive rates.** Anthropic's Auto Mode classifier reports an **8.5% first-stage false positive rate**. Aggressive Falco rules generate alert fatigue identical to the approval-gating problem in [Covenants L2-C4](./controls/approval-gating/client-side/). **Detection that humans ignore is detection that does not exist.**

## Where this matrix sits

Sentinels is one of four operational matrices in the Agentic Matrix family:

- **Covenants** (Protect, NIST CSF 2.0 PR): what binds the running agent — [`MATRIX.md`](./MATRIX.md), [`controls/`](./controls/)
- **Sentinels** (Detect, NIST CSF 2.0 DE): what watches the running agent — this document, [`sentinels/`](./sentinels/)
- **Interventions** (Respond, NIST CSF 2.0 RS): what stops the running agent — tracked separately
- **Restorations** (Recover, NIST CSF 2.0 RC): what fixes after the agent — tracked separately

Two upstream strategic matrices wrap the operational four:

- **Charter** (Govern, NIST CSF 2.0 GV): who authorized the agent and under what policy
- **Inventory** (Identify, NIST CSF 2.0 ID): what agents exist and what they touch

A complete agent governance posture has all six. Most teams start with Covenants because prevention is the floor, then add Sentinels because uncovered detection is the most common audit finding. Interventions and Restorations follow when the org has matured enough to handle the runbook complexity.

## Two principles before the cells

1. **Every detection must have a defined response.** Sentinels alerts that do not page someone or trigger an Interventions runbook are theatre. Build the alert and the runbook together.
2. **Detection has false-positive cost.** Anthropic's Auto Mode reports an 8.5% first-stage classifier rate; acceptable when the false-positive cost is "ask a human." Unacceptable when the false-positive cost is "page the on-call at 3 a.m." A SIEM rule with 8.5% FP at 10,000 events/day is 850 unnecessary pages. **Tune.**

## Reading order

1. This document — framework essay.
2. [`docs/walkthrough-agentic-sentinels-engineering-actions-v5.md`](./docs/walkthrough-agentic-sentinels-engineering-actions-v5.md) — engineering-actions companion (gitignored; lives in operator working notes).
3. [`sentinels/`](./sentinels/) — pick a cell, copy the artifact.

## Engineering actions

Each cell has a directory under [`sentinels/`](./sentinels/) with:

- **Tooling** — what to install or enable.
- **Configuration** — the actual files, snippets, or commands you commit.
- **Verification** — how you confirm the detection is firing on real events.
- **Common mistakes** — failure modes that defeat detection.
- **Citation** — authoritative source.

## Citations

Per-cell citation crosswalk lives in [`CITATIONS.md`](./CITATIONS.md), which carries Covenants citations side-by-side. Sentinels primarily cites NIST CSF 2.0 DE.CM-* (Continuous Monitoring), DE.AE-* (Adverse Event Analysis), and supporting NIST SP 800-92 (Computer Security Log Management). The lethal-trifecta detector at L1 blast-radius cites Simon Willison's June 2025 framing of "private data + untrusted content + external communication" as the forbidden state.
