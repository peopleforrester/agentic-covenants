#!/usr/bin/env bash
# ABOUTME: Wraps bubblewrap so its stderr (where EPERM events surface) is teed to syslog tagged agent-sandbox.
# ABOUTME: Replace your agent's bubblewrap invocation with this wrapper; downstream Vector ships the syslog tag to SIEM.

set -euo pipefail

# All args pass through. The wrapper only adds stderr capture.
exec bwrap "$@" 2> >(tee >(logger -t agent-sandbox -p user.warning) >&2)
