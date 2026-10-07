# Karpathy 3-Layer Skills Pack v17 (High-Context Epic Edition)

Fully compliant with Anthropic's **"The Complete Guide to Building Skills for Claude"**.

## The Day-2 Maintenance Evolutions (v17 Capstones):
1. **Strict Epic Detection (The 6-AC Rule):** Enforces a hard limit of 6 Acceptance Criteria per spec, forcing the LLM to decompose high-context functional requirements into multi-spec Epic roadmaps.
2. **Shift-Left Security & Threat Modeling:** Enforces OWASP threat vector analysis and specific Security Acceptance Criteria (AC-Sec) in all new specifications.
2. **Routine Maintenance Bypass (`/chore`):** Dedicated workflow for dependency bumps and minor refactors that skips heavy spec generation and goes straight to global regression validation.
3. **Infrastructure as Code (IaC) Sync:** Extends environment drift prevention by ensuring `.env` changes are automatically propagated to Docker, Kubernetes (Helm), or Terraform manifests.
4. **Structured Telemetry Ingestion (Noise Reduction):** Mandates CLI-based log truncation (`grep`, `jq`) during Stage 0 Forensic Triage to prevent context window saturation from raw Sentry/Datadog dumps.

## Full Feature Set (SDLC Complete):
- **Pull Request & Release Artifact Generator:** Compiles PR bodies with AC ground-truth evidence, rollback instructions, and observability alerts.
- **Async PR Feedback Loop (`/iterate`):** Formal support for asynchronous GitHub code review feedback via `pending-iteration.md`.
- **Production Build & Dependency Security Audit:** Formal verification checkpoint (`pnpm build` & `pnpm audit`).
- **Visual Regression Testing (VRT):** Native checkpoints for Playwright Golden Master Visuals, protecting UI bounds.
- **Forensic Bug Routing (`/bugfix`):** Strict isolation of maintenance patches (`specs/{feature}/bugs/BUG-{NNN}.md`).
- **Zero-Downtime Database Migration Protocol:** Expand & Contract for persistence models.
- **Release Strategy, Rollback & Observability SLO Contracts:** Enriched spec templates for operational readiness.
- **Robust Multi-line YAML Parser in `okf-lint.py`:** Dependency-free YAML parsing for OKF graphs.
- **Branch Coverage Floor (≥85%):** Strict gating on modified domain logic.
- **Stash Shield & Atomic Rollback Protocol (`/task-abort`):** Guards against dirty working trees.
- **Config & Environment Drift Prevention:** Automatic `.env.example` and IaC sync.
- **Trunk Staleness & Rebase Guard:** Validates upstream divergence before regression.
- **Tooling Anti-Sabotage Rule:** Explicitly prohibits agents from modifying `.tools/` scripts or `.claude/skills/`.
- **Self-Contained OKF Compiler Tool:** Auto-contained within the skill to prevent path collisions.
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

## Installation
```bash
unzip -o karpathy-3-layer-anthropic-skills-v16.zip -d .claude/skills/
```