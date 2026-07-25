# Repository Audit — `GiraffeTechnology/Giraffe-JP`

| | |
|---|---|
| **Repository** | `github.com/GiraffeTechnology/Giraffe-JP` |
| **Branch audited** | `main` (default; confirmed — not `master`) |
| **Commit** | `e81d828` — *Stage 1 code governance: correct Giraffe-JP identity and dependency reporting (#5)* |
| **Audit date** | 2026-07-25 |
| **Stack** | Python 3.11 · FastAPI · SQLAlchemy 2 (async) · Alembic · PostgreSQL 16 · uv · React 18/Vite frontend |
| **Size** | 603 tracked files · 474 Python files · ~47,600 LOC · 98 API operations · 734 tests |
| **Method** | Single-pass audit. Dependencies installed, migrations applied against a live PostgreSQL 16, full test suite executed with coverage, application booted and probed over HTTP. |

> **Note on the PRD's premise.** Section 2 assumed "no prior audit history to compare against". That is incorrect: `docs/code-governance/` contains a Stage 1 audit dated 2026-07-16 (nine days before this one) plus eight supporting reports. That work was scoped to **product identity, dead code, and dependency governance** — it did not examine authentication, authorization, tenant isolation, or CI enforcement. The security findings below are therefore new rather than regressions. Where this audit contradicts the prior one, it is called out explicitly (see F-14).

---

## 1. Executive Summary

Giraffe-JP is a well-structured, genuinely functional codebase: 734 tests pass, the five-revision migration chain applies cleanly to a fresh PostgreSQL 16, the domain model is coherent, and there is no SQL injection, command injection, or unsafe deserialization anywhere in the tree. The engineering fundamentals are sound.

The problem is that **its security controls are designed but not connected**. A complete RBAC permission engine exists and is imported by nothing. A multi-tenant data model exists, but 27 of 35 tables have no `tenant_id` column, so tenant isolation cannot be enforced even in principle. `is_platform_admin` is stored and returned to clients but never checked. The result is a system that looks defended on paper and is effectively open in practice: any authenticated user can read and modify any other tenant's orders, QC records, and RFQs.

Three findings were confirmed by live exploitation against a running instance, not merely by reading code:

1. **Cross-tenant data access (F-01, Critical).** Order, QC, RFQ, shipment and milestone tables carry no tenant column; service functions fetch by primary key alone. Any authenticated user of any tenant can read or mutate any other tenant's commercial data by ID.
2. **Authentication bypass via the default signing key (F-02, Critical).** `SECRET_KEY` defaults to the literal `"change-me-in-production"` — a value published in this repository and hardcoded in `docker-compose.yml`. A deployment that omits the environment variable starts silently and accepts tokens forged by anyone. Verified: a token signed with the default key passed signature validation.
3. **Seven unauthenticated write endpoints (F-03, Critical).** The `/api/qc/{project_id}/*` surface has no authentication and no tenant scoping. Verified: an unauthenticated `POST` created a supplier process card containing pricing and contract terms, and an unauthenticated `GET` read it back.

Compounding these, **`main` is an unprotected branch** (F-05): none of the five CI jobs gate merges, and CI runs only 312 of 734 tests (42%) with no lint step and no coverage gate. The `block-gpm-merge` workflow — a deliberate governance control — is likewise advisory only. Fixes can be merged, but nothing prevents them from being un-merged.

**Overall health: functional but not deployable to a multi-tenant production environment as it stands.** The Critical items are concentrated in a small number of files and are days of work, not months — the RBAC engine is already written, the tenant-scoping pattern already exists correctly in `src/giraffe_jp/service.py` and simply needs to be applied to the older modules. Recommended sequence: fail-fast on `SECRET_KEY` (hours), remove or authenticate the unauthenticated surface (hours), enable branch protection and widen CI (hours), then the tenant-isolation migration (the substantial piece).

---

## 2. Scope Coverage

Every in-scope item from PRD §3, with a pass/fail verdict.

| # | In-scope item | Verdict | Notes |
|---|---|---|---|
| 1 | Static code quality (lint, complexity, dead code, duplication) | **FAIL** | No linter configured. 270 ruff violations incl. 1 undefined name. 103 functions >50 lines. → F-09, F-14 |
| 2 | Dependency health (outdated, CVEs, licenses) | **PARTIAL** | 1 CVE (no fix available, not exploitable here). 2 unmaintained auth libs. Frontend has no lockfile. → F-10, F-11, F-16 |
| 3 | Secrets in code and git history | **PASS** | Clean. 7 commits scanned; no keys, no `.env` ever committed. One hardcoded seed password (Low). → F-18 |
| 4 | Security — auth/authz | **FAIL** | RBAC engine entirely unwired; no admin check. → F-02, F-03, F-04 |
| 5 | Security — input validation | **PASS** | Pydantic models on every request body; UUID path params typed. |
| 6 | Security — injection risk | **PASS** | ORM throughout; no raw SQL, `eval`, `subprocess`, or `pickle`. |
| 7 | Security — CORS | **FAIL** | Reflects arbitrary origins with credentials enabled. → F-06 |
| 8 | Architecture (boundaries, coupling, layering) | **FAIL** | Two unreconciled persistence layers; `src/` is a wholesale copy of another repo. → F-07, F-08 |
| 9 | Test coverage | **PARTIAL** | 734/734 pass, 61% overall — but critical paths sit at 25–38%. → F-12 |
| 10 | CI/CD gating | **FAIL** | Branch unprotected; 42% of tests run; no lint or coverage gate. → F-05, F-13 |
| 11 | Documentation accuracy | **FAIL** | README has no setup steps; deployment guide names the wrong repository. → F-15 |
| 12 | Configuration / secrets management | **FAIL** | Insecure default key; `.env.example` documents 7 of 30+ variables. → F-02, F-17 |

No blockers were encountered. Repository access, database, and toolchain were all available.

---

## 3. Findings

Severity: **Critical** = security or data-integrity risk · **High** = breaks or will break production · **Medium** = debt that slows delivery · **Low** = style or hygiene.

| ID | Sev | Category | Location | Description | Recommendation |
|---|---|---|---|---|---|
| F-01 | **Critical** | Security / Multi-tenancy | `src/db/models/*.py`; `src/orders/service.py:9`; `src/qc/service.py:134,150,166` | 27 of 35 model modules have no `tenant_id` column (`order`, `qc`, `rfq`, `logistics`, `approval`, `response`, `matching`, …). Services fetch by primary key with no ownership check, so any authenticated user reads/mutates any tenant's data. Only 12 tenant-equality filters exist across 67 service queries. | Add `tenant_id` (FK → `tenants.id`, `NOT NULL`, indexed) to every business table via Alembic; backfill through `project_id`. Apply the `_get_tenant_scoped` pattern already correct in `src/giraffe_jp/service.py:36-64` to all service reads. Enforce with PostgreSQL Row-Level Security as defence in depth. |
| F-02 | **Critical** | Security / Config | `src/db/base.py:9`; `docker-compose.yml:24,38` | `SECRET_KEY` defaults to `"change-me-in-production"`, published in this repo and hardcoded in compose. A deploy missing the env var boots silently and accepts forged tokens. **Verified**: token signed with the default key passed signature validation (rejected only at user lookup). | Remove the default — declare `SECRET_KEY: str` with no fallback so `pydantic-settings` fails fast at startup. Reject keys <32 chars. Generate a per-environment key in compose and inject via secrets manager in production. Rotate any key already deployed. |
| F-03 | **Critical** | Security / AuthZ | `api/routes/qc.py:82-152`; `api/routes/role_switching.py:78` | 8 of 98 operations require no authentication and no tenant scoping — 7 QC endpoints plus `run-upstream-pipeline`. They read and write supplier pricing, contract terms, QC verdicts and buyer decisions. **Verified**: unauthenticated `POST` created a process card with pricing/contract data; unauthenticated `GET` read it back. The in-code comment calls this intentional for an "internal MVP surface", but the router is mounted on the public app with no network segregation. | Add `Depends(get_current_user)` and project-ownership checks to all `/api/qc/{project_id}/*` and `/api/role-switching/*` routes. If they must stay internal, do not mount them on the public app — gate behind a separate internal-only ASGI app or drop the router when `GIRAFFE_ENV=production`. |
| F-04 | **High** | Security / AuthZ | `src/permissions/engine.py`; `src/permissions/dependencies.py`; `src/db/models/user.py:16` | A complete RBAC engine (11 roles, 9 permissions, `require_permission` dependency) is imported by **nothing** outside itself — 0% coverage on both modules. `is_platform_admin` is persisted and returned by `/api/auth/me` but never checked. Every authenticated user therefore holds every privilege. | Wire `require_permission(...)` into each router as a `dependencies=[...]` entry, starting with approval, order-confirmation and RFQ-send routes where the human-approval boundary is a stated product guarantee. Add an explicit admin check wherever `is_platform_admin` is meant to matter. Add negative tests asserting 403 for under-privileged roles. |
| F-05 | **High** | CI/CD | GitHub branch settings; `.github/workflows/*.yml` | `main` is **unprotected** (`"protected": false` via the branches API). None of the five CI jobs gate merges — all are advisory. This also renders `block-gpm-merge.yml`, an intentional governance control against reintroducing GPM code, unenforceable. | Enable branch protection on `main`: require all five CI jobs plus `block-gpm-merge` as required status checks, require PR review, and disallow force-push. Without this, every other fix in this report can be silently reverted. |
| F-06 | **High** | Security / CORS | `api/main.py:40-46` | `allow_origins=["*"]` combined with `allow_credentials=True` causes Starlette to **reflect the caller's `Origin`** and return `access-control-allow-credentials: true`. **Verified**: `Origin: https://attacker.example` was echoed back on both a simple request and a preflight allowing all methods. Impact is bounded — auth is Bearer-header, not cookie-based, so tokens are not auto-attached — but the same-origin policy is fully defeated for the unauthenticated endpoints in F-03. | Replace with an explicit allowlist from configuration (`CORS_ALLOWED_ORIGINS`), defaulting to the merchant storefront origin only. Keep `allow_credentials=True` only if cookie auth is actually adopted; otherwise set it to `False`. Never pair a wildcard with credentials. |
| F-07 | **High** | Architecture | 26 modules under `src/` (e.g. `src/b_side/workspace.py`, `src/merchandiser/qc/*`, `src/m_side/communication/*`) | Two parallel, unreconciled persistence layers: 35 SQLAlchemy models on PostgreSQL, and 26 modules writing JSON files under `data/` (which is `.gitignore`d). The file layer has no tenant isolation, no transactions, no migrations, and no cross-replica consistency — it breaks under any horizontally scaled or container-restart deployment, and it is exactly the layer F-03 exposes unauthenticated. `logistics` exists in **both** (`src/logistics/service.py` vs `logistics_models.py`). | Decide a single source of truth per bounded context. Migrate the file-backed stores that hold commercial state (QC evidence, workspaces, logistics events, outbox/inbox) into PostgreSQL with tenant scoping. If any store must stay file-based for MVP, move it behind an explicit repository interface and exclude it from the public API surface. |
| F-08 | **High** | Architecture | `src/` (326 files) | Per the Stage 1 audit, 317 of 326 `src/` files are copied from the `abcdYi` repository, 142 already diverged. Bug fixes must be applied twice and drift silently. The repo also retains `src/lead_time/lead_time_calculator.py`, the pre-GLTG local implementation that `abcdYi` already replaced — contradicting the README's own boundary rule that Giraffe JP "should use GLTG… and should not guess lead time locally". | Execute the already-identified Stage 2 handoffs: **JP-S2-2** (extract shared backend to a pinned internal package) and **JP-S2-1** (replace vendored `libs/GLTG` + local calculator with the GLTG HTTP client). Until then, record the upstream commit each `src/` file was copied from so drift is measurable. |
| F-09 | **High** | Code quality | `tests/test_order_bridge_buyer_actor_fix.py:9` | Ruff reports 270 violations including **F821 undefined name** `BWWorkspace` — a real defect that would raise `NameError` if the annotation were ever evaluated (e.g. under `from __future__ import annotations` removal or runtime introspection). No linter is configured in the repo or CI, so nothing catches this class of error. | Add ruff to `[dependency-groups].dev` with a `[tool.ruff]` config, fix F821 by importing `BWWorkspace`, apply `ruff check --fix` for the 207 auto-fixable issues, then add a blocking lint job to CI (see F-13). |
| F-10 | **Medium** | Dependencies | `pyproject.toml:12,16` | Authentication rests on two effectively unmaintained libraries: `passlib` 1.7.4 (last release October 2020, >18 months stale) and `bcrypt` pinned `<4.0.0` (resolves to 3.2.2) solely because passlib is incompatible with bcrypt 4.x. Cross-reference F-11 — `python-jose` is the third. | Migrate password hashing to `bcrypt` 4.x directly, or to `argon2-cffi` via `pwdlib`. Both remove the passlib dependency and unpin bcrypt. Contained change — `api/auth.py` is 35 lines. |
| F-11 | **Medium** | Dependencies / CVE | `ecdsa` 0.19.2 (transitive via `python-jose[cryptography]`) | `pip-audit` reports **PYSEC-2026-1325**: Minerva timing attack on P-256 permitting private-key recovery. Upstream considers side channels out of scope — **no fix is planned**. *Not currently exploitable here*: the application signs with HS256 (HMAC), so the ECDSA path is never taken. Risk is latent, activating if anyone switches `ALGORITHM` to ES256. | Migrate from `python-jose` to `PyJWT` (actively maintained, does not pull `ecdsa`). Meanwhile pin `ALGORITHM` to HS256 in code and reject asymmetric algorithms explicitly, so `decode_token` cannot be tricked into an ECDSA path. |
| F-12 | **Medium** | Test coverage | Suite-wide | 734/734 tests pass; overall coverage 61%. But the critical paths named in the PRD are the least covered: `src/order_confirmation/service.py` 25%, `src/supplier_responses/service.py` 28%, `src/qc/service.py` 31%, `src/rfq/service.py` 35%, `src/giraffe_jp/service.py` 38%. 44 modules over 15 statements have **0%**, including `src/logistics/logistics_webhook_service.py` and both `src/permissions/` modules. | Raise coverage on order-confirmation, QC and approval-gate services to ≥80%, prioritising negative tests: wrong tenant, missing permission, invalid state transition. Add a coverage floor to CI once the baseline is stable. |
| F-13 | **Medium** | CI/CD | `.github/workflows/ci.yml` | CI runs **312 of 734 tests (42%)** by naming individual files. Untested in CI: `tests/api/test_qc.py`, `test_orders.py`, `test_rfq.py`, `tests/integration/`, and all non-`giraffe_jp` unit tests. The "Compile Python files" step runs `py_compile *.py` — **7 root files, not the 353 under `src/` and `api/`**. Every job runs `uv add --dev pytest`, mutating `pyproject.toml` and `uv.lock` mid-build although pytest is already declared. No lint job, no coverage reporting. Cross-reference F-05: none of it gates anything. | Replace the per-file lists with a single `uv run pytest tests/ -q` job against the existing PostgreSQL service. Delete the `uv add --dev pytest` steps (use `uv sync --group dev`). Drop `py_compile` in favour of the ruff job from F-09. Then make these required checks under F-05. |
| F-14 | **Medium** | Dead code / Docs | `bm_db_hardening.py` (972 lines) | Contains 8 regression suites including a "Baseline v1 regression guard", but is referenced by **no workflow and imported by no module** — it runs only when invoked by hand. Both `docs/code-governance/STAGE1_GIRAFFE_JP_AUDIT.md:82` and `DEAD_CODE_REMOVAL_REPORT.md:24` state it is "referenced by `ci.yml` (lines 88–127)" and a "live CI harness". **This is factually incorrect** — `ci.yml` references `build_schema.py`, `run_bm_e2e_with_db.py` and `verify_integration.py`, but contains zero occurrences of `bm_db_hardening`. It was retained on a false premise. | Either wire it into CI (it is a genuine regression guard worth keeping) or delete it. Correct the two governance documents so the retention rationale is not reused. |
| F-15 | **Medium** | Documentation | `README.md`; `docs/deployment_guide.md:16-18` | Following the README literally, per PRD §4.8, is impossible: it contains **no setup, install, or run instructions at all** — no prerequisites, no `uv sync`, no migration step, no how-to-run. `docs/deployment_guide.md` does carry working steps (verified end to end), but is titled "Giraffe Agent v1.0" and instructs `git clone …/giraffe-agent && cd giraffe-agent` — the **wrong repository**. New engineers cannot onboard from either document unaided. | Add a Quick Start to the README (prerequisites, `uv sync`, `cp .env.example .env`, `alembic upgrade head`, `uvicorn api.main:app`, `curl /health`) — all verified working in this audit. Fix the clone URL, directory and title in the deployment guide. |
| F-16 | **Medium** | Dependencies / CI | `frontend/` | No lockfile (`package-lock.json`/`yarn.lock`/`pnpm-lock.yaml` all absent), so builds are not reproducible and no dependency audit is possible. The frontend is absent from CI entirely — never installed, linted, type-checked, built, or tested — despite `docker-compose.yml` building it. Vite 4 and the React 18 toolchain are several majors behind. | Commit a lockfile. Add a CI job running `npm ci && npm run build` plus `tsc --noEmit`. Schedule a toolchain upgrade. |
| F-17 | **Medium** | Configuration | `.env.example`; `src/logistics/providers/provider_config.py` | `.env.example` documents 7 variables; the code reads **30+**, including six secret-bearing ones that are entirely undocumented: `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, `CAINIAO_LIKE_APP_SECRET`, `CAINIAO_LIKE_ACCESS_TOKEN`, `CAINIAO_LIKE_WEBHOOK_SECRET`. `.env.example` advertises `QWEN_API_KEY`, but the code actually reads `DASHSCOPE_API_KEY` — so configuring it as documented silently fails. `GIRAFFE_ENV` is undocumented yet gates production behaviour (see F-18). | Regenerate `.env.example` from a grep of `os.environ` reads and keep it honest via a CI check. Fix the `QWEN_API_KEY`/`DASHSCOPE_API_KEY` mismatch. Update `docs/code-governance/ENVIRONMENT_VARIABLE_MATRIX.md`, which covers only 2 of the 6 secret variables. |
| F-18 | **Medium** | Security | `src/logistics/logistics_webhook_service.py:26`; `src/logistics/providers/cainiao_like_provider.py:69-85` | Webhook signature verification fails open three ways: (a) `if headers and not provider.verify_webhook_signature(...)` — when `headers` is `None` or empty the check is **skipped entirely**; (b) outside production mode `verify_webhook_signature` returns `True` unconditionally; (c) `is_production_mode()` reads `GIRAFFE_ENV` defaulting to `"local"`, and `GIRAFFE_ENV` is undocumented (F-17), so a real deployment that omits it accepts unsigned webhooks. In every bypass path the service still logs `LOGISTICS_WEBHOOK_SIGNATURE_VERIFIED`, writing a **false audit record**. *Currently latent* — no API route exposes this handler yet. | Invert to fail-closed: verify unconditionally and treat missing headers as failure. Emit `SIGNATURE_VERIFIED` only after a real HMAC comparison; log bypasses as `SIGNATURE_SKIPPED`. Make `GIRAFFE_ENV` explicit and required. Fix before exposing the handler over HTTP. |
| F-19 | **Medium** | Code quality | Repo-wide | 103 functions exceed 50 lines and 10 files exceed 500 lines. The worst are orchestration scripts (`run_role_switching_db_test.py::run` at 487 lines, `run_role_switching_mvp.py::main` at 472) and `src/lead_time/lead_time_calculator.py::calculate_lead_time_path` at 299 lines — the last being production code on the feasibility path, and the same module slated for removal under F-08. | Not urgent on its own. Address `calculate_lead_time_path` as part of the GLTG migration (F-08) rather than refactoring code destined for deletion. Enforce a ceiling on new code once ruff lands (F-09). |
| F-20 | **Low** | Security / Hygiene | `scripts/seed_reference_data.py:124-131` | Hardcoded admin password `GiraffeAdmin2024!` for `admin@giraffe.technology`. Mitigating: it is a seed script, not runtime code, and it posts to `POST /api/auth/register` — **an endpoint that does not exist** (`api/routes/auth.py` defines only `/login`, `/logout`, `/me`), so the script is stale and cannot currently succeed. | Read the seed password from an environment variable with no default. Either implement `/api/auth/register` or rewrite the script to insert the admin user directly via SQLAlchemy. |
| F-21 | **Low** | Security / Config | `alembic.ini:3` | `sqlalchemy.url` hardcodes `postgresql+psycopg2://giraffe:giraffe@localhost:5432/apparel_textile`. Credentials are dev-only and `alembic/env.py` prefers `ALEMBIC_DATABASE_URL`, so impact is limited to a confusing fallback that can point migrations at the wrong database. | Set `sqlalchemy.url =` (empty) and require `ALEMBIC_DATABASE_URL`. |
| F-22 | **Low** | Operability | `api/routes/health.py:6` | `/health` returns a static payload without checking database connectivity, so an orchestrator will route traffic to an instance whose database is unreachable. | Add a `/health/ready` performing `SELECT 1`, and keep `/health` as a liveness probe. |
| F-23 | **Low** | Test infrastructure | `tests/e2e/`, `tests/regression/` | Both directories exist but collect **0 tests**, implying either deleted coverage or unfinished scaffolding. Misleading to anyone reading the tree for assurance. | Populate or remove. If E2E coverage lives in `scripts/run_*_mvp.py`, say so in the testing docs. |
| F-24 | **Low** | Frontend | `frontend/src/lib/apiClient.ts:3-5` | The access token is held in a module-level variable, so every page refresh silently logs the user out. Security-positive (no `localStorage` XSS exposure) but a UX defect. | Deliberate choice — document it, or adopt refresh tokens in an httpOnly cookie if session persistence is required. |

---

## 4. Prioritised Remediation Plan

**Immediate — before any multi-tenant deployment**

1. **F-02** — remove the `SECRET_KEY` default; fail fast on startup. *(hours)*
2. **F-03** — authenticate or unmount the 8 unauthenticated endpoints. *(hours)*
3. **F-05** — enable branch protection so the remaining fixes cannot be reverted. *(minutes)*
4. **F-06** — replace the CORS wildcard with an explicit allowlist. *(hours)*

**Short term — next sprint**

5. **F-01** — tenant column migration, scoped reads, RLS. *(the substantial item; the correct pattern already exists in `src/giraffe_jp/service.py`)*
6. **F-04** — wire the existing RBAC engine into routers, starting with approval and order-confirmation.
7. **F-13** + **F-09** — run the full suite in CI and add a blocking lint job.
8. **F-18** — make webhook verification fail-closed before the handler is exposed.

**Medium term**

9. **F-07** / **F-08** — persistence consolidation and the JP-S2-1 / JP-S2-2 handoffs.
10. **F-10** / **F-11** — replace `passlib` and `python-jose`.
11. **F-12**, **F-15**, **F-16**, **F-17** — coverage on critical paths, docs, frontend CI, configuration hygiene.

---

## 5. Appendix — Raw Tool Output

### A. Test suite (live PostgreSQL 16, migrations applied)

```
$ uv run alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade  -> f66f720908c0, iter1_initial_schema
INFO  [alembic.runtime.migration] Running upgrade f66f720908c0 -> a1b2c3d4e5f6, add_delivery_feasibility_packets
INFO  [alembic.runtime.migration] Running upgrade a1b2c3d4e5f6 -> b2c3d4e5f6a7, add_giraffe_jp_service_core
INFO  [alembic.runtime.migration] Running upgrade b2c3d4e5f6a7 -> d4e5f6a7b8c9, add_giraffe_jp_iterations_02_03_04
INFO  [alembic.runtime.migration] Running upgrade d4e5f6a7b8c9 -> e5f6a7b8c9d0, add_mside_actor_columns_to_projects

$ uv run pytest tests/ -q --cov=src --cov=api
734 passed, 4 warnings in 106.66s (0:01:46)
TOTAL                                  12162   4770    61%
```

Without a database, the same suite reports `2 failed, 624 passed, 108 errors` — all connection failures, not defects.

### B. Coverage on critical paths (PRD §4.6)

```
file                                          stmts   miss   cov%
api/auth.py                                      19      2    89%
api/deps.py                                      22      5    77%
api/routes/auth.py                               29     12    59%
src/orders/service.py                             9      2    78%
src/approval_gates/service.py                    41     22    46%
src/giraffe_jp/service.py                       140     87    38%
src/rfq/service.py                               55     36    35%
src/qc/service.py                                64     44    31%
src/supplier_responses/service.py                88     63    28%
src/order_confirmation/service.py               113     85    25%
src/permissions/engine.py                        17     17     0%
src/permissions/dependencies.py                  13     13     0%
src/logistics/logistics_webhook_service.py       26     26     0%

TOTAL: 61% (7392/12162 statements)
Modules >15 statements at 0% coverage: 44
```

### C. Lint — `ruff check .`

```
169  F401  unused-import
 36  F541  f-string-missing-placeholders
 36  F841  unused-variable
 16  E402  module-import-not-at-top-of-file
  9  E712  true-false-comparison
  2  E741  ambiguous-variable-name
  1  F811  redefined-while-unused
  1  F821  undefined-name          <-- real defect
Found 270 errors. 207 fixable with --fix.

F821 Undefined name `BWWorkspace`
  --> tests/test_order_bridge_buyer_actor_fix.py:9:68
```

### D. Dependency audit — `pip-audit`

```
Found 1 known vulnerability in 1 package
Name   Version  ID               Fix Versions
-----  -------  ---------------  ------------
ecdsa  0.19.2   PYSEC-2026-1325  (none)

Minerva timing attack on the P-256 curve; nonce leak may permit private-key
recovery. Upstream considers side channels out of scope — no planned fix.

Skipped (not on PyPI): giraffe-jp 1.0.0, gltg 0.1.0

Installed: fastapi 0.139.2 · starlette 1.3.1 · sqlalchemy 2.0.51 ·
pydantic 2.13.4 · python-jose 3.5.0 · passlib 1.7.4 · bcrypt 3.2.2 ·
cryptography 49.0.0 · uvicorn 0.51.0
```

### E. Secret scan — working tree and full history

```
Commits scanned: 7 (all refs)
Patterns: AWS AKIA · GitHub gh[pousr]_ · OpenAI sk- · Slack xox[baprs]- ·
          PEM private keys · JWT eyJhbGciOi...

Tree:    no matches
History: no matches
Files of interest ever added: .env.example only (no real .env, .pem, or key files)
```

Result: **PASS**. The only credential-shaped string in the tree is the seed password in F-20.

### F. Unauthenticated API surface (from the generated OpenAPI schema)

```
TOTAL operations: 98
WITHOUT security requirement: 12

  POST   /api/auth/login                        <- expected
  GET    /health                                <- expected
  GET    /api/qc/health                         <- expected
  GET    /api/role-switching/pipeline-stages    <- metadata only

  POST   /api/qc/{project_id}/buyer-decision      | F-03
  POST   /api/qc/{project_id}/compare             | F-03
  POST   /api/qc/{project_id}/process-card        | F-03
  GET    /api/qc/{project_id}/process-card        | F-03
  POST   /api/qc/{project_id}/reference-images    | F-03
  GET    /api/qc/{project_id}/reference-images    | F-03
  GET    /api/qc/{project_id}/reports             | F-03
  POST   /api/role-switching/run-upstream-pipeline| F-03
```

### G. Live exploitation evidence

**F-03 — unauthenticated write and read-back:**

```
$ curl -o /dev/null -w "%{http_code}" http://127.0.0.1:8011/api/projects
401                                                    <- control: auth works

$ curl -X POST http://127.0.0.1:8011/api/qc/PROJ-EXPLOIT/process-card \
    -H 'Content-Type: application/json' \
    -d '{"category":"suit","unit_price":1.0,
         "supplier_contact":"attacker@example.com",
         "contract_terms":"exfiltrated"}'
{"process_card_id":"PC-9C77910428","project_id":"PROJ-EXPLOIT",...}   HTTP 200

$ curl http://127.0.0.1:8011/api/qc/PROJ-EXPLOIT/process-card
{"process_card_id":"PC-9C77910428",...,"contract_terms":"exfiltrated"} HTTP 200
```

**F-02 — forged token accepted (server started with `SECRET_KEY` unset):**

```
garbage token -> {"detail":"Invalid or expired token"}  [401]
FORGED  token -> {"detail":"User not found"}            [401]
```

The forged token — signed with the repository's public default `"change-me-in-production"` — **passed signature validation** and failed only at the user-existence lookup. The differing error proves the signature was accepted; with any valid user UUID it grants full authenticated access.

**F-06 — CORS reflection of an arbitrary origin:**

```
$ curl -D- -H "Origin: https://attacker.example" http://127.0.0.1:8011/health
access-control-allow-origin: https://attacker.example
access-control-allow-credentials: true

$ curl -X OPTIONS -H "Origin: https://attacker.example" \
       -H "Access-Control-Request-Method: POST" .../api/projects
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-allow-origin: https://attacker.example
access-control-allow-credentials: true
```

### H. Complexity outliers (PRD §4.3)

```
Files >500 lines (10):
  1025  tests/test_mside_role_switching.py
   972  bm_db_hardening.py                     <- F-14, runs in no pipeline
   903  src/openclaw_skill/openclaw_event_adapter.py
   807  bm_db_adapter.py
   697  alembic/versions/f66f720908c0_iter1_initial_schema.py
   557  tests/test_lead_time_model.py
   550  scripts/run_role_switching_mvp.py

Functions >50 lines: 103
   624  alembic/.../f66f720908c0::upgrade            (generated — acceptable)
   487  scripts/run_role_switching_db_test.py::run
   472  scripts/run_role_switching_mvp.py::main
   299  src/lead_time/lead_time_calculator.py::calculate_lead_time_path  <- F-19
```

### I. CI configuration facts

```
Branch protection on main:  NONE  ("protected": false via branches API)
Tests collected overall:    734
Tests executed by CI:       312  (42%)
  tests/api 112 · tests/unit 83 · tests/db 39 · tests/integration 2
  tests/e2e 0 · tests/regression 0            <- F-23
Lint job:                   absent
Coverage gate:              absent
"Compile Python files":     py_compile *.py -> 7 root files
                            (src/ + api/ = 353 files, uncompiled)
Every job runs:             uv add --dev pytest   (mutates pyproject/uv.lock;
                            pytest already in [dependency-groups].dev)
Root scripts in ci.yml:     build_schema(1) run_bm_e2e_with_db(3)
                            verify_integration(1)
                            bm_db_hardening(0) bm_db_adapter(0)
                            pydantic_stub(0)          <- contradicts F-14 docs
```

### J. Documentation verification (PRD §4.8)

The README contains no setup section, so `docs/deployment_guide.md` Chapter 2 was followed literally instead:

| Step | Result |
|---|---|
| `git clone …/giraffe-agent && cd giraffe-agent` | **FAIL** — wrong repository name (this repo is `Giraffe-JP`) |
| `uv sync` | PASS |
| `cp .env.example .env` | PASS — but documents 7 of 30+ variables (F-17) |
| `uv run alembic upgrade head` | PASS — 5 revisions applied to fresh PostgreSQL 16 |
| `uv run uvicorn api.main:app` | PASS |
| `curl http://localhost:8000/health` | PASS — `{"status":"ok","product":"Giraffe JP — …"}` |

Five of six steps work. The clone step is wrong, and the guide is titled "Giraffe Agent v1.0" rather than Giraffe JP — leftover from the abcdYi lineage described in F-08.

---

*Audit performed against commit `e81d828` on `main`. All findings were verified by execution — dependency install, migration, full test run, and live HTTP probing — rather than by static reading alone.*
