# Content integrity: server-side

**Deliberately the weakest server-side cell in the framework, and the reason this concern was added.**

Every other concern has a server-side answer that ends the argument. RBAC denies the verb. The admission controller rejects the manifest. cosign refuses the unsigned image. The agent's opinion is irrelevant.

There is no equivalent here. **Nothing on the server side can tell a prompt injection from the document it arrived in**, because it is well-formed text on an authorized channel from an approved source. By the time anything server-side observes the agent, the manipulation has already happened.

So this cell catches the **consequence** rather than the manipulation, and it does that well enough to matter.

## What belongs here

| Control | Catches | Artifact |
|---|---|---|
| **Egress containment** | Exfiltration having anywhere to go. If the agent can only reach an approved set of hosts, a successful injection cannot post data to the attacker's endpoint | [`egress-exfiltration-policy.yaml`](./egress-exfiltration-policy.yaml) |
| **Send-side audit** | What actually left, recorded outside the agent's reach, so an incident has an evidence trail | [`egress-audit-policy.yaml`](./egress-audit-policy.yaml) |
| **DLP at the boundary** | Credentials and regulated data in outbound payloads, independent of whether the client-side scanner ran | Vendor-specific; see notes below |
| **Volume and shape anomaly** | The aggregate case, where every individual request was authorized and only the pattern is a leak | [`sentinels/blast-radius/server-side/`](../../../sentinels/blast-radius/server-side) |

## The control that actually works is not in this directory

The strongest server-side answer to prompt injection is **not a content control at all**. It is making a successful injection worthless:

- A scoped credential means the injected agent cannot reach the data worth stealing. See [`controls/identity/server-side/`](../../identity/server-side).
- Deny-by-default RBAC means it cannot perform the action. See [`controls/authorization/server-side/`](../../authorization/server-side).
- A default-deny NetworkPolicy means it cannot send anything anywhere. See [`controls/blast-radius/server-side/`](../../blast-radius/server-side).

This is why the framework's answer to "what about prompt injection?" is not "we scan for it." It is that **injection is an authorization and blast-radius problem wearing a content costume**, and those cells are where the enforcement lives.

The lethal trifecta framing makes this concrete: injection becomes exfiltration only when the agent has private data, untrusted content, and external communication together. Removing any one is a design decision available on day one and costs nothing at runtime.

## Honest limitations

- **Egress allowlists leak through allowed hosts.** If the agent may reach GitHub, exfiltration to a Gist is permitted traffic. Allowlisting by host is coarse; allowlisting by host and method and path is better and still incomplete.
- **DNS and timing channels** survive most egress policy.
- **The audit trail is after the fact.** It converts an unknown into a known, which is the Article 73 reporting requirement, and it stops nothing.
- **DLP inspects payloads it can read.** End-to-end encrypted destinations defeat it.

## Verification

```bash
# Policy must deny egress to a host outside the allowlist.
kubectl run egress-probe --rm -i --restart=Never \
  --image=curlimages/curl:8.11.1 \
  --namespace agent-claude-prod \
  -- curl -s --max-time 5 https://example.invalid && echo "FAIL: egress permitted" || echo "ok: egress denied"

# Allowlisted host must still work, or the policy is an outage.
kubectl run egress-probe --rm -i --restart=Never \
  --image=curlimages/curl:8.11.1 \
  --namespace agent-claude-prod \
  -- curl -s --max-time 5 -o /dev/null -w '%{http_code}' https://api.anthropic.com
```

Both directions, for the same reason the Kyverno suite tests both: a policy that denies everything is an outage rather than a control.
