# Authorization / In-agent

**Control.** Model instructions and tool descriptions that scope each tool to its safe operations and explicitly say what the tool is not for.

**Strength.** Advisory only. Model instructions are bypassable. Tool descriptions are slightly more durable because the model uses them for its own decision-making, but they are still not enforcement.

## Tooling

None. The artifact is text in the system prompt and in each tool's `description` field.

## Files in this directory

- [`tool-description-template.md`](./tool-description-template.md), drop-in template for a tool description that names the tool's purpose, lists what it must not be used for, and includes a "if you are about to do X, stop and ask" line.

## Verification

You cannot verify this layer the way you verify the others. The "verification" is a lint that confirms each tool description has scope and exclusion language. A linter like `mcp-scanner` (see [`../../supply-chain/client-side/`](../../supply-chain/client-side/)) can enforce a basic pattern.

## Common mistakes

- Tool descriptions that say what the tool *can* do but not what it must not do. The asymmetry matters; models will assume capability when scope is silent.
- Treating the description as documentation for humans. The model reads it. Write it for the model first, the operator second.
- Embedding examples of forbidden inputs in the description. Models pattern-match; an example of a forbidden command can become a template the model uses.

## Citation

Advisory; no direct framework mapping. Thematic: NIST AI RMF MAP 5.1 (likelihood and magnitude of impacts documented). OWASP LLM06 (Excessive Agency), mitigation principle. OWASP ASI02 (Tool Misuse), mitigation principle.
