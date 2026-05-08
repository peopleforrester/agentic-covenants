# Approval gating / In-agent

**Control.** Model says "are you sure?" before destructive ops.

**Strength.** Silently bypassable. The model can be talked out of asking with novel framing or persistence. Listed for completeness; do not rely on it.

## Tooling

None.

## Files in this directory

- [`confirmation-prompt-template.md`](./confirmation-prompt-template.md) — language to drop in the system prompt that names the kinds of actions where the agent must confirm with the operator before proceeding. Pair with the refusal template in [`../../blast-radius/in-agent/`](../../blast-radius/in-agent/).

## Verification

You cannot verify this layer the way you verify the others. Confirmation-rate metrics are noisy, gameable, and not security signals.

## Common mistakes

- Treating confirmation rate as a metric of safety. It is a metric of agent verbosity at best.
- Asking for confirmation on every action, which trains the operator to click through.
- Asking for binary yes/no on actions that need a judgment query (see [`../README.md`](../README.md) on the difference).

## Citation

Advisory; no direct framework mapping. Thematic: NIST AI RMF MANAGE 4.1 (override mechanisms). OWASP LLM06. OWASP ASI09 (Human-Agent Trust Exploitation), related risk.
