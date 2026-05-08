#!/usr/bin/env python3
# ABOUTME: Hashes MCP server tool descriptions in a canonical order and compares to the allowlist for rug-pull defense.
# ABOUTME: Run after the MCP handshake. Mismatch causes the agent runtime to refuse the connection until the operator re-approves.

import argparse
import hashlib
import json
import sys
from pathlib import Path


ALLOWLIST_PATH_DEFAULT = "/etc/agents/mcp-allowlist.json"


def hash_tool_descriptions(tool_list: list) -> str:
    """Stable hash over tool descriptions, ignoring ordering.

    The canonical form sorts tools by name, normalizes the input schema by
    sorting its keys, and concatenates with explicit separators so a tool
    that contains the separator literally cannot collide with a different
    tool whose name happens to match.
    """
    canonical = sorted(
        [
            (
                t.get("name", ""),
                t.get("description", ""),
                json.dumps(t.get("inputSchema", {}), sort_keys=True),
            )
            for t in tool_list
        ],
        key=lambda x: x[0],
    )
    h = hashlib.sha256()
    for name, desc, schema in canonical:
        h.update(name.encode())
        h.update(b"\x00")
        h.update(desc.encode())
        h.update(b"\x00")
        h.update(schema.encode())
        h.update(b"\xff")
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Hash MCP tool descriptions and compare to allowlist (rug-pull defense)."
    )
    parser.add_argument("server_name", help="The MCP server name as it appears in the allowlist.")
    parser.add_argument(
        "--allowlist",
        default=ALLOWLIST_PATH_DEFAULT,
        help=f"Path to allowlist JSON (default: {ALLOWLIST_PATH_DEFAULT}).",
    )
    parser.add_argument(
        "--tools-from-stdin",
        action="store_true",
        help="Read the MCP tool list as JSON from stdin (default: true; given for clarity).",
    )
    args = parser.parse_args()

    try:
        tools = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        print(f"BLOCKED: {args.server_name} sent malformed tool list: {exc}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(tools, list):
        print(
            f"BLOCKED: {args.server_name} tool list is not a JSON array",
            file=sys.stderr,
        )
        sys.exit(2)

    actual = hash_tool_descriptions(tools)

    try:
        allowlist = json.loads(Path(args.allowlist).read_text())
    except FileNotFoundError:
        print(f"BLOCKED: allowlist not found at {args.allowlist}", file=sys.stderr)
        sys.exit(2)

    server_entry = allowlist.get("servers", {}).get(args.server_name)
    if not server_entry:
        print(f"BLOCKED: {args.server_name} not in allowlist", file=sys.stderr)
        sys.exit(2)

    expected = server_entry.get("tool_descriptions_sha256")
    fail_on_change = allowlist.get("policy", {}).get("fail_on_tool_description_change", True)

    if not expected or expected.startswith("REPLACE_AFTER_FIRST_HANDSHAKE"):
        # First handshake; record-and-prompt rather than block.
        print(
            f"FIRST-USE: {args.server_name} tool descriptions sha256 = {actual}",
            file=sys.stderr,
        )
        print(
            "Update mcp-allowlist.json: set servers[" + args.server_name + "].tool_descriptions_sha256 = " + actual,
            file=sys.stderr,
        )
        sys.exit(0)

    if actual != expected:
        print(f"BLOCKED: {args.server_name} tool descriptions changed (rug-pull?)", file=sys.stderr)
        print(f"  expected: {expected}", file=sys.stderr)
        print(f"  actual:   {actual}", file=sys.stderr)
        print(
            f"  Re-approve with: mcp-approve {args.server_name} --tool-descriptions-sha {actual}",
            file=sys.stderr,
        )
        if fail_on_change:
            sys.exit(2)

    print(f"OK: {args.server_name} tool descriptions match allowlist")


if __name__ == "__main__":
    main()
