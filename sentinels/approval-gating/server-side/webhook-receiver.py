#!/usr/bin/env python3
# ABOUTME: Lambda-style GitHub webhook receiver that verifies HMAC signature and ships bypass events to SIEM.
# ABOUTME: HMAC verification is the load-bearing line; without it any actor can spoof events into the SIEM.

import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request


SIEM_URL = os.environ.get("SIEM_URL", "https://siem.example.com:9200/agent-sentinel-bp/_doc")
SIEM_TOKEN = os.environ["SIEM_TOKEN"]            # required
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"].encode()  # required


def verify_signature(headers: dict, body: bytes) -> bool:
    """GitHub computes HMAC-SHA256 over the body using the configured secret."""
    sig = headers.get("X-Hub-Signature-256") or headers.get("x-hub-signature-256")
    if not sig:
        return False
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def ship_alert(event_type: str, payload: dict) -> None:
    body = json.dumps(
        {
            "event": event_type,
            "data": payload,
            "ts": payload.get("created_at") or payload.get("pushed_at"),
        }
    ).encode()
    req = urllib.request.Request(
        SIEM_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {SIEM_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except urllib.error.URLError as exc:
        # Fail-open on SIEM unavailability is less bad than dropping the event;
        # log to stderr/CloudWatch so operations sees the gap.
        print(f"webhook-receiver: SIEM unreachable: {exc}", flush=True)


def handler(event: dict, _context=None) -> dict:
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    body_str = event.get("body", "") or ""
    body_bytes = body_str.encode() if isinstance(body_str, str) else body_str

    if not verify_signature(headers, body_bytes):
        return {"statusCode": 401, "body": "invalid signature"}

    delivery_id = headers.get("x-github-delivery", "unknown")
    event_name = headers.get("x-github-event", "unknown")

    try:
        payload = json.loads(body_str) if body_str else {}
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "malformed JSON"}

    # branch_protection_rule events: deleted, edited.
    if event_name == "branch_protection_rule":
        action = payload.get("action")
        if action in {"deleted", "edited"}:
            ship_alert(f"branch_protection_{action}", {**payload, "delivery_id": delivery_id})

    # push events: forced is True for `git push -f`. `--force-with-lease`
    # also surfaces as forced=true on the API; both are bypass attempts on
    # protected branches.
    if event_name == "push":
        if payload.get("forced") and payload.get("ref", "").startswith("refs/heads/"):
            ship_alert("force_push", {**payload, "delivery_id": delivery_id})
        # Branch deletion on a protected branch is also worth surfacing.
        if payload.get("deleted") and payload.get("ref") in {"refs/heads/main", "refs/heads/master"}:
            ship_alert("protected_branch_delete", {**payload, "delivery_id": delivery_id})

    return {"statusCode": 200, "body": "ok"}
