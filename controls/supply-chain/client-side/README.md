# Supply chain / Client-side

**Control.** MCP server allowlist with manifest hash pinning. Tool-description hashing on first approval (rug-pull defense). Sigstore signature verification before install. Lockfile pinning paired with server-side integrity validation. Pre-commit dependency scan. Reject unsigned MCP servers at handshake.

**Strength.** Deterministic for the artifacts named in the allowlist. Bypassable if the agent can write to `mcp-allowlist.json`, `package-lock.json`, or other lockfiles; through tool-description rug-pull when the MCP server's descriptions are not re-hashed at every handshake; through `--no-verify` on pre-commit.

## Tooling

- `cosign` for Sigstore signature verification.
- `syft` and `grype` (or Trivy) for SBOM and vulnerability scanning.
- A skill-scanning tool: SkillCheck, ToxicSkills, SecureClaw, Snyk agent-scan, or `mcp-scanner`.
- Lockfile linters: `npm-lockfile-fixed`, `pip-audit`, `cargo-audit`.

## Files in this directory

- [`mcp-allowlist.json`](./mcp-allowlist.json) — declarative allowlist of approved MCP servers with binary `sha256`, `tool_descriptions_sha256`, and per-server `permissions` scope. Owned by the operator; the agent's user must not have write permission on this file.
- [`mcp-launch`](./mcp-launch) — wrapper that verifies the binary's `sha256` against the allowlist before `exec`, and calls `cosign verify-blob` if a signature is present. Refuses to start if the server is not allowlisted or the hash mismatches.
- [`mcp-verify-tools.py`](./mcp-verify-tools.py) — runs after the MCP handshake, hashes the returned tool descriptions in a canonical order, compares to `tool_descriptions_sha256` in the allowlist. Mismatch → block + re-approve flow. **This is the rug-pull defense.**
- [`pre-commit-deps-scan.yaml`](./pre-commit-deps-scan.yaml) — extension to `.pre-commit-config.yaml` adding `pip-audit` and `trivy-fs` hooks. The server-side lockfile-integrity job in [`../server-side/lockfile-integrity.yml`](../server-side/lockfile-integrity.yml) is the backstop when `--no-verify` is used.

## Verification

```bash
# 1. Allowlist enforcement
mcp-launch unknown-server
# expected: "not in allowlist"

# 2. Hash mismatch detection
echo "extra byte" >> /usr/local/bin/mcp-filesystem
mcp-launch filesystem
# expected: sha256 mismatch
git checkout -- /usr/local/bin/mcp-filesystem  # revert

# 3. Tool description rug-pull detection
# Modify a tool description in a running MCP server's source; restart;
# verify mcp-verify-tools.py blocks with the expected/actual hashes.

# 4. Pre-commit catches a known CVE
echo "django==1.0.0" >> requirements.txt
git add requirements.txt && git commit -m "test"
# expected: failure at pip-audit

# 5. Cosign verification
cosign verify-blob \
  --signature /usr/local/bin/mcp-filesystem.sig \
  --certificate /usr/local/bin/mcp-filesystem.cert \
  /usr/local/bin/mcp-filesystem
# expected: success against your signing key
```

## Common mistakes

- Allowlist with no hash pinning. The supply-chain bypass is "trusting npm publication" (postmark-mcp, September 2025).
- Tool-description hash captured but not re-checked at every handshake. The rug-pull works because day-7's description is different from day-1's.
- Lockfile pinning without server-side integrity validation. The agent edits `package-lock.json` and pins a malicious version; without server-side validation, the malicious version is now self-attesting.
- Pre-commit dependency scan that runs only on the operator's machine. `--no-verify` skips it. The same scan must run server-side.
- Skill allowlist that approves whole publishers. ClawHavoc (1,184+ malicious skills) demonstrated that publisher trust does not transfer to individual skills.

## Citation

NIST CSF 2.0 PR.PS-02, PR.PS-01, ID.SC-04 (supplier integrity verified). NIST AI RMF MAP 4.1, MANAGE 3.1 (third-party risk treatment). OWASP LLM03 (Supply Chain), LLM04 (Data and Model Poisoning). OWASP ASI04 (Agentic Supply Chain Vulnerabilities), ASI06 (Memory & Context Poisoning). NIST SP 800-218 v1.1 PS.2. NIST SP 800-218A (Generative AI Profile of SSDF). OWASP MCP01, MCP03, MCP04.
