# Data Engineering Knowledge Base

A source-driven LLM wiki for modern data engineering: architecture, storage, integration, processing, platforms, quality, governance, observability, DataOps, and performance.

## Ingest a source

1. Place the original document in `raw/`.
2. Ask your coding agent to ingest pending raw sources. The complete workflow and data-engineering taxonomy are in `AGENTS.md`.
3. Check the queue with `python3 scripts/raw-status.py`.
4. Preview the site with `mkdocs serve`.

The agent integrates a source into existing topical pages where possible, creates pages only when needed, adds citations and cross-links, updates the logs, validates OKF frontmatter, and records the source hash in `.ingest-state.json`.

Raw sources remain immutable. The synthesized wiki lives under `docs/` and is published through MkDocs and Read the Docs.

## Visualize the OKF knowledge graph

Generate Google's interactive OKF bundle viewer locally:

```bash
.venv/bin/python3 scripts/okf-visualize.py
open html/okf-viz.html
```

The command first runs the repository's OKF validation, then renders only concept pages; reserved indexes and operational logs are excluded from the graph. On first use it caches the pinned [GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format) revision under `.okf-tools/`. Later runs can prohibit network access with `--offline`.

The generated HTML embeds the wiki content and is ignored by Git. Google's viewer loads Cytoscape.js and Marked from a CDN when opened, so its interactive rendering requires network access unless those browser dependencies are already cached.
