# Sentinels

Detection artifacts for every cell of the [Agentic Sentinels Matrix](../SENTINELS_MATRIX.md). Companion to [`controls/`](../controls/).

## Layout

```
sentinels/
├── identity/{in-agent,client-side,server-side}/
├── authorization/{in-agent,client-side,server-side}/
├── blast-radius/{in-agent,client-side,server-side}/
├── approval-gating/{in-agent,client-side,server-side}/
└── supply-chain/{in-agent,client-side,server-side}/
```

The structure mirrors `controls/` exactly. The layer named "client-side" detects what the client-side controls in `controls/` enforce. The layer named "server-side" detects what the server-side controls enforce. This makes it easy to walk both matrices for a single concern in one pass.

## What each cell directory contains

Every cell directory has the same six-section README:

1. **Control.** One-line summary from [`SENTINELS_MATRIX.md`](../SENTINELS_MATRIX.md).
2. **Tooling.** What to install or enable (Vector, Fluent Bit, Falco, Cilium Hubble, auditd, bpftrace, GitHub webhooks, ...).
3. **Files in this directory.** Hook scripts, audit policies, Falco rules, SIEM detection rules.
4. **Verification.** How you confirm the detection fires on real events.
5. **Common mistakes.** Failure modes that defeat detection.
6. **Citation.** From [`CITATIONS.md`](../CITATIONS.md).

## Two principles

These come from the matrix; repeating them here because they govern every cell:

1. **Every detection must have a defined response.** Alerts without runbooks are theatre. Where Sentinels detects something, [Interventions Matrix] should have a runbook keyed to the alert.
2. **Detection has false-positive cost.** Tune thresholds against your traffic; the defaults in these artifacts are starting points, not production-ready values.

## Order of operations (rollout)

The companion engineering-actions document recommends a four-week rollout, server-side-first:

- **Week 1.** K8s audit logs, CloudTrail with Object Lock, SIEM ingestion pipeline, Kyverno PolicyReports, GitHub branch-protection webhooks.
- **Week 2.** Falco, Cilium Hubble flow export, ResourceQuota Prometheus alerts, daily SBOM-diff job.
- **Week 3.** Hook decision logger, identity-fingerprint logger, approval-timing logger, Vector/Fluent Bit on every operator host.
- **Week 4.** bpftrace/Falco userspace on operator hosts, MCP allowlist violation logger, lockfile-diff CI extension.

If you have no log aggregation, build that first. Detection without aggregation does not scale past one host.

## A note on the in-agent layer

The in-agent cells are deliberately thin. The agent-runtime layer is forensic-only — useful after the fact when you have a remote sink, but not real-time detection. The lethal-trifecta detector is the one exception, and it is implemented at the wrapper layer (`controls/` or `sentinels/` depending on whether you treat it as prevention or detection), not in the agent.
