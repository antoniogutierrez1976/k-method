---
name: k-orchestrator
description: >-
  End-to-end master state-machine orchestrator binding Spec, Verifier, Environment, and LLM-Wiki into an enterprise-grade SDLC software engineering pipeline. Dispatches isolated subagents with zero-history context windows across the full lifecycle: Stage 0 forensic triage (with telemetry log truncation), /bugfix routing, PR feedback loops (/iterate), /chore for routine maintenance bypass, Threat Modeling (OWASP), Visual Regression Testing (VRT), Stash Shield guards, Git branch isolation, atomic rollbacks (/task-abort), token budgeting, MCP tooling, Strangler Fig migrations, Golden Master snapshots, flaky test immunity (3x run), Negative Fault Injection, deadlock circuit breakers, ≥85% branch coverage gates, CI build & dependency audit sanity, Zero-Downtime Database Migration protocols, config & IaC drift checks, upstream staleness checks, full global regression runs, automated OKF graph compilation, Tooling Anti-Sabotage guards, and Pull Request artifact generation.
---

# Karpathy 3-Layer SDD Master Orchestrator (v16 Final Production Edition)

## Architecture Overview
Coordinates development according to Andrej Karpathy's 3 layers, hardened with ephemeral subagent isolation, deterministic local tooling, automated circuit breakers, flaky test elimination, workspace protection, and complete end-to-end SDLC lifecycle coverage:

```text
               ┌──────────────────────────────────────────────┐
               │    SUPERVISOR ORCHESTRATOR (State Machine)   │
               │      (Holds high-level state & gates only)   │
               └───────┬──────────────┬──────────────┬────────┘
                       │              │              │
        ┌──────────────┘              │              └──────────────┐
        ▼                             ▼                             ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ SUBAGENT: SPEC   │        │ SUBAGENT: TDD    │        │ SUBAGENT: RELEASE│
│ (Isolated Window)│        │ (Isolated Window)│        │ (Isolated Window)│
│ • Intent & Triage │        │ • Stash Shield   │        │ • OKF Schema     │
│ • /iterate (PR)  │        │ • Branch / Abort │        │ • Selective Ingest│
│ • /bugfix Router │        │ • Baseline Snap  │        │ • okf-lint       │
│ • /chore (Bypass)│        │ • Red -> Green   │        │   --compile-index│
│ • Threat Modeling│        │ • Circuit Breaker│        │ • PR Generation  │
│ • Sizing/Strangler│        │ • Flaky 3x Run   │        │   (pull-request. │
│ • Config & .env   │        │ • Mutation Test  │        │    template.md)  │
│ • Zero-Downtime DB│        │ • 85% Branch Cov │        │ • Halts & dies   │
│ • Release & SLOs  │        │ • UI VRT Snapshot│        └──────────────────┘
│ • Writes spec.md │        │ • IaC & .env Sync│
│ • Halts & dies   │        │ • Rebase & Regres│
└──────────────────┘        │ • Build & Audit  │
                            │ • Red-Team Audit │
                            │ • Halts & dies   │
                            └──────────────────┘
```

## Hardened Subagent Execution Pipeline across SDLC

### Stage 1: Intent Routing & Full-Lifecycle Spec Architect (`k-spec`)
- **Context:** Fresh session. Prompt + `AGENTS.md` + active OKF index.
- **Intent Fork:**
  - *Async Feedback Iteration:* Triggered by `/iterate`. Reads `pending-iteration.md`. Evaluates against original spec, logs amendment, and redispatches Verifier on existing branch.
  - *Routine Maintenance (`/chore`):* Bypasses Spec creation. Dispatches directly to Verifier on `chore/` branch for mechanical updates/linting fixes.
  - *Feature/Adaptation:* Bypasses Stage 0. Runs interview, sizing, identifies Threat Modeling (OWASP), configuration, database impact, release strategy, and SLOs.
  - *Brownfield Refactoring:* Scaffolds `characterization-spec.template.md` (Golden Master baseline).
  - *Radical Migration:* Scaffolds `migration-spec.template.md` (Strangler Fig).
  - *Opaque Bug / Incident:* Triggered by `/bugfix`. Triggers Stage 0 forensic triage (Truncates logs with CLI tools first). Routes to `specs/{feature}/bugs/BUG-{NNN}.md`.
- **Deliverable:** The `.md` specification artifact. Halts for human approval.

### Stage 2: Environment Governor & Workspace Isolation (`k-environment`)
- **Context:** Fresh session. Reads `AGENTS.md` and approved spec.
- **Actions:**
  - Auto-bootstraps environment if `AGENTS.md` is missing (`/init-environment` or `/constitution`).
  - Executes **Stash Shield** (`git status --porcelain` must be clean).
  - Activates branch isolation (`git checkout -b feat/[name]`, `fix/[id]`, or `chore/[name]`). Supports atomic rollback via `/task-abort`.
  - Configures compact test flags (`--bail`, `--onlyFailures`).
  - Runs OKF linter to assert initial graph validity.
  - Enforces **Tier 3 Tooling Protection**: Never edits files in `.tools/` or `.claude/skills/`.

### Stage 3: Verifier & Implementer (`k-verifier`)
- **Context:** Fresh session. Reads ONLY `AGENTS.md` + spec artifact.
- **Loop & Quality Gates:**
  1. *Baseline Snapshot:* For brownfield refactors, asserts Golden Master passes.
  2. *Red Phase:* Translates ACs (including Security ACs) to failing tests named `AC-X: [desc]`. Sets up Playwright Visual Regression Testing (VRT) for UI components (Checkpoint 1 `[x]`).
  3. *Green Phase & Circuit Breaker:* Writes minimal code. If 2 identical failures occur, breaker trips: stops edits, runs `git diff`, and escalates friction report. Confirms exit code 0 (Checkpoint 2 `[x]`).
  4. *Flaky Test Immunity:* If async/concurrency, asserts 3 out of 3 successful consecutive runs.
  5. *Negative Fault Injection:* Mutates domain logic to verify test sensitivity (Checkpoint 3 `[x]`).
  6. *Refactor Phase & Coverage Floor:* Cleans code under green guard; asserts ≥85% branch coverage on modified files (Checkpoint 4 `[x]`).
  7. *SemVer & Public Contract Check:* Confirms no unapproved exported contract changes.
  8. *Sync ACs with Matrix:* Updates `- [x] **AC-X** (Verified by: `[test-file.spec.ts::AC-X]`)` in the spec (Checkpoint 5 `[x]`).
  9. *Upstream Staleness & Global Regression:* Verifies branch freshness against origin/trunk; runs full test suite + typecheck with compact logs.
  10. *Production Build & Security Audit:* Executes `pnpm build` and `pnpm audit`. Confirms exit code 0 and zero high/critical vulnerabilities (Checkpoint 6 `[x]`).
  11. *Red-Team Audit:* Verifies absence of N+1 queries, unhandled async exceptions, PII leaks, syncs `.env.example` AND IaC manifests (Docker/Helm/Terraform), validates UI visual bounds, and verifies Zero-Downtime Database Migrations (Checkpoint 7 `[x]`).

### Stage 4: OKF Knowledge Compiler & PR Release Generator (`k-wiki` + `k-orchestrator`)
- **Context:** Fresh session. Reads completed spec + `SCHEMA.md`.
- **Actions:**
  - Selectively compiles ADRs / gotchas into `wiki/` with OKF frontmatter.
  - Executes `okf-lint.py --compile-index` to validate links and rebuild `wiki/index.md` deterministically.
  - Generates commit message per Commit Metadata Standard.
  - Generates Pull Request description from `templates/pull-request.template.md` incorporating verified AC evidence, release strategy, rollback plans, and observability alerts.
  - Marks Checkpoint 8 `[x]` in the spec.