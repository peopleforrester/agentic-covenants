# Bypasses

The matrix makes a defense-in-depth argument. That argument requires honesty about each layer's bypass surface. None of these bypasses invalidate the matrix. They explain why the matrix has three columns instead of one.

If a layer here lacks a bypass entry, that's a documentation gap, not a hardness claim. File an issue.

## In-agent

### Model instructions and refusals

- Prompt injection (direct and indirect).
- Jailbreak.
- Novel framing the model has not been trained to refuse.
- Model error: the same prompt produces different outputs across calls.
- Tool-description manipulation through upstream content (a malicious doc the agent ingests redefines what `delete_user` does).
- The structural absence of homeostatic stake, pre-action pause, and second-order learning means the layer cannot be made reliable by better prompting. The bypass is the architecture, not a bug.

**Treat as nudge, not control.**

## Client-side

### Per-agent credentials in config

- Token theft if the filesystem is accessible to other processes.
- Credential leakage in logs, process listings (`ps -ef`), or environment exports.
- World-readable env files (`chmod 644 .env`).
- Token reuse across machines if the operator copies the config.

### User-agent string identity

- Spoofable by the client itself.
- Logging convenience only. **Not a control.**

### `--allowedTools` allowlist

- Shell-out to non-allowlisted commands through an allowlisted shell tool (e.g., `Bash` allowed but used to invoke things you didn't allowlist directly).
- Bypass if the agent can edit its own config and start a new session.
- Pattern matching on tool names misses semantically equivalent tools (e.g., allowlist blocks `kubectl` but allows `kubectl-cnpg`).

### PreToolUse pattern hooks

- Command obfuscation: base64-encoded payloads, `eval`, env-variable indirection, write-payload-to-tmpfile-and-execute.
- Equivalent commands not in the pattern list:
  - `find /target -delete` instead of `rm`.
  - `kubectl scale --replicas=0` instead of `kubectl delete`.
  - `TRUNCATE` instead of `DROP TABLE`.
  - Editing `.tf` files instead of running `terraform destroy`.
  - `dd if=/dev/zero of=$file` instead of `rm`.
- Hook bypass if the hook script is on a path the agent can write to.
- Race condition if the hook timeout is short enough to skip via `sleep`.

### Pre-commit hooks

- `git commit --no-verify`.
- `git config core.hooksPath /dev/null`.
- `rm .git/hooks/*` if filesystem write is allowed.
- Bypassing git entirely via filesystem APIs (commit objects written directly).
- `git -c core.hooksPath=/dev/null commit`.

### Sandbox (Seatbelt, bubblewrap, gVisor)

- Spawning unsandboxed children when inheritance is not enforced at launch.
- Sandbox configuration gaps (missed syscall, allowed network range, leaked file descriptor).
- Kernel-level escape (rare but documented for each sandbox technology).
- Sandbox not applied to agent-spawned subprocesses if the launcher does not propagate.

### Seccomp or AppArmor profile

- Profile gaps: missing syscall not in the deny list.
- Profile not applied to spawned children.
- Profile not loaded at agent launch (race window).
- Mount namespace escape if not joined.

### Lockfile pinning

- Only effective if a server-side step validates lockfile integrity.
- An agent that can edit `package-lock.json`, `requirements.txt`, `Pipfile.lock`, `go.sum`, or `Cargo.lock` can pin malicious versions.
- Lockfile rewrite during install (some package managers regenerate on install if the manifest changed).

### MCP server allowlist

- Bypass if the agent can write to the allowlist config.
- Bypass via direct API calls outside the MCP protocol (curl).
- Stale allowlist hash if the MCP server publishes a new version that gets blindly approved.
- Trust on first use without subsequent re-verification.

## Approval gates (both client- and server-side)

### Tiered approval and human-in-the-loop confirmation

This control's primary failure mode is **alert fatigue**: reviewers approve reflexively after enough repetitions. The same failure mode is documented in:

- 2FA push prompts (Microsoft, Cisco Duo telemetry).
- Medical alert systems (Joint Commission Sentinel Event reports).
- GDPR consent flows (cookie-banner click-through rates).
- Code review on large PRs (the bigger the diff, the lower the per-line scrutiny).

Effectiveness degrades over time without rotation, sampling, threshold review, or signal-to-noise tuning.

- Tiered approval (auto-approve trivial, quick-confirm routine, typed confirmation for tier-3, out-of-band channel for highest-tier) reduces but does not eliminate the failure mode.
- Flat approval workflows degrade fastest.
- Judgment-query escalation, where the agent only escalates genuinely novel decisions, is more fatigue-resistant but has limited tooling support as of May 2026.

Pattern-matched gating also fails on equivalent commands. See PreToolUse bypass section.

## Server-side

### `prevent_destroy` lifecycle (Terraform)

- Agent edits `.tf` to remove the lifecycle block and runs `terraform apply` in the same cycle.
- Only effective when paired with a gated apply pipeline that prevents the change from reaching production.
- State drift if the resource was created without the lifecycle block originally.

### RBAC Roles

- Privilege escalation through `escalate`, `bind`, impersonation, or aggregated roles missed by the policy author.
- Subresource access not denied (e.g., denying `pods` but not `pods/exec` or `pods/portforward`).
- API surface gaps where REST is denied but gRPC, CRD-derived APIs, or aggregated API servers are allowed (or vice versa).
- ClusterRole granted on a "scoped" RoleBinding that the operator forgot to scope.

### IAM scoped policies

- Token theft (compromised metadata service, exposed env, leaked logs).
- IAM condition logic bugs (missing `aws:RequestTag` clauses, wildcard string matches).
- Cross-service trust paths missed by the policy author (e.g., `iam:PassRole` to a more-privileged role).
- Policy size limits forcing operator to use `*` to fit (a real failure mode in AWS).

### Kyverno or OPA admission policies

- Logic bugs. Rule misses a case.
- Subresource not covered (`pods/exec`, `services/proxy`).
- Policy applied to wrong namespace (label-selector mismatch).
- Mutating-versus-validating ordering errors.
- Policy bypass via `kubectl --dry-run=client` then `--dry-run=none` race.
- Webhook timeout failure-open (default for some configurations).

### Branch protection plus PR review

- Operator manipulation through persuasive PR description influenced by agent output.
- Collusion between two reviewers.
- Review fatigue on large PRs.
- Force push to release branch by an operator with admin override.
- Bot accounts approving on behalf of operator (CODEOWNERS misconfigured).

### CODEOWNERS

- Paths not covered by the CODEOWNERS file.
- PR touching both protected and unprotected paths if the owner check is per-file rather than per-PR (depends on platform).
- Stale owner team after a reorg.

### Image signature verification (cosign)

- Compromise of signing infrastructure (KMS key theft, OIDC trust path).
- Signature stripping at a registry mirror that the policy doesn't verify.
- Policy misconfigured to allow unsigned images in some namespaces (the "tools" namespace exception).
- Trust on signed-but-malicious images (signature verifies provenance, not safety).

### Egress NetworkPolicy

- Rule misconfiguration (forgot to deny `kube-system` egress).
- CNI plugin bugs.
- Overlay bypass (host network pods).
- DNS exfiltration if DNS resolution is allowed without filtering.
- Service-mesh sidecar bypass.

### OIDC federation plus bound tokens

- IdP compromise.
- Token replay within the TTL window.
- Misconfigured trust policy that accepts tokens from unintended issuers.
- Audience mismatch tolerated by relying party.

---

## What this list is for

When you populate a cell, you are buying the cell's strength minus the cell's bypass surface. A reviewer's first job is to ensure the bypasses are documented and consciously accepted. **An undocumented control that fails to its bypass is the worst kind of governance theatre.**

When you skip a cell, you are accepting that an attack at this layer will be unstopped. The threat model in your repo should say so explicitly.
