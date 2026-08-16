# Sentinels, Blast radius / Server-side

**Control.** Falco runtime detection in agent containers. NetworkPolicy violation events via Cilium Hubble. ResourceQuota near-limit alerts via Prometheus. VPC Flow Logs for unexpected egress.

**Strength.** Deterministic at the cluster and cloud layer. Failure modes: Falco rules tagged `WARNING` that should be `ERROR` (never page anyone); Hubble enabled but flow export not configured (alerts visible only in Hubble UI); ResourceQuota alert at 85% without auto-scale (alerts but no remediation); VPC Flow Log retention too short to see slow exfiltration.

## Tooling

- Falco 0.40+ deployed as a DaemonSet.
- Cilium with Hubble flow export enabled.
- Prometheus + AlertManager.
- AWS VPC Flow Logs delivered to CloudWatch Logs.

## Files in this directory

- [`falco-agent-container.yaml`](./falco-agent-container.yaml), Falco rules for agent Pods: shell spawn, sensitive-path writes, non-allowlisted egress.
- [`hubble-export.sh`](./hubble-export.sh), pipes `hubble observe --type drop` to the SIEM.
- [`prometheus-quota-alert.yaml`](./prometheus-quota-alert.yaml), AlertManager rule firing when ResourceQuota usage exceeds 85%.
- [`vpc-flow-rejects.sql`](./vpc-flow-rejects.sql), CloudWatch Logs Insights query for VPC Flow REJECT records sourced from agent CIDRs.

## Verification

```bash
# 1. Falco fires on shell spawn in agent Pod
kubectl exec -n agent-claude-prod claude-code -- /bin/sh -i
# expected: Falco alert "Agent pod spawned shell" via journalctl on Falco node

# 2. Hubble surfaces drops
kubectl exec -n agent-claude-prod claude-code -- curl -sS --max-time 3 http://blocked.example.com
hubble observe --pod agent-claude-prod/claude-code --type drop --last 2m
# expected: drop event

# 3. Quota alert fires
# Deploy enough Pods to hit 85% of CPU quota; confirm Prometheus alert.
```

## Common mistakes

- Falco rule output not parseable. Use `json_output: true` in `falco.yaml`.
- Hubble enabled but `hubble observe --output json` not piped anywhere; SIEM has no detection signal.
- ResourceQuota alert at 85% with no auto-scale, alerts but no remediation. Pair with HPA or operator runbook.
- VPC Flow Log retention shorter than incident discovery window.

## Citation

NIST CSF 2.0 DE.CM-01, DE.CM-09, DE.AE-03. NISTIR 8596 (Cybersecurity for AI).
