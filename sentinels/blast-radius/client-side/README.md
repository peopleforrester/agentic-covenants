# Sentinels, Blast radius / Client-side

**Control.** bpftrace catches unexpected network attempts from the agent process tree. Falco userspace catches unsandboxed children and writes to unexpected paths. bubblewrap stderr captures EPERM (sandbox boundary) events.

**Strength.** Deterministic for events the kernel surfaces. Failure modes: Falco `proc.pname` only catches one level (use `proc.aname` for ancestors); bpftrace requires kernel headers and root; boundary events not correlated with session ID (set `SESSION_ID` in the bubblewrap launch env).

## Tooling

- `bpftrace` and kernel headers, or Falco userspace (`falco --userspace`) for portability.
- `auditd` (already configured in [`../../identity/client-side/auditd-agent.rules`](../../identity/client-side/auditd-agent.rules)).

## Files in this directory

- [`network-attempt.bt`](./network-attempt.bt), bpftrace one-liner that prints `agent_network_attempt` for any `connect()` syscall from a process tree rooted at the agent. Adjust `comm` filter for your runtime's actual process names.
- [`falco-agent-host.yaml`](./falco-agent-host.yaml), Falco userspace rules for unsandboxed agent children and writes outside `/workspace`/`/tmp`.
- [`bubblewrap-with-logging.sh`](./bubblewrap-with-logging.sh), wrapper that tees bubblewrap stderr to syslog so EPERM events surface in the SIEM.

## Verification

```bash
# 1. Falco fires on unsandboxed child
sudo -u agent-runner /usr/local/bin/claude --version &
journalctl -t falco --since "1 minute ago" | grep "Unsandboxed child"

# 2. bpftrace catches network attempt from a sandboxed agent
sudo bpftrace ./network-attempt.bt &
agent-bwrap /tmp -- /bin/sh -c 'curl https://example.com'
# expected: "agent_network_attempt" output

# 3. Boundary EPERM events shipped
journalctl -t agent-sandbox --since "1 minute ago"
# expected: bubblewrap permission denials when triggered
```

## Common mistakes

- Falco `proc.pname` only catches one level. Use `proc.aname` for ancestors.
- bpftrace requires kernel headers and root. Falco userspace is more portable but heavier.
- Boundary events not correlated with session ID. Set `SESSION_ID` in the bubblewrap launch env so events tie back.
- Falco rule `output` not parseable by SIEM. Use `json_output: true` in `falco.yaml`.

## Citation

NIST CSF 2.0 DE.CM-01, DE.CM-09. NIST SP 800-160 Vol. 1.
