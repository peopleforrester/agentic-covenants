# Sentinels — Supply chain / Server-side

**Control.** Image-pull events captured via Kyverno mutate. Daily SBOM-diff CronJob. Cosign verification failures surface as PolicyReport entries. Cilium FQDN denial flow events shipped to SIEM.

**Strength.** Deterministic at admission and at the network layer. Failure modes: SBOM diff that compares only top-level package counts (misses transitive dependency changes); image-pull annotation policy in Audit mode (does not actually annotate); cosign failure alert without context (operator gets paged with image SHA but no PR or build context); Hubble FQDN logs disabled by default in some Cilium installs (verify `enable-l7-proxy: true`).

## Tooling

- Kyverno 1.18+.
- syft for SBOM generation.
- Cilium with Hubble and L7 proxy enabled.

## Files in this directory

- [`kyverno-log-image-pulls.yaml`](./kyverno-log-image-pulls.yaml) — mutating ClusterPolicy that annotates every Pod with the image references and pull timestamp; the annotation is shipped to SIEM by the policy-report shipping CronJob in [`../../authorization/server-side/ship-policy-reports.yaml`](../../authorization/server-side/ship-policy-reports.yaml).
- [`sbom-diff-cronjob.yaml`](./sbom-diff-cronjob.yaml) — daily CronJob that runs syft against every image in agent namespaces, hashes the SBOM, compares to the previous day's hash, ships sbom_diff events when changed.
- [`hubble-fqdn-deny-export.sh`](./hubble-fqdn-deny-export.sh) — pipes Hubble L7 DNS denials to SIEM (the FQDN-egress denial signal).
- [`sigma-cosign-failure.yaml`](./sigma-cosign-failure.yaml) — SIEM rule firing on policy-report entries where `data.policy: verify-image-signatures` and `data.failed > 0`.

## Verification

```bash
# 1. Image pull event captured
# Replace digest with a real signed agent image digest from your registry
kubectl run test --image=ghcr.io/example-org/claude-agent@sha256:9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f -n agent-claude-prod
kubectl get pod test -n agent-claude-prod \
  -o jsonpath='{.metadata.annotations.agent-sentinel/image-audit}'
# expected: matches the image

# 2. SBOM diff fires on image update
# Push a new image. Wait for next CronJob run. Check SIEM.

# 3. Cosign verification failure surfaces
kubectl run unsigned --image=docker.io/alpine -n agent-claude-prod
# expected: admission rejection; PolicyReport entry; SIEM alert via sigma-cosign-failure

# 4. FQDN denial captured
kubectl exec -n agent-claude-prod claude-code -- curl -sS --max-time 3 https://blocked-mcp.example.com
hubble observe --type drop --since 1m | grep blocked-mcp
# expected: drop event
```

## Common mistakes

- SBOM diff that compares only top-level package counts. Misses transitive dependency changes.
- Image pull annotation runs as `mutate` policy in Audit mode. Does not actually annotate.
- Cosign failure alert without context. Operator gets paged with image SHA, no PR or build context.
- Hubble FQDN logs disabled by default in some Cilium installs. Verify `enable-l7-proxy: true`.

## Citation

NIST CSF 2.0 DE.CM-09, ID.RA-09, GV.SC-07. NIST SP 800-161 Rev. 1. SLSA framework. CISA/NSA/FBI AI Data Security CSI (May 2025).
