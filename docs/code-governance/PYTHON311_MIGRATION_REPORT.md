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

## Dependency diff (lock names, before → after)

Removed: `abcdyi` (self-entry renamed), `structlog`. Added: `giraffe-jp`
(self-entry). All other resolutions unchanged.

## Test results (clean 3.11 env, PostgreSQL 16)

```
uv run pytest tests/ -q   →   734 passed, 0 failed
```

5× consecutive-run results from the same commit: see TEST_BASELINE_REPORT.md.

## Known risks

- The dev-dependency consolidation lowers the pytest floor from the
  conflicting `>=9.1` declaration to `>=8.2` (resolves to the same latest
  version in practice; suite verified on the resolved version).
