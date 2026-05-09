# Restorations — Approval gating / Server-side

**Precondition.** Interventions L3-C4 has fired (branch protection locked, workflows disabled, DEPLOY_FREEZE engaged, environments locked). Restorations identity, authorization, and blast-radius rows complete.

**Authority.** On-call plus security review.

## Tooling

- `gh` CLI authenticated with `repo_admin`.
- The branch-protection JSON in source: `controls/approval-gating/server-side/branch-protection-expected.json`.

## Files in this directory

- [`agent-restore-approval-server`](./agent-restore-approval-server) — runbook script. Restores branch protection from source (verifies `enforce_admins: true`), re-enables every workflow, audits bypass events from the incident window, unfreezes deployments **only when explicitly authorized** via the `--unfreeze` flag.
- [`audit-bypass-events.sh`](./audit-bypass-events.sh) — helper that lists every push to a protected branch during the incident window with `forced: true` or admin-bypass markers. Output must be reviewed manually before declaring approval-gating recovered.

## Verification

```bash
# 1. Branch protection restored from source-of-truth
gh api repos/$REPO/branches/main/protection \
  --jq '{enforce_admins: .enforce_admins.enabled, reviews: .required_pull_request_reviews.required_approving_review_count}'
# expected: enforce_admins: true, reviews: 2

# 2. Workflows re-enabled
gh api repos/$REPO/actions/workflows --jq '.workflows[] | {name, state}' | grep -v "disabled_manually"

# 3. DEPLOY_FREEZE off (only after the rest of recovery verified)
gh variable list -R $REPO | grep DEPLOY_FREEZE
# expected: DEPLOY_FREEZE=false

# 4. No bypass events found unreviewed during incident window
./audit-bypass-events.sh "$INCIDENT_START_TIMESTAMP" "$INCIDENT_END_TIMESTAMP"
```

## Common failure modes

- Protection config not version-controlled; restored from incomplete copy. The expected JSON must live at `controls/approval-gating/server-side/branch-protection-expected.json`.
- Bypass events during incident not reviewed. **Any commit that landed via bypass during the incident window is suspect.** Audit each one for malicious changes before the cleanup is complete.
- DEPLOY_FREEZE unfrozen before recovery complete. The runbook requires `--unfreeze` as an explicit flag rather than unfreezing by default.

## Citation

NIST CSF 2.0 RC.RP-01, RC.IM-01; GV.RR-02 (recovery dimension). NIST AI RMF GOVERN 4.1, MANAGE 4.1. OWASP ASI02, ASI09. EU AI Act Art. 14, Art. 26.
