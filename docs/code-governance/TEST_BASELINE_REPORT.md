# Test Baseline Report — Giraffe-JP (Stage 1)

## Classification (Phase E.1)

| Category | Location | Count (files) | Notes |
|---|---|---|---|
| unit | `tests/unit/` | 10 | incl. giraffe_jp policy suites (conversation/message permissions, formalwear rules), GLTG adapter, lead-time |
| contract | GLTG-adapter/feasibility unit suites against the vendored engine | — | becomes an HTTP-contract suite after Stage 2 JP-S2-1 |
| api | `tests/api/` | 18 | route-layer incl. 6 `giraffe_jp_*` suites, auth, health |
| integration | `tests/integration/` + `integration` marker | 1 | requires live migrated PostgreSQL |
| db | `tests/db/` | 6 | schema/migration behavior |
| e2e | root `tests/test_*` (38 files) incl. role-switching E2E | 38 | business-chain level |
| live / hardware-external | scripts under `scripts/` requiring real keys | — | excluded from default suite by design |

`tests/e2e/` and `tests/regression/` are empty placeholder packages
(`__init__.py` only) — noted; kept as structure markers.

## Deleted tests (Phase E.2)

- `test_readme_mentions_role_switching` (one method) — asserted only that a
  keyword exists in README; broke when the README was repositioned for
  Giraffe JP; PRD-deletable category ("仅断言 README 中存在某个词").
  All 79 behavioral role-switching tests retained.

Protected categories all retained and passing: tenant isolation, approval
gates/confirmation flow, message permissions, auto-send policy (human-gated),
append-only events, migration up/down/up, API auth, fail-closed defaults.

## Core E2E chain (Phase E.3) — retained and passing

`customer/service request → service node → confirmation → communication draft
→ auto-send policy decision → human approval where required → formalwear/C2B2M
project state → append-only audit/execution event` is exercised by
`tests/api/test_giraffe_jp_service_core.py`, `test_giraffe_jp_conversations.py`,
`test_giraffe_jp_message_permissions.py`, `test_giraffe_jp_formalwear.py` plus
the unit policy suites.

## Continuous validation (Phase E.4)

Environment: clean `uv venv --python 3.11`, PostgreSQL 16 (fresh container).
All five runs from commit `55f0be1`, no code changes between runs:

```
clean install:        PASS
compileall:           PASS
migration up/down/up: PASS (fresh database)
core E2E:             PASS (within suite)
RUN 1: 734 passed   (119.37s)
RUN 2: 734 passed   (120.20s)
RUN 3: 734 passed   (120.81s)
RUN 4: 734 passed   (120.86s)
RUN 5: 734 passed   (120.18s)
```

## Baseline comparison

- Before (main `41f24fb`): 734 passed / **1 failed** (the README-keyword test).
- After: 734 passed / 0 failed ×5 — the suite is now stable and truthful; no
  behavioral test was removed.
