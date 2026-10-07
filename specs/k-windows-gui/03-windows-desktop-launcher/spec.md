# Spec: Phase 3 - Windows Desktop Launcher & PowerShell Integration (`03-windows-desktop-launcher`)

## 1. Goal & Context
- **Business Rationale:** Proveer la capa de arranque nativa para Windows (`run-gui.ps1` y `scripts/harness/gui/launch.py`) que permita a los desarrolladores iniciar la aplicación gráfica de Antigravity 2.0 con un solo comando o doble clic en PowerShell, abriendo automáticamente la interfaz web en su navegador predeterminado o en ventana nativa de escritorio.
- **User Story:** Como usuario de Windows, quiero ejecutar `.\run-gui.ps1` en mi terminal para que se levante el servidor local ASGI y se abra de inmediato la interfaz visual de Antigravity 2.0 sin tener que recordar URLs, puertos ni comandos complejos de uvicorn.
- **Git Branch Target:** `feat/windows-gui-app`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar cualquier archivo dentro del directorio `.agents/skills/`. (Verificado: git status confirma 0 modificaciones en .agents/skills/).
- [x] **OOS-2:** Eliminar o romper el lanzador de consola existente (`run-harness.ps1` y `k_runner.py` deben seguir funcionando como opción CLI alternativa).
- [x] **OOS-3:** Forzar instalación obligatoria de compiladores C++ para empaquetado de ejecutables Windows.

## 3. Technical Contract & Architecture
- **Launcher en Python (`scripts/harness/gui/launch.py`):**
  - Soporta argumentos de línea de comandos: `--port` (default: 8000 o puerto libre), `--host` (default: 127.0.0.1), `--no-browser`.
  - Detección de puerto disponible para evitar conflictos con otros servicios locales (`find_available_port(start_port)`).
  - Apertura automática de navegador (`webbrowser.open`).
  - Gestión limpia de señales de apagado (*graceful shutdown* con Ctrl+C).
- **Lanzador PowerShell (`run-gui.ps1`):**
  - Configuración forzada de codificación UTF-8 en consola de Windows.
  - Parámetros: `-Port`, `-HostAddress`, `-NoBrowser`.
  - Invocación de `python scripts/harness/gui/launch.py` con propagación del código de salida.
- **Documentación en `README.md`:**
  - Actualización de la sección de uso del CLI y GUI explicando el arranque con `.\run-gui.ps1`.

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:**
  - Exposición no autorizada del servidor en interfaces de red públicas (0.0.0.0). El host por defecto debe ser exclusivamente la interfaz de bucle local (`127.0.0.1` / `localhost`).
  - Inyección de argumentos maliciosos en la invocación de subprocesos o launchers.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** El launcher debe enlazar por defecto exclusivamente a `127.0.0.1` para prevenir acceso no autorizado desde la red local a las APIs de ejecución de código. (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_Sec_1_localhost_binding_default`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Enlace por defecto a localhost (`127.0.0.1`) sin exposición a interfaces de red externas. (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_Sec_1_localhost_binding_default`)
- [x] **AC-1 (Happy Path - Port Auto-Resolution):** El launcher detecta si el puerto predeterminado está en uso y encuentra el siguiente puerto TCP libre disponible. (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_1_port_auto_resolution`)
- [x] **AC-2 (Happy Path - Python Launcher CLI):** `launch.py` procesa argumentos `--port`, `--host`, `--no-browser` y expone función invocable de arranque. (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_2_launch_cli_args`)
- [x] **AC-3 (Happy Path - PowerShell Script Existence & Arguments):** `run-gui.ps1` existe en la raíz del repositorio y define parámetros válidos con codificación UTF-8. (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_3_powershell_launcher_contract`)
- [x] **AC-4 (Happy Path - Server Lifecycle & Health Check):** El launcher es capaz de verificar que el servidor local responde en `/api/status` antes de reportar el arranque exitoso. (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_4_healthcheck_verification`)
- [x] **AC-5 (Happy Path - Documentation Integrity):** `README.md` documenta con precisión cómo ejecutar tanto la versión gráfica (`.\run-gui.ps1`) como la versión CLI (`.\run-harness.ps1`). (Verified by: `tests/test_gui_desktop_launcher.py::test_AC_5_documentation_updated`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Archivos `run-gui.ps1`, `scripts/harness/gui/launch.py`, y actualización de `README.md`.
- **Production Rollback Plan:** Revertir commits de la fase en `feat/windows-gui-app`.
- **Observability Contract:** Emisión de logs de consola en Windows indicando la URL local activa.

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
