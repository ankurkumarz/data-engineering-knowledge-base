#!/usr/bin/env python3
"""Verify OKF frontmatter and internal wiki invariants."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

DOCS = Path(__file__).resolve().parent.parent / "docs"
RESERVED = {"index.md", "log.md", "ingest-log.md", "graph.md"}
APPROVED_TYPES = {
    "Architecture",
    "Benchmark",
    "Concept",
    "Design Pattern",
    "Platform",
    "Playbook",
    "Reference",
    "Research",
    "Standard",
    "Tool",
}
REQUIRED = {"type", "title", "description", "tags", "timestamp"}


def frontmatter(text: str) -> tuple[dict, str] | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1)) or {}, text[match.end():]


def main() -> int:
    errors: list[str] = []
    checked = 0
    for path in sorted(DOCS.rglob("*.md")):
        relative = path.relative_to(DOCS)
        text = path.read_text(encoding="utf-8")
        parsed = frontmatter(text)
        if path.name.lower() in RESERVED:
            if parsed and not (relative == Path("index.md") and set(parsed[0]) == {"okf_version"}):
                errors.append(f"RESERVED FRONTMATTER: {relative}")
            continue
        if not parsed:
            errors.append(f"MISSING FRONTMATTER: {relative}")
            continue
        metadata, body = parsed
        missing = sorted(key for key in REQUIRED if not metadata.get(key))
        if missing:
            errors.append(f"MISSING FIELDS {', '.join(missing)}: {relative}")
        if metadata.get("type") not in APPROVED_TYPES:
            errors.append(f"UNKNOWN TYPE {metadata.get('type')!r}: {relative}")
        h1 = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
        if not h1:
            errors.append(f"MISSING H1: {relative}")
        elif metadata.get("title") != h1.group(1).strip():
            errors.append(f"TITLE/H1 MISMATCH: {relative}")
        checked += 1

    print(f"Concept pages checked: {checked}")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print(f"  {error}")
    if not errors:
        print("OKF validation passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
