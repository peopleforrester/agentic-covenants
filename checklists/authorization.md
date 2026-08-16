# Checklist: Authorization

> **If this agent decides to do something outside its scope, what stops it at this layer?**

Agent: ________________  Charter ref: ________________  Risk tier: ____  Date: __________
Auditor: ________________  Owner present: ________________

---

## L1, In-agent (advisory only)

- [ ] Every tool description states what the tool is **not** for, not only what it does
- [ ] Tool descriptions name the lower-layer enforcement ("cluster RBAC will reject this anyway")
- [ ] No forbidden-command examples embedded in descriptions (models pattern-match on them)
- [ ] Under 50 lines of prompt spent on enforcing any security property

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L2, Client-side

- [ ] `defaultMode` is a **valid** mode. Valid: `default`/`manual`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`. **There is no `deny` mode**
- [ ] Deny-by-default posture: `dontAsk` with an explicit allow list, or equivalent
- [ ] No `Bash(*)` or `PowerShell(*)` in the allow list, that gates nothing
- [ ] PreToolUse hook exists and follows **deny → ask → allow** precedence
- [ ] Agent runtime is on a version where `allow` cannot override `deny` (Claude Code ≥ 2.1.40)
- [ ] Hook script and config owned by **root/operator**, not the agent's user
- [ ] Obfuscation patterns covered (base64 decode, `eval $(`, `curl | bash`)
- [ ] Pre-commit hooks block protected paths, and you know `--no-verify` defeats them

**Verify:**
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/x"}}' | /etc/agents/hooks/pre_tool_use.sh; echo "exit=$?"   # expect BLOCKED, exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}'        | /etc/agents/hooks/pre_tool_use.sh; echo "exit=$?"   # expect exit 0
ls -la /etc/agents/hooks/pre_tool_use.sh                              # owner root, mode 0755
sudo -u agent-runner touch /etc/agents/hooks/pre_tool_use.sh          # must fail
claude --version                                                      # confirm patched line
```

**Known bypasses accepted?** shell-out through an allowlisted Bash tool · equivalent commands not in the pattern list (`kubectl scale --replicas=0` for `delete`; `find -delete` for `rm`) · `--dangerously-skip-permissions` · agent edits its own config and restarts

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L3, Server-side

- [ ] Namespace-scoped **Role**, never ClusterRole, for the agent SA
- [ ] **No wildcard verbs and no wildcard resources**
- [ ] Subresources enumerated explicitly, denying `pods` does **not** deny `pods/exec`, `pods/portforward`, `pods/attach`
- [ ] Escalation primitives denied: `escalate`, `bind`, `impersonate`
- [ ] IAM policies scoped to explicit ARNs; `iam:PassRole` and policy-attachment actions denied
- [ ] Admission policy in **Enforce**, not Audit
- [ ] Webhook `failurePolicy: Fail`, or use in-tree ValidatingAdmissionPolicy and remove the fail-open path entirely
- [ ] Agent SAs denied from binding into prod namespaces
- [ ] Server-side Git pre-receive hook backstops `--no-verify`

**Verify:**
```bash
kubectl apply -f - <<'EOF'    # must be REJECTED
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: bad-role, namespace: agent-claude-prod}
rules: [{apiGroups: ["*"], resources: ["*"], verbs: ["*"]}]
EOF
kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa>   # read the effective set, not the intended one
kubectl get clusterpolicies -o json | jq -r '.items[].spec.validationFailureAction' | sort -u   # expect Enforce
```

**Known bypasses accepted?** aggregated roles the author missed · subresource gaps · admission webhook fail-open under load · IAM condition logic bugs · persuasive PR description manipulating a human reviewer

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## Row verdict

☐ All three present ☐ In-agent only, **audit finding** ☐ Server-side only ☐ Client-side only

**Federal/DoD note.** 800-53 **AC-3, AC-6, AC-6(9), AC-24, CM-7**; DoD ZT **User** + **Application & Workload**; RAI *Governable*. **CVE-2026-46519** is the cautionary case: a Kubernetes MCP server enforced read-only only at the tool-discovery layer and clients called delete directly. Scope declared to the agent is advisory; **RBAC on the ServiceAccount is the boundary.**

**Product note.** Amazon Bedrock AgentCore Policy (GA March 3, 2026, Cedar, default-deny, evaluated at the gateway) is a shipping implementation of this cell. If you use it, this checklist still applies, verify the policies, do not assume the product.

**Open items:**

| # | Gap | Owner | Due |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
