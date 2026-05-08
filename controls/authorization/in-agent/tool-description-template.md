# Tool-description template — Authorization scoping

Use this shape for every tool description in your agent's tool registry, MCP server, or Claude Code skill. The model reads the description; write it for the model.

---

## Template

```
{{ TOOL_NAME }}

Purpose:
  {{ ONE_SENTENCE_PURPOSE }}

Allowed inputs:
  - {{ ALLOWED_INPUT_1 }}
  - {{ ALLOWED_INPUT_2 }}

Not for:
  - {{ FORBIDDEN_USE_1 }}     (this is a hard scope boundary; do not use this tool for it)
  - {{ FORBIDDEN_USE_2 }}     (this is enforced at <client-side hook | server-side policy>)

When you are about to call this tool, check:
  1. Is the input within the allowed list?
  2. Is the action consistent with the operator's stated goal in this session?
  3. Will this action be reversible without operator intervention?

If any answer is no, stop and ask the operator. The lower-layer enforcement
will reject the call regardless; you will save a round-trip.
```

---

## Example: a `kubectl` wrapper tool

```
kubectl_get

Purpose:
  Read the state of Kubernetes resources in the operator's diagnostic namespace.

Allowed inputs:
  - kubectl get pods, services, deployments, configmaps in namespace=agent-claude-prod
  - kubectl logs of pods in namespace=agent-claude-prod

Not for:
  - kubectl delete, apply, patch, edit, exec, port-forward, cp, debug
  - any action targeting namespaces other than agent-claude-prod
  - any action with --all-namespaces or -A

When you are about to call this tool, check:
  1. Is the verb "get" or "logs"?
  2. Is the namespace agent-claude-prod?
  3. Are there no flags that broaden the scope (--all-namespaces, --as, --as-group)?

If any answer is no, stop and ask the operator. The cluster RBAC (Role
"claude-code" in namespace agent-claude-prod) will reject the call anyway,
but asking first is faster than waiting for the rejection.
```

## Notes

- Mention the lower-layer enforcement explicitly. "The cluster RBAC will reject this anyway" is a hint to the model that this tool is real-world scoped, not just norm-scoped.
- Keep the "When you are about to call this tool, check" list short. Three to five items, each answerable in one second.
- Use the imperative ("stop and ask"), not the suggestive ("you should consider").
- Do not include real production resource names in the example. The example must be obviously an example.
