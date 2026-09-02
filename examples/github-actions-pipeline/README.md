# Example: agent in a CI/CD pipeline

An agent running as a GitHub Actions job, with the credentials the pipeline holds.

The other three examples differ in *where* enforcement lives. This one differs in something sharper: **the constraints are files in the repository the agent can propose changes to.**

## The problem this environment has and the others do not

A workstation agent cannot edit the operator's hooks without touching a machine it does not own. A cluster agent cannot edit the admission policy without RBAC it does not have.

A CI agent's constraints are `.github/workflows/*.yml`, `CODEOWNERS`, and the branch-protection settings. The first two are **files in the repo**. An agent that can open a pull request can propose changing the very rules that bound it, and a pipeline that auto-merges anything green will merge that change.

So the enforcement boundary is not the runner and not the workflow file. **It is the forge.** Branch protection, required reviewers, and environment gates are settings on GitHub's side that a commit cannot alter. Everything in the repo is a proposal; only the forge's settings are a control.

That inverts the usual reading of the matrix. In this environment the workflow YAML is **client-side** even though it runs on GitHub's infrastructure, because it is config the agent can rewrite. The server-side column is the repository settings API.

## The second problem: trusted credentials, untrusted interpreter

The runner is destroyed after every job, so blast radius *inside* it barely matters. What matters is entirely outward: what it can push, deploy, publish, and sign.

A CI agent is an untrusted interpreter holding trusted credentials. Three specific hazards:

| Hazard | Control |
|---|---|
| Default token is write-scoped | An explicit `permissions:` block on every job. The repo-wide default is a setting, not a file, and is often `write-all` |
| Long-lived cloud secrets in the environment | OIDC federation, so the credential is minted per job, scoped, and expires |
| `pull_request_target` running fork code with secrets | Never combine it with a checkout of the PR head. This is the single most exploited Actions pattern |

## What the agent job may and may not do

The rule that makes the rest work: **the agent proposes, the pipeline disposes.**

An agent job writes a branch and opens a pull request. It never pushes to a protected branch, never applies infrastructure, and never publishes an artifact. Those steps are separate jobs gated on a GitHub environment with required reviewers, which is enforced by the forge rather than by the YAML.

That is not a style preference. It is what makes the review gate real: if the agent could apply directly, the gate would be a comment in a file the agent can edit.

## Files here

| File | What it is |
|---|---|
| [`agent-job.yml`](./agent-job.yml) | A constrained agent workflow: minimal permissions, OIDC, timeout, concurrency, PR output only |
| [`verify.sh`](./verify.sh) | Probes the **forge settings**, which are invisible in the repo and drift silently |

Composed from, rather than duplicating:

- [`controls/approval-gating/server-side/CODEOWNERS`](../../controls/approval-gating/server-side/CODEOWNERS), which already reserves `/.github/workflows/` and `/.github/CODEOWNERS` for security review. That entry is the one that closes the loop described above.
- [`controls/approval-gating/server-side/apply-branch-protection.sh`](../../controls/approval-gating/server-side/apply-branch-protection.sh) and [`branch-protection-expected.json`](../../controls/approval-gating/server-side/branch-protection-expected.json).
- [`controls/blast-radius/server-side/iac-gated-pipeline.yml`](../../controls/blast-radius/server-side/iac-gated-pipeline.yml) for the plan and apply split.
- [`controls/supply-chain/server-side/build-and-sign.yml`](../../controls/supply-chain/server-side/build-and-sign.yml) and [`lockfile-integrity.yml`](../../controls/supply-chain/server-side/lockfile-integrity.yml).
- [`sentinels/approval-gating/server-side/audit-branch-protection.yml`](../../sentinels/approval-gating/server-side/audit-branch-protection.yml), which detects the settings drifting back.

## Install order

1. **Branch protection on the default branch**, with `enforce_admins` and required review. Everything else assumes a commit cannot land unreviewed.
2. **CODEOWNERS covering `/.github/`**, so a change to the workflow or to CODEOWNERS itself needs a reviewer the agent is not.
3. **Set the repository default token permission to read**, then grant per job. This is a settings-API change, not a file.
4. **An environment with required reviewers** for anything that acts.
5. **The agent workflow**, last, because it depends on all of the above being true.

Order matters: installing the workflow first gives you an agent job running under whatever the defaults happen to be, which is usually write-all.

## Verification is against the forge, not the repo

```bash
./verify.sh peopleforrester/some-repo
```

Reading the workflow file tells you what the YAML says. It cannot tell you whether the default token is write-scoped, whether admins can bypass review, or whether an environment actually has reviewers attached. Those live in the settings API and are exactly what drifts, because changing them leaves no diff anyone reviews.

## What this example does not solve

- **A compromised Action.** A third-party action pinned by tag is mutable. Pin by commit SHA and see [`framework/BYPASSES.md`](../../framework/BYPASSES.md) for the 2026 corpus, including the Trivy release-pipeline compromise where the scanner was the vector.
- **A malicious maintainer.** Every control here is a setting a repo admin can turn off. `enforce_admins` narrows it; it does not close it.
- **Secrets already leaked.** Scoping and OIDC bound future exposure. A secret that has already left needs rotation, which is outside this repo.
- **Prompt injection through issue or PR text.** An agent triggered by an issue comment is reading attacker-controlled input by design. The bound is what the job's token permits, which is the whole argument for the `permissions:` block. See [`controls/content-integrity/`](../../controls/content-integrity/).
- **Detection.** [`sentinels/approval-gating/server-side/`](../../sentinels/approval-gating/server-side/) watches for the settings being changed back.
