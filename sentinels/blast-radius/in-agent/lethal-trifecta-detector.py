#!/usr/bin/env python3
# ABOUTME: Reference implementation of Simon Willison's lethal-trifecta detector at the wrapper layer.
# ABOUTME: Flags when private data, untrusted content, and an external-communication tool appear in the same context window.

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Class(str, Enum):
    """The three input classes whose simultaneous presence constitutes the trifecta."""
    PRIVATE = "private"
    UNTRUSTED = "untrusted"
    EXTERNAL_COMMS = "external-communication"


@dataclass(frozen=True)
class TaggedInput:
    """An item already tagged at provenance time. Tagging by content is the wrong layer."""
    classes: frozenset[Class]
    source: str
    content_preview: str


@dataclass
class TrifectaState:
    """Tracks which classes are present in the current context window."""
    seen_classes: set[Class]
    items_by_class: dict[Class, list[TaggedInput]]

    @classmethod
    def empty(cls) -> "TrifectaState":
        return cls(seen_classes=set(), items_by_class={c: [] for c in Class})

    def admit(self, item: TaggedInput) -> None:
        for c in item.classes:
            self.seen_classes.add(c)
            self.items_by_class[c].append(item)

    def is_trifecta(self) -> bool:
        return self.seen_classes == set(Class)

    def explain(self) -> dict:
        return {
            "trifecta": self.is_trifecta(),
            "classes_present": sorted(c.value for c in self.seen_classes),
            "sources": {c.value: [i.source for i in items] for c, items in self.items_by_class.items() if items},
        }


def evaluate(items: Iterable[TaggedInput]) -> dict:
    """Walk a sequence of context-window items and return the trifecta state."""
    state = TrifectaState.empty()
    for item in items:
        state.admit(item)
    return state.explain()


# ---------- self-tests ----------

def _self_test_positive() -> int:
    items = [
        TaggedInput(frozenset({Class.PRIVATE}), source="vault://customer-pii", content_preview="<redacted>"),
        TaggedInput(frozenset({Class.UNTRUSTED}), source="github://issues/comment", content_preview="hello there..."),
        TaggedInput(frozenset({Class.EXTERNAL_COMMS}), source="tool://send_email", content_preview="<tool>"),
    ]
    result = evaluate(items)
    print("TRIFECTA DETECTED" if result["trifecta"] else "TRIFECTA NOT DETECTED")
    print(json.dumps(result, indent=2))
    return 0 if result["trifecta"] else 1


def _self_test_negative() -> int:
    items = [
        TaggedInput(frozenset({Class.PRIVATE}), source="vault://customer-pii", content_preview="<redacted>"),
        TaggedInput(frozenset({Class.UNTRUSTED}), source="github://issues/comment", content_preview="hello there..."),
    ]
    result = evaluate(items)
    print("TRIFECTA DETECTED" if result["trifecta"] else "TRIFECTA NOT DETECTED")
    print(json.dumps(result, indent=2))
    return 0 if not result["trifecta"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", action="store_true", help="Run positive self-test (trifecta should detect).")
    parser.add_argument("--test-negative", action="store_true", help="Run negative self-test (trifecta should not detect).")
    parser.add_argument("--from-stdin", action="store_true", help="Read JSON list of TaggedInput dicts from stdin.")
    args = parser.parse_args()

    if args.test:
        return _self_test_positive()
    if args.test_negative:
        return _self_test_negative()
    if args.from_stdin:
        raw = json.loads(sys.stdin.read())
        items = [
            TaggedInput(
                classes=frozenset(Class(c) for c in entry["classes"]),
                source=entry["source"],
                content_preview=entry.get("content_preview", ""),
            )
            for entry in raw
        ]
        result = evaluate(items)
        print(json.dumps(result, indent=2))
        return 0 if not result["trifecta"] else 2

    parser.print_help()
    return 64


if __name__ == "__main__":
    sys.exit(main())
