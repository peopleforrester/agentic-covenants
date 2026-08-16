# Example: single operator workstation

The most common agentic deployment there is. One person, one laptop, an agent with a terminal and the operator's own credentials.

It is also the deployment with the least governance, because none of the usual infrastructure is present. There is no admission controller on a laptop. There is no platform team enforcing a namespace. The server-side column of the matrix is mostly unavailable, which means the client-side column is carrying weight it does not carry anywhere else.

That is the whole difficulty of this environment, and it is why this example leads with an assessment rather than a set of files to copy.

## Start by finding out where you are

```bash
./assess.sh
```

It reads the local machine and reports a level from 0 to 4 against [`MATURITY.md`](./MATURITY.md), with the specific evidence for each finding and the next action to take. It changes nothing and needs no privileges.

Run it before copying any artifact from this directory. Most operators are Level 0 and expect to be Level 2, and knowing which controls are actually absent is more useful than installing a control you already had.

## What this environment can and cannot do

| Matrix layer | On a laptop |
|---|---|
| **In-agent (L1)** | Available, and as advisory here as anywhere. Unchanged |
| **Client-side (L2)** | **The primary enforcement layer.** Hooks, sandbox at launch, MCP allowlist, filesystem ACLs. Everything this example installs lives here |
| **Server-side (L3)** | Mostly absent locally, but not entirely. The remote side of anything the agent touches still enforces: cloud IAM, branch protection, the pre-receive hook on the git server |

The last row is the one people give up on too early. An agent on a laptop with a scoped IAM role and branch protection on the remote is meaningfully governed at L3 for the actions that matter most, even though nothing on the laptop is doing the enforcing. Push the boundary outward wherever the agent touches something with a server on the other end.

## What is different from a cluster deployment

**Credentials are the hard part.** In a cluster the agent gets a ServiceAccount and a projected token with a 15 minute lifetime. On a laptop the agent inherits whatever is in the operator's environment: a long-lived cloud key, an SSH agent with the operator's personal key loaded, a `gh` token with full repo scope. The single highest-value control in this environment is giving the agent its own credential rather than the operator's, which is Level 1 and which most setups skip.

**The sandbox must be applied at launch.** There is no admission controller to attach a security context. If the sandbox is not wrapped around the process at the moment it starts, and inherited by every child it spawns, it is not applied at all. A sandbox the agent can start a subshell outside of is decorative.

**Nothing is logged off-box by default.** A cluster gives you an audit log for free. Here, if the agent deletes the log directory, there is no second copy. Shipping decisions off the machine as they happen is what separates Level 3 from Level 4, and it is cheap.

## Files in this directory

| File | What it is |
|---|---|
| [`MATURITY.md`](./MATURITY.md) | The five-level model, what each level requires, and how each requirement is verified |
| [`assess.sh`](./assess.sh) | Reads the machine, reports a level with evidence. Read-only |
| [`settings.json`](./settings.json) | A composed deny-by-default permission posture for the workstation |
| [`launch-agent`](./launch-agent) | Sandbox-at-launch wrapper that applies the constraint before the process starts |

The per-cell artifacts these compose from live in [`controls/`](../../controls/) and are not duplicated here. Where this example references one, it references the real path.

## The order to install things in

Follow the levels. They are ordered by dependency, not by importance, so skipping ahead produces controls that cannot be verified.

1. **Give the agent its own identity** ([`controls/identity/client-side/provision-credential.sh`](../../controls/identity/client-side/provision-credential.sh)). Everything downstream depends on being able to tell agent action from operator action.
2. **Deny by default** ([`settings.json`](./settings.json), [`controls/authorization/client-side/pre_tool_use.sh`](../../controls/authorization/client-side/pre_tool_use.sh)).
3. **Sandbox at launch** ([`launch-agent`](./launch-agent), composing [`controls/blast-radius/client-side/agent-bwrap`](../../controls/blast-radius/client-side/agent-bwrap) on Linux or [`claude.sb`](../../controls/blast-radius/client-side/claude.sb) on macOS).
4. **Pin the supply chain** ([`controls/supply-chain/client-side/mcp-allowlist.json`](../../controls/supply-chain/client-side/mcp-allowlist.json)).
5. **Ship decisions off the box** ([`sentinels/identity/client-side/vector.toml`](../../sentinels/identity/client-side/vector.toml)).

## What this example does not solve

- **A compromised operator account.** Every control here runs as the operator and is configurable by the operator. This bounds what a misbehaving agent does, not what a hostile human does.
- **The agent reading things it should not.** Filesystem ACLs and the sandbox mount set bound this, but an agent with read access to the operator's home directory has read access to the operator's secrets. Moving secrets out of the agent's mount namespace is a real control and is not automatic.
- **Prompt injection.** Nothing here prevents the agent from being convinced to do something. The point is that being convinced is not sufficient, because the hook and the sandbox do not read the conversation.
- **Anything after the fact.** This directory is Protect. Detection is [`sentinels/`](../../sentinels/), stopping it is [`interventions/`](../../interventions/), and recovering is [`restorations/`](../../restorations/).
