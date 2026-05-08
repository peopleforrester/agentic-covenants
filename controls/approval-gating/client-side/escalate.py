#!/usr/bin/env python3
# ABOUTME: Judgment-query escalation tool. The agent calls this when it hits a value-laden decision it cannot make alone.
# ABOUTME: Distinct from yes/no approval: the operator supplies the missing input, not a binary answer.

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


ESCALATE_URL = os.environ.get(
    "ESCALATE_URL",
    "https://escalate.example.com/api/queries",
)
ESCALATE_TIMEOUT_SEC = int(os.environ.get("ESCALATE_TIMEOUT_SEC", "600"))


def escalate(question: str, context: dict, tier: str = "judgment") -> str:
    """Send a judgment query to the operator and return the operator's input.

    The operator is expected to provide a free-form response, not a yes/no.
    This is the load-bearing distinction from `approve()`: an approval is
    bypassable through alert fatigue; a judgment query is not, because the
    response is not on a small set of values the operator can rubber-stamp.
    """
    token = os.environ.get("ESCALATE_TOKEN")
    if not token:
        print("ESCALATE_TOKEN not set; refusing to escalate without auth.", file=sys.stderr)
        sys.exit(2)

    payload = json.dumps(
        {
            "question": question,
            "context": context,
            "tier": tier,
            "session_id": context.get("session_id"),
        }
    ).encode()

    req = urllib.request.Request(
        ESCALATE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ESCALATE_TIMEOUT_SEC) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        print(f"escalate.py: transport error: {exc}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError:
        print("escalate.py: malformed response from escalation service", file=sys.stderr)
        sys.exit(2)

    operator_input = body.get("operator_input")
    if not operator_input:
        print("escalate.py: operator did not supply input; default deny", file=sys.stderr)
        sys.exit(2)
    return operator_input


def main():
    parser = argparse.ArgumentParser(
        description="Send a judgment query to the operator. The operator supplies the missing input, not yes/no.",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="Read a JSON blob from stdin with keys: question, context, tier (optional).",
    )
    parser.add_argument("--question", help="The question to ask. Used when --from-stdin is not set.")
    parser.add_argument("--session-id", help="Session ID for correlation.")
    parser.add_argument("--tier", default="judgment", help="Tier label for the dashboard.")
    args = parser.parse_args()

    if args.from_stdin:
        payload = json.loads(sys.stdin.read())
        response = escalate(
            question=payload["question"],
            context=payload["context"],
            tier=payload.get("tier", "judgment"),
        )
    else:
        if not args.question:
            parser.error("--question is required when --from-stdin is not set.")
        response = escalate(
            question=args.question,
            context={"session_id": args.session_id or "default"},
            tier=args.tier,
        )
    print(json.dumps({"operator_input": response}))


if __name__ == "__main__":
    main()
