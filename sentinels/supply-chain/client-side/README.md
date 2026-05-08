# Sentinels — Supply chain / Client-side

**Control.** mcp-launch wrapper logs every connection attempt with status (`ok | hash_mismatch | not_in_allowlist`). Tool-description hash mismatch alerts on rug-pull. Lockfile diff in CI shipped to SIEM. Pre-commit dependency scan results centralized.

**Strength.** Deterministic when emit happens. Failure modes: MCP wrapper logs only successful connections (failures and rejections are the interesting events); lockfile diff log includes the entire diff for huge PRs (truncate to first 200 lines); tool-description hash mismatch suppressed on legitimate update (the mismatch is the alert; reapproval is a separate workflow).

## Tooling

- The mcp-launch wrapper from [`../../../controls/supply-chain/client-side/mcp-launch`](../../../controls/supply-chain/client-side/mcp-launch).
- The mcp-verify-tools.py script from [`../../../controls/supply-chain/client-side/mcp-verify-tools.py`](../../../controls/supply-chain/client-side/mcp-verify-tools.py).
- The lockfile-integrity workflow from [`../../../controls/supply-chain/server-side/lockfile-integrity.yml`](../../../controls/supply-chain/server-side/lockfile-integrity.yml).

## Files in this directory

- [`mcp-launch-emit.sh`](./mcp-launch-emit.sh) — append-only snippet that the mcp-launch wrapper sources to emit a structured per-connection event including status and hash.
- [`tool-desc-mismatch-emit.py`](./tool-desc-mismatch-emit.py) — patch fragment for `mcp-verify-tools.py` that emits a structured event on hash mismatch (the rug-pull alert).
- [`ci-lockfile-diff.yml`](./ci-lockfile-diff.yml) — workflow extension that ships the truncated lockfile diff to SIEM on every PR that touches a lockfile.

## Verification

```bash
# 1. MCP allowlist violation logged
mcp-launch unknown-server || true
journalctl -t agent-sentinel --since "1 minute ago" | grep mcp_connect
# expected: status: not_in_allowlist event

# 2. Tool-description mismatch logged
# Modify a tool description in a running MCP server's source; restart.
journalctl -t agent-sentinel | grep mcp_tool_desc_mismatch

# 3. Lockfile diff in SIEM
# Open a PR with a lockfile change; check SIEM for the lockfile_diff event.
```

## Common mistakes

- MCP wrapper logs only successful connections. The interesting events are failures and rejections.
- Lockfile diff log includes the entire diff for huge PRs. Truncate to first 200 lines.
- Tool-description hash mismatch suppressed on legitimate update. The mismatch is the alert; reapproval is a separate workflow.

## Citation

NIST CSF 2.0 DE.CM-09, ID.RA-09. OWASP MCP08, MCP09.
