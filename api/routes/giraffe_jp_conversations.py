import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from src.giraffe_jp.conversations import (
    approve_outbound_draft,
    create_conversation_thread,
    create_outbound_draft,
    get_conversation_thread,
    get_outbound_draft,
    list_conversation_threads,
    list_outbound_drafts,
    list_thread_messages,
    record_inbound_message,
    reject_outbound_draft,
)
from src.giraffe_jp.schemas import (
    ConversationThreadCreate,
    ConversationThreadOut,
    InboundMessageCreate,
    MessageOut,
    OutboundMessageDraftCreate,
    OutboundMessageDraftOut,
)

router = APIRouter()


@router.post(
    "/conversations",
    response_model=ConversationThreadOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation_thread_route(
    body: ConversationThreadCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    thread = await create_conversation_thread(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(thread)
    return thread


@router.get("/conversations", response_model=list[ConversationThreadOut])
async def list_conversation_threads_route(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_conversation_threads(db, current_user.tenant_id)


@router.get("/conversations/{thread_id}", response_model=ConversationThreadOut)
async def get_conversation_thread_route(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_conversation_thread(db, thread_id, current_user.tenant_id)


@router.get("/conversations/{thread_id}/messages", response_model=list[MessageOut])
async def list_thread_messages_route(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_thread_messages(db, thread_id, current_user.tenant_id)


@router.post(
    "/conversations/{thread_id}/messages/inbound",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def record_inbound_message_route(
    thread_id: uuid.UUID,
    body: InboundMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    message = await record_inbound_message(db, thread_id, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(message)
    return message


@router.post(
    "/outbound-drafts",
    response_model=OutboundMessageDraftOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_outbound_draft_route(
    body: OutboundMessageDraftCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    draft = await create_outbound_draft(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.get("/outbound-drafts", response_model=list[OutboundMessageDraftOut])
async def list_outbound_drafts_route(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_outbound_drafts(db, current_user.tenant_id)


@router.get("/outbound-drafts/{draft_id}", response_model=OutboundMessageDraftOut)
async def get_outbound_draft_route(
    draft_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_outbound_draft(db, draft_id, current_user.tenant_id)


@router.post("/outbound-drafts/{draft_id}/approve-send", response_model=OutboundMessageDraftOut)
async def approve_outbound_draft_route(
    draft_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    draft = await approve_outbound_draft(db, draft_id, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.post("/outbound-drafts/{draft_id}/reject", response_model=OutboundMessageDraftOut)
async def reject_outbound_draft_route(
    draft_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    draft = await reject_outbound_draft(db, draft_id, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(draft)
    return draft
