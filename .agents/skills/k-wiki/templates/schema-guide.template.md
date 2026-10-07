# Knowledge Base Schema & OKF Conventions (SCHEMA.md)

## OKF Standard Frontmatter
Every compiled note in `wiki/` must include:
```yaml
---
okf_version: "1.0"
node_type: concept | entity | decision
id: "[unique-kebab-id]"
status: active | draft | deprecated | superseded
domain: "[functional-domain]"
governed_by: ["[[ADR-XXX]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "YYYY-MM-DD"
---
```

## Note Naming Conventions
- Concept notes: `wiki/concepts/[kebab-case-concept].md`
- Entity notes: `wiki/entities/[kebab-case-tool-or-lib].md`
- Architectural decisions: `wiki/decisions/ADR-[000]-[name].md`

## Selective Ingestion Standard
- Maintain high signal-to-noise ratio: do not record transient code commits.
- Record structural patterns, public API interfaces, and technology trade-offs.

## Wikilink Protocol
- Always use standard double brackets: `[[concept-name]]`.
- Every concept page must link back to at least one parent hub or `index.md`.

## Raw Source Invariance
- Never edit files inside `raw/`. They represent permanent immutable truth.