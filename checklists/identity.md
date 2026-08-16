# Checklist: Identity

> **If this agent's identity is forged, stale, or shared, what stops the action at this layer?**

Agent: ________________  Charter ref: ________________  Risk tier: ____  Date: __________
Auditor: ________________  Owner present: ________________

Identity is the row everything else anchors to. If it is sloppy, per-agent authorization, per-agent attribution, and per-agent revocation are all fiction.

---

## L1, In-agent (advisory only)

- [ ] System prompt names the agent, the operator, and the authorized scope
- [ ] Prompt contains no secrets, internal hostnames, or attack-surface detail (assume it is public)
- [ ] Nobody is treating this cell as a control

> Identity is **carried**, not **established**. A prompt declaration has no cryptographic weight; the agent cannot prove its own identity to the target.

**Mark:** `[ ]` present / `[~]` untested / `[N/A]` skipped, reason: ____________________

---

## L2, Client-side

- [ ] One credential per agent. **No credential shared across agents**
- [ ] Credential lives in operator-owned config, not the agent user's home
- [ ] Agent's own user cannot read the credential at rest (`setfacl` deny, or equivalent)
- [ ] Credential is not in `/etc/profile` or any shell rc every process inherits
- [ ] Credential does not appear in the agent's own startup logs

**Verify (all three must pass):**
```bash
ps -eo pid,user,args | grep -i claude          # must NOT show the key in args
sudo -u agent-runner cat /etc/agents/<name>/token   # must fail: Permission denied
md5sum /etc/agents/*/token | awk '{print $1}' | sort | uniq -d   # must print nothing
```

**Known bypasses accepted?** token theft from a readable FS · credential in logs or `ps` · operator copies config to another machine

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L3, Server-side

- [ ] Dedicated ServiceAccount or IAM principal **per agent** (grep for shared SAs)
- [ ] OIDC federation / workload identity, no long-lived static keys
- [ ] Projected token TTL **≤ 900s**, not the 1-hour default, not unbounded
- [ ] Token `audience` pinned to this agent, not a generic `sts` audience
- [ ] IAM trust policy `sub` pins one exact `system:serviceaccount:<ns>:<sa>`, **no wildcards**
- [ ] Token in a projected volume, not a long-lived Secret
- [ ] SPIFFE/SPIRE registered if the agent crosses clusters

**Verify:**
```bash
kubectl get sa -A | grep -E "(claude|agent|bot)"    # one SA per agent, none shared
kubectl get pod -n <ns> <pod> -o jsonpath='{.spec.volumes[?(@.projected)].projected.sources[?(@.serviceAccountToken)].serviceAccountToken.expirationSeconds}'
aws iam get-role --role-name <agent> --query 'AssumeRolePolicyDocument'   # inspect sub condition
```

**Known bypasses accepted?** IdP compromise · token replay inside the TTL · trust policy accepting unintended issuers · audience not verified by the relying party

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## Row verdict

☐ All three present, defense in depth
☐ In-agent only, **audit finding**
☐ Server-side only, add client-side to fail fast
☐ Client-side only, acceptable only if the agent has no cloud/cluster reach

**Federal/DoD note.** 800-53 **AC-2, IA-2, IA-5, IA-8, IA-9**; DoD ZT **User** pillar. Under DoD ICAM every NPE must be under the control of an authorized **Person Entity** who can create, modify, and destroy the account. The charter's named owner is that PE, and the charter `identifier` is the NPE registry join key. If the owner has departed and no backup accepted handoff, the NPE should not still exist. See [`examples/dod-air-gapped/icam-npe-binding.md`](../examples/dod-air-gapped/icam-npe-binding.md).

**Open items:**

| # | Gap | Owner | Due |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
