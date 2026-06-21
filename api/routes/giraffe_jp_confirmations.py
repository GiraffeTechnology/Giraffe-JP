import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from src.giraffe_jp.schemas import (
    ConfirmationRequestCreate,
    ConfirmationRequestOut,
    ConfirmationResponseBody,
)
from src.giraffe_jp.service import (
    confirm_confirmation_request,
    create_confirmation_request,
    escalate_confirmation_request,
    get_confirmation_request,
    list_confirmation_requests,
    reject_confirmation_request,
)

router = APIRouter()


@router.post("/confirmation-requests", status_code=status.HTTP_201_CREATED, response_model=ConfirmationRequestOut)
async def create_confirmation_request_route(
    body: ConfirmationRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    confirmation = await create_confirmation_request(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(confirmation)
    return confirmation


@router.get("/confirmation-requests", response_model=list[ConfirmationRequestOut])
async def list_confirmation_requests_route(
    service_node_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_confirmation_requests(db, current_user.tenant_id, service_node_id, status)


@router.get("/confirmation-requests/{confirmation_id}", response_model=ConfirmationRequestOut)
async def get_confirmation_request_route(
    confirmation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_confirmation_request(db, confirmation_id, current_user.tenant_id)


@router.post("/confirmation-requests/{confirmation_id}/confirm", response_model=ConfirmationRequestOut)
async def confirm_confirmation_request_route(
    confirmation_id: uuid.UUID,
    body: ConfirmationResponseBody | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    confirmation = await confirm_confirmation_request(
        db,
        confirmation_id,
        current_user.tenant_id,
        current_user.id,
        body.response_payload if body else None,
    )
    await db.commit()
    await db.refresh(confirmation)
    return confirmation


@router.post("/confirmation-requests/{confirmation_id}/reject", response_model=ConfirmationRequestOut)
async def reject_confirmation_request_route(
    confirmation_id: uuid.UUID,
    body: ConfirmationResponseBody | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    confirmation = await reject_confirmation_request(
        db,
        confirmation_id,
        current_user.tenant_id,
        current_user.id,
        body.response_payload if body else None,
    )
    await db.commit()
    await db.refresh(confirmation)
    return confirmation


@router.post("/confirmation-requests/{confirmation_id}/escalate", response_model=ConfirmationRequestOut)
async def escalate_confirmation_request_route(
    confirmation_id: uuid.UUID,
    body: ConfirmationResponseBody | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    confirmation = await escalate_confirmation_request(
        db,
        confirmation_id,
        current_user.tenant_id,
        current_user.id,
        body.response_payload if body else None,
    )
    await db.commit()
    await db.refresh(confirmation)
    return confirmation
