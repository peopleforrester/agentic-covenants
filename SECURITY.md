# Security policy

## What this repository is, for threat-model purposes

This repo ships **documentation and copy-ready templates**. It has no runtime, no package manifest, no build, and no published artifact. Nothing here executes anywhere unless you copy it into your own environment and run it deliberately.

That shapes what a vulnerability means here. There are three categories worth reporting, and they are handled differently.

## 1. A defect in an artifact in this repo

An example policy that does not do what its README claims, a hook with a logic error, a verification command that reports success when the control is not actually in place, a YAML that admits what it says it denies.

These are the highest-severity issues this repo can have, because someone may have copied the artifact and believed it. **Open a public issue.** There is no embargo value in withholding it: the fix is a corrected template, and everyone who copied the broken one needs to know.

Please include the file path, what you expected, and what actually happened.

## 2. A bypass in a control the framework recommends

A documented way to defeat something in [`controls/`](./controls) that [`BYPASSES.md`](./framework/BYPASSES.md) does not already list.

- **If the bypass is already public** (a published CVE, a vendor advisory, a conference talk, a blog post), open a PR or issue adding it to `BYPASSES.md` with the source. This is one of the most valuable contributions to the project.
- **If the bypass is novel and not yet public**, do not open an issue here. Report it to the affected vendor or project first, through their own disclosure process. This repo is not a disclosure venue and cannot coordinate a fix in someone else's software. Once it is public, please come back and add it.

## 3. A vulnerability in this repository's own infrastructure

Secrets or personal information committed to the tree or present in git history, a malicious commit, or a compromised maintainer account.

Report these privately. Use GitHub's **[private vulnerability reporting](https://github.com/peopleforrester/agentic-covenants/security/advisories/new)** on this repository, or contact the maintainer directly rather than opening a public issue.

## What is deliberately not a vulnerability

- **Placeholders.** `123456789012`, `REPLACE_WITH_DIGEST_FROM_CRANE`, `registry.enclave.mil`, `agent-claude-prod`, and the example public-key blocks are intentional and must be substituted by the adopter. They are not leaked credentials.
- **Permissive examples shown as counter-examples.** Some artifacts deliberately show a misconfiguration in order to name it, such as a wildcard IAM `Resource` in a "common mistakes" section.
- **Bypasses that are already documented.** If it is in `BYPASSES.md`, it is a known and accepted limitation of that layer, which is why the framework has three.

## Supported versions

There is no release train. `main` is the current state, and the framework is versioned by its git history rather than by tags. Currency is the product: if you are reading a fork or a copy, check it against `main` before relying on any version pin, regulatory date, or framework citation.

## A note on the artifacts themselves

Every template here is a starting point that you are expected to review before deploying. Treat a policy copied from this repo the way you would treat a policy copied from any other public source: read it, understand what it denies, and verify it in your own environment. The [`checklists/`](./checklists) exist for exactly that step.
