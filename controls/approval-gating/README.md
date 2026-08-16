# Approval gating

**Intent.** Friction scaled to risk. Trivial actions pass through; routine actions get a quick confirm; high-risk actions require typed verbatim re-entry; production-touching actions require an out-of-band channel; value-laden decisions get escalated to the operator as a judgment query, not a yes/no.

## The row, at a glance

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | A confirmation-prompt template the model uses before destructive ops. Silently bypassable; the model can be talked out of asking. |
| Client-side | [`client-side/`](./client-side/) | Tiered PreToolUse hook (extends the deny hook from Authorization with tier-3 typed confirmation, tier-4 out-of-band approval, session destructive-action counter), and a judgment-query escalation tool the agent calls explicitly when it hits a value-laden decision. |
| Server-side | [`server-side/`](./server-side/) | Branch protection with `enforce_admins=true` (the load-bearing flag), CODEOWNERS on critical paths, GitHub environments with required reviewers on the IaC apply job, deployment-freeze automation triggered by active PagerDuty incidents, and an hourly drift-detection job comparing live branch protection to a checked-in expected JSON. |

## Why it matters

This row is what people mean when they say "human in the loop." Done well, it is the single most operationally useful row in the matrix: it lets you ship agents that touch real systems without ceding judgment.

Done badly, it is the **alert-fatigue** row, and alert fatigue is the failure mode the row exists to fight. The cure is **tiering**, most actions auto-allow, only the dangerous ones interrupt, and **judgment-query escalation** for the small set of decisions that need genuine human input rather than a rubber-stamp click.

## How to walk it

For each layer ask: *if the agent attempts a high-risk action, what friction does it encounter at this layer, and is that friction proportional to the blast radius?*

- **In-agent only:** the model says "are you sure?" The agent can be talked out of asking, and the operator can be lulled into clicking through.
- **Client-side adds:** typed verbatim confirmation for tier-3, out-of-band channel (Slack approval, FIDO2 prompt, separate terminal) for tier-4, session counter so the agent cannot loop on destructive actions. Pattern matching catches obvious destructive verbs; equivalent commands like `kubectl scale --replicas=0` defeat it. Document this and move it to server-side.
- **Server-side adds:** the change cannot reach production without a PR review by a CODEOWNER, an environment-gated apply job, and an unbroken branch-protection state. Bypass requires admin override (which `enforce_admins=true` blocks) or social-engineering through a persuasive PR description.

## Important: `enforce_admins=true`

The single most common branch-protection failure is leaving `enforce_admins` at its historical default of `false`. With it false, anyone with admin role on the repo walks through every other rule. **Verify with `gh api repos/:owner/:repo/branches/main/protection --jq '.enforce_admins.enabled'`.** It must return `true`.

The "Do not allow bypassing the above settings" checkbox in the GitHub UI is the same setting. Use the API; UI clicks are not auditable.

## Judgment-query escalation vs approval

These are different controls, frequently confused:

- **Approval** is a yes/no on a specific proposed action. The agent says "I'm about to run X." The operator says "yes" or "no." Susceptible to alert fatigue because the answer is binary and almost always yes.
- **Judgment-query escalation** is "I cannot generate this input; you must." The agent says "I'm about to make a tradeoff between A and B; both are reasonable; you decide." The operator supplies the missing input. Resistant to fatigue because the frequency is bounded by genuine novelty.

The agent platform's tooling support for the second pattern is limited as of May 2026. The wrapper-layer implementation in [`client-side/escalate.py`](./client-side/escalate.py) is illustrative.

## Citations (per layer)

See [`../../CITATIONS.md`](../../CITATIONS.md). Quick reference:

- **In-agent**: advisory; thematically NIST AI RMF MANAGE 4.1 (override mechanisms); OWASP LLM06; OWASP ASI09 (Human-Agent Trust Exploitation).
- **Client-side**: NIST CSF 2.0 PR.AA-05, PR.PS-01; NIST AI RMF MANAGE 4.1 (post-deployment monitoring, appeal and override); OWASP LLM06; OWASP ASI02, ASI09; OWASP Agentic Least Agency principle; assistance-games framing (Russell, 2019); EU AI Act Art. 14 (human oversight); Singapore IMDA "meaningful human accountability."
- **Server-side**: NIST CSF 2.0 PR.AA-05, PR.PS-01, GV.RR-02; NIST AI RMF GOVERN 4.1, MANAGE 4.1; OWASP LLM06; OWASP ASI02, ASI03; EU AI Act Art. 14, Art. 26; ISO/IEC 42001 §A.4; NIST SP 800-160 Vol. 1 (separation of duties).
