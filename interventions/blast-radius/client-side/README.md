# Interventions, Blast radius / Client-side

**Trigger.** Falco alert from operator host, network attempt from `--network none` agent, sandbox boundary EPERM spike, unsandboxed-child detection.

**Authority.** On-call, no second approval. **Highest urgency.**

**Speed target.** Under 5 seconds.

## Tooling

- `pkill`, `pgrep`, `ps` for process-tree kill.
- Optionally `nmcli`, `ip link` for last-resort host network isolation.
- `docker` and `kubectl` for containerized agents.

## Files in this directory

- [`agent-isolate-host`](./agent-isolate-host), runbook script. Process-group kill of the agent tree, kills bubblewrap parents, optionally severs host network, stops Docker/Kubernetes containers labeled with the agent.

## Verification

```bash
# 1. No agent processes
pgrep -f "claude.*claude-code-prod"
# expected: no output

# 2. No sandbox processes
pgrep -f "bwrap.*claude-code-prod"
# expected: no output

# 3. Containerized agents stopped
docker ps --filter "label=agent=claude-code-prod"
# expected: empty list
```

## Common mistakes

- `pkill -f` matches partial commands; if the agent is invoked through a wrapper, the wrapper survives. The runbook uses process-group kill (`kill -- -PGID`) to take the whole tree.
- Sandbox `--die-with-parent` flag was not set at launch. The sandbox does not exit when its parent dies. Verify [Covenants L2-C3 launch flags](../../../controls/blast-radius/client-side/agent-bwrap).
- Network isolation cuts off the operator's ability to remediate. Use only as last resort, and have an out-of-band channel (phone, separate device) to maintain command.
- Forgetting the containerized-agent step, operator host is clean but Kubernetes pods keep running.

## Citation

NIST CSF 2.0 RS.MI-01, RS.MI-02. NIST SP 800-160 Vol. 1. OWASP ASI05, ASI08. NIST AI RMF MANAGE 4.1.
