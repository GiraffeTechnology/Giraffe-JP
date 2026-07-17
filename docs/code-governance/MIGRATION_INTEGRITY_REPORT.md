# Migration Integrity Report — Giraffe-JP (Stage 1)

## Migration graph

Linear chain, no branches:

```
f66f720908c0  iter1_initial_schema                       (shared with abcdYi)
    └─ a1b2c3d4e5f6  add_delivery_feasibility_packets    (shared with abcdYi)
        └─ b2c3d4e5f6a7  add_giraffe_jp_service_core     (JP-specific; ID COLLIDES with abcdYi's b2c3d4e5f6a7!)
            └─ d4e5f6a7b8c9  add_giraffe_jp_iterations_02_03_04
                └─ e5f6a7b8c9d0  add_mside_actor_columns_to_projects
```

## Validation (fresh PostgreSQL 16, empty database `mig_check_jp`)

```
alembic upgrade head      PASS  (all 5 revisions applied)
alembic downgrade base    PASS  (clean teardown, correct reverse order)
alembic upgrade head      PASS  (re-applied from empty)
```

Existing-database upgrade: the JP test database was migrated to head and the
full suite (unit/api/db/integration) passes against it.

## Checks

- No duplicate tables/columns/indexes within this chain.
- JP extension tables (`giraffe_jp` service core + iterations) are additive
  revisions on top of the shared base — no fork of shared tables detected.
- Tenant FKs present in JP service tables (verified by `tests/db` +
  tenant-isolation API tests, all passing).
- No migration rewritten; Stage 1 added no revisions.

## Fork hazard (documented, not fixed here)

Revision id `b2c3d4e5f6a7` means `add_giraffe_jp_service_core` here but
`reconcile_projects_role_switching_columns` in abcdYi. Consequences:
1. The two applications must NEVER share an `alembic_version` table/database.
2. Any future tooling that merges the repos' histories must renumber first.
3. New revisions in both repos must use freshly generated (random) ids —
   do not hand-pick sequential ids like `c3d4...`/`d4e5...` again.
Status: REVIEW_REQUIRED (Stage 2 cross-repo item; rewriting published
migration history is forbidden by PRD §9/§12.12).
