# Restorations — Blast radius / Client-side

**Precondition.** Interventions L2-C3 has fired (process tree killed, sandbox torn down). Identity and Authorization restorations rows complete. **If the operator host itself is suspect, reimage from a known-good base before running this script.**

**Authority.** On-call.

## Tooling

- A known-good base image for the operator host (a hardware refresh image, an AMI, a Vagrant box, etc.).
- `cosign` to verify the agent runtime signature on reinstall.
- `strace` to re-derive seccomp allowlists against the rebuilt workload.

## Files in this directory

- [`agent-restore-host-local`](./agent-restore-host-local) — runbook script. Reinstalls the agent runtime from a verified source with cosign signature check, reapplies the bubblewrap launcher and Seatbelt profile from source, optionally re-derives the seccomp allowlist using `strace`.

## Verification

```bash
# 1. Agent runtime signature verifies
cosign verify-blob --signature /usr/local/bin/claude.sig /usr/local/bin/claude

# 2. Bubblewrap launcher in place
ls -la /usr/local/bin/agent-bwrap

# 3. Seccomp profile loaded at next launch
sudo -u agent-runner /usr/local/bin/agent-bwrap /tmp -- /bin/sh -c 'unshare -n echo test' 2>&1 \
  | grep -i "operation not permitted" || echo "FAIL: seccomp not enforcing"
```

## Common failure modes

- Hardware-level compromise (firmware, BIOS) survives reimage. Hardware replacement may be required for top-tier compromises.
- Sandbox profile re-derived against a still-compromised workload — the new profile inherits the malicious syscall pattern. Derive against a clean baseline only.

## Citation

NIST CSF 2.0 RC.RP-01. NIST AI RMF MANAGE 4.1. OWASP ASI05, ASI08. NIST SP 800-160 Vol. 1.
