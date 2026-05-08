# Authorization / Client-side

**Control.** `--allowedTools` deny-by-default. Capability-based tool restriction at the SDK layer. PreToolUse pattern hooks with **deny-then-ask-then-allow** precedence. Pre-commit hooks blocking changes to protected paths. Hooks directory and config owned by the operator, not the agent.

**Strength.** Deterministic when the hook config is uncompromised and the agent runtime honors precedence. Bypassable through allowlisted-shell shell-out, command obfuscation (base64, eval, env-var indirection), equivalent commands not in the pattern list, `--no-verify`, and filesystem tampering when the agent has write access to the hook surface.

## Tooling

- Claude Code v2.1.40 or later (the May 2026 PreToolUse precedence patch — pre-patch versions allow `allow` to override `deny`).
- `pre-commit` framework on the operator's machine.
- `jq` for the hook script.
- A server-side Git pre-receive hook to backstop `--no-verify`. Lives in [`../server-side/`](../server-side/).

## Files in this directory

- [`settings.json`](./settings.json) — Claude Code project settings with `permissions` `defaultMode: deny`, an explicit `allow` list (read-only ops), an `ask` list (mutation ops), a `deny` list (destructive ops). Drop in your project at `.claude/settings.json` (operator-owned, agent runs as a different user).
- [`pre_tool_use.sh`](./pre_tool_use.sh) — PreToolUse hook that receives JSON on stdin per the Claude Code hook spec. Hard-deny patterns (`rm -rf /`, `terraform destroy`, fork bombs) and obfuscation patterns (base64 decode, eval). Deploy to `/etc/agents/hooks/` with mode 0755 and owner root.
- [`pre-commit-config.yaml`](./pre-commit-config.yaml) — pre-commit framework config that runs gitleaks plus a deny-protected-paths hook. Drop at the repo root as `.pre-commit-config.yaml` and run `pre-commit install`.
- [`deny-protected-paths.sh`](./deny-protected-paths.sh) — pre-commit hook that fails when the diff touches `infrastructure/prod/`, `.github/workflows/`, or `secrets/`. Operator commits to those paths; agent commits do not.

## Verification

```bash
# 1. Hook fires on a denied command
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/test"}}' \
  | /etc/agents/hooks/pre_tool_use.sh
echo "exit code: $?"
# expected: BLOCKED message + exit 2

# 2. Hook does not fire on an allowed command
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' \
  | /etc/agents/hooks/pre_tool_use.sh
echo "exit code: $?"
# expected: exit 0

# 3. Hook config ownership
ls -la /etc/agents/hooks/pre_tool_use.sh
# expected: owner root, mode 0755

# 4. Agent cannot edit the hook
sudo -u agent-runner touch /etc/agents/hooks/pre_tool_use.sh
# expected: Permission denied

# 5. Pre-commit fires on a protected path
git checkout -b test-protected
echo "test" >> infrastructure/prod/main.tf
git add . && git commit -m "test"
# expected: failure at the deny-protected-paths hook
```

## Common mistakes

- Allowing `Bash(*)` in the allow list, which gates nothing.
- Pattern hooks that match `kubectl delete` but not `kubectl scale --replicas=0`. Pattern hooks catch casual misuse, not adversarial agents. Document the equivalent-command bypass and accept the matrix's framing.
- Hook config owned by the agent's own user. The agent edits its own deny list at runtime.
- Forgetting to enable the May 2026 Claude Code patch where `allow` no longer beats `deny`. Verify with `claude --version` and check the changelog.
- Pre-commit only on the operator's machine. The agent runs `git commit --no-verify` and skips it. Mitigation is the server-side pre-receive hook in [`../server-side/`](../server-side/).

## Citation

NIST CSF 2.0 PR.AA-05 (least privilege, separation of duties), PR.PS-01 (configuration management practices). NIST AI RMF MANAGE 2.4, MANAGE 4.1. OWASP LLM06 (Excessive Agency); LLM05 (Improper Output Handling). OWASP ASI02 (Tool Misuse), ASI05 (Unexpected Code Execution). OWASP MCP02, MCP05. OWASP Agentic Least Agency principle. NIST SP 800-207 §2.1 (least privilege).
