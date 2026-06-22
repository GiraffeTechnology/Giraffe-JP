import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.giraffe_jp import GiraffeJPMessageCategoryPermission
from src.db.models.project import Project
from src.execution_graph.event_types import (
    MESSAGE_CATEGORY_PERMISSION_UPDATED,
    MESSAGE_CATEGORY_PERMISSIONS_SEEDED,
)
from src.execution_graph.writer import emit_event
from src.giraffe_jp.schemas import MessageCategoryPermissionUpdate

_DEFAULT_CATEGORIES = [
    # Customer-side
    {"category_id": "CUSTOMER_ORDER_RECEIVED_UPDATE", "category_name": "Customer: Order Received Update", "direction": "CUSTOMER", "channel": "ANY", "auto_send": True},
    {"category_id": "CUSTOMER_REQUIREMENT_CONFIRMED_UPDATE", "category_name": "Customer: Requirement Confirmed Update", "direction": "CUSTOMER", "channel": "ANY", "auto_send": True},
    {"category_id": "CUSTOMER_SUPPLIER_SEARCH_UPDATE", "category_name": "Customer: Supplier Search Update", "direction": "CUSTOMER", "channel": "ANY", "auto_send": True},
    {"category_id": "CUSTOMER_PRODUCTION_STARTED_UPDATE", "category_name": "Customer: Production Started Update", "direction": "CUSTOMER", "channel": "ANY", "auto_send": True},
    {"category_id": "CUSTOMER_QC_REVIEW_UPDATE", "category_name": "Customer: QC Review Update", "direction": "CUSTOMER", "channel": "ANY", "auto_send": True},
    {"category_id": "CUSTOMER_LOGISTICS_UPDATE", "category_name": "Customer: Logistics Update", "direction": "CUSTOMER", "channel": "ANY", "auto_send": True},
    {"category_id": "CUSTOMER_PRICE_CONFIRMATION", "category_name": "Customer: Price Confirmation", "direction": "CUSTOMER", "channel": "ANY", "auto_send": False},
    {"category_id": "CUSTOMER_DELIVERY_COMMITMENT", "category_name": "Customer: Delivery Commitment", "direction": "CUSTOMER", "channel": "ANY", "auto_send": False},
    {"category_id": "CUSTOMER_FINAL_APPROVAL", "category_name": "Customer: Final Approval", "direction": "CUSTOMER", "channel": "ANY", "auto_send": False},
    # Supplier-side
    {"category_id": "SUPPLIER_BASIC_PROGRESS_QUESTION", "category_name": "Supplier: Basic Progress Question", "direction": "SUPPLIER", "channel": "ANY", "auto_send": True},
    {"category_id": "SUPPLIER_QC_EVIDENCE_REQUEST", "category_name": "Supplier: QC Evidence Request", "direction": "SUPPLIER", "channel": "ANY", "auto_send": True},
    {"category_id": "SUPPLIER_LOGISTICS_NUMBER_REQUEST", "category_name": "Supplier: Logistics Number Request", "direction": "SUPPLIER", "channel": "ANY", "auto_send": True},
    {"category_id": "SUPPLIER_BASIC_CUSTOMIZATION_QUESTION", "category_name": "Supplier: Basic Customization Question", "direction": "SUPPLIER", "channel": "ANY", "auto_send": True},
    {"category_id": "SUPPLIER_PRICE_QUOTE_REQUEST", "category_name": "Supplier: Price Quote Request", "direction": "SUPPLIER", "channel": "ANY", "auto_send": False},
    {"category_id": "SUPPLIER_PRICE_CONFIRMATION", "category_name": "Supplier: Price Confirmation", "direction": "SUPPLIER", "channel": "ANY", "auto_send": False},
    {"category_id": "SUPPLIER_ORDER_PLACEMENT", "category_name": "Supplier: Order Placement", "direction": "SUPPLIER", "channel": "ANY", "auto_send": False},
    {"category_id": "SUPPLIER_PAYMENT_RELATED", "category_name": "Supplier: Payment Related", "direction": "SUPPLIER", "channel": "ANY", "auto_send": False},
    {"category_id": "SUPPLIER_DISPUTE_OR_CLAIM", "category_name": "Supplier: Dispute or Claim", "direction": "SUPPLIER", "channel": "ANY", "auto_send": False},
    # Model partner side
    {"category_id": "MODEL_PARTNER_AVAILABILITY_REQUEST", "category_name": "Model Partner: Availability Request", "direction": "MODEL_PARTNER", "channel": "ANY", "auto_send": True},
    {"category_id": "MODEL_PARTNER_SCHEDULE_CONFIRMATION", "category_name": "Model Partner: Schedule Confirmation", "direction": "MODEL_PARTNER", "channel": "ANY", "auto_send": False},
    {"category_id": "MODEL_PARTNER_EVIDENCE_REQUEST", "category_name": "Model Partner: Evidence Request", "direction": "MODEL_PARTNER", "channel": "ANY", "auto_send": True},
    {"category_id": "MODEL_PARTNER_FEE_CONFIRMATION", "category_name": "Model Partner: Fee Confirmation", "direction": "MODEL_PARTNER", "channel": "ANY", "auto_send": False},
]


async def seed_default_categories(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[GiraffeJPMessageCategoryPermission]:
    result = await db.execute(
        select(GiraffeJPMessageCategoryPermission).where(
            GiraffeJPMessageCategoryPermission.tenant_id == tenant_id
        )
    )
    existing = {row.category_id: row for row in result.scalars().all()}

    seeded = []
    for defn in _DEFAULT_CATEGORIES:
        if defn["category_id"] in existing:
            seeded.append(existing[defn["category_id"]])
            continue
        perm = GiraffeJPMessageCategoryPermission(
            tenant_id=tenant_id,
            category_id=defn["category_id"],
            category_name=defn["category_name"],
            direction=defn["direction"],
            channel=defn["channel"],
            auto_send=defn["auto_send"],
            is_active=True,
        )
        db.add(perm)
        seeded.append(perm)

    await db.flush()
    await emit_event(
        db=db,
        event_type=MESSAGE_CATEGORY_PERMISSIONS_SEEDED,
        payload={"seeded_count": len(_DEFAULT_CATEGORIES), "tenant_id": str(tenant_id)},
        tenant_id=tenant_id,
        triggered_by_user_id=user_id,
    )
    return seeded


async def list_category_permissions(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[GiraffeJPMessageCategoryPermission]:
    result = await db.execute(
        select(GiraffeJPMessageCategoryPermission)
        .where(GiraffeJPMessageCategoryPermission.tenant_id == tenant_id)
        .order_by(GiraffeJPMessageCategoryPermission.category_id)
    )
    return result.scalars().all()


async def get_category_permission(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    category_id: str,
) -> GiraffeJPMessageCategoryPermission:
    result = await db.execute(
        select(GiraffeJPMessageCategoryPermission).where(
            GiraffeJPMessageCategoryPermission.tenant_id == tenant_id,
            GiraffeJPMessageCategoryPermission.category_id == category_id,
        )
    )
    perm = result.scalars().first()
    if not perm:
        raise HTTPException(status_code=404, detail="Message category permission not found")
    return perm


async def update_category_permission(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    category_id: str,
    body: MessageCategoryPermissionUpdate,
    user_id: uuid.UUID,
) -> GiraffeJPMessageCategoryPermission:
    perm = await get_category_permission(db, tenant_id, category_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(perm, field, value)
    perm.updated_by_user_id = user_id
    await db.flush()
    await emit_event(
        db=db,
        event_type=MESSAGE_CATEGORY_PERMISSION_UPDATED,
        payload={
            "category_id": category_id,
            "auto_send": perm.auto_send,
            "is_active": perm.is_active,
        },
        tenant_id=tenant_id,
        triggered_by_user_id=user_id,
    )
    return perm


async def is_auto_send_allowed(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    category_id: str,
    channel: str | None = None,
) -> bool:
    result = await db.execute(
        select(GiraffeJPMessageCategoryPermission).where(
            GiraffeJPMessageCategoryPermission.tenant_id == tenant_id,
            GiraffeJPMessageCategoryPermission.category_id == category_id,
        )
    )
    perm = result.scalars().first()
    if not perm:
        return False
    if not perm.is_active:
        return False
    if channel and perm.channel not in ("ANY", channel):
        return False
    return perm.auto_send
