# Giraffe JP — Merchant-Owned C-B-M Backend Package

`C-B-M` | `Merchant Backend` | `Custom Order Execution` | `Giraffe Agent / abcdYi` | `giraffe-language-skill` | `giraffe-db` | `GLTG` | `QC Evidence`

Giraffe JP is the first deployable C-B-M merchant backend package built on Giraffe Agent / abcdYi.

It is a configurable agentic AI backend package for merchants operating custom-order stores. Merchants own their storefront, UI, brand, customer relationship, pricing, and B-side commercial responsibility. Giraffe JP provides backend workflows, supplier coordination, confirmation controls, QC evidence process, logistics model, and operating know-how required to execute cross-border and cross-region custom-order business.

The project was initiated by Giraffe Technology LLC / キリン技術合同会社 as the first landing package of Giraffe Agent / abcdYi. The name `Giraffe JP` reflects this origin and does not limit the package to Japan, any specific geography, consumer group, or apparel category.

---

## Product Position

Giraffe JP is not a consumer marketplace, shopping app, sourcing agency, or price-first cross-border shopping clone.

It is a merchant-owned C-B-M backend package:

```text
C = end customer / wearer / requester / demand source
B = merchant / store operator / brand owner / legal commercial operator
M = supplier / factory / QC / logistics / service partner network
```

The merchant owns the customer relationship and commercial responsibility. Giraffe JP provides the structured backend execution layer.

---

## System Boundary

```text
giraffe-language-skill = multilingual canonicalization and output localization
giraffe-db             = private business facts, customer/order/supplier memory
GLTG                   = lead-time and delivery-feasibility simulation
GPM                    = procurement and supplier-path reasoning
giraffe-qc-model       = SKU-specific visual QC intelligence
Giraffe JP             = merchant-owned C-B-M backend package
human merchant         = final commercial/legal approval
```

Giraffe JP must not embed its own language rules, supplier truth store, GLTG calculator, QC visual judge, channel credential runtime, or legal decision-maker.

---

## P0 Language Boundary

Standard English is the only internal working language across Giraffe products.

Custom-order input may arrive in Japanese, Chinese, English, or other languages. Before Giraffe JP extracts business fields, creates requirements, routes suppliers, runs GLTG, writes execution data, generates QC test points, or creates outbound drafts, raw multilingual input must pass through `giraffe-language-skill`.

Allowed path:

```text
raw multilingual customer / merchant / supplier input
-> giraffe-language-skill
-> canonical English custom-order packet
-> Giraffe JP backend workflow
-> giraffe-db / GLTG / GPM / QC integrations
-> localized customer / merchant / supplier output
```

Localized output is not the internal source of truth. The canonical English packet is the audit source.

---

## Initial Reference Scenario

The initial reference scenario is custom apparel and formalwear.

This scenario is useful because formalwear and made-to-order apparel require more than product listing and checkout. They require:

```text
measurement support
style confirmation
material and process confirmation
production timeline visibility
QC evidence before delivery
logistics transparency
handover confidence
human approval at critical boundaries
```

The package can expand to broader apparel, textile, handicraft, and high-touch bespoke-order categories.

---

## Standard C-B-M Flow

```text
End customer
    ↓
Merchant-owned storefront
    ↓
Giraffe JP backend package
    ↓
Production / supplier / service partner network
```

| Party | C-B-M role | Meaning |
|---|---|---|
| End customer | C | Final buyer, wearer, requester, or demand source |
| Merchant / store operator / brand owner | B | Owns storefront, brand, customer relationship, pricing, and commercial responsibility |
| Giraffe JP | Backend package / execution layer | Provides workflow engine, confirmations, supplier coordination, QC process, logistics model, and operating know-how |
| Supplier / factory / service partner | M | Executes production, supply, QC, logistics, model try-on, or other service functions |

---

## Core Backend Workflow

```text
customer request
-> language canonicalization
-> merchant requirement confirmation
-> measurement / style / material / fit confirmation
-> supplier or production partner routing
-> GLTG lead-time feasibility
-> quote / schedule / risk summary
-> merchant approval
-> supplier communication
-> production tracking
-> QC evidence collection
-> logistics segmentation
-> customer handover / sign-off
-> execution graph and merchant memory update
```

---

## GLTG / Lead-Time Boundary

Giraffe JP should use GLTG for delivery feasibility and should not guess lead time locally.

GLTG provides:

```text
P50 / P80 / P90 lead-time estimates
risk-adjusted delivery dates
supplier behavior buffers
buyer / customer decision delay buffers
fallback supplier recommendation
manual review trigger
explanation JSON
```

---

## QC Boundary

Giraffe JP may collect QC requirements and evidence, but QC intelligence belongs to `giraffe-qc-model`.

Visual QC must be based on confirmed Training Packs, Playbooks, capture protocols, detection points, and readiness gates. If QC evidence is insufficient, the result must be review-required.

---

## Human Approval Boundary

The merchant remains the legal and commercial actor.

Human approval is required for:

```text
customer-facing commitment
supplier inquiry release
supplier selection
price confirmation
production commitment
delivery commitment
QC exception acceptance
refund / dispute / payment instruction
contractual obligation
```

Giraffe JP assists execution. It does not become the merchant.

---

## Deployment Principle

Giraffe JP is a deployable package, not a marketplace.

Each deployment should preserve:

```text
merchant-owned UI / storefront
merchant-owned customer relationship
canonical English internal state
localized customer and supplier output
private business data boundary
human approval boundary
auditable execution history
```

---

## License

See `LICENSE`.
