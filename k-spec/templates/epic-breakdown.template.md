# Epic Breakdown: [System/Epic Name]

## 1. Executive Summary
- **Overall Goal:** What high-level capability does the complete system deliver?
- **Total Architectural Scope:** [e.g., Database, Services, APIs, UI, Observability]

## 2. Decomposition into Sequential Slices (Milestones)

Each slice represents an autonomous, verifiable sub-feature that can execute through its own Karpathy 3-layer cycle:

### Phase 1: [Sub-Feature Name: e.g., Core Domain & Persistence]
- **Target Spec:** `.specs/[epic-name]/01-[feature-name]/spec.md`
- **Scope:** Pure data models, persistence contracts, unit tests.
- **Out-of-Scope for Phase 1:** API routing, client UI, external webhooks.
- **Verification Gate:** Fast unit/integration tests green with zero external mocks.

### Phase 2: [Sub-Feature Name: e.g., Business Logic & Service API]
- **Target Spec:** `.specs/[epic-name]/02-[feature-name]/spec.md`
- **Scope:** Application services, authorization, validation, HTTP endpoints.
- **Out-of-Scope for Phase 2:** Frontend screens, client SDKs.
- **Verification Gate:** API contract tests pass (200/400/401/500 scenarios).

### Phase 3: [Sub-Feature Name: e.g., Frontend & User Experience]
- **Target Spec:** `.specs/[epic-name]/03-[feature-name]/spec.md`
- **Scope:** Components, state store integration, error feedback.
- **Verification Gate:** Component unit tests & Playwright E2E happy-path.

## 3. Recommended Immediate Action
- Approve this breakdown to lock the architectural boundary.
- Generate Phase 1 spec immediately.