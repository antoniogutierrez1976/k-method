# Spec: Phase 1 - GUI Backend API & Real-time Event Streaming (`01-gui-backend-api`)

## 1. Goal & Context
- **Business Rationale:** Proveer la capa de backend de comunicación en tiempo real y gestión de contexto embebido para la aplicación gráfica de Antigravity 2.0. El backend debe encapsular e inyectar las directivas de las 5 skills de Karpathy v17 en memoria, garantizando la reserva y privacidad metodológica sin requerir `.agents/skills/` en repositorios destino, y orquestar el bucle SDLC vía WebSocket/REST.
- **User Story:** Como operador de la aplicación gráfica `k-windows-gui`, quiero que el backend gestione la conexión WebSocket, el streaming de tokens, la notificación de aprobaciones humanas requeridas y la inyección segura de las directivas de Karpathy en el LLM, para que la interfaz web reaccione en tiempo real sin bloquear el hilo ni exponer las directivas como archivos sueltos en el workspace.
- **Git Branch Target:** `feat/windows-gui-backend-api`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar cualquier archivo dentro del directorio `.agents/skills/`. (Verificado: git status confirma 0 modificaciones en .agents/skills/).
- [x] **OOS-2:** Implementar el diseño visual completo en HTML/CSS ni los componentes frontend (reservados para la Fase 2 `02-gui-frontend-layout`).
- [x] **OOS-3:** Forzar dependencias externas no instaladas (debe utilizar la pila existente de `fastapi`, `starlette` y librerías estándar).

## 3. Technical Contract & Architecture
- **Embedded Skills Directives Registry (`scripts/harness/engine/embedded_skills.py`):**
  - Módulo que almacena internamente las especificaciones canónicas de Karpathy v17:
    - `k-orchestrator`, `k-spec`, `k-verifier`, `k-environment`, `k-wiki`.
  - API: `get_embedded_directive(skill_name: str) -> str` y `list_embedded_skills() -> list[dict]`.
- **FastAPI / Starlette Server (`scripts/harness/gui/server.py`):**
  - WebSocket: `/ws/sdlc`
    - Mensajes entrantes del cliente:
      - `{"action": "start", "task": str, "provider": str, "model": Optional[str]}`
      - `{"action": "approval_response", "approved": bool, "feedback": Optional[str]}`
    - Eventos atómicos salientes hacia el cliente:
      - `{"event": "stage_changed", "stage": str}`
      - `{"event": "token", "content": str}`
      - `{"event": "approval_required", "spec_content": str}`
      - `{"event": "tdd_output", "returncode": int, "output": str}`
      - `{"event": "circuit_breaker", "report": str}`
      - `{"event": "completed", "pr_content": str}`
      - `{"event": "error", "message": str}`
  - REST Endpoints:
    - `GET /api/status`: Devuelve `{ "workspace": str, "branch": str, "is_clean": bool, "provider_default": str }`
    - `GET /api/diff`: Devuelve `{ "diff": str }`
    - `GET /api/skills`: Devuelve `{ "skills": list[dict] }` con metadatos de las skills embebidas.

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:**
  - Fuga accidental de tokens de autenticación o claves API en los payloads de eventos WebSocket.
  - Inyección de comandos no autorizados o denegación de servicio por payloads malformados en WebSocket.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** Los eventos WebSocket y endpoints REST deben sanitizar todos los mensajes y redactar credenciales o claves sensibles antes de su emisión hacia el cliente. (Verified by: `tests/test_gui_backend_api.py::test_AC_Sec_1_credential_redaction_in_api`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Sanitización y redacción de credenciales en todos los eventos emitidos por WebSocket y endpoints REST. (Verified by: `tests/test_gui_backend_api.py::test_AC_Sec_1_credential_redaction_in_api`)
- [x] **AC-1 (Happy Path - Embedded Skills Registry):** El registro embebido provee las directivas completas de las 5 skills de Karpathy v17 y `KMethodEngine` las inyecta en el contexto sin requerir archivos en `.agents/skills/`. (Verified by: `tests/test_gui_backend_api.py::test_AC_1_embedded_skills_registry`)
- [x] **AC-2 (Happy Path - REST Endpoints):** Endpoints `/api/status`, `/api/diff`, y `/api/skills` devuelven el estado del workspace, diff de git y catálogo de directivas con código HTTP 200. (Verified by: `tests/test_gui_backend_api.py::test_AC_2_rest_endpoints`)
- [x] **AC-3 (Happy Path - WebSocket Execution Protocol):** Una conexión WebSocket a `/ws/sdlc` permite iniciar una ejecución con proveedor mock y recibe la secuencia ordenada de eventos atómicos (`stage_changed`, `token`, etc.). (Verified by: `tests/test_gui_backend_api.py::test_AC_3_websocket_execution_protocol`)
- [x] **AC-4 (Boundary - Interactive Approval Gate via WS):** Al alcanzar la fase `SPEC`, el backend emite `approval_required`, pausa la ejecución y se reanuda únicamente tras recibir `approval_response` del cliente. (Verified by: `tests/test_gui_backend_api.py::test_AC_4_interactive_approval_gate_via_ws`)
- [x] **AC-5 (Edge Case - Disconnect & Error Resilience):** Si el cliente WebSocket se desconecta inesperadamente o envía un JSON inválido, el servidor limpia los recursos y no bloquea el event loop. (Verified by: `tests/test_gui_backend_api.py::test_AC_5_disconnect_and_error_resilience`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Módulos en `scripts/harness/engine/embedded_skills.py` y `scripts/harness/gui/server.py`.
- **Production Rollback Plan:** Revertir commits de la fase en `feat/windows-gui-app`.
- **Observability Contract:** Emisión de eventos tipados en tiempo real con marcas de tiempo (`timestamp`) en cada mensaje WebSocket.

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
