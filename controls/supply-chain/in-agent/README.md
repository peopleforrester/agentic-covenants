# Supply chain / In-agent

**Control.** Model warns about unvetted packages or unfamiliar MCP servers.

**Strength.** Unreliable. Frequently wrong about provenance. Listed for completeness; the real defenses are at client-side and server-side.

## Tooling

None.

## Files in this directory

- [`supply-chain-warning-prompt.md`](./supply-chain-warning-prompt.md) — language to drop in the system prompt that tells the agent to flag, not silently install, any package or MCP server it has not seen before.

## Verification

You cannot verify this layer. Models hallucinate package names with non-trivial frequency (Khati et al. document ~24% of hallucinated imports in code generation pointing to nonexistent packages); a model that warns on its own hallucinations would be miscalibrated in the other direction.

## Common mistakes

- Treating a model's "this looks safe" as a safety signal.
- Asking the model whether a package is well-maintained. The model has no real-time signal.

## Citation

Advisory; no direct framework mapping. Thematic: NIST AI RMF MAP 4.1 (third-party risks identified). OWASP LLM03 (Supply Chain), related risk. OWASP ASI04 (Agentic Supply Chain Vulnerabilities) — mitigation principle.
