# ABOUTME: Patch fragment for mcp-verify-tools.py that emits a structured event when the tool-description hash mismatches.
# ABOUTME: This is the rug-pull alert. Add the import + call inside the existing mismatch branch.

import json
import syslog


def _emit_tool_desc_mismatch(server_name: str, expected_hash: str, actual_hash: str) -> None:
    """Emit a structured rug-pull event to local syslog tagged agent-sentinel.

    Call this from `mcp-verify-tools.py` inside the `if expected and actual != expected:`
    branch, before `sys.exit(2)`.
    """
    syslog.openlog("agent-sentinel")
    syslog.syslog(
        syslog.LOG_WARNING,
        json.dumps(
            {
                "event": "mcp_tool_desc_mismatch",
                "server": server_name,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
            }
        ),
    )


# Patch fragment to apply in mcp-verify-tools.py:
#
#     if expected and actual != expected:
#         _emit_tool_desc_mismatch(server_name, expected, actual)
#         print(f"BLOCKED: {server_name} tool descriptions changed", file=sys.stderr)
#         ...
