# Elicitation & Interview Checklist

Before drafting `spec.md`, review these dimensions to extract missing requirements from the user:

1. **Scope Sizing Check (Is this an Epic or Breaking Migration?):**
   - Does this replace an existing core subsystem? -> Activate Migration Spec (Strangler Fig)!
   - Does this request encompass multiple architectural layers? -> Switch to Epic Decomposition!
2. **State & Persistence:**
   - Where does state live (database, in-memory, local cache, session)?
   - Are transactions, savepoints, or idempotency keys required?
3. **Error & Degraded States:**
   - What happens on downstream timeout or network disconnect?
   - Should errors fail loudly with typed exceptions or degrade gracefully?
4. **Security & Permissions:**
   - Which user roles or authorization scopes are required?
   - Payload sanitization, PII filtering, and FLS/CRUD enforcement.
5. **Performance & Concurrency:**
   - Throughput targets, N+1 query prevention, bulkification.