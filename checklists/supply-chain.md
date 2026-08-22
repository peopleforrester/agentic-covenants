# Checklist: Supply chain

> **Is everything this agent loads verified before it is trusted?**

Agent: ________________  Charter ref: ________________  Risk tier: ____  Date: __________
Auditor: ________________  Owner present: ________________

Declared dependencies from the charter (model, MCP servers + hashes, base image digest):
_________________________________________________________________________________

---

## L1, In-agent

**No enforcement at this layer.** The model is unreliable about provenance, roughly 24% of hallucinated imports in code generation point at nonexistent packages, which is the same surface slopsquatting attacks target.

- [ ] Prompt tells the agent to install only what the lockfile pins
- [ ] Nobody treats "this package looks fine" from the model as a signal

**Mark:** `[N/A]`, no enforcement at this layer

---

## L2, Client-side

- [ ] MCP allowlist exists, with **binary sha256 pinned** per server
- [ ] **Tool-description hash pinned on first approval and re-checked at every handshake** (rug-pull defense: day-7 descriptions can differ from day-1)
- [ ] Allowlist file owned by operator; the agent's user cannot write it
- [ ] Unsigned MCP servers rejected at handshake, or the exception is written down
- [ ] Lockfiles pinned **and** validated server-side (a lockfile the agent can edit is self-attesting)
- [ ] Skill/extension marketplace installs scanned, publisher trust does **not** transfer to individual artifacts
- [ ] Security scanners themselves pinned by digest, not floating tags

**Verify:**
```bash
mcp-launch unknown-server                       # must fail: not in allowlist
echo x >> /usr/local/bin/mcp-filesystem && mcp-launch filesystem   # must fail: sha mismatch (then restore)
# modify a tool description in a test MCP server, restart:
#   mcp-verify-tools.py must BLOCK with expected vs actual hash
```

**Known bypasses accepted?** agent edits the allowlist · direct API calls outside MCP · trust-on-first-use without re-verification · `--no-verify` skipping pre-commit scans

**The scanner is part of your supply chain.** Trivy shipped a malicious `v0.69.4` and compromised Actions in March 2026. Teams running "the scanner" to defend their supply chain pulled a backdoored scanner. Pin and verify the tools whose job is verification.

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## L3, Server-side

- [ ] Admission verifies **cosign signatures**; unsigned images rejected
- [ ] Keyless trust policy pins an **issuer and a subject regex**, `subject: "*"` accepts anyone's signature
- [ ] Images pinned **by digest**, not tag (a tag moves; a digest does not)
- [ ] Registry allowlist enforced at admission, covering `containers`, `initContainers`, **and** `ephemeralContainers`
- [ ] SBOM attestation required, and actually checked against vulnerability data (provenance for a malicious package is still a malicious package)
- [ ] Egress restricted to approved registry and MCP domains at the **network layer**, not just agent config
- [ ] Lockfile-integrity job runs in CI **before merge**, regardless of local `--no-verify`
- [ ] Air-gapped: self-hosted Sigstore, or static-key verification with documented key custody

**Verify:**
```bash
kubectl run t --image=docker.io/alpine -n <ns>          # must be REJECTED (unsigned + wrong registry)
cosign tree <registry>/<image>@sha256:<digest>          # SPDX attestation present?
kubectl exec -n <ns> <pod> -- curl -sS --max-time 3 https://example.com   # must fail (egress fenced)
```

**Known bypasses accepted?** signing-infrastructure compromise · signature stripping at a mirror · a namespace exception admitting unsigned images · cached images on nodes surviving a registry delete · signed-but-malicious

**Mark:** `[ ]` / `[~]` / `[N/A]`, reason: ____________________

---

## Row verdict

☐ All three present ☐ Client-side only, lockfiles are unenforced ☐ Server-side only ☐ Gaps

**Charter drift check:** do the runtime MCP hashes and image digest match `dependencies` in the charter? ☐ yes ☐ **no, finding**

**Federal/DoD note.** 800-53 **SR-3, SR-4, SR-5, SR-11, SA-11, CM-14, SI-7**; CSF 2.0 **GV.SC-07**, **ID.RA-09**; DoD ZT **Application & Workload**; RAI *Reliable*, *Traceable*. In an enclave, public Sigstore and public registries do not exist, see [`examples/dod-air-gapped/`](../examples/dod-air-gapped) for the substitutions and what each one satisfies.

**Named incidents worth knowing before this audit:** postmark-mcp (first in-the-wild malicious MCP server, ~300 orgs), ClawHavoc (1,184+ malicious marketplace skills), Trivy (the scanner itself), CVE-2026-5058/5059 (unauthenticated MCP RCE, CVSS 9.8).

**Open items:**

| # | Gap | Owner | Due |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
