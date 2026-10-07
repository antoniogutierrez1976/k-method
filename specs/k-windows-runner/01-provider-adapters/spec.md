# Spec: Phase 1 - Multi-Provider Adapters (Copilot & Antigravity)

## 1. Goal & Context
- **Business Rationale:** Permitir que el arnés de ejecución de `k-method` se conecte tanto a GitHub Copilot SDK (orientado a entornos corporativos con modelos como GPT-6 Luna) como a Google Antigravity SDK (para desarrollo y pruebas locales), mediante una capa de abstracción desacoplada y atomizada.
- **User Story:** Como desarrollador o agente de software, quiero invocar modelos de lenguaje de forma atómica a través de un proveedor configurable (`copilot` o `antigravity`) para que el arnés ejecute las fases del SDLC sin acoplarse a un SDK específico ni retener historial no deseado.
- **Git Branch Target:** `feat/windows-runner-provider-adapters`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** Modificar o alterar cualquier archivo, plantilla o script dentro del directorio `.agents/skills/`. (Verificado: git status confirma cero modificaciones en .agents/skills/).
- [x] **OOS-2:** Implementar la máquina de estados completa de TDD o la interfaz gráfica de usuario de Windows (reservadas para las Fases 2 y 3).
- [x] **OOS-3:** Forzar dependencias duras de paquetes en entornos donde los SDKs no estén instalados (deben emplearse importaciones dinámicas o mocks controlados).

## 3. Technical Contract & Architecture
- **Data Models / Schemas:**
  ```python
  from dataclasses import dataclass
  from typing import Optional, Dict, Any, AsyncGenerator

  @dataclass
  class AgentResponse:
      content: str
      model: str
      usage: Optional[Dict[str, int]] = None
      raw_payload: Optional[Dict[str, Any]] = None

  class ProviderError(Exception):
      """Base exception for provider initialization, authentication or execution errors."""
      pass
  ```
- **Endpoints / Signatures:**
  - `BaseAgentProvider.chat_atomic(prompt: str, system_prompt: str, **kwargs) -> AgentResponse`
  - `BaseAgentProvider.stream_atomic(prompt: str, system_prompt: str, **kwargs) -> AsyncGenerator[str, None]`
  - `CopilotProvider(BaseAgentProvider)` (configurado con `model="gpt-6-luna"`, etc.)
  - `AntigravityProvider(BaseAgentProvider)` (configurado con capacidades de permisos)
  - `MockProvider(BaseAgentProvider)` (para pruebas deterministas sin conexión de red)
  - `ProviderFactory.create(provider_type: str, model: Optional[str] = None, **kwargs) -> BaseAgentProvider`

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:** 
  - Fuga accidental de tokens de autenticación o claves API en trazas de error o representaciones de objetos (`__repr__`, logs).
  - Ejecución de comandos no autorizados si las capacidades del proveedor no se restringen adecuadamente.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** Los adaptadores de proveedores deben redactar cualquier clave API, token de sesión o credencial sensible en sus representaciones de texto (`__repr__`, `__str__`) y en los mensajes de excepción capturados. (Verified by: `tests/test_provider_adapters.py::test_AC_Sec_1_credential_redaction`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Redacción de credenciales en `__repr__` y excepciones. (Verified by: `tests/test_provider_adapters.py::test_AC_Sec_1_credential_redaction`)
- [x] **AC-1 (Happy Path - Factory & Mock):** `ProviderFactory.create('mock')` instancia un proveedor funcional que devuelve `AgentResponse` con contenido y modelo esperados. (Verified by: `tests/test_provider_adapters.py::test_AC_1_factory_and_mock`)
- [x] **AC-2 (Happy Path - Copilot Adapter):** `CopilotProvider` formatea instrucciones de sistema, interactúa con el runtime de Copilot y devuelve un `AgentResponse` normalizado. (Verified by: `tests/test_provider_adapters.py::test_AC_2_copilot_adapter`)
- [x] **AC-3 (Happy Path - Antigravity Adapter):** `AntigravityProvider` mapea flags de capacidad (`allow_write`, `allow_terminal`) a `CapabilitiesConfig` y retorna la respuesta acumulada. (Verified by: `tests/test_provider_adapters.py::test_AC_3_antigravity_adapter`)
- [x] **AC-4 (Edge Case - Error Normalization):** Ante ausencia de librería o error de autenticación, los proveedores emiten `ProviderError` tipado y normalizado sin romper el hilo principal. (Verified by: `tests/test_provider_adapters.py::test_AC_4_error_normalization`)
- [x] **AC-5 (Boundary - Atomic Zero-History):** Invocaciones sucesivas de `chat_atomic` generan solicitudes independientes sin arrastrar el historial de turnos previos. (Verified by: `tests/test_provider_adapters.py::test_AC_5_atomic_zero_history`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Direct en módulo `scripts/harness/providers/`.
- **Production Rollback Plan:** Descartar rama `feat/windows-runner-provider-adapters` y volver a `main`.
- **Observability & SLI/SLO Telemetry:** Emisión de métricas de tiempo de inferencia y conteo de tokens en `AgentResponse.usage`.

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
