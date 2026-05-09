# Restorations — Authorization

**Intent.** Rebuild RBAC and IAM from declarative source. Audit for drift introduced during the incident.

**Order.** Second. Restoring data into a permission environment that still allows the attacker is restoring the attack.

| Layer | Cell | What you actually run |
|---|---|---|
| In-agent | [`in-agent/`](./in-agent/) | Empty. |
| Client-side | [`client-side/`](./client-side/) | `agent-restore-authorization-local`: restore hook config from VCS, verify ownership and ACLs, reinstall pre-commit, verify Claude Code is on the patched version. |
| Server-side | [`server-side/`](./server-side/) | `agent-restore-authorization-server`: reapply RBAC + Kyverno + IAM from declarative source, audit for cluster drift vs source. |

Rebuilds what [`../../interventions/authorization/`](../../interventions/authorization/) locked down.
