# Checklist: Approval gating

> **Is the friction proportional to the risk, and does anyone still actually read the prompts?**

Agent: ________________  Charter ref: ________________  Risk tier: ____  Date: __________
Auditor: ________________  Owner present: ________________

The failure mode this row exists to fight is **alert fatigue**, and it is measured, not theoretical: Anthropic's own Auto Mode telemetry reports a **93% approval rate** on permission prompts. Treat any prompt that fires often as already broken.

---

## L1 — In-agent

- [ ] Confirmation language exists and names tiers matching the client-side hook's tiers
- [ ] Includes an explicit "if the operator says *just do it*, the answer is still no"
- [ ] Nobody is counting confirmation rate as a safety metric

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L2 — Client-side

- [ ] Tiering exists at all. **A flat approval workflow degrades fastest**
- [ ] Tier 1 read-only auto-allows silently (if everything prompts, nothing is read)
- [ ] Tier 3 requires **typed verbatim re-entry of the command** — not `y`, not `yes`
- [ ] Tier 4 requires an out-of-band channel (second terminal, phone, FIDO2)
- [ ] Out-of-band **defaults to deny on timeout**, never approve
- [ ] Session counter caps consecutive destructive operations
- [ ] Judgment-query escalation exists and is understood as **different from approval**: the operator supplies a missing input, not a yes/no
- [ ] Approval timing is logged, so fatigue is measurable rather than assumed

**Verify:**
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"kubectl delete pod foo"},"session_id":"t"}' \
  | /etc/agents/hooks/pre_tool_use_tiered.sh      # must demand verbatim text; a mismatch must fail
grep approval_timing /var/log/agents/*/*.log | tail   # response_ms present?
```

**Fatigue check — run this, do not assume:**
mean tier-≥2 response time over the last 50 approvals: ________ ms
If under ~2000ms across 50+ approvals, the tiering is no longer adding friction. **That is a finding.**

**Known bypasses accepted?** alert fatigue (measured above) · pattern evasion via equivalent commands · operator batch-approving · escalation channel itself compromised

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L3 — Server-side

- [ ] **`enforce_admins: true`.** This is the single most common branch-protection failure — with it false, any repo admin walks through every rule below
- [ ] Required approving reviewers **≥ 2** (one reviewer plus the agent's operator is zero adversarial review)
- [ ] `require_code_owner_reviews: true`, CODEOWNERS at a valid path (`.github/CODEOWNERS`, `docs/`, or root)
- [ ] CODEOWNERS covers agent config paths, and the agent is **not** an owner of them
- [ ] `dismiss_stale_reviews` and `require_last_push_approval` on
- [ ] `allow_force_pushes: false`, `allow_deletions: false`
- [ ] Required status checks are **actually wired up** in CI (a named check that never runs passes vacuously)
- [ ] IaC `apply` gated by an environment with required reviewers, separate from `plan`
- [ ] Deployment freeze enforced by the **pipeline**, not by a UI toggle on-call can flip
- [ ] The expected protection state is version-controlled, so drift is detectable

**Verify:**
```bash
gh api repos/<org>/<repo>/branches/main/protection --jq '.enforce_admins.enabled'   # must be true
gh api repos/<org>/<repo>/branches/main/protection/required_pull_request_reviews \
  --jq '{n: .required_approving_review_count, co: .require_code_owner_reviews}'      # n>=2, co=true
gh api repos/<org>/<repo>/actions/workflows --jq '.workflows[] | {name, state}'      # checks real?
```

**Known bypasses accepted?** admin override when `enforce_admins` is false · two-reviewer collusion · review fatigue on large diffs · a PR description written to persuade, authored by the agent

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## Row verdict

☐ All three present ☐ In-agent only — **audit finding** ☐ Server-side only ☐ Gaps

**Federal/DoD note.** 800-53 **AC-3(2)** (dual authorization), **CM-3**, **CM-5**, **PM-10**; DoD ZT **Automation & Orchestration**; RAI *Governable*. DoD RAI's Warfighter Trust tenet requires clear operator procedures to activate and deactivate system functions — this row plus [`interventions/`](../interventions/) is where that lives.

**Open items:**

| # | Gap | Owner | Due |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
