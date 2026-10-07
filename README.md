# k-method: Karpathy 3-Layer Skills Pack v17 (High-Context Epic Edition)

Enterprise-grade SDLC software engineering pipeline based on Andrej Karpathy's 3 layers (Spec, Verifier, Environment) + LLM-Wiki knowledge graph. Fully compliant with Anthropic's **"The Complete Guide to Building Skills for Claude"** and Agent Skills standards.

## Skills Included (`k-*`)

| Skill | Directory | Layer / Role | Description |
| :--- | :--- | :--- | :--- |
| **`k-orchestrator`** | [`k-orchestrator/`](file:///d:/dev/k-method/k-orchestrator/SKILL.md) | **Master Orchestrator** | State-machine supervisor dispatching ephemeral subagents across the complete SDLC pipeline. |
| **`k-spec`** | [`k-spec/`](file:///d:/dev/k-method/k-spec/SKILL.md) | **Layer 1: Spec** | Intent classification (`/bugfix`, `/chore`, `/iterate`), 6-AC hard limit, OWASP Threat Modeling. |
| **`k-verifier`** | [`k-verifier/`](file:///d:/dev/k-method/k-verifier/SKILL.md) | **Layer 2: Verifier** | Red-Green-Refactor, mutation testing, flaky 3x pass, circuit breaker, ≥85% branch coverage, VRT. |
| **`k-environment`** | [`k-environment/`](file:///d:/dev/k-method/k-environment/SKILL.md) | **Layer 3: Environment** | `AGENTS.md` constitution, Stash Shield, Git branch isolation, atomic rollback, IaC & `.env` sync. |
| **`k-wiki`** | [`k-wiki/`](file:///d:/dev/k-method/k-wiki/SKILL.md) | **Knowledge Graph** | Open Knowledge Format (OKF) engine, typed frontmatter, ADR lifecycle, `okf-lint.py` compiler. |


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

## Installation & Usage

Clone or copy the `k-*` skill directories into your agent skills path (e.g. `.claude/skills/` or `.agents/skills/`):

```bash
git clone https://github.com/antoniogutierrez1976/k-method.git
cp -r k-method/k-* .claude/skills/
```