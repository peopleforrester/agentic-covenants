# Sentinels — Approval gating / Server-side

**Control.** GitHub webhook for branch-protection bypass and force-push events. Hourly drift-detection job comparing live branch protection to a checked-in expected JSON. Deployment-freeze breach alerts. Audit log on changes to branch protection itself.

**Strength.** Deterministic. Failure modes: webhook secret not set or not verified (anyone can spoof events to the SIEM); audit cron at 24h interval (a bypass-then-restore cycle goes undetected); expected protection JSON not version-controlled (drift detection uses a stale baseline); webhook receiver discards push events with `forced: false` even though `--force-with-lease` still bypasses required review.

## Tooling

- GitHub webhook target (Lambda or service that verifies HMAC signatures).
- A scheduled GitHub Actions workflow for hourly drift detection.
- A SIEM that accepts JSON events.

## Files in this directory

- [`webhook-receiver.py`](./webhook-receiver.py) — Lambda-style handler that verifies the webhook signature, then ships filtered events (`branch_protection_rule.deleted|edited`, force-pushes, branch deletions on protected branches) to the SIEM.
- [`audit-branch-protection.yml`](./audit-branch-protection.yml) — hourly GitHub Actions workflow that fetches the live branch protection and diffs against [`../../../controls/approval-gating/server-side/branch-protection-expected.json`](../../../controls/approval-gating/server-side/branch-protection-expected.json). Drift fires a SIEM event.
- [`freeze-breach-step.yml`](./freeze-breach-step.yml) — drop-in workflow step (snippet) for the IaC apply job that posts a SIEM event when an apply attempts to run while `DEPLOY_FREEZE=true`.

## Verification

```bash
# 1. Webhook receives a force-push event
git push --force-with-lease origin main:test-branch
# expected: SIEM receives event within seconds

# 2. Audit job detects drift
gh api -X PUT repos/:owner/:repo/branches/main/protection -F enforce_admins=false   # introduce drift
# Wait for next hourly run; SIEM should receive branch_protection_drift event
gh api -X PUT repos/:owner/:repo/branches/main/protection -F enforce_admins=true    # restore

# 3. Freeze breach alert
gh variable set DEPLOY_FREEZE -b true
# Trigger an apply via PR merge; SIEM gets freeze_breach_attempt
gh variable set DEPLOY_FREEZE -b false
```

## Common mistakes

- Webhook secret not set or not verified — anyone can spoof events.
- Audit cron at 24h interval. Bypass-then-restore goes undetected.
- Expected protection JSON not version-controlled. Drift detection uses a stale baseline.
- Webhook receiver discards push events with `forced: false`. `--force-with-lease` is also a bypass and presents differently.

## Citation

NIST CSF 2.0 DE.CM-09, DE.AE-02, GV.RR-02. EU AI Act Art. 14 (human oversight obligations).
