# The economics of agentic governance

What an incident costs, what the controls cost, and where the line sits between them.

**A note on sourcing before any number appears.** This document separates two kinds of figure, and never lets one borrow the other's authority:

- **Sourced.** Published, dated, attributed. Cited to the primary release where one exists.
- **Estimated.** Derived here from the artifacts in this repository. Labeled as an estimate every time, with the reasoning shown so you can substitute your own rates and disagree specifically.

Nobody publishes the cost of implementing agent controls, because the population is too new and too varied. Any document that presents such a figure as a benchmark is presenting an estimate in a benchmark's clothing. The estimates below are honest guesses with their working shown, and they should be replaced with your own numbers the moment you have them.

---

## Part 1: What an incident costs (sourced)

From **IBM Cost of a Data Breach 2026**, published 29 July 2026:

| Figure | Value |
|---|---|
| Global average cost of a breach | USD 4.99M, up 12% year over year, a record |
| Average when the breach was AI-enabled | USD 6M |
| Share of malicious breaches that were AI-enabled | 1 in 4, a 56% increase in one year |
| Organizations reporting a breach targeting AI models or applications | More than 20% |
| Of those with an AI model or application incident, share **missing role-based access, MFA, and similar controls** | **92%** |
| Security incidents involving workers' unapproved AI tools | 43%, more than double the prior year |
| Savings where AI and automation were used in security operations | Almost USD 2M per breach |

Outcomes of the unapproved-tool incidents: data loss or compromise about half the time, operational disruption in four out of ten, and roughly one in five drew a regulatory fine.

### The 92% is the whole argument

Read it carefully, because it is easy to round off into something weaker. It does not say AI caused the breaches. It says that among organizations that *had* an AI model or application incident, **92% did not have ordinary access controls on that model or application**.

Role-based access and MFA are not exotic. They are controls these organizations almost certainly applied to their databases, their cloud accounts, and their source repositories. They did not apply them to the AI system, and that is where the incident happened.

This is the strongest available evidence that the agentic gap is an infrastructure gap rather than a model-quality gap, and infrastructure is the category you already know how to fund, staff, and audit.

### The regulatory clock is now a cost line

**Since 2 August 2026**, EU AI Act Article 73 has required serious-incident reporting: 15 days generally, 10 days where a death may have been caused, and **2 days** for a widespread infringement or serious and irreversible disruption of critical infrastructure. Verify how the Digital Omnibus deferral of the high-risk obligations interacts with your specific system class before relying on this timeline.

The two-day clock converts detection from a maturity nicety into a compliance dependency. An organization that detects agent misbehavior in thirty days cannot report it in two, and the failure to report is separately actionable from the incident itself.

---

## Part 2: What the controls cost (estimated)

**These are estimates.** They are derived from the artifacts in this repository by counting the work each requires, at an assumed fully loaded cost of **USD 1,200 per engineer-day**. Substitute your own rate; the ratios are what matter.

Effort is expressed per agent estate rather than per agent, because most of the work is building the pattern once and applying it repeatedly. The marginal cost of the second agent is small, and this is the single most important property of the model.

| Level | Work required | Estimated first estate | Estimated per additional agent |
|---|---|---|---|
| **1 Named** | Provision a distinct credential per agent, register each in an inventory, name an accountable owner | 3 to 5 days | ~0.25 day |
| **2 Bounded** | Deny-by-default permission config, PreToolUse hook, protected-path enforcement, verify the deny path actually denies | 5 to 8 days | ~0.5 day |
| **3 Contained** | Sandbox at launch with inheritance, mount-set isolation of secrets, egress allowlist, MCP hash pinning | 10 to 15 days | ~1 day |
| **4 Observed** | Off-box log shipping, tiered approval with an out-of-band path, kill-switch drill, restoration rehearsal | 15 to 25 days | ~1 day |

**Cumulative estimate to Level 2**, the defensible minimum: roughly **8 to 13 engineer-days**, or **USD 10K to 16K** at the assumed rate.

**Cumulative estimate to Level 4**: roughly **33 to 53 engineer-days**, or **USD 40K to 64K**.

### Why the estimates are shaped this way

Level 2 is cheap because the artifacts already exist. The permission config and the hooks in [`controls/authorization/client-side/`](./controls/authorization/client-side/) are copy-and-substitute work, and the expensive part is not writing them but deciding what belongs on the deny list, which is a half-day conversation rather than an engineering project.

Level 3 is the step change, and the cost is concentrated in one requirement: **sandbox inheritance**. Applying a sandbox is easy. Guaranteeing that a process the agent spawns is subject to the same constraint requires getting the launch path right and then testing it, and it is the requirement most commonly claimed and least commonly verified.

Level 4 costs the most and is the only level whose cost is mostly **recurring**. Off-box logging has a monthly bill, and the drills have to be re-run when the estate changes. Budget it as run cost, not project cost.

---

## Part 3: Putting the two halves together

The comparison that matters is not "controls versus breach," because controls do not eliminate breach probability. It is the change in expected loss against the cost of the change.

The honest version of the arithmetic, with every input labeled:

| Input | Value | Kind |
|---|---|---|
| Cost of an AI-enabled breach | USD 6M | Sourced |
| Cost to reach Level 2 across an estate | USD 10K to 16K | **Estimated** |
| Reduction in annual probability of an AI-related incident from Level 0 to Level 2 | **Unknown** | **Not published by anyone** |

That third row is the one every vendor fills in and nobody can support. The population of governed agent estates is too young for a credible incidence study, and any percentage offered for it today is invented.

So the argument has to be made without it, which it can be:

**At USD 10K to 16K against a USD 6M event, the break-even is a probability reduction of roughly 0.2 to 0.3 percentage points.** Not 20%. A fifth of one percent. Given that 92% of organizations with an AI-model incident lacked exactly the controls Level 2 installs, a reduction that small is a conservative assumption rather than an optimistic one.

That is the whole case for Level 2, and it does not require anyone to believe a fabricated efficacy number.

**Level 4 is a harder sell on pure expected-loss grounds** and should usually be justified differently: on the Article 73 two-day clock if you are in scope, on contractual detection commitments, or on the observation that the recurring cost buys the ability to answer "what did the agent do" at all. Organizations that cannot answer that question tend to discover it during the incident, when the answer is most expensive.

### The cost of the assessment itself

Roughly **one hour per agent** using [`checklists/`](./checklists/), or seconds per workstation using [`examples/claude-code-laptop/assess.sh`](./examples/claude-code-laptop/assess.sh).

This is the highest-return spend in the document and the one most often skipped. Organizations routinely fund controls they already had while leaving the binding constraint untouched, because scoring by average hides the gap that scoring by minimum reveals.

---

## Part 4: What would change these numbers

State the conditions under which this document becomes wrong, so a later reader can tell staleness from disagreement:

- **A credible incidence study.** The moment someone publishes agent-incident rates by governance level, the unknown row above gets filled in and the argument should be rebuilt around it.
- **Platform defaults improving.** Several controls here exist because the platform does not enforce them. If sandbox-at-launch or deny-by-default becomes the shipped default, the Level 2 and Level 3 estimates fall sharply.
- **Regulatory scope changes.** The Digital Omnibus deferral is provisional. If Article 73's application to a given system class moves, the compliance-driven half of the Level 4 case moves with it.
- **A large public agentic incident with disclosed costs.** Present incident cost figures are averages across all breach types. A disclosed agentic incident with a real number attached would replace the USD 6M proxy with something specific.

---

## Sources

- IBM, *Cost of a Data Breach Report 2026*, announced 29 July 2026. [IBM newsroom release](https://newsroom.ibm.com/2026-07-29-ibm-study-one-in-four-malicious-breaches-are-ai-enabled,-costing-companies-6-million-on-average). Figures not carried in the release (the 92% access-control finding, the 43% unapproved-tool share, and the outcome breakdown) are as reported in [Help Net Security's coverage, 30 July 2026](https://www.helpnetsecurity.com/2026/07/30/ibm-cost-of-a-data-breach-2026/), which quotes the report directly. IBM's own report landing page returned HTTP 403 to automated retrieval, so the primary PDF was not read directly and these figures are attributed to the release and that coverage rather than to a page that was opened.
- EU AI Act Articles 72 and 73, serious-incident reporting. See [`CITATIONS.md`](./CITATIONS.md) for the full entry and the Digital Omnibus caveat.
- Incident corpus behind the qualitative claims: [`BYPASSES.md`](./BYPASSES.md).

All engineer-day and dollar-cost estimates in Part 2 and Part 3 are this document's own, not IBM's, and carry no external authority.
