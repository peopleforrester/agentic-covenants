# Sentinels, Authorization / Server-side

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

**Control.** RBAC denial events from Kubernetes audit. IAM Access Analyzer findings reporting unused permissions. Kyverno PolicyReports surface admission failures. OPA decision logs centralized.

**Strength.** Deterministic and external. Failure modes: Kyverno in `Audit` mode (logs but does not enforce; the violation already happened); OPA decision log streams everything (floods SIEM unless filtered); Access Analyzer is regional (configure per-region).

## Tooling

- Kyverno 1.18 to 1.19 Reports controller.
- OPA Gatekeeper with decision logging configured.
- AWS IAM Access Analyzer enabled per region.
- A SIEM with field-level filtering.

## Files in this directory

- [`ship-policy-reports.yaml`](./ship-policy-reports.yaml), CronJob that reads Kyverno PolicyReports across all namespaces every 5 minutes, filters for `summary.fail > 0`, and ships each failure to the SIEM as a structured event.
- [`opa-decision-log-config.yaml`](./opa-decision-log-config.yaml), OPA config snippet that streams decision logs to the SIEM. Filters on `decision == false` so the SIEM is not flooded with allow events.
- [`access-analyzer-eventbridge.sh`](./access-analyzer-eventbridge.sh), wires AWS IAM Access Analyzer findings to EventBridge → Lambda → SIEM.
- [`sigma-rbac-denial-spike.yaml`](./sigma-rbac-denial-spike.yaml), SIEM rule firing when more than 10 RBAC denials occur in a single namespace within 5 minutes.

## Verification

```bash
# 1. Trigger a Kyverno deny, find it in PolicyReport
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bad-binding-test
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: claude-code
  namespace: agent-claude-prod
EOF
# expected: rejected; PolicyReport in kyverno namespace shows fail entry

# 2. Ingestion job runs and ships
kubectl logs -n kyverno -l job-name=ship-policy-reports --tail=50

# 3. Access Analyzer surfaces unused permission
aws accessanalyzer list-findings --analyzer-arn $ANALYZER_ARN \
  --filter '{"status":{"eq":["ACTIVE"]},"resourceType":{"eq":["AWS::IAM::Role"]}}' \
  | jq '.findings[].principalArn'
# expected: agent role ARN if it has unused permissions
```

## Common mistakes

- Kyverno running in `Audit` mode silently logs but does not enforce. Always pair the policies you care about with `Enforce`.
- OPA decision log streams everything, including allows. Filter at the OPA side or the SIEM is unusable.
- Access Analyzer is regional. Configure per-region if multi-region.
- RBAC denials from `kubectl auth can-i` checks count as denials in audit log. Filter on `verb` and `resource` to avoid noise.

## Citation

NIST CSF 2.0 DE.CM-01, DE.CM-09, DE.AE-02. NIST SP 800-207.
