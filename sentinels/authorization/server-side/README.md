# Sentinels — Authorization / Server-side

**Control.** RBAC denial events from Kubernetes audit. IAM Access Analyzer findings reporting unused permissions. Kyverno PolicyReports surface admission failures. OPA decision logs centralized.

**Strength.** Deterministic and external. Failure modes: Kyverno in `Audit` mode (logs but does not enforce; the violation already happened); OPA decision log streams everything (floods SIEM unless filtered); Access Analyzer is regional (configure per-region).

## Tooling

- Kyverno 1.13+ Reports controller.
- OPA Gatekeeper with decision logging configured.
- AWS IAM Access Analyzer enabled per region.
- A SIEM with field-level filtering.

## Files in this directory

- [`ship-policy-reports.yaml`](./ship-policy-reports.yaml) — CronJob that reads Kyverno PolicyReports across all namespaces every 5 minutes, filters for `summary.fail > 0`, and ships each failure to the SIEM as a structured event.
- [`opa-decision-log-config.yaml`](./opa-decision-log-config.yaml) — OPA config snippet that streams decision logs to the SIEM. Filters on `decision == false` so the SIEM is not flooded with allow events.
- [`access-analyzer-eventbridge.sh`](./access-analyzer-eventbridge.sh) — wires AWS IAM Access Analyzer findings to EventBridge → Lambda → SIEM.
- [`sigma-rbac-denial-spike.yaml`](./sigma-rbac-denial-spike.yaml) — SIEM rule firing when more than 10 RBAC denials occur in a single namespace within 5 minutes.

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
