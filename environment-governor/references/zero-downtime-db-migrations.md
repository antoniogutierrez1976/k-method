# Zero-Downtime Database Migration Protocol (Expand & Contract for Data)

Use this guide whenever a task introduces or alters database schemas, tables, fields, or persistence models.

## Core Rule
**Never alter, rename, or drop active columns or tables in a single step.** The application running in production must always remain compatible with the database schema during and after deployment.

## The 5-Phase Zero-Downtime Lifecycle

```text
Phase 1: EXPAND (Backward Compatible Schema Change)
  - Add new column as NULLABLE (or with safe non-locking default).
  - Add new table or index CONCURRENTLY (without exclusive table locks).
  - Deploy schema migration to database.

Phase 2: DUAL-WRITE / READ-FALLBACK (Application Update)
  - Application writes to both old and new columns/tables.
  - Application reads from old column with fallback to new column.
  - Deploy application update.

Phase 3: ASYNCHRONOUS BACKFILL
  - Execute background batch / job to migrate historical legacy records to new schema.
  - Verify 100% data parity between old and new columns.

Phase 4: SWITCH READS (Application Update)
  - Switch application to read exclusively from the new schema.
  - Keep dual-writing to old column temporarily if rollback window is required.
  - Deploy application update.

Phase 5: CONTRACT (Prune Legacy)
  - Stop dual-writing.
  - Drop old column/table in an isolated migration once all consumers are updated.
  - Record deprecation in `knowledge-base/wiki/decisions/`.
```

## Migration Safety Checklist
- [ ] Columns added without exclusive table locks (`ADD COLUMN ... NULL`).
- [ ] No `ALTER TABLE ... DROP COLUMN` without a prior deprecation release.
- [ ] Indexes created using `CREATE INDEX CONCURRENTLY` (PostgreSQL) or non-blocking equivalent.
- [ ] Migration script tested on an isolated replica or scratch org with realistic data volume.