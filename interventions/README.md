# Interventions

Response runbooks for every cell of the [Agentic Interventions Matrix](../INTERVENTIONS_MATRIX.md). Companion to [`controls/`](../controls/) (Protect) and [`sentinels/`](../sentinels/) (Detect).

## Layout

```
interventions/
├── identity/{in-agent,client-side,server-side}/
├── authorization/{in-agent,client-side,server-side}/
├── blast-radius/{in-agent,client-side,server-side}/
├── approval-gating/{in-agent,client-side,server-side}/
└── supply-chain/{in-agent,client-side,server-side}/
```

The structure mirrors `controls/` and `sentinels/` exactly. The cell named `identity/server-side/` carries the runbook that responds to identity violations detected by `sentinels/identity/server-side/` after prevention by `controls/identity/server-side/` failed.

## All in-agent cells are empty

The L1 in-agent column is empty for every concern. **An agent acting badly cannot be reliably told to stop acting badly.** The same structural absence that makes the in-agent layer advisory in Covenants makes it useless in Interventions. The in-agent cell directories carry only a README explaining the empty state. There is no runbook, by design.

## Pre-staging is the precondition

Every runbook in this directory assumes pre-staging:

- **Break-glass identity** with permissions to revoke, disable, and lock, separate from the agent's own identity. Stored in a hardware key or sealed-secret vault. Tested in non-prod within the last 90 days.
- **Pre-staged emergency policy directory** at `/etc/agents/emergency/` (or `emergency/` in source control) containing every artifact each runbook expects: deny-all hook, deny-all Kyverno policy, emergency NetworkPolicy, locked branch-protection JSON, IAM deny-all policy, last-known-good image SHA. Each runbook lists exactly which file it reads.
- **PagerDuty (or equivalent) wired to Sentinels alerts.**
- **On-call drilled on the runbooks.** *Drilled, not "informed."*

An incident is the wrong time to discover that emergency credentials expired, that a pre-staged policy has a typo, or that the on-call has never run the script.

## Cell README structure

Every cell directory has the same six-section README:

1. **Trigger.** Which Sentinels alert maps to this intervention.
2. **Authority.** Who is authorized to execute. On-call alone, or on-call plus security review.
3. **Tooling.** What must be installed.
4. **Files in this directory.** The runbook script and pre-staged emergency artifacts.
5. **Verification.** How you confirm the cutoff worked.
6. **Common mistakes.** Failure modes that leave residual capability.
7. **Citation.** From [`CITATIONS.md`](../CITATIONS.md).

## Speed targets

| Concern | Target time-to-response |
|---|---|
| Identity | 30 seconds |
| Authorization | 10 seconds |
| Blast radius | **5 seconds** |
| Approval gating | 60 seconds |
| Supply chain | 5 minutes |

## Practiced incident order

For an active misuse incident:

1. Blast radius (L2-C3 + L3-C3), **5 seconds**
2. Identity server-side (L3-C1), 30 seconds
3. Identity client-side (L2-C1), 30 seconds
4. Authorization (L3-C2 + L2-C2), 1 minute
5. Approval gating server-side (L3-C4), 1 minute
6. Supply chain (L2-C5 + L3-C5), 5 minutes

For a slow-and-low compromise: reverse the order. Quarantine first, contain last.

The incident commander records which steps fired in what order. The recovery (Restorations) depends on knowing exactly what state the response left the system in.
