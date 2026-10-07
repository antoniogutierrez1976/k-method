# Epic Breakdown: k-windows-runner (Windows Skills Harness & Runner)

## 1. Executive Summary
- **Overall Goal:** Desarrollar un arnés de ejecución y aplicación interactiva para Windows (CLI + TUI/Desktop runner estilo Antigravity) capaz de orquestar el bucle de las skills existentes en `k-method` (`k-orchestrator`, `k-spec`, `k-verifier`, `k-environment`, `k-wiki`) de manera determinista y atomizada, con soporte dual para **Google Antigravity SDK** (uso personal) y **GitHub Copilot SDK** (uso profesional con GPT-6 Luna).
- **Invariante Crítica / Restricción Negativa:** **PROHIBIDO modificar los archivos y scripts de las skills existentes en `.agents/skills/`**. El arnés consume las skills exclusivamente como artefactos y referencias de entrada inmutables.
- **Alcance Arquitectónico:**
  - Capa de Abstracción de Proveedores (Google Antigravity SDK & GitHub Copilot SDK).
  - Motor de Orquestación y Máquina de Estados Karpathy (Spec -> Git/Stash -> TDD -> Circuit Breaker -> Wiki).
  - Aplicación Runner para Windows (Interfaz interactiva con streaming de tokens, paneles auxiliares de estado, y paradas de aprobación humana).

---

## 2. Descomposición en Fases Secuenciales (Milestones)

Cada fase representa un incremento autónomo y verificable con su propia especificación y compuertas de calidad:

### Fase 1: Abstracción de Proveedores y Motor Atómico (`01-provider-adapters`)
- **Target Spec:** `specs/k-windows-runner/01-provider-adapters/spec.md`
- **Alcance:**
  - Definición de la interfaz agnóstica `BaseAgentProvider`.
  - Implementación de `CopilotProvider` utilizando `github-copilot-sdk` con soporte para modelos OpenAI (GPT-6 Luna / Sol).
  - Implementación de `AntigravityProvider` utilizando `google-antigravity` con gestión de capacidades (`CapabilitiesConfig`).
  - Suite de pruebas unitarias y de contrato con mocks para ambos SDKs.
- **Fuera de Alcance:** Lógica completa del ciclo TDD o interfaz de usuario de Windows.
- **Compuerta de Verificación:** Suite de pruebas unitarias (`unittest`) verdes con cobertura $\ge 85\%$ sobre los adaptadores, validando llamadas atómicas sin acumulación de contexto.

### Fase 2: Motor Determinista de Orquestación SDLC y Disyuntor (`02-sdlc-orchestration-engine`)
- **Target Spec:** `specs/k-windows-runner/02-sdlc-orchestration-engine/spec.md`
- **Alcance:**
  - Máquina de estados que ejecuta las fases de `k-orchestrator` por software:
    - *Fase Spec:* Validación automática del límite duro de 6 ACs.
    - *Fase Environment:* Ejecución determinista de *Stash Shield* (`git status --porcelain`) y aislamiento de ramas.
    - *Fase Verifier:* Ciclo Red-Green atomizado, verificación de cobertura ($\ge 85\%$) y **Deadlock Circuit Breaker** en código (activación al segundo fallo idéntico consecutivo).
    - *Fase Wiki:* Invocación del compilador OKF existente sin tocar sus fuentes.
- **Fuera de Alcance:** Interfaz gráfica interactiva de Windows (solo API de backend y CLI básico).
- **Compuerta de Verificación:** Pruebas de integración simuladas verificando transiciones de estado, disparo del disyuntor y generación de diffs.

### Fase 3: Aplicación Runner para Windows estilo Antigravity (`03-windows-app-runner`)
- **Target Spec:** `specs/k-windows-runner/03-windows-app-runner/spec.md`
- **Alcance:**
  - Aplicación de escritorio / consola enriquecida (TUI/GUI en Windows) con estética y paneles auxiliares inspirados en Antigravity:
    - Panel de conversación y streaming de tokens en vivo.
    - Panel auxiliar de estado: etapa activa, estado de Git, salida de tests y consumo de tokens/costes.
    - Modales interactivos de aprobación humana (*Human Approval Gate* tras la especificación y resolución de fricción en el disyuntor).
  - Empaquetado para Windows (ejecutable o CLI con launcher directo de PowerShell).
- **Fuera de Alcance:** Modificación de especificaciones de fases previas.
- **Compuerta de Verificación:** Verificación visual en Windows (renderizado de paneles, control de eventos de teclado, manejo de señales de cancelación).

---

## 3. Acción Inmediata Recomendada
- El usuario debe revisar y aprobar este desglose de épica.
- Tras la aprobación humana explícita, se generará la especificación detallada de la **Fase 1 (`01-provider-adapters/spec.md`)** para iniciar el primer ciclo TDD.
