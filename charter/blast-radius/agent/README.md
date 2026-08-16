# Charter, Blast radius / Agent

**Structural question.** Does the agent charter declare a specific risk tier, a quantitative damage cap, and the conditions that trigger automatic tier downgrade or retirement?

**Owner.** Named human owner. Counter-signed by domain authority and (Tier 3+) security review.

## Template fragment

The `risk_tier:`, `damage_cap:`, and `retirement_criteria:` blocks of [`../../templates/agent-charter.yaml`](../../templates/agent-charter.yaml):

```yaml
risk_tier: 2

damage_cap:
  max_records_per_session: 100
  max_cloud_spend_per_day_usd: 50
  forbidden_operations:
    - prod_database_writes
    - secret_modifications

retirement_criteria:
  - "Owner departs and no backup-owner accepts handoff within 30 days"
  - "Sustained false-positive rate above 30% for 14 days"
  - "Sustained Sentinels-detected scope drift for 7 days"
  - "Foundation model deprecated by vendor"
```

## Audit prompts

- For [agent X], is the declared tier consistent with the actual scope it operates? An agent that touches prod databases is not Tier 2.
- Are damage caps enforced at runtime (ResourceQuota, IAM tag-based limits, application-level limits)?
- Have any retirement criteria fired? When was the agent last evaluated against them?

## Operational tie-in

- `damage_cap.max_cloud_spend_per_day_usd` → AWS Cost Anomaly Detection or per-tag budget alerts.
- `damage_cap.max_records_per_session` → application-level rate limit enforced by the agent's wrapper.
- `damage_cap.forbidden_operations` → server-side denylist in [`../../../controls/authorization/server-side/aws-iam-scoped-policy.json`](../../../controls/authorization/server-side/aws-iam-scoped-policy.json) and Kyverno policies.
- `retirement_criteria` is the input to a periodic review job that flags agents for retirement.

## Citation

NIST CSF 2.0 GV.RM-01, GV.RM-02. NIST AI RMF GOVERN 1.3, MAP 5.1, MAP 5.2. ISO/IEC 42001 §A.6. EU AI Act Art. 9(2)(a)–(d).
