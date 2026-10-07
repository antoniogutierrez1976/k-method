# Pull Request: feat(gui) - Phase 1: GUI Backend API & Embedded Skills Registry

- **Closes:** #k-windows-gui (Phase 1)
- **Governed-By:** [[ADR-004-antigravity-gui-and-embedded-skills]]
- **Verified-By:** `python scripts/verify-all.py` (51 unit tests passing, OKF graph clean)

---

## 1. Summary of Changes

### Encapsulated Skills Pattern
- Created [embedded_skills.py](file:///d:/dev/k-method/scripts/harness/engine/embedded_skills.py) containing the complete canonical system directives for all 5 core Karpathy v0 skills (`k-orchestrator`, `k-spec`, `k-verifier`, `k-environment`, `k-wiki`).
- Integrated dynamic context injection into [state_machine.py](file:///d:/dev/k-method/scripts/harness/engine/state_machine.py), eliminating the requirement of having `.agents/skills/` on target workspaces and reserving methodology use to the application.

### ASGI Backend & WebSocket Streaming
- Created [server.py](file:///d:/dev/k-method/scripts/harness/gui/server.py) providing:
  - `GET /api/status`: Real-time workspace branch and Stash Shield state.
  - `GET /api/diff`: Live git diff output.
  - `GET /api/skills`: Catalog of embedded Karpathy skills.
  - `WebSocket /ws/sdlc`: Real-time bidirectional streaming of SDLC stages, tokens, approval requests, and TDD outputs.
- Comprehensive security redaction via `redact_secrets()` on all emitted REST and WebSocket payloads.

---

## 2. Acceptance Criteria Verification

- [x] **AC-Sec-1:** Secret redaction on all WebSocket and REST payloads (`test_AC_Sec_1_credential_redaction_in_api`).
- [x] **AC-1:** Embedded skills registry provides complete Karpathy v0 directives in memory (`test_AC_1_embedded_skills_registry`).
- [x] **AC-2:** REST endpoints return workspace status, git diff, and skills catalog (`test_AC_2_rest_endpoints`).
- [x] **AC-3:** WebSocket `/ws/sdlc` streams lifecycle events (`test_AC_3_websocket_execution_protocol`).
- [x] **AC-4:** Interactive approval gate via WebSocket (`test_AC_4_interactive_approval_gate_via_ws`).
- [x] **AC-5:** Disconnect & error resilience (`test_AC_5_disconnect_and_error_resilience`).
