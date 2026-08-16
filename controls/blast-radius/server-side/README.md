# Blast radius / Server-side

**Control.** Gated IaC apply pipeline as the actual backstop. ResourceQuota and LimitRange per namespace. NetworkPolicy default-deny with explicit allowlist. Physical separation of prod and non-prod clusters. Immutable backups with separate credentials. PodDisruptionBudget on critical workloads.

**Strength.** Deterministic and external. Bypass requires multiple simultaneous server-side failures: `prevent_destroy` removed in the same cycle as the apply (only effective when paired with the gated pipeline), DNS exfiltration when DNS is allowed without filtering, "immutable" backups in the same account as the credential that wrote them.

## Tooling

- GitHub Actions / GitLab CI / Jenkins for the pipeline split.
- Kubernetes ResourceQuota, LimitRange, NetworkPolicy.
- AWS S3 Object Lock, GCP Bucket Retention Policy, or Azure Blob immutable storage for immutable backups.
- A second AWS account, GCP project, or Azure subscription for prod, separate from non-prod.

## Files in this directory

- [`iac-gated-pipeline.yml`](./iac-gated-pipeline.yml), split-stage Terraform pipeline. The `plan` job runs on every PR and push with read-only credentials; the `apply` job runs only on `main` push and requires manual approval via a GitHub environment with required reviewers. Drop in `.github/workflows/`.
- [`networkpolicy-default-deny.yaml`](./networkpolicy-default-deny.yaml), namespace-wide default deny on ingress and egress.
- [`networkpolicy-allowlist.yaml`](./networkpolicy-allowlist.yaml), explicit allow rules layered over the default deny: kube-dns, public HTTPS to non-RFC1918 ranges only.
- [`resourcequota.yaml`](./resourcequota.yaml), namespace-level quota on CPU, memory, pods, PVCs, LoadBalancer/NodePort services (set to 0).
- [`limitrange.yaml`](./limitrange.yaml), per-container default and max requests/limits.
- [`s3-immutable-backups.sh`](./s3-immutable-backups.sh), provisions an S3 bucket with Object Lock in compliance mode and a 30-day default retention.
- [`cross-account-providers.tf`](./cross-account-providers.tf), Terraform provider blocks demonstrating the cross-account separation pattern: agent role lives in the non-prod account and explicitly cannot AssumeRole into prod.

## Verification

```bash
# 1. Pipeline split: plan runs without approval, apply does not
gh run list --workflow=iac-gated-pipeline.yml --branch=main --limit 1
# expected: apply job shows "Waiting for review" or "Approved"

# 2. NetworkPolicy default-deny in effect
kubectl run -n agent-claude-prod test --image=alpine --rm -it -- \
  wget -O- --timeout=3 http://10.0.0.5
# expected: timeout

# 3. ResourceQuota enforced
kubectl apply -n agent-claude-prod -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-quota
spec:
  containers:
  - name: c
    image: alpine@sha256:REPLACE_WITH_DIGEST
    resources:
      requests:
        cpu: "100"
        memory: 200Gi
EOF
# expected: rejected by ResourceQuota admission

# 4. Immutable backup cannot be deleted
aws s3 rm s3://prod-backups-immutable/test-object
# expected: AccessDenied due to Object Lock

# 5. Cross-account assumption denied
aws --profile claude-code-prod sts assume-role \
  --role-arn arn:aws:iam::PROD_ACCOUNT:role/anything \
  --role-session-name test
# expected: failure; agent role has no AssumeRole on prod account
```

## Common mistakes

- Pipeline split where apply auto-runs after plan with no environment gate.
- NetworkPolicy default-deny without an allow rule for kube-dns; pods cannot resolve names and silently fail.
- ResourceQuota without LimitRange; new Pods without explicit limits get rejected by the quota's `requests` ceiling.
- "Immutable" backups in the same account as the credential that wrote them, with `s3:DeleteObjectVersion` and `s3:PutBucketLifecycleConfiguration` available.
- Prod and non-prod in the same cluster separated only by namespaces. Namespace boundary is not a security boundary if NetworkPolicy or admission policies have gaps.

## Citation

NIST CSF 2.0 PR.IR-01 (networks protected), PR.IR-02 (technology assets protected from environmental threats), PR.IR-03 (mechanisms achieving resilience requirements), PR.IR-04 (adequate resource capacity), PR.DS-11 (backups created, protected, maintained, tested). NIST AI RMF MANAGE 2.4, MANAGE 4.1. OWASP LLM10 (Unbounded Consumption). OWASP ASI05, ASI08 (Cascading Failures). NIST SP 800-160 Vol. 1. NIST SP 800-34 Rev. 1 (contingency planning).
