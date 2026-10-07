# Pull Request: feat(harness): implement deterministic SDLC engine with deadlock circuit breaker

## 1. Traceability & Context
- **Specification:** Closes `specs/k-windows-runner/02-sdlc-orchestration-engine/spec.md`
- **Governing Architecture:** Governed by `[[ADR-003-dual-sdk-execution-harness]]` and `[[ADR-001-karpathy-3-layer-architecture]]`
- **Git Branch:** `feat/windows-runner-sdlc-engine` -> Target: `main`

## 2. Summary of Changes
- Implementación de la máquina de estados Karpathy en Python (`scripts/harness/engine/state_machine.py`):
  - `KMethodEngine`: Coordina la fase de especificación (validación estricta de límite de 6 ACs y parada para aprobación humana), el bucle TDD (Red-Green) y el cierre de release.
  - `CircuitBreaker`: Disyuntor determinista que se activa tras 2 fallos consecutivos idénticos, aborta ediciones y emite informe de fricción con diff.
  - `StashShield`: Validación de árbol limpio con `git status --porcelain`, sanitización de ramas contra inyecciones y aislamiento en branches de tarea.
- **Invariante Crítica:** 100% de los archivos y scripts en `.agents/skills/` se preservan intactos sin modificaciones.

## 3. Ground Truth Verification Evidence
- [x] **Acceptance Criteria Verification:**
  - AC-Sec-1 passing: `tests/test_sdlc_engine.py::test_AC_Sec_1_no_shell_injection`
  - AC-1 passing: `tests/test_sdlc_engine.py::test_AC_1_spec_gate_and_ac_limit`
  - AC-2 passing: `tests/test_sdlc_engine.py::test_AC_2_stash_shield`
  - AC-3 passing: `tests/test_sdlc_engine.py::test_AC_3_tdd_cycle`
  - AC-4 passing: `tests/test_sdlc_engine.py::test_AC_4_circuit_breaker`
  - AC-5 passing: `tests/test_sdlc_engine.py::test_AC_5_okf_and_pr_generation`
  - 100% de las casillas sincronizadas en la especificación.
- [x] **Negative Fault Injection (Mutation Testing):** Validada la sensibilidad mutando el límite de 6 ACs en `execute_spec_stage` (fallo de test inmediato).
- [x] **Flaky Test Immunity:** 11 pruebas asíncronas deterministas ejecutadas con éxito.
- [x] **Branch Coverage Floor:** ≥85% de cobertura de ramas alcanzada en el motor y disyuntor.
- [x] **Universal Quality Gates:** `scripts/verify-all.py` superado con 34 pruebas unitarias totales y grafo OKF íntegro.

## 4. Release Strategy & Operational Rollback Plan
- **Deployment Strategy:** Direct en módulo `scripts/harness/engine/`.
- **Operational Rollback Procedure:**
  1. Revertir cambios: `git checkout main && git branch -D feat/windows-runner-sdlc-engine`.
- **Runtime Observability & Alerts:**
  - Registro de transiciones en `SDLCStage` y estados de disyuntor en `CircuitBreakerStatus`.
