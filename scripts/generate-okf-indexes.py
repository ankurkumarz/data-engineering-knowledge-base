#!/usr/bin/env python3
"""Generate reserved section index.md files from concept frontmatter."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
RESERVED = {"index.md", "log.md", "ingest-log.md", "graph.md"}
SKIP_DIRS = {"assets"}
SECTIONS = {
    "Foundations", "Architecture", "DataModeling", "StorageFormats",
    "Lakehouse", "DataWarehousing", "DataIntegration", "Orchestration",
    "BatchProcessing", "StreamProcessing", "DataPlatforms",
    "AnalyticsServing", "DataQuality", "MetadataCatalog",
    "GovernanceSecurity", "Observability", "DataOps", "PerformanceCost",
    "DesignPatterns", "ReferenceArchitecture", "BestPractices", "Standards",
    "Research", "Benchmarks", "DevAgents", "LearningResources",
}
HEADINGS = {
    "DataModeling": "Data Modeling",
    "StorageFormats": "Storage and Table Formats",
    "DataWarehousing": "Data Warehousing and OLAP",
    "DataIntegration": "Data Integration and Ingestion",
    "BatchProcessing": "Batch Processing",
    "StreamProcessing": "Stream Processing",
    "DataPlatforms": "Data Platforms",
    "AnalyticsServing": "Analytics and Serving",
    "DataQuality": "Data Quality and Contracts",
    "MetadataCatalog": "Metadata, Catalog, and Lineage",
    "GovernanceSecurity": "Governance, Privacy, and Security",
    "DataOps": "DataOps and Delivery",
    "PerformanceCost": "Performance and Cost",
    "DesignPatterns": "Design Patterns",
    "ReferenceArchitecture": "Reference Architectures",
    "BestPractices": "Production Best Practices",
    "DevAgents": "AI for Data Engineering",
    "LearningResources": "Learning Resources",
    "NewsletterBlogs": "Newsletters and Blogs",
}


def split_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        return yaml.safe_load(match.group(1)) or {}, text[match.end():]
    except yaml.YAMLError:
        return {}, text


def info(path: Path) -> tuple[str, str]:
    metadata, body = split_frontmatter(path)
    h1 = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    title = metadata.get("title") or (h1.group(1).strip() if h1 else path.stem)
    description = metadata.get("description") or "Data engineering reference."
    return str(title), str(description)


def render(directory: Path) -> str:
    heading = HEADINGS.get(directory.name, re.sub(r"(?<!^)(?=[A-Z])", " ", directory.name))
    pages = [
        path
        for path in sorted(directory.glob("*.md"))
        if path.name.lower() not in RESERVED
    ]
    lines = [f"# {heading}", ""]
    if pages:
        lines.extend(["## Pages", ""])
        for page in pages:
            title, description = info(page)
            lines.append(f"- [{title}]({page.name}) — {description}")
        lines.append("")
    else:
        lines.extend([
            "This section is ready for source-driven pages. Add material to `raw/` and run the ingest workflow described in `AGENTS.md`.",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    count = 0
    for directory in sorted(DOCS.iterdir()):
        if (
            not directory.is_dir()
            or directory.name.startswith(".")
            or directory.name in SKIP_DIRS
            or directory.name not in SECTIONS
        ):
            continue
        target = directory / "index.md"
        if not dry_run:
            target.write_text(render(directory), encoding="utf-8")
        print(f"{'WOULD WRITE' if dry_run else 'WROTE'}: {target.relative_to(REPO)}")
        count += 1
    print(f"\nSection indexes: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
