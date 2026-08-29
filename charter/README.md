# Charter

Per-cell governance guidance and templates for the [Agentic Charter Matrix](../framework/CHARTER_MATRIX.md). This is a **documentation discipline**, not a runbook. Each cell directory contains template fragments and the structural questions your governance documents must answer.

## Layout

```
charter/
├── identity/{in-agent,client-side,server-side}/   # authority: agent, domain, organizational
├── authorization/{in-agent,client-side,server-side}/
├── blast-radius/{in-agent,client-side,server-side}/
├── approval-gating/{in-agent,client-side,server-side}/
├── supply-chain/{in-agent,client-side,server-side}/
├── examples/            # a worked bundle that satisfies every cell
└── templates/
    ├── agent-charter.yaml
    ├── domain-charter.md
    └── organizational-policy.md
```

The structure mirrors the operational matrices' five concerns but uses three different layers: **organizational** (top-of-house policy), **domain** (per-class), and **agent** (per-instance).

## The scoring instrument

Each cell also ships [`checks.yaml`](./identity/in-agent/checks.yaml), which expresses that
cell's audit prompts as machine checks. [`scripts/validate_charter.py`](../scripts/validate_charter.py)
reads all fifteen and scores a governance bundle against them.

```bash
python3 scripts/validate_charter.py --bundle charter/examples
python3 scripts/validate_charter.py --bundle charter/examples --format json
```

[`examples/`](./examples/) holds a worked bundle for a synthetic organisation that satisfies
every cell. It is the reference for what a filled charter looks like. The templates in
[`templates/`](./templates/) deliberately do not pass: they carry placeholders, and a bundle
that still carries them has not been filled in.

**A concern scores as its weakest cell rather than as the mean.** An agent takes the open
path rather than the average one, so averaging hides the cell that matters.

This is the answer to the obvious objection. A governance matrix made of prose is the thing
this framework criticises everywhere else: an assertion nobody can check. Expressing the
audit prompts as executable checks is the same argument applied to Charter itself. What the
checks cannot decide is whether the named humans are the right ones, whether the council's
decisions are sound, or whether a policy is honest. Those need a reviewer. The checks
establish that the structure exists and is current, which is the part a reviewer should not
have to spend time on.

## What each cell directory contains

Every cell directory has a README following this shape:

1. **The structural question.** What does this cell of the matrix actually require?
2. **Who owns this cell.** Named role responsible.
3. **Template fragment.** The piece of policy or charter that goes in your governance documents.
4. **Audit prompts.** Questions a reviewer (EU AI Act, ISO/IEC 42001, internal audit) will ask. If your documents don't answer them, the cell is empty.
5. **Operational tie-in.** Which Covenants/Sentinels/Interventions/Restorations cell consumes this Charter cell at runtime.
6. **Citations.**

## Templates

[`templates/agent-charter.yaml`](./templates/agent-charter.yaml) is the canonical YAML for a single agent. Drop into your governance repo, branch-protect, PR-review every change. The other two templates are markdown for the higher layers (organizational policy, domain charter).

## Charter feeds the operational matrices

Each Charter cell has a downstream consumer:

| Charter cell | Operational consumer |
|---|---|
| Identity / agent | [`controls/identity/server-side/`](../controls/identity/server-side) (the named owner becomes the on-call paged by Sentinels) |
| Authorization / agent | [`controls/authorization/server-side/`](../controls/authorization/server-side) (RBAC role implements the charter scope) |
| Blast radius / agent | Decides which Covenants cells must be populated. Tier 1 → minimal; Tier 4 → all 15. |
| Approval gating / agent | [`controls/approval-gating/server-side/`](../controls/approval-gating/server-side) (branch protection on the charter file itself) |
| Supply chain / agent | [`controls/supply-chain/client-side/mcp-allowlist.json`](../controls/supply-chain/client-side/mcp-allowlist.json) and [`controls/supply-chain/server-side/`](../controls/supply-chain/server-side) (declared dependencies become the runtime allowlist) |

If the Charter is missing for an agent, the operational matrices have no anchor.

## Audit posture

A complete Charter posture survives:

- **EU AI Act conformity assessment**: Articles 9, 14, 17, 25, 26 require the structures Charter documents.
- **ISO/IEC 42001 audit**: §A.2 through §A.10 each map to Charter cells.
- **NIST AI RMF GOVERN review**: each GOVERN subcategory (1.1 through 6.2) has a Charter cell answering it.
- **Internal/external incident-readiness review**: each cell names a human accountable so when an alert fires the page goes to a real person.

## Common emptiness patterns

- Org policy as a one-time PDF, never operationalized.
- Risk appetite as aspiration ("low risk for innovation") with no quantitative caps.
- Governance Council named but never meets.
- Single domain charter copy-pasted to every agent (no real tiering).
- Agent charter YAML hand-edited without PR review.
- Approval signatures are reflexive ("alert fatigue at the governance layer").
- Quarterly review never happens.
- Retirement criteria are vague ("when no longer needed").
- Dependency manifest in Charter and allowlist hashes in Covenants drift apart.
