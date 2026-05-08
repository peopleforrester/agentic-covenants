# The Agentic Sentinels Matrix

A detection framework for autonomous-agent governance. Companion to the [Agentic Covenants Matrix](./MATRIX.md). Three layers, five concerns, fifteen cells. Designed to be walked left-to-right by a platform engineer asking one question per row: *if this concern is breached, how do we know?*

## What this is

The **Detect** view of agent governance, mapped to NIST CSF 2.0 DE.* and DE.AE.* subcategories. While the Covenants Matrix names the controls that prevent a violation, the Sentinels Matrix names the controls that surface a violation — preferably in real time, at minimum forensically.

## What this is not

This is not a prevention framework (that is the Covenants Matrix). This is not a response framework (that is Interventions, tracked separately). This is not a recovery framework (that is Restorations, tracked separately).

**Detection without prevention is a notification service.** The Sentinels Matrix exists alongside Covenants, not instead of it. Falco rules that page someone three seconds after the database is dropped do not protect the database; they protect the people whose job is to respond. Build prevention first. Build sentinels to catch what prevention misses.

## Two principles before the cells

1. **Every detection must have a defined response.** Sentinels alerts that do not page someone or trigger an Interventions runbook are theatre. Build the alert and the runbook together.
2. **Detection has false-positive cost.** Anthropic's Auto Mode reports an 8.5% first-stage classifier rate. Acceptable when the false-positive cost is "ask a human." Unacceptable when the false-positive cost is "page the on-call at 3am." A SIEM rule with 8.5% FP at 10,000 events/day is 850 unnecessary pages. Tune.

## The two axes

### Vertical: where detection happens

1. **In-agent (forensic only, not real-time).** Transcript and tool-call logs from the agent runtime. Useful after the fact. The agent can edit its own forensic record if logs are local-only; ship to a remote sink. The lethal-trifecta detector at the wrapper layer is the only L1 control with real-time detection value, and it is implemented at the wrapper, not in the agent.

2. **Client-side hooks.** auditd, eBPF, hook decision logs, MCP allowlist violation logs, lockfile diff in CI logs. Runs on the operator's machine or in the agent's execution context. Can be made tamper-evident if logs ship to a remote sink owned by the operator account, not the agent's.

3. **Server-side.** Kubernetes audit logs, CloudTrail, Falco, Hubble flow events, Kyverno PolicyReports, GitHub branch-protection-bypass webhooks. Runs on the target system. Authoritative and external to the agent's compromise model.

### Horizontal: what is being detected

The five concerns mirror the Covenants Matrix exactly:

1. **Identity.** Identity used outside expected hours, source IP, or by an unexpected principal.
2. **Authorization.** Hook denial events, RBAC denials, IAM Access Analyzer findings, OPA decision logs.
3. **Blast radius.** Sandbox boundary events, network attempts on `--network none` agents, NetworkPolicy denials, ResourceQuota near-limit alerts, VPC Flow Log REJECTs.
4. **Approval gating.** Hook decision-log timing analysis (alert-fatigue patterns), branch-protection bypass events, deployment-freeze breach attempts, drift in branch protection itself.
5. **Supply chain.** MCP allowlist violation events, lockfile diff, tool-description hash mismatch, image-pull events with signature status, SBOM diff over time, cosign verification failures.

## The matrix

| Concern | In-agent (forensic) | Client-side hooks | Server-side enforcement |
|---|---|---|---|
| **Identity** | Tool-call logs include credential fingerprint (hash, never the token); session correlation. | PreToolUse hook emits structured identity events; auditd watches agent process startup; Vector/Fluent Bit ships to SIEM. | K8s audit log captures every agent SA action; CloudTrail with Object Lock; SIEM rules on out-of-hours, unexpected source IP, identity reuse across agents. |
| **Authorization** | Tool descriptions logged with each call (forensic). | Hook decision events (allow/ask/deny/error); auditd watches hook config edits and `--no-verify` flag; SIEM rule for multi-deny patterns. | RBAC denial events from K8s audit; IAM Access Analyzer findings; Kyverno PolicyReports; OPA decision logs centralized. |
| **Blast radius** | Forensic only; sandbox events do not surface in-agent. | bpftrace or Falco userspace catches unsandboxed children, sandbox EPERM events, unexpected network attempts; correlates by session ID. | Falco runtime rules for shells in agent containers and writes to sensitive paths; Cilium Hubble drops; ResourceQuota near-limit Prometheus alert; VPC Flow Log REJECTs. |
| **Approval gating** | Confirmation-prompt usage forensically logged. | Approval-timing analysis surfaces alert-fatigue (response < 2s across > 50 approvals); typed-confirmation mismatch events; out-of-band channel decisions joined to session. | GitHub webhook for branch-protection bypass; hourly drift-detection job comparing live protection to expected JSON; deployment-freeze breach alerts; audit on changes to branch protection itself. |
| **Supply chain** | "Where did this dependency come from" forensically traceable through tool-call log. | MCP allowlist violation events; tool-description hash mismatch alerting; lockfile diff in CI logs centralized; pre-commit dependency scan results. | Image-pull events with signature verification status; SBOM diff over time per workload; cosign verification failures as alert source; egress NetworkPolicy denials when agents try to reach non-allowlisted MCP domains. |

## How to walk it

Pick a concern. Walk the row left to right. For each cell, ask:

> If this concern is breached, how do we know?

Three test outcomes:

- **All three cells populated:** the concern is observable across all layers. In-agent surfaces the call that violated; client-side surfaces the deterministic decision; server-side surfaces the consequence at the target. None of the layers alone reconstructs the incident; the stack does.
- **Server-side cell populated, client-side empty:** the consequence is detected, but you cannot reconstruct the agent's reasoning. Forensic blind spot. Add the client-side cell.
- **Client-side cell populated, server-side empty:** the agent's intent is logged, but you cannot tell whether the action actually reached the target. Add the server-side cell.

Some cells legitimately stay empty (the in-agent column is forensic-only by design; treating it as a control would be miscalibration). Document empty cells in the threat model.

## What sits next to this matrix (deliberately separate)

- **Covenants Matrix** ([`MATRIX.md`](./MATRIX.md)). Prevention. The first pass of defense. Sentinels is what catches what Covenants misses.
- **Interventions Matrix.** One-button credential revocation, session termination, kill switches, rollback automation. Activates after Sentinels fires.
- **Restorations Matrix.** Backup restoration, GitOps `git revert`, postmortem and learning loop.

## Reading order

1. This document — framework essay.
2. [`docs/walkthrough-sentinels-engineering-actions-v1.md`](./docs/walkthrough-sentinels-engineering-actions-v1.md) — engineering actions companion (gitignored; lives in operator working notes).
3. [`sentinels/`](./sentinels/) — pick a cell, copy the artifact.

## Engineering actions

Each cell has a directory under [`sentinels/`](./sentinels/) with:

- **Tooling** — what to install or enable.
- **Configuration** — the actual files, snippets, or commands you commit.
- **Verification** — how you confirm the detection is firing on real events.
- **Common mistakes** — failure modes that defeat detection.
- **Citation** — authoritative source.

## Citations

Per-cell citation crosswalk lives in [`CITATIONS.md`](./CITATIONS.md), which carries both Covenants and Sentinels citations side by side. Sentinels primarily cites NIST CSF 2.0 DE.CM-* (Continuous Monitoring), DE.AE-* (Adverse Event Analysis), and supporting NIST SP 800-92 (Computer Security Log Management).
