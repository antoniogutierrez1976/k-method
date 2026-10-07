# k-method: Karpathy 3-Layer Skills Pack (WIP)

> [!NOTE]
> **Status:** Work In Progress (WIP) — Active Development. There is no released or in-flight production version yet.

Enterprise-grade SDLC software engineering pipeline based on Andrej Karpathy's 3 layers (Spec, Verifier, Environment) + LLM-Wiki knowledge graph. Fully compliant with Anthropic's **"The Complete Guide to Building Skills for Claude"** and Google Antigravity Agent Skills standards.

## Skills Included (`k-*`)

| Skill | Directory | Layer / Role | Description |
| :--- | :--- | :--- | :--- |
| **`k-orchestrator`** | [`.agents/skills/k-orchestrator/`](file:///d:/dev/k-method/.agents/skills/k-orchestrator/SKILL.md) | **Master Orchestrator** | State-machine supervisor dispatching ephemeral subagents across the complete SDLC pipeline. |
| **`k-spec`** | [`.agents/skills/k-spec/`](file:///d:/dev/k-method/.agents/skills/k-spec/SKILL.md) | **Layer 1: Spec** | Intent classification (`/bugfix`, `/chore`, `/iterate`), 6-AC hard limit, OWASP Threat Modeling. |
| **`k-verifier`** | [`.agents/skills/k-verifier/`](file:///d:/dev/k-method/.agents/skills/k-verifier/SKILL.md) | **Layer 2: Verifier** | Red-Green-Refactor, mutation testing, flaky 3x pass, circuit breaker, ≥85% branch coverage, VRT. |
| **`k-environment`** | [`.agents/skills/k-environment/`](file:///d:/dev/k-method/.agents/skills/k-environment/SKILL.md) | **Layer 3: Environment** | `AGENTS.md` constitution, Stash Shield, Git branch isolation, atomic rollback, IaC & `.env` sync. |
| **`k-wiki`** | [`.agents/skills/k-wiki/`](file:///d:/dev/k-method/.agents/skills/k-wiki/SKILL.md) | **Knowledge Graph** | Open Knowledge Format (OKF) engine, typed frontmatter, ADR lifecycle, [`.agents/skills/k-wiki/scripts/okf-lint.py`](file:///d:/dev/k-method/.agents/skills/k-wiki/scripts/okf-lint.py) compiler. |


## Core Evolutions & Hardened Protocols
1. **Strict Epic Detection (The 6-AC Rule):** Enforces a hard limit of 6 Acceptance Criteria per spec, forcing the LLM to decompose high-context functional requirements into multi-spec Epic roadmaps.
2. **Shift-Left Security & Threat Modeling:** Enforces OWASP threat vector analysis and specific Security Acceptance Criteria (AC-Sec) in all new specifications.
3. **Routine Maintenance Bypass (`/chore`):** Dedicated workflow for dependency bumps and minor refactors that skips heavy spec generation and goes straight to global regression validation.
4. **Infrastructure as Code (IaC) Sync:** Extends environment drift prevention by ensuring `.env` changes are automatically propagated to Docker, Kubernetes (Helm), or Terraform manifests.
5. **Structured Telemetry Ingestion (Noise Reduction):** Mandates CLI-based log truncation (`grep`, `jq`) during Stage 0 Forensic Triage to prevent context window saturation from raw Sentry/Datadog dumps.

## Full Feature Set (SDLC Complete):
- **Pull Request & Release Artifact Generator:** Compiles PR bodies with AC ground-truth evidence, rollback instructions, and observability alerts.
- **Async PR Feedback Loop (`/iterate`):** Formal support for asynchronous GitHub code review feedback via `pending-iteration.md`.
- **Production Build & Dependency Security Audit:** Formal verification checkpoint (`pnpm build` & `pnpm audit`).
- **Visual Regression Testing (VRT):** Native checkpoints for Playwright Golden Master Visuals, protecting UI bounds.
- **Forensic Bug Routing (`/bugfix`):** Strict isolation of maintenance patches (`specs/{feature}/bugs/BUG-{NNN}.md`).
- **Zero-Downtime Database Migration Protocol:** Expand & Contract for persistence models.
- **Release Strategy, Rollback & Observability SLO Contracts:** Enriched spec templates for operational readiness.
- **Robust Multi-line YAML Parser in `k-wiki/scripts/okf-lint.py`:** Dependency-free YAML parsing for OKF graphs.
- **Branch Coverage Floor (≥85%):** Strict gating on modified domain logic.
- **Stash Shield & Atomic Rollback Protocol (`/task-abort`):** Guards against dirty working trees.
- **Config & Environment Drift Prevention:** Automatic `.env.example` and IaC sync.
- **Trunk Staleness & Rebase Guard:** Validates upstream divergence before regression.
- **Tooling Anti-Sabotage Rule:** Explicitly prohibits agents from modifying skill scripts (`k-wiki/scripts/`) or `.claude/skills/` / `.agents/skills/`.
- **Self-Contained OKF Compiler Tool:** Auto-contained within `k-wiki/scripts/` to eliminate root collisions and ensure skill portability.
- **Environment Auto-Bootstrapping (`/init-environment` & `/constitution`):** Single-step initialization of `AGENTS.md` and `knowledge-base/`.
- **Flaky Test Immunity Pass (Stochastic 3x Run):** 3 consecutive executions for async/timing tests.
- **Bidirectional Traceability Matrix:** Links AC checkboxes to test identifiers.
- **Deadlock Circuit Breaker:** Stops infinite loops after 2 identical failures with diff output.
- **Characterization Testing (Golden Master Snapshots):** Baseline captures before brownfield refactors.
- **Red-Team Adversarial Audit:** Antagonistic check against N+1 queries, unhandled async exceptions, and PII leaks.
- **Token Budgeting & Output Filtering:** Enforces compact test logs (`--bail`).
- **SemVer & Public Contract Guardian:** Automated protection for shared interfaces.
- **Commit Metadata Grounding Standard:** Standardized commit messages linking to specs and ADRs.
- **Open Knowledge Format (OKF):** Typed YAML frontmatter with lifecycle states (`active`, `deprecated`, etc.).
- **Negative Fault Injection (Mutation Testing):** Defeats the "vacuous / tautological test" syndrome.
- **Workspace Isolation (Git Branches / Worktrees):** Enforces dedicated branches for atomic rollbacks.
- **Tooling Ground Truth (CLI & MCP):** Native Model Context Protocol (MCP) support.
- **Strangler Fig / Expand & Contract Template:** Breaking changes without downtime.
- **Subagent Context Isolation:** Master supervisor state machine with zero-history context windows.

## Graphical & CLI Tools

The repository provides both an interactive Graphical Webview (**k-method app**, replicating Antigravity 2.0 3-column layout) and deterministic CLI tools implementing the **"Code > Prompt"** pattern.

### 1. k-method app Graphical Studio (`run-gui.ps1` / `scripts/harness/gui/launch.py`)

A modern, dark-mode 3-column desktop/browser application (**k-method app**):
- **Left Sidebar:** Workspace selector, LLM provider & model switcher, and embedded Karpathy v0 skills catalog.
- **Central Chat Canvas:** Real-time token streaming, state badge progression, and human-in-the-loop spec approval action bar.
- **Right Auxiliary Pane:** Tabbed views for *Artifacts* (`spec.md` & PR description), *Files Changed* (live Git diff), *TDD Verifier* (test logs), and *OKF Graph*.

```powershell
# Launch k-method app (auto-opens browser at http://127.0.0.1:8000):
.\run-gui.ps1

# Custom port or headless background mode:
.\run-gui.ps1 -Port 8080 -NoBrowser

# Compile as a Standalone Windows Executable (dist/k-method-studio.exe):
.\scripts\build\build-exe.ps1
```

---

### 2. Interactive Windows Skills Runner CLI (`k_runner.py` / `run-harness.ps1`)

An interactive terminal application with Antigravity-style ANSI visual presentation (header banners, auxiliary status panels, human approval gates, and deadlock circuit breaker alerts).

```powershell
# 🏢 Professional Mode (GitHub Copilot SDK + OpenAI GPT-6 Luna / Sol):
.\run-harness.ps1 -Provider copilot -Model gpt-6-luna -Task "Implement metrics endpoint"

# 🏠 Personal Mode (Google Antigravity SDK + Gemini):
.\run-harness.ps1 -Provider antigravity -Model gemini-3.8-flash -Task "Refactor database client"

# 🧪 Offline / Mock Mode (Automated CI):
python scripts/harness/k_runner.py --provider mock --task "Test pipeline" --auto-approve
```

#### CLI Options & Flags:

| Flag | Env Variable | Default | Description |
| :--- | :--- | :--- | :--- |
| `--provider` | `K_HARNESS_PROVIDER` | `copilot` | Provider adapter: `copilot`, `antigravity`, or `mock`. |
| `--model` | `K_HARNESS_MODEL` | `gpt-6-luna` / `gemini-3.8-flash` | Target model identifier. |
| `--task` | — | *(Prompt)* | Description of task (prompts interactively if omitted). |
| `--auto-approve` | — | `False` | Bypasses interactive spec approval gate (for CI/CD). |
| `--branch` | — | `feat/{slug}` | Explicit Git task branch name. |

---

### 2. Universal Quality Gates Runner (`verify-all.py`)

A platform-agnostic, all-in-one verification runner that executes all quality gates sequentially:

```bash
# Standard run (Unit tests + OKF lint + Stash Shield git diff check):
python scripts/verify-all.py

# Recompile the OKF index and run checks:
python scripts/verify-all.py --compile-index

# Skip git diff check (e.g. while editing in local development):
python scripts/verify-all.py --skip-git-diff
```

---

### 3. OKF Knowledge Graph Linter & Compiler (`okf-lint.py`)

Deterministic compiler and validator for Open Knowledge Format (OKF) nodes:

```bash
# Lint knowledge graph integrity and check for broken links:
python .agents/skills/k-wiki/scripts/okf-lint.py

# Recompile knowledge-base/wiki/index.md deterministically:
python .agents/skills/k-wiki/scripts/okf-lint.py --compile-index
```

---

### 4. Automated Unit Test Suite

```bash
# Run all unit tests with verbose reporting:
python -m unittest discover -s tests -v
```

---

## Installation & Usage

This repository is structured natively as an Antigravity skills repository.

To use these skills in another project, clone the repo and copy `.agents/skills/*` into your target workspace:

```bash
git clone https://github.com/antoniogutierrez1976/k-method.git
cp -r k-method/.agents/skills/* mi-proyecto/.agents/skills/
```