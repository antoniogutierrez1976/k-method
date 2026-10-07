---
okf_version: "1.0"
node_type: concept
id: "open-knowledge-format"
status: active
domain: "knowledge-management"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# [[open-knowledge-format]]

## Resumen
Open Knowledge Format (OKF) es el protocolo de grafo de conocimiento estructurado en Markdown basado en la arquitectura `llm-wiki.md` de Andrej Karpathy. Implementa nodos tipados, frontmatter YAML estandarizado, compilación determinista del índice y control del ciclo de vida de los conceptos.

## Principios Clave y Contratos
- **Nodos Tipados:** Distinción explícita entre Conceptos (`wiki/concepts/`), Entidades (`wiki/entities/`) y Decisiones Arquitectónicas (`wiki/decisions/`).
- **Estados de Ciclo de Vida:** Cada nodo declara su estado (`active`, `draft`, `deprecated`, `superseded`) garantizando la recolección de basura del conocimiento obsoleto.
- **Ingesta Selectiva (Alta Relación Señal/Ruido):** Sólo se registran decisiones estructurales, interfaces públicas y compromisos técnicos estables, ignorando cambios efímeros.
- **Enlaces Bidireccionales (Wikilinks):** Sintaxis obligatoria con corchetes dobles auditada sin enlaces rotos por el compilador determinista en [[antigravity-skills-engine]].

## Relaciones Arquitectónicas
- Gobernado por: [[ADR-001-karpathy-3-layer-architecture]]
- Conecta con: [[environment-governor]], [[antigravity-skills-engine]]
- Índice global: [[index]]
