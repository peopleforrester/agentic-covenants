# Checklist: Blast radius

> **When this agent does the wrong thing, how much breaks before it stops?**

Agent: ________________  Charter ref: ________________  Risk tier: ____  Date: __________
Auditor: ________________  Owner present: ________________

Declared damage cap from the charter: ____________________________________________
(records/session, spend/day, forbidden operations, if blank, stop and fill the charter first)

---

## L1, In-agent

**Empty by design.** The model declining destructive operations is a verified failure mode: Kiro, Replit, DataTalks.Club, Amazon Q (CVE-2025-8217). In the Replit case the agent wiped a production database *during an explicit freeze, having been told eleven times not to act*.

- [ ] Nobody on this team believes refusal is a control

**Mark:** `[N/A]`, no enforcement at this layer

---

## L2, Client-side

- [ ] Sandbox applied **at process launch** (bubblewrap / Seatbelt / gVisor), not after
- [ ] Inheritance enforced, `--die-with-parent`, `--new-session`, so children cannot outlive or escape
- [ ] Seccomp or AppArmor profile loaded at launch; AppArmor in **enforce**, not complain (`aa-status`)
- [ ] Profile derived from the real workload (`strace -c`), not copy-pasted
- [ ] `clone` flag-filtered so the agent cannot create new namespaces
- [ ] `--network none` for offline tasks; otherwise egress through a proxy whose **allowlist lives outside the sandbox**
- [ ] Read-only mounts on operator data; no second writable mountpoint to the same FS
- [ ] Dry-run defaults for destructive commands

**Verify:**
```bash
agent-bwrap /tmp -- /bin/sh -c 'cat /etc/shadow'                 # must fail
agent-bwrap /tmp -- curl -sS https://example.com                 # must fail
agent-bwrap /tmp -- /bin/sh -c 'sh -c "curl -sS https://example.com"'   # child must ALSO fail
aa-status | grep -A2 enforce                                     # profile enforcing, not complain
```

**Known bypasses accepted?** unsandboxed children when inheritance is not enforced · profile gaps · kernel escape (rare, documented) · read-only bind with a writable path elsewhere. Note: Claude Code's own denylist and sandbox are **documented as escapable**. That is why this is not the last layer.

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L3, Server-side

- [ ] IaC pipeline splits `plan` (read-only creds) from `apply` (gated by required reviewers)
- [ ] `terraform prevent_destroy` **not** relied on alone, `state rm`, config removal, and direct state edits all go around it
- [ ] NetworkPolicy default-deny, then explicit allow. **kube-dns allowed** or pods fail silently
- [ ] Egress denies RFC1918, link-local `169.254.0.0/16` (cloud metadata), and CGN ranges
- [ ] ResourceQuota **and** LimitRange both present (quota alone rejects naive pods)
- [ ] `services.loadbalancers: 0` and `services.nodeports: 0` in the agent namespace
- [ ] Prod and non-prod separated by **account/cluster**, not just namespace
- [ ] Immutable backups (Object Lock COMPLIANCE) written by a **different credential** than the agent's
- [ ] Agent role cannot `AssumeRole` into the prod account (explicit deny, not just absent allow)
- [ ] PodDisruptionBudget on critical workloads

**Verify:**
```bash
kubectl run -n <ns> t --image=alpine --rm -it -- wget -O- --timeout=3 http://10.0.0.5   # must time out
kubectl run -n <ns> t --image=alpine --rm -it -- wget -O- --timeout=3 http://169.254.169.254/  # metadata must fail
aws s3 rm s3://<immutable-bucket>/test-object                    # must fail: AccessDenied
aws --profile <agent> sts assume-role --role-arn arn:aws:iam::<PROD>:role/any --role-session-name t   # must fail
```

**Known bypasses accepted?** backup taken *after* contamination · "immutable" backups in the same account as the compromised credential · existing TCP connections surviving a NetworkPolicy change (CNI-dependent) · drain honoring a 300s grace period

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## Row verdict

☐ All three present ☐ Client-side only, insufficient with cluster reach ☐ Server-side only ☐ Gaps

**Federal/DoD note.** 800-53 **SC-7, SC-39, SC-5, SI-4, CP-9, CP-10**; DoD ZT **Network/Environment**, **Application & Workload**, **Data**; RAI *Reliable*, *Governable*; DISA STIG for the container platform and OS. **An air gap is a network control, not a behavioral one**, every incident above would have happened identically inside an enclave. See [`examples/dod-air-gapped/`](../examples/dod-air-gapped).

**Open items:**

| # | Gap | Owner | Due |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
