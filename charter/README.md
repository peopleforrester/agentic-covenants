# Charter

Per-cell governance guidance and templates for the [Agentic Charter Matrix](../framework/CHARTER_MATRIX.md). This is a **documentation discipline**, not a runbook. Each cell directory contains template fragments and the structural questions your governance documents must answer.

## Layout

```
charter/
├── identity/{organizational,domain,agent}/
├── authorization/{organizational,domain,agent}/
├── blast-radius/{organizational,domain,agent}/
├── approval-gating/{organizational,domain,agent}/
├── supply-chain/{organizational,domain,agent}/
└── templates/
    ├── agent-charter.yaml
    ├── domain-charter.md
    └── organizational-policy.md
```

The structure mirrors the operational matrices' five concerns but uses three different layers: **organizational** (top-of-house policy), **domain** (per-class), and **agent** (per-instance).

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
