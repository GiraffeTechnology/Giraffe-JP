# Giraffe JP Backend — Iterations 02–04 Implementation Report

## 1. Summary

This report covers the implementation of three backend iterations extending the Giraffe JP service-led C2B2M platform. All three iterations were built additively on top of the Iteration 01 service core (service nodes, confirmation requests, customer-service tasks) without modifying existing tables or routes.

| Iteration | Feature | Status |
|---|---|---|
| 02 | Message Category Auto-Send Permissions | Complete |
| 03 | Web Dialog and Email Communication Layer | Complete |
| 04 | Formalwear C2B2M Order Extension | Complete |

All changes are on branch `feature/giraffe-jp-communication-formalwear`.

---

## 2. Files Changed

### Modified Files

| File | Change |
|---|---|
| `src/execution_graph/event_types.py` | Added 13 new event type constants |
| `src/db/models/giraffe_jp.py` | Added 7 new SQLAlchemy models |
| `src/db/models/__init__.py` | Added imports and `__all__` entries for 7 new models |
| `src/giraffe_jp/schemas.py` | Extended with schemas for Iterations 02–04 |
| `api/main.py` | Registered 3 new routers |

### New Files

| File | Purpose |
|---|---|
| `src/giraffe_jp/message_permissions.py` | Auto-send permission service + 22 default category definitions |
| `src/giraffe_jp/conversations.py` | Conversation thread, inbound message, and outbound draft service |
| `src/giraffe_jp/formalwear.py` | Formalwear order profile and C2B2M role edge service |
| `api/routes/giraffe_jp_message_permissions.py` | 4 routes for message category permissions |
| `api/routes/giraffe_jp_conversations.py` | 10 routes for threads, messages, and outbound drafts |
| `api/routes/giraffe_jp_formalwear.py` | 8 routes for formalwear profiles and role edges |
| `alembic/versions/c3d4e5f6a7b8_add_giraffe_jp_iter02_03_04.py` | DB migration for all 7 new tables |
| `tests/unit/test_giraffe_jp_message_permissions.py` | 8 unit tests for auto-send permission logic |
| `tests/unit/test_giraffe_jp_formalwear_rules.py` | 8 unit tests for schema validation and hollow-to-hem defaults |
| `tests/unit/test_giraffe_jp_conversation_permissions.py` | 3 unit tests for outbound draft permission gate |
| `tests/api/test_giraffe_jp_message_permissions.py` | 8 API integration tests |
| `tests/api/test_giraffe_jp_conversations.py` | 14 API integration tests |
| `tests/api/test_giraffe_jp_formalwear.py` | 15 API integration tests |
| `docs/giraffe_jp_service_backend.md` | Architecture and iteration reference documentation |
| `docs/giraffe_jp_api_reference.md` | Full API reference for all Giraffe JP routes |

---

## 3. New Models

All models are in `src/db/models/giraffe_jp.py`. All include `tenant_id` for tenant isolation.

### `GiraffeJPMessageCategoryPermission`
Controls whether each message category is auto-sent or requires human confirmation.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | Scoped to tenant |
| `category_id` | String | e.g. `CUSTOMER_ORDER_RECEIVED_UPDATE` |
| `category_name` | String | Human-readable label |
| `direction` | String | `CUSTOMER` / `SUPPLIER` / `MODEL_PARTNER` / `INTERNAL` |
| `channel` | String | `WEB_DIALOG` / `EMAIL` / `ANY` |
| `auto_send` | Boolean | Whether this category is auto-sent |
| `is_active` | Boolean | Whether this category is active |
| `description` | String | Optional notes |

Unique constraint: `(tenant_id, category_id)`.

### `GiraffeJPConversationThread`
A communication thread between the platform and a customer, supplier, or model partner.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | |
| `thread_type` | String | `CUSTOMER` / `SUPPLIER` / `MODEL_PARTNER` / `INTERNAL` |
| `channel` | String | `WEB_DIALOG` / `EMAIL` |
| `status` | String | `OPEN` / `CLOSED` |
| `project_id` | UUID | Optional project link |
| `order_id` | UUID | Optional order link |
| `participant_id` | UUID | Optional participant link |
| `customer_id` | UUID | Optional customer link |

### `GiraffeJPMessage`
Individual inbound or outbound message record in a thread.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | |
| `thread_id` | UUID FK | Parent conversation thread |
| `direction` | String | `INBOUND` / `OUTBOUND` |
| `sender_type` | String | `CUSTOMER` / `SUPPLIER` / `MODEL_PARTNER` / `CS_STAFF` / `AGENT` / `SYSTEM` |
| `sender_id` | UUID | Optional sender reference |
| `message_text` | Text | Message body |
| `category_id` | String | Optional category label |
| `sent_at` | DateTime | When the message was sent |

### `GiraffeJPOutboundMessageDraft`
Pending outbound message requiring either auto-send or human approval before delivery.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | |
| `thread_id` | UUID FK | Parent conversation thread |
| `category_id` | String | Message category |
| `message_text` | Text | Draft body |
| `channel` | String | `WEB_DIALOG` / `EMAIL` |
| `status` | String | `DRAFT` / `AUTO_SENT` / `PENDING_HUMAN_CONFIRMATION` / `APPROVED_SENT` / `REJECTED` / `FAILED` |
| `auto_send_allowed` | Boolean | Result of permission check at creation time |
| `created_by` | String | `AGENT` / `CS_STAFF` / `SYSTEM` |
| `sent_at` | DateTime | Populated when sent |
| `approved_by_user_id` | UUID | Populated when approved |
| `service_node_id` | UUID | Optional link |
| `confirmation_request_id` | UUID | Optional link |
| `message_id` | UUID | Link to created `GiraffeJPMessage` after send |

### `GiraffeJPMessageDeliveryLog`
Delivery status record for each outbound draft.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | |
| `draft_id` | UUID FK | Parent outbound draft |
| `delivery_status` | String | `MOCK_SENT` / `PENDING_HUMAN_CONFIRMATION` / `FAILED` |
| `channel` | String | |
| `delivered_at` | DateTime | |
| `failure_reason` | String | Optional |

### `GiraffeJPFormalwearOrderProfile`
Japan formalwear-specific order data linked to a project.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | |
| `project_id` | UUID | Linked project |
| `order_id` | UUID | Optional linked order |
| `product_category` | String | One of 5 valid categories |
| `occasion` | String | Wear occasion |
| `use_date` | DateTime | Intended wear date |
| `status` | String | `DRAFT` / `ACTIVE` / `CLOSED` |
| `budget_min_jpy` | Numeric(12,0) | Minimum budget in JPY |
| `budget_max_jpy` | Numeric(12,0) | Maximum budget in JPY |
| `color_preference` | String | Optional |
| `fit_preference` | String | Optional |
| `hollow_to_hem_required` | Boolean | Measurement requirement flag |
| `model_try_on_required` | Boolean | Default `true` |
| `local_alteration_possible` | Boolean | Default `true` |
| `notes` | Text | Optional |

### `GiraffeJPC2B2MRoleEdge`
C2B2M role relationship edge between platform actors for a project.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `tenant_id` | UUID FK | |
| `project_id` | UUID | Linked project |
| `from_actor_type` | String | e.g. `JP_CUSTOMER` / `GIRAFFE_JP` |
| `from_actor_id` | UUID | Optional actor ID |
| `from_role` | String | e.g. `B_SIDE` / `UPSTREAM_B_SIDE` |
| `to_actor_type` | String | e.g. `GIRAFFE_JP` / `SUPPLIER` |
| `to_actor_id` | UUID | Optional actor ID |
| `to_role` | String | e.g. `MAIN_M_SIDE` / `UPSTREAM_M_SIDE` |
| `edge_type` | String | `DEFAULT` / `CUSTOM` |

---

## 4. New Routes

All routes are prefixed with `/api/giraffe-jp` and require `Authorization: Bearer <jwt_token>`.

### Iteration 02 — Message Category Permissions (`giraffe_jp_message_permissions.py`)

| Method | Path | Description |
|---|---|---|
| GET | `/message-category-permissions` | List all category permissions for tenant |
| GET | `/message-category-permissions/{category_id}` | Get a specific category permission |
| PATCH | `/message-category-permissions/{category_id}` | Update `auto_send` or `is_active` |
| POST | `/message-category-permissions/seed-defaults` | Upsert 22 default categories for tenant |

### Iteration 03 — Conversations and Outbound Drafts (`giraffe_jp_conversations.py`)

| Method | Path | Description |
|---|---|---|
| POST | `/conversations` | Create a conversation thread |
| GET | `/conversations` | List all conversation threads |
| GET | `/conversations/{id}` | Get thread detail |
| GET | `/conversations/{id}/messages` | List all messages in thread |
| POST | `/conversations/{id}/messages/inbound` | Record an inbound message |
| POST | `/outbound-drafts` | Create outbound draft (auto-sends or pends) |
| GET | `/outbound-drafts` | List outbound drafts |
| GET | `/outbound-drafts/{id}` | Get draft detail |
| POST | `/outbound-drafts/{id}/approve-send` | Approve and send a pending draft |
| POST | `/outbound-drafts/{id}/reject` | Reject a pending draft |

### Iteration 04 — Formalwear and Role Edges (`giraffe_jp_formalwear.py`)

| Method | Path | Description |
|---|---|---|
| POST | `/formalwear/order-profiles` | Create a formalwear order profile |
| GET | `/formalwear/order-profiles` | List formalwear order profiles |
| GET | `/formalwear/order-profiles/{id}` | Get profile detail |
| PATCH | `/formalwear/order-profiles/{id}` | Update a profile |
| POST | `/c2b2m/role-edges` | Create a role edge |
| GET | `/c2b2m/role-edges` | List role edges (filter: project_id) |
| GET | `/c2b2m/role-edges/{id}` | Get edge detail |
| POST | `/c2b2m/projects/{id}/initialize-default-edges` | Initialize default C2B2M edges for a project |

---

## 5. New Migration

**File:** `alembic/versions/c3d4e5f6a7b8_add_giraffe_jp_iter02_03_04.py`

**Revision:** `c3d4e5f6a7b8`
**Down revision:** `b2c3d4e5f6a7` (Iteration 01 migration)

Tables created (in dependency order):

1. `giraffe_jp_message_category_permissions` — unique on `(tenant_id, category_id)`
2. `giraffe_jp_conversation_threads` — indexed on `tenant_id`, `project_id`, `order_id`
3. `giraffe_jp_messages` — FK to `giraffe_jp_conversation_threads`
4. `giraffe_jp_outbound_message_drafts` — FK to `giraffe_jp_conversation_threads`
5. `giraffe_jp_message_delivery_logs` — FK to `giraffe_jp_outbound_message_drafts`
6. `giraffe_jp_formalwear_order_profiles` — indexed on `tenant_id`, `project_id`
7. `giraffe_jp_c2b2m_role_edges` — indexed on `tenant_id`, `project_id`

The migration uses `postgresql.JSONB` for JSON columns where applicable and is fully reversible via `downgrade()`.

---

## 6. New Tests

### Unit Tests (no database required)

| File | Tests | Coverage |
|---|---|---|
| `tests/unit/test_giraffe_jp_message_permissions.py` | 8 | `is_auto_send_allowed()` — all 4 rule branches, edge cases |
| `tests/unit/test_giraffe_jp_formalwear_rules.py` | 8 | Schema validation, `hollow_to_hem_required` defaults, `model_try_on_required` default |
| `tests/unit/test_giraffe_jp_conversation_permissions.py` | 3 | Auto-send path, pending path, unknown category path |

### API Integration Tests (PostgreSQL required)

| File | Tests | Coverage |
|---|---|---|
| `tests/api/test_giraffe_jp_message_permissions.py` | 8 | Seed defaults, list, get, update, tenant isolation |
| `tests/api/test_giraffe_jp_conversations.py` | 14 | Thread CRUD, inbound messages, auto-send, approve, reject, tenant isolation |
| `tests/api/test_giraffe_jp_formalwear.py` | 15 | Profile CRUD, hollow-to-hem defaults, role edges, duplicate prevention, tenant isolation |

---

## 7. Test Results

### Unit Tests

```
uv run pytest tests/unit/ -v -m "not integration"
...
======================== 69 passed, 2 warnings in 0.18s ========================
```

All 69 unit tests pass (50 pre-existing + 19 new Giraffe JP unit tests).

### API Integration Tests

Not run — PostgreSQL is not available in this environment. API tests require a live database and are expected to pass once the migration is applied against a running PostgreSQL instance.

To run:
```bash
uv run pytest tests/api/test_giraffe_jp_message_permissions.py -v
uv run pytest tests/api/test_giraffe_jp_conversations.py -v
uv run pytest tests/api/test_giraffe_jp_formalwear.py -v
```

---

## 8. Known Limitations

- **No real email delivery.** Outbound messages are recorded as `MOCK_SENT`. No SMTP or transactional email provider is integrated in this iteration. The delivery log captures `MOCK_SENT` status to signal this.

- **Auto-send channel matching uses string equality.** The `is_auto_send_allowed()` function checks `perm.channel in ("ANY", channel)`. If the permission record stores `ANY`, it matches any channel. Channel mismatches return `False` conservatively.

- **`approved_by_user_id` set from JWT context.** The approve-send route sets `approved_by_user_id` from the authenticated user's ID. If the JWT payload does not include a resolvable user ID, this field will be empty.

- **C2B2M edge deduplication is at-creation-time only.** The `_edge_exists()` check prevents the default initialization endpoint from creating duplicates. Manual `POST /c2b2m/role-edges` calls are not deduplicated — callers are responsible for avoiding duplicate custom edges.

- **`hollow_to_hem_required` default applies at creation only.** If a profile is patched via `PATCH /formalwear/order-profiles/{id}` after creation, the default logic does not re-apply. The caller must explicitly set the field.

- **`budget_min_jpy` / `budget_max_jpy` are stored as integers (Numeric 12,0).** Sub-yen precision is not supported, matching Japanese currency conventions.

- **No pagination.** All list endpoints return all records for the tenant. Pagination should be added before high-volume use.

---

## 9. Remaining Iteration 05+ Work

The following features are planned but not yet implemented:

| Feature | Description |
|---|---|
| Message category permission templates | Pre-configured permission sets by business scenario |
| QC raw evidence repository | Node-based raw photo/document evidence linked to `QCRecord` |
| Measurement profile interface | Customer measurement record capture (no raw video upload) |
| Digital human profile interface | Digital fit simulation profile |
| Local model try-on scheduling | Booking and evidence submission for local model try-on sessions |
| Segmented logistics adapters | China domestic → cross-border → Japan arrival → final delivery service nodes |
| Marketplace supplier abstraction layer | Unified qualified production partner search interface |
| Giraffe JP supplier memory extension | Formalwear-specific supplier trait history (sizing reliability, evidence quality, try-on cooperation) |
| Integrated E2E readiness script | End-to-end 3× readiness test across all Giraffe JP iterations |
| Pagination on all list endpoints | Cursor or offset pagination for production-scale use |
| Real email delivery integration | Transactional email provider integration for `EMAIL` channel threads |
