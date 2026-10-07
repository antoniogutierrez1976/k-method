---
okf_version: "1.0"
node_type: decision
id: "ADR-004-antigravity-gui-and-embedded-skills"
status: active
domain: "gui-architecture-and-embedded-skills"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]", "[[ADR-003-dual-sdk-execution-harness]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# ADR-004: Aplicación Gráfica Antigravity 2.0 y Patrón de Inyección de Skills Embebidas

## Contexto y Problema
La interfaz de línea de comandos (CLI) de `k-windows-runner` requiere ejecución directa en terminal de PowerShell, lo que dificulta la inspección interactiva y simultánea de artefactos (`spec.md`), diffs de Git con coloreado de sintaxis, trazas de TDD en vivo y paradas de aprobación humana.
Asimismo, existe la necesidad estratégica de **proteger la propiedad intelectual y privatizar el uso de la metodología Karpathy v17**: si las directivas de las skills residen únicamente como archivos markdown descubiertos en el repositorio (`.agents/skills/`), cualquier usuario o agente puede alterarlas, omitir sus compuertas de calidad o copiarlas a otros entornos sin utilizar el arnés de gobernanza.

## Decisión
1. **Aplicación Gráfica basada en Web Moderna (Estilo Antigravity 2.0):**
   Se adopta una arquitectura de escritorio ligera con backend ASGI local (FastAPI + Starlette WebSockets) y frontend reactivo Dark-Mode con la disposición de tres columnas de Antigravity 2.0:
   - *Sidebar Izquierda:* Gestión de proyectos, selector de proveedor/modelo, y catálogo de skills activas.
   - *Canvas Central:* Flujo de conversación, streaming de tokens y modal de aprobación humana.
   - *Panel Auxiliar Derecho:* Pestañas para *Artifacts*, *Files Changed / Diff*, *TDD Verifier Console*, y *OKF Graph*.
2. **Patrón de Inyección de Skills Embebidas (*Encapsulated Skills Pattern*):**
   Las directivas canónicas de Karpathy v17 (`k-orchestrator`, `k-spec`, `k-verifier`, `k-environment`, `k-wiki`) se encapsulan internamente en el backend de la aplicación (`scripts/harness/engine/embedded_skills.py`).
   El motor inyecta las directivas directamente en el `system_prompt` del LLM en cada fase, permitiendo operar en repositorios completamente limpios sin requerir la presencia de la carpeta `.agents/skills/` en el proyecto destino.

## Consecuencias
- **Positivas:**
  - Experiencia de usuario gráfica de nivel enterprise idéntica a Antigravity 2.0.
  - Blindaje y reserva del know-how metodológico contra manipulaciones accidentales o sabotaje de compuertas.
  - Portabilidad total: la app puede ejecutarse sobre cualquier repositorio sin necesidad de desplegar archivos de configuración en él.
- **Negativas / Costes:**
  - Mantenimiento del servidor ASGI local y del canal de comunicación WebSocket.

## Enlaces Relacionados
- [[ADR-001-karpathy-3-layer-architecture]]
- [[ADR-003-dual-sdk-execution-harness]]
- [[antigravity-skills-engine]]
- [[environment-governor]]
- [[verifier-driven-development]]
- [[index]]
