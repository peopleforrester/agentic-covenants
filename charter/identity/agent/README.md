# Charter, Identity / Agent

**Structural question.** Does each agent have a charter file naming a specific accountable human owner, a backup owner, and a registered agent identifier that ties runtime identity claims back to the charter?

**Owner.** The named human owner. Counter-signed by domain authority.

## Template fragment

The `ownership:` block of [`../../templates/agent-charter.yaml`](../../templates/agent-charter.yaml):

```yaml
ownership:
  owner_name: Michael Forrester
  owner_role: Principal Training Architect
  owner_email: michael@example.com
  backup_owner_name: Steven Heckler
  backup_owner_role: Managing Director
  backup_owner_email: steven@example.com

agent:
  name: claude-code-prod
  identifier: agent-claude-code-prod-001
```

## Audit prompts

- For [agent X], who is the human owner? When did they accept ownership?
- Is there a backup owner? Have they acknowledged the backup role?
- Does the runtime identity (ServiceAccount or IAM principal) reference the charter `identifier`?

## Operational tie-in

- The owner's contact info goes into PagerDuty as the on-call recipient for that agent's Sentinels alerts.
- The backup owner is the failover when the named owner is unavailable.
- The `identifier` in the charter must match the `agentic-covenants.io/agent-name` label on the Kubernetes namespace and ServiceAccount in [`../../../controls/identity/server-side/`](../../../controls/identity/server-side/).

## Common failure modes

- Owner departs and no backup-owner accepts handoff. **Charter retirement criterion** in [`../../templates/agent-charter.yaml`](../../templates/agent-charter.yaml) handles this; the agent retires automatically after 30 days.
- Owner-name field filled in but the person never knew they owned the agent. Drill: ask the listed owner whether they own this agent.

## Citation

NIST CSF 2.0 GV.RR-02; PR.AA-01 (charter dimension of identity management). NIST AI RMF GOVERN 2.1, GOVERN 2.2 (accountability). ISO/IEC 42001 §A.4.1 (leadership commitment). EU AI Act Art. 14(4) (human oversight role); Art. 26. NIST NCCoE Concept Paper on Software and AI Agent Identity and Authorization (Feb 5, 2026).
