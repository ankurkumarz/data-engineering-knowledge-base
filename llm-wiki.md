# LLM Wiki

This repository uses an LLM-maintained wiki rather than treating uploaded documents as a passive retrieval corpus. Each source is read once, mapped into a stable data-engineering taxonomy, reconciled with existing knowledge, cited, and cross-linked. Later questions can start from that maintained synthesis instead of reconstructing it from unrelated chunks.

The operating model has three layers:

- `raw/` is the immutable evidence layer.
- `docs/` is the evolving synthesis layer.
- `AGENTS.md` is the schema and maintenance contract.

The workflow supports ingestion, query, and lint operations. Ingestion compounds the wiki; queries use it; linting keeps it accurate and navigable. Hash-based state tracks which local sources have been integrated without confusing file discovery with semantic indexing.
