# Restorations — Supply chain / Client-side

**Precondition.** Interventions L2-C5 has fired (suspect MCP removed from allowlist, packages quarantined, lockfiles locked). Restorations identity, authorization, blast-radius, and approval-gating rows complete. **A clean MCP allowlist source has been verified** (signed commits, off-cluster mirror, not the possibly-tainted local copy).

**Authority.** On-call.

## Tooling

- `cosign` for signature verification on the agent runtime install.
- `pip-audit`, `npm audit`, `trivy`, `cargo audit`, `go vuln` — whichever apply.
- A repo with the canonical `mcp-allowlist.json` under signed-commit branch protection.

## Files in this directory

- [`agent-restore-supply-chain-local`](./agent-restore-supply-chain-local) — runbook script. Reinstalls agent runtime with cosign verification, copies a fresh `mcp-allowlist.json` from clean source (overwriting the post-incident local copy), removes `chattr +i` from lockfiles, regenerates lockfiles from manifest, runs vulnerability scan.

## Verification

```bash
# 1. Agent runtime signature verifies
cosign verify-blob --signature /usr/local/bin/claude.sig /usr/local/bin/claude

# 2. MCP allowlist matches clean source
md5sum /etc/agents/mcp-allowlist.json controls/supply-chain/client-side/mcp-allowlist.json

# 3. Lockfiles editable (chattr +i removed)
lsattr /etc/agents/claude-code-prod/package-lock.json
# expected: 'i' attribute absent

# 4. Vulnerability scan clean
pip-audit --requirement requirements.txt --strict
npm audit --audit-level=high
```

## Common failure modes

- Re-pin to "current" pins to a poisoned current. Pin to a hash from before the earliest indicator of compromise, even if a newer version exists.
- Lockfile regenerated against a still-tainted manifest. Verify manifest before regen.
- Signature verification accepts the same compromised key — if there's any chance the signing identity itself was exposed, the server-side row's key-rotation step must run first.

## Citation

NIST CSF 2.0 RC.RP-01. NIST AI RMF MANAGE 3.1. OWASP ASI04, ASI06. OWASP MCP04, MCP09.
