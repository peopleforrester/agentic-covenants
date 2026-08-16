# Interventions, Supply chain / Client-side

**Trigger.** MCP allowlist violation, tool-description hash mismatch, lockfile diff with unsigned package, pre-commit dependency scan finding.

**Authority.** On-call.

**Speed target.** Under 60 seconds.

## Tooling

- The MCP allowlist layout from [`../../../controls/supply-chain/client-side/`](../../../controls/supply-chain/client-side/).
- `chattr` for locking lockfiles.

## Files in this directory

- [`agent-quarantine-supply-chain-local`](./agent-quarantine-supply-chain-local), runbook script. Removes the suspect server from `mcp-allowlist.json`, moves suspect package files to `/var/quarantine/<incident>/`, sets `chattr +i` on lockfiles, pins runtime to last-known-good, kills the agent so the new state applies.

## Verification

```bash
# 1. Suspect removed from allowlist
jq '.servers | has("filesystem-bad")' /etc/agents/mcp-allowlist.json
# expected: false

# 2. Quarantine populated
ls -la /var/quarantine/

# 3. Lockfile immutable
lsattr /etc/agents/claude-code-prod/package-lock.json
# expected: 'i' attribute present
```

## Common mistakes

- Quarantining files but missing in-memory state, Python with already-imported modules keeps the malicious code loaded. The kill step is mandatory.
- `chattr +i` on a file in tmpfs, does not stick across reboot. Mitigate by ensuring lockfile lives on persistent FS.
- Forgetting that the agent may have credentials cached in OS keychain that the quarantined package planted.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02. NIST AI RMF MANAGE 3.1. OWASP ASI04, ASI06. OWASP MCP04, MCP09.
