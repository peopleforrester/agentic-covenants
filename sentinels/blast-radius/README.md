# Sentinels, Blast radius

**Intent.** Surface sandbox boundary events, network attempts on `--network none` agents, NetworkPolicy denials, ResourceQuota near-limit alerts, VPC Flow Log REJECTs.

| Layer | Cell | What you actually deploy |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Forensic only. Sandbox events do not surface in-agent. |
| Client-side | [`client-side/`](./client-side/) | bpftrace one-liner catching unexpected `connect()` calls from agent process tree; Falco userspace rules detecting unsandboxed children and writes to unexpected paths; bubblewrap stderr capture for EPERM events. |
| Server-side | [`server-side/`](./server-side/) | Falco runtime rules in agent containers (shell spawn, sensitive-path writes, non-allowlisted egress); Cilium Hubble flow shipping (drops); Prometheus alert on ResourceQuota at 85%; CloudWatch Logs Insights query for VPC Flow REJECTs. |

Detects what [`../../controls/blast-radius/`](../../controls/blast-radius/) prevents.
