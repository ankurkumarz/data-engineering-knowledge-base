# AGENTS.md — Data Engineering Knowledge Base

This file governs how AI agents maintain this repository. Read it before changing files.

## Purpose

This repository is a persistent, compounding data-engineering wiki rendered with MkDocs and published on Read the Docs. The goal is not merely to summarize documents in chat. Knowledge from every source must be integrated into durable, discoverable, cross-linked pages.

The repository has three layers:

- `raw/` contains immutable source material supplied by the user. Read it; never rewrite, rename, or delete it.
- `docs/` contains the synthesized wiki. Agents create and maintain this layer.
- `AGENTS.md`, `mkdocs.yml`, and `scripts/` define the schema, navigation, and checks.

## Repository layout

```text
docs/
├── Foundations/             # Core concepts, terminology, and principles
├── Architecture/            # System architecture and component selection
├── DataModeling/            # Logical, dimensional, Data Vault, semantic models
├── StorageFormats/          # Files, tables, catalogs, and interoperability
├── Lakehouse/               # Lakehouse architecture and implementations
├── DataWarehousing/         # Warehouses, OLAP, and analytical databases
├── DataIntegration/         # Ingestion, CDC, ELT/ETL, connectors, replication
├── Orchestration/           # Scheduling, dependencies, and workflow engines
├── BatchProcessing/         # Batch compute engines and patterns
├── StreamProcessing/        # Event streaming and real-time processing
├── DataPlatforms/           # Platform products and internal data platforms
├── AnalyticsServing/        # Query, BI, metrics, APIs, and data products
├── DataQuality/             # Testing, contracts, validation, and reliability
├── MetadataCatalog/         # Catalogs, lineage, discovery, and semantics
├── GovernanceSecurity/      # Ownership, privacy, access, compliance, governance
├── Observability/           # Pipeline and data observability
├── DataOps/                 # SDLC, CI/CD, environments, incident response
├── PerformanceCost/         # Performance engineering and FinOps
├── DesignPatterns/          # Reusable data-system patterns and anti-patterns
├── ReferenceArchitecture/   # End-to-end blueprints
├── BestPractices/           # Cross-cutting production guidance
├── Standards/               # Open specifications and interoperability standards
├── Research/                # Papers, surveys, and emerging techniques
├── Benchmarks/              # Workloads, datasets, and performance comparisons
├── DevAgents/               # AI-assisted data engineering tools and practices
├── LearningResources/       # Courses, books, newsletters, and learning paths
├── index.md                 # Root catalog and section map
├── log.md                   # Concise OKF change history, newest first
└── ingest-log.md            # Detailed append-only ingest audit trail

raw/                         # User-supplied source documents; immutable
.ingest-state.json           # Hash-based record of successfully ingested sources
scripts/raw-status.py        # Lists pending, changed, and processed sources
scripts/record-ingest.py     # Records a source only after wiki integration succeeds
scripts/generate-okf-indexes.py
scripts/okf-frontmatter.py
scripts/okf-verify.py
mkdocs.yml
```

Do not introduce a new top-level section without user approval. Extend the closest existing section and cross-link it when a source spans several topics.

## Section mapping

| Source topic | Primary section | Common secondary sections |
|---|---|---|
| Data engineering definitions, lifecycle, roles | `Foundations/` | `BestPractices/` |
| Distributed data-system design, medallion, mesh | `Architecture/` | `DesignPatterns/`, `ReferenceArchitecture/` |
| Dimensional modeling, Data Vault, semantic models | `DataModeling/` | `AnalyticsServing/`, `GovernanceSecurity/` |
| Parquet, Avro, Iceberg, Delta, Hudi, catalogs | `StorageFormats/` | `Lakehouse/`, `Standards/` |
| Lakehouse architecture or products | `Lakehouse/` | `StorageFormats/`, `DataPlatforms/` |
| Warehouses, OLAP engines, analytical databases | `DataWarehousing/` | `DataPlatforms/`, `PerformanceCost/` |
| ETL/ELT, CDC, replication, connectors, ingestion | `DataIntegration/` | `Orchestration/`, `DataQuality/` |
| DAGs, schedulers, workflow orchestration | `Orchestration/` | `DataOps/`, `Observability/` |
| Spark, MapReduce, batch pipelines | `BatchProcessing/` | `PerformanceCost/`, `DataPlatforms/` |
| Kafka, Flink, streaming semantics, event time | `StreamProcessing/` | `Architecture/`, `Observability/` |
| Cloud or internal data platforms | `DataPlatforms/` | relevant topical section |
| BI, metrics layers, data APIs, data products | `AnalyticsServing/` | `DataModeling/`, `GovernanceSecurity/` |
| Tests, data contracts, validation, SLOs | `DataQuality/` | `Observability/`, `BestPractices/` |
| Catalogs, lineage, metadata, discovery | `MetadataCatalog/` | `GovernanceSecurity/`, `Standards/` |
| Privacy, IAM, policy, compliance, ownership | `GovernanceSecurity/` | `BestPractices/` |
| Freshness, volume, schema, lineage monitoring | `Observability/` | `DataQuality/`, `DataOps/` |
| CI/CD, IaC, environments, deployment, incidents | `DataOps/` | `BestPractices/`, `Observability/` |
| Query tuning, capacity, efficiency, FinOps | `PerformanceCost/` | relevant engine or platform section |
| Reusable solution or anti-pattern | `DesignPatterns/` | `Architecture/` |
| End-to-end blueprint | `ReferenceArchitecture/` | every component's topical section |
| Cross-cutting production advice | `BestPractices/` | relevant topical section |
| Open standard or specification | `Standards/` | `StorageFormats/`, `MetadataCatalog/` |
| Academic paper or industry survey | `Research/` | the topic it informs |
| Benchmark, workload, or measured comparison | `Benchmarks/` | relevant engine or platform section |
| AI coding/data agents or LLM-assisted workflows | `DevAgents/` | `DataOps/`, `GovernanceSecurity/` |
| Course, book, newsletter, or curriculum | `LearningResources/` | relevant topic section |

Vendor-specific knowledge belongs in the appropriate topical page, not in a duplicate vendor silo. A platform overview may live in `DataPlatforms/`, but detailed guidance about its ingestion, storage, quality, or cost capabilities belongs in those topical sections with reciprocal links.

## Ingest workflow

Process one substantive source at a time unless the user explicitly requests a batch.

When the user asks to ingest, sync, process, or refresh `raw/` without naming a file, treat every `pending` or `changed` source reported by `raw-status.py` as in scope. Process them sequentially so each source is reconciled against the wiki state produced by the previous one.

### 1. Discover pending sources

Run:

```bash
.venv/bin/python3 scripts/raw-status.py
```

If `.venv/bin/python3` is unavailable, use `python3`. A source is pending when its path and SHA-256 hash are absent from `.ingest-state.json`. A changed hash is a new revision and must be re-ingested. Hidden files, temporary editor files, and `raw/README.md` are ignored.

Resolve sources in this order:

1. Local file in `raw/`.
2. A user-provided URL only when no local file was supplied.

Never mark a source processed before all updates and checks succeed.

### 2. Identify and extract

Determine source type, publication date/version, primary topic, secondary topics, and whether it adds, revises, or contradicts existing material. Extract only supported knowledge:

- concepts and precise definitions;
- architecture, data flow, state, and failure behavior;
- consistency, delivery, ordering, and processing guarantees;
- interfaces, formats, dependencies, and interoperability;
- operational practices, failure modes, and tradeoffs;
- security, governance, quality, observability, cost, and scale implications;
- benchmark methodology and results with hardware, dataset, date, and caveats;
- references and canonical URLs.

Distinguish source claims from synthesis. Do not convert vendor claims into neutral facts without attribution.

### 3. Map and integrate

Read `docs/index.md`, then search the relevant sections before writing. Update an existing page when one already covers the concept. Create a narrowly scoped page only when the concept has no suitable home.

For every updated page:

- integrate rather than append a disconnected summary;
- remove duplication and preserve still-valid content;
- record contradictions or changed evidence explicitly;
- add or update `See Also` links using relative paths ending in `.md`;
- make important links reciprocal where meaningful;
- cite the canonical source in `References`;
- maintain OKF frontmatter.

When a new page is created, add it to `mkdocs.yml`. If a source materially changes a section, update the concise section description in `docs/index.md`.

### 4. Log the ingest

Add an entry below today's heading in `docs/log.md` (newest dates first):

```markdown
## YYYY-MM-DD

* **Ingest**: [Source title] → Section, Section — canonical URL or `raw/path`
  * Created: `docs/Section/page.md`
  * Extended: `docs/OtherSection/page.md`
```

Use only **Ingest**, **Update**, **Creation**, or **Deprecation** as the leading verb.

Append a detailed record to `docs/ingest-log.md`:

```markdown
## [YYYY-MM-DD] ingest | Source title | sections touched: Section, Section

- Source: `raw/path` or canonical URL
- Source type: paper, documentation, whitepaper, article, book, dataset, presentation, or other
- Files modified: `docs/...`
- Knowledge added: concise factual summary
- Caveats: extraction limitations, disputed claims, or none
```

### 5. Regenerate, validate, and record

Run in order:

```bash
.venv/bin/python3 scripts/generate-okf-indexes.py
.venv/bin/python3 scripts/okf-verify.py
.venv/bin/python3 scripts/raw-status.py
mkdocs build --strict
```

After all checks pass, record each successfully processed local source:

```bash
.venv/bin/python3 scripts/record-ingest.py raw/path \
  --pages docs/Section/page.md docs/OtherSection/page.md
```

Then rerun `scripts/raw-status.py`; the source must report `processed`.

## Page format

Every non-reserved wiki page uses:

```markdown
---
type: <approved type>
title: <Page Title>
description: <One-sentence description>
tags: [data-engineering, <topic>]
timestamp: <YYYY-MM-DDT00:00:00Z>
---

# <Page Title>

## Overview

Explain what it is and why it matters.

## Key Concepts

Use prose, tables, or focused subsections appropriate to the topic.

## Tradeoffs and Failure Modes

Describe boundaries, operational consequences, and alternatives when supported.

## Best Practices

Prefer a table for three or more comparable practices.

## See Also

- [Related Page](../Section/file.md)

## References

- [Canonical title](URL) — source and relevance
```

Adapt headings to the material; do not create empty boilerplate sections.

## OKF compliance

Reserved filenames (`index.md`, `log.md`, `ingest-log.md`, and `graph.md`) do not receive concept frontmatter. The root `docs/index.md` may contain only `okf_version: "0.1"` frontmatter.

Approved `type` values are a closed list:

| Type | Use |
|---|---|
| `Architecture` | System structure or end-to-end blueprint |
| `Benchmark` | Measured workload, dataset, or comparison |
| `Concept` | Foundational definition or principle |
| `Design Pattern` | Reusable design solution or anti-pattern |
| `Platform` | Managed or integrated data platform |
| `Playbook` | Operational guidance or best practices |
| `Reference` | Survey, catalog, product overview, or learning resource |
| `Research` | Paper or research synthesis |
| `Standard` | Specification, protocol, or open format |
| `Tool` | Specific engineering tool or end-user product |

Directory defaults are encoded in `scripts/okf-frontmatter.py`. Do not invent a type. A new type requires user approval and matching updates to this file and `scripts/okf-verify.py`.

Every concept page must have `type`, `title`, `description`, `tags`, and `timestamp`; `title` must match its H1. Run `scripts/okf-verify.py` after changes.

## Quality rules

- Write in a neutral, technical, vendor-aware tone.
- Cite factual claims and retain version/date context for changing technologies.
- For benchmarks, preserve workload, data size, configuration, hardware, software version, concurrency, metric, and source caveats. Do not compare numbers from incompatible methodologies as though they were equivalent.
- For streaming systems, state delivery semantics, ordering scope, event-time/watermark behavior, replay model, and state/checkpoint behavior when known.
- For storage and table formats, separate file format, table format, catalog, and query-engine responsibilities.
- For architectures, describe control plane, data plane, metadata plane, security boundary, failure recovery, and operational ownership when the source supports them.
- Prefer tables when comparing three or more alternatives along common dimensions.
- Use relative links for wiki pages and canonical URLs for external references.
- Never manufacture missing details. Say that the current sources do not establish them.
- Never silently replace conflicting claims; preserve attribution and explain the conflict.

## Query workflow

When answering a data-engineering question, read `docs/index.md`, search the relevant pages, and cite those pages in the response. If a useful synthesis is missing, offer to file it into the wiki. A query is not an ingest unless the user asks to persist it.

## Lint workflow

When asked to lint the wiki, check for broken relative links, MkDocs nav targets that do not exist, orphan pages, missing `See Also` links, missing/invalid frontmatter, unprocessed raw sources, duplicate coverage, contradictions, and versioned claims older than 12 months. Fix mechanical issues in scope and report claims that require source review.

## Prohibitions

- Do not modify, rename, or delete anything in `raw/`.
- Do not mark a source ingested until its wiki changes, logs, and validations are complete.
- Do not delete existing wiki knowledge or navigation entries unless explicitly requested or demonstrably superseded; preserve useful history.
- Do not invent facts, citations, benchmark equivalence, or product capabilities.
- Do not commit, push, or publish without explicit user instruction.
