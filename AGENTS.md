# Project Constitution: AGENTS.md

## 1. Tech Stack & Environment
- **Project Purpose:** `k-method` - Enterprise-grade Karpathy 3-Layer Skills Pack v17 for Agentic SDLC.
- **Runtimes & Tooling:** Python 3.10+ (standard library only for OKF compiler), PowerShell / Bash, Git.
- **Standards:** Google Antigravity Skills & Anthropic Agent Skills specifications.
- **Skill Locations:** `.agents/skills/k-*` (Self-contained skills).

## 2. Available Execution Interfaces (CLI)
### Standard CLI Commands
- OKF Graph Lint & Recompile Index:
  ```bash
  python .agents/skills/k-wiki/scripts/okf-lint.py --compile-index
  ```
- Git Status Verification (Stash Shield check):
  ```bash
  git status --porcelain
  ```

## 3. Git Workspace Isolation, Stash Shield & Commit Traceability
- **Default Trunk:** `main`
- **Stash Shield:** Must verify working tree is clean (`git status --porcelain`) before creating task branches.
- **Branch Naming:** `feat/[feature-name]`, `fix/[bug-id]`, or `chore/[maintenance]`
- **Atomic Rollback Protocol:** `/task-abort` -> Return to base branch, delete task branch (`git branch -D`), and clean untracked artifacts (`git clean -fd`).
- **Commit Message Standard:**
  ```text
  <type>(<scope>): <summary>

  - Closes: [spec or issue reference]
  - Verified-By: [verification evidence or okf-lint]
  - Governed-By: [[ADR-XXX]]
  ```

## 4. Code Quality & SDLC Invariants
- **Self-Contained Skills:** Each skill in `.agents/skills/k-*` must be completely self-contained with its own `SKILL.md`, `scripts/`, `references/`, and `templates/`.
- **Frontmatter Schema:** Every `SKILL.md` must declare valid YAML frontmatter containing `name` and `description` matching the directory name.
- **Knowledge Base Integrity:** The OKF graph compiler (`.agents/skills/k-wiki/scripts/okf-lint.py`) must pass with zero broken links and valid frontmatter.
- **Zero Duplication (DRY):** No duplicate helper scripts or schemas across the repository.

## 5. Operational Permissions Taxonomy
### Always Do (Autonomous)
- Read documentation, templates, and skill markdown files.
- Switch to local feature/bugfix branches.
- Execute OKF lint and compilation commands (`python .agents/skills/k-wiki/scripts/okf-lint.py`).
- Inspect working tree state with `git status`.

### Ask First (Human Confirmation)
- Adding, renaming, or deprecating skills in `.agents/skills/`.
- Modifying public interfaces, constitution invariants, or architectural decision records (ADRs).
- Rebasing on updated upstream trunk.
- Remote git push and pull request creation.

### Never Do (Forbidden / Anti-Sabotage)
- **Modifying any file inside skill scripts (`.agents/skills/k-wiki/scripts/`) or `.agents/skills/` without explicit authorization.**
- Committing secrets, `.env` files, or private keys.
- Direct unstaged commits to trunk branch (`main`).
- Skipping failing validations or checks.
