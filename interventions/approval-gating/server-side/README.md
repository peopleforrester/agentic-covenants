# Interventions, Approval gating / Server-side

**Trigger.** Branch protection bypass detected, deployment freeze breach, CODEOWNERS bypass, force-push to a protected branch.

**Authority.** On-call plus security review (changes to approval surfaces themselves are sensitive).

**Speed target.** Under 60 seconds.

## Tooling

- `gh` CLI authenticated as a break-glass identity with `repo_admin` permission.
- A PagerDuty webhook (or equivalent) configured for the `incident-response` team.

## Files in this directory

- [`agent-approval-lockdown-server`](./agent-approval-lockdown-server), runbook script. Locks branch protection to require 4 reviewers, `enforce_admins: true`, `lock_branch: true`. Disables every workflow in the repo. Sets `DEPLOY_FREEZE=true`. Locks every GitHub environment to require the `incident-response` team.
- [`branch-protection-locked.json`](./branch-protection-locked.json), pre-staged branch-protection config applied during the lockdown. **Pre-stage** at `/etc/agents/emergency/branch-protection-locked.json`.
- [`environment-locked.json`](./environment-locked.json), pre-staged GitHub Environment config restricting deployments to the incident-response team. **Pre-stage** at `/etc/agents/emergency/environment-locked.json`.

## Verification

```bash
# 1. Branch protection locked
gh api repos/example-org/agent-config/branches/main/protection \
  --jq '{enforce_admins: .enforce_admins.enabled, lock: .lock_branch.enabled, reviews: .required_pull_request_reviews.required_approving_review_count}'
# expected: enforce_admins: true, lock: true, reviews: 4

# 2. Workflows disabled
gh api repos/example-org/agent-config/actions/workflows --jq '.workflows[] | {name, state}'
# expected: all state: disabled_manually

# 3. Freeze active
gh variable list -R example-org/agent-config | grep DEPLOY_FREEZE
# expected: DEPLOY_FREEZE=true
```

## Common mistakes

- `enforce_admins` set to false in the locked config, the lockdown does not lock admins out.
- Workflow disable applied to wrong repo, emergency triage requires double-checking the `-R` flag.
- Freeze variable set but the apply job does not check it. Verify the workflow reads `vars.DEPLOY_FREEZE`.
- Locking out the incident-response team itself by removing them from the restrictions list.

## Citation

NIST CSF 2.0 RS.MI-01, RS.CO-02; GV.RR-02 (response dimension). EU AI Act Art. 14, Art. 26. NIST AI RMF GOVERN 4.1, MANAGE 4.1. OWASP ASI02, ASI09.
