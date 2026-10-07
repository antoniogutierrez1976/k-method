# Spec: Multi-Platform Quality Gates & Universal Runner

## 1. Goal & Context
- **Business Rationale:** Permitir que los equipos utilicen `k-method` de forma estandarizada y segura con independencia de su plataforma de repositorio o CI/CD (Bitbucket On-Premise, Bitbucket Cloud, Azure DevOps, GitHub Actions o desarrollo local offline), eliminando el bloqueo a un proveedor específico.
- **User Story:** Como ingeniero/mantenedor de `k-method`, quiero un comando de verificación universal y plantillas de CI/CD para las 4 plataformas soportadas para garantizar que todas las skills y el grafo OKF se validen de forma idéntica en cualquier entorno.
- **Git Branch Target:** `feat/multi-platform-quality-gates`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
- [x] **OOS-1:** No introducir paquetes externos o dependencias vía `pip` ni `npm` (se mantiene estrictamente en Python 3.10+ standard library).
- [x] **OOS-2:** No modificar los scripts dentro de `.agents/skills/` (protección nivel 3 de tooling).
- [x] **OOS-3:** No forzar la subida ni commits de secretos ni tokens de CI/CD.

## 3. Technical Contract & Architecture
- **Universal Runner Script:** `scripts/verify-all.py`
  - Función principal: `main() -> int`
  - Comprobaciones ejecutadas secuencialmente:
    1. `tests`: Ejecuta `unittest discover -s tests -v`
    2. `okf-lint`: Ejecuta `.agents/skills/k-wiki/scripts/okf-lint.py --compile-index`
    3. `git-diff`: Ejecuta `git diff --exit-code` para asegurar ausencia de deriva en el working tree.
  - Salida: Resumen estructurado por consola y código de retorno `0` (éxito total) o `1` (fallo de cualquier compuerta).
  - CLI Flags soportados: `--skip-git-diff` (para entornos o contenedores donde no esté inicializado Git).
- **CI Templates Directory:** `templates/ci/`
  - `templates/ci/bitbucket-pipelines.template.yml` (Bitbucket Cloud)
  - `templates/ci/azure-pipelines.template.yml` (Azure DevOps)
  - `templates/ci/github-ci.template.yml` (GitHub Actions)
  - `templates/ci/git-pre-push.template.sh` (Hook Git local para Bitbucket On-Premise / Local)

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:** Ejecución de código malicioso mediante runners no confiables, fuga de variables de entorno en logs de CI, permisos excesivos en tokens de CI, bypass de puertas de calidad en entornos on-premise sin pipelines automáticos.
- **Security Acceptance Criteria:**
  - [x] **AC-Sec-1:** Todas las plantillas de CI/CD declaran mínimos privilegios (solo lectura de contenidos o tokens restringidos) y no exponen variables de entorno sensibles en logs. (Verified by: `tests/test_ci_templates.py::test_AC_Sec_1_least_privilege_and_no_secrets`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
- [x] **AC-Sec-1:** Las plantillas de CI (`github-ci`, `azure-pipelines`, `bitbucket-pipelines`) aplican principio de mínimos privilegios y no registran secretos. (Verified by: `tests/test_ci_templates.py::test_AC_Sec_1_least_privilege_and_no_secrets`)
- [x] **AC-1 (Universal Runner CLI):** `scripts/verify-all.py` ejecuta unit tests, linter OKF y chequeo Git diff, retornando 0 sólo si todos pasan y 1 ante cualquier fallo. (Verified by: `tests/test_verify_all_runner.py::test_AC_1_runner_executes_successfully`)
- [x] **AC-2 (Bitbucket Pipelines Template):** `templates/ci/bitbucket-pipelines.template.yml` define pasos válidos con imagen estándar de Python para Bitbucket Cloud. (Verified by: `tests/test_ci_templates.py::test_AC_2_bitbucket_pipelines_template`)
- [x] **AC-3 (Azure DevOps Pipeline Template):** `templates/ci/azure-pipelines.template.yml` define un pipeline válido con `UsePythonVersion@0` y ejecución del runner universal. (Verified by: `tests/test_ci_templates.py::test_AC_3_azure_pipelines_template`)
- [x] **AC-4 (GitHub Actions Template):** `templates/ci/github-ci.template.yml` define workflow multiplataforma con permisos `contents: read` explícitos. (Verified by: `tests/test_ci_templates.py::test_AC_4_github_actions_template`)
- [x] **AC-5 (Local Git Pre-Push Hook):** `templates/ci/git-pre-push.template.sh` es un script POSIX ejecutable que invoca `scripts/verify-all.py` antes de permitir `git push`. (Verified by: `tests/test_ci_templates.py::test_AC_5_git_pre_push_hook_template`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** Direct merge a `main` tras validación completa del ciclo TDD y suite global.
- **Production Rollback Plan:** Revertir la rama mediante `git revert` sin impacto en las skills existentes.
- **Observability & SLI/SLO Telemetry:**
  - Salida formateada con marcas de tiempo en el runner `scripts/verify-all.py`.
  - Reporte de estado en el log de ejecución de cada plataforma de CI.

## 7. Execution Checkpoints
- [x] Checkpoint 1: Automated tests committed in failing (Red) state.
- [x] Checkpoint 2: Minimal domain logic implemented (Green state).
- [x] Checkpoint 3: Negative Fault Injection (Mutation Test) passed.
- [x] Checkpoint 4: Refactored logic clean with tests maintaining Green state and ≥85% branch coverage.
- [x] Checkpoint 5: All Acceptance Criteria validated in terminal and marked `[x]` with test identifier.
- [x] Checkpoint 6: Full global regression passes cleanly.
- [x] Checkpoint 7: Adversarial review passed, and all OOS negative constraints in Section 2 audited and marked `[x]`.
- [x] Checkpoint 8: Selective OKF compilation completed and Pull Request description generated.

## 8. Amendment Log
- 2026-10-07: Generalizada la especificación desde GitHub Actions hacia una arquitectura agnóstica multi-plataforma soportando Bitbucket On-Premise, Bitbucket Cloud, Azure DevOps y GitHub Actions con runner universal `scripts/verify-all.py`.
