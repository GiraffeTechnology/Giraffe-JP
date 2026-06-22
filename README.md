# Giraffe JP / ABCDYi Japan

> AI-powered C2B2M custom formalwear platform for women in Japan.

Giraffe JP / ABCDYi Japan is a service-led made-to-order formalwear platform for women in Japan.

It is designed for formal dresses, women's suits, bridalwear, light wedding dresses, reception dresses, and other formal-occasion apparel where customers need more than a product listing: they need guided measurement, structured confirmation, production follow-up, quality evidence review, local model try-on, segmented logistics tracking, and human-confirmed delivery.

Giraffe JP is built on the abcdYi apparel execution foundation and extends it with a Japan-focused C2B2M service layer.

---

## Product Position

Giraffe JP is not a price-first cross-border shopping clone.

The product value is service density:

- AI-guided measurement support
- structured customer confirmation
- proportional digital human profile
- proactive customer progress updates
- qualified production partner network
- supplier progress follow-up
- QC raw photo/video evidence review
- local model try-on as a standard service
- segmented China / cross-border / Japan logistics tracking
- customer sign-off and auditable execution history

The customer does not need to manage production details alone. Giraffe JP turns a custom formalwear order into a structured, trackable, confirmable service workflow.

---

## Why Giraffe JP Exists

Women's formalwear orders are high-context purchases.

A customer ordering a dress, suit, bridalwear item, or reception dress often needs help with:

- measurement accuracy
- size and fit confidence
- style and occasion confirmation
- production timeline visibility
- quality evidence before delivery
- logistics transparency
- final handover confidence

Low-price shopping platforms are optimized for selection and checkout speed. Giraffe JP is optimized for assisted execution.

---

## Core Scenario

```text
Japanese customer
    ↓
Formalwear requirement intake
    ↓
AI-guided measurement
    ↓
Measurement Profile
    ↓
Proportional Digital Human Profile
    ↓
Customer confirmation
    ↓
Qualified production partner search
    ↓
Quote / timeline / service confirmation
    ↓
Customer approval
    ↓
Supplier order execution
    ↓
QC raw evidence collection
    ↓
Segmented logistics tracking
    ↓
Local model try-on
    ↓
Customer try-on review
    ↓
Final delivery
    ↓
Customer sign-off
    ↓
Supplier Memory update
    ↓
Industrial Execution Graph record
```

---

## Role Model

Giraffe JP uses Giraffe Agent's edge-based role logic.

### Edge 1 — Customer to Giraffe JP

```text
JP Customer → Giraffe JP
JP Customer: B-side originator
Giraffe JP: MAIN_M_SIDE
```

The customer gives Giraffe JP a custom formalwear requirement. Giraffe JP faces the customer as the main service executor.

### Edge 2 — Giraffe JP to Production Partner

```text
Giraffe JP → Qualified production supplier
Giraffe JP: UPSTREAM_B_SIDE
Supplier: UPSTREAM_M_SIDE
```

Giraffe JP sends structured requirements to qualified full-package production suppliers that can handle fabric/trims internally, production, custom sizing, basic QC, packaging, and logistics preparation.

---

## Service-Led Execution Layer

Giraffe JP adds a customer-service execution layer on top of the existing abcdYi apparel backend.

The key runtime objects are:

- **Service Node** — an actionable service checkpoint, not merely an order status.
- **Confirmation Request** — a structured request for a customer, supplier, staff member, model partner, or logistics provider to confirm specific information.
- **Customer Service Task** — a work item for human review, escalation, or manual confirmation.
- **Message Category Permission** — a simple `auto_send=true/false` control for outbound communication categories.
- **Evidence Asset** — raw or customer-visible quality evidence metadata.
- **Measurement Profile** — structured measurement data confirmed by the customer.
- **Digital Human Profile** — proportional body parameters used for fit communication and model-card matching.
- **Model Try-On Request** — a standard service flow before final delivery.
- **Shipment Segment** — China domestic, cross-border, and Japan domestic logistics segments.
- **Supplier Performance Snapshot** — Giraffe JP-specific supplier cooperation memory.

---

## Confirmation Priority

Giraffe JP uses P0/P1/P2/P3 priority for service execution.

| Priority | Meaning |
|---|---|
| P0 | Blocks the next service step until confirmed |
| P1 | Urgent and should be escalated if overdue |
| P2 | Normal confirmation |
| P3 | Informational acknowledgement |

Examples of P0 confirmations:

- customer confirms measurements
- customer confirms price
- customer confirms delivery commitment
- supplier confirms order acceptance
- supplier confirms production cycle
- supplier submits required QC evidence

---

## Outbound Communication Control

Giraffe JP follows a simple category-level outbound permission model:

```text
message category → auto_send=true/false
```

If `auto_send=true`, the system may send the message through the configured channel.

If `auto_send=false`, the message becomes a pending human-confirmation task.

This keeps routine updates efficient while keeping price, delivery commitment, order placement, payment-related, final approval, and dispute-related communication under human control.

---

## Measurement and Digital Human

The measurement assistant is designed as an independent module or SDK.

The backend stores only structured output:

- height
- bust / waist / hip
- shoulder width
- arm length
- hollow-to-hem for dresses and bridalwear
- fit preference
- coverage preference
- confidence score
- customer confirmation status

Raw customer measurement videos must not be uploaded to the backend.

The digital human profile is not an entertainment avatar. It is an anonymous, proportional, parameterized body model used for service execution, customer confirmation, supplier communication, and local model-card matching.

---

## Local Model Try-On

Local model try-on is a standard Giraffe JP service.

Before final delivery, the garment can be tried on by a local model partner with comparable body parameters. The system records try-on photos/videos, fit notes, customer-visible reports, and customer confirmation.

This service is part of Giraffe JP's trust layer and should be integrated with the evidence repository and service-node engine.

---

## QC Evidence

Giraffe JP treats QC as node-based evidence collection.

Suggested QC nodes:

- style / material appearance confirmation
- pre-production confirmation
- cutting or in-progress evidence
- finished-product evidence
- measurement-check evidence
- packaging evidence
- shipping handover evidence

The system distinguishes:

- internal raw evidence
- customer-visible evidence
- evidence requiring further review
- accepted / rejected evidence submissions

---

## Segmented Logistics

Giraffe JP logistics should be segment-aware:

```text
China domestic segment
    ↓
Cross-border segment
    ↓
Japan domestic segment
```

The backend is designed to support manual tracking first and future carrier adapters later.

Planned carriers and adapters include:

- Cainiao-style China domestic tracking adapter
- cross-border EMS-style tracking adapter
- Japan Post-style domestic tracking adapter
- manual tracking adapter

No real external API credentials are required for the first backend phase.

---

## Current Backend Status

**Service Core (Iteration 01)**

- `GiraffeJPServiceNode`
- `GiraffeJPConfirmationRequest`
- `GiraffeJPCustomerServiceTask`
- service-node API routes
- confirmation-request API routes (confirm, reject, escalate)
- customer-service task API routes (start, complete, escalate)
- P0 blocking confirmation behavior
- tenant isolation tests
- execution graph event emission for service actions
- Alembic migration `b2c3d4e5f6a7` (service-core tables)

**Iteration 02 — Message Category Auto-Send Permissions**

- `GiraffeJPMessageCategoryPermission`
- 22 default categories (8 CUSTOMER, 7 SUPPLIER, 7 MODEL_PARTNER)
- `is_auto_send_allowed()` — unknown categories default to `auto_send=False` (spec rule 7)
- message category permission routes (seed, list, get, patch)
- execution graph events: `MESSAGE_CATEGORY_PERMISSIONS_SEEDED`, `MESSAGE_CATEGORY_PERMISSION_UPDATED`

**Iteration 03 — Web Dialog and Email Communication Layer**

- `GiraffeJPConversationThread`, `GiraffeJPMessage`, `GiraffeJPOutboundMessageDraft`, `GiraffeJPMessageDeliveryLog`
- conversation thread routes (create, list, get)
- inbound message recording
- outbound draft creation with auto-send enforcement
- human approve/reject flow (HTTP 400 on invalid state)
- simulated delivery logging
- execution graph events: 7 communication event types

**Iteration 04 — Formalwear C2B2M Order Extension**

- `GiraffeJPFormalwearOrderProfile`, `GiraffeJPC2B2MRoleEdge`
- formalwear profile routes (create, get, patch)
- automatic `hollow_to_hem_required` detection from garment category
- C2B2M role edge initialization (idempotent, 4 default edges per project)
- execution graph events: `FORMALWEAR_ORDER_PROFILE_CREATED`, `FORMALWEAR_ORDER_PROFILE_UPDATED`, `C2B2M_ROLE_EDGE_CREATED`, `C2B2M_DEFAULT_EDGES_INITIALIZED`
- Alembic migration `d4e5f6a7b8c9` (iter 02/03/04 tables, chained after service-core)

Planned Giraffe JP modules:

- service node automation templates
- QC raw evidence repository
- measurement profile interface
- digital human profile interface
- local model try-on service layer
- segmented logistics records and mock adapters
- marketplace supplier abstraction
- Giraffe JP supplier memory extension
- integrated Giraffe JP E2E readiness scripts

---

## Existing abcdYi Foundation

Giraffe JP is built on the existing abcdYi apparel execution foundation.

The base backend already provides:

- authentication and tenant isolation
- participant management
- buyer inquiry intake
- dynamic order forms
- supplier matching
- RFQ workflow
- approval gates
- decision packets
- order state machine
- production monitoring
- QC records
- logistics records
- supplier memory
- Industrial Execution Graph
- GPM integration for price benchmark lookup and quote validation
- GLTG integration for delivery feasibility evaluation

Giraffe JP extends these capabilities with Japan-specific formalwear service execution.

---

## API Overview

All routes except `/health` and `/api/auth/*` require:

```text
Authorization: Bearer <jwt_token>
```

Giraffe JP service-core routes:

| Method | Path | Description |
|---|---|---|
| POST | `/api/giraffe-jp/service-nodes` | Create a service node |
| GET | `/api/giraffe-jp/service-nodes` | List service nodes |
| GET | `/api/giraffe-jp/service-nodes/{id}` | Get service node detail |
| PATCH | `/api/giraffe-jp/service-nodes/{id}` | Update a service node |
| POST | `/api/giraffe-jp/confirmation-requests` | Create a confirmation request |
| GET | `/api/giraffe-jp/confirmation-requests` | List confirmation requests |
| GET | `/api/giraffe-jp/confirmation-requests/{id}` | Get confirmation request detail |
| POST | `/api/giraffe-jp/confirmation-requests/{id}/confirm` | Confirm a request |
| POST | `/api/giraffe-jp/confirmation-requests/{id}/reject` | Reject a request |
| POST | `/api/giraffe-jp/confirmation-requests/{id}/escalate` | Escalate a request |
| GET | `/api/giraffe-jp/customer-service/tasks` | List customer-service tasks |
| POST | `/api/giraffe-jp/customer-service/tasks` | Create a customer-service task |
| POST | `/api/giraffe-jp/customer-service/tasks/{id}/start` | Start a task |
| POST | `/api/giraffe-jp/customer-service/tasks/{id}/complete` | Complete a task |
| POST | `/api/giraffe-jp/customer-service/tasks/{id}/escalate` | Escalate a task |

Iteration 02 — Message category permissions:

| Method | Path | Description |
|---|---|---|
| POST | `/api/giraffe-jp/permissions/seed-defaults` | Seed 22 default message category permissions |
| GET | `/api/giraffe-jp/permissions` | List message category permissions |
| GET | `/api/giraffe-jp/permissions/{id}` | Get a permission |
| PATCH | `/api/giraffe-jp/permissions/{id}` | Update auto-send setting |

Iteration 03 — Conversations and outbound drafts:

| Method | Path | Description |
|---|---|---|
| POST | `/api/giraffe-jp/conversations` | Open a conversation thread |
| GET | `/api/giraffe-jp/conversations` | List conversation threads |
| GET | `/api/giraffe-jp/conversations/{id}` | Get a conversation thread |
| POST | `/api/giraffe-jp/conversations/{id}/messages/inbound` | Record inbound message |
| POST | `/api/giraffe-jp/conversations/{id}/outbound-drafts` | Create outbound draft (auto-send or pending) |
| GET | `/api/giraffe-jp/conversations/{id}/outbound-drafts` | List outbound drafts |
| POST | `/api/giraffe-jp/outbound-drafts/{id}/approve` | Approve a pending draft |
| POST | `/api/giraffe-jp/outbound-drafts/{id}/reject` | Reject a pending draft |

Iteration 04 — Formalwear and C2B2M:

| Method | Path | Description |
|---|---|---|
| POST | `/api/giraffe-jp/projects/{id}/formalwear-profile` | Create formalwear order profile |
| GET | `/api/giraffe-jp/projects/{id}/formalwear-profile` | Get formalwear profile |
| PATCH | `/api/giraffe-jp/projects/{id}/formalwear-profile` | Update formalwear profile |
| POST | `/api/giraffe-jp/projects/{id}/c2b2m-edges/initialize` | Initialize default C2B2M role edges |
| GET | `/api/giraffe-jp/projects/{id}/c2b2m-edges` | List C2B2M role edges |

Core abcdYi routes remain available for projects, participants, dynamic forms, matching, RFQs, decision packets, orders, QC, logistics, and execution graph queries.

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- `uv` package manager

### Local Development

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn api.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

### Docker

```bash
docker compose up -d db
docker compose run --rm migrate
docker compose up api
```

---

## Validation

Run clean-state validation:

```bash
./scripts/run_clean_db_validation.sh
```

Run unit tests:

```bash
uv run pytest tests/unit/ -v -m "not integration"
```

Run API tests when a migrated PostgreSQL database is available:

```bash
uv run pytest tests/api/ -v
```

Existing abcdYi acceptance script:

```bash
BASE_URL=http://localhost:8000 uv run python scripts/run_v1_acceptance_apparel_order.py
```

Expected output:

```text
GIRAFFE APPAREL & TEXTILE V1 ACCEPTANCE: PASS
```

---

## Documentation

| Document | Description |
|---|---|
| `docs/giraffe_jp_backend_integration_plan.md` | Giraffe JP integration planning doc |
| `docs/giraffe_jp_service_backend.md` | Giraffe JP backend architecture and business rules |
| `docs/giraffe_jp_api_reference.md` | Full Giraffe JP API reference |
| `docs/api_reference.md` | abcdYi core API reference |
| `docs/user_manual.md` | User guide |
| `docs/admin_manual.md` | Admin and operations guide |
| `docs/deployment_guide.md` | Deployment guide |
| `docs/patent_alignment_matrix.md` | Patent unit mapping |
| `docs/workflow_overview.md` | Workflow documentation |
| `docs/product_scope.md` | Product scope and positioning |
| `docs/acceptance_criteria_v1.md` | V1 acceptance criteria |

---

## Patent Notice and License

This repository is released under the Apache-2.0 software license.

Certain workflows, system logic, role-based participant coordination mechanisms, dynamic order forms, participant matching, production monitoring, quality inspection, participant supervision, supplier memory, pricing benchmark interaction, GPM buffer handoff, and multi-party apparel order-execution workflows in this project may be covered by patents owned by Giraffe Technology Holding Limited.

abcdYi is the Apparel / Textile / Handicraft industry foundation used by Giraffe JP.

Patent references:

| Jurisdiction | Patent |
|---|---|
| China | ZL 2023 1 1645939.9 / CN 117670482 B |
| Japan | P7644545 / 特許第7644545号 |

Giraffe Technology Holding Limited grants a Global Free Patent License to individuals, developers, researchers, students, startups, SMEs, nonprofit organizations, and educational institutions for use, study, modification, and non-exclusive deployment of the patented workflows embodied in this open-source project, subject to the license terms in this repository.

For commercial licensing, private deployment, enterprise support, or patent-related inquiries, contact Giraffe Technology Holding Limited.
