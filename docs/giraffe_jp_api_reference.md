# Giraffe JP API Reference

All routes require `Authorization: Bearer <jwt_token>` unless noted.

Base prefix: `/api/giraffe-jp`

---

## Service Core (Iteration 01)

### Service Nodes

| Method | Path | Description |
|---|---|---|
| POST | `/service-nodes` | Create a service node |
| GET | `/service-nodes` | List service nodes (filter: project_id, order_id, status) |
| GET | `/service-nodes/{id}` | Get service node detail |
| PATCH | `/service-nodes/{id}` | Update a service node |

### Confirmation Requests

| Method | Path | Description |
|---|---|---|
| POST | `/confirmation-requests` | Create a confirmation request |
| GET | `/confirmation-requests` | List confirmation requests (filter: service_node_id, status) |
| GET | `/confirmation-requests/{id}` | Get confirmation request detail |
| POST | `/confirmation-requests/{id}/confirm` | Confirm a request |
| POST | `/confirmation-requests/{id}/reject` | Reject a request |
| POST | `/confirmation-requests/{id}/escalate` | Escalate a request |

### Customer-Service Tasks

| Method | Path | Description |
|---|---|---|
| GET | `/customer-service/tasks` | List customer-service tasks (filter: status) |
| POST | `/customer-service/tasks` | Create a customer-service task |
| POST | `/customer-service/tasks/{id}/start` | Start a task (OPEN → IN_PROGRESS) |
| POST | `/customer-service/tasks/{id}/complete` | Complete a task (IN_PROGRESS → DONE) |
| POST | `/customer-service/tasks/{id}/escalate` | Escalate a task (→ ESCALATED) |

---

## Message Category Auto-Send Permissions (Iteration 02)

| Method | Path | Description |
|---|---|---|
| GET | `/message-category-permissions` | List all category permissions for tenant |
| GET | `/message-category-permissions/{category_id}` | Get a specific category permission |
| PATCH | `/message-category-permissions/{category_id}` | Update auto_send or is_active |
| POST | `/message-category-permissions/seed-defaults` | Upsert 22 default categories for tenant |

### PATCH body

```json
{
  "auto_send": true,
  "is_active": true,
  "description": "Optional notes"
}
```

All fields are optional. Only provided fields are updated.

### Default Categories

Seeded by direction:

**CUSTOMER (9):** `CUSTOMER_ORDER_RECEIVED_UPDATE` (true), `CUSTOMER_REQUIREMENT_CONFIRMED_UPDATE` (true), `CUSTOMER_SUPPLIER_SEARCH_UPDATE` (true), `CUSTOMER_PRODUCTION_STARTED_UPDATE` (true), `CUSTOMER_QC_REVIEW_UPDATE` (true), `CUSTOMER_LOGISTICS_UPDATE` (true), `CUSTOMER_PRICE_CONFIRMATION` (false), `CUSTOMER_DELIVERY_COMMITMENT` (false), `CUSTOMER_FINAL_APPROVAL` (false)

**SUPPLIER (9):** `SUPPLIER_BASIC_PROGRESS_QUESTION` (true), `SUPPLIER_QC_EVIDENCE_REQUEST` (true), `SUPPLIER_LOGISTICS_NUMBER_REQUEST` (true), `SUPPLIER_BASIC_CUSTOMIZATION_QUESTION` (true), `SUPPLIER_PRICE_QUOTE_REQUEST` (false), `SUPPLIER_PRICE_CONFIRMATION` (false), `SUPPLIER_ORDER_PLACEMENT` (false), `SUPPLIER_PAYMENT_RELATED` (false), `SUPPLIER_DISPUTE_OR_CLAIM` (false)

**MODEL_PARTNER (4):** `MODEL_PARTNER_AVAILABILITY_REQUEST` (true), `MODEL_PARTNER_SCHEDULE_CONFIRMATION` (false), `MODEL_PARTNER_EVIDENCE_REQUEST` (true), `MODEL_PARTNER_FEE_CONFIRMATION` (false)

---

## Conversation Threads & Outbound Drafts (Iteration 03)

### Conversation Threads

| Method | Path | Description |
|---|---|---|
| POST | `/conversations` | Create a conversation thread |
| GET | `/conversations` | List all conversation threads |
| GET | `/conversations/{id}` | Get thread detail |
| GET | `/conversations/{id}/messages` | List all messages in thread |
| POST | `/conversations/{id}/messages/inbound` | Record an inbound message |

**POST /conversations body:**
```json
{
  "thread_type": "CUSTOMER",
  "channel": "WEB_DIALOG",
  "project_id": "<uuid>",
  "order_id": "<uuid>",
  "participant_id": "<uuid>",
  "customer_id": "<uuid>"
}
```

thread_type: `CUSTOMER` | `SUPPLIER` | `MODEL_PARTNER` | `INTERNAL`
channel: `WEB_DIALOG` | `EMAIL`

**POST /conversations/{id}/messages/inbound body:**
```json
{
  "sender_type": "CUSTOMER",
  "sender_id": "<uuid>",
  "message_text": "Hello, I'd like to order a formal dress.",
  "category_id": "CUSTOMER_ORDER_RECEIVED_UPDATE"
}
```

sender_type: `CUSTOMER` | `SUPPLIER` | `MODEL_PARTNER` | `CS_STAFF` | `AGENT` | `SYSTEM`

### Outbound Message Drafts

| Method | Path | Description |
|---|---|---|
| POST | `/outbound-drafts` | Create outbound draft (auto-sends or pends based on category permission) |
| GET | `/outbound-drafts` | List outbound drafts |
| GET | `/outbound-drafts/{id}` | Get draft detail |
| POST | `/outbound-drafts/{id}/approve-send` | Approve and send a pending draft |
| POST | `/outbound-drafts/{id}/reject` | Reject a pending draft |

**POST /outbound-drafts body:**
```json
{
  "thread_id": "<uuid>",
  "category_id": "CUSTOMER_PRICE_CONFIRMATION",
  "message_text": "Please confirm the price of ¥120,000.",
  "channel": "WEB_DIALOG",
  "created_by": "AGENT",
  "service_node_id": "<uuid>",
  "confirmation_request_id": "<uuid>"
}
```

**Draft statuses:** `DRAFT` → `AUTO_SENT` | `PENDING_HUMAN_CONFIRMATION` → `APPROVED_SENT` | `REJECTED` | `FAILED`

Only drafts in `PENDING_HUMAN_CONFIRMATION` or `DRAFT` can be approved.

---

## Formalwear Order Profiles & C2B2M Role Edges (Iteration 04)

### Formalwear Order Profiles

| Method | Path | Description |
|---|---|---|
| POST | `/formalwear/order-profiles` | Create a formalwear order profile |
| GET | `/formalwear/order-profiles` | List formalwear order profiles |
| GET | `/formalwear/order-profiles/{id}` | Get profile detail |
| PATCH | `/formalwear/order-profiles/{id}` | Update a profile |

**POST /formalwear/order-profiles body:**
```json
{
  "project_id": "<uuid>",
  "product_category": "BRIDALWEAR",
  "occasion": "Wedding ceremony",
  "use_date": "2026-10-01T00:00:00Z",
  "budget_min_jpy": 80000,
  "budget_max_jpy": 150000,
  "color_preference": "Ivory",
  "fit_preference": "FITTED",
  "hollow_to_hem_required": null,
  "model_try_on_required": true,
  "local_alteration_possible": true
}
```

Valid `product_category` values: `FORMAL_DRESS`, `WOMENS_SUIT`, `BRIDALWEAR`, `LIGHT_WEDDING_DRESS`, `RECEPTION_DRESS`

If `hollow_to_hem_required` is null/omitted and product_category is `FORMAL_DRESS`, `BRIDALWEAR`, or `LIGHT_WEDDING_DRESS`, the service defaults it to `true`.

### C2B2M Role Edges

| Method | Path | Description |
|---|---|---|
| POST | `/c2b2m/role-edges` | Create a role edge |
| GET | `/c2b2m/role-edges` | List role edges (filter: project_id) |
| GET | `/c2b2m/role-edges/{id}` | Get edge detail |
| POST | `/c2b2m/projects/{id}/initialize-default-edges` | Initialize default C2B2M edges for a project |

**POST /c2b2m/projects/{id}/initialize-default-edges body:**
```json
{
  "order_id": "<uuid>",
  "customer_id": "<uuid>",
  "supplier_id": "<uuid>"
}
```

Creates at most 2 edges:
1. `JP_CUSTOMER → GIRAFFE_JP` (B_SIDE → MAIN_M_SIDE) — always created if not exists
2. `GIRAFFE_JP → SUPPLIER` (UPSTREAM_B_SIDE → UPSTREAM_M_SIDE) — only if `supplier_id` is provided

Duplicate edges are silently skipped. Returns only newly created edges.

---

## Execution Graph Event Types

| Event | Trigger |
|---|---|
| `SERVICE_NODE_CREATED` | Service node created |
| `SERVICE_NODE_UPDATED` | Service node updated |
| `CONFIRMATION_REQUEST_CREATED` | Confirmation request created |
| `CONFIRMATION_CONFIRMED` | Confirmation confirmed |
| `CONFIRMATION_REJECTED` | Confirmation rejected |
| `CONFIRMATION_ESCALATED` | Confirmation escalated |
| `CUSTOMER_SERVICE_TASK_CREATED` | CS task created |
| `CUSTOMER_SERVICE_TASK_STARTED` | CS task started |
| `CUSTOMER_SERVICE_TASK_COMPLETED` | CS task completed |
| `CUSTOMER_SERVICE_TASK_ESCALATED` | CS task escalated |
| `MESSAGE_CATEGORY_PERMISSIONS_SEEDED` | Default categories seeded |
| `MESSAGE_CATEGORY_PERMISSION_UPDATED` | Category auto_send or is_active changed |
| `CONVERSATION_THREAD_CREATED` | Conversation thread created |
| `INBOUND_MESSAGE_RECORDED` | Inbound message recorded |
| `OUTBOUND_DRAFT_CREATED` | Outbound draft created (any path) |
| `OUTBOUND_MESSAGE_AUTO_SENT` | Draft auto-sent via permitted category |
| `OUTBOUND_MESSAGE_PENDING_APPROVAL` | Draft pending human approval |
| `OUTBOUND_MESSAGE_APPROVED_SENT` | Draft approved and sent |
| `OUTBOUND_MESSAGE_REJECTED` | Draft rejected |
| `FORMALWEAR_ORDER_PROFILE_CREATED` | Formalwear profile created |
| `FORMALWEAR_ORDER_PROFILE_UPDATED` | Formalwear profile updated |
| `C2B2M_ROLE_EDGE_CREATED` | Role edge created |
| `C2B2M_DEFAULT_EDGES_INITIALIZED` | Default edges initialized for project |
