# Pull Request: feat(harness): implement dual provider adapters for Copilot and Antigravity

## 1. Traceability & Context
- **Specification:** Closes `specs/k-windows-runner/01-provider-adapters/spec.md`
- **Governing Architecture:** Governed by `[[ADR-003-dual-sdk-execution-harness]]` and `[[ADR-001-karpathy-3-layer-architecture]]`
- **Git Branch:** `feat/windows-runner-provider-adapters` -> Target: `main`

## 2. Summary of Changes
- Se implementa la capa de abstracción desacoplada para proveedores de LLM con interfaz común `BaseAgentProvider` y fábrica `ProviderFactory`.
- Adaptador `CopilotProvider` basado en `github-copilot-sdk` con soporte para modelos OpenAI (GPT-6 Luna y Sol) y redacción de credenciales en logs/excepciones (`AC-Sec-1`).
- Adaptador `AntigravityProvider` basado en `google-antigravity` con mapeo de capacidades (`CapabilitiesConfig`).
- Adaptador `MockProvider` para pruebas unitarias deterministas sin conexión a red.
- Documentación de arquitectura en `ADR-003-dual-sdk-execution-harness.md` y re-compilación determinista del grafo OKF (`knowledge-base/wiki/index.md`).
- **Invariante Crítica:** 100% de los archivos existentes en `.agents/skills/` se preservan intactos sin modificaciones.

## 3. Ground Truth Verification Evidence
- [x] **Acceptance Criteria Verification:**
  - AC-Sec-1 passing: `tests/test_provider_adapters.py::test_AC_Sec_1_credential_redaction`
  - AC-1 passing: `tests/test_provider_adapters.py::test_AC_1_factory_and_mock`
  - AC-2 passing: `tests/test_provider_adapters.py::test_AC_2_copilot_adapter`
  - AC-3 passing: `tests/test_provider_adapters.py::test_AC_3_antigravity_adapter`
  - AC-4 passing: `tests/test_provider_adapters.py::test_AC_4_error_normalization`
  - AC-5 passing: `tests/test_provider_adapters.py::test_AC_5_atomic_zero_history`
  - Todas las casillas de la especificación sincronizadas al 100%.
- [x] **Negative Fault Injection (Mutation Testing):** Verificada la sensibilidad del test alterando `redact_secrets` (fallo inmediato asegurado).
- [x] **Flaky Test Immunity:** Pruebas asíncronas deterministas ejecutadas con aislamiento.
- [x] **Branch Coverage Floor:** ≥85% de cobertura de ramas alcanzada en los adaptadores.
- [x] **OKF Knowledge Base Lint:** `python .agents/skills/k-wiki/scripts/okf-lint.py --compile-index` ejecutado con éxito (8 nodos validados).
- [x] **Universal Quality Gates:** `python scripts/verify-all.py --skip-git-diff` ejecutado con éxito total.

## 4. Release Strategy & Operational Rollback Plan
- **Deployment Strategy:** Direct en módulo `scripts/harness/providers/` con dependencias opcionales en `requirements-harness.txt`.
- **Operational Rollback Procedure:**
  1. Revertir cambios en Git: `git checkout main && git branch -D feat/windows-runner-provider-adapters`.
- **Runtime Observability & Alerts:**
  - Normalización de errores en `ProviderError` con sanitización de credenciales.
