# Examples

End-to-end deployments that wire the matrix cells together for a specific environment. Each example says what it assumes, what it substitutes, and what it does not solve.

| Example | Environment | Status |
|---|---|---|
| [`dod-air-gapped/`](./dod-air-gapped/) | DoD IL4–IL5 enclave, no internet egress. Self-hosted or offline Sigstore, enclave registry, ICAM NPE identity binding, in-tree admission policy. | Available |
| `claude-code-laptop/` | Single operator workstation. Sandbox at launch, PreToolUse hooks, per-agent credentials, MCP allowlist. | Planned |
| `github-actions-pipeline/` | CI/CD agent. Gated IaC apply, branch protection, lockfile integrity, cosign signing. | Planned |
| `kubernetes-cluster/` | Multi-agent cluster. Per-agent ServiceAccount, Kyverno/VAP admission, NetworkPolicy, Falco, SBOM diff. | Planned |

The connected examples are largely assembled from artifacts already in [`controls/`](../controls/) and [`sentinels/`](../sentinels/); the air-gapped one is published first because its substitutions are the ones you cannot derive by reading the connected cells.

## How to use an example

1. Read the example's README end to end before copying anything. Each one documents assumptions that, if false in your environment, change which artifacts apply.
2. Copy artifacts into your own repo. **Every placeholder is intentional**, `REPLACE_WITH_DIGEST_FROM_CRANE`, `123456789012`, `registry.enclave.mil`. Substitute them deliberately; do not leave them.
3. Run the example's verification steps. An unverified control is a documented control, which is not the same thing.
4. Record what you skipped and why. Skipped cells belong in your threat model, not in a gap nobody wrote down.
