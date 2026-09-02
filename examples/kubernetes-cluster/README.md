# Example: multi-agent Kubernetes cluster

Several agents, each in its own namespace, on a cluster you control.

This is the **inverse of the [workstation example](../claude-code-laptop/)**, and the inversion is the point. There, the server-side column was mostly unavailable and the client-side column carried weight it does not carry anywhere else. Here, the server-side column is fully available, and **client-side is the layer you lose**.

## Why client-side is weaker here, not stronger

On a laptop, a PreToolUse hook lives on the operator's machine, in a file the agent process does not own. That separation is what makes it deterministic.

In a cluster there is no operator machine. The agent is a pod, and any hook constraining it runs **inside the container it constrains**. An agent with write access to its own filesystem can edit the hook that is supposed to stop it. The separation that made the control real on a laptop does not exist here.

Three consequences, and they shape everything below:

1. **Client-side controls must be baked into the image and the filesystem made read-only**, or they are advisory. A hook on a writable `emptyDir` is decoration.
2. **The server side has to carry what the client side carried on the laptop.** RBAC, admission policy and NetworkPolicy are not defense in depth here, they are the defense.
3. **Everything client-side is inside the blast radius.** When you assess a cluster agent against [`MATURITY.md`](../claude-code-laptop/MATURITY.md), a hook in a writable container does not count toward Level 2.

## What changes when there is more than one agent

Both other examples govern a single agent. A cluster has several, and four problems appear only at N > 1:

| Problem | Control |
|---|---|
| Agent A reaching agent B's namespace | Namespace-scoped Roles only, and admission denial of any cross-namespace binding |
| Agent A talking to agent B directly | Default-deny NetworkPolicy per namespace, allowlist egress only outward |
| One agent starving the others | `ResourceQuota` and `LimitRange` per namespace |
| **Not knowing which agent did something** | A distinct ServiceAccount per agent, and audit policy keyed on it |

The fourth is the one that bites during an incident. Two agents sharing a ServiceAccount are one agent as far as every log is concerned, and you will discover that at exactly the wrong moment.

## Install order, and why it is an order

Dependencies run one way. Applying out of order produces resources that exist but do not constrain.

```bash
./bootstrap.sh agent-payments-bot          # one agent, idempotent
./bootstrap.sh --verify agent-payments-bot # prove each layer denies
```

1. **Namespace** with Pod Security `restricted`. Everything else is scoped to it, and the PSA label has to be present before the first pod, because it is evaluated at admission and not retroactively.
2. **ServiceAccount**, one per agent, `automountServiceAccountToken: false`. The token arrives through a projected volume with a bound audience and a short TTL instead.
3. **Role and RoleBinding**, namespace-scoped. Never a ClusterRole. [`controls/authorization/server-side/kyverno-no-cluster-roles.yaml`](../../controls/authorization/server-side/kyverno-no-cluster-roles.yaml) enforces that at admission, so a later mistake is denied rather than reviewed.
4. **ResourceQuota and LimitRange**, before the agent can schedule anything.
5. **NetworkPolicy default-deny**, then the allowlist. In that order: an allowlist applied first is permissive until the deny lands.
6. **Admission policies**, cluster-wide, applied once rather than per agent.
7. **Sentinels**, last, because they observe the rest.

Steps 1 to 5 are per agent. 6 and 7 are per cluster.

## Files here

| File | What it is |
|---|---|
| [`bootstrap.sh`](./bootstrap.sh) | Applies the per-agent stack in dependency order, idempotently, and refuses to continue when a step did not take |
| [`agent-namespace.yaml`](./agent-namespace.yaml) | The per-agent template, parameterized by `AGENT_NAME`. Namespace, SA, Role, RoleBinding, quota, limits, default-deny |
| [`kyverno-multi-agent.yaml`](./kyverno-multi-agent.yaml) | The policies that only matter with more than one agent |
| [`verify.sh`](./verify.sh) | Proves each control denies what it claims, and admits what it should |

Everything else is referenced from [`controls/`](../../controls/) and [`sentinels/`](../../sentinels/) rather than copied, so there is one source per artifact.

## Verification is two-directional

`verify.sh` checks both that the bad thing is denied and that the good thing still works. A cluster where the agent can do nothing is not governed, it is broken, and the two are easy to confuse from a green check.

```
[deny ] agent cannot create a Deployment in its own namespace
[deny ] agent cannot read Secrets
[deny ] agent cannot reach another agent's namespace
[deny ] agent cannot egress to an unlisted host
[admit] agent can list Pods in its own namespace
[admit] agent can read its own Pod logs
[admit] agent can reach the model API
```

The `admit` half is what catches an over-broad NetworkPolicy or a Role that denies the agent's actual job. That is the failure that gets a control switched off next quarter.

## What this example does not solve

- **A compromised control plane.** Every control here is enforced by the API server. An attacker with cluster-admin has already won, and nothing in this directory changes that.
- **Container escape.** RBAC and NetworkPolicy constrain the agent's API and network access, not the kernel. Pair with a sandboxed runtime; see [`controls/blast-radius/client-side/gvisor-runtimeclass-and-pod.yaml`](../../controls/blast-radius/client-side/gvisor-runtimeclass-and-pod.yaml).
- **The agent's cloud credentials.** IRSA means the pod's identity extends into the cloud account, and its blast radius there is bounded by the IAM policy, not by anything in the cluster. See [`controls/identity/server-side/aws-iam-trust-policy.json`](../../controls/identity/server-side/aws-iam-trust-policy.json).
- **Prompt injection.** As everywhere. The point is that a successful injection is bounded by what the ServiceAccount, the NetworkPolicy and the quota allow. See [`controls/content-integrity/`](../../controls/content-integrity/).
- **Detection and response.** [`sentinels/`](../../sentinels/) and [`interventions/`](../../interventions/). The kill switch for a cluster agent is [`interventions/authorization/server-side/kyverno-deny-all-agents.yaml`](../../interventions/authorization/server-side/kyverno-deny-all-agents.yaml), and it should be rehearsed before it is needed.
