# Tests

Verification for the artifacts in this repository. Runs client-side, with no cluster and no CI round trip.

```bash
kyverno test tests/kyverno/     # policy tests alone
./scripts/check.py              # everything, including these
```

## Why this directory exists

This framework argues that an asserted control is not an enforced one. A framework making that argument whose own policies had never been verified to load had the problem it was built to name. That was [issue #2](https://github.com/peopleforrester/agentic-covenants/issues/2).

## What the Kyverno suite asserts

Both directions, which is the point:

- **Deny cases.** A manifest that violates the covenant must be rejected.
- **Admit cases.** A correctly-scoped manifest must be accepted. A policy that denies everything is an outage rather than a control, and only the admit cases can tell the difference.

The admit cases earned their place on the first run. `kyverno-no-cluster-roles.yaml` denied every Role in a cluster, including correctly-scoped ones, because two rules nested a map pattern under `verbs` and `resources`, which are lists of strings. The deny cases all passed while the policy was broken. Only the admit cases caught it.

## Adding a test when you add a policy

1. Put fixtures in `tests/kyverno/resources/`, one file per resource kind.
2. Add both a `fail` and a `pass` entry to `tests/kyverno/kyverno-test.yaml` for every rule.
3. Run `kyverno test tests/kyverno/` and confirm the counts.

A rule with only a deny case is half-tested, and it is the half that hides outages.

## Verified against

Kyverno CLI 1.17.1, 2026-08-17. The version is recorded because a policy that loads today can fail to load after a syntax change upstream, and a claim with no date behind it is the thing this repo exists to argue against.
