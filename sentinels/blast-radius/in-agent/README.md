# Sentinels, Blast radius / In-agent

**Control.** Reasoning-trace and tool-call log capture for forensics, plus a **lethal-trifecta detector** at the wrapper layer that flags when private data, untrusted content, and an external communication tool appear in the same context window.

**Strength.** Forensic for the trace. Real-time for the lethal-trifecta detector, but only because the detector runs in the wrapper, not in the agent. The agent itself cannot be trusted to surface a violation it is participating in.

## Tooling

- The transcript-shipping pipeline from [`../../identity/in-agent/`](../../identity/in-agent/).
- A wrapper that intercepts tool calls and inspects the in-context state. The reference implementation is in [`lethal-trifecta-detector.py`](./lethal-trifecta-detector.py).

## Files in this directory

- [`lethal-trifecta-detector.py`](./lethal-trifecta-detector.py), minimal reference implementation of the detector. Tags inputs as private/untrusted/external as they enter the context window; alerts when all three classes are simultaneously present and the agent attempts a tool call. Intended to wrap the agent runtime; deployment is platform-specific.

## Verification

```bash
# 1. Detector identifies the trifecta on a synthetic input
python3 lethal-trifecta-detector.py --test
# expected: prints "TRIFECTA DETECTED" with the three input classes

# 2. Detector does not fire on absence of any class
python3 lethal-trifecta-detector.py --test-negative
# expected: exits clean
```

## Common mistakes

- Implementing the detector inside the agent's prompt. The agent that violates the trifecta will not reliably report on its own violation. The detector must run outside the agent's reasoning.
- Tagging classes by content keywords alone. "Untrusted content" is identified by source (provenance), not by what it says. A polite-sounding email from an unknown sender is still untrusted content.
- Treating the detector as preventive. It is detection only; an alert fires, but the action proceeds unless paired with an Interventions runbook (kill switch, session termination).

## Citation

Forensic only at the agent layer; no direct CSF 2.0 detection mapping for the trace itself.

For the lethal-trifecta detector: Simon Willison, "the lethal trifecta for AI agents" (June 2025; cited continuously through April 2026). Operational definition of the forbidden state, private data + untrusted content + external communication. NIST CSF 2.0 DE.CM-09 (computing hardware and software monitored) for the detector itself when wired to a SIEM.
