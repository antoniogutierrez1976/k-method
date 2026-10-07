# Epic Breakdown: k-windows-gui (Antigravity 2.0 Graphical Desktop/Web App for k-method)

## 1. Executive Summary
- **Overall Goal:** Desarrollar una aplicación gráfica para Windows con la estética, disposición y paneles auxiliares idénticos a **Antigravity 2.0** (Left Sidebar, Central Chat Canvas, y Right Auxiliary Pane con Artifacts, Diffs y TDD), sustituyendo la interfaz puramente de consola (CLI) por una experiencia visual interactiva en tiempo real.
- **Invariante Crítica / Restricción Negativa:** **PROHIBIDO modificar los archivos y scripts de las skills existentes en `.agents/skills/`**. La aplicación gráfica consume el motor existente `KMethodEngine` y las skills exclusivamente como artefactos y referencias de entrada inmutables.
- **Stack Técnico Seleccionado:**
  - **Backend:** Servidor ASGI local ultraligero (FastAPI + Starlette WebSockets) enlazado directamente a `KMethodEngine` y `ProviderFactory` (`scripts/harness/engine/state_machine.py`).
  - **Frontend:** Interfaz web moderna Dark-Mode inspirada en Antigravity 2.0 (Tailwind CSS, Marked.js para renderizado de Markdown/Specs, Highlight.js/Diff2Html para diffs de Git en tiempo real, e iconos Phosphor).
  - **Launcher Windows:** Script PowerShell `run-gui.ps1` que arranca el servidor local y abre la interfaz automáticamente en el navegador predeterminado o en ventana de escritorio sin marcos.

---

## 2. Arquitectura Visual de Antigravity 2.0

```
┌─────────────────────────┬──────────────────────────────────┬─────────────────────────────┐
│ 1. SIDEBAR IZQUIERDA    │ 2. CHAT CANVAS CENTRAL           │ 3. PANEL AUXILIAR DERECHO   │
├─────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 📂 Workspace: k-method  │ 🚀 Ejecución de Tarea en Vivo    │ 📑 [Artifacts]              │
│ 🤖 Provider Selector:   │                                  │    - spec.md (Markdown)     │
│    [Copilot | Agy | Mock]│  [k-orchestrator] Analizando... │    - PR description         │
│ 🧠 Model:               │  [k-spec] Generando spec...      │ 🔄 [Files Changed / Diff]   │
│    [gemini-2.5-flash ▾] │                                  │    - git diff interactivo   │
│ ⚙️ Skills Activas:      │  ╔═════════════════════════════╗ │ 🧪 [TDD & Verifier]         │
│    • k-spec             │  ║ ✋ APROBACIÓN REQUERIDA    ║ │    - Red phase failure log  │
│    • k-verifier         │  ║ [Aprobar]    [Revisar]    ║ │    - Green pass status      │
│    • k-environment      │  ╚═════════════════════════════╝ │ 📚 [OKF Graph]              │
│    • k-wiki             │                                  │    - Linter & ADRs list     │
│ 🛡️ Stash Shield: Clean  │ 💬 Prompt / Entrada de Usuario   │ ⚠️ [Alertas Disyuntor]      │
└─────────────────────────┴──────────────────────────────────┴─────────────────────────────┘
```

---

## 3. Descomposición en Fases Secuenciales (Milestones)

### Fase 1: API de Backend y Streaming de Eventos en Tiempo Real (`01-gui-backend-api`)
- **Target Spec:** `specs/k-windows-gui/01-gui-backend-api/spec.md`
- **Alcance:**
  - Servidor FastAPI/Starlette en `scripts/harness/gui/server.py`.
  - Canal WebSocket bi-direccional (`/ws/sdlc`) para:
    - Iniciar ejecuciones enviando prompt, proveedor y modelo.
    - Emitir eventos atómicos: `stage_change`, `token_stream`, `approval_required`, `tdd_output`, `circuit_breaker_tripped`, `completed`.
    - Recibir respuestas de interacción humana: `submit_approval(decision: bool, feedback: str)`.
  - Endpoints REST auxiliares para consultar estado del workspace, diff de Git y lista de ADRs.
- **Fuera de Alcance:** Diseño visual detallado en HTML/CSS.
- **Compuerta de Verificación:** Pruebas unitarias con `TestClient` de FastAPI validando el protocolo WebSocket, serialización de eventos y manejo de la máquina de estados sin bloqueos de hilo.

### Fase 2: Layout y Componentes Frontend Estilo Antigravity 2.0 (`02-gui-frontend-layout`)
- **Target Spec:** `specs/k-windows-gui/02-gui-frontend-layout/spec.md`
- **Alcance:**
  - Plantilla SPA estática servida por FastAPI en `scripts/harness/gui/static/`:
    - Sidebar izquierda (selección de proveedor, modelo, skills activas y Stash Shield status).
    - Canvas central de chat con burbujas de estado de `k-orchestrator`, streaming de tokens y modal/barra de aprobación humana.
    - Panel auxiliar derecho con pestañas interactivas: *Artifacts* (vista previa de la spec y PR), *Files Changed* (diff de Git con coloreado de sintaxis), *TDD Verifier* (terminal de pruebas) y *OKF Graph*.
  - Cliente WebSocket en JavaScript puro (sin dependencias complejas de Node.js) que se reconecta y actualiza el DOM de forma reactiva.
- **Fuera de Alcance:** Empaquetado binario como ejecutable Windows.
- **Compuerta de Verificación:** Pruebas automatizadas de renderizado y contratos de API, asegurando que todos los archivos estáticos carguen con código HTTP 200 y que la vista se adapte correctamente.

### Fase 3: Lanzador para Windows y Flujo de Trabajo Integrado (`03-windows-desktop-launcher`)
- **Target Spec:** `specs/k-windows-gui/03-windows-desktop-launcher/spec.md`
- **Alcance:**
  - Script de arranque `scripts/harness/gui/app.py` y lanzador PowerShell `run-gui.ps1`.
  - Apertura automática en el navegador predeterminado (o ventana nativa si `pywebview` está instalado) en `http://127.0.0.1:8000`.
  - Cierre ordenado (*graceful shutdown*) al presionar Ctrl+C o cerrar la ventana.
  - Actualización de `README.md` documentando el uso de `run-gui.ps1`.
- **Fuera de Alcance:** Modificación del motor CLI existente (`k_runner.py` permanece intacto como opción de terminal).
- **Compuerta de Verificación:** Ejecución de `verify-all.py` superando compuertas de pruebas unitarias, grafo OKF y Stash Shield.

---

## 4. Próxima Acción Inmediata
- Confirmar el inicio de la **Fase 1 (`01-gui-backend-api`)** con la creación de su especificación formal (`spec.md`) siguiendo el límite duro de $\le 6$ Criterios de Aceptación de Karpathy.
