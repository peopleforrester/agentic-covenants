# Sentinels — Blast radius / In-agent

Forensic only; sandbox events do not surface in-agent. There is no artifact at this layer. The detection is at client-side (bpftrace, Falco userspace) and server-side (Falco containers, Hubble).

## Citation

NIST CSF 2.0 DE.CM-09 (the post-event log only).
