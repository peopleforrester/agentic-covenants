# Charter — Supply chain / Agent

**Structural question.** Does the agent charter declare specific dependencies (named foundation model, MCP servers with hashes, base image digest, runtime version), and require charter amendment for changes?

**Owner.** Named human owner. Counter-signed by domain authority.

## Template fragment

The `dependencies:` block of [`../../templates/agent-charter.yaml`](../../templates/agent-charter.yaml):

```yaml
dependencies:
  foundation_model: claude-opus-4-7
  foundation_model_pinned_at: 2026-04-15
  mcp_server_hashes:
    filesystem: sha256:REPLACE_WITH_ACTUAL_SHA256
    github: sha256:REPLACE_WITH_ACTUAL_SHA256
  base_image: ghcr.io/example-org/claude-agent
  base_image_digest: sha256:REPLACE_WITH_DIGEST_FROM_CRANE
  agent_runtime_version: 2.1.40
  pinned_at: 2026-04-15
```

## Audit prompts

- For [agent X], does the charter `mcp_server_hashes` match the runtime [`controls/supply-chain/client-side/mcp-allowlist.json`](../../../controls/supply-chain/client-side/mcp-allowlist.json) entries?
- Does `base_image_digest` match the deployed pod's resolved digest?
- When was each dependency last pinned? When was it last reviewed?

## Operational tie-in

- `mcp_server_hashes` is the source-of-truth for [`controls/supply-chain/client-side/mcp-allowlist.json`](../../../controls/supply-chain/client-side/mcp-allowlist.json). Drift between charter and allowlist is a Sentinels finding.
- `base_image_digest` is the value that should be pinned in [`controls/identity/server-side/pod-with-projected-token.yaml`](../../../controls/identity/server-side/pod-with-projected-token.yaml) and verified by [`controls/supply-chain/server-side/kyverno-verify-image-signatures.yaml`](../../../controls/supply-chain/server-side/kyverno-verify-image-signatures.yaml).
- `agent_runtime_version: 2.1.40` is the May 2026 PreToolUse precedence patch line — pre-patch versions of Claude Code allow the deny-bypass regression. The charter must reflect the patched version.

## Common failure mode

Manifest is updated in Charter but allowlist hashes in Covenants L2-C5 are not regenerated. Charter and runtime drift apart. Charter says one model, agent uses another. The fix is automation that derives the runtime allowlist from the charter file at deploy time.

## Citation

NIST CSF 2.0 GV.SC-07; ID.RA-09 (authenticity and integrity assessed prior to acquisition). NIST AI RMF GOVERN 6.2, MAP 4.1. ISO/IEC 42001 §A.10. EU AI Act Art. 25. OWASP MCP04, MCP09.
