---
name: k-spec
description: Halts premature code generation and enforces Layer 1 (Spec) of Karpathy's method. Discriminates intent between Features, Incidents (/bugfix), Routine Maintenance (/chore), Radical System Pivots, and PR Feedback (/iterate). Features strict Epic Detection with a hard limit of 6 Acceptance Criteria per spec to force decomposition of high-context requirements into multiple specs. Integrates Threat Modeling (OWASP), defines out-of-scope boundaries, manages formal spec amendments upon technical friction, and generates verifiable spec.md artifacts.
---

# Spec-Driven Development (Karpathy Layer 1: Spec)

## Objective
Prevent the LLM from leaping directly into code generation or cramming high-context requirements into a single monolithic spec. Outsource computation to the AI, but never delegate understanding. Break down complex problems before coding.

## Protocol & Operational Rules

### 0. Intent Classification
Upon receiving a user task, determine the **Nature of the Intent**:

- **Branch A: ASYNC FEEDBACK ITERATION (`/iterate`)**
  - *Action:* Read `pending-iteration.md`. Evaluate against original spec, log amendment, dispatch Verifier on existing branch.
- **Branch B: ROUTINE MAINTENANCE (`/chore` or `/bump`)**
  - *Action:* BYPASS SPEC CREATION. Dispatch directly to Layer 2 (Verifier) on a new `chore/` branch to execute the change and validate global regression.
- **Branch C: FEATURE / ENHANCEMENT (New Capability or Functional Adaptation)**
  - *Action:* BYPASS STAGE 0. Jump directly to **Section 1: Mandatory Scope Sizing & Epic Detection**. Include Threat Modeling (OWASP).
- **Branch D: INCIDENT / BUG (`/bugfix`)**
  - *Action:* Trigger Stage 0 Forensic Triage. All bug specifications MUST be routed to: `specs/{feature}/bugs/BUG-{NNN}.md`.
- **Branch E: RADICAL ARCHITECTURAL MIGRATION / BREAKING CHANGE**
  - *Action:* Activate the **Strangler Fig (Expand & Contract) Protocol**. Scaffold `migration-spec.md`.

### Stage 0: Pre-Spec Forensic Triage (ONLY for Bugs / Incidents)
- **DO NOT** attempt to guess the fix or read massive raw telemetry logs directly.
- Consult `references/forensic-triage-guide.md` (Enforce Log Truncation using CLI tools first).
- Perform read-only static code reconnaissance. Formulate a Competing Hypothesis Tree and present it.

### 1. Mandatory Scope Sizing, Epic Detection & The 6-AC Rule
LLMs naturally attempt to cram high-context functional requirements into a single monolithic file to "please" the user in one turn. You are strictly forbidden from doing this.
- **The 6-AC Hard Limit:** A single `spec.md` MUST NOT contain more than 6 Acceptance Criteria (including Security ACs).
- **Cognitive Density Limit:** If the feature spans >3 architectural layers (e.g., DB + API + UI) or requires deep domain context, it is an Epic.
- **Action for Epics:** Do NOT write a monolithic `spec.md`. Instead, scaffold `templates/epic-breakdown.template.md` to decompose the high-context request into 2 or more sequential, verifiable specs (e.g., `01-core-domain.spec.md`, `02-api-layer.spec.md`). Present the roadmap and **HALT** for user approval.

### 2. Inquire & Security (Interview Phase)
- Review `references/interview-checklist.md`. Include Shift-Left Security considerations (Threat Modeling).

### 3. Human Approval Gate
- After drafting the single spec OR the epic breakdown, **STOP YOUR TURN IMMEDIATELY**. Prompt the user for explicit approval.

### 4. Spec Amendment Protocol (Preventing Spec Drift)
- If technical roadblocks occur during TDD, update the `## Amendment Log` in the spec and request user re-approval.

### 5. Spec Checkbox Integrity & Closure Gate
- A specification is incomplete if any checkbox remains unchecked.
- Before PR creation or merging to trunk, the agent MUST audit and verify 100% of checkboxes in `spec.md`:
  - **Section 2 (Boundaries & OOS):** Every negative constraint audited (e.g. via `git grep`) and marked `[x]`.
  - **Section 4 & 5 (Security & Functional ACs):** Every AC (including `AC-Sec-X`) marked `[x]` with its test identifier.
  - **Section 7 (Checkpoints):** Checkpoints 1 through 8 verified and marked `[x]`.
- **Zero Unchecked Gate:** Merging a spec with unresolved `- [ ]` boxes is strictly prohibited.