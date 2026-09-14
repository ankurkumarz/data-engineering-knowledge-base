#!/usr/bin/env python3
"""Report raw sources as pending, changed, processed, or missing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "raw"
STATE_PATH = REPO / ".ingest-state.json"
IGNORED_NAMES = {"README.md", ".DS_Store", ".gitkeep"}
IGNORED_SUFFIXES = {".swp", ".swo", ".tmp", ".part"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def source_files() -> list[Path]:
    if not RAW.exists():
        return []
    return sorted(
        path
        for path in RAW.rglob("*")
        if path.is_file()
        and not any(part.startswith(".") for part in path.relative_to(RAW).parts)
        and path.name not in IGNORED_NAMES
        and path.suffix.lower() not in IGNORED_SUFFIXES
    )


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"version": 1, "sources": {}}
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("sources"), dict):
        raise SystemExit(f"Unsupported or malformed state file: {STATE_PATH}")
    return data


def main() -> int:
    state = load_state()["sources"]
    current: dict[str, str] = {}
    counts = {"pending": 0, "changed": 0, "processed": 0, "missing": 0}

    for path in source_files():
        key = path.relative_to(REPO).as_posix()
        checksum = digest(path)
        current[key] = checksum
        record = state.get(key)
        if record is None:
            status = "pending"
        elif record.get("sha256") != checksum:
            status = "changed"
        else:
            status = "processed"
        counts[status] += 1
        print(f"{status:9} {key}")

    for key in sorted(set(state) - set(current)):
        counts["missing"] += 1
        print(f"{'missing':9} {key}")

    print(
        "\nSummary: "
        + ", ".join(f"{name}={value}" for name, value in counts.items())
    )
    return 1 if counts["pending"] or counts["changed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
