# Agentic Covenants

**A practitioner framework for autonomous-agent governance.** Six matrices, mapped to NIST CSF 2.0's six functions, with working artifacts in every populated cell.

```
        Govern      Identify      Protect      Detect      Respond      Recover
       ┌───────┐   ┌─────────┐   ┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌──────────────┐
       │Charter│ → │Inventory│ → │Covenants│  │Sentinels│  │Interventions│  │Restorations  │
       └───────┘   └─────────┘   └─────────┘  └─────────┘  └─────────────┘  └──────────────┘
        authorize   track          bind         watch        stop             rebuild
```

The framework that tells a platform engineer *which Kyverno policy to write on Monday morning*, *which Falco rule alerts on Tuesday*, *which kill-switch runbook fires on Wednesday*, and *which backup to restore from on Thursday*.

---

## TL;DR — start with Covenants

Stop trying to prompt your way out of an agent governance problem.

The **Agentic Covenants Matrix** ([`MATRIX.md`](./MATRIX.md)) is the prevention layer. Three columns, five rows, fifteen cells. Each cell answers: *if the agent decides to violate this concern, what stops it at this layer?*

| Concern | In-agent (advisory) | Client-side hooks | Server-side enforcement |
|---|---|---|---|
| **Identity** | system-prompt declaration | per-agent credentials, FS ACLs | dedicated SA / IAM, OIDC, short-TTL tokens |
| **Authorization** | scoped tool descriptions | `--allowedTools`, PreToolUse, pre-commit | RBAC, IAM, Kyverno/OPA admission |
| **Blast radius** | refusals (verified-bypassable) | sandbox at launch, seccomp/AppArmor, dry-run | gated IaC apply, ResourceQuota, NetworkPolicy, immutable backups |
| **Approval gating** | "are you sure?" (93% rubber-stamp ceiling) | tiered hooks, judgment-query escalation | branch protection (`enforce_admins: true`), CODEOWNERS, plan-and-apply split |
| **Supply chain** | warning prompt | MCP allowlist + tool-description hashing, Sigstore, lockfile pinning | cosign verification, SBOM admission, egress NetworkPolicy |

Every cell ships working artifacts in [`controls/`](./controls/).

---

## The six matrices

| Matrix | Function | Question | Top-level | Artifacts |
|---|---|---|---|---|
| **Charter** | Govern (GV) | *Who authorized this agent to exist?* | [`CHARTER_MATRIX.md`](./CHARTER_MATRIX.md) | [`charter/`](./charter/) — policy templates |
| **Inventory** | Identify (ID) | *What agents exist and what do they touch?* | [`INVENTORY_MATRIX.md`](./INVENTORY_MATRIX.md) | [`inventory/`](./inventory/) — registration daemon, discovery scripts |
| **Covenants** | Protect (PR) | *What stops the agent from violating?* | [`MATRIX.md`](./MATRIX.md) | [`controls/`](./controls/) — Kyverno, RBAC, seccomp, hooks |
| **Sentinels** | Detect (DE) | *What just happened?* | [`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md) | [`sentinels/`](./sentinels/) — Falco, audit, SIEM rules |
| **Interventions** | Respond (RS) | *How do I stop the bleeding now?* | [`INTERVENTIONS_MATRIX.md`](./INTERVENTIONS_MATRIX.md) | [`interventions/`](./interventions/) — kill-switch runbooks |
| **Restorations** | Recover (RC) | *How do I get back to known-good?* | [`RESTORATIONS_MATRIX.md`](./RESTORATIONS_MATRIX.md) | [`restorations/`](./restorations/) — rebuild runbooks |

The flow: **Charter authorizes → Inventory tracks → Covenants binds → Sentinels watches → Interventions stops → Restorations rebuilds → feedback loops back to Charter.**

A defensible posture has at minimum Charter, Inventory, and Covenants populated, with Sentinels in flight. Interventions and Restorations come online when the org has the operational maturity to handle the runbook complexity.

## What this is

The practitioner-layer realization of:

- **NIST Cybersecurity Framework 2.0** (CSF 2.0): all six functions.
- **NIST AI RMF 1.0** GOVERN, MAP, MEASURE, MANAGE; AI 600-1 GAI Profile; AI 100-2 E2025; AI Action Plan + CAISI directions.
- **OWASP** LLM Top 10 (2025), Agentic Top 10 (2026), MCP Top 10 (beta), AIVSS scoring.
- **CSA MAESTRO** seven-layer threat model.
- **ISO/IEC 42001:2023** AI management system.
- **EU AI Act** Articles 9, 14, 15, 17, 25, 26.
- **NIST SPs**: 800-207 (Zero Trust), 800-218 / 218A (SSDF / GenAI Profile), 800-160 Vol. 1 (defense in depth), 800-61 Rev. 2 (incident handling), 800-34 Rev. 1 (contingency planning), 800-92 (log management), 800-63 Rev. 4 (digital identity).
- **Government / international**: NIST NCCoE Concept Paper on AI Agent Identity (Feb 2026), CISA/NSA/FBI AI Data Security CSI (May 2025), CISA/ASD ACSC OT Principles (Dec 2025), Singapore IMDA Agentic AI Framework (Jan 2026).

The 2026 incident corpus is catalogued in [`BYPASSES.md`](./BYPASSES.md): OpenClaw ClawJacked (CVE-2026-32025), ClawHavoc, postmark-mcp, Cline/Cacheract/Clinejection, Comment-and-Control, Filesystem MCP EscapeRoute, Amazon Q CVE-2025-8217, Trend Micro Trust Signals, Check Point CVEs.

## Why prevention-first

Corporate governance (audits, reviews, quarterly access reviews, postmortems) was built for actors that are slow and have internal valence: a homeostatic stake, a pre-action pause, a learning loop. Agents collapse the time gap and have none of the internal machinery. **Scaling up post-hoc machinery either becomes a bottleneck or induces alert fatigue** — Anthropic's Auto Mode telemetry: 93% approval rate on permission prompts is the empirical ceiling.

Engineer the bad outcome out of reach (server-side). Make deterministic checks fail fast at the operator's machine (client-side). Use the in-agent layer as a nudge, not a control. Then attach Detect / Respond / Recover for residual risk.

## How to use this repo

1. **If you have nothing yet:** start with [`MATRIX.md`](./MATRIX.md) and [`controls/`](./controls/). Walk one row, populate the three cells, run the verification commands. Repeat.
2. **If Covenants is in place:** add [`SENTINELS_MATRIX.md`](./SENTINELS_MATRIX.md) and [`sentinels/`](./sentinels/). Each prevention control gets a corresponding detection.
3. **If Sentinels is in place:** wire Sentinels alerts to [`interventions/`](./interventions/) runbooks. Every alert needs a runbook; alerts without runbooks are theatre.
4. **If you have an incident response capability:** add [`restorations/`](./restorations/) for the rebuild after intervention.
5. **If you face a regulatory review (EU AI Act, ISO/IEC 42001):** start with [`CHARTER_MATRIX.md`](./CHARTER_MATRIX.md) and the templates under [`charter/templates/`](./charter/templates/).
6. **If you have agents proliferating without ownership:** start with [`INVENTORY_MATRIX.md`](./INVENTORY_MATRIX.md) and the discovery tooling under [`inventory/identity/discovered/`](./inventory/identity/discovered/).

## Layout

```
agentic-covenants/
├── README.md
├── MATRIX.md, BYPASSES.md, CITATIONS.md, matrix.yaml      # Covenants (Protect)
├── SENTINELS_MATRIX.md, sentinels.yaml                     # Sentinels (Detect)
├── INTERVENTIONS_MATRIX.md, interventions.yaml             # Interventions (Respond)
├── RESTORATIONS_MATRIX.md, restorations.yaml               # Restorations (Recover)
├── CHARTER_MATRIX.md, charter.yaml                         # Charter (Govern)
├── INVENTORY_MATRIX.md, inventory.yaml                     # Inventory (Identify)
├── controls/{identity,authorization,blast-radius,approval-gating,supply-chain}/
├── sentinels/      (mirror of controls/)
├── interventions/  (mirror; in-agent cells deliberately empty)
├── restorations/   (mirror; in-agent cells deliberately empty)
├── charter/        (organizational / domain / agent layers — policy templates)
└── inventory/      (self-declared / operator-declared / discovered layers — registration + discovery tooling)
```

## License

Dual-licensed:

- **Code** (shell, Python, Terraform, Rego, YAML policy, hooks, runbook scripts) under [Apache 2.0](./LICENSE-CODE).
- **Content** (Markdown, the matrices, the citations, the framework text) under [CC BY-SA 4.0](./LICENSE-CONTENT).

See [`LICENSE`](./LICENSE) for the split rule.

## Contributing

A reviewer who finds an additional citation mapping is welcome to contribute it; a reviewer who finds an incorrect mapping is welcome to flag it. Both improve the document.

## Status

This repo is the practitioner layer beneath OWASP (which catalogs the threats), NIST (which governs and structures), CSA MAESTRO (which models the attack surface), ISO/IEC 42001 (which provides the management system), the EU AI Act (which sets the regulatory floor), and lab-side capability frameworks (which govern what models are released). **None of those tells a platform engineer what to commit on Monday morning. This does.**

## For US federal and DoD readers

The five concerns line up almost one-to-one with the five risk categories named in **"Careful Adoption of Agentic AI Services"** (CISA, NSA, ACSC, Canadian Centre for Cyber Security, NZ NCSC, UK NCSC — April 30, 2026), the first multi-nation joint guidance on agentic AI.

[`CITATIONS.md`](./CITATIONS.md#us-dod--federal-crosswalk) carries a **US DoD / federal crosswalk**: NIST SP 800-53 Rev. 5 control families per concern, DoD Zero Trust pillars, RMF / cATO / CSRMC, DoD Responsible AI principles, ICAM NPE constraints, and Cloud SRG Impact Levels. [`examples/dod-air-gapped/`](./examples/dod-air-gapped/) is an IL4–IL5 variant with every public dependency (Sigstore, public registries, commercial IdP) replaced by an in-enclave equivalent, plus the ICAM PE-to-NPE binding.

The framing that matters: **ICAM tells you who the agent is and what it may reach. Zero Trust conditional access tells you whether this request is permitted right now. Neither tells you what an authenticated, authorized agent is permitted to *do* once it is inside.** RMF to cATO already moved assurance out of periodic review and into the infrastructure; CSRMC made that the default. This framework applies the same relocation to agent behavior. As of July 2026 there is still no official US government policy specifically on agentic AI (CRS IF13151), so these are crosswalks a program can defend to an AO, not compliance claims.
