# Stage 1 Code Governance — Giraffe-JP Baseline Audit (Phase A)

- **Repository:** `GiraffeTechnology/Giraffe-JP`
- **Audit commit:** `41f24fb014cc8b6f6ae1a4e00253d6ef05031cd8` (main)
- **Audit date:** 2026-07-16
- **Status:** Read-only audit completed BEFORE any code modification.

## 1. Repository tree (top level)

```
.github/workflows/ci.yml     CI (Python 3.11, PostgreSQL 16 service)
alembic/                     5-revision linear migration chain
api/                         FastAPI app (api.main:app), 24 route modules, 97 routes
src/                         46 packages copied from abcdYi + src/giraffe_jp (JP extension)
libs/GLTG/                   vendored GLTG engine (3 py files, editable path dependency)
tests/                       81 files
scripts/                     24 scripts
openclaw/, frontend/, docs/  skills / assets / docs
main.py                      helper entry (identical to abcdYi's)
run_bm_e2e_with_db.py        CI-referenced E2E script (root)
bm_db_adapter.py             imported by run_bm_e2e_with_db.py / verify_integration.py
bm_db_hardening.py           imported by the BM DB E2E path
build_schema.py              CI-referenced schema builder
verify_integration.py        CI-referenced 5x verification runner
pydantic_stub.py             fallback shim imported only by verify_integration.py
15 root *.md files           session reports / validation reports / README / notices
```

Python files: **474** (src 326, api 27, tests 81, scripts 24, libs 3).

## 2. Identity audit (CONFIRMED DEFECTS)

| Location | Current value | Correct value |
|---|---|---|
| `pyproject.toml` `name` | `abcdyi` | `giraffe-jp` |
| `pyproject.toml` `description` | "abcdYi — Giraffe Agent Apparel / Textile / Handicraft Industry Edition" | Giraffe JP merchant-backend description |
| `api/main.py` FastAPI `title`/`description` | abcdYi identity | Giraffe JP identity |
| `GET /health` `product` field | abcdYi identity | Giraffe JP identity |
| `main.py` banner | "Giraffe Agent" | Giraffe JP |
| README | already repositioned to "Giraffe JP" | (consistent) |

README is correct; package metadata, OpenAPI title, health payload and logs still claim to be abcdYi.

## 3. Relationship to abcdYi (measured)

- `src/` has 326 files; **317 exist in abcdYi's `src/`** — 175 byte-identical, 142 diverged (independent fixes applied on both sides since the copy).
- Japan-specific code is small and well-contained:
  - `src/giraffe_jp/` — communication, formalwear, message_permissions, schemas, service (5 modules)
  - `src/db/models/giraffe_jp.py`
  - 6 `api/routes/giraffe_jp_*.py` route modules
  - 2 JP-specific Alembic revisions
- abcdYi-only modules NOT copied here: `src/aivan`, `src/gpm`, `src/db/tenant_scope.py`, `src/integrations/gltg_client.py`, `gltg_leadtime.py`, `src/lead_time/gltg_models.py`.
- Giraffe-JP retains `src/lead_time/lead_time_calculator.py` and `path_enumerator.py` — the **pre-GLTG local lead-time implementation that abcdYi already replaced** with the GLTG HTTP client.

## 4. Vendored GLTG (`libs/GLTG`)

- `pyproject.toml`: `gltg = { path = "libs/GLTG", editable = true }`, dependency `gltg`.
- Contents: `gltg/engine.py`, `gltg/models.py`, `gltg/__init__.py` — a local copy of the GLTG lead-time engine.
- **Live runtime imports** (evidence why it cannot be deleted this stage):
  - `src/services/delivery_feasibility_service.py`
  - `src/decision_packets/service.py`
  - `src/lead_time/gltg_adapter.py`
  - CI lead-time test job depends on this path.
- abcdYi already migrated the same three call sites to an HTTP client (`src/integrations/gltg_client.py`, fail-closed). The same migration applies here → **Stage 2 handoff item JP-S2-1** (canonical destination: standalone `GLTG` service consumed over HTTP). Deleting `libs/GLTG` now would break the runtime; vendoring is kept **only** with this documented evidence, per acceptance criterion "libs/GLTG 删除，或提交不可删除的明确证据".

## 5. API route inventory

24 route modules, 97 routes: the 18 abcdYi modules (minus `gpm_service`) plus 6 `giraffe_jp_*` modules (service_nodes, confirmations, customer_service, message_permissions, conversations, formalwear). All registered in `api/main.py`; no dead routers found.

## 6. Migrations

Linear 5-revision chain, `upgrade head` verified on fresh PostgreSQL 16:
`f66f720908c0` → `a1b2c3d4e5f6` → `b2c3d4e5f6a7` → `d4e5f6a7b8c9` → `e5f6a7b8c9d0`.

**Fork hazard:** revision id `b2c3d4e5f6a7` is `add_giraffe_jp_service_core` here but `reconcile_projects_role_switching_columns` in abcdYi — same id, different meaning. The two repos' databases must never share an `alembic_version` table. Documented; no rewrite of published migrations this stage (PRD §9).

## 7. Dead code candidates (evidence per PRD §4.1)

| Path | Evidence | Verdict |
|---|---|---|
| root session/validation reports (11 files) | historical session output | **ARCHIVE** → `docs/archive/` |
| `bm_db_adapter.py`, `bm_db_hardening.py`, `build_schema.py`, `run_bm_e2e_with_db.py`, `verify_integration.py`, `pydantic_stub.py` | referenced by `ci.yml` (lines 88–127) | **KEEP** (live CI harness) |
| `src/lead_time/lead_time_calculator.py`, `path_enumerator.py` | imported by runtime feasibility path + CI job `test_lead_time_*` | **KEEP** until JP-S2-1 GLTG migration (deleting now breaks runtime) |
| `libs/GLTG` | runtime imports (see §4) | **KEEP + Stage 2 handoff JP-S2-1** |
| `tests/test_mside_role_switching.py::TestPatentNotice::test_readme_mentions_role_switching` | asserts a README keyword only; broken by README repositioning; PRD Phase E explicitly allows deleting keyword-assert tests | **DELETE (test)** |

No unregistered route modules, no orphan Python packages beyond the above were found.

## 8. Tests baseline

Baseline (main, Python 3.11, PostgreSQL 16):
**734 passed, 1 failed** — the failure is the README-keyword test above (doc drift, not behavior). Security suites present and passing: tenant isolation, approval gates, role switching, auth, giraffe_jp permissions/confirmation policies.

## 9. Dependencies

- `structlog` — **zero imports** anywhere → DELETE.
- `python-multipart` — required (OAuth2PasswordRequestForm login).
- `asyncpg` + `psycopg2-binary` — both justified: runtime uses asyncpg, Alembic/CI uses psycopg2 (`ALEMBIC_DATABASE_URL`).
- Dev deps declared twice with **conflicting ranges**: `optional-dependencies.dev` (`pytest>=8.2`) vs `dependency-groups.dev` (`pytest>=9.1`) → consolidate.
- `gltg` — vendored path dependency (see §4).

## 10. Environment variables

See `ENVIRONMENT_VARIABLE_MATRIX.md`. `.env.example` (13 lines) covers DB/auth basics; `GIRAFFE_DB_*`, `QWEN_*` flags read by BM DB harness; fail-closed defaults observed.

## 11. Python version

`requires-python = ">=3.11"` already correct; CI on 3.11; no `eval-type-backport`; no 3.9 residue found. Phase B for this repo = consistency verification + lockfile/metadata refresh after identity fix.

## 12. Documentation drift

- README already describes Giraffe JP correctly — but package metadata contradicts it (§2).
- 11 root-level historical reports present stale results as current → ARCHIVE.
- `CHANGELOG.md` describes abcdYi iterations copied wholesale → keep, annotate provenance in archive note (REVIEW).

## 13. Architecture relationship decision (Phase D input)

Measured state = "copy of abcdYi backend + JP extension layer + vendored GLTG". Options per PRD:
- **Option A** (depend on pinned abcdYi package): target state, requires abcdYi to publish a package and JP imports to be rewritten — **not executable inside Stage 1** without cross-repo coupling.
- **Option B** (shared common package): explicitly deferred by PRD (no third repo in Stage 1).
- **Option C** (deployment overlay): equivalent end-state to A for the runtime.

**Stage 1 decision: adopt Option A as the target architecture, document it, and stop the fork from deepening** (identity fixed, duplication measured and frozen, JP-specific code inventoried above so extraction is mechanical in Stage 2). No wholesale re-sync in either direction (PRD §12.16).

## 14. Deletion risk assessment

- Identity fixes: LOW (strings/metadata only; tests asserting the old title updated in the same change).
- Report archival: NONE (moves).
- `structlog` removal: LOW (zero imports).
- Keyword-test deletion: NONE (PRD-sanctioned category).

## 15. Currently runnable / failing commands

```
uv venv --python 3.11 && uv sync --all-extras --dev   # PASS
uv run alembic upgrade head                            # PASS (fresh PG16)
uv run pytest tests/ -q                                # 734 passed, 1 failed (README keyword test)
uv run uvicorn api.main:app                            # canonical serve path
```

## 16. Disposition summary

| Item | Action |
|---|---|
| distribution name / description / OpenAPI title / health product / main.py banner | FIX → Giraffe JP identity |
| root historical reports (11) | MOVE → `docs/archive/` (ARCHIVED banner) |
| `structlog` dependency | DELETE |
| dev-dependency double declaration | MERGE |
| README-keyword test | DELETE |
| `libs/GLTG` + local lead-time modules | KEEP + **Stage 2 handoff JP-S2-1** (migrate to GLTG HTTP client as abcdYi did) |
| copied abcdYi backend | KEEP frozen; Option A extraction is Stage 2 (handoff JP-S2-2) |
| migrations | KEEP (no history rewrite); revision-id collision documented |
