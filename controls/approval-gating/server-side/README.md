# Approval gating / Server-side

**Control.** Branch protection requiring PR review. CODEOWNERS on critical paths. Multi-party approval on prod merges. IaC pipeline runs `plan` only; separate gated job runs `apply`. Deployment freezes during incident windows enforced by pipeline, not policy. **"Do not allow bypassing the above settings"** must be enabled.

**Strength.** Deterministic. Bypass requires admin-override (which `enforce_admins=true` blocks), collusion between two reviewers, social-engineering through a persuasive PR description, or paths not covered by CODEOWNERS.

## Tooling

- GitHub branch protection rules (or GitLab protected branches, or Bitbucket equivalents).
- A CODEOWNERS file in `.github/CODEOWNERS` (or `docs/CODEOWNERS`, or `CODEOWNERS` at root).
- GitHub environments with required reviewers (configured against the IaC pipeline's `apply` job from [`../../blast-radius/server-side/iac-gated-pipeline.yml`](../../blast-radius/server-side/iac-gated-pipeline.yml)).
- A deployment-freeze automation: PagerDuty event hook or a cron-driven config flip.

## Files in this directory

- [`apply-branch-protection.sh`](./apply-branch-protection.sh), wraps the `gh api` call that sets every branch-protection field correctly. Run once per repo. The script asserts `enforce_admins=true` and refuses to apply without it.
- [`branch-protection-expected.json`](./branch-protection-expected.json), declarative target state for branch protection. The detection job in [`../../../sentinels/approval-gating/server-side/`](../../../sentinels/approval-gating/server-side/) compares this to the live state and alerts on drift.
- [`CODEOWNERS`](./CODEOWNERS), template CODEOWNERS file. Drop at `.github/CODEOWNERS` and substitute team names.
- [`freeze.yml`](./freeze.yml), workflow that polls PagerDuty every minute and sets the `DEPLOY_FREEZE` repo variable. The `apply` job in the IaC pipeline reads the variable and refuses to run when true.

## Verification

```bash
# 1. Confirm enforce_admins (the load-bearing flag)
gh api repos/peopleforrester/agentic-covenants/branches/main/protection \
  --jq '.enforce_admins.enabled'
# expected: true

# 2. Confirm required reviews and CODEOWNERS
gh api repos/peopleforrester/agentic-covenants/branches/main/protection/required_pull_request_reviews \
  --jq '{count: .required_approving_review_count, codeowners: .require_code_owner_reviews}'
# expected: count >= 2, codeowners: true

# 3. Confirm bypass is not allowed
# Open a PR as an admin without approvals and try to merge:
gh pr merge --admin
# expected: failure ("required pull request review")

# 4. Confirm freeze actually freezes
gh variable set DEPLOY_FREEZE -b true
# (next apply run skips with "Deployment freeze active")
gh variable set DEPLOY_FREEZE -b false
```

## Common mistakes

- `enforce_admins: false` (the GitHub default historically). Anyone with admin role on the repo walks through every other rule. **The most common branch-protection failure.**
- CODEOWNERS file in the wrong path. Must be at `.github/CODEOWNERS`, `docs/CODEOWNERS`, or `CODEOWNERS` at root. Anywhere else is treated as data, not code-ownership.
- Required reviewers count of 1. One reviewer plus the agent operating the keyboard equals zero adversarial review.
- Freeze controlled by a UI toggle that the on-call engineer can flip. The freeze should require a PR to disable.
- Required status checks named in protection but never wired up in CI; the rule passes vacuously because the check never runs.

## Citation

NIST CSF 2.0 PR.AA-05 (least privilege, separation of duties), PR.PS-01, GV.RR-02. NIST AI RMF GOVERN 4.1 (organizational practices supporting AI risk management), MANAGE 4.1. OWASP LLM06. OWASP ASI02, ASI03. EU AI Act Art. 14 (human oversight), Art. 26 (deployer obligations). ISO/IEC 42001 §A.4. NIST SP 800-160 Vol. 1 (separation of duties as a security principle).
