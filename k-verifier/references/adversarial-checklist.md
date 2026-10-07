# Adversarial Reviewer Checklist (Hardened Enterprise Edition)

Conduct this audit after all tests and regression suites pass green, acting as a critical external reviewer:

1. **Boundary & Scope Creep:**
   - Did the code alter files or dependencies outside the approved `spec.md`?
   - Were any shared contracts or interfaces modified that could break external consumers?
2. **False Positives & Vacuous Test Resistance:**
   - Did the test fail when the Negative Fault Injection (mutation) was applied?
   - Are assertions testing real business outcomes or just trivial mocked returns?
3. **Hidden Side-Effects & Performance Traps:**
   - **N+1 Query Detection:** Are database queries or network requests issued inside loops? Are queries properly bulkified?
   - **Transaction Atomicity:** Are database mutations wrapped in transactions/savepoints with rollback on error?
   - **Async Hygiene:** Are there unhandled promise rejections, dangling timeouts, or memory leaks?
4. **Data Privacy & Telemetry Leaks:**
   - Are debug logs free of authorization tokens, passwords, private keys, or Customer PII?
   - Are log messages structured with proper severity levels?
5. **Code Cleanliness & Strict Typing:**
   - No leftover debug `console.log` statements or commented-out dead code.
   - Types are strictly defined without indiscriminate `any` or `@ts-ignore`.