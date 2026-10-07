# Spec: Phase 3 - Windows Antigravity-Style App Runner

## 1. Goal & Context
- **Business Rationale:** Proveer una experiencia de usuario enriquecida y ergonómica en Windows (PowerShell / Windows Terminal) similar a Google Antigravity y GitHub Copilot CLI, permitiendo ejecutar el loop de `k-method` de forma interactiva con paneles auxiliares de estado en vivo, aprobación de especificaciones y alertas visuales del disyuntor.
- **User Story:** Como desarrollador en Windows, quiero ejecutar `python scripts/harness/k_runner.py` (o `./run-harness.ps1`) para orquestar mis tareas con GPT-6 Luna o Antigravity, viendo en tiempo real el progreso de cada etapa, el estado de Git y las paradas de aprobación con una estética visual clara.
- **Git Branch Target:** `feat/windows-runner-app`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar cualquier archivo, plantilla o script dentro de `.agents/skills/`. (Verificado: git status confirma cero modificaciones en .agents/skills/).
- [x] **OOS-2:** Introducir dependencias binarias pesadas de GUI (ej. Qt, Electron, WPF compilado); debe ejecutarse de forma nativa en la consola de Windows y PowerShell.
- [x] **OOS-3:** Almacenar claves o credenciales en archivos de configuración planos.

## 3. Technical Contract & Architecture
- **Data Models / Schemas:**
  ```python
  from dataclasses import dataclass
  from typing import Optional

  @dataclass
  class RunnerConfig:
      provider: str
      model: str
      task: str
      auto_approve: bool = False
      branch_name: Optional[str] = None
  ```
- **Endpoints / Signatures:**
  - `scripts/harness/ui/renderer.py`:
    - `sanitize_terminal_output(text: str) -> str`
    - `render_banner(provider: str, model: str, stage: str) -> str`
    - `render_auxiliary_panel(stage: str, branch: str, tokens: int) -> str`
    - `render_friction_alert(diff_report: str) -> str`
    - `prompt_human_approval(spec_content: str, auto_approve: bool = False) -> bool`
  - `scripts/harness/k_runner.py`:
    - `parse_args(args: List[str]) -> RunnerConfig`
    - `async def main()`
  - `run-harness.ps1`:
    - Launcher script de PowerShell para Windows.

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:**
  - Inyección de secuencias de escape ANSI maliciosas desde respuestas no confiables de modelos que pudieran alterar el buffer de la consola de Windows.
  - Ejecución accidental desatendida sin confirmación explícita.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** El renderizador debe sanitizar caracteres de control de terminal no seguros antes de imprimir texto proveniente del LLM en la consola. (Verified by: `tests/test_app_runner.py::test_AC_Sec_1_terminal_escape_sanitization`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Sanitización de caracteres de escape peligrosos en la consola. (Verified by: `tests/test_app_runner.py::test_AC_Sec_1_terminal_escape_sanitization`)
- [x] **AC-1 (Happy Path - CLI Parser):** `k_runner.py` resuelve `--provider`, `--model` y `--task` correctamente, con soporte para variables de entorno (`K_HARNESS_PROVIDER`). (Verified by: `tests/test_app_runner.py::test_AC_1_cli_arg_resolution`)
- [x] **AC-2 (Happy Path - Antigravity Banner & Panels):** El renderizador genera el banner estilizado y el panel auxiliar mostrando etapa, proveedor, modelo y rama. (Verified by: `tests/test_app_runner.py::test_AC_2_antigravity_banner_and_panels`)
- [x] **AC-3 (Happy Path - Human Approval Prompt):** `prompt_human_approval` devuelve True con respuestas afirmativas ('s', 'y', enter) y False con negativas, bypassando inmediatamente si `auto_approve=True`. (Verified by: `tests/test_app_runner.py::test_AC_3_human_approval_prompt`)
- [x] **AC-4 (Edge Case - Circuit Breaker Alert Rendering):** El renderizador formatea el informe del disyuntor en un cuadro de alerta visual delimitado. (Verified by: `tests/test_app_runner.py::test_AC_4_circuit_breaker_alert_rendering`)
- [x] **AC-5 (Integration - End-to-End Runner Execution):** La ejecución del runner con proveedor mock completa las 4 etapas y retorna exit code 0. (Verified by: `tests/test_app_runner.py::test_AC_5_end_to_end_runner_execution`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Direct en módulo `scripts/harness/` y `run-harness.ps1`.
- **Production Rollback Plan:** Revertir rama `feat/windows-runner-app`.
- **Observability & SLI/SLO Telemetry:** Telemetría en consola con conteo de tokens acumulados y tiempo de ciclo.

## 7. Execution Checkpoints
- [x] Checkpoint 1: Automated tests committed in failing (Red) state.
- [x] Checkpoint 2: Minimal domain logic implemented (Green state).
- [x] Checkpoint 3: Negative Fault Injection (Mutation Test) passed: deliberately altered logic causes test failure.
- [x] Checkpoint 4: Refactored logic clean with tests maintaining Green state and ≥85% branch coverage.
- [x] Checkpoint 5: All Acceptance Criteria (including Security AC-Sec in Sections 4 and 5) validated in terminal and marked `[x]` with test identifier.
- [x] Checkpoint 6: Full global regression, production build, and security audit pass cleanly.
- [x] Checkpoint 7: Adversarial review passed, and all OOS negative constraints in Section 2 audited and marked `[x]`.
- [x] Checkpoint 8: Selective OKF compilation completed and Pull Request description generated. (Zero unchecked `[ ]` boxes remaining in spec).

## 8. Amendment Log
<!-- Ninguna enmienda hasta el momento -->
