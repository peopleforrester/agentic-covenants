# Blast radius / In-agent

**Control.** Model declines destructive operations.

**Strength.** Verified failure mode. Documented incidents in Kiro, Replit, and DataTalks.Club where the model proceeded with destructive operations despite training to refuse. Treat as nudge.

## Tooling

None.

## Files in this directory

- [`refusal-prompt-template.md`](./refusal-prompt-template.md) — drop-in language for the system prompt that explicitly enumerates destructive operations the agent should refuse. Pair with the constraints block in [`../../identity/in-agent/system-prompt-template.md`](../../identity/in-agent/system-prompt-template.md).

## Verification

You cannot verify this layer the way you verify the others. The "verification" here is a red-team test: run the agent against a set of prompts that try to coax it into a destructive operation. Track the refusal rate. Refuse to call the result a "control" no matter how high the rate.

## Common mistakes

- Treating the refusal rate as a security metric. It is a model-quality metric. Security comes from client-side and server-side enforcement.
- Writing extensive enumerations of destructive ops in the prompt. Long lists are ignored or contradicted by later context.
- Assuming "stronger" models refuse better. Capability and refusal are loosely correlated and not monotonic across model versions.

## Citation

Advisory; no direct framework mapping. Thematic: NIST AI RMF MAP 5.1; MEASURE 2.6 (safety risks evaluated). OWASP LLM06 (Excessive Agency). OWASP ASI02, ASI05.
