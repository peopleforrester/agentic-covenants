# Authorization / Server-side

> **Kyverno API deprecation, verified 2026-09-17.** The policies here are legacy
> `kyverno.io/v1` `ClusterPolicy` resources. Kyverno **1.19 deprecates** that API
> group and emits an admission warning naming the `policies.kyverno.io`
> replacement. Current release is **v1.19.1** (2026-09-10). These policies load
> and enforce on 1.19; verified with the 1.19.1 CLI, the repo's suite passes
> 14 of 14 with three deprecation warnings.
>
> **What 1.20 does is not settled.** The upstream removal plan
> ([kyverno#17214](https://github.com/kyverno/kyverno/issues/17214), open, last
> updated 2026-09-16) carries a "DO NOT submit PRs, under discussion" banner and
> proposes that all CRDs stay served in 1.20 with stored policies still
> enforcing, while **submitting** a policy outside `policies.kyverno.io` becomes
> a hard error and full deletion moves to 1.21. For a template you copy into
> your own cluster, rejected-on-apply is the failure that matters, and it is a
> different failure from stopping working. Treat the November 2026 date as an
> estimate. Migration is tracked in
> [#11](https://github.com/peopleforrester/agentic-covenants/issues/11).

**Control.** Scoped RBAC Roles, never ClusterRoles. IAM policies scoped to specific resources with explicit ARN. Kyverno or OPA admission policies. Namespace-scoped permissions. Deny `*` verbs. Deny prod namespaces from agent ServiceAccounts. Server-side Git pre-receive hooks for repo-level enforcement.

**Strength.** Deterministic and external to both the agent and the operator's machine. Bypass requires escalation primitives in RBAC (`escalate`, `bind`, impersonation), aggregated roles missed by the policy author, subresource access not denied (`pods/exec` when only `pods` is denied), admission webhook fail-open, IAM condition logic bugs, or operator manipulation through a persuasive PR description.

## Tooling

- Kubernetes RBAC (built-in).
- Kyverno 1.18 to 1.19 (older releases use a different `attestors` block shape) or OPA Gatekeeper.
- **Kubernetes-native admission (no controller to install): ValidatingAdmissionPolicy (GA since 1.30) and MutatingAdmissionPolicy (GA and default-on in 1.36 "Haru", April 2026).** These are in-tree CEL admission policies with no webhook, which removes the "admission webhook fail-open" bypass listed below. Prefer VAP for the deny-wildcard-verbs / deny-ClusterRoleBinding rules where you want zero external dependencies; reach for Kyverno/OPA when you need `verifyImages`, generate rules, or cross-cluster policy libraries. The two compose.
- AWS IAM, GCP IAM, or Azure RBAC.
- **Managed deterministic pre-action authorization (this cell as a product).** **Amazon Bedrock AgentCore Policy went GA March 3, 2026**: authorization rules written in the **Cedar** policy language, default-deny, evaluated **at the Gateway** on every agent-to-tool request, outside the agent's code, outside the model's reasoning, and therefore not reachable by prompt injection. Microsoft shipped comparable runtime enforcement starting with Copilot in Q1 2026. This is the same control the rest of this cell builds by hand; if you are on Bedrock, use it rather than reimplementing it, and keep the Kubernetes-side admission policies as the second layer for anything the gateway does not mediate. The design point to preserve either way: **policy is evaluated before the tool executes, by something the agent does not control.**
- Server-side Git pre-receive hooks (every Git server in your org, not just origin).

## Files in this directory

- [`kyverno-no-cluster-roles.yaml`](./kyverno-no-cluster-roles.yaml), ClusterPolicy with three rules: deny `ClusterRoleBinding` whose subjects include any agent ServiceAccount; deny wildcard verbs in any Role or ClusterRole; deny RoleBinding into prod namespaces with agent SA subjects. Apply with `kubectl apply -f`.
- [`git-pre-receive-hook.sh`](./git-pre-receive-hook.sh), server-side pre-receive hook. Rejects force-pushes to main, blocks edits to protected paths from non-CODEOWNERS, runs gitleaks against the diff. Install in `/var/lib/git/<repo>.git/hooks/pre-receive` on every Git server.
- [`aws-iam-scoped-policy.json`](./aws-iam-scoped-policy.json), example IAM policy with explicit `Resource` ARNs for the allow list and a tagged-deny clause for everything else. Substitute resource ARNs for your environment.

## Verification

```bash
# 1. Confirm Kyverno blocks wildcard verbs
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: bad-role
  namespace: agent-claude-prod
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
EOF
# expected: rejected by Kyverno

# 2. Confirm pre-receive hook blocks --no-verify bypass
cd /tmp/test-repo
echo "test" >> infrastructure/prod/main.tf
git add . && git commit --no-verify -m "test"
git push origin main
# expected: failure at server-side pre-receive

# 3. Confirm IAM denies cross-resource access
aws --profile claude-code-prod s3 ls s3://other-bucket
# expected: AccessDenied

# 4. Confirm Kyverno background scan finds existing violations
kubectl get clusterpolicyreport -A
# expected: report of any pre-existing wildcard roles
```

## Common mistakes

- Kyverno installed in audit mode (`Audit`), which logs but does not enforce. Confirm `validationFailureAction: Enforce`.
- Pre-receive hook installed only on origin; clones to other Git remotes do not enforce. Make it a server-wide hook on every Git server in the org.
- IAM with `"Resource": "*"` and a forgotten `"Action": "*"` next to it.
- ClusterRole created for legitimate operator use, then accidentally bound to an agent SA via a copy-pasted RoleBinding.
- Forgetting subresources: denying `pods` does not deny `pods/exec`, `pods/portforward`, `pods/attach`. List them.
- Webhook timeout `failurePolicy: Ignore`, under load, the policy fails open and admits the violating resource.

## Citation

NIST CSF 2.0 PR.AA-05 (least privilege, separation of duties), PR.PS-01 (configuration management practices), PR.PS-05 (unauthorized software prevented). NIST SP 800-207 (Zero Trust). OWASP ASI02:2026, ASI03:2026, ASI05:2026. CIS Kubernetes Benchmark.
