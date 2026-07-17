# Dead Code Removal Report — Giraffe-JP (Stage 1)

Every change was cross-verified with ripgrep string scan, import scan, route
registry, CI/deploy file scan, and a full-suite run after the change. No
deletion happened before the Phase A audit was written.

| Path | Reason | Replacement | Runtime references | Test references | Risk | Result |
|---|---|---|---|---|---|---|
| distribution name `abcdyi` + abcdYi description (pyproject) | wrong product identity inherited from wholesale copy | `giraffe-jp` + correct description | packaging metadata only | none asserting old name | LOW | FIXED |
| abcdYi OpenAPI title/description (`api/main.py`), `/health` product string, `main.py` banner | service claimed to be abcdYi in API docs, health payload, logs | Giraffe JP identity strings | string constants | `tests/api/test_health.py` updated in same change | LOW | FIXED |
| `structlog` dependency | zero imports repo-wide | — | none | none | LOW | DELETED |
| dev-dep double declaration (optional-dependencies.dev vs dependency-groups.dev, conflicting pytest floors) | duplicate + conflicting | single `[dependency-groups].dev` | — | — | LOW | MERGED |
| `tests/test_mside_role_switching.py::test_readme_mentions_role_switching` | asserted only that a keyword exists in README (PRD Phase E deletable category); was the only failing test on main after README repositioning | behavioral role-switching tests (79) remain | — | itself | NONE | DELETED |
| `APP_ENV`, `LOG_LEVEL` in `.env.example` | read by no code | — | none | none | NONE | DELETED |
| 10 root `*_REPORT/RESULT*.md` session reports | historical output presented as current | `docs/archive/` with ARCHIVED banner | none (grep-verified) | none | NONE | ARCHIVED |

## Explicitly NOT removed (with evidence)

| Path | Why kept |
|---|---|
| `libs/GLTG` (vendored GLTG engine) | live runtime imports: `src/services/delivery_feasibility_service.py`, `src/decision_packets/service.py`, `src/lead_time/gltg_adapter.py`; CI lead-time job depends on it. Removal requires the abcdYi-style GLTG HTTP-client migration → **Stage 2 handoff JP-S2-1**. This satisfies the acceptance clause "delete libs/GLTG **or provide explicit evidence it cannot be deleted**". |
| `src/lead_time/lead_time_calculator.py`, `path_enumerator.py` | pre-GLTG implementation abcdYi already replaced; here still on the runtime feasibility path + CI job → removed together with JP-S2-1 |
| copied abcdYi backend under `src/` (317 files; 142 diverged) | working runtime of this deployment; wholesale re-sync or deletion is forbidden (PRD §12.2/§12.16); extraction to a pinned abcdYi package dependency = **Stage 2 handoff JP-S2-2 (Option A)** |
| `bm_db_adapter.py`, `bm_db_hardening.py`, `build_schema.py`, `run_bm_e2e_with_db.py`, `verify_integration.py`, `pydantic_stub.py` (root) | live CI harness (`ci.yml`) |
| all security/tenant/approval/communication-policy tests | protected categories (PRD §6.E.2) |

## Net effect

- Product identity: correct everywhere (metadata, OpenAPI, health, banner).
- Dependencies (direct): 16 → 15 (−1; plus conflict resolved).
- Root markdown files: 15 → 4 (README, CHANGELOG, LICENSE_NOTICE, PATENT_NOTICE).
- Tests: 1 keyword test deleted; suite went from 734 passed/1 failed → 734 passed/0 failed.
- No business logic changed.
