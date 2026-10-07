# Spec: Phase 2 - Antigravity 2.0 GUI Frontend Layout (`02-gui-frontend-layout`)

## 1. Goal & Context
- **Business Rationale:** Construir la interfaz de usuario gráfica de escritorio/web de **Antigravity 2.0** en una Single Page Application (SPA) moderna, limpia y reactiva que consuma el backend ASGI desarrollado en la Fase 1. La interfaz reproduce la disposición visual de tres columnas de Antigravity (Sidebar Izquierda, Chat Canvas Central y Panel Auxiliar Derecho con pestañas de Artifacts, Diffs y TDD), ofreciendo una experiencia inmersiva para gobernar el SDLC.
- **User Story:** Como desarrollador que utiliza `k-windows-gui`, quiero una interfaz gráfica Dark-Mode con la estética de Antigravity 2.0 para interactuar con el agente en streaming, aprobar especificaciones mediante botones interactivos y visualizar artefactos y diffs de Git en tiempo real.
- **Git Branch Target:** `feat/windows-gui-app`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar cualquier archivo dentro del directorio `.agents/skills/`. (Verificado: git status confirma 0 modificaciones en .agents/skills/).
- [x] **OOS-2:** Requerir compiladores pesados de Node.js o bundlers complejos (el frontend debe ser HTML5/CSS/JavaScript vanilla servido directamente por FastAPI).
- [x] **OOS-3:** Implementar el lanzador de escritorio y empaquetado de PowerShell (reservado para la Fase 3 `03-windows-desktop-launcher`).

## 3. Technical Contract & Architecture
- **Estructura de Archivos Estáticos:**
  - `scripts/harness/gui/static/index.html`: Plantilla SPA principal con layout de 3 columnas estilo Antigravity 2.0.
  - `scripts/harness/gui/static/app.js`: Cliente reactivo en JavaScript vanilla que gestiona el ciclo de vida del WebSocket `/ws/sdlc`, streaming de tokens, conmutación de pestañas y botones de aprobación humana.
  - `scripts/harness/gui/static/style.css`: Estilos visuales dark-mode con tokens de diseño de Antigravity (paleta oscura, bordes sutiles, tipografía monoespaciada para código y paneles de estado).
- **Montaje en FastAPI:**
  - `server.py` monta `StaticFiles(directory=static_dir, html=True)` en `/static` y sirve `index.html` en la raíz `/`.
- **Estructura DOM de 3 Columnas:**
  - `#sidebar-left`: Selector de Proveedor (`Copilot`, `Antigravity`, `Mock`), selector de Modelo, lista de skills embebidas y estado de Git / Stash Shield.
  - `#chat-canvas`: Historial de conversación en vivo, burbujas de estado de fase (`k-orchestrator`), contenedor de streaming de tokens, barra de aprobación humana interactiva (`#approval-bar`), y campo de entrada de tarea.
  - `#auxiliary-pane`: Panel derecho con pestañas navegables:
    - `tab-artifacts`: Vista previa en Markdown de la `spec.md` y PR description generada.
    - `tab-diff`: Visor coloreado de líneas añadidas/eliminadas de Git.
    - `tab-tdd`: Salida de terminal de pruebas (fase Red fallida y fase Green superada).
    - `tab-okf`: Catálogo de directivas embebidas y enlaces de ADRs.

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:**
  - Inyección de código malicioso Cross-Site Scripting (XSS) a través del contenido Markdown generado por el LLM o introducido en el prompt.
  - Exposición de rutas absolutas peligrosas o ejecución de scripts inline en el renderizado de diffs.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** El renderizado de Markdown y diffs en el cliente debe sanitizar el contenido HTML para prevenir ejecución de scripts (XSS) y manipulación del DOM. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_Sec_1_xss_sanitization`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Sanitización contra XSS en el renderizado de contenido dinámico en el DOM. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_Sec_1_xss_sanitization`)
- [x] **AC-1 (Happy Path - Static Asset Serving):** FastAPI sirve `index.html` en la ruta `/` con código HTTP 200 y monta `/static` con los recursos estáticos. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_1_static_asset_serving`)
- [x] **AC-2 (Happy Path - Antigravity 2.0 3-Column Layout):** El documento HTML declara los tres contenedores estructurales principales: `#sidebar-left`, `#chat-canvas`, y `#auxiliary-pane`. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_2_antigravity_3_column_layout`)
- [x] **AC-3 (Happy Path - Reactive WebSocket Client):** El cliente JavaScript se conecta a `/ws/sdlc`, actualiza las insignias de fase (`SPEC`, `VERIFIER_RED`, etc.) en tiempo real e inserta el streaming de tokens en el canvas. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_3_websocket_client_contract`)
- [x] **AC-4 (Boundary - Interactive Human Approval Action Bar):** Al recibir el evento `approval_required`, la interfaz muestra la barra interactiva de aprobación con botones "Aprobar" y "Revisar", enviando `approval_response` al backend al hacer clic. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_4_human_approval_action_bar`)
- [x] **AC-5 (Happy Path - Auxiliary Tabs Switching):** El panel auxiliar permite alternar entre las 4 pestañas (*Artifacts*, *Files Changed / Diff*, *TDD Verifier*, y *OKF Graph*) actualizando el contenido visible. (Verified by: `tests/test_gui_frontend_layout.py::test_AC_5_auxiliary_tabs_switching`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Archivos en `scripts/harness/gui/static/` integrados en `server.py`.
- **Production Rollback Plan:** Revertir commits de la fase en `feat/windows-gui-app`.
- **Observability Contract:** Los cambios de pestaña y eventos WebSocket emiten mensajes estructurados en la consola de depuración del navegador.

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
