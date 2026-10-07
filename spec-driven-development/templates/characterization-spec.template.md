# Characterization Spec: [Legacy Module / Brownfield Target]

## 1. Goal & Context
- **Target Legacy Component:** `[Path to file / class]`
- **Refactoring Objective:** [e.g. Modernization, performance fix, dependency upgrade]
- **Invariant:** Zero observable behavior changes for pre-existing consumers.

## 2. Characterization Golden Master Baseline (Pre-Refactor Snapshot)
Before touching any production code:
1. Define a matrix of representative historical inputs (valid inputs, edge cases, boundaries, invalid inputs).
2. Execute the legacy component against this matrix and record exact outputs into a Golden Master snapshot:
   - File: `tests/snapshots/[legacy-module].snapshot.json`
3. Commit this baseline test in a passing state:
   - Spec Checkpoint: `Baseline Snapshot Committed [x]`

## 3. Refactoring Invariants & Boundary Guards
- [ ] No changes to public interface signatures.
- [ ] Golden Master snapshot must pass with 0 byte diff against refactored code.
- [ ] Out-of-Scope (OOS): Excluded optimizations or unapproved feature additions.

## 4. Verification Checkpoints
- [ ] Checkpoint 1: Golden Master baseline tests pass against legacy code.
- [ ] Checkpoint 2: Refactored code passes 100% of Golden Master snapshot assertions.
- [ ] Checkpoint 3: Negative Fault Injection verified on new implementation.
- [ ] Checkpoint 4: Full repository regression & SemVer guardian pass cleanly.