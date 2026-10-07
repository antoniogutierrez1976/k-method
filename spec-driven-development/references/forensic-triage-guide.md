# Forensic Triage & Hypothesis Guide (Stage 0: Pre-Spec)

Use this guide when handling vague, incomplete, or opaque production incident reports (e.g., "500 error on checkout", "nightly batch failed", screenshot of generic alert).

## Objectives
1. Convert ambiguous symptom reports into testable technical hypotheses.
2. Prevent premature code editing or speculative fixing.
3. Establish whether the path is Direct Fix or Observability Enhancement.

## Step-by-Step Diagnostic Protocol

### Step 0.0: Telemetry Log Truncation (Noise Reduction)
**WARNING:** Never attempt to ingest massive raw JSON dumps (Sentry, Datadog, CloudWatch) directly into your context window.
- Use local CLI tools (`grep`, `jq`, `tail`, `head`, `awk`) to filter the raw log files first.
- Extract ONLY the relevant stack traces, the last 50 error occurrences, or specific correlation IDs before reading the content.

### Step 0.1: Static Code Reconnaissance (Read-Only)
- Search codebase for exact string literals, error codes, custom labels, or exception types.
- Identify the call hierarchy: which entrypoints reach the suspected code?
- Inspect git commit history (`git log -S` / git blame) for recent modifications in the suspect path.

### Step 0.2: Construct the Competing Hypothesis Tree
Formulate 2-3 mutually exclusive, falsifiable technical hypotheses:
- **Hypothesis A (Data / Input anomaly):** Missing required field, unexpected null, malformed payload.
- **Hypothesis B (State / Concurrency):** Record lock, race condition, stale cache, idempotency violation.
- **Hypothesis C (Infrastructure / Limits):** Platform limits (CPU/Heap/Governor limits), timeout, expired credentials.

### Step 0.3: The Fork Decision
- **Scenario 1 (Sufficient clues to reproduce):**
  Draft a single exploratory failing test reproducing Hypothesis A or B. If confirmed, proceed to Stage 1 to draft the `spec.md` with known Ground Truth.
- **Scenario 2 (Total opacity - impossible to reproduce without data):**
  Do NOT guess the fix. Halt code modification and route the task as an **Observability & Defensive Logging Spec**:
  - Spec objective: Inject surgical logging/telemetry and safe degradation around the suspect block.
  - Verification: Confirm via unit test that logging fires and errors degrade gracefully without crashing.