# Agentic governance: executive brief

**One page. For a CISO, CIO, or authorizing official deciding whether this needs funding this quarter.**

---

## The finding that should decide this

Of organizations that reported a security incident involving an AI model or application, **92% were missing role-based access, multifactor authentication, and similar controls** on those models and applications.

*IBM Cost of a Data Breach 2026, published 29 July 2026.*

That is not a statement about model quality, prompt engineering, or vendor choice. It is a statement that the incidents happened where the ordinary access controls were absent. The gap is infrastructure, and infrastructure is a thing you can fund and verify.

## What is different about an agent

A conventional application does what it was written to do. An agent decides what to do at runtime, then acts with whatever credentials it holds.

That single difference breaks the assumption every existing control rests on. You can no longer enumerate the actions in advance, so you cannot review them in advance. What you can still do is bound what the agent is *able* to do, which is the same discipline you already apply to a contractor, a service account, or a junior engineer on their first week.

**The governing constraint: anything an agent can be told, it can be talked out of.** Instructions, refusals, and "are you sure" prompts are advisory. They are worth having and they are not evidence of control. A widely reported 2025 incident had a coding agent delete a production database during an explicit action freeze, after being instructed eleven times not to act.

## The three questions to ask your team

1. **Can you list every agent running against our systems, and who is accountable for each?** If the answer takes more than a day, the exposure is unmeasured rather than small.
2. **If an agent tried to do the worst thing it could do, what would stop it, and is that thing outside the agent?** "It would refuse" is not an answer. "The IAM policy denies it" is.
3. **Would we know within two days?** From 2 August 2026, EU AI Act Article 73 sets a two-day reporting clock for serious and irreversible disruption of critical infrastructure, and 15 days generally.

## The numbers

| | |
|---|---|
| Average cost of a data breach, 2026 | **USD 4.99M**, up 12% year over year, a record |
| Average cost when the breach was AI-enabled | **USD 6M**, about USD 1M above the global average |
| Share of malicious breaches that were AI-enabled | **1 in 4**, up 56% in one year |
| Organizations with an AI-model incident that lacked access controls | **92%** |
| Security incidents involving unapproved AI tools | **43%**, more than double the prior year |
| Savings where AI and automation were used in security operations | **~USD 2M** per breach |

*All figures: IBM Cost of a Data Breach 2026.*

## What good looks like

A five-level maturity model, scored as the **minimum across five concerns rather than the average**, because an agent looking for a way out takes the open path rather than the mean one.

| Level | State | Typical effort to reach |
|---|---|---|
| **0** | Ungoverned. The security posture is the system prompt | Where most deployments are now |
| **1** | Named. Each agent has its own revocable identity and an accountable owner | Days |
| **2** | Bounded. Deny-by-default, enforced without consulting the model | About a week |
| **3** | Contained. Blast radius bounded by the operating system | Two to three weeks |
| **4** | Observed and reversible. Detected off-box, stoppable, rehearsed recovery | A quarter |

**Level 2 is the defensible minimum** and is achievable inside a normal sprint. Level 4 is where the Article 73 clock becomes meetable.

## The ask

Fund the assessment first, not the tooling. A read-only assessment across your agent estate takes about an hour per agent and produces a level, a binding constraint, and a cost for the next level. Buying controls before knowing which are absent is how organizations end up with a second copy of something they already had.

## What this is not

Not a product, not a compliance certification, and not a claim that any control here is unbypassable. Every control has a documented bypass, which is why the framework specifies three independent layers rather than one. Federal crosswalks are a starting point for a conversation with an authorizing official, not a determination.

---

**Full framework:** [`README.md`](./README.md) · **Cost model:** [`ECONOMICS.md`](./ECONOMICS.md) · **Maturity model:** [`examples/claude-code-laptop/MATURITY.md`](./examples/claude-code-laptop/MATURITY.md) · **Assessment sheets:** [`checklists/`](./checklists/)
