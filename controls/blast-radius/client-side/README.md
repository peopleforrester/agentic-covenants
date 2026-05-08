# Blast radius / Client-side

**Control.** Sandbox at process launch with inheritance enforcement. Linux: bubblewrap. macOS: Seatbelt. Containerized: gVisor. Network isolation via unix-domain-socket egress proxy. Seccomp or AppArmor profile applied at launch. `--network none` for non-network tasks. Read-only volume mounts. Dry-run defaults.

**Strength.** Deterministic for the syscall and filesystem surface covered by the profile. Bypass through unsandboxed children when inheritance is not enforced, profile gaps, kernel-level escape (rare), or read-only mounts that are read-only at the bind but writable elsewhere on the same FS via a different mountpoint.

## Tooling

- `bubblewrap` (Linux): `apt-get install bubblewrap` or `dnf install bubblewrap`. Version 0.10 or later.
- Seatbelt (macOS): built into macOS as `sandbox-exec`.
- gVisor (containers): `runsc` runtime. Install per gVisor docs.
- `seccomp` (Linux): kernel feature; profiles via systemd `SystemCallFilter=` or container runtime `--security-opt seccomp=`.
- AppArmor (Linux): kernel LSM; profiles in `/etc/apparmor.d/`.

## Files in this directory

- [`agent-bwrap`](./agent-bwrap) — bubblewrap launcher script. Drop in `/usr/local/bin/`. Wraps the agent in a sandbox with inheritance enforcement (`--die-with-parent`, `--new-session`), no network by default, capability dropping. The systemd unit in [`../../identity/client-side/claude-code-prod.service`](../../identity/client-side/claude-code-prod.service) can call this instead of `claude` directly.
- [`seccomp-claude.json`](./seccomp-claude.json) — illustrative seccomp profile in OCI format. **Use `strace -c` against your real workload to derive the actual minimal allowlist.** Anthropic publishes a reference seccomp profile for Claude Code in their sandbox docs; consult the current list.
- [`claude.sb`](./claude.sb) — Seatbelt sandbox profile for macOS. Run with `sandbox-exec -D WORKSPACE="$PWD" -D HOME="$HOME" -f claude.sb /usr/local/bin/claude`.
- [`gvisor-runtimeclass-and-pod.yaml`](./gvisor-runtimeclass-and-pod.yaml) — Kubernetes RuntimeClass declaring `runsc` and a sample Pod that uses it. Combines with the Pod from [`../../identity/server-side/pod-with-projected-token.yaml`](../../identity/server-side/pod-with-projected-token.yaml).

## Verification

```bash
# 1. Sandbox is active: a privileged read fails
agent-bwrap /tmp -- /bin/sh -c 'cat /etc/shadow'
# expected: failure (file not bound or not readable)

# 2. Network is blocked
agent-bwrap /tmp -- curl -sS https://example.com
# expected: connection refused or no network

# 3. Child inheritance is enforced
agent-bwrap /tmp -- /bin/sh -c 'sh -c "curl -sS https://example.com"'
# expected: also fails

# 4. Seccomp profile is loaded (test inside a container)
docker run --rm --security-opt seccomp=/etc/agents/seccomp-claude.json \
  alpine /bin/sh -c 'unshare -n /bin/sh'
# expected: Operation not permitted if unshare not in allowlist

# 5. gVisor runtime is in effect
kubectl exec claude-agent -- dmesg | head
# expected: runsc-specific output ("Starting gVisor...")
```

## Common mistakes

- Sandbox set on the parent only; child processes inherit nothing. Use `--die-with-parent` and `--new-session`.
- `--unshare-net` plus a forgotten `--bind /run/network-namespace` that re-exposes networking.
- Seccomp profile that allows `clone` without flag filtering. Agents spawn unsandboxed children via `clone(CLONE_NEWNS)`.
- AppArmor profile in complain mode (logs but does not enforce). Confirm with `aa-status`.
- Read-only mounts that are read-only at the bind but writable elsewhere on the same FS via a different mountpoint.
- Egress proxy allowlist living inside the sandbox. The allowlist must live outside the sandbox so a compromised agent cannot rewrite it.

## Citation

NIST CSF 2.0 PR.PS-01, PR.PS-05, PR.PS-06 (secure software development practices), PR.IR-01 (networks protected). NIST AI RMF MANAGE 2.4. OWASP LLM05, LLM10 (Unbounded Consumption). OWASP ASI05 (Unexpected Code Execution). NIST SP 800-160 Vol. 1 (defense in depth).
