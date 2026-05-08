# Sentinels — Authorization / In-agent

**Control.** Tool descriptions logged with each call (forensic).

**Strength.** Forensic only.

## Tooling

- Whatever logs your agent runtime emits per tool call. For Claude Code, see `~/.claude/sessions/`.

## Files in this directory

(None. The capture is a property of the agent runtime; the shipping is handled by `../../identity/in-agent/ship-sessions.sh`.)

## Verification

Find a known tool call in the shipped session log and confirm its description was captured.

## Common mistakes

- Trusting tool descriptions in the session log to be authoritative for what the tool will actually do. Tool-description rug-pull (see [`../../supply-chain/`](../../supply-chain/)) means the description at call time may differ from the description at approval time.

## Citation

NIST CSF 2.0 DE.CM-09.
