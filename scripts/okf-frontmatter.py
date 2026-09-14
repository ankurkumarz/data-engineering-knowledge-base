#!/usr/bin/env python3
"""Add data-engineering OKF frontmatter to Markdown concept pages."""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
RESERVED = {"index.md", "log.md", "ingest-log.md", "graph.md"}

DIR_TYPES = {
    "Foundations": "Concept",
    "Architecture": "Architecture",
    "DataModeling": "Design Pattern",
    "StorageFormats": "Standard",
    "Lakehouse": "Architecture",
    "DataWarehousing": "Architecture",
    "DataIntegration": "Reference",
    "Orchestration": "Reference",
    "BatchProcessing": "Reference",
    "StreamProcessing": "Reference",
    "DataPlatforms": "Platform",
    "AnalyticsServing": "Reference",
    "DataQuality": "Playbook",
    "MetadataCatalog": "Reference",
    "GovernanceSecurity": "Playbook",
    "Observability": "Playbook",
    "DataOps": "Playbook",
    "PerformanceCost": "Playbook",
    "DesignPatterns": "Design Pattern",
    "ReferenceArchitecture": "Architecture",
    "BestPractices": "Playbook",
    "Standards": "Standard",
    "Research": "Research",
    "Benchmarks": "Benchmark",
    "DevAgents": "Tool",
    "LearningResources": "Reference",
    "NewsletterBlogs": "Reference",
    "Courses": "Reference",
}


def title_from(text: str, path: Path) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return " ".join(word.capitalize() for word in re.split(r"[-_]", path.stem))


def description_from(text: str, title: str) -> str:
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    paragraphs = re.split(r"\n\s*\n", body)
    for paragraph in paragraphs:
        value = " ".join(line.strip() for line in paragraph.splitlines()).strip()
        if not value or value.startswith(("#", "|", "!", "```", "<")):
            continue
        value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
        value = re.sub(r"[*_`]", "", value)
        if len(value) >= 20:
            return value[:197] + "..." if len(value) > 200 else value
    return f"A data engineering reference for {title}."


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def process(path: Path, dry_run: bool) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        return "SKIP"
    relative = path.relative_to(DOCS)
    section = relative.parts[0] if len(relative.parts) > 1 else ""
    title = title_from(text, path)
    description = description_from(text, title)
    doc_type = DIR_TYPES.get(section, "Reference")
    tag = re.sub(r"(?<!^)(?=[A-Z])", "-", section).lower() or "reference"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    frontmatter = (
        "---\n"
        f"type: {yaml_quote(doc_type)}\n"
        f"title: {yaml_quote(title)}\n"
        f"description: {yaml_quote(description)}\n"
        f"tags: [data-engineering, {tag}]\n"
        f"timestamp: {timestamp}\n"
        "---\n\n"
    )
    if not dry_run:
        path.write_text(frontmatter + text.lstrip(), encoding="utf-8")
    return "ADD"


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    added = 0
    for path in sorted(DOCS.rglob("*.md")):
        if path.name.lower() in RESERVED:
            continue
        status = process(path, dry_run)
        if status == "ADD":
            added += 1
            print(f"{'WOULD ADD' if dry_run else 'ADDED'}: {path.relative_to(DOCS)}")
    print(f"\nFrontmatter additions: {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
