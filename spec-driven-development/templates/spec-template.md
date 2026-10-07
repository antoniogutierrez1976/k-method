# Spec: [Feature Name]

## 1. Goal & Context
- **Business Rationale:** What capability or business metric is unlocked?
- **User Story:** As a `[role]`, I want to `[action]` so that `[benefit]`.
- **Git Branch Target:** `feat/[feature-name]` or `fix/[feature-name]`

## 2. Boundaries & Out-of-Scope (OOS)
The implementation must explicitly NOT:
<!-- Every OOS negative constraint must be verified via static analysis/review and marked [x] before PR merge -->
- [ ] **OOS-1:** [Specific related feature/refactor excluded from this ticket]
- [ ] **OOS-2:** [Changes to third-party modules or external contracts]

## 3. Technical Contract & Architecture
- **Data Models / Schemas:**
  ```typescript
  // Interface contracts or schema types
  ```
- **Endpoints / Signatures:**
  - Method / Function: `name(params): ReturnType`
  - HTTP Endpoint (if applicable): `METHOD /path`
- **Environment & Configuration Variables:**
  - `ENV_VAR_NAME`: [Description and default dummy value in .env.example]
- **Zero-Downtime Data Migration Phase (if applicable):**
  - Phase: `[Expand / Dual-Write / Backfill / Switch / Contract / None]`

## 4. Security & Threat Modeling (Shift-Left Security)
- **Threat Vectors Analyzed:** [e.g., IDOR on user records, SQLi on search, Rate Limiting on login, SSRF on webhooks]
- **Security Acceptance Criteria:**
  <!-- Security criteria must be numbered AC-Sec-1..N and tracked in the unified matrix in Section 5 below -->
  - [ ] **AC-Sec-1:** [e.g. Unauthenticated user receives 401 Unauthorized] (Verified by: `tests/path.spec.ts::AC-Sec-1`)

## 5. Verifiable Acceptance Criteria (Bidirectional Traceability Matrix)
<!-- Unified traceability matrix: Every AC (including AC-Sec) must be verified and marked [x] with test identifier -->
- [ ] **AC-Sec-1:** [Security criterion mirrored from Section 4] (Verified by: `tests/path.spec.ts::AC-Sec-1`)
- [ ] **AC-1 (Happy Path):** Given `[precondition]`, when `[action]`, then `[expected output/state]`. (Verified by: `tests/path.spec.ts::AC-1`)
- [ ] **AC-2 (Edge Case):** Given invalid `[input]`, when processed, system throws/returns `[specific error]`. (Verified by: `tests/path.spec.ts::AC-2`)
- [ ] **AC-3 (Boundary):** Handled empty collections, nulls, and maximum payloads deterministically. (Verified by: `tests/path.spec.ts::AC-3`)

## 6. Release Strategy, Rollback & Observability Contract
- **Release Strategy:** `[Direct / Feature Flag: FLAG_NAME / Canary]`
- **Production Rollback Plan:** [Step-by-step mitigation if runtime failure occurs post-deploy]
- **Observability & SLI/SLO Telemetry:**
  - Metrics emitted: `[e.g. Counter discount_calculation_total, Histogram calculation_duration_ms]`
  - Error alert condition: `[e.g. Failure rate > 0.5% over 5m window]`

## 7. Execution Checkpoints
- [ ] Checkpoint 1: Automated tests committed in failing (Red) state. (Includes Visual Regression baselines if UI).
- [ ] Checkpoint 2: Minimal domain logic implemented (Green state).
- [ ] Checkpoint 3: Negative Fault Injection (Mutation Test) passed: deliberately altered logic causes test failure.
- [ ] Checkpoint 4: Refactored logic clean with tests maintaining Green state and ≥85% branch coverage.
- [ ] Checkpoint 5: All Acceptance Criteria (including Security AC-Sec in Sections 4 and 5) validated in terminal and marked `[x]` with test identifier.
- [ ] Checkpoint 6: Full global regression, production build (`pnpm build`), and security audit (`pnpm audit`) pass cleanly.
- [ ] Checkpoint 7: Adversarial review (anti-N+1, side-effects, privacy leaks, .env sync, IaC sync, zero-downtime DB, UI bounds) passed, and all OOS negative constraints in Section 2 audited and marked `[x]`.
- [ ] Checkpoint 8: Selective OKF compilation completed and Pull Request description generated (`pull-request.template.md`). (Zero unchecked `[ ]` boxes remaining in spec).

## 8. Amendment Log (Populated only if technical discovery forces spec changes)
<!-- Example:
- YYYY-MM-DD: Modified AC-2 to accept 422 Unprocessable Entity instead of 400 Bad Request due to validation library constraints. Approved by user.
-->