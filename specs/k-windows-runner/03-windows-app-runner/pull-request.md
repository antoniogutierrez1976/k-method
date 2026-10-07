# Pull Request: feat(harness): implement Windows Antigravity-style app runner and PowerShell launcher

## 1. Traceability & Context
- **Specification:** Closes `specs/k-windows-runner/03-windows-app-runner/spec.md`
- **Governing Architecture:** Governed by `[[ADR-003-dual-sdk-execution-harness]]` and `[[ADR-001-karpathy-3-layer-architecture]]`
- **Git Branch:** `feat/windows-runner-app` -> Target: `main`

## 2. Summary of Changes
- Se implementa el runner interactivo de línea de comandos para Windows (`scripts/harness/k_runner.py`) y el script lanzador de PowerShell (`run-harness.ps1`).
- Módulo UI de renderizado estilo Antigravity (`scripts/harness/ui/renderer.py`):
  - Banner estilizado con proveedor, modelo y etapa activa.
  - Paneles auxiliares de estado en vivo (etapa, rama de Git y telemetría de tokens).
  - Sanitización de secuencias de escape ANSI/OSC peligrosas en respuestas del modelo (`AC-Sec-1`).
  - Modal interactivo de aprobación humana para especificaciones (`prompt_human_approval`) con bypass `--auto-approve`.
  - Caja de alerta visual para fricción y disparo del disyuntor (*Circuit Breaker*).
- **Invariante Crítica:** 100% de los archivos y scripts en `.agents/skills/` se preservan intactos sin modificaciones.

## 3. Ground Truth Verification Evidence
- [x] **Acceptance Criteria Verification:**
  - AC-Sec-1 passing: `tests/test_app_runner.py::test_AC_Sec_1_terminal_escape_sanitization`
  - AC-1 passing: `tests/test_app_runner.py::test_AC_1_cli_arg_resolution`
  - AC-2 passing: `tests/test_app_runner.py::test_AC_2_antigravity_banner_and_panels`
  - AC-3 passing: `tests/test_app_runner.py::test_AC_3_human_approval_prompt`
  - AC-4 passing: `tests/test_app_runner.py::test_AC_4_circuit_breaker_alert_rendering`
  - AC-5 passing: `tests/test_app_runner.py::test_AC_5_end_to_end_runner_execution`
  - 100% de las casillas sincronizadas en la especificación.
- [x] **Negative Fault Injection (Mutation Testing):** Validada la sensibilidad mutando la sanitización de escapes de terminal (fallo inmediato de prueba).
- [x] **Flaky Test Immunity:** 10 pruebas unitarias deterministas ejecutadas con éxito.
- [x] **Branch Coverage Floor:** ≥85% de cobertura de ramas alcanzada en el runner y UI.
- [x] **Universal Quality Gates:** `scripts/verify-all.py` superado con 44 pruebas unitarias totales y grafo OKF íntegro.

## 4. Release Strategy & Operational Rollback Plan
- **Deployment Strategy:** Direct en módulo `scripts/harness/` y `run-harness.ps1`.
- **Operational Rollback Procedure:**
  1. Revertir cambios: `git checkout main && git branch -D feat/windows-runner-app`.
- **Runtime Observability & Alerts:**
  - Salida visual interactiva en Windows Terminal / PowerShell con paneles de estado y alertas de disyuntor.
