# Giraffe JP Service Backend

This document describes the Giraffe JP service backend layer built on top of the abcdYi apparel execution foundation.

---

## Architecture Overview

Giraffe JP extends the abcdYi backend with a Japan-focused C2B2M service layer for custom formalwear.

All Giraffe JP API routes are mounted under `/api/giraffe-jp/` and require JWT authentication via `Authorization: Bearer <token>`.

All Giraffe JP top-level database tables include `tenant_id` for tenant isolation.

Every meaningful action emits an event to the Industrial Execution Graph via `emit_event()`.

---

## How Service Node Differs from Order Status

An **Order** has a `status` field (`DRAFT`, `IN_PRODUCTION`, `QC_PENDING`, `DELIVERED`, etc.) that represents the procurement lifecycle stage.

A **Service Node** (`GiraffeJPServiceNode`) is an actionable service checkpoint that exists alongside the order lifecycle. Examples:

- `MEASUREMENT_REQUIRED` — customer measurement needs to be guided and confirmed
- `SUPPLIER_SEARCH_STARTED` — qualified production partner is being identified
- `QC_EVIDENCE_REVIEW` — raw QC photos need customer-facing review

Service nodes can be created at any point, can block each other via P0 confirmation logic, and exist independently of order status transitions. They represent the service layer, not the procurement state machine.

---

## Confirmation Priority

| Priority | Meaning |
|---|---|
| P0 | Blocks the next service node completion until confirmed |
| P1 | Urgent — should be escalated if overdue |
| P2 | Normal confirmation |
| P3 | Informational acknowledgement |

A service node with `status=COMPLETED` cannot be completed while any P0 blocking confirmation remains unconfirmed.

---

## Iteration 01 — Service Core (Implemented)

**Models:**
- `GiraffeJPServiceNode`
- `GiraffeJPConfirmationRequest`
- `GiraffeJPCustomerServiceTask`

**Routes:** See `docs/giraffe_jp_api_reference.md` — Service Core section.

---

## Iteration 02 — Message Category Auto-Send Permissions (Implemented)

### Purpose

Controls whether outbound messages in each category may be sent automatically (auto_send=true) or require human confirmation before sending (auto_send=false).

### Model: `GiraffeJPMessageCategoryPermission`

Each permission record is scoped to a `(tenant_id, category_id)` pair.

Fields: `category_id`, `category_name`, `direction` (CUSTOMER/SUPPLIER/MODEL_PARTNER/INTERNAL), `channel` (WEB_DIALOG/EMAIL/ANY), `auto_send`, `is_active`.

### Auto-Send Logic

```
is_auto_send_allowed(db, tenant_id, category_id, channel=None) → bool
```

Rules applied in order:
1. Category not found → False
2. `is_active=False` → False
3. Channel supplied and `perm.channel` not in `("ANY", channel)` → False
4. Return `perm.auto_send`

Unknown categories always return False — they are never auto-sent.

### Default Categories

Call `POST /api/giraffe-jp/message-category-permissions/seed-defaults` to upsert 22 default categories for the current tenant:

- 9 customer-side (6 auto_send=true, 3 auto_send=false)
- 9 supplier-side (4 auto_send=true, 5 auto_send=false)
- 4 model-partner-side (2 auto_send=true, 2 auto_send=false)

Categories with `auto_send=false`: price confirmations, delivery commitments, order placement, payment-related, dispute/claim, final approval, schedule confirmations, fee confirmations.

---

## Iteration 03 — Web Dialog and Email Communication Layer (Implemented)

### Purpose

Provides controlled outbound/inbound communication records for customers, suppliers, and local model partners. No real email provider is integrated in this iteration — outbound messages are recorded as mock-sent.

### Models

- `GiraffeJPConversationThread` — a communication thread (CUSTOMER/SUPPLIER/MODEL_PARTNER/INTERNAL)
- `GiraffeJPMessage` — individual inbound or outbound message records
- `GiraffeJPOutboundMessageDraft` — pending outbound messages with send status
- `GiraffeJPMessageDeliveryLog` — delivery status records (MOCK_SENT/PENDING_HUMAN_CONFIRMATION/FAILED)

### Outbound Draft Creation Flow

1. Category permission is loaded for `(tenant_id, category_id)`.
2. If `auto_send=true`:
   - Draft status → `AUTO_SENT`
   - Outbound `GiraffeJPMessage` created
   - `GiraffeJPMessageDeliveryLog` created with `MOCK_SENT`
   - `sent_at` set
3. If `auto_send=false` (or unknown category):
   - Draft status → `PENDING_HUMAN_CONFIRMATION`
   - `GiraffeJPCustomerServiceTask` created with `task_type=REVIEW_OUTBOUND_MESSAGE`
   - `GiraffeJPMessageDeliveryLog` created with `PENDING_HUMAN_CONFIRMATION`

No outbound message may bypass message category permission. There is no direct send path.

### Approve / Reject Flow

- `POST /outbound-drafts/{id}/approve-send` — creates outbound message + delivery log, sets status `APPROVED_SENT`
- `POST /outbound-drafts/{id}/reject` — sets status `REJECTED`, no message created

---

## Iteration 04 — Formalwear C2B2M Order Extension (Implemented)

### Purpose

Adds Japan formalwear-specific order data and C2B2M role-edge support. Makes the backend service-led and Japan-specific.

### Supported Formalwear Categories

- `FORMAL_DRESS`
- `WOMENS_SUIT`
- `BRIDALWEAR`
- `LIGHT_WEDDING_DRESS`
- `RECEPTION_DRESS`

### hollow_to_hem_required Default Rule

If `product_category` is `FORMAL_DRESS`, `BRIDALWEAR`, or `LIGHT_WEDDING_DRESS`, and `hollow_to_hem_required` is not explicitly set by the caller, the service defaults it to `true`.

For `WOMENS_SUIT` and `RECEPTION_DRESS`, the default is `false` unless explicitly set.

### Model Defaults

- `model_try_on_required`: defaults to `true`
- `local_alteration_possible`: defaults to `true`

### C2B2M Role Edge Logic

Two default edges are supported:

```
JP_CUSTOMER → GIRAFFE_JP
from_role=B_SIDE, to_role=MAIN_M_SIDE

GIRAFFE_JP → SUPPLIER
from_role=UPSTREAM_B_SIDE, to_role=UPSTREAM_M_SIDE
```

The supplier edge is only created when `supplier_id` is provided. Duplicate edges (same project, actor types, and edge_type) are never created by the default initialization endpoint.

---

## What Is Implemented vs Planned

### Implemented

- Service nodes, confirmation requests, customer-service tasks (Iter 01)
- Message category auto-send permissions + seed defaults (Iter 02)
- Conversation threads, messages, outbound drafts, delivery logs (Iter 03)
- Formalwear order profiles (Iter 04)
- C2B2M role edges and default edge initialization (Iter 04)
- All actions write to Industrial Execution Graph
- Tenant isolation enforced on every resource
- JWT authentication on all routes

### Planned (Iteration 05+)

- Message category auto-send permission templates
- QC raw evidence repository
- Measurement profile interface
- Digital human profile interface
- Local model try-on scheduling and evidence
- Segmented logistics adapters (China domestic, cross-border, Japan domestic)
- Marketplace supplier abstraction layer
- Giraffe JP supplier memory extension
- Integrated Giraffe JP E2E 3x readiness script

---

## Testing Commands

```bash
# Unit tests (no PostgreSQL required)
uv run pytest tests/unit/ -v -m "not integration"

# Specific unit test groups
uv run pytest tests/unit/test_giraffe_jp_message_permissions.py -v
uv run pytest tests/unit/test_giraffe_jp_formalwear_rules.py -v
uv run pytest tests/unit/test_giraffe_jp_conversation_permissions.py -v

# API tests (PostgreSQL required)
uv run pytest tests/api/test_giraffe_jp_service_core.py -v
uv run pytest tests/api/test_giraffe_jp_message_permissions.py -v
uv run pytest tests/api/test_giraffe_jp_conversations.py -v
uv run pytest tests/api/test_giraffe_jp_formalwear.py -v
```
