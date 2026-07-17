# Python 3.11 Migration Report — Giraffe-JP (Stage 1)

## Constraint state

| | Before | After |
|---|---|---|
| `requires-python` | `>=3.11` (already correct) | `>=3.11` |
| CI matrix | 3.11 | 3.11 (unchanged) |
| Dockerfile | `python:3.11-slim` | unchanged |
| `uv.lock` | distribution `abcdyi`, contained `structlog` | rebuilt: distribution `giraffe-jp`, 54 packages |

Giraffe-JP never regressed to 3.9; no `eval-type-backport`, no 3.9-only
compatibility code was found (audit §11). Stage 1 work here was consistency
verification plus a lockfile rebuild forced by the identity fix
(distribution name `abcdyi` → `giraffe-jp`) and dependency pruning.

## Removed compatibility dependencies

None existed.

## Removed unused dependencies

- `structlog` — zero imports repo-wide.

## Compatibility code changes

None required. Legacy-but-valid typing styles left untouched per PRD §5.2.

## CI matrix

Unchanged (all jobs Python 3.11).

## Clean install result (from empty environment)

```
rm -rf .venv uv.lock
uv venv --python 3.11        # PASS (CPython 3.11.15)
uv lock                      # PASS — resolved 55 packages (incl. local gltg path dep)
uv sync --all-extras --dev   # PASS
uv run python -m compileall -q src api scripts tests *.py   # exit 0
```

## Dependency diff (lockfile rebuild)

The lockfile rebuild was not identity-only. It made the following direct and
runtime-resolution changes:

- Removed the old self-entry `abcdyi` and added the corrected self-entry
  `giraffe-jp`.
- Removed unused `structlog`.
- Upgraded resolved runtime packages, including:
  - FastAPI `0.136.3` → `0.139.2`
  - Starlette `1.1.0` → `1.3.1`
  - Uvicorn `0.48.0` → `0.51.0`
  - SQLAlchemy and associated transitive resolutions, as recorded in the
    committed `uv.lock` diff.

These upgrades are disclosed as behavior-affecting dependency changes rather
than identity-only metadata changes. They were validated on the final lockfile
through clean installation, application import/startup checks, Alembic
upgrade/downgrade/upgrade, the complete test suite, and the GitHub CI workflow.
No API route, business rule, ORM model, or migration source was changed by this
PR.

## Test results (clean 3.11 env, PostgreSQL 16)

```
uv run pytest tests/ -q   →   734 passed, 0 failed
```

5× consecutive-run results from the same commit: see TEST_BASELINE_REPORT.md.

## Known risks

- The runtime dependency upgrades above may expose upstream behavior changes
  despite the passing regression suite. Release review must therefore treat
  the committed lockfile as part of the functional change surface.
- The dev-dependency consolidation lowers the pytest floor from the
  conflicting `>=9.1` declaration to `>=8.2` (resolves to the same latest
  version in practice; suite verified on the resolved version).
