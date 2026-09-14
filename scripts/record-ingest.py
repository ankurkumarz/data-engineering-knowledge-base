#!/usr/bin/env python3
"""Record a raw source after its semantic wiki ingest has completed."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW = (REPO / "raw").resolve()
STATE_PATH = REPO / ".ingest-state.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def repo_file(value: str) -> Path:
    path = (REPO / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("path must be inside the repository") from exc
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=repo_file)
    parser.add_argument("--pages", nargs="+", required=True, type=repo_file)
    args = parser.parse_args()

    source = args.source
    if not source.is_file():
        parser.error(f"source does not exist: {source}")
    try:
        source.relative_to(RAW)
    except ValueError:
        parser.error("source must be inside raw/")

    pages: list[str] = []
    for page in args.pages:
        if not page.is_file() or page.suffix.lower() != ".md":
            parser.error(f"wiki page does not exist or is not Markdown: {page}")
        try:
            page.relative_to((REPO / "docs").resolve())
        except ValueError:
            parser.error(f"wiki page must be inside docs/: {page}")
        pages.append(page.relative_to(REPO).as_posix())

    state = (
        json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if STATE_PATH.exists()
        else {"version": 1, "sources": {}}
    )
    state.setdefault("version", 1)
    state.setdefault("sources", {})
    key = source.relative_to(REPO).as_posix()
    for log_path in (REPO / "docs" / "log.md", REPO / "docs" / "ingest-log.md"):
        if not log_path.is_file() or key not in log_path.read_text(encoding="utf-8"):
            parser.error(f"{log_path.relative_to(REPO)} must mention {key} before it can be recorded")
    state["sources"][key] = {
        "sha256": digest(source),
        "processed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "pages": sorted(set(pages)),
    }
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"recorded {key} -> {len(set(pages))} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
