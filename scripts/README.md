# Repository checks

This repo runs its own checks **client-side**, before a commit exists, rather than only in CI after one has been pushed. That is the same argument the framework makes about agents: a constraint that fires at the point of action beats one that reports after the fact.

## Setup

One command, once per clone:

```bash
git config core.hooksPath .githooks
```

That is the whole install. The hook is version-controlled in [`.githooks/pre-commit`](../.githooks/pre-commit), so it travels with the repo and does not need a separate tool to manage it.

The only dependency is `python3`. PyYAML is used if present and the YAML check reports itself as unavailable if it is not; nothing else is required.

## Running by hand

```bash
./scripts/check.py                  # whole repository
./scripts/check.py --staged         # only staged files, as the hook does
./scripts/check.py --only links     # one check; repeatable
```

Exit code 0 means clean, 1 means findings.

## What is checked

| Check | What it catches |
|---|---|
| `links` | Relative Markdown links that do not resolve. Resolved from each file's own directory, not the repo root, so nested cell READMEs are handled correctly |
| `yaml` | Unparseable YAML, including the machine-readable matrix data files at the root. Multi-document files are supported |
| `json` | Unparseable JSON. Settings artifacts here use `_comment` keys rather than JSONC comments so they stay valid, and this enforces that |
| `prose` | Em-dashes, and en-dashes in running prose. Identifier ranges such as `IL4–IL5` and `Art. 9(2)(a)–(d)` are allowed. Code fences are skipped |
| `placeholders` | Credential-shaped strings and non-placeholder AWS account ids in example ARNs. This is what backs the promise in [`SECURITY.md`](../SECURITY.md) that the placeholders are placeholders |
| `shell` | Runbooks that fail `bash -n`, and runbooks missing the executable bit. A runbook nobody can execute is worse than useless during the incident it was written for |

## Bypassing

`git commit --no-verify` skips the hook. That is deliberate and occasionally correct. It is not the default path, and the hook says so when it blocks.

## On CI

There is no GitHub Actions workflow here. The checks are fast, run locally, and catch the same things a workflow would, one round trip earlier. If a mirror job is ever added it should call this same script rather than reimplement the rules, so the local check and the remote one cannot disagree.
