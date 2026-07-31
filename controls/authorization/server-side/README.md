# Authorization / Server-side

**Control.** Scoped RBAC Roles, never ClusterRoles. IAM policies scoped to specific resources with explicit ARN. Kyverno or OPA admission policies. Namespace-scoped permissions. Deny `*` verbs. Deny prod namespaces from agent ServiceAccounts. Server-side Git pre-receive hooks for repo-level enforcement.

**Strength.** Deterministic and external to both the agent and the operator's machine. Bypass requires escalation primitives in RBAC (`escalate`, `bind`, impersonation), aggregated roles missed by the policy author, subresource access not denied (`pods/exec` when only `pods` is denied), admission webhook fail-open, IAM condition logic bugs, or operator manipulation through a persuasive PR description.

## Tooling

- Kubernetes RBAC (built-in).
- Kyverno 1.18+ (older releases use a different `attestors` block shape) or OPA Gatekeeper.
- AWS IAM, GCP IAM, or Azure RBAC.
- Server-side Git pre-receive hooks (every Git server in your org, not just origin).

## Files in this directory

- [`kyverno-no-cluster-roles.yaml`](./kyverno-no-cluster-roles.yaml) — ClusterPolicy with three rules: deny `ClusterRoleBinding` whose subjects include any agent ServiceAccount; deny wildcard verbs in any Role or ClusterRole; deny RoleBinding into prod namespaces with agent SA subjects. Apply with `kubectl apply -f`.
- [`git-pre-receive-hook.sh`](./git-pre-receive-hook.sh) — server-side pre-receive hook. Rejects force-pushes to main, blocks edits to protected paths from non-CODEOWNERS, runs gitleaks against the diff. Install in `/var/lib/git/<repo>.git/hooks/pre-receive` on every Git server.
- [`aws-iam-scoped-policy.json`](./aws-iam-scoped-policy.json) — example IAM policy with explicit `Resource` ARNs for the allow list and a tagged-deny clause for everything else. Substitute resource ARNs for your environment.

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
- Webhook timeout `failurePolicy: Ignore` — under load, the policy fails open and admits the violating resource.

## Citation

NIST CSF 2.0 PR.AA-05 (least privilege, separation of duties), PR.PS-01 (configuration management practices), PR.PS-05 (unauthorized software prevented). NIST SP 800-207 (Zero Trust). OWASP ASI02, ASI03, ASI05. CIS Kubernetes Benchmark.
