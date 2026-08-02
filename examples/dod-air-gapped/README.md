# Example: air-gapped / DoD IL4–IL5 deployment

The rest of this repo assumes internet egress: public Sigstore (Fulcio/Rekor), `ghcr.io`, `api.anthropic.com`, PyPI, npm. **In a DoD IL4/IL5 enclave, none of those exist.** This example is the same fifteen Covenants cells with every public dependency replaced by an in-enclave equivalent, plus the identity binding that DoD ICAM actually requires.

It is written for a program office that has to defend this to an AO, so every substitution names what it satisfies.

## What changes and what does not

**Does not change.** The framework's thesis is unaffected by air-gapping. In-agent controls are still advisory. Client-side hooks still catch casual misuse. Server-side enforcement is still the backstop. The five concerns are the same five concerns. **An air gap is a network control, not a behavioral control** — it constrains where the agent can reach, and does nothing about what the agent does with what it can already reach. Several of the incidents in [`BYPASSES.md`](../../BYPASSES.md) (Replit's freeze-violation wipe, the K8s MCP read-only bypass) would have happened identically inside an enclave.

**Does change.** Every cell that depended on a public service needs an in-enclave substitute, and the identity cells need to bind to ICAM rather than to a commercial IdP.

| Cell | Connected assumption | Air-gapped substitute | Satisfies |
|---|---|---|---|
| Identity / client-side | Commercial IdP (Okta, Auth0) issues per-agent tokens | DoD PKI: NPE certificate issued under the enterprise ICAM NPE certificate lifecycle; short-lived where the CA supports it | IA-5, IA-9; ZT **User** pillar |
| Identity / server-side | Public OIDC discovery, `sts.amazonaws.com` audience | In-enclave OIDC provider (cluster issuer or enclave IdP); SPIFFE/SPIRE with an enclave trust domain; audience pinned to the enclave | IA-2, IA-8; ZT **User**; DoD ICAM NPE |
| Authorization / server-side | Public Kyverno chart pull | Mirrored chart in the enclave registry, or **in-tree ValidatingAdmissionPolicy / MutatingAdmissionPolicy** (no controller to install, no chart to mirror) | AC-3, AC-6, CM-7 |
| Blast radius / client-side | `apt`/`dnf` install of bubblewrap | Pre-baked into the STIG-hardened base image; seccomp/AppArmor profiles shipped as part of the image, not fetched | SC-39, CM-6; DISA STIG |
| Blast radius / server-side | Public Terraform registry providers | Vendored providers in an enclave mirror; `terraform init -plugin-dir` | CM-2, SA-10 |
| Approval gating / server-side | `github.com` branch protection, PagerDuty | Enclave Git (GitLab/Gitea) protected branches + CODEOWNERS equivalent; enclave paging/notification | AC-3(2), CM-3, CM-5 |
| Supply chain / client-side | Public PyPI/npm, Sigstore verification | Enclave package mirror (Artifactory/Nexus) with hash-pinned lockfiles; **self-hosted Sigstore** or offline cosign key verification | SR-4, SR-11, SI-7 |
| Supply chain / server-side | `cosign verify` against public Rekor; `ghcr.io` | **Self-hosted Sigstore** (Fulcio + Rekor in-enclave) *or* offline key-pair verification with the public key distributed as a ConfigMap; images only from the enclave registry | SR-3, SR-4, CM-14, SI-7 |
| Sentinels (all) | SaaS SIEM | Enclave SIEM (Splunk on-prem, Elastic on-prem); same event schemas | AU-6, SI-4; ZT **Visibility & Analytics** |
| Interventions | PagerDuty webhook, `gh` CLI | Enclave notification + enclave Git API; break-glass identity issued under ICAM | IR-4, IR-6; ZT **Automation & Orchestration** |

## The identity substitution is the load-bearing one

Everything else on that list is a mirroring exercise. Identity is not.

DoD ICAM requires that every **Non-Person Entity** be **under the control of an authorized Person Entity** who can create, modify, or destroy the NPE account. That is a stronger constraint than anything in the commercial framing of this repo, and it maps directly onto the Charter matrix: the agent charter's **named human owner** *is* the controlling PE, and the charter's `identifier` *is* what the NPE registry entry must reference.

Two consequences worth stating to an AO:

1. **The Charter file becomes an ICAM artifact, not just governance paperwork.** [`charter/templates/agent-charter.yaml`](../../charter/templates/agent-charter.yaml) already carries `ownership.owner_name`, `agent.identifier`, and the approval signatures. In an ICAM context those fields are the PE-to-NPE binding record.
2. **Agent NPEs must be in the same lifecycle as every other NPE.** Provisioning, rotation, and — critically — **de-provisioning**. The charter's `retirement_criteria` is the de-provisioning trigger. An agent whose owner departs and whose backup owner does not accept handoff has no controlling PE, which under FICAM means the NPE account should not continue to exist.

See [`icam-npe-binding.md`](./icam-npe-binding.md) for the field-by-field mapping.

## Files in this directory

- [`icam-npe-binding.md`](./icam-npe-binding.md) — maps agent-charter fields to ICAM NPE registry attributes and the PE control relationship.
- [`offline-cosign-verify.yaml`](./offline-cosign-verify.yaml) — Kyverno `verifyImages` using a **static public key from a ConfigMap** instead of keyless/Rekor, for enclaves with no transparency log.
- [`enclave-registry-policy.yaml`](./enclave-registry-policy.yaml) — admission policy restricting images to the enclave registry only, with an explicit deny on every public registry.
- [`airgap-preflight.sh`](./airgap-preflight.sh) — verifies the enclave actually has no egress to the public services this framework otherwise assumes, so you find out at deploy time rather than during an assessment.

## Impact Level applicability

| IL | Data | What this example assumes |
|---|---|---|
| IL2 | Non-CUI, public-releasable | Commercial cloud; the *connected* examples apply. This directory is overkill. |
| IL4 | CUI | Commercial cloud with logical separation; enclave registry and mirrors; this example applies. |
| IL5 | CUI + unclassified NSS | Physically isolated federal community cloud; this example applies with the self-hosted Sigstore path. |
| IL6 | SECRET | DISA-authorized separately; this example is a starting point, but IL6 authorization is its own regime and nothing here should be read as satisfying it. |

**A hard caveat on foundation models.** A commercial model endpoint reachable from an enclave is a contradiction. In practice DoD programs reach models through an authorized service at the right IL (for example Azure OpenAI under Azure Government at IL5) rather than through vendor public endpoints. Do not read "agent in an enclave" as "public model API in an enclave." The Charter's `dependencies.foundation_model` field must name the **authorized in-enclave or IL-appropriate endpoint**, not a vendor marketing name, or the charter is not truthful about the system boundary.

## What this example does not solve

- **Model provenance.** SBOM and signature verification cover the container and the dependency tree. They do not attest what a model weights file was trained on. That is an open problem industry-wide, not something this framework closes.
- **Cross-domain transfer.** Moving artifacts into the enclave is a cross-domain solution problem governed by its own accreditation. This example assumes artifacts are already inside.
- **IL6 and above.** See the table.
- **The behavioral gap remains the point.** Air-gapping constrains reach. Every control in [`controls/`](../../controls/) is still required, because an agent inside the enclave with valid credentials and legitimate access is exactly the threat the matrix exists to bound.
