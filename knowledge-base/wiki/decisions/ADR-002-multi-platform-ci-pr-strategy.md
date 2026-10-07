---
okf_version: "1.0"
node_type: decision
id: "ADR-002-multi-platform-ci-pr-strategy"
status: active
domain: "ci-cd-governance"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# ADR-002: Estrategia Agnóstica Multi-Plataforma para CI/CD y Pull Requests

## Contexto y Problema
En entornos enterprise coexisten diferentes plataformas de control de versiones y CI/CD según el tipo de cliente, criticidad o restricciones de red: Bitbucket Server (On-Premise), Bitbucket Cloud, Azure DevOps y GitHub. Acoplar la suite de calidad a una plataforma propietaria (ej. GitHub Actions) fragmentaría la adopción del método de 3 capas.

## Decisión
Se adopta el patrón **Thin CI Wrapper / Local Verification First**:
1. **Comando Canónico Agnóstico:** La lógica de compuertas de calidad reside en `scripts/verify-all.py`, ejecutable con Python estándar 3.10+ en cualquier sistema operativo sin dependencias externas.
2. **Plantillas Desacopladas (`templates/ci/`):** Se suministran conectores para Bitbucket Pipelines, Azure Pipelines, GitHub Actions y hooks `pre-push` de Git local.
3. **Pull Requests en Markdown Universal:** Las descripciones generadas por la Capa 4 de `k-orchestrator` se redactan en GitHub Flavored Markdown (GFM), compatible de forma nativa con los visualizadores de PR de Bitbucket, Azure Repos y GitHub.

## Consecuencias
- **Positivas:** Máxima portabilidad. Los desarrolladores pueden auditar el 100% de las compuertas de calidad en su estación local antes de emitir commits o push, independientemente de qué CI/CD emplee la organización.
- **Negativas / Costes:** Mantenimiento de plantillas de configuración para cada proveedor de CI.

## Enlaces Relacionados
- [[ADR-001-karpathy-3-layer-architecture]]
- [[environment-governor]]
- [[verifier-driven-development]]
- [[antigravity-skills-engine]]
- [[index]]
