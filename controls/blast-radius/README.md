# Blast radius

**Intent.** One bad action stays contained. The agent should not be able to take down a service it didn't intend to touch, exhaust a shared resource, or reach a network endpoint outside its declared dependency surface. When something goes wrong, the damage is bounded by deliberate engineering, not by the agent's restraint.

## The row, at a glance

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Refusal-language template. Verified-bypassable in Kiro, Replit, and DataTalks.Club incidents. Listed for completeness; do not rely on it. |
| Client-side | [`client-side/`](./client-side/) | Sandbox at process launch with inheritance enforcement: bubblewrap (Linux), Seatbelt (macOS), gVisor (containerized). Seccomp or AppArmor profile. `--network none` plus a unix-domain-socket egress proxy when network is needed. Read-only mounts on operator data. |
| Server-side | [`server-side/`](./server-side/) | Gated IaC apply pipeline as the actual backstop. NetworkPolicy default-deny with explicit allowlist. ResourceQuota and LimitRange per namespace. Immutable backups with separate credentials. Cross-account separation. PodDisruptionBudget on critical workloads. |

## Why it matters

Blast radius is the row that turns a near-miss into a contained incident. If identity and authorization were perfect, blast radius would be redundant. They aren't, so it isn't.

The Kiro incident, the Replit incident, the DataTalks.Club incident — every one of them had identity and authorization failures upstream. What made them survivable (or not) was whether blast radius was contained. Where it was, the recovery was a `git revert` and a postmortem. Where it wasn't, it was a database restore, a customer-facing announcement, and a board call.

## How to walk it

For each layer ask: *if the agent does the wrong thing, how much can break before it stops?*

- **In-agent only:** the answer is "as much as the model fails to refuse." Verified to be a lot.
- **Client-side adds:** the agent runs inside a sandbox; it cannot reach the host filesystem outside its workspace, cannot make arbitrary network calls, cannot spawn unsandboxed children. Bypass requires a sandbox config gap, a kernel-level escape (rare), or a parent that fails to enforce inheritance.
- **Server-side adds:** even an agent that escapes its sandbox is rejected at admission, capped by quota, fenced by NetworkPolicy, and unable to mutate immutable backups. Bypass requires multiple simultaneous server-side failures.

## A note on `prevent_destroy` (Terraform)

`prevent_destroy` is a lifecycle metadata flag. It is bypassable: the agent edits the `.tf` file to remove the lifecycle block and runs `terraform apply` in the same cycle. **It is not a control.** It is effective only when paired with the gated apply pipeline ([`server-side/iac-gated-pipeline.yml`](./server-side/iac-gated-pipeline.yml)) where the apply job requires human review of the plan.

## Citations (per layer)

See [`../../CITATIONS.md`](../../CITATIONS.md). Quick reference:

- **In-agent**: advisory; thematically MAP 5.1, MEASURE 2.6 (safety risks evaluated); OWASP LLM06; OWASP ASI02, ASI05.
- **Client-side**: NIST CSF 2.0 PR.PS-01, PR.PS-05, PR.PS-06, PR.IR-01; OWASP LLM05, LLM10; OWASP ASI05; NIST SP 800-160 Vol. 1 (defense in depth).
- **Server-side**: NIST CSF 2.0 PR.IR-01 through PR.IR-04, PR.DS-11 (backups); OWASP LLM10 (Unbounded Consumption); OWASP ASI05, ASI08 (Cascading Failures); NIST SP 800-160 Vol. 1; NIST SP 800-34 Rev. 1 (contingency planning).
