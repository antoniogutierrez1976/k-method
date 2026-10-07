---
okf_version: "1.0"
node_type: entity
id: "antigravity-skills-engine"
status: active
domain: "tooling-runtime"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# [[antigravity-skills-engine]]

## Resumen
Motor de ejecución de habilidades para agentes autónomos desarrollado bajo las especificaciones de Google Antigravity y Anthropic Agent Skills. Opera en `.agents/skills/` mediante paquetes modulares auto-contenidos dotados de `SKILL.md`, scripts locales y plantillas.

## Principios Clave y Contratos
- **Auto-Contención:** Cada skill (`k-orchestrator`, `k-spec`, `k-verifier`, `k-environment`, `k-wiki`) empaqueta sus propias referencias, dependencias de script y plantillas sin contaminar el espacio global.
- **Invariante DRY:** Prohibición de duplicación de scripts auxiliares o esquemas entre diferentes carpetas de skills.
- **Herramientas Estándar:** Ejecución mediante CLI estándar y compatibilidad nativa multiplataforma (Windows PowerShell y POSIX Bash).

## Relaciones Arquitectónicas
- Gobernado por: [[ADR-001-karpathy-3-layer-architecture]]
- Conecta con: [[open-knowledge-format]], [[environment-governor]]
- Índice global: [[index]]
