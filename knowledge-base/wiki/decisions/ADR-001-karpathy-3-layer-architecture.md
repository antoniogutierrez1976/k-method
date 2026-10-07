---
okf_version: "1.0"
node_type: decision
id: "ADR-001-karpathy-3-layer-architecture"
status: active
domain: "architecture"
governed_by: []
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# ADR-001: Adopción de la Arquitectura de 3 Capas de Karpathy y OKF

## Contexto y Problema
En el desarrollo asistido por agentes LLM, delegar directamente la implementación sin especificación rigurosa ni validación automatizada conduce a alucinaciones de interfaz, sobreescritura destructiva de código, regresiones silenciosas y degradación del contexto.

## Decisión
Se adopta formalmente el estándar de **3 Capas de Andrej Karpathy** complementado con el grafo de conocimiento **OKF (Open Knowledge Format)**:
1. **Capa 1: Spec** ([`spec-driven-development`](file:///d:/dev/k-method/knowledge-base/wiki/concepts/spec-driven-development.md)) - Ninguna línea de código de producción se redacta sin una especificación previa aprobada (máximo 6 ACs).
2. **Capa 2: Verifier** ([`verifier-driven-development`](file:///d:/dev/k-method/knowledge-base/wiki/concepts/verifier-driven-development.md)) - Ciclo Red-Green-Refactor estricto, inmunidad estocástica 3x, inyección de fallos y cobertura ≥85%.
3. **Capa 3: Environment** ([`environment-governor`](file:///d:/dev/k-method/knowledge-base/wiki/concepts/environment-governor.md)) - Constitución `AGENTS.md`, aislamiento Git, Stash Shield y aborto atómico `/task-abort`.
4. **Grafo de Conocimiento** ([`open-knowledge-format`](file:///d:/dev/k-method/knowledge-base/wiki/concepts/open-knowledge-format.md)) - Memoria tipada incremental gobernada por el compilador determinista en [[antigravity-skills-engine]].

## Consecuencias
- **Positivas:** Trazabilidad bidireccional entre requerimientos, tests y decisiones. Protección contra alucinaciones y regresiones en entornos agentic.
- **Negativas / Costes:** Mayor fricción inicial requerida antes de generar código; los cambios deben modelarse y verificarse formalmente.

## Enlaces Relacionados
- [[spec-driven-development]]
- [[verifier-driven-development]]
- [[environment-governor]]
- [[open-knowledge-format]]
- [[index]]
