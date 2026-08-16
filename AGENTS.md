# agentic-covenants

_Repo context file for AI coding CLIs (Claude Code, Codex, OpenCode, Gemini, etc.). Mirrors the human-facing [`README.md`](./README.md)._

## What this is

A practitioner framework for autonomous-agent governance: **six matrices mapped to the six NIST CSF 2.0 functions**, each with working artifacts in every populated cell. Charter (Govern) authorizes → Inventory (Identify) tracks → Covenants (Protect) binds → Sentinels (Detect) watches → Interventions (Respond) stops → Restorations (Recover) rebuilds. Every matrix is five concerns (identity, authorization, blast-radius, approval-gating, supply-chain) × three layers.

This is **not** a code project. There is no build, no test suite, no package manifest. The deliverables are Markdown (framework essays, per-cell READMEs, citations) and copy-ready **template artifacts** (Kubernetes/Kyverno YAML, RBAC, seccomp/AppArmor profiles, PreToolUse hooks, Terraform, cosign policies, Falco/Sigma rules, runbook shell scripts). Placeholders like `agent-claude-prod`, `123456789012`, and `sha256:REPLACE_WITH_DIGEST` are intentional. They are meant to be substituted by the person adopting a cell.

## Stack

Markdown + YAML + shell + a little Python/Terraform/Rego, all as **illustrative templates**. No runtime, no dependency tree (so Dependabot has nothing to scan). Machine-readable matrix data lives in the `*.yaml` files at the root (`matrix.yaml`, `sentinels.yaml`, etc.).

## Layout

- `MATRIX.md` / `SENTINELS_MATRIX.md` / `INTERVENTIONS_MATRIX.md` / `RESTORATIONS_MATRIX.md` / `CHARTER_MATRIX.md` / `INVENTORY_MATRIX.md`, the six framework essays.
- `BYPASSES.md`, per-control bypass surface + the running 2026 incident/CVE corpus.
- `CITATIONS.md`, per-cell crosswalk to NIST / OWASP / ISO / EU AI Act.
- `controls/ sentinels/ interventions/ restorations/ charter/ inventory/`, one directory per matrix, mirroring the five-concern × three-layer grid.
- `docs/`, gitignored working notes / source walkthroughs (never published).

## Commands

- **Build / Test / Lint:** none. This repo has no test suite by design; do not scaffold one.
- **Preview Markdown:** any Markdown viewer; the matrices are GitHub-flavored tables.

## Conventions

- **Currency is the product.** This framework's value is being correct as of *now*. Any version pin, framework citation, regulatory date, or "X is deprecated / does not exist" claim is high-stakes: verify against a live primary source with a dated citation before writing it. Do not trust training data for versions or deprecation status. When in doubt, check the `mrf-knowledge` research spikes first, then the vendor's own docs.
- **In-agent cells are advisory by thesis.** In Interventions and Restorations the in-agent (L1) cells are deliberately *empty*; in Covenants/Sentinels they are explicitly "nudge, not control." Do not "fill them in" with enforcement claims, that inverts the framework's whole argument.
- **Artifacts are templates, not deployments.** Keep the `REPLACE_WITH_*` placeholders and the "resolve with crane / substitute your ARN" comments. Never insert real account IDs, hostnames, or secrets.
- **Prose style:** no em-dashes; no aphoristic closing lines; avoid reflexive rule-of-three. Match the terse, evidence-first voice of the existing cell READMEs.
- **Git workflow:** work on `staging`, commit there, then promote to `main` (see `/ship`). Commit messages are plain technical descriptions, no AI attribution.
- **Don't touch:** `docs/` (gitignored source material), and don't commit `transcripts/` or `claude-ai-context/` (local-only, gitignored).

_Seeded 2026-07-10; filled in 2026-07-21._
