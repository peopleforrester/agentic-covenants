# Restorations, Blast radius

**Intent.** Restore data, redeploy infrastructure, rebuild from clean state. Verify network policies and resource quotas survived.

**Order.** Third. Data and workloads need a known-good identity and authorization environment to land into.

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-restore-host-local`: rebuild operator host from known-good system image (if untrusted), reinstall agent runtime with signature verification, re-derive sandbox profiles, reapply launchers. |
| Server-side | [`server-side/`](./server-side/) | `agent-restore-blast-radius-server`: restore data from immutable backups verified pre-incident, redeploy IaC, reapply NetworkPolicy default-deny + allow, reapply ResourceQuota and LimitRange, re-create namespace if needed. |

Rebuilds what [`../../interventions/blast-radius/`](../../interventions/blast-radius/) contained.
