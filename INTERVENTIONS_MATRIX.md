# The Agentic Interventions Matrix

A response framework for autonomous-agent governance. Three layers of action, five concerns, fifteen cells. Companion to the [Agentic Covenants Matrix](./MATRIX.md) (Protect), the [Agentic Sentinels Matrix](./SENTINELS_MATRIX.md) (Detect), and the Agentic Restorations Matrix (Recover, tracked separately). Maps to NIST CSF 2.0 **Respond (RS)** function.

## What this is

Where Sentinels notices, Interventions stops. The Interventions Matrix is the answer to *how do I stop the bleeding now?* Not *what just happened* (Sentinels). Not *how did I prevent this* (Covenants). Not *how do I get back to normal* (Restorations). Specifically: the agent is doing the wrong thing right now, and you need it to stop in seconds, not minutes.

The matrix differs structurally from Covenants and Sentinels in one important way: **the in-agent layer is essentially empty for response.** An agent that is acting badly cannot be reliably instructed to stop acting badly. The same structural absence that makes the in-agent layer advisory in Covenants makes it useless in Interventions. Telling the agent "stop now" through prompts or system messages is on average ignored by agents that are already off the rails. Real response lives in client-side and server-side cutoffs.

## Why response is its own matrix

Detection without response is a notification service. The 90-day Claude Code CVE corpus shows the cost: in several incidents the prevention layer was bypassed and the detection layer fired, but no automated response capability existed and the operator was left manually killing processes from a phone notification at 2am. The Interventions Matrix exists so that there is a defined, tested, fast path from "alert fired" to "agent stopped" without depending on a human reading the alert in time.

Response also needs to be deliberate about scope. Stopping an agent too aggressively breaks legitimate work. Stopping it too narrowly misses the actual harm. Each cell answers a different aspect of "stop what, exactly?"

## The two axes

### Vertical: where action is taken

1. **In-agent.** The agent itself stops. **Empty in this matrix.** An agent that can be talked into stopping cannot be relied on to stop when it matters. Listed for completeness.
2. **Client-side cutoffs.** Operator-machine actions: kill the process tree, terminate the session, revoke the local credential, freeze the local hook config, isolate the operator host from the network. Fast (milliseconds to seconds). Effective if the agent is contained to one host.
3. **Server-side cutoffs.** Target-system actions: revoke the agent's ServiceAccount or IAM credential, invalidate active tokens, apply emergency-deny admission policy, network-isolate the namespace, freeze branch protection, halt all deployments. Slower (seconds to minutes) but catches agents and operator hosts that have been compromised.

### Horizontal: what is being stopped

1. **Identity.** Revoke the credential, kill the session.
2. **Authorization.** Shrink permissions to nothing.
3. **Blast radius.** Contain the in-flight damage.
4. **Approval gating.** Lock down all approval surfaces.
5. **Supply chain.** Quarantine packages, halt distribution.

## The matrix

| Concern | In-agent (empty) | Client-side cutoffs | Server-side cutoffs |
|---|---|---|---|
| **Identity** | (no enforcement; the agent that misuses identity will not voluntarily revoke it) | Kill agent process tree (`pkill -KILL -f claude` or `systemctl stop`). Delete local credential file. Force re-authentication on next launch. Logout SSO session on the operator host. **Time to effect: seconds.** | Revoke OIDC token at IdP. Disable ServiceAccount (`kubectl patch sa claude-code -p '{"automountServiceAccountToken":false}'`). Rotate IAM access keys. Add deny-all IAM policy to the principal. Invalidate all active sessions for the agent identity. **Time to effect: tens of seconds, plus existing token TTL window.** |
| **Authorization** | (no enforcement) | Force-replace local hook config with deny-all. Stop the agent process. Set `--allowedTools=""` on next launch. Lock the hook config file with `chattr +i` (Linux) so even root cannot edit without removing the immutable bit first. | Apply emergency Kyverno policy denying all operations from agent ServiceAccounts. Update IAM policy to deny `*` on `*` for the agent role. Pre-receive hook on Git server rejects all pushes from the agent identity. **Effect: every subsequent agent action gets denied at the API layer.** |
| **Blast radius** | (no enforcement) | `kill -KILL` the agent and all child processes. Tear down sandbox (bubblewrap exits, child processes die with parent). Disconnect operator host from network if process tree cannot be reliably traced (`nmcli connection down` / Wi-Fi off / pull ethernet). For containerized agents, `docker stop` or `kubectl delete pod`. | Cordon and drain the agent's node. Apply emergency NetworkPolicy default-deny-everything in the agent namespace. Scale agent Deployment to zero replicas. Delete the agent's namespace if the blast radius is bigger than one workload. Block the agent's egress IP at the cloud provider firewall. **Time to effect: seconds for namespace freeze, minutes for full cluster cordon.** |
| **Approval gating** | (no enforcement) | Set every PreToolUse hook to deny-all. Disable Auto Mode classifier (`--auto-mode=off`). Disable judgment-query escalation. Force out-of-band confirmation on every action (which the agent cannot produce). | Set every protected branch to require admin override (revoke "bypass" permission from all roles). Pause all CI/CD pipelines via repo-level workflow disable. Engage deployment freeze automation (`gh variable set DEPLOY_FREEZE -b true`). Lock all environments in the GitHub Environment configuration. Notify on-call humans, all decisions go through them. |
| **Supply chain** | (no enforcement) | Stop using the suspect MCP server (remove from local allowlist). Quarantine downloaded packages (move to `/var/quarantine/` with restrictive ACL). Lock lockfile against further changes. Pin agent runtime to last-known-good version. | Remove poisoned image from registry (`crane delete` or registry UI). Add cosign deny rule for the compromised signature. Apply emergency egress NetworkPolicy blocking the compromised registry domain. Block the malicious MCP domain at the corporate DNS resolver or web proxy. Force redeploy of agent workloads with last-known-good image SHA pinned. |

## How to use this as a runbook

Each cell has a defined script. When an alert fires from the [Sentinels Matrix](./SENTINELS_MATRIX.md), the on-call follows the script for the affected concern. The runbook for each cell answers four questions:

1. **Trigger.** What Sentinels alert maps to this intervention?
2. **Authority.** Who is allowed to execute this script? Pre-authorized at the on-call level, or requires a second approval?
3. **Steps.** The literal commands, in order, that effect the cutoff.
4. **Verification.** How you confirm the cutoff worked.

Three test outcomes when you walk a row:

- **All three cells operational and tested:** the concern is responsive. Detection-to-stop time is measured in seconds for the right cells.
- **Only client-side populated:** sufficient if the agent is fully on the operator's machine. Insufficient if the agent has cloud or cluster reach.
- **Only server-side populated:** the operator host can keep doing damage during the response window. Add client-side cutoffs.

## Speed matters

Detection that fires in fifty milliseconds and a response that takes ten minutes equals a ten-minute incident. Each row should target a maximum acceptable detection-to-response time. Suggested floors:

| Concern | Target time-to-response |
|---|---|
| Identity | 30 seconds (account for token TTL) |
| Authorization | 10 seconds (Kyverno can be applied that fast) |
| Blast radius | **5 seconds** (the one you cannot afford to lose) |
| Approval gating | 60 seconds (lower urgency; the bypass already happened) |
| Supply chain | 5 minutes (registry-level operations are slower) |

## A practiced incident order

When Sentinels fires and the on-call must execute Interventions, the order matters.

**For an active misuse incident (highest urgency):**

1. **L2-C3 + L3-C3:** contain blast radius first. Kill the process, scale to zero, NetworkPolicy emergency deny. *Five seconds. Stops the bleeding.*
2. **L3-C1:** revoke server-side identity. Disable ServiceAccount, IAM deny, OIDC revocation. *Thirty seconds.*
3. **L2-C1:** revoke client-side identity. Kill, delete credentials. *Thirty seconds.*
4. **L3-C2 + L2-C2:** lock down authorization surfaces. Emergency Kyverno deny-all, deny-all hooks. *One minute.*
5. **L3-C4:** lock approval surfaces. Branch protection, freeze deployments. *One minute.*
6. **L2-C5 + L3-C5:** quarantine supply chain if compromise vector is dependency or MCP. *Five minutes.*
7. **L2-C4:** lock client-side approval gating (covered in step 4).

**For a slow-and-low compromise (lower urgency, more precision):**

Reverse the order. Start with supply chain quarantine and identity revocation. Move to authorization shrink and approval lockdown. Blast radius containment last, only when the scope of contamination is understood.

The incident command must record which steps fired in what order and which steps were skipped. The recovery (Restorations) depends on knowing exactly what state the response left the system in.

## What this matrix deliberately does not cover

- **Restoring credentials, rebuilding RBAC, re-establishing identity flows, and unfreezing deployments.** Those are the Restorations Matrix. Do not try to combine response and recovery in one runbook; conflating them is how partial response leaves the agent in a broken half-state.
- **Human escalation, paging, communications, or incident command.** Those are organizational practices that wrap the technical response. Document them separately; the matrix gives you the technical knobs.
- **Forensic preservation.** If the incident may be investigated externally, snapshot memory and disk before destructive runbooks fire. The runbooks here optimize for speed-to-stop; preservation requires extra steps.

## Pre-staging is the precondition

Every runbook in [`interventions/`](./interventions/) assumes pre-staging:

- A **break-glass identity** with permissions to revoke, disable, and lock — separate from the agent's own identity. Stored in a hardware key or sealed-secret vault. Tested in non-prod within the last 90 days.
- A **pre-staged emergency policy directory** in source control (`emergency/` at repo root) containing the deny-all hook config, the deny-all Kyverno policy, the deny-all NetworkPolicy, the locked branch-protection JSON, and the IAM deny-all policy. These are the artifacts Interventions applies; pre-staging means seconds to apply, not minutes to write.
- **PagerDuty (or equivalent) wired to Sentinels alerts.**
- **On-call drilled on the runbooks.** Drilled, not "informed."

An incident is the wrong time to discover that emergency credentials expired, that a pre-staged policy has a typo, or that the on-call has never run the script.

## Where this matrix sits

Interventions is the third of four operational matrices:

- Covenants (Protect, NIST CSF 2.0 PR): what binds the running agent
- Sentinels (Detect, NIST CSF 2.0 DE): what watches the running agent
- **Interventions (Respond, NIST CSF 2.0 RS): what stops the running agent ← this document**
- Restorations (Recover, NIST CSF 2.0 RC): what fixes after the agent

The pre-engagement order is Sentinels → Interventions → Restorations. You cannot respond to what you have not detected, and you cannot recover from what you have not stopped.

## Reading order

1. This document — framework essay.
2. [`docs/walkthrough-agentic-interventions-engineering-actions-v5.md`](./docs/walkthrough-agentic-interventions-engineering-actions-v5.md) — engineering-actions companion (gitignored; lives in operator working notes).
3. [`interventions/`](./interventions/) — pick a cell, run the runbook (after drill).

## Citations

NIST CSF 2.0 RS.MI-* (Mitigation), RS.CO-* (Communications). NIST SP 800-61 Rev. 2 (Computer Security Incident Handling Guide). EU AI Act Articles 14 and 26. NIST AI RMF MANAGE 4.1. OWASP Agentic ASI02, ASI03, ASI04, ASI05, ASI08, ASI09, ASI10. Per-cell crosswalk in [`CITATIONS.md`](./CITATIONS.md) (interventions section to be added).
