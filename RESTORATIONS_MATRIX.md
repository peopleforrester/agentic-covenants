# The Agentic Restorations Matrix

A recovery framework for autonomous-agent governance. Three layers of repair, five concerns, fifteen cells. Companion to the [Agentic Covenants Matrix](./MATRIX.md) (Protect), the [Agentic Sentinels Matrix](./SENTINELS_MATRIX.md) (Detect), and the [Agentic Interventions Matrix](./INTERVENTIONS_MATRIX.md) (Respond). Maps to NIST CSF 2.0 **Recover (RC)** function.

## What this is

Where Interventions stops, Restorations rebuilds. The Restorations Matrix is the answer to *how do I get back to a known-good state and not repeat this?* It assumes the agent has been stopped (Interventions has fired) and the incident scope is known (Sentinels has reported). Recovery picks up from there.

The matrix has the same structural shape as Interventions: **the in-agent layer is empty.** An agent that has been stopped does not participate in its own recovery. The agent is the patient, not the surgeon. Recovery is operator-side and infrastructure-side.

## Why recovery is its own matrix and not a checklist appendix

Three reasons:

1. **Recovery has its own bypass surface.** Backups can include the malicious change. "Known-good" sources can already be compromised. Identity rotation can leave stale tokens valid. Each recovery action is a control with failure modes, not a foregone conclusion. The bypass appendix below catalogs the most common ways recovery itself fails.

2. **Recovery has time pressure of a different shape.** Interventions is measured in seconds. Recovery is measured in minutes-to-hours. The pressure is different: not "stop now" but "do not do this badly because mistakes here become permanent." **Restoring from a poisoned backup is worse than running degraded.**

3. **Recovery has the most direct postmortem hook.** The recovery process is when you find out what your prevention layer missed and your detection layer was slow on. Each cell has an implicit "what do I learn from this?" question that feeds back into Covenants v5+1.

## The two axes

### Vertical: where the rebuild happens

1. **In-agent.** Empty. The agent is not part of its own recovery.
2. **Client-side rebuild.** Operator-machine actions: rebuild local hook config from version control, rotate local credentials, reset sandbox image, reinstall agent from a verified source, replay the sequence of trusted operations to bring local state back. Fast (minutes), low blast radius for mistakes.
3. **Server-side restore.** Target-system actions: rebuild RBAC and IAM from declarative source, restore data from immutable backups (verified clean), regenerate ServiceAccounts, re-establish OIDC trust, redeploy from signed images, rebuild network policy, unfreeze deployments. Slower (minutes to hours), higher blast radius for mistakes, but the only way to recover from cluster-level compromise.

### Horizontal: what is being restored

1. **Identity.** Rotate credentials, re-issue per-agent identities, regenerate trust relationships.
2. **Authorization.** Rebuild RBAC and IAM from declarative source. Audit for drift introduced during the incident.
3. **Blast radius.** Restore data, redeploy infrastructure, rebuild from clean state. Verify network policies and resource quotas survived.
4. **Approval gating.** Re-enable branch protection, audit bypass events for forensics, harden gates that were exploited.
5. **Supply chain.** Re-pin dependencies, regenerate SBOMs, re-verify signatures, rebuild from clean source.

## The matrix

| Concern | In-agent (empty) | Client-side rebuild | Server-side restore |
|---|---|---|---|
| **Identity** | (no enforcement) | Delete and regenerate per-agent credential file. Rotate the OIDC client secret if the agent had one. Re-authenticate the operator host to SSO. Confirm filesystem ACLs on credential paths survived (an attacker may have weakened them during the incident). | Disable old ServiceAccount, create new with same name and bindings (forces token rotation). Rotate IAM access keys. Re-establish OIDC trust policy if it was modified. Re-issue SPIFFE identity if cross-cluster. **Verify that the new identity does not inherit residual permissions from the old.** |
| **Authorization** | (no enforcement) | Restore local hook config from version control (`git checkout main -- .claude/`). Verify hook config file ownership returned to operator account. Reapply file ACLs. Reinstall pre-commit hooks. Re-verify Claude Code version is the patched one. | Reapply RBAC Roles and RoleBindings from declarative source. Reapply Kyverno policies. Reapply IAM policies from Terraform / Crossplane / equivalent source-of-truth. **Audit for drift:** anything that exists in the cluster but not in source is suspect. Diff and decide: delete or capture. |
| **Blast radius** | (no enforcement) | Rebuild operator host from a known-good system image if you do not trust that the host itself is clean. Reinstall agent runtime from official source with signature verification. Re-derive seccomp / AppArmor profiles against current workload. Reapply sandbox launchers. | Restore data from immutable backups. **Critically: verify the backup pre-dates the incident.** S3 Object Lock or equivalent ensures the backup itself is unaltered, but you still must pick a backup from before contamination. Redeploy infrastructure from IaC (`terraform plan` against fresh state, then apply). Reapply NetworkPolicy default-deny with explicit allow. Reapply ResourceQuota and LimitRange. Re-create namespace if the namespace itself was scope of damage. |
| **Approval gating** | (no enforcement) | Restore PreToolUse hook config from version control. Reapply tier definitions. Re-enable Auto Mode classifier if it was disabled in response. Re-establish out-of-band confirmation channel. | Re-enable branch protection from saved config. **Confirm `enforce_admins: true`.** Re-add CODEOWNERS approvers. **Audit bypass events from the incident:** if any commits landed via bypass, those must be reviewed for malicious changes. Unfreeze deployments via `gh variable set DEPLOY_FREEZE -b false` only after the rest of recovery is verified. Re-establish required reviewers on every Environment. |
| **Supply chain** | (no enforcement) | Reinstall agent runtime with signature verification. Re-pin MCP server hashes in allowlist (regenerate from clean source, do not copy from possibly-tainted local copy). Re-hash tool descriptions on first connection. Regenerate lockfiles from declared dependencies and re-pin. Run pip-audit / npm audit / Trivy on the rebuilt environment. | Rebuild and re-sign agent images from source. Regenerate SBOMs with current vulnerability data. Re-establish cosign signing key (**if the key may have been exposed during the incident, rotate the signing key entirely**). Force redeploy with new SHA pins. Re-establish image-registry admission policies. Re-establish egress NetworkPolicy with current MCP domain allowlist. |

## How to use this as a runbook

Each cell has an associated rebuild script. **The order matters:** identity first, then authorization, then blast radius, then approval gating, then supply chain.

- **Identity first** because every later step authenticates against an identity. If the identity is compromised, every later restore inherits the compromise.
- **Authorization second** because restoring data into a permission environment that still allows the attacker is restoring the attack.
- **Blast radius third** because the data and workloads need to land into a known-good identity and authorization environment.
- **Approval gating fourth** because re-enabling gates before the rebuild is complete creates a window where legitimate recovery operations are blocked.
- **Supply chain last** because rebuilding from a clean source assumes the rest of the stack is ready to receive the rebuild.

For each cell, the runbook should answer:

1. **Precondition.** What must already be done (Interventions complete, scope known, backups verified).
2. **Steps.** The literal commands and expected output.
3. **Verification.** How you confirm the rebuild is healthy and not still tainted.
4. **Exit criteria.** What state lets you move to the next cell.

## Recovery is the right time to fix prevention

Every successful incident exposes which Covenants cells failed. The Restorations runbook should produce a follow-up action list:

- Which prevention control was bypassed?
- Was the bypass in [`BYPASSES.md`](./BYPASSES.md), or new?
- What change to Covenants prevents this class in the future?

If recovery does not feed back into prevention, the org is treating each incident as a one-off and accepting that the same class of attack will work again.

## Forensic preservation comes first

If you start restoring before forensic preservation, you destroy the evidence that tells you what happened. **Document a hold-and-image step at the top of every recovery runbook.** If the incident is going to be investigated by law enforcement or external IR, preserving evidence (memory dumps, disk images, log archives) takes priority over rebuilding speed.

## What this matrix deliberately does not cover

- **Postmortem and learning loop.** Technical recovery is necessary but not sufficient. The blameless postmortem is a separate organizational practice.
- **Customer communication and incident disclosure.** Legal, PR, and customer-success have their own runbooks.
- **Data-subject notification under GDPR, CCPA, or similar.** Privacy-incident response has regulatory-specific timelines.
- **Insurance claim filing.** Cyber-insurance often has 24- or 48-hour reporting requirements.

## Where this matrix sits

Restorations is the fourth and last operational matrix:

- Covenants (Protect, NIST CSF 2.0 PR): what binds the running agent
- Sentinels (Detect, NIST CSF 2.0 DE): what watches the running agent
- Interventions (Respond, NIST CSF 2.0 RS): what stops the running agent
- **Restorations (Recover, NIST CSF 2.0 RC): what fixes after the agent ← this document**

The pre-engagement order is Sentinels → Interventions → Restorations. The feedback order is **Restorations → Covenants**. Recovery is where prevention learns.

## Reading order

1. This document: the framework essay.
2. [`docs/walkthrough-agentic-restorations-engineering-actions-v5.md`](./docs/walkthrough-agentic-restorations-engineering-actions-v5.md), engineering-actions companion (gitignored).
3. [`restorations/`](./restorations/), pick a cell, run the rebuild script.

## Citations

NIST CSF 2.0 RC.RP-* (Recovery Plan), RC.IM-* (Improvements), RC.CO-* (Communications). NIST SP 800-61 Rev. 2 (Computer Security Incident Handling Guide). NIST SP 800-34 Rev. 1 (Contingency Planning). NIST AI RMF MANAGE 4.1. EU AI Act Articles 14 and 26. Per-cell crosswalk in [`CITATIONS.md`](./CITATIONS.md) (restorations section to be added).
