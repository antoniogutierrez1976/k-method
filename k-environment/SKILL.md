---
name: k-environment
description: Enforces Layer 3 (Environment) of Karpathy's method across the full SDLC. Scaffolds and governs AGENTS.md via the /constitution command. Manages automated bootstrapping (/init-environment), enforces Git branch/worktree isolation, dirty working tree protection (Stash Shield), atomic rollbacks (/task-abort), trunk staleness rebase guards, minimum 85% branch coverage gates, CI build sanity and dependency audit checks, Zero-Downtime Database Migration protocols, config/env drift prevention (including IaC Sync for Docker/Helm/Terraform), token budgeting, and deterministic OKF graph validation. Strictly protects skill scripts (including k-wiki/scripts/okf-lint.py) and .claude/skills/ / .agents/skills/ directories from tampering. Use when configuring projects, bootstrapping environments, running system commands, checking operational permissions, planning database migrations, retrieving prior decisions, aborting tasks, or inspecting environment policies.
---

# Environment Governance Protocol (Karpathy Layer 3: Environment)

## Objective
Guarantees predictable, reproducible execution across the entire SDLC: isolates changes in Git branches, eliminates context rot via strict token budgeting, enforces commit/PR traceability, verifies production builds, enforces Zero-Downtime DB Migrations, prevents config/IaC drift, and gates on 85% branch coverage.

## 1. Single Constitution Standard (`/constitution`)
- The project constitution is strictly and exclusively stored in **`AGENTS.md`** at the repository root.
- Never generate `CLAUDE.md`. Exclusively generate `AGENTS.md`.
- Upon command `/constitution` or missing environment, scaffold `AGENTS.md` from `templates/agents-constitution.template.md`.

## 2. Tooling & Skill Protection (Anti-Sabotage Rule)
- **Tier 3 (Never Do):** The agent is strictly forbidden from autonomously modifying, deleting, or attempting to "fix" any files inside skill scripts (including `k-wiki/scripts/okf-lint.py`) or `.claude/skills/` / `.agents/skills/` without explicit human confirmation. If a tool fails, fix the domain code or the OKF markdown node, never the tooling itself. Process improvements to skills require explicit Tier 2 human authorization.

## 3. Workspace Isolation, Stash Shield & Atomic Rollback Protocol
- **Stash Shield:** Verify `git status --porcelain` before branching. If dirty, stash (`git stash push -u -m "pre-task-checkpoint"`) or prompt user.
- **Branch Convention:** `git checkout -b feat/[name]`, `fix/[bug-id]`, or `chore/[maintenance]`.
- **Atomic Rollback (`/task-abort`):** Revert to previous branch and delete aborted branch (`git branch -D`). Clean untracked files (`git clean -fd`).

## 4. Trunk Staleness & Rebase Guard
- Check upstream divergence (`git fetch origin [base-branch]`). If new commits exist, trigger Tier 2 request for `git rebase origin/[base-branch]`.

## 5. Quality, CI Build & Package Security Gates
- **Branch Coverage Floor (≥85%):** Domain modules must achieve ≥85% branch coverage.
- **Production Build Sanity:** Always execute production compilation (e.g., `pnpm build`) to ensure bundle integrity.
- **Dependency Security Audit:** Execute package vulnerability scanner (e.g., `pnpm audit`). High/Critical vulnerabilities block completion.
- **Config & IaC Drift Guardian:** Sync new environment variables to `.env.example`, `spec.md`, and any associated Infrastructure as Code (IaC) manifests (e.g., `docker-compose.yml`, Helm values, Terraform).

## 6. Zero-Downtime Database Migration Protocol
- Follow Expand & Contract (`references/zero-downtime-db-migrations.md`). No destructive schema ops in the same phase as app changes.

## 7. Token Budgeting & OKF Compilation
- Test commands must append compact flags (`--bail`, `--reporter=compact`).
- Always invoke `python3 k-wiki/scripts/okf-lint.py --compile-index` deterministically.

## 8. Three-Tier Permission Taxonomy
- **Tier 1 (Always Do):** Read code/specs, switch branches, run tests/linters (compact), run OKF compiler, stash checks.
- **Tier 2 (Ask First):** Add packages, run DB migrations, rebase trunk, alter public contracts, MCP mutating calls, PR creation, modify skills/tooling under explicit human confirmation.
- **Tier 3 (Never Do):** Autonomous modification of skill scripts (`k-wiki/scripts/`) or `.claude/skills/` / `.agents/skills/`, commit secrets, commit to trunk, skip tests.