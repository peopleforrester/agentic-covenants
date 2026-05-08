# Sentinels — Identity / Server-side

**Control.** Cloud audit log attributes every API call to a verified identity. Alert on identity not in expected set, identity used outside expected hours, identity used from unexpected source IP, identity reuse across agents.

**Strength.** Authoritative and external. Bypass requires audit logging not enabled, immutable storage not configured, or SIEM rule based on the wrong identifier (e.g. STS opaque session ID instead of resolved role ARN).

## Tooling

- Kubernetes API server with audit logging configured.
- AWS CloudTrail with Object Lock on the destination S3 bucket. (GCP Audit Logs or Azure Monitor for the equivalent.)
- A SIEM with Sigma-style detection rules.

## Files in this directory

- [`audit-policy.yaml`](./audit-policy.yaml) — Kubernetes audit policy that captures every agent SA action at RequestResponse level for mutations and Metadata level for reads. Identity-binding events (RoleBindings, ServiceAccount creation) are captured at full body.
- [`enable-cloudtrail.sh`](./enable-cloudtrail.sh) — provisions a multi-region CloudTrail trail with log file validation enabled, delivering to an Object-Lock S3 bucket (provisioned in [`../../../controls/blast-radius/server-side/s3-immutable-backups.sh`](../../../controls/blast-radius/server-side/s3-immutable-backups.sh)).
- [`sigma-out-of-hours.yaml`](./sigma-out-of-hours.yaml) — Sigma rule firing when an agent SA is used outside the expected business-hours window.
- [`sigma-unexpected-source-ip.yaml`](./sigma-unexpected-source-ip.yaml) — Sigma rule firing when the source IP of an agent action is outside the known agent-egress IP set.

## Verification

```bash
# 1. Audit log captures agent SA actions
kubectl --as=system:serviceaccount:agent-claude-prod:claude-code get pods
grep "claude-code" /var/log/kubernetes/audit.log | tail -1
# expected: user.username with the agent SA

# 2. CloudTrail captures IAM action attributable to agent
aws --profile claude-code-prod sts get-caller-identity
sleep 60   # CloudTrail has delivery delay
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=claude-code-prod \
  | jq '.Events | length'
# expected: greater than 0

# 3. SIEM rule fires on out-of-hours
# Manually run an action at 03:00 local time; alert should fire within minutes.
```

## Common mistakes

- K8s audit policy not applied because the flag was not set on API server start. Verify with a known kubectl call against an audit log entry.
- CloudTrail bucket without Object Lock; an attacker with bucket-write deletes evidence.
- SIEM rule based on `userIdentity.principalId` instead of resolved role ARN. STS sessions present opaque IDs.
- Audit log retention shorter than incident discovery window. 30 days is the floor; 365 days is defensible for compliance.

## Citation

NIST CSF 2.0 DE.CM-01, DE.CM-09, DE.AE-02. NIST SP 800-92.
