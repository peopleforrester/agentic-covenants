# Restorations

Recovery runbooks for every cell of the [Agentic Restorations Matrix](../RESTORATIONS_MATRIX.md). Companion to [`controls/`](../controls/) (Protect), [`sentinels/`](../sentinels/) (Detect), and [`interventions/`](../interventions/) (Respond).

## Layout

```
restorations/
├── identity/{in-agent,client-side,server-side}/
├── authorization/{in-agent,client-side,server-side}/
├── blast-radius/{in-agent,client-side,server-side}/
├── approval-gating/{in-agent,client-side,server-side}/
└── supply-chain/{in-agent,client-side,server-side}/
```

The structure mirrors the other operational matrices exactly. The cell at `identity/server-side/` carries the rebuild that follows the response in `interventions/identity/server-side/`.

## All in-agent cells are empty

The L1 in-agent column is empty for every concern. **The agent is the patient, not the surgeon.** Recovery is operator-side and infrastructure-side.

## The recovery order is not optional

1. **Identity first**: every later step authenticates against an identity.
2. **Authorization**: restoring data into a permission environment that still allows the attacker is restoring the attack.
3. **Blast radius**: data and workloads need a known-good identity and authorization environment.
4. **Approval gating**: re-enabling gates before rebuild is complete blocks legitimate recovery.
5. **Supply chain last**: rebuilding from clean source assumes the rest of the stack is ready.

Each cell assumes the prior cells have completed.

## Forensic preservation comes first

If the incident may be investigated externally, snapshot memory and disk **before** destructive recovery actions. Every recovery runbook in this directory destroys evidence; document the hold-and-image step at the top of your incident command.

## Pick a backup from before the contamination point

The most common recovery failure: restoring from the most recent backup, which is from after the attacker's window. Pick the earliest indicator of compromise from Sentinels and roll back to before that timestamp.

## Cell README structure

Every cell directory has the same six-section README:

1. **Precondition.** What must already be done (Interventions complete, scope known, backups verified, prior cells in this row complete).
2. **Authority.** Who is authorized.
3. **Tooling.** What must be installed.
4. **Files in this directory.** The rebuild script and pre-staged restore artifacts.
5. **Verification.** How you confirm the rebuild is healthy and not still tainted.
6. **Common failure modes.** From the matrix Appendix A.
7. **Citation.** From [`CITATIONS.md`](../CITATIONS.md).

## Recovery feeds prevention

Every successful recovery produces a follow-up action list:

- Which Covenants prevention control was bypassed?
- Was the bypass already in [`BYPASSES.md`](../BYPASSES.md), or new?
- What change to Covenants prevents this class in the future?

If recovery does not feed back into prevention, the org is treating each incident as a one-off and accepting that the same class of attack will work again.
