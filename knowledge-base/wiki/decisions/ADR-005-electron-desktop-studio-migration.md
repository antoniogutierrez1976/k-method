---
okf_version: "1.0"
node_type: decision
id: "ADR-005-electron-desktop-studio-migration"
status: active
domain: "desktop-gui-architecture"
governed_by: ["[[ADR-001-karpathy-3-layer-architecture]]", "[[ADR-004-antigravity-gui-and-embedded-skills]]"]
dependencies: []
supersedes: null
superseded_by: null
updated_at: "2026-10-08"
---

# ADR-005: Migración de la Interfaz a Frameworks Modernos (React, Vite) y Empaquetado Nativo con Electron

## Contexto y Problema
La interfaz web inicial servida mediante archivos estáticos (`scripts/harness/gui/static/`) permitía la interacción básica a través del navegador web tradicional. Sin embargo, presentaba limitaciones para la experiencia de desarrollo:
1. Dependencia de abrir ventanas del navegador externo, compitiendo con las pestañas de navegación personal y sin aislamiento de proceso ni controles de ventana dedicados.
2. Dificultad para incorporar componentes reactivos avanzados (como paneles interactivos con recarga en caliente HMR, árboles de directorios colapsables y editores enriquecidos) utilizando únicamente JavaScript vainilla sin empaquetador moderno.
3. Necesidad de lanzar manualmente el intérprete de Python o depender de scripts PowerShell en terminal abierta.

## Decisión
Se adopta una arquitectura de aplicación de escritorio desacoplada (**Electron Desktop Studio** con **Sidecar Python**) ubicada en el directorio `desktop/`:
1. **Frontend Moderno:**
   - Construido con **React 18**, **TypeScript 5**, **Vite 6** y **Tailwind CSS**.
   - Disposición en 3 columnas ergonómicas con renderizado reactivo:
     - *Sidebar Izquierda:* Árbol del workspace real (`k-method`, `specs`, `knowledge-base`, `.agents/skills`), selector de modelo y visualizador modal de directivas canónicas de Karpathy v0.
     - *Canvas Central:* Streaming de tokens atómicos, tarjetas colapsables de fase y compuerta interactiva de aprobación de especificaciones (`ApprovalModal`).
     - *Panel Auxiliar Derecho:* Pestañas para *Artifacts*, *Files Changed* (diff de Git coloreado en vivo), *TDD Logs*, y *OKF Graph*.
2. **Proceso Principal de Electron & Gestión de Sidecar:**
   - El proceso principal de Electron (`desktop/electron/main.ts`) actúa como supervisor del proceso hijo en Python (`scripts/harness/gui/launch.py --headless`), garantizando el apagado automático al cerrar la aplicación.
   - Seguridad reforzada: `nodeIntegration: false`, `contextIsolation: true`, y `webSecurity: true`.
3. **Distribución y Empaquetado:**
   - Empaquetado automatizado con `electron-builder` generando el binario desempacado en `desktop/release/win-unpacked/k-method app.exe`.
   - Script lanzador raíz `run-desktop.ps1` que soporta tanto el modo desarrollo (`-Dev` con Vite HMR) como el binario de producción.

## Consecuencias
- **Positivas:**
  - Experiencia de escritorio nativa independiente del navegador, con tiempos de respuesta inmediatos y alta fidelidad visual.
  - Ecosistema frontend moderno basado en componentes tipados reutilizables.
  - Gestión automática y transparente del servidor ASGI de Python sin requerir comandos manuales.
- **Negativas / Costes:**
  - Tamaño de distribución incrementado por el empaquetado del runtime de Chromium/Electron (~188 MB).
  - Mantenimiento de la capa de dependencias en `desktop/package.json` y el bridge de comunicación WebSocket.

## Enlaces Relacionados
- [[ADR-001-karpathy-3-layer-architecture]]
- [[ADR-004-antigravity-gui-and-embedded-skills]]
- [[environment-governor]]
- [[index]]
