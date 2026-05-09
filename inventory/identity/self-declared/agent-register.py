#!/usr/bin/env python3
# ABOUTME: Minimal agent self-registration daemon. POSTs registration on start, heartbeats every N sec, deregisters on shutdown.
# ABOUTME: Refuses to start if the agent's charter is missing or expired. Wrap your agent process so this runs alongside.

import argparse
import datetime as dt
import json
import os
import signal
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


REGISTRY_URL = os.environ.get("INVENTORY_REGISTRY_URL", "https://inventory.example.com")
HEARTBEAT_INTERVAL = int(os.environ.get("INVENTORY_HEARTBEAT_SEC", "60"))
INSTANCE_ID = os.environ.get("INVENTORY_INSTANCE_ID", f"{socket.gethostname()}-{os.getpid()}")


class RegistrationError(Exception):
    pass


def load_charter(charter_path: Path) -> dict:
    """Load and minimally validate the charter file. Refuse to register if charter is expired."""
    if not charter_path.exists():
        raise RegistrationError(f"Charter not found: {charter_path}")

    import yaml  # local import so the rest of this script does not require pyyaml unless a charter exists
    charter = yaml.safe_load(charter_path.read_text())

    next_review = charter.get("next_review_due")
    if next_review:
        # next_review is a date string YYYY-MM-DD per agent-charter.yaml
        if dt.date.fromisoformat(str(next_review)) < dt.date.today():
            raise RegistrationError(
                f"Charter review is overdue ({next_review}). Refusing to start agent."
            )

    return charter


def http_post(path: str, body: dict, token: str) -> dict:
    req = urllib.request.Request(
        f"{REGISTRY_URL}{path}",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def register(charter: dict, charter_ref: str, token: str) -> dict:
    body = {
        "agent_identifier": charter["agent"]["identifier"],
        "charter_ref": charter_ref,
        "charter_version": charter["charter_version"],
        "owner_email": charter["ownership"]["owner_email"],
        "instance_id": INSTANCE_ID,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "heartbeat_interval_seconds": HEARTBEAT_INTERVAL,
    }
    return http_post("/api/v1/agents/register", body, token)


def heartbeat(agent_identifier: str, token: str) -> None:
    body = {
        "agent_identifier": agent_identifier,
        "instance_id": INSTANCE_ID,
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    try:
        http_post("/api/v1/agents/heartbeat", body, token)
    except urllib.error.URLError as exc:
        # Backoff is the caller's responsibility; log and keep going.
        print(f"agent-register: heartbeat failed: {exc}", file=sys.stderr, flush=True)


def deregister(agent_identifier: str, token: str) -> None:
    body = {
        "agent_identifier": agent_identifier,
        "instance_id": INSTANCE_ID,
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    try:
        http_post("/api/v1/agents/deregister", body, token)
    except urllib.error.URLError as exc:
        print(f"agent-register: deregister failed: {exc}", file=sys.stderr, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--charter", required=True, type=Path, help="Path to the agent charter YAML.")
    parser.add_argument("--charter-ref", required=True, help="Source-of-truth path of the charter (e.g., charters/claude-code-prod.yaml).")
    args = parser.parse_args()

    token = os.environ.get("INVENTORY_TOKEN")
    if not token:
        print("INVENTORY_TOKEN not set. Refusing to start.", file=sys.stderr)
        return 2

    try:
        charter = load_charter(args.charter)
    except RegistrationError as exc:
        print(f"REFUSING: {exc}", file=sys.stderr)
        return 3

    register(charter, args.charter_ref, token)
    agent_identifier = charter["agent"]["identifier"]

    stop = False
    def _shutdown(_signo, _frame):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        while not stop:
            heartbeat(agent_identifier, token)
            for _ in range(HEARTBEAT_INTERVAL):
                if stop:
                    break
                time.sleep(1)
    finally:
        deregister(agent_identifier, token)

    return 0


if __name__ == "__main__":
    sys.exit(main())
