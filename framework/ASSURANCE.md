# Assurance

Every matrix in this framework answers *what stops the agent*. None of them answers *how do you know it stopped the agent*.

That is the question an auditor asks second, and it is the one that applies this framework's own standard to itself. The thesis is that assertion is not enforcement. A framework whose controls have never been verified is asserting.

## Assurance is not Sentinels

| | Asks | When | Answers to |
|---|---|---|---|
| **Sentinels** (Detect) | What just happened? | At runtime, continuously | An on-call engineer |
| **Assurance** | Does this control do what we claim, against someone trying? | Before deployment, and repeatedly after | An auditor, a CISO, a buyer |

A Sentinel firing means a control was tested by an adversary. Assurance means you tested it first.

## The four activities

### 1. Control validation

Does the policy load, and does it deny what it claims to deny?

This is the mechanical floor, it is cheap, and it is where this repository found its own worst defect. **`kyverno-no-cluster-roles.yaml` shipped with `validationFailureAction: Enforce` and would have denied every Role in any cluster that installed it**, because two rules nested a map pattern under a list of strings. All three deny cases passed while the policy was broken. Only the admit cases caught it.

The lesson generalizes: **a rule tested only for what it blocks is half-tested, and it is the half that hides outages.**

Run it: `kyverno test tests/kyverno/`, or `./scripts/check.py` for everything. See [`tests/`](../tests).

### 2. Adversarial evaluation

Red-teaming the agent against the controls. The [`BYPASSES.md`](./BYPASSES.md) corpus is the obvious source of test cases, and the coverage map below is the current state of that work.

### 3. Behavioral evaluation

Does the agent still do the right thing with the guardrails on?

This is the activity nothing else in this repo addresses, and skipping it is how a control dies. **A guardrail that breaks the agent gets switched off by the team next quarter**, and the switch-off is rarely recorded anywhere. Measure the agent's task success rate before and after, and treat a large drop as a control defect rather than an acceptable cost. The `pass` cases in the Kyverno suite are the smallest possible version of this idea.

### 4. Evidence

What you hand an auditor. This is where the ISO/IEC 42001 and EU AI Act material in [`CITATIONS.md`](./CITATIONS.md) stops being a citation and becomes an artifact: a dated test run, a policy report, an off-box decision log, a kill-switch drill record.

## Coverage map: what this framework actually catches

Issue #5's definition of done is that every [`BYPASSES.md`](./BYPASSES.md) entry maps to a control that catches it, or to an explicit statement that nothing here does. Both outcomes are useful. The second is more useful than silence.

### Ecosystem incidents, 2026 corpus

| Incident | Contained by | Honest verdict |
|---|---|---|
| **K8s MCP read-only bypass** (CVE-2026-46519) | [`controls/authorization/server-side/`](../controls/authorization/server-side) | **Prevented.** The cleanest case in the corpus. The MCP server enforced read-only at tool discovery; RBAC on the ServiceAccount denies the verb regardless |
| **postmark-mcp npm backdoor** | [`supply-chain/client-side/`](../controls/supply-chain/client-side) hash pinning, [`server-side/`](../controls/supply-chain/server-side) egress allowlist | **Prevented** if the allowlist is hash-pinned. Path-only allowlists do not catch it |
| **EscapeRoute** filesystem MCP path traversal | [`blast-radius/client-side/`](../controls/blast-radius/client-side) sandbox mount set | **Prevented.** Traversal outside the mount set has nothing to reach |
| **MCP unauthenticated RCE** (CVE-2026-5058/5059) | [`blast-radius/`](../controls/blast-radius) sandbox, egress NetworkPolicy | **Bounded, not prevented.** RCE still occurs; the sandbox and egress policy decide what it reaches |
| **OpenClaw ClawJacked** (CVE-2026-32025) | [`supply-chain/client-side/`](../controls/supply-chain/client-side) | **Bounded.** Allowlisting limits which servers launch; a compromised allowlisted server is unaffected |
| **ClawHavoc / ClawHub skills** (1,184+ malicious) | [`supply-chain/`](../controls/supply-chain), [`inventory/`](../inventory) | **Partially.** Allowlisting works; the marketplace-scale discovery problem is an inventory problem this framework names and does not solve |
| **Cline / Cacheract / Clinejection** | [`supply-chain/client-side/`](../controls/supply-chain/client-side) | **Partially.** Cache-poisoning paths are not addressed by any artifact here |
| **"Comment and Control"** (Guan et al.) | [`content-integrity/`](../controls/content-integrity) | **Detection only.** Injection via code comments is exactly the semantic case. Scanners flag it probabilistically; containment is blast radius |
| **Trend Micro "Weaponizing Trust Signals"** | [`content-integrity/client-side/`](../controls/content-integrity/client-side) | **Detection only.** Same reasoning |
| **Amazon Q VS Code extension** (CVE-2025-8217) | [`supply-chain/`](../controls/supply-chain) | **Not prevented.** A signed extension from the official marketplace defeats provenance controls |
| **Trivy supply-chain compromise** | Nothing here | **Not prevented.** The scanner was the vector. A framework that recommends scanning has no answer when the scanner is compromised, and this entry exists to say so |
| **Check Point CVE-2025-59536 / CVE-2026-21852** | Nothing here | **Not prevented.** Hook auto-execution from repo-local config is a client platform defect. Operator-owned config placement mitigates; the artifact for it is advisory |
| **Claude Code symlink sandbox escape** (CVE-2026-39861) | Nothing here | **Not prevented.** A sandbox escape defeats the cell that would otherwise contain it. Patch is the only control |
| **Agent-framework CVE wave** (CVE-2026-25592, -25253, -32922) | [`inventory/`](../inventory), [`blast-radius/`](../controls/blast-radius) | **Not prevented.** Inventory tells you what to patch; blast radius buys time between disclosure and patch |
| **Taiwan government campaign** (July 2026) | Not applicable | **Out of scope, deliberately.** This is agentic tooling used *against* a target. Nothing in a framework for governing your own agents defends against someone else's. It is in the corpus because the capability is symmetric and the tooling is free |

### Control-layer bypasses

The first 29 entries in `BYPASSES.md` are bypasses *of* the controls this framework recommends, so the mapping is inverted: the question is what catches the bypass.

| Bypass class | Caught by | Verdict |
|---|---|---|
| In-agent instruction and refusal bypasses | Every client-side and server-side cell | **By design.** The whole framework exists because this layer fails |
| `--dangerously-skip-permissions`, allowlist evasion, hook pattern evasion | Server-side column | **Caught,** provided the server-side cell is populated. On a laptop with no remote enforcement, it is not |
| Pre-commit `--no-verify`, lockfile edits | [`authorization/server-side/git-pre-receive-hook.sh`](../controls/authorization/server-side/git-pre-receive-hook.sh), CI lockfile integrity | **Caught server-side** |
| Sandbox, seccomp, AppArmor escapes | Nothing in-repo | **Not caught.** A kernel-level escape defeats the strongest client-side cell. This is the residual risk the server-side column exists to bound |
| RBAC, IAM, admission-policy misconfiguration | [`tests/kyverno/`](../tests/kyverno), [`checklists/`](../checklists) | **Caught now.** It was not before this document existed, which is how the flagship policy shipped broken |
| Approval fatigue at a measured 93% approval rate | [`sentinels/approval-gating/`](../sentinels/approval-gating) | **Measured, not prevented.** A human who approves everything is a control that reports success |

### The tally, stated plainly

Of the 15 ecosystem incidents: **3 prevented, 5 bounded or partial, 6 not prevented, 1 out of scope.**

Six of fifteen is not a failure of the framework. It is what an honest coverage map looks like, and the alternative is a matrix that claims everything and is checked by nobody. The not-prevented column is dominated by two classes, and neither is closable by adding cells:

1. **Platform defects.** A sandbox escape or a hook auto-execution bug is fixed by the vendor, not by policy.
2. **Trusted-component compromise.** When the scanner, the signed extension, or the official marketplace is the vector, provenance controls confirm the wrong thing correctly.

## What is not done yet

Stated so a reader can tell an unfinished item from an unmade claim:

- **Executable adversarial tests.** Each `BYPASSES.md` entry should become a check that the controls now catch it. Currently the corpus is prose and the mapping above is analysis, not execution. `tests/kyverno/` is the only executable part.
- **Behavioral evals.** No task-success measurement exists for an agent before and after guardrails.
- **Evidence templates.** The auditor-facing artifact set is named in activity 4 and not yet written.

## Related

[`tests/`](../tests) for what runs today. [`BYPASSES.md`](./BYPASSES.md) for the corpus this maps. [`checklists/`](../checklists) for the per-agent manual pass. [`SECURITY.md`](../SECURITY.md) for reporting a defect in an artifact here, which is the highest-severity issue this repository can have.
