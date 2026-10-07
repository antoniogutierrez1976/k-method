# Project Constitution: AGENTS.md

## 1. Tech Stack & Environment
- **Runtime & Language:** [e.g., Node 20+, TypeScript 5+, Python 3.12, Salesforce Apex/LWC]
- **Package Manager / CLI:** [e.g., pnpm / npm / sf cli]
- **Testing Framework:** [e.g., vitest / jest / pytest / playwright / sf apex run test]
- **Linters & Analyzers:** [e.g., eslint, prettier, ruff, sf scanner]

## 2. Available Execution Interfaces (CLI & MCP)
### Standard CLI Commands
- Build / Bundle: `pnpm build`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Full Test Suite (Compact output): `pnpm test --bail --reporter=compact`
- Visual Regression Test: `pnpm playwright test --update-snapshots` (UI only)
- Single Test: `pnpm test [path/to/test]`
- Test Coverage (≥85% Floor): `pnpm test --coverage`
- Dependency Security Audit: `pnpm audit`
- OKF Graph Lint & Compile: `python3 k-wiki/scripts/okf-lint.py --compile-index` (or relative to skill path: `python3 <skill-dir>/k-wiki/scripts/okf-lint.py --compile-index`)

### MCP Tools Mapped (if configured)
- Test Runner MCP: `[e.g., mcp__sfdx__runApexTests or mcp__playwright__runTest]`
- Database Inspector MCP: `[e.g., mcp__postgres__query]`

## 3. Git Workspace Isolation, Stash Shield & Commit Traceability
- Default Trunk: `main` (or `develop`)
- Stash Shield: Must verify `git status --porcelain` is clean before task branching.
- Working Branch: `feat/[feature-name]` or `fix/[bug-id]`
- Iteration / PR Feedback: Executed on the existing branch via `/iterate` reading `pending-iteration.md`.
- Rollback Command: `/task-abort` -> `git checkout main && git branch -D feat/[feature-name]`
- **Atomic Commit Message Standard:**
  ```text
  <type>(<scope>): <summary>

  - Closes: .specs/[feature-path]/spec.md (or specs/{feature}/bugs/BUG-{NNN}.md)
  - Verified-By: AC-1..AC-N passing under mutation injection
  - Governed-By: [[ADR-XXX]]
  ```

## 4. Code Quality, SDLC & Database Invariants
- **Branch Coverage Threshold:** 85% branch coverage required on new/modified domain logic.
- **Production Packaging Sanity:** `pnpm build` must pass cleanly with exit code 0.
- **Security Audit:** `pnpm audit` must report zero high/critical vulnerabilities.
- **Visual Regression (UI):** Frontend components must pass Golden Master visual snapshot comparisons.
- **Zero-Downtime Migrations:** Follow Expand & Contract protocol for schema changes.
- **Config & Environment Sync:** Any new environment variable must be added to `.env.example`.
- **Token Budgeting:** Compact test reporters required; no terminal dumps >60 lines.

## 5. Operational Permissions Taxonomy
### Always Do (Autonomous)
- Read code, documentation, and config files.
- Create and switch to local feature branches.
- Query wiki and run OKF compiler (`python3 k-wiki/scripts/okf-lint.py --compile-index`).
- Run tests, builds, visual regressions, audits, and coverage with compact output flags.

### Ask First (Human Confirmation)
- Adding or upgrading packages.
- Rebasing on updated trunk (`git rebase origin/main`).
- Modifying database migrations.
- Deleting files, modifying public contracts, or running mutating MCP tools.
- Remote git push and Pull Request creation.

### Never Do (Forbidden / Anti-Sabotage)
- **Modifying any file inside skill scripts (including `k-wiki/scripts/okf-lint.py`) or `.claude/skills/` / `.agents/skills/`.**
- Committing secrets, `.env` files, or private keys.
- Direct unstaged commits to trunk branches (`main`/`develop`).
- Skipping failing tests with `--no-verify` or `@ts-ignore`.
- Making changes beyond approved specification scopes.