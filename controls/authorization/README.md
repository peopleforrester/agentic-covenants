# Authorization

**Intent.** Least-privilege scoped access. No wildcards. No inherited operator permissions. The agent has exactly the permissions it needs to do its declared job, no more.

## The row, at a glance

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent) | Tool descriptions that scope each tool to safe operations and explicitly say what the tool is not for. Advisory only. |
| Client-side | [`client-side/`](./client-side) | Claude Code `settings.json` with deny-by-default `permissions`, a PreToolUse hook with deny-then-ask-then-allow precedence, pre-commit hooks blocking edits to protected paths. Hooks owned by the operator account, not the agent. |
| Server-side | [`server-side/`](./server-side) | Kyverno ClusterPolicy denying wildcard verbs and ClusterRoleBindings on agent ServiceAccounts, server-side Git pre-receive hook (cannot be bypassed by `--no-verify`), IAM policies with explicit ARN scoping. |

## Why it matters

Authorization is the layer the agent reaches for first when it goes wrong. Identity tells you *who* the agent is; authorization tells you *what it is allowed to do*. A clean per-agent identity is meaningless if the role it binds to has `verbs: ["*"]`.

## How to walk it

For each layer ask: *if the agent decides to perform a forbidden action, what stops it at this layer?*

- **In-agent only:** the answer is "the model declines." That is bypassable through prompt injection, jailbreak, novel framing, or simply asking again.
- **Client-side adds:** `--allowedTools` denies the tool name entirely; PreToolUse hooks gate dangerous patterns; pre-commit blocks commits to protected paths. Bypassable through `--no-verify`, base64 obfuscation of commands, equivalent commands not in the pattern list (`kubectl scale --replicas=0` instead of `kubectl delete`), and through a hook config the agent can write to.
- **Server-side adds:** the cluster, the cloud provider, and the Git server reject the action regardless of what the agent or the operator's machine wants. Bypass requires escalation primitives in RBAC (`escalate`, `bind`, impersonation), aggregated roles missed by the policy author, subresource access not denied (`pods/exec` when only `pods` is denied), or admission webhook fail-open.

## Important note on Claude Code 2.1.40 patch

Pre-2.1.40 Claude Code allowed `allow` in `settings.json` `permissions` to override `deny`. This was patched in May 2026 so that `deny` always wins. Verify your version: `claude --version`. If you cannot upgrade, do not rely on `deny` rules; assume the bypass and move the control to client-side hooks or server-side admission.

## Citations (per layer)

See [`../../CITATIONS.md`](../../framework/CITATIONS.md). Quick reference:

- **In-agent**: advisory; thematically MAP 5.1; OWASP LLM06 (Excessive Agency); OWASP ASI02 (Tool Misuse).
- **Client-side**: NIST CSF 2.0 PR.AA-05 (least privilege, separation of duties), PR.PS-01; OWASP LLM05, LLM06; OWASP ASI02, ASI05; OWASP MCP02, MCP05; OWASP Agentic Least Agency principle.
- **Server-side**: NIST CSF 2.0 PR.AA-05, PR.PS-01, PR.PS-05; NIST SP 800-207; OWASP ASI02, ASI03, ASI05; CIS Kubernetes Benchmark.
