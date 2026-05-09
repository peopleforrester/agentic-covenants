# Supply chain

**Intent.** Every dependency, MCP server, registry, container image, and tool description verified before trusted. The agent operates only on artifacts whose provenance the operator can name and whose integrity the cluster can verify.

## The row, at a glance

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | A "warn before installing unvetted packages" prompt. Frequently wrong. Listed for completeness. |
| Client-side | [`client-side/`](./client-side/) | MCP allowlist with manifest hash pinning, **tool-description hashing on first approval (rug-pull defense)**, Sigstore signature verification before install, lockfile pinning paired with server-side integrity validation, pre-commit dependency scan, reject unsigned MCP servers at handshake. |
| Server-side | [`server-side/`](./server-side/) | Image registry restrictions in admission policy, OCI signature verification (cosign), SBOM admission requirements, egress NetworkPolicy to approved registries only, OPA policy denying images without provenance attestation, SLSA build-provenance attestation gates, MCP domain allowlist enforced at the network layer (Cilium FQDN policy). |

## Why it matters

The two highest-impact agent supply-chain incidents through May 2026 — **postmark-mcp** (September 2025) and **ClawHavoc** (1,184+ malicious skills) — both exploited the same gap: trust transferred from a publisher to an artifact without per-artifact verification. postmark-mcp was a signed npm package whose code changed between approval and use; ClawHavoc was a marketplace where publisher trust was assumed to extend to every skill the publisher uploaded.

This row defends against that pattern with three controls applied at different layers:

1. **Hash pinning at install.** The artifact you ran today must be byte-for-byte identical to the artifact you approved.
2. **Tool-description hashing.** When an MCP server's tool descriptions change, the agent treats it as a new server and re-prompts the operator. Defeats the rug-pull where day-7's description is a malicious mutation of day-1's.
3. **Signature verification at admission.** The cluster refuses to run an image whose provenance does not match a trusted issuer.

## How to walk it

For each layer ask: *if a dependency, tool, or image is malicious, what stops the agent from running it at this layer?*

- **In-agent only:** the model warns, sometimes. It is wrong about supply-chain provenance more often than it is right.
- **Client-side adds:** the MCP server's hash is verified before launch; lockfiles are pinned (and an agent that edits the lockfile is detected by the server-side lockfile-integrity check); pre-commit catches known CVEs in dependencies; tool descriptions are hashed and a rug-pull triggers a re-approval.
- **Server-side adds:** the cluster admission policy refuses images without a cosign signature from a trusted GitHub OIDC subject; SBOMs are required as attestations; egress is allowlisted to known-good MCP and registry domains only; the lockfile-integrity CI job runs even when `--no-verify` was used locally.

## A note on lockfile pinning

Lockfile pinning is **only** meaningful when paired with server-side integrity validation in CI. A lockfile alone does not protect against an agent that can edit `package-lock.json`, `requirements.txt`, `Pipfile.lock`, `go.sum`, or `Cargo.lock`. The agent edits the lockfile to pin a malicious version, and the lockfile is now self-attesting that the malicious version is the legitimate one. The server-side lockfile-integrity job in [`server-side/lockfile-integrity.yml`](./server-side/lockfile-integrity.yml) is what makes lockfiles a real control.

## Citations (per layer)

See [`../../CITATIONS.md`](../../CITATIONS.md). Quick reference:

- **In-agent**: advisory; thematically MAP 4.1 (third-party risks identified); OWASP LLM03; OWASP ASI04 (Agentic Supply Chain Vulnerabilities) — mitigation principle.
- **Client-side**: NIST CSF 2.0 PR.PS-02, PR.PS-01, GV.SC-07 (risks from suppliers identified, recorded, prioritized, assessed); NIST AI RMF MAP 4.1, MANAGE 3.1 (third-party risk treatment); OWASP LLM03 (Supply Chain), LLM04 (Data and Model Poisoning); OWASP ASI04, ASI06 (Memory & Context Poisoning); NIST SP 800-218 PS.2; NIST SP 800-218 Rev. 1 draft (Dec 17, 2025); NIST SP 800-218A (Generative AI Profile of SSDF); OWASP MCP01, MCP03, MCP04.
- **Server-side**: NIST CSF 2.0 PR.PS-02, PR.PS-05, PR.IR-01, GV.SC-07 (supplier integrity), ID.RA-09 (authenticity and integrity of hardware and software assessed prior to acquisition and use); NIST AI RMF MAP 4.1, MANAGE 3.1; OWASP LLM03, LLM04; OWASP ASI04; OWASP MCP04, MCP09; NIST SP 800-218 PS.3; NIST SP 800-161 Rev. 1 (supply chain risk management); SLSA framework (build provenance); CISA/NSA/FBI AI Data Security CSI (May 2025); CISA/ASD ACSC OT Principles (Dec 2025).
