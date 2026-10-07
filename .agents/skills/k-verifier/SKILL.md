---
name: k-verifier
description: Implements Layer 2 (Verifier) of Karpathy's method. Executes full Red-Green-Refactor TDD cycle, characterization testing for brownfield legacy, Visual Regression Testing (VRT) for UI components via Playwright golden master snapshots, Negative Fault Injection (Mutation Testing) to defeat vacuous tests, stochastic 3x repetition to eliminate flaky tests, minimum 85% branch coverage verification, deadlock circuit breakers (hard abort after 2 identical failures with diff dump), production build and dependency security audit sanity gates, Zero-Downtime Database Migration checks, SemVer contract drift detection, compact regression suites, MCP tooling, and Red-Team adversarial audits (including Infrastructure as Code drift checks).
---

# Karpathy Verifier Protocol (Karpathy Layer 2: Verifier)

## Objective
Anchors verification in ruthless objective Ground Truth: automated compilers, test runners, mutation injection, snapshot baselines, visual regression tests for UIs, branch coverage floors, production build sanity, dependency audits, flaky test immunity, and adversarial Red-Team critique including IaC sync.

## Verification Protocol: The Industrial Hardened Loop

### 0. Brownfield / Refactoring Baseline (Characterization Testing)
When refactoring legacy code without comprehensive pre-existing tests:
- Elicit and scaffold `characterization-spec.template.md`.
- Capture inputs/outputs into a Golden Master snapshot (`.snapshot.json`).
- Ensure the snapshot test is 100% Green before refactoring begins.

### 1. Test-First Grounding (Red Phase)
- Translate every Acceptance Criterion (including Threat Modeling AC-Sec) from `spec.md` into an executable automated test: `it('AC-1: [description]', ...)`
- **For UI / Frontend Components (VRT):** Initialize Visual Regression Testing (e.g., Playwright Golden Master Visuals) to ensure elements render inside bounds.
- Execute tests via CLI runner (compact flag) or configured MCP tool. Confirm failure (Checkpoint 1 `[x]`).

### 2. Minimal Implementation & Deadlock Circuit Breaker (Green Phase)
- Implement minimal viable code to turn failing tests green.
- **Deadlock Circuit Breaker Guardrail:**
  - If the test runner fails with the **same error or assertion 2 consecutive times**, the subagent MUST NOT attempt a third speculative edit.
  - **Action:** Abort code edits, execute `git diff`, and output a **Friction Escalation Report** with 2 architectural alternatives.
- Confirm exit code 0. Mark Checkpoint 2 as `[x]`.

### 3. Flaky Test Immunity Pass (Stochastic 3x Run)
- If the test touches asynchronous logic, timeouts, network mocks, date/time, or concurrency:
  - Execute the test suite 3 consecutive times (`python -m unittest` 3x or `pnpm test --repeat=3`).
  - **PASS CRITERIA:** 3 out of 3 runs must return exit code 0.

### 4. Negative Fault Injection Pass (Mutation Resistance Check)
- Deliberately mutate newly written domain logic. Re-run test suite.
- **PASS:** The test MUST FAIL. Proves sensitivity to domain errors. Mark Checkpoint 3 as `[x]`.
- Revert temporary mutation back to Green state.

### 5. Dedicated Refactor Phase & Branch Coverage Gate (≥85%)
- Modularize and clean code. Execute coverage runner (`coverage run -m unittest` / `pytest --cov` or `pnpm test --coverage`). Verify ≥85% branch coverage on modified domain files (Checkpoint 4 `[x]`).

### 6. SemVer & Public Contract Drift Guardian
- Verify no exported signatures, schemas, or API contracts were broken without an approved Spec Amendment.

### 7. Synchronize Acceptance Criteria with Test Matrix
- Update spec: `- [x] **AC-X** (Verified by: `[test-file.spec.ts::AC-X]`)`.
- **Full Security Sync:** Ensure all Security Acceptance Criteria (in both Section 4 Threat Modeling and Section 5 Verifiable ACs) are synchronized and marked `[x]` with test identifiers. Mark Checkpoint 5 as `[x]`.

### 8. Upstream Staleness, Production Build & Global Regression
- Verify local branch is not stale against upstream (`git log HEAD..origin/[main]`).
- Run full repository test suite + typecheckers + linters:
  - Universal Quality Gates Runner: `python scripts/verify-all.py`
  - Automated Unit Tests: `python -m unittest discover -s tests -v`
- **Production Build Sanity Check:** Execute production compilation command (`pnpm run build` in `desktop/` or Python build).
- **Dependency Security Audit:** Execute dependency scanner (`pnpm audit` / `pip-audit`). Assert zero high/critical vulnerabilities. Mark Checkpoint 6 as `[x]`.

### 9. Adversarial Red-Team Audit Pass (Side-Effects, Privacy, IaC Config, UI & DB Migrations)
- Act as an antagonistic Red-Team auditor:
  - **Boundaries & OOS Audit:** Verify via static analysis (`git grep`, dependency audits) that all negative constraints in Section 2 (`OOS-1..N`) were strictly respected, and mark each `[x]`.
  - **Side-Effects:** Check for N+1 queries, unhandled promises, transaction rollbacks.
  - **Visual/UI:** Confirm Golden Master Visuals match and responsive bounds are respected.
  - **Privacy:** Verify absence of secrets or PII in loggers.
  - **Config & IaC Drift:** Confirm `.env.example` sync AND ensure associated Infrastructure as Code manifests (Docker, Helm, Terraform) are updated with new environment variables.
  - **Zero-Downtime DB Check:** Confirm compliance with Expand & Contract. Mark Checkpoint 7 as `[x]`.
  - **Zero Unchecked Box Gate:** Assert that 100% of markdown checkboxes in `spec.md` are marked `[x]`. Closing a task or merging with pending `[ ]` boxes is strictly prohibited. Mark Checkpoint 8 as `[x]`.