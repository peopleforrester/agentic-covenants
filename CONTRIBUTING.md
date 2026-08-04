# Contributing

This repo is a governance framework, not a code project. There is no build, no test suite, and no dependency tree. Contributions are mostly prose, citations, and copy-ready policy artifacts. The bar is different from a normal repo: **the product is being correct as of now**, so accuracy and currency matter more than volume.

## The most valuable contributions

In rough order of how much they improve the framework:

1. **A citation that is wrong.** A subcategory that does not say what it is cited for, an identifier that changed (`ID.SC-04` moved to `GV.SC-07`; `GV.RR-04` in CSF 2.0 final is HR-related, not authorization), a standard that was superseded. These are defects. File them even if you cannot propose the replacement.
2. **A bypass that is missing.** If a control in `controls/` can be defeated in a way [`BYPASSES.md`](./BYPASSES.md) does not document, that is the highest-severity gap in the repo. An undocumented control that fails to its bypass is worse than no control, because someone trusted it.
3. **A version pin that has gone stale.** See [Currency](#currency-is-the-product) below.
4. **A cell that does not work as written.** An artifact that fails against the tooling version it claims to target, a verification command that does not verify what it says.
5. **An additional citation mapping.** A framework subcategory that legitimately applies and is not listed.

## Currency is the product

Any claim of these shapes is high-stakes and must be verified against a **live primary source** before you submit it:

- "Use version X" / "pin to X" / "the current stable is X"
- "X is deprecated" / "X is end-of-life" / "X does not exist"
- Any regulatory date or applicability window
- Any framework subcategory identifier

Rules for those claims:

- **Cite the primary source, dated.** The vendor's own changelog, the standards body's own publication, the registry. Not a blog post summarizing it, unless the primary source is unavailable and you say so.
- **Never trust model output or training data for a version number.** It will be confidently wrong.
- **Never recommend a version lower than the current pin** without an explicit, dated justification in the PR. Numerical regressions are almost always an error.
- **Verify the replacement is itself current.** Recommending a stale replacement is the same defect as the stale original.

If a claim cannot be verified, mark it `UNVERIFIED` inline rather than deleting it or asserting it. An honest gap is usable; a confident wrong answer is not.

## Conventions

- **In-agent (L1) cells are advisory by thesis.** In Interventions and Restorations they are deliberately *empty*; in Covenants and Sentinels they are explicitly "nudge, not control." Do not fill them in with enforcement claims. That inverts the framework's central argument. If you think an in-agent control genuinely enforces something, open an issue and make the case first.
- **Artifacts are templates, not deployments.** Keep placeholders (`REPLACE_WITH_DIGEST_FROM_CRANE`, `123456789012`, `agent-claude-prod`, `registry.enclave.mil`) and the "resolve with crane" / "substitute your ARN" comments. **Never** commit real account IDs, hostnames, credentials, or internal infrastructure names.
- **Every cell README follows the same shape**: Control, Tooling, Files in this directory, Verification, Common mistakes, Citation. Match it.
- **Every artifact carries two `ABOUTME:` comment lines** at the top saying what it is and where it goes.
- **Prose style**: no em-dashes; no aphoristic closing lines; avoid the reflexive rule of three. Match the terse, evidence-first voice of the existing cell READMEs. Write the substance and stop.
- **Crosswalks are not compliance claims.** The DoD/federal mappings in [`CITATIONS.md`](./CITATIONS.md) are defensible starting points for a conversation with an authorizing official. Do not phrase anything as "this satisfies control X."

## Making a change

1. Open an issue first for anything structural: a new cell, a new matrix, a change to what a layer means. Small fixes can go straight to a PR.
2. Branch from `main`.
3. Keep the diff small and single-purpose. A citation fix and a new example are two PRs.
4. In the PR description, state **what you verified and against what source, with the date**. For a version bump, that means the release page you read. For a citation, the standard's own text.
5. If you touched a YAML or JSON artifact, confirm it parses. If you touched a shell script, confirm `bash -n` passes.

## What will be declined

- Filling in in-agent cells with enforcement claims (see Conventions).
- Real infrastructure identifiers replacing placeholders.
- Scaffolding a test suite, CI, or a package manifest. This repo has none by design.
- Version bumps without a dated source.
- Marketing language for a vendor product. Naming a product as a real implementation of a cell is welcome; positioning it is not.
- Broad rewrites of the framework essays without a prior issue.

## Licensing of contributions

This repo is dual-licensed: code under [Apache 2.0](./LICENSE-CODE), content under [CC BY-SA 4.0](./LICENSE-CONTENT). See [`LICENSE`](./LICENSE) for the split rule.

By submitting a contribution you agree it is licensed under the same terms as the file it touches, and that you have the right to contribute it. Do not paste text from a source whose license does not permit redistribution under CC BY-SA 4.0. Quoting and citing a framework is fine; wholesale copying of its text is not.

## Reporting a security-relevant finding

If you find a bypass in a control that is deployed in the wild, treat it like any other vulnerability disclosure: contact the affected vendor or project first. This repo documents publicly disclosed bypasses. It is not a disclosure venue for a novel zero-day. Once a finding is public, a PR adding it to [`BYPASSES.md`](./BYPASSES.md) is very welcome.
