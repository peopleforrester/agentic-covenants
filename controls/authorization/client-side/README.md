# Authorization / Client-side

**Control.** `--allowedTools` deny-by-default. Capability-based tool restriction at the SDK layer. PreToolUse pattern hooks with **deny-then-ask-then-allow** precedence. Pre-commit hooks blocking changes to protected paths. Hooks directory and config owned by the operator, not the agent.

**Strength.** Deterministic when the hook config is uncompromised and the agent runtime honors precedence. Bypassable through allowlisted-shell shell-out, command obfuscation (base64, eval, env-var indirection), equivalent commands not in the pattern list, `--no-verify`, and filesystem tampering when the agent has write access to the hook surface.

## Tooling

- Claude Code v2.1.40 or later (the May 2026 PreToolUse precedence patch, pre-patch versions allow `allow` to override `deny`).
- `pre-commit` framework on the operator's machine.
- `jq` for the hook script.
- A server-side Git pre-receive hook to backstop `--no-verify`. Lives in [`../server-side/`](../server-side).

## Files in this directory

- [`settings.json`](./settings.json), Claude Code project settings with `permissions` `defaultMode: deny`, an explicit `allow` list (read-only ops), an `ask` list (mutation ops), a `deny` list (destructive ops). Drop in your project at `.claude/settings.json` (operator-owned, agent runs as a different user).
- [`pre_tool_use.sh`](./pre_tool_use.sh), PreToolUse hook that receives JSON on stdin per the Claude Code hook spec. Hard-deny patterns (`terraform destroy`, `DROP TABLE`, fork bombs), a flag parser for `rm`, the equivalent-command evasions listed in [`BYPASSES.md`](../../../framework/BYPASSES.md), and obfuscation patterns (base64 decode, eval, env-variable indirection). Deploy to `/etc/agents/hooks/` with mode 0755 and owner root. Behavior is locked by [`tests/test_pre_tool_use.py`](../../../tests/test_pre_tool_use.py).
- [`pre-commit-config.yaml`](./pre-commit-config.yaml), pre-commit framework config that runs gitleaks plus a deny-protected-paths hook. Drop at the repo root as `.pre-commit-config.yaml` and run `pre-commit install`.
- [`deny-protected-paths.sh`](./deny-protected-paths.sh), pre-commit hook that fails when the diff touches `infrastructure/prod/`, `.github/workflows/`, or `secrets/`. Operator commits to those paths; agent commits do not.

## What the hook catches, and what it does not

**This is a filter, not a boundary.** It raises the cost of the casual and the careless path. It does not stop an adversary. Anyone with shell access and time gets past a pattern matcher, and GHSA-xq4m-mc3c-vvg3 is the proof that even the runtime's own allowlist parser can be talked into the wrong answer about a command it read correctly. The boundary is the [server-side column](../server-side): RBAC on the target, an admission controller, a pre-receive hook, a credential the agent never holds. Nothing in this directory is a substitute for those, and the hardening below does not change that.

What it does catch, because these are cheap to catch and are what casual misuse actually looks like:

| Evasion class | Handling |
|---|---|
| Case variation (`drop table`, `TerraForm destroy`) | All patterns match case-insensitively. |
| `rm` flag permutation (`-fr`, `-Rf`, `-f -r`, `--recursive --force`) | Flags are parsed, not pattern-matched. One rule covers every spelling. |
| Word splitting (`r""m`, `r\m`, `rm${IFS}-rf${IFS}/`) | The command is normalized before matching: empty quote pairs removed, escapes stripped, `$IFS` expanded, whitespace collapsed. |
| Equivalent commands (`find / -delete`, `kubectl scale --replicas=0`, `TRUNCATE`) | Denied by name, from the list in [`BYPASSES.md`](../../../framework/BYPASSES.md). |
| Env-variable indirection (`X=rm; $X -rf /`) | Heuristic: binding a destructive binary to a variable name is denied. |
| Hand-editing Terraform state or production `.tf` | Denied on the Edit and Write tools by file path, where the path is detectable. |

What it deliberately does not catch, so nobody mistakes an untested gap for a covered one:

- **Anything that reaches the shell through an interpreter.** A Python or Node one-liner, a script written to a file and then executed, a Makefile target. The hook sees a command string, not a syscall.
- **Indirection the normalizer cannot resolve.** `$(echo cm0K | base64 -d)`, a function defined earlier in the session, an alias, a wrapper script on `PATH`. Some spellings trip the obfuscation list; the class is open-ended.
- **Absolute-path deletes below the recursion rule.** `rm /etc/passwd` is a single-file delete, so it is allowed. Deny-by-default on paths belongs in the filesystem, not here.
- **`DELETE FROM` without a `WHERE` clause**, and most data-destroying SQL that is not `DROP` or `TRUNCATE`. Distinguishing a routine delete from a table wipe needs a parser, and a half-parser produces false denials.
- **Shell redirection into a protected path.** `echo x > infrastructure/prod/main.tf` is a Bash command, not an Edit call, and the path check only reads the Edit and Write tool inputs.
- **A hook the agent can rewrite.** File ownership answers this, not the hook's own content.

The policy line for deletes is that a recursive delete aimed at an absolute path, `$HOME`, or `~` is denied, while the same delete inside the working tree is ordinary work. `rm -rf /var/lib` is denied; `rm -rf ./node_modules` is allowed. A hook that denies both is an outage, not a control.

### Writing about a dangerous command is the same as running one

The hook is handed a command string. It cannot tell a command that uses a dangerous pattern from one that quotes it, and it does not try. Both of these are harmless and both are denied:

```bash
grep -rn "drop table" docs/
echo "find /target -delete is a known bypass" >> notes.md
```

Case folding widens this. `git commit -m "drop table rendering from the docs"` is denied for the same reason `drop table users` is.

A quote-aware exemption for read-only commands (`grep`, `echo`, `printf`, `cat`) was considered and rejected. These are the same shape as the two above, and all three are destructive:

```bash
echo "drop table users" | psql prod
echo "rm -rf /" > payload.sh; sh payload.sh
printf "%s" "find /target -delete" > p.sh && bash p.sh
```

They are denied today precisely because quoted text is matched, and write-payload-then-execute is an obfuscation class [`BYPASSES.md`](../../../framework/BYPASSES.md) already lists. An exemption broad enough to clear the false positives clears these too. Separating them needs a shell interpreter, not a rule, and deciding what counts as "inside a quote" is the defect in GHSA-xq4m-mc3c-vvg3, where the parser read the command correctly and still reached the wrong verdict. A filter that cannot parse intent is wrong in one direction or the other. For a control whose failure mode is destruction, erring toward denial is the right default, and a loud false denial is a better failure than a quiet exploitable exemption.

The trade is survivable because the Edit and Write tools carry a file path rather than a command, so the hook never sees the text. Documenting an evasion in `BYPASSES.md` goes through unaffected. Use the file tools rather than a shell heredoc, and if a specific denied string blocks real work, tune the pattern list to your own traffic rather than adding a general exemption.

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

# 6. Known evasions are denied, not just the canonical spelling
for cmd in 'rm -fr /' 'find /target -delete' 'drop table users' 'TerraForm destroy'; do
  printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}' "$cmd" \
    | /etc/agents/hooks/pre_tool_use.sh >/dev/null 2>&1
  echo "$? <- $cmd"
done
# expected: 2 on every line

# 7. Ordinary work still runs
for cmd in 'git status' 'kubectl get pods' 'rm -rf ./node_modules'; do
  printf '{"tool_name":"Bash","tool_input":{"command":"%s"}}' "$cmd" \
    | /etc/agents/hooks/pre_tool_use.sh >/dev/null 2>&1
  echo "$? <- $cmd"
done
# expected: 0 on every line
```

Both directions are covered by the test suite, which drives the hook over the same JSON-on-stdin contract Claude Code uses:

```bash
uvx --with pyyaml --from pytest pytest tests/test_pre_tool_use.py -q
```

## Common mistakes

- Allowing `Bash(*)` in the allow list, which gates nothing.
- Pattern hooks that match `kubectl delete` but not `kubectl scale --replicas=0`, or `DROP TABLE` but not `drop table`. Every deny pattern needs its equivalent commands and its case variants tested, in both directions, or the list is a guess. Even then, pattern hooks catch casual misuse and not adversarial agents. Document the residual bypass and accept the matrix's framing.
- Treating a hardened pattern list as a boundary. Closing the known evasions makes the filter better at being a filter. It does not make it a control the server-side column can lean on.
- Reading a false positive as a bug in the pattern list. `grep -rn "drop table" docs/` and `echo "find /target -delete is a known bypass" >> notes.md` are both denied, and both are harmless. Adding a quote-aware exemption to fix that also un-blocks `echo "drop table users" | psql prod`, which is the same shape and is not harmless. See the trade above before loosening anything.
- Hook config owned by the agent's own user. The agent edits its own deny list at runtime.
- Forgetting to enable the May 2026 Claude Code patch where `allow` no longer beats `deny`. Verify with `claude --version` and check the changelog.
- Pre-commit only on the operator's machine. The agent runs `git commit --no-verify` and skips it. Mitigation is the server-side pre-receive hook in [`../server-side/`](../server-side).

## Citation

NIST CSF 2.0 PR.AA-05 (least privilege, separation of duties), PR.PS-01 (configuration management practices). NIST AI RMF MANAGE 2.4, MANAGE 4.1. OWASP LLM06:2025 (Excessive Agency); LLM05:2025 (Improper Output Handling). OWASP ASI02:2026 (Tool Misuse), ASI05:2026 (Unexpected Code Execution). OWASP MCP02:2025, MCP05:2025. OWASP Agentic Least Agency principle. NIST SP 800-207 §2.1 (least privilege).
