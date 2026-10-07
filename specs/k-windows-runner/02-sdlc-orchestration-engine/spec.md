# Spec: Phase 2 - SDLC Orchestration Engine & Circuit Breaker

## 1. Goal & Context
- **Business Rationale:** Dotar al arnés de una máquina de estados determinista en Python que gobierne el ciclo Karpathy SDLC (Spec -> Environment -> Verifier TDD -> OKF) sin depender de que el LLM mantenga la disciplina por sí mismo, protegiendo contra bucles infinitos y violaciones de compuertas.
- **User Story:** Como operador del arnés o desarrollador, quiero que el motor ejecute las validaciones de Git, detenga turnos tras la especificación, fuerce el ciclo TDD y dispare un disyuntor (*Circuit Breaker*) si un test falla 2 veces con el mismo error, para que modelos de bajo coste como GPT-6 Luna ejecuten de forma segura y fiable.
- **Git Branch Target:** `feat/windows-runner-sdlc-engine`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar cualquier archivo, plantilla o script dentro de `.agents/skills/`. (Verificado: git status confirma cero modificaciones en .agents/skills/).
- [x] **OOS-2:** Implementar la interfaz visual/gráfica de usuario para Windows (reservada para la Fase 3).
- [x] **OOS-3:** Invocar shells con `shell=True` o concatenar argumentos de comandos sin sanitizar. (Verificado: todas las llamadas subprocess emplean listas de argumentos y shell=False).

## 3. Technical Contract & Architecture
- **Data Models / Schemas:**
  ```python
  from enum import Enum
  from dataclasses import dataclass
  from typing import Optional, List, Dict, Callable

  class SDLCStage(Enum):
      SPEC = "spec"
      ENVIRONMENT = "environment"
      VERIFIER_RED = "verifier_red"
      VERIFIER_GREEN = "verifier_green"
      CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"
      RELEASE_OKF = "release_okf"
      COMPLETED = "completed"
      ABORTED = "aborted"

  @dataclass
  class CircuitBreakerStatus:
      tripped: bool
      failure_count: int
      last_signature: Optional[str] = None
      diff_report: Optional[str] = None
  ```
- **Endpoints / Signatures:**
  - `CircuitBreaker.record_failure(error_signature: str) -> bool` (retorna True si se dispara)
  - `StashShield.check_clean(cwd: str) -> bool`
  - `KMethodEngine(provider: BaseAgentProvider, runner_cmd: Callable)`
  - `KMethodEngine.run_pipeline(task: str, branch_name: str) -> SDLCStage`

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:**
  - Inyección de comandos en terminal vía nombres de ramas o parámetros de tareas no validados (`subprocess`).
  - Bucles infinitos de llamadas que agoten la cuota de tokens o bloqueen el sistema.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** Toda ejecución de comandos de terminal en el motor debe emplear llamadas de subproceso parametrizadas (`shell=False`) con listas de argumentos estrictas y sanitización de nombres de rama. (Verified by: `tests/test_sdlc_engine.py::test_AC_Sec_1_no_shell_injection`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Ejecución segura de subprocesos sin `shell=True` y sanitización de argumentos. (Verified by: `tests/test_sdlc_engine.py::test_AC_Sec_1_no_shell_injection`)
- [x] **AC-1 (Spec Gate & 6-AC Limit):** El motor rechaza especificaciones que contengan más de 6 Criterios de Aceptación (`AC-*`) y activa la compuerta de aprobación antes de continuar. (Verified by: `tests/test_sdlc_engine.py::test_AC_1_spec_gate_and_ac_limit`)
- [x] **AC-2 (Environment & Stash Shield):** El motor verifica el estado de Git (`git status --porcelain`) y rehúsa continuar en un working tree sucio salvo confirmación o stash explícito. (Verified by: `tests/test_sdlc_engine.py::test_AC_2_stash_shield`)
- [x] **AC-3 (TDD Red-Green Cycle):** El motor exige que la prueba falle (código != 0) en la fase Red antes de autorizar la fase Green, y valida la finalización con código 0. (Verified by: `tests/test_sdlc_engine.py::test_AC_3_tdd_cycle`)
- [x] **AC-4 (Deadlock Circuit Breaker):** Al detectarse 2 fallos consecutivos con la misma firma de error, el disyuntor se dispara, detiene las ediciones y genera un informe de fricción con diff. (Verified by: `tests/test_sdlc_engine.py::test_AC_4_circuit_breaker`)
- [x] **AC-5 (OKF & PR Closure):** Tras superar la fase Verifier, el motor invoca la verificación OKF y genera el borrador de Pull Request. (Verified by: `tests/test_sdlc_engine.py::test_AC_5_okf_and_pr_generation`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Direct en módulo `scripts/harness/engine/`.
- **Production Rollback Plan:** Revertir rama `feat/windows-runner-sdlc-engine`.
- **Observability & SLI/SLO Telemetry:** Emisión de eventos de cambio de estado en `KMethodEngine.on_state_change`.

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
