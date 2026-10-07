---
okf_version: "1.0"
node_type: concept
id: "spec-driven-development"
status: active
domain: "layer-1-spec"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# [[spec-driven-development]]

## Resumen
La Capa 1 (Spec) de Karpathy detiene la generación prematura de código. Exige discriminar la intención antes de actuar (Feature, `/bugfix`, `/chore`, `/iterate` o Migración) y descompone requerimientos complejos mediante la regla dura de máximo 6 Criterios de Aceptación (6-AC Rule).

## Principios Clave y Contratos
- **Clasificación de Intención:** Enrutamiento explícito entre características nuevas, triaje forense de incidentes y mantenimiento rutinario.
- **Regla de los 6 ACs (Epic Detection):** Ninguna especificación puede superar los 6 Criterios de Aceptación. Si la densidad funcional es mayor, se fuerza la descomposición secuencial en roadmap de Epics.
- **Shift-Left Security:** Incorporación obligatoria de Modelado de Amenazas OWASP y criterios de seguridad (`AC-Sec`).
- **Gate de Aprobación Humana:** El agente se detiene de forma obligatoria tras redactar la especificación para confirmación humana explícita.

## Relaciones Arquitectónicas
- Gobernado por: [[ADR-001-karpathy-3-layer-architecture]]
- Conecta con: [[verifier-driven-development]], [[environment-governor]]
- Índice global: [[index]]
