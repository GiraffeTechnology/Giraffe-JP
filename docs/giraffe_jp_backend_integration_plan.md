# Giraffe JP Backend Integration Plan

## Scope

This document records the Iteration 00 audit for adding the Giraffe JP service-led C2B2M backend layer to the existing `abcdYi` backend.

The goal is additive extension, not a rewrite. The current backend already contains the core B2M execution system: tenants, users, participants, projects, buyer inquiries, dynamic forms, matching, RFQs, supplier responses, decision packets, approvals, orders, production monitoring, QC records, logistics records, supplier memory, and execution graph events.

## Existing Reusable Modules

### Authentication and Tenant Context

- `api/auth.py` provides password hashing and JWT token creation/decoding.
- `api/deps.py` provides `get_current_user`, `get_current_user_id`, and async database session dependencies.
- Most existing API routes require `get_current_user`, so new Giraffe JP routes should follow the same dependency pattern.
- Core tenant ownership is stored on `users.tenant_id`, `participants.tenant_id`, `projects.tenant_id`, and `execution_events.tenant_id`.

Recommendation: all Giraffe JP tables that are directly queryable should include `tenant_id` unless the table is strictly child-scoped through a tenant-owned parent. Including `tenant_id` directly will make tenant isolation easier to test and enforce.

### Participants and Actor Roles

- UUID-based participants live in `src/db/models/participant.py`.
- Actor-based role-switching tables live alongside the UUID schema, including `actors`, `role_context`, `procurement_edges`, and upstream approval/response tables.
- Existing role-switching routes and services can inform the C2B2M edge design.

Recommendation: use UUID `participants` for customer, supplier, logistics provider, model agency, and staff-facing links in the Giraffe JP service layer. Add Giraffe JP-specific C2B2M role edges as a separate module that can reference either UUID participants or actor IDs through typed actor fields.

### Projects, Buyer Inquiries, and Dynamic Forms

- `Project`, `BuyerInquiry`, and `RawMessage` are defined in `src/db/models/project.py`.
- Dynamic form models and routes already support extracting structured requirements from buyer inquiries.
- The existing project API is a natural entry point for Giraffe JP formalwear order profiles.

Recommendation: connect Giraffe JP formalwear profiles to existing `projects.id` and, when available, `orders.id`. Avoid duplicating buyer inquiry or general requirement capture.

### Supplier Matching, RFQ, Supplier Responses, and Decision Packets

- Matching records live in `src/db/models/matching.py`.
- RFQs and supplier responses live in `src/db/models/rfq.py`.
- Decision packets and core approval requests live in `src/db/models/decision.py`.
- Existing route modules already expose matching, RFQ, supplier response, and decision packet workflows.

Recommendation: reuse the current supplier workflow for qualified full-package suppliers. Giraffe JP should add service nodes and confirmations around this workflow instead of replacing RFQ or decision packet behavior.

### Approval Gates

- Core approval requests are modeled in `src/db/models/decision.py` as `approval_requests`.
- Actor/upstream approvals also exist in `src/db/models/approval.py` as `upstream_approval_requests`.

Recommendation: Giraffe JP confirmation requests should be separate from generic approval requests because they model customer-service checkpoints, target parties, priority, channel, due dates, and blocking behavior. Where a confirmation creates a business decision, it can reference or create a core `approval_requests` row.

### Orders and Production Monitoring

- Orders are defined in `src/db/models/order.py`.
- Production records are defined in `src/db/models/production.py`.
- Existing order routes cover order creation from approved options, confirmation, and buyer sign-off.

Recommendation: service nodes should reference existing `orders.id` and `projects.id`. Do not add a parallel Giraffe JP order state machine in Phase 1; add service-node orchestration on top of the existing order lifecycle.

### QC

- Core QC standards and QC records are defined in `src/db/models/qc.py`.
- Existing QC models include measurement tolerance, defects, inspection metadata, evidence metadata, result status, and rework flags.
- Separate actor-oriented QC reference image, process card, and comparison report tables also exist.

Recommendation: keep existing `QCRecord` as the summarized QC result. Add Giraffe JP raw evidence request/submission/asset models later to represent node-based raw photo/video/document evidence and link accepted summaries back to `QCRecord`.

### Logistics

- Shipments and shipment tracking events are defined in `src/db/models/logistics.py`.
- The repository also has logistics provider, parser, normalizer, ingestion, and state mapper tests.

Recommendation: reuse `Shipment` and `ShipmentTrackingEvent` for base tracking. Giraffe JP logistics adapters should initially create normalized shipment events and add segmented Japan-specific service nodes for China, cross-border, Japan arrival, model try-on, and final delivery steps.

### Supplier Memory

- UUID-based supplier memory is present as `SupplierMemoryRecord` in `src/db/models/logistics.py`.
- Actor-based supplier memory extension tables exist in `src/db/models/supplier_memory.py`.

Recommendation: Giraffe JP should add extension tables only for formalwear-specific supplier traits, such as custom sizing reliability, evidence submission quality, model try-on cooperation, and Japan-bound logistics performance. General score snapshots should remain in existing supplier memory modules.

### Execution Graph

- Core execution events are defined in `src/db/models/execution_graph.py`.
- Read APIs are exposed through `api/routes/execution_graph.py`.
- Existing event records include `tenant_id`, `project_id`, `order_id`, `participant_id`, `event_type`, `payload`, `triggered_by_user_id`, and `occurred_at`.

Recommendation: every Giraffe JP service action should write an `ExecutionEvent`. Add a small helper in `src/giraffe_jp/execution_events.py` or a shared service wrapper to keep event payloads consistent across routes.

## New Modules To Add

Add the new service layer under `src/giraffe_jp/` and route modules under `api/routes/`:

```text
src/giraffe_jp/
  __init__.py
  service_nodes/
  confirmations/
  customer_service/
  conversations/
  message_permissions/
  formalwear/
  c2b2m/
  evidence/
  qc_nodes/
  measurement/
  digital_human/
  model_try_on/
  logistics_adapters/
  marketplaces/
  supplier_memory_ext/

api/routes/
  giraffe_jp_service_nodes.py
  giraffe_jp_confirmations.py
  giraffe_jp_customer_service.py
  giraffe_jp_conversations.py
  giraffe_jp_message_permissions.py
  giraffe_jp_formalwear.py
  giraffe_jp_evidence.py
  giraffe_jp_measurement.py
  giraffe_jp_digital_human.py
  giraffe_jp_model_try_on.py
  giraffe_jp_logistics.py
  giraffe_jp_marketplaces.py
```

Database models should be added either in `src/db/models/giraffe_jp.py` for the first iteration or split into focused files once the module set grows. If split, remember to import them from `src/db/models/__init__.py` so Alembic metadata registration remains complete.

## Migration Strategy

- Use additive Alembic migrations only.
- Do not alter or drop existing tables for Phase 1.
- Prefer nullable `project_id` and `order_id` links when a service record may be created before an order exists.
- Add `tenant_id` to top-level Giraffe JP records for direct tenant filtering.
- Use `src.db.json_type.PortableJSON` for JSON payload fields to preserve the repository's PostgreSQL/SQLite portability pattern.
- Keep enum-like fields as bounded strings first, matching the current codebase style.
- Add indexes for common filters: `tenant_id`, `project_id`, `order_id`, `status`, `node_type`, `category_id`, and due-date fields.

Initial migration order:

1. Service nodes, confirmation requests, and customer service tasks.
2. Message category permissions.
3. Conversation threads, messages, outbound drafts, and delivery logs.
4. Formalwear order profiles and C2B2M role edges.
5. QC evidence requests/submissions/assets.
6. Measurement and digital human profiles.
7. Model try-on and logistics adapter records.

## Route Namespace Strategy

All Giraffe JP APIs should live under:

```text
/api/giraffe-jp/...
```

Route files should be included from `api/main.py` with the same dependency style as existing routes:

```python
app.include_router(giraffe_jp_service_nodes_router, prefix="/api/giraffe-jp", tags=["giraffe_jp_service_nodes"])
```

Every route should require JWT authentication via `get_current_user` unless it is explicitly designed as a public webhook. Phase 1 should avoid public webhooks.

Avoid public-facing API labels that use intermediary, broker, middleman, sourcing agent, or agency language. Use service-led custom formalwear, production partner, confirmation, service node, evidence review, and local model try-on terminology.

## Compatibility Risks

- There are two coexisting schema styles: UUID-based core tables and actor/string-ID upstream tables. Giraffe JP must be explicit about which identity system each relation uses.
- Some core tables do not have foreign keys for `project_id` even when they store UUIDs. New Giraffe JP tables should use explicit foreign keys where possible.
- Existing execution graph APIs currently read events but do not expose a shared write helper. Direct event creation in multiple new services could drift unless centralized.
- Tests rely on async SQLAlchemy sessions and authenticated `httpx` clients. New tests should follow `tests/conftest.py`.
- The repository supports database portability through `PortableJSON`; using PostgreSQL-only `JSONB` directly would make SQLite-style tests brittle.
- Service nodes can look similar to order statuses. Documentation and schemas must keep them separate: order status is lifecycle state, service node is an actionable checkpoint.
- Outbound communication must route through category-level `auto_send` permissions. Any helper that sends or records outbound messages should enforce that lookup.
- Measurement privacy is a product constraint: raw customer measurement videos must not be accepted by backend APIs.

## Test Strategy

Each implementation iteration should include both focused unit tests and API tests.

Recommended layout:

```text
tests/unit/test_giraffe_jp_*.py
tests/api/test_giraffe_jp_*.py
tests/integration/test_giraffe_jp_migrations.py
```

Test requirements:

- Use authenticated clients from `tests/conftest.py`.
- Verify tenant isolation for all list and detail endpoints.
- Verify service-node state transitions and P0 blocking behavior.
- Verify confirmation request confirm/reject/escalate behavior.
- Verify customer-service task creation and completion.
- Verify execution graph events for every externally meaningful action.
- Verify unknown message categories default to `auto_send=False`.
- Verify outbound drafts never bypass category-level permission checks.
- Verify raw measurement video upload fields are rejected or absent.
- Run existing tests plus new tests before merging each iteration.

## Iteration 01 Implementation Notes

The first runtime iteration created:

- `GiraffeJPServiceNode`
- `GiraffeJPConfirmationRequest`
- `GiraffeJPCustomerServiceTask`
- API routes for creating, listing, retrieving, and updating service nodes.
- API routes for creating, confirming, rejecting, and escalating confirmations.
- API routes for starting, completing, and escalating customer-service tasks.
- Execution event writes for created and completed service actions.

**Status: Complete.** Migration: `b2c3d4e5f6a7`.

---

## Iteration 02 Implementation Notes

Adds `GiraffeJPMessageCategoryPermission` with 22 default categories across CUSTOMER, SUPPLIER, and MODEL_PARTNER directions. The `is_auto_send_allowed()` helper applies 4 ordered rules (category not found → False, is_active=False → False, channel mismatch → False, return perm.auto_send). The seed-defaults endpoint is idempotent.

**Status: Complete.** Routes under `/api/giraffe-jp/message-category-permissions`.

---

## Iteration 03 Implementation Notes

Adds conversation threads, inbound/outbound messages, outbound drafts, and delivery logs. Every outbound draft checks `is_auto_send_allowed()` at creation time — no direct send path bypasses this check. Auto-sent drafts create a `GiraffeJPMessage` and `GiraffeJPMessageDeliveryLog(MOCK_SENT)`. Pending drafts create a `GiraffeJPCustomerServiceTask(REVIEW_OUTBOUND_MESSAGE)` and a pending delivery log. Approve and reject flows are separate endpoints.

**Status: Complete.** Routes under `/api/giraffe-jp/conversations` and `/api/giraffe-jp/outbound-drafts`. No real email provider integrated; outbound messages are mock-sent.

---

## Iteration 04 Implementation Notes

Adds `GiraffeJPFormalwearOrderProfile` linked to existing projects. The `hollow_to_hem_required` field defaults to `true` for FORMAL_DRESS, BRIDALWEAR, and LIGHT_WEDDING_DRESS product categories when not explicitly set. Adds `GiraffeJPC2B2MRoleEdge` and a default-edge initializer that creates at most 2 edges per project (JP_CUSTOMER→GIRAFFE_JP always; GIRAFFE_JP→SUPPLIER only when supplier_id is provided). Duplicate edges are silently skipped by the initializer.

**Status: Complete.** Migration: `c3d4e5f6a7b8`. Routes under `/api/giraffe-jp/formalwear` and `/api/giraffe-jp/c2b2m`.
