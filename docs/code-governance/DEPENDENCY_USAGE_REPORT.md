# Dependency Usage Report — Giraffe-JP (Stage 1)

| Dependency | Class | Evidence / notes |
|---|---|---|
| gltg (path: `libs/GLTG`, editable) | runtime direct — **vendored, flagged** | imported by `src/services/delivery_feasibility_service.py`, `src/decision_packets/service.py`, `src/lead_time/gltg_adapter.py`. Kept this stage with evidence; replacement by GLTG HTTP client = Stage 2 handoff JP-S2-1 |
| fastapi | runtime direct | `api/` app |
| uvicorn[standard] | runtime direct | serve entry |
| pydantic[email] | runtime direct | schemas |
| pydantic-settings | runtime direct | `src/db/base.py` Settings |
| sqlalchemy | runtime direct | ORM + async engine |
| alembic | runtime direct | migrations |
| asyncpg | runtime direct | async PG driver |
| psycopg2-binary | runtime direct (tooling) | sync driver for Alembic (`ALEMBIC_DATABASE_URL`) and CI harness — deliberate two-driver split, documented |
| python-jose[cryptography] | runtime direct | JWT auth |
| passlib[bcrypt] | runtime direct | password hashing |
| python-multipart | runtime direct | `OAuth2PasswordRequestForm` login |
| httpx | runtime direct | HTTP clients + test client |
| bcrypt (<4 pin) | runtime direct | passlib compatibility pin |

Dev group (`[dependency-groups].dev`): pytest, pytest-asyncio, pytest-cov — dev only.

## Removed in Stage 1

| Dependency | Prior class | Reason |
|---|---|---|
| structlog | unused | zero imports repo-wide |

## Duplicate / conflicting declarations fixed

- Dev dependencies were declared in BOTH `[project.optional-dependencies].dev`
  (`pytest>=8.2.0`) and `[dependency-groups].dev` (`pytest>=9.1.0`) — a real
  version conflict. Consolidated into `[dependency-groups].dev` only.

## Security-flagged (PRD watchlist) status

- No `eval-type-backport`, `aiosqlite`, `jinja2`, `python-dotenv` present.
- Two PostgreSQL drivers kept with documented reason (async app / sync alembic).
- `gltg` vendoring is the largest remaining governance issue → JP-S2-1.
