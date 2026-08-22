# Agentic governance maturity model

Five levels, from an ungoverned agent to one that is bounded, observed, and reversible.

The model exists because "are we doing agent security" has no useful answer, while "we are Level 1 on identity and Level 0 on blast radius, and the gap is a sandbox we have not installed" is something a team can act on and a leader can fund.

## The one rule that makes this model honest

**Your level is your lowest concern, not your average.**

An operator with excellent identity, excellent supply-chain pinning, and no sandbox is **Level 0**, not Level 2.5. Averaging is how a governance program reports progress while the actual exposure is unchanged, because an agent looking for a way out does not take the average path. It takes the open one.

This is the same reason the matrix asks each cell "what stops it *here*" rather than scoring a row overall.

## The levels

### Level 0: Ungoverned

The default state of any fresh install, and the state most agent deployments are in right now.

The agent runs as the operator, with the operator's credentials, with no tool restriction beyond what it chooses to respect. Nothing in any log distinguishes an action the agent took from an action the human took.

The defining property is not that controls are weak. It is that **no control exists outside the model's reasoning**, so the entire security posture is the system prompt. This is exactly the configuration that deleted Replit's production database during an explicit action freeze.

| Requirement | None |
|---|---|

### Level 1: Named

The agent has an identity of its own.

This is first because everything after it depends on it. You cannot scope permissions for a principal that does not exist, you cannot attribute an action you cannot distinguish, and you cannot revoke access that is the operator's own. Most operators skip this and start at Level 2, which produces controls that cannot be verified and audit trails that cannot be read.

| Requirement | Verified by |
|---|---|
| The agent uses a credential that is not the operator's | The cloud principal in the agent's environment differs from the operator's default profile |
| The credential is short-lived or independently revocable | The credential can be revoked without locking the operator out |
| The agent is registered somewhere a human can enumerate it | An entry exists in an inventory, per [`inventory/`](../../inventory) |
| A named human is accountable for it | The inventory entry names a person, not a group mailbox |

### Level 2: Bounded

Deterministic constraints exist outside the model's reasoning.

The distinction from Level 0 is not that the agent has been told what not to do. It is that something **denies the call without consulting the model**, which means the constraint holds whether the agent is cooperative, confused, or under injection.

| Requirement | Verified by |
|---|---|
| Tool permissions are deny-by-default rather than allow-by-default | The permission config denies unlisted tools, not just listed ones |
| A PreToolUse hook evaluates calls before execution | The hook fires on a call it should deny, and the call does not run |
| The hook's decision cannot be overridden by the model | The deny path returns non-zero and is not advisory |
| Protected paths are enforced by the filesystem, not only by policy | The agent's principal cannot write to them even with the hook disabled |

Level 2 is where most serious deployments should be within a week, and it is achievable in an afternoon.

### Level 3: Contained

The blast radius is bounded by the operating system, not by configuration the agent could route around.

The failure mode Level 2 does not cover is a control that is correctly configured and simply stepped around: a subshell spawned outside the wrapper, an MCP server swapped for a different binary at the same path, a network call to something the policy never contemplated.

| Requirement | Verified by |
|---|---|
| A sandbox is applied at launch and inherited by children | A subshell spawned by the agent is subject to the same restriction |
| The filesystem view is a mount set, not the whole home directory | Secrets outside the mount set are unreadable from inside the sandbox |
| Egress is restricted to an allowlist | A connection to a non-allowlisted host fails from inside the sandbox |
| MCP servers are allowlisted and pinned by hash | Substituting a binary at an allowlisted path fails the launch check |
| Tool descriptions are hashed and compared on load | A changed tool description is detected before use |

The inheritance requirement is the one that gets skipped, and it is the one that matters. A sandbox the agent can start a process outside of is not a sandbox.

### Level 4: Observed and reversible

You would know, and you could undo it.

Levels 1 through 3 are all Protect. Level 4 is where the other four NIST CSF functions come online, and it is the first level at which the two-day incident reporting clock in EU AI Act Article 73 is meetable at all, because you cannot report in two days what you detect in thirty.

| Requirement | Verified by |
|---|---|
| Decisions are shipped off the machine as they happen | Deleting the local log does not destroy the record |
| Denials and approvals are both recorded, with timing | Approval-fatigue rate is measurable, per [`sentinels/approval-gating/`](../../sentinels/approval-gating) |
| High-consequence actions require out-of-band approval | The approval path does not run on the machine the agent controls |
| A kill switch exists and has been executed in a drill | Time from decision to agent stopped is measured, not estimated |
| Restoration from a known-good state has been rehearsed | The runbook has been run, per [`restorations/`](../../restorations) |

The drill requirements are deliberate. An untested kill switch is a Level 3 control with a Level 4 label, and the difference is only discovered during the incident.

## Scoring per concern

Assess each of the five concerns independently, then take the minimum.

| Concern | L1 Named | L2 Bounded | L3 Contained | L4 Observed |
|---|---|---|---|---|
| **Identity** | Own credential, registered | Credential scoped to task | Short-lived, bound to workload | Every use attributed off-box |
| **Authorization** | Principal is distinguishable | Deny-by-default plus hook | Enforced by the OS and the remote | Denials analyzed for pattern |
| **Blast radius** | Scope is written down | Protected paths enforced | Sandbox at launch, inherited | Kill switch drilled |
| **Approval gating** | Actions are attributable | Tiered gating exists | Out-of-band for the top tier | Fatigue rate measured |
| **Supply chain** | Dependencies enumerated | Lockfiles pinned | MCP allowlisted and hashed | Drift detected on change |

## How to use this in a conversation with leadership

Report the level, the binding concern, and the cost of the next level. Three numbers.

> "We are Level 1. The binding concern is blast radius: the agent runs unsandboxed with our full cloud credentials. Level 2 across all five concerns is about a week of one engineer. Level 3 needs the sandbox work, which is another two weeks and is the one that would have contained the failure mode in the Replit incident."

What makes this land is that the level is falsifiable. Every requirement above has a verification column, and [`assess.sh`](./assess.sh) runs the machine-checkable ones. A maturity claim nobody can check is a slide, not a posture.

## What this model deliberately does not do

- **It does not score in-agent controls.** Prompt-level constraints do not move a level, at any level. They are worth having and they are not evidence.
- **It does not average.** See the rule at the top.
- **It does not end at Level 4.** Level 4 is a defensible posture for a single workstation, not a finished state. A multi-agent production deployment has cells this model does not evaluate, which is what the full matrix is for.
- **It is not a compliance mapping.** The crosswalks in [`CITATIONS.md`](../../framework/CITATIONS.md) are the starting point for that conversation, and an authorizing official makes the determination.
