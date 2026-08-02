#!/usr/bin/env bash
# ABOUTME: Verifies an enclave really has no egress to the public services the connected examples assume.
# ABOUTME: Run from inside the agent namespace before deploying. Non-zero exit means an assumption is violated.
#
# Why this exists: the failure mode is not "the enclave blocks everything." It is
# "the enclave blocks almost everything, and one proxy exception nobody remembered
# lets an agent reach a public registry." Find that at deploy time, not during an
# assessment or an incident.
#
# Satisfies (crosswalk): SC-7 (boundary protection) verification evidence;
# CA-2/CA-7 (assessment and continuous monitoring) supporting artifact.

set -uo pipefail

TIMEOUT="${TIMEOUT:-5}"
FAILURES=0
CHECKED=0

# Public endpoints the connected examples in this repo depend on. If ANY of these
# is reachable, this is not the air-gapped posture you documented to your AO.
PUBLIC_ENDPOINTS=(
  "https://ghcr.io"
  "https://registry-1.docker.io"
  "https://index.docker.io"
  "https://pypi.org"
  "https://registry.npmjs.org"
  "https://proxy.golang.org"
  "https://crates.io"
  "https://rekor.sigstore.dev"
  "https://fulcio.sigstore.dev"
  "https://api.github.com"
  "https://api.anthropic.com"
  "https://sts.amazonaws.com"
)

# In-enclave endpoints that MUST be reachable, or the deployment cannot work.
# Override via ENCLAVE_ENDPOINTS="a b c" to match your enclave's names.
read -r -a ENCLAVE_ENDPOINTS <<< "${ENCLAVE_ENDPOINTS:-https://registry.enclave.mil https://mirror.enclave.mil}"

say()  { printf '%s\n' "$*"; }
pass() { printf 'PASS  %s\n' "$*"; }
fail() { printf 'FAIL  %s\n' "$*"; FAILURES=$((FAILURES + 1)); }

reachable() {
  # Returns 0 if the endpoint answered at all (any HTTP status), 1 otherwise.
  curl -sS --max-time "$TIMEOUT" -o /dev/null "$1" 2>/dev/null
}

say "== Air-gap preflight =="
say "Timeout per check: ${TIMEOUT}s"
say ""

say "-- Public endpoints (expected UNREACHABLE) --"
for url in "${PUBLIC_ENDPOINTS[@]}"; do
  CHECKED=$((CHECKED + 1))
  if reachable "$url"; then
    fail "$url is REACHABLE — the enclave has egress it should not have."
  else
    pass "$url unreachable"
  fi
done

say ""
say "-- Enclave endpoints (expected REACHABLE) --"
for url in "${ENCLAVE_ENDPOINTS[@]}"; do
  CHECKED=$((CHECKED + 1))
  if reachable "$url"; then
    pass "$url reachable"
  else
    fail "$url is UNREACHABLE — the deployment cannot pull what it needs."
  fi
done

# DNS-level check: in a properly sealed enclave, public names should not even resolve.
# Resolution without connectivity still leaks the fact that a split-horizon DNS or a
# forwarder is configured, which is worth knowing.
say ""
say "-- DNS resolution of public names (expected to FAIL to resolve) --"
if command -v getent >/dev/null 2>&1; then
  for host in ghcr.io pypi.org rekor.sigstore.dev; do
    CHECKED=$((CHECKED + 1))
    if getent hosts "$host" >/dev/null 2>&1; then
      fail "$host RESOLVES — a DNS forwarder is reaching public resolvers."
    else
      pass "$host does not resolve"
    fi
  done
else
  say "SKIP  getent unavailable; DNS checks not run."
fi

say ""
say "== Summary: ${CHECKED} checks, ${FAILURES} failures =="
if [[ "$FAILURES" -gt 0 ]]; then
  say ""
  say "The enclave does not match the air-gapped assumptions in examples/dod-air-gapped/README.md."
  say "Either close the egress, or update your documented posture and your AO's package to match reality."
  exit 1
fi
say "Enclave posture matches the documented air-gapped assumptions."
