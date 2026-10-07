# Spec: Phase 4 - Electron Desktop Migration & Framework Modernization (`04-electron-desktop-migration`)

## 1. Goal & Context
- **Business Rationale:** Migrar la experiencia visual de la interfaz gráfica a una pila de frameworks modernos (React 18 + Vite 6 + Tailwind CSS) empaquetada como una aplicación de escritorio nativa multiplataforma con **Electron 33**, bajo el nombre oficial **`k-method app`**. La aplicación sustituye la dependencia exclusiva del navegador por una ventana nativa de alto rendimiento con ciclo de vida gobernado, manteniendo paridad funcional estricta con las capacidades del repositorio (3 columnas, live git diffs, catálogo Karpathy v0, streaming de tokens y compuertas humanas).
- **User Story:** Como desarrollador u operador de `k-method`, quiero ejecutar una aplicación de escritorio nativa (`k-method app.exe`) que orqueste automáticamente el backend de Python en segundo plano (sidecar), presente una interfaz ergonómica en 3 columnas con recarga en caliente y renderizado reactivo, y permita interactuar con el motor SDLC sin exponer directivas ni requerir terminal abierta.
- **Git Branch Target:** `feat/electron-desktop-migration`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar los archivos canónicos de skills en `.agents/skills/`. (Verificado: 0 modificaciones en `.agents/skills/`).
- [x] **OOS-2:** Reimplementar la lógica de negocio o la máquina de estados en JavaScript/TypeScript; el motor de IA, orquestación y adaptadores permanecen en Python (`scripts/harness/engine/`).
- [x] **OOS-3:** Utilizar la marca o nombre comercial de "Antigravity". La identidad del producto se establece como `k-method app` / `k-method Studio`.
- [x] **OOS-4:** Reintroducir referencias obsoletas a `v17`; toda la arquitectura, metadatos y skills se estandarizan exclusivamente en `v0`.

## 3. Technical Contract & Architecture
- **Desktop Architecture (`desktop/`):**
  - **Main Process (`desktop/electron/main.ts`):** Proceso Node.js que administra la ventana principal de Electron (`1400x900`), gestiona IPC (`window-minimize`, `window-maximize`, `window-close`), y supervisa el proceso hijo *sidecar* de Python (`scripts/harness/gui/launch.py --headless`).
  - **Preload Bridge (`desktop/electron/preload.ts`):** Context bridge seguro que expone la API `window.electronAPI` sin comprometer `nodeIntegration`.
  - **Renderer App (`desktop/src/`):** Aplicación SPA en React 18 + TypeScript + Vite 6 + Tailwind CSS estructurada en 3 columnas:
    - *Columna Izquierda (`Sidebar.tsx`):* Explorador del workspace (`k-method`, `specs`, `knowledge-base`, `.agents/skills`), selectores de proveedor/modelo y catálogo de directivas canónicas de Karpathy v0.
    - *Columna Central (`ChatCanvas.tsx`):* Flujo conversacional, badges de discriminación de intención, tarjetas colapsables de etapas TDD (`StepCard.tsx`), streaming de tokens y modal de aprobación (`ApprovalModal.tsx`).
    - *Columna Derecha (`AuxiliaryPane.tsx`):* Pestañas para *Artifacts*, *Files Changed* (diff de Git coloreado), *TDD Logs*, y *OKF Graph*.
- **Empaquetado (`desktop/package.json` & `electron-builder`):**
  - Configuración para generación de instaladores y distribución desempacada en `desktop/release/win-unpacked/k-method app.exe`.
  - Script lanzador raíz `run-desktop.ps1` con soporte para modo desarrollo (`-Dev` con HMR) y ejecución directa del binario.

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:**
  - Ejecución de código arbitrario (RCE) desde el contexto del renderizador hacia el sistema operativo.
  - Exposición de claves o credenciales mediante inyección en el canal WebSocket o IPC.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1 (Security - Context Isolation & Node Integration Guard):** `BrowserWindow` debe declarar explícitamente `nodeIntegration: false`, `contextIsolation: true` y `webSecurity: true`, impidiendo el acceso a APIs de Node en el DOM. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_Sec_1_context_isolation_and_security`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Configuración estricta de aislamiento de contexto y seguridad en la ventana nativa de Electron. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_Sec_1_context_isolation_and_security`)
- [x] **AC-1 (Desktop Architecture & Directory Layout):** La aplicación de escritorio reside en `desktop/` y declara configuraciones válidas de TypeScript, Vite, Tailwind y Electron sin referencias a `v17`. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_1_desktop_directory_layout`)
- [x] **AC-2 (Electron Main & Sidecar Lifecycle):** `desktop/electron/main.ts` gestiona la creación de ventana, enlace al backend ASGI en puerto 8000 y terminación limpia de procesos hijos al cerrar. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_2_electron_main_and_sidecar`)
- [x] **AC-3 (Component Hierarchy & 3-Column Layout):** Los componentes de React (`Sidebar`, `ChatCanvas`, `AuxiliaryPane`, `Header`) implementan la arquitectura de 3 columnas vinculada a los endpoints reales de `k-method`. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_3_component_hierarchy`)
- [x] **AC-4 (CORS & Communication Protocol):** El servidor ASGI en `scripts/harness/gui/server.py` incorpora `CORSMiddleware` para habilitar peticiones locales cruzadas desde el renderer de Vite y Electron. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_4_cors_middleware_enabled`)
- [x] **AC-5 (Windows Launcher & Packaging Script):** El script `run-desktop.ps1` permite arrancar la aplicación en modo desarrollo (`-Dev`) o lanzar el ejecutable compilado `k-method app.exe`. (Verified by: `tests/test_electron_desktop_migration.py::test_AC_5_launcher_script_exists`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Compilación mediante `pnpm run build` produciendo el bundle de Vite en `desktop/dist/` y el ejecutable empaquetado en `desktop/release/win-unpacked/k-method app.exe`.
- **Production Rollback Plan:** Revertir a la versión anterior de la interfaz web (`run-gui.ps1` con archivos estáticos en `scripts/harness/gui/static/`).
- **Observability Contract:** Eventos tipados emitidos por WebSocket (`stage_changed`, `token`, `approval_required`, `tdd_output`, `circuit_breaker`, `completed`) y logs de consola de Electron/Python.

## 7. Execution Checkpoints
- [x] Checkpoint 1: Estructura de carpetas y dependencias de `desktop/` configuradas.
- [x] Checkpoint 2: Componentes de React y estilos de Tailwind compilando sin errores de TypeScript (`tsc --noEmit`).
- [x] Checkpoint 3: Proceso principal de Electron compilado como CommonJS eliminando conflictos de ESM.
- [x] Checkpoint 4: Empaquetado completado en `desktop/release/win-unpacked/k-method app.exe` (188 MB).
- [x] Checkpoint 5: Ejecución verificada en vivo con procesos activos y sin errores de JavaScript.
- [x] Checkpoint 6: Todas las pruebas de compuerta (`scripts/verify-all.py`) pasando al 100%.

## 8. Amendment Log
- 2026-10-08: Creación inicial de la especificación formal para documentar la migración de la GUI a frameworks modernos (React/Vite/Tailwind) y empaquetado con Electron.
