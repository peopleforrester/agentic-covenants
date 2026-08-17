# Content integrity

**The question:** if the agent is manipulated by the text it reads, or leaks through the text it writes, what catches it at this layer?

This is the sixth concern and the only one whose server-side column is deliberately weak. That is the finding, not an omission.

## Why this row is different from the other five

Identity, authorization, blast radius, approval gating, and supply chain all have a strong server-side answer. Something outside the agent makes a binary decision and the agent's opinion is irrelevant.

Content integrity has no such answer, because the failure is **semantic**. A prompt injection inside a retrieved document is well-formed text arriving over an authorized channel from an approved source. No admission controller can distinguish it from the document it is hiding in. The exfiltration case is worse: every individual action may be authorized, and only the aggregate is a leak.

So the controls here are **probabilistic**. They score and threshold rather than admit and deny. That means they have false positives, false negatives, and an evasion surface against an adversary who is trying. Treat them as **detection**, and never let a scanner's presence justify relaxing a deterministic control elsewhere.

## The three layers

| Layer | Control | Honest limitation |
|---|---|---|
| [**In-agent**](./in-agent/) | System-prompt hardening, instruction hierarchy, refusal training | Advisory, as everywhere in this framework. Worse here: the attack is aimed precisely at this layer, so it is the one surface the adversary is directly optimizing against |
| [**Client-side**](./client-side/) | Input scanning before the model sees the text, output scanning before it leaves, tool-result sanitization, provenance tagging of untrusted content | Scoring, so false positives and false negatives are inherent. Evadable by encoding, indirection, multi-turn setup, and translation |
| [**Server-side**](./server-side/) | Egress policy so exfiltration has nowhere to go, DLP at the boundary, audit of what was actually sent | Catches the consequence rather than the manipulation. The agent is already compromised by the time this fires |

## What actually works here

The strongest available control for this concern is not a scanner. It is **making a successful injection worthless**, which is a blast-radius problem rather than a content problem.

An agent that has been successfully injected can only do what its credentials, its RBAC, its sandbox, and its egress policy permit. If those are tight, the injection succeeds and accomplishes nothing. This is why [`controls/blast-radius/`](../blast-radius/) and [`controls/authorization/`](../authorization/) matter more to this concern than anything in this directory does.

Scanners narrow the funnel. They do not close it.

## The lethal trifecta

The practical risk rule for this concern. An agent is exposed when it has all three of:

1. Access to **private data**
2. Exposure to **untrusted content**
3. The ability to **communicate externally**

Remove any one and injection stops being an exfiltration path. This is a design constraint you apply when deciding what an agent is for, and it is cheaper than any scanner. A detector for the pattern is in [`sentinels/blast-radius/in-agent/lethal-trifecta-detector.py`](../../sentinels/blast-radius/in-agent/lethal-trifecta-detector.py).

## Tooling landscape

Named for evaluation, not endorsed. Each needs the same treatment every other control here gets: a pinned version, a working artifact, and a documented bypass.

| Tool | Role | Noted caveat |
|---|---|---|
| **LLM Guard** (Protect AI, MIT) | Input and output scanners: prompt injection, PII, secrets, toxicity | Bundles the Rebuff injection scanner, which is no longer primarily a standalone project |
| **NVIDIA NeMo Guardrails** | Programmable rails, can reject or rewrite before the model sees input | **NVIDIA states it is not recommended for production as-is in its current beta state.** Latest stable reported as v0.17.0, October 2025 |
| **Meta Llama Guard / Prompt Guard 2** | LLM-based classifiers for harm taxonomy and injection detection | A model classifying model input. Inherits the failure modes it is meant to catch |
| **Microsoft Presidio** (MIT) | PII detection and anonymization | Covers one category very well and is not a full guardrail layer. Do not present it as one |

Version and status claims above are as reported by secondary sources in August 2026. **Verify against the project's own repository before adopting**, per the currency discipline in [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## Cells

- [`in-agent/`](./in-agent/): prompt hardening, and why it is the weakest cell in the matrix
- [`client-side/`](./client-side/): scanning pipeline and provenance tagging
- [`server-side/`](./server-side/): egress containment and send-side audit

## Crosswalk

OWASP LLM Top 10 **LLM01** (prompt injection), **LLM02** (sensitive information disclosure), **LLM05** (improper output handling). OWASP Agentic **ASI02** (tool misuse). NIST AI RMF **MEASURE 2.7**. See [`CITATIONS.md`](../../CITATIONS.md).
