# Migration Spec: [System/Subsystem Name] (Strangler Fig / Expand & Contract)

## 1. Context & Motivation
- **Legacy Architecture:** What component/system is being phased out and why?
- **Target Architecture:** What is the replacement design and its technical benefits?
- **Associated ADR:** `[[ADR-XXX-[title]]]` (Mandatory architectural decision recorded in wiki).

## 2. Phase 1: EXPAND (Parallel Coexistence)
- **Objective:** Build the new implementation in parallel without altering or breaking existing legacy contracts.
- **New Path/Namespace:** `[e.g., src/v2/ or NewServiceImplementation]`
- **Invariants:**
  - [ ] Legacy code paths remain completely untouched.
  - [ ] Zero breaking changes to public consumers.
  - [ ] 100% of pre-existing test suites remain green.
- **Acceptance Criteria for Phase 1:**
  - [ ] AC-1: New component implemented under isolated unit tests.
  - [ ] AC-2: New component passes contract validation tests against expected inputs.

## 3. Phase 2: SWITCH (Consumer Rerouting)
- **Objective:** Atomically migrate caller entrypoints from legacy to the new implementation.
- **Entrypoints to Reroute:** `[List controllers, UI components, background jobs, trigger handlers]`
- **Acceptance Criteria for Phase 2:**
  - [ ] AC-1: Entrypoints route payloads to the new implementation.
  - [ ] AC-2: Integration tests pass with active traffic flowing through the new implementation.
  - [ ] AC-3: Fallback / feature-flag switch verification (if applicable).

## 4. Phase 3: CONTRACT (Legacy Deletion & Garbage Collection)
- **Objective:** Safely prune dead legacy code, obsolete dependencies, and deprecated tests.
- **Files to Remove:** `[List legacy classes, tables, routes]`
- **Acceptance Criteria for Phase 3:**
  - [ ] AC-1: Dead files deleted without broken imports.
  - [ ] AC-2: Full project regression and typecheck cleanly pass exit code 0.
  - [ ] AC-3: Mark legacy node in `knowledge-base/wiki/` as `status: deprecated` (OKF standard).