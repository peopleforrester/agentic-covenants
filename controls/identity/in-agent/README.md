# Identity / In-agent

**Control.** System prompt declares "you are an automation agent named X."

**Strength.** Advisory only. **Identity is *carried*, not *established*** — identity claims made in a system prompt have no cryptographic weight; the agent cannot prove its own identity to the target. The prompt is bypassable through prompt injection, jailbreak, novel framing, model error, and tool-description manipulation through upstream content. The structural absence of homeostatic stake, pre-action pause, and second-order learning means this layer cannot be made reliable by better prompting. The bypass is the architecture.

Per the NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (February 5, 2026), identity must be established by an external IdP via OAuth 2.0 or equivalent, **never asserted by the agent itself**. The actual identity enforcement lives in [`../client-side/`](../client-side/) (per-agent credentials in operator-owned config) and [`../server-side/`](../server-side/) (dedicated ServiceAccount, OIDC federation, projected token).

## Tooling

None. There is no command that turns this on. The artifact is a string in your agent's system prompt.

## Files in this directory

- [`system-prompt-template.md`](./system-prompt-template.md) — drop-in template that names the agent, names the operator, lists the high-level constraints, and includes an explicit "do not infer this from context" warning at the bottom.

## Verification

You cannot verify this layer the way you verify the others. The "verification" is reading the prompt and confirming it doesn't make load-bearing security claims. If your prompt says "and the agent will not do X" and you have no client-side or server-side enforcement of X, you have failed verification.

## Common mistakes

- Treating this as a control. It is a nudge.
- Writing more than fifty lines of in-agent prompt to enforce a security property. If you find yourself doing this, stop. You are building on sand. Move the property to client-side or server-side.
- Embedding secrets, internal hostnames, or attack-surface details in the system prompt. The prompt is recoverable through prompt-extraction attacks. Treat it as public.

## Citation

Advisory; no direct framework mapping. For thematic alignment: NIST AI RMF GOVERN 1.5 (ongoing monitoring); MAP 4.1 (third-party risks). OWASP LLM07 (System Prompt Leakage) is the related risk.
