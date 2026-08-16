# Bypasses

The matrix makes a defense-in-depth argument. That argument requires honesty about each layer's bypass surface. None of these bypasses invalidate the matrix. They explain why the matrix has three columns instead of one.

If a layer here lacks a bypass entry, that's a documentation gap, not a hardness claim. File an issue.

> **The failure classes here are not idiosyncratic.** On April 30, 2026, CISA, NSA, Australia's ACSC, the Canadian Centre for Cyber Security, NZ NCSC, and UK NCSC published **"Careful Adoption of Agentic AI Services"**, the first multi-nation joint guidance on agentic AI. It names five risk categories: **privilege escalation, design and configuration flaws, behavioral misalignment, structural cascading failures, and accountability opacity.** Every bypass catalogued below falls into one of those five. The crosswalk to this matrix's concerns is in [`CITATIONS.md`](./CITATIONS.md#five-eyes-risk-categories-mapped-to-the-five-concerns).

## In-agent layer

### Model instructions and refusals

- Prompt injection (direct and indirect).
- Jailbreak.
- Novel framing the model has not been trained to refuse.
- Model error: the same prompt produces different outputs across calls.
- Tool-description manipulation through upstream content (a malicious doc the agent ingests redefines what `delete_user` does).
- The structural absence of homeostatic stake, pre-action pause, and second-order learning means the layer cannot be made reliable by better prompting. The bypass is the architecture, not a bug.

**Treat as nudge, not control.**

### Approval prompts at the in-agent layer

- **93% approval rate** measured by Anthropic across Claude Code permission prompts (March 26, 2026). Equivalent to 2FA prompt fatigue (MFA bombing literature), AHRQ-documented clinical alarm fatigue, and GDPR consent fatigue.
- Any approval prompt that fires often degrades to a rubber stamp. The bypass is human cognition, not a software defect.
- The cure is not "ask better"; it is "ask less, and only on genuinely novel decisions." See judgment-query escalation in the Approval Gating column.

## Client-side layer

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

### `--dangerously-skip-permissions` ("yolo mode")

- Disables all PreToolUse permission checks by design. **Documented and intended.** Mitigation: organizational policy plus runtime monitoring for the flag in process arguments.
- Not a software bug. Treat as a policy boundary: detect it, alert on it, deny by default in your agent runner.

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

### Claude Code "allow" precedence regression (pre-May 2026)

- Pre-May 2026 versions of Claude Code: PreToolUse hooks returning `"allow"` bypassed `deny` rules.
- Patched in May 2026 release; correct precedence is **deny then ask then allow**.
- Pre-patch deployments remain vulnerable until upgraded. Verify your version.

### Claude Code 50-subcommand cap (Adversa, April 2, 2026)

- A chain of 50 no-op subcommands in `bashPermissions.ts` flips a `deny` rule into "ask the user," which Auto Mode then approves at the 93% rate.
- Proof of concept published. Mitigation: audit your installed Claude Code version against the disclosure.

### Claude Code VS Code extension `settings.json` deny rules

- Multiple GitHub issues from July 2025 through February 2026 report that `~/.claude/settings.json` deny rules and hooks do not consistently fire from the VS Code sidebar/extension panel.
- Hooks may not execute in sidebar sessions. Mitigation: run agent flows from the CLI, not from the IDE sidebar, until the issue is resolved.

### Claude Code `.claude/settings.json` hook auto-execution (CVE-2025-59536, CVE-2026-21852)

- Opening a project containing untrusted hooks executed them automatically without prompt.
- Patched. Warning dialog is the remaining barrier; treat untrusted projects as hostile.

### Claude Code symlink sandbox escape (CVE-2026-39861)

- Sandboxed processes prior to v2.1.64 could create symlinks; the unsandboxed parent followed them and wrote outside the workspace.
- Patched. Verify your runner is on a current version.

### Claude Code prompt-editor command injection (CVE-2026-35021)

- File paths interpolated into shell commands via `execSync` allowed `$()` and backtick command substitution despite double-quoting.
- Patched. Mitigation upstream: avoid interpolating untrusted strings into shell.

### Pre-commit hooks

- `git commit --no-verify` and `git commit -n` skip pre-commit, prepare-commit-msg, and commit-msg hooks by design.
- `git push --no-verify` skips pre-push.
- `git config core.hooksPath /dev/null` redirects hooks to nothing.
- `rm .git/hooks/*` if filesystem write is allowed.
- Bypassing git entirely via filesystem APIs (commit objects written directly).
- **Mitigation: server-side pre-receive hook running the same checks.** See [`controls/authorization/server-side/git-pre-receive-hook.sh`](./controls/authorization/server-side/git-pre-receive-hook.sh).

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

### MCP STDIO architecture (Anthropic SDK, all official languages)

- Treats configuration as command execution **by design** across Python, TypeScript, Java, and Rust SDKs.
- Disclosed by OX Security on April 15, 2026 across LangChain, LangFlow, Flowise, LettaAI, plus the Anthropic SDK itself.
- Anthropic declined to change the protocol.
- Mitigation is operator-side: allowlists, sandboxing, manifest hashing.

### MCP tool-description integrity

- **Tool-poisoning rug-pull**: a tool description approved on day 1 can be replaced silently on day 7. The agent operates against the new description without re-prompting the operator.
- Mitigation: pin tool-description hashes on first approval, re-prompt on change. See [`controls/supply-chain/client-side/mcp-verify-tools.py`](./controls/supply-chain/client-side/mcp-verify-tools.py).

## Approval gates (both client- and server-side)

### Tiered approval and human-in-the-loop confirmation

This control's primary failure mode is **alert fatigue**: reviewers approve reflexively after enough repetitions. The same failure mode is documented in:

- 2FA push prompts (Microsoft, Cisco Duo telemetry; MFA bombing literature).
- Medical alert systems (AHRQ-documented clinical alarm fatigue, Joint Commission Sentinel Event reports).
- GDPR consent flows (cookie-banner click-through rates).
- Code review on large PRs (the bigger the diff, the lower the per-line scrutiny).

**Anthropic's measured 93% approval rate** is the empirical ceiling for human-in-the-loop on top of in-agent gates.

Effectiveness degrades over time without rotation, sampling, threshold review, or signal-to-noise tuning.

- Tiered approval (auto-approve trivial, quick-confirm routine, typed confirmation for tier-3, out-of-band channel for highest-tier) reduces but does not eliminate the failure mode.
- Flat approval workflows degrade fastest.
- Judgment-query escalation, where the agent only escalates genuinely novel decisions, is more fatigue-resistant but has limited tooling support.

Pattern-matched gating also fails on equivalent commands. See PreToolUse bypass section.

## Server-side layer

### Terraform `prevent_destroy` lifecycle

- `terraform state rm` removes the resource from state without destroying it.
- Removing the resource block from configuration plus `terraform apply` deletes the resource.
- Direct state edits go around the lifecycle entirely.
- The attribute does not lock the resource at the cloud provider.
- **Effective only when paired with a gated apply pipeline.** See [`controls/blast-radius/server-side/iac-gated-pipeline.yml`](./controls/blast-radius/server-side/iac-gated-pipeline.yml).

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

- Repository admins and roles with the "bypass branch protections" permission walk through every rule **unless "Do not allow bypassing the above settings" is explicitly enabled.** This is the single most common branch-protection misconfiguration.
- Force-push and branch-deletion exemptions apply to admins.
- Operator manipulation through persuasive PR description influenced by agent output.
- Collusion between two reviewers.
- Review fatigue on large PRs.

### CODEOWNERS

- Paths not covered by the CODEOWNERS file.
- PR touching both protected and unprotected paths if the owner check is per-file rather than per-PR (depends on platform).
- Stale owner team after a reorg.

### Image signature verification (cosign)

- Compromise of signing infrastructure.
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

## Cross-cutting and ecosystem-level bypasses (2026 incidents)

These are documented incidents and disclosures from 2025 and 2026 that defeated multiple matrix layers in combination, or that revealed structural weaknesses in the agent ecosystem. They are listed by name because reviewers and talk audiences will ask about them.

### OpenClaw ClawJacked (CVE-2026-32025)

- **Disclosed**: Oasis Security, February 25, 2026.
- **Layer affected**: Client-side identity and authorization.
- **What it did**: Any visited webpage brute-forced the localhost gateway password without user interaction.
- **Patched**: OpenClaw 2026.2.25.
- **Lesson**: Localhost services on agent-operator machines are part of the attack surface. Treat them as untrusted external services.

### ClawHavoc / ClawHub skill ecosystem

- **Disclosed**: Koi Security and Repello AI, February through April 2026.
- **Layer affected**: Client-side and server-side supply chain.
- **What it did**: 341 → 1,184+ malicious skills published to the marketplace in two months. Skills run with full agent permissions; `SKILL.md` interpreted as trusted instructions.
- **Mitigation**: SkillCheck, ToxicSkills, SecureClaw scanning, plus dev-container isolation. Treat marketplaces as part of the supply chain.

### postmark-mcp npm backdoor

- **Disclosed**: Koi Security, September 25, 2025.
- **Layer affected**: Supply chain.
- **What it did**: First publicly documented in-the-wild malicious MCP server. ~300 organizations affected.
- **Lesson**: The supply-chain bypass is "trusting npm publication." Hash-pin manifests; never trust a name.

### Cline 2.3.0 / Cacheract / Clinejection

- **Disclosed**: February 17, 2026.
- **Layer affected**: Cross-layer (in-agent, client-side, supply chain).
- **What it did**: Prompt injection in a GitHub issue title triggered `npm install` from an attacker-controlled commit, exfiltrating `NPM_RELEASE_TOKEN` and `VSCE_PAT`.
- **Lesson**: GitHub Actions plus Claude triage plus untrusted issue title equals taint propagation. Treat untrusted strings as untrusted across every boundary they cross.

### "Comment and Control" (Aonan Guan et al., April 21, 2026)

- **Layer affected**: In-agent + client-side.
- **What it did**: A single prompt-injection pattern via crafted GitHub PR titles or issue bodies compromised Claude Code Security Review, Gemini CLI Action, and GitHub Copilot Agent simultaneously. Exfiltration via GitHub itself.
- **Lesson**: Cross-vendor agentic security review is not vendor-isolated; one injection works against multiple agents.

### Filesystem MCP path traversal "EscapeRoute" (Cymulate)

- **Layer affected**: Client-side blast radius.
- **What it did**: Symlinks and unnormalized paths escape the allowed directory scope in Anthropic's reference filesystem MCP server.
- **Lesson**: Path normalization is hard; sandbox the filesystem access at a layer below the MCP.

### Amazon Q Developer VS Code extension (CVE-2025-8217)

- **Layer affected**: Supply chain.
- **What it did**: Malicious code injected via overly permissive GitHub token in AWS CodeBuild. Non-functional only because the attacker introduced a syntax error.
- **Lesson**: The supply-chain bypass is "trusting the build pipeline." Build provenance must be cryptographically attested, not just CI-emitted.

### Trend Micro "Weaponizing Trust Signals" (April 2026)

- **Layer affected**: Supply chain.
- **What it did**: Fake Claude Code installers and GitHub Release payloads.
- **Lesson**: The supply-chain bypass is "trusting branded download channels." Verify Sigstore signatures on every install.

### Check Point CVE-2025-59536 / CVE-2026-21852

- **Layer affected**: Client-side authorization.
- **What it did**: RCE via Claude Code project files; `settings.json` execution without prompt prior to patch.
- **Lesson**: Warning dialogs are the last line of defense, not the first. Sandbox project loading by default.

### Taiwan government agencies, near-autonomous agent campaign (July 2026)

- **Disclosed**: Taiwan's Ministry of Digital Affairs, August 2026; initially identified by the Israeli AI firm Dream. Alerts began circulating from Taiwan's National Institute of Cyber Security around July 20, 2026.
- **Layer affected**: All of them, from the other side.
- **What it did**: Over roughly four days, largely autonomous agents mapped **21 government systems**, cracked **85 accounts**, and exfiltrated approximately **2,500 personnel records**, then expanded to a nuclear safety agency, supply-chain vendors, and at least seven energy companies. The operators combined conventional tradecraft with **publicly available agent tooling**, reported to include OpenClaw. Widely characterized as the first known largely autonomous attack against government agencies.
- **Why it belongs in a defensive framework**: every other entry here describes an agent you run getting loose. This one describes the same class of tooling pointed at you. The capabilities are not different. An agent that can enumerate your infrastructure, chain credentials, and act at machine speed is the same artifact whether it is on your side of the perimeter or the other one, and the tooling is off-the-shelf and free.
- **Lesson**: Two, and they pull in the same direction. First, **speed is the whole problem**: four days, autonomously, across 21 systems. Any control that depends on a human noticing and intervening on a human timescale has already lost. That is the argument for the client-side and server-side columns and against the in-agent one. Second, **your own agent inventory is attack surface**. The [`inventory/`](./inventory/) matrix exists because a shadow agent nobody registered is indistinguishable from an intruder's agent, and neither will appear in a registry nobody maintains.

### Trivy scanner supply-chain compromise (March 2026)

- **Disclosed**: StepSecurity and Aqua Security, March 19, 2026 (a second incident after an earlier 2026 compromise).
- **Layer affected**: Supply chain, and pointedly, the **supply-chain *tooling* itself**.
- **What it did**: A malicious `trivy v0.69.4` release was published, and the `aquasecurity/setup-trivy` and `aquasecurity/trivy-action` GitHub Actions were compromised. Teams that ran "the scanner" in CI to *defend* their supply chain pulled a backdoored scanner. Safe versions at disclosure: `trivy v0.69.3`, `trivy-action v0.35.0`, `setup-trivy v0.2.6`.
- **Lesson**: Your security scanner is part of your supply chain. The control that verifies everything else must itself be verified. **Pin scanners by digest and verify their signatures, do not float a tag**, even (especially) for the tools whose whole job is supply-chain integrity. This repo recommends Trivy, pip-audit, gitleaks, syft, and cosign; every one of them is itself a dependency that can be poisoned. The L3-C5 admission policies ([`controls/supply-chain/server-side/`](./controls/supply-chain/server-side/)) and the SBOM-diff sentinel ([`sentinels/supply-chain/server-side/sbom-diff-cronjob.yaml`](./sentinels/supply-chain/server-side/sbom-diff-cronjob.yaml)) apply to the security toolchain too, not just the application image.

### Kubernetes MCP server read-only bypass (CVE-2026-46519)

- **Disclosed**: NeuralTrust, 2026.
- **Layer affected**: Authorization, and it is the cleanest proof of the matrix's central thesis.
- **What it did**: A Kubernetes MCP server enforced its "read-only mode" **only at the tool-discovery layer** (it hid the mutating tools from the listing). Clients simply invoked `delete` operations directly, bypassing the filter, because the restriction lived in agent-facing config rather than on the target.
- **Lesson**: Agent-declared scope is not authorization. **RBAC on the ServiceAccount is the real boundary**, exactly as the Authorization server-side cell ([`controls/authorization/server-side/`](./controls/authorization/server-side/)) insists. Anything enforced at the in-agent or tool-description layer (Charter scope, an MCP server's own "read-only" flag) is advisory until the target system denies the verb. This is the L3 covenant in one CVE.

### MCP unauthenticated RCE (CVE-2026-5058, CVE-2026-5059)

- **Layer affected**: Supply chain and blast radius.
- **What it did**: Two CVSS 9.8 vulnerabilities allowing unauthenticated remote code execution against MCP installations (unvalidated user-supplied strings reaching system calls; improper allowed-command handling). Part of a wave: 30+ MCP CVEs were filed in January to February 2026 alone, and independent scans place the share of public MCP servers carrying exploitable flaws somewhere between 30% and 82%.
- **Lesson**: The MCP ecosystem is an attack surface, not a convenience layer. Treat every MCP server as untrusted remote code: allowlist by hash ([`controls/supply-chain/client-side/mcp-allowlist.json`](./controls/supply-chain/client-side/mcp-allowlist.json)), fence egress to approved MCP domains at the network layer ([`controls/supply-chain/server-side/cilium-mcp-fqdn-egress.yaml`](./controls/supply-chain/server-side/cilium-mcp-fqdn-egress.yaml)), and never run an MCP server with more privilege than the covenant allows.

### Agent-framework CVE wave (mid-2026)

- **Layer affected**: Identity, authorization, and blast radius, depending on the entry.
- **What they did**:
  - **CVE-2026-25592**: Microsoft Semantic Kernel for .NET below 1.71.0. Fixed in 1.71.0; the remediation is a version bump, which is exactly the class of claim the currency discipline in [`CONTRIBUTING.md`](./CONTRIBUTING.md) exists to keep honest.
  - **CVE-2026-25253**: OpenClaw token leakage, CVSS 8.8. A leaked agent token is a leaked identity, and it is indistinguishable from legitimate use on the target side unless the credential is short-lived and bound.
  - **CVE-2026-32922**: privilege escalation to remote code execution, CVSS 9.9. The near-maximum score reflects that the escalation path ends outside the agent's intended scope entirely.
- **Also**: Tenable tracked a cluster of **seven distinct agentic-AI incidents between November 2025 and August 2026**, including JADEPUFFER (exploiting CVE-2025-3248 in Langflow) and the knaithe/KnYuan activity documented by Unit 42. The interesting property of the cluster is not any single entry, it is the rate.
- **Lesson**: Agent frameworks are now a routine CVE surface with a normal patch cadence, and they should be inventoried and patched like any other production dependency. That is an [`inventory/`](./inventory/) problem before it is a [`controls/`](./controls/) problem: you cannot patch the agent framework you did not know was running. The blast-radius controls are what buy you time between disclosure and patch.

### MCP `2026-07-28` protocol revision (new surface, and a stronger identity floor)

- **Status**: Release candidate locked 2026-05-21; final targeted 2026-07-28. The largest protocol change since launch.
- **Layer affected**: Identity (strengthened) and supply chain (new surface).
- **What changed**: The protocol goes **stateless**, the `initialize` handshake, protocol-level sessions, and the `Mcp-Session-Id` header are removed; each request now carries its protocol version, client identity, and client capabilities in `_meta`, and cross-call state moves to explicit server-minted handles passed as ordinary tool arguments. Authorization is hardened toward OAuth 2.0 / OpenID Connect: `iss` validation (RFC 9207), issuer-bound credentials, and Dynamic Client Registration deprecated in favor of Client ID Metadata Documents. HTTP+SSE transport is deprecated in favor of Streamable HTTP.
- **Why it matters here**: The OAuth 2.0 / OIDC hardening and issuer-bound credentials *raise the floor* under the Identity covenant ([`controls/identity/`](./controls/identity/)), server-established identity is now the protocol's own direction of travel, matching the NIST NCCoE agent-identity concept paper. But statelessness relocates trust: identity and capabilities now ride in `_meta` on every request (validate them; do not trust client-asserted `_meta`), and the JSON Schema 2020-12 support means **clients must not auto-dereference external `$ref` URIs** and must bound schema depth. Token passthrough remains forbidden and the host still enforces the trust boundary, the covenant does not move to the protocol, it composes with it.

---

## What this list is for

When you populate a cell, you are buying the cell's strength minus the cell's bypass surface. A reviewer's first job is to ensure the bypasses are documented and consciously accepted. **An undocumented control that fails to its bypass is the worst kind of governance theatre.**

When you skip a cell, you are accepting that an attack at this layer will be unstopped. The threat model in your repo should say so explicitly.
