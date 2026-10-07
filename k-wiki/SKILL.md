---
name: k-wiki
description: Implements Open Knowledge Format (OKF) on top of Andrej Karpathy's llm-wiki.md architecture. Manages an incremental, typed, and interconnected Markdown knowledge graph with Ingest, Query, Lint, and Deprecate operations. Enforces high signal-to-noise selective ingestion, tracks node lifecycles (active, draft, deprecated, superseded), and compiles structural ADRs and gotchas. Use when cataloging documentation, compiling research, recording architectural decision records (ADRs), deprecating obsolete architectural patterns, reconciling contradictory notes, or checking knowledge graphs for broken links.
---

# LLM Wiki Engine (Open Knowledge Format - OKF Standard)

## Core Philosophy
*"Compile once, compound continuously. Obsidian is the IDE; the LLM is the compiler; the wiki is the codebase."*
Replace ephemeral RAG with an evolving, interconnected Markdown knowledge repository governed by **Open Knowledge Format (OKF)** typed frontmatter.

## Architecture & OKF Topology
```text
knowledge-base/
├── SCHEMA.md          # OKF taxonomy, frontmatter schema rules, and tag conventions
├── raw/               # Immutable sources (articles, PDFs, transcripts, PRs)
└── wiki/              # Agent-compiled markdown repository (OKF compliant)
    ├── index.md       # High-level table of contents and concept map
    ├── log.md         # Append-only chronological ledger of updates
    ├── concepts/      # Domain concepts with OKF frontmatter & [[wikilinks]]
    ├── entities/      # Components, tools, libraries with typed schemas
    └── decisions/     # Architectural Decision Records (ADRs) with lifecycle states
```

## OKF Lifecycle States
Every node in `wiki/` must declare an `okf_version: "1.0"` block with an explicit `status`:
- `active`: Currently approved, active pattern in the codebase.
- `draft`: Proposed concept under review.
- `deprecated`: Obsolete pattern marked for removal; must link to its replacement.
- `superseded`: Replaced directly by a newer ADR (`superseded_by: [[ADR-XXX]]`).

## Selective Ingestion Policy (Preventing Wiki Bloat)
**Do NOT** ingest mundane implementation details (minor bugfixes, syntax tweaks).
Only compile new permanent pages into `wiki/` when the change involves:
1. **Architectural Decision Records (ADRs):** A structural choice between competing libraries/patterns.
2. **Public Contract Changes:** Breaking modifications or new core domain interfaces.
3. **Hard-Earned Discoveries / Gotchas:** Non-trivial bugs, platform constraints (e.g. governor limits), or technical debt.
*For routine feature completions:* Only append a one-line summary to `wiki/log.md`.

## Primary Operations

### 1. Ingest (`/wiki-ingest [file]`)
- Read new source in `raw/` or inspect newly completed feature spec.
- Evaluate against the Selective Ingestion Policy.
- If qualifying as an ADR or Concept:
  - Create note in `wiki/decisions/` or `wiki/concepts/` using `templates/concept-page.template.md`.
  - Format typed OKF YAML frontmatter.
  - Enrich existing notes using `[[wikilinks]]`.
  - **Reconcile Contradictions:** If source conflicts with an existing note, insert a `### Discrepancies & Divergences` section or execute a formal deprecation.
- Append log record to `wiki/log.md`. Refresh `wiki/index.md`.

### 2. Deprecate & Retire (`/wiki-deprecate [node] --replaced-by [new-node]`)
- When an architectural pivot occurs (e.g., after an Expand & Contract migration):
  - Change target node status from `status: active` to `status: superseded` (or `deprecated`).
  - Add metadata field: `superseded_by: "[[new-node]]"`.
  - In the target note body, insert a prominent deprecation notice warning agents not to use this pattern.
  - Log the deprecation in `wiki/log.md`.

### 3. Query (`/wiki-query [question]`)
- Consult `wiki/index.md` and follow conceptual wikilinks.
- Read typed frontmatter (`status`, `governed_by`, `dependencies`) to prune inactive patterns instantly.
- Synthesize an answer citing active notes and ADRs.
- Feed this context directly into Layer 3 (Environment Check) before starting new specifications.

### 4. Lint (`/wiki-lint`)
- Scan all markdown files in `wiki/`:
  - Broken links (`[[note]]` pointing to missing files).
  - Orphan pages (no inbound links).
  - Schema validity: check that OKF YAML frontmatter is present and valid against `SCHEMA.md`.