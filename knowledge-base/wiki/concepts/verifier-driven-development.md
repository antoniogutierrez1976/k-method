---
okf_version: "1.0"
node_type: concept
id: "verifier-driven-development"
status: active
domain: "layer-2-verifier"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-07"
---

# [[verifier-driven-development]]

## Resumen
La Capa 2 (Verifier) de Karpathy aplica la metodología Test-Driven Development (TDD) estricta e industrializada para agentes autónomos. Protege contra tests vacuos o tautológicos, elimina la variabilidad estocástica y garantiza la robustez mediante disyuntores de circuito (deadlock circuit breakers).

## Principios Clave y Contratos
- **Ciclo Red-Green-Refactor:** El código se escribe únicamente para satisfacer un test fallido existente correspondiente a un AC concreto.
- **Inmunidad contra Tests Inestables (3x Run):** Ejecución estocástica consecutiva 3 de 3 en tests de concurrencia y asíncronos.
- **Inyección Negativa de Fallos (Mutation Testing):** Mutación deliberada de la lógica de negocio para confirmar la sensibilidad del test.
- **Suelo de Cobertura de Ramas (≥85%):** Puerta de calidad obligatoria en archivos modificados antes de release.
- **Deadlock Circuit Breaker:** Si ocurren 2 fallos idénticos consecutivos, el agente detiene ediciones, vuelca `git diff` y escala un informe de fricción técnica.

## Relaciones Arquitectónicas
- Gobernado por: [[ADR-001-karpathy-3-layer-architecture]]
- Conecta con: [[spec-driven-development]], [[environment-governor]]
- Índice global: [[index]]
