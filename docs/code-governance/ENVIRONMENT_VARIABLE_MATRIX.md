# Environment Variable Matrix — Giraffe-JP (Stage 1)

| Variable | Repository | Reader | Default | Production required | Secret | Obsolete |
|---|---|---|---|---|---|---|
| DATABASE_URL | Giraffe-JP | `src/db/base.py`, `src/db/config.py` | local PG dsn (`apparel_textile`) | yes | contains credentials | no — but DB name still mirrors abcdYi's; REVIEW for JP deployments |
| ALEMBIC_DATABASE_URL | Giraffe-JP | CI / alembic sync path | unset | migration jobs | contains credentials | no |
| SECRET_KEY | Giraffe-JP | `src/db/base.py`, auth | placeholder | yes | yes | no |
| ALGORITHM / ACCESS_TOKEN_EXPIRE_MINUTES | Giraffe-JP | auth | HS256 / 60 | no | no | no |
| LLM_PROVIDER / LLM_ENABLE_REAL_CALLS | Giraffe-JP | `src/llm/*` | stub / off (fail-closed) | no | no | no |
| OPENAI_API_KEY / QWEN_API_KEY / DASHSCOPE_API_KEY | Giraffe-JP | `src/llm/*`, QC | empty | only if provider enabled | yes | no |
| QWEN_TEXT_MODEL / QWEN_VISION_MODEL | Giraffe-JP | `src/qc/*` | provider defaults | no | no | no |
| QC_ALLOW_EXTERNAL_LLM / QC_ALLOW_CAD_TO_LLM / QC_ALLOW_BOM_TO_LLM | Giraffe-JP | `src/qc/*` | off (fail-closed) | no | no | no |
| GIRAFFE_ENV | Giraffe-JP | provider registries | development | yes | no | no |
| GIRAFFE_DB_MODE / GIRAFFE_DB_URL | Giraffe-JP | BM DB CI harness | off / unset | CI only | URL may embed credentials | no |
| BASE_URL | Giraffe-JP | smoke/e2e scripts | http://localhost:8000 | no | no | no |
| WECHAT_ENABLED / WHATSAPP_ENABLED | Giraffe-JP | `src/channels/*` | off | no | no | no |

## Removed in Stage 1

| Variable | Where | Reason |
|---|---|---|
| APP_ENV | `.env.example` | read by no code (grep-verified) |
| LOG_LEVEL | `.env.example` | read by no code |

## Rules verified

- No real secrets committed.
- Mock/live switches explicit and fail-closed (`LLM_ENABLE_REAL_CALLS`,
  `QC_ALLOW_*`, `GIRAFFE_DB_MODE`, channel `*_ENABLED` flags).
- Auto-send / communication policy remains human-gated (see
  `src/giraffe_jp/communication.py` policy tests) — unchanged by Stage 1.
- One variable per configuration concern; no duplicate-priority conflicts found.
