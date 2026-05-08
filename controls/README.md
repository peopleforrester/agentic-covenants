# Controls

Working artifacts for every cell of the Covenants Matrix. Each subdirectory under `controls/` is one of the five concerns; each concern has three layer subdirectories (`in-agent/`, `client-side/`, `server-side/`).

## Layout

```
controls/
├── identity/{in-agent,client-side,server-side}/
├── authorization/{in-agent,client-side,server-side}/
├── blast-radius/{in-agent,client-side,server-side}/
├── approval-gating/{in-agent,client-side,server-side}/
└── supply-chain/{in-agent,client-side,server-side}/
```

## What each cell directory contains

Every cell directory has the same six-section README:

1. **Control.** One-line summary from [`MATRIX.md`](../MATRIX.md).
2. **Tooling.** What to install or enable.
3. **Files in this directory.** What each artifact does and where it goes in your environment.
4. **Verification.** How you confirm the control is enforcing what it claims.
5. **Common mistakes.** Bypasses from [`BYPASSES.md`](../BYPASSES.md) that defeat this cell if you do it wrong.
6. **Citation.** From [`CITATIONS.md`](../CITATIONS.md).

The artifacts themselves are templates with sensible defaults. Names like `agent-claude-prod`, `claude-code`, and `1.2.3.4` are placeholders. Every YAML, shell script, and JSON file is annotated so you can find the substitution points.

## A note on the in-agent layer

The in-agent cells contain a `system-prompt-template.md` and not much else. That is by design. The in-agent layer is advisory only — it has no enforcement and the matrix repeatedly says so. If you find yourself building a 200-line in-agent prompt to enforce a security property, stop. Move the property to client-side or server-side.

## Order of operations

Build server-side first, client-side second, in-agent last. Reason: server-side does not depend on the agent or operator behaving correctly. If you only have time for one row, build the bottom one. The week-by-week rollout sequence is at the end of [`MATRIX.md`](../MATRIX.md).
