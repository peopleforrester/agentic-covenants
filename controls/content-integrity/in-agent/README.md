# Content integrity: in-agent

**Advisory, and weaker here than anywhere else in this framework.**

Everywhere else, the in-agent layer is weak because a model can be argued out of an instruction. Here it is weak for a sharper reason: **this layer is the attack surface**. A prompt injection is an attack aimed precisely at the mechanism this cell relies on. Hardening the system prompt is hardening the thing the adversary is directly optimizing against.

This cell is not empty, because unlike blast radius and supply chain there is something real to do. It is populated with an explicit ceiling on what it buys you.

## What belongs here

| Technique | What it buys | What it does not |
|---|---|---|
| **Instruction hierarchy** | Stating that system instructions outrank content encountered in tool results raises the bar for casual injection | Does not survive a determined multi-turn setup, and the model has no reliable way to tell a tool result from an instruction once both are text |
| **Provenance framing** | Wrapping untrusted content in explicit delimiters with a "this is data, not instruction" preamble measurably reduces naive injection | Delimiters can be spoofed by content that closes them |
| **Refusal training on known patterns** | Catches the published, obvious attacks | Catches yesterday's attacks. The corpus is public, so it is also the adversary's test set |
| **Output shape constraints** | Requiring structured output makes some exfiltration channels awkward | Awkward is not blocked |

## The honest ceiling

Treat everything in this cell as **reducing the volume of low-effort attacks so the probabilistic scanners downstream have less to score**. That is worth something. It is not a control, and it must never be cited as one in a risk register.

If a threat model says "prompt injection is mitigated by system-prompt hardening," the threat model is wrong. The correct statement is that injection is *bounded* by what the agent's credentials, sandbox, and egress policy permit after the injection succeeds. Those live in [`controls/authorization/`](../../authorization), [`controls/blast-radius/`](../../blast-radius), and [`server-side/`](../server-side).

## Artifact

[`untrusted-content-framing.md`](./untrusted-content-framing.md) is a template for wrapping tool results and retrieved documents before they enter context.

## Verification

There is no verification block for this cell, and that absence is deliberate. You cannot verify a prompt-level mitigation the way you verify an admission policy: there is no manifest that either loads or does not. The closest available thing is adversarial evaluation, which measures a rate rather than proving a property, and which belongs in assurance. See [`ASSURANCE.md`](../../../framework/ASSURANCE.md).

A cell that cannot be verified should say so rather than offering a check that proves nothing.
