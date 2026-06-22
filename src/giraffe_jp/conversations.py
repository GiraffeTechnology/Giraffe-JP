import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.giraffe_jp import (
    GiraffeJPConversationThread,
    GiraffeJPCustomerServiceTask,
    GiraffeJPMessage,
    GiraffeJPMessageDeliveryLog,
    GiraffeJPOutboundMessageDraft,
)
from src.execution_graph.event_types import (
    CONVERSATION_THREAD_CREATED,
    INBOUND_MESSAGE_RECORDED,
    OUTBOUND_DRAFT_CREATED,
    OUTBOUND_MESSAGE_APPROVED_SENT,
    OUTBOUND_MESSAGE_AUTO_SENT,
    OUTBOUND_MESSAGE_PENDING_APPROVAL,
    OUTBOUND_MESSAGE_REJECTED,
)
from src.execution_graph.writer import emit_event
from src.giraffe_jp.message_permissions import is_auto_send_allowed
from src.giraffe_jp.schemas import (
    ConversationThreadCreate,
    InboundMessageCreate,
    OutboundMessageDraftCreate,
)


async def _get_thread(
    db: AsyncSession, thread_id: uuid.UUID, tenant_id: uuid.UUID
) -> GiraffeJPConversationThread:
    thread = await db.get(GiraffeJPConversationThread, thread_id)
    if not thread or thread.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Conversation thread not found")
    return thread


async def create_conversation_thread(
    db: AsyncSession,
    body: ConversationThreadCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPConversationThread:
    thread = GiraffeJPConversationThread(
        tenant_id=tenant_id,
        project_id=body.project_id,
        order_id=body.order_id,
        participant_id=body.participant_id,
        customer_id=body.customer_id,
        thread_type=body.thread_type,
        channel=body.channel,
        status="OPEN",
    )
    db.add(thread)
    await db.flush()
    await emit_event(
        db=db,
        event_type=CONVERSATION_THREAD_CREATED,
        payload={
            "thread_id": str(thread.id),
            "thread_type": thread.thread_type,
            "channel": thread.channel,
        },
        tenant_id=tenant_id,
        project_id=thread.project_id,
        order_id=thread.order_id,
        triggered_by_user_id=user_id,
    )
    return thread


async def list_conversation_threads(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[GiraffeJPConversationThread]:
    result = await db.execute(
        select(GiraffeJPConversationThread)
        .where(GiraffeJPConversationThread.tenant_id == tenant_id)
        .order_by(GiraffeJPConversationThread.created_at.desc())
    )
    return result.scalars().all()


async def get_conversation_thread(
    db: AsyncSession,
    thread_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> GiraffeJPConversationThread:
    return await _get_thread(db, thread_id, tenant_id)


async def list_thread_messages(
    db: AsyncSession,
    thread_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> list[GiraffeJPMessage]:
    await _get_thread(db, thread_id, tenant_id)
    result = await db.execute(
        select(GiraffeJPMessage)
        .where(GiraffeJPMessage.tenant_id == tenant_id, GiraffeJPMessage.thread_id == thread_id)
        .order_by(GiraffeJPMessage.created_at)
    )
    return result.scalars().all()


async def record_inbound_message(
    db: AsyncSession,
    thread_id: uuid.UUID,
    body: InboundMessageCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPMessage:
    thread = await _get_thread(db, thread_id, tenant_id)
    message = GiraffeJPMessage(
        tenant_id=tenant_id,
        thread_id=thread_id,
        sender_type=body.sender_type,
        sender_id=body.sender_id,
        message_text=body.message_text,
        message_payload=body.message_payload,
        category_id=body.category_id,
        direction="INBOUND",
    )
    db.add(message)
    await db.flush()
    await emit_event(
        db=db,
        event_type=INBOUND_MESSAGE_RECORDED,
        payload={
            "message_id": str(message.id),
            "thread_id": str(thread_id),
            "sender_type": message.sender_type,
        },
        tenant_id=tenant_id,
        project_id=thread.project_id,
        order_id=thread.order_id,
        triggered_by_user_id=user_id,
    )
    return message


async def create_outbound_draft(
    db: AsyncSession,
    body: OutboundMessageDraftCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPOutboundMessageDraft:
    thread = await _get_thread(db, body.thread_id, tenant_id)

    auto_send = await is_auto_send_allowed(db, tenant_id, body.category_id, body.channel)

    draft = GiraffeJPOutboundMessageDraft(
        tenant_id=tenant_id,
        thread_id=body.thread_id,
        service_node_id=body.service_node_id,
        confirmation_request_id=body.confirmation_request_id,
        category_id=body.category_id,
        message_text=body.message_text,
        channel=body.channel,
        auto_send_allowed=auto_send,
        status="DRAFT",
        created_by=body.created_by,
    )
    db.add(draft)
    await db.flush()

    now = datetime.now(timezone.utc)

    if auto_send:
        draft.status = "AUTO_SENT"
        draft.sent_at = now

        message = GiraffeJPMessage(
            tenant_id=tenant_id,
            thread_id=body.thread_id,
            sender_type="SYSTEM",
            message_text=body.message_text,
            category_id=body.category_id,
            direction="OUTBOUND",
        )
        db.add(message)
        await db.flush()

        log = GiraffeJPMessageDeliveryLog(
            tenant_id=tenant_id,
            draft_id=draft.id,
            message_id=message.id,
            channel=body.channel,
            delivery_status="MOCK_SENT",
        )
        db.add(log)
        await db.flush()

        await emit_event(
            db=db,
            event_type=OUTBOUND_MESSAGE_AUTO_SENT,
            payload={
                "draft_id": str(draft.id),
                "message_id": str(message.id),
                "category_id": body.category_id,
            },
            tenant_id=tenant_id,
            project_id=thread.project_id,
            order_id=thread.order_id,
            triggered_by_user_id=user_id,
        )
    else:
        draft.status = "PENDING_HUMAN_CONFIRMATION"

        task = GiraffeJPCustomerServiceTask(
            tenant_id=tenant_id,
            task_type="REVIEW_OUTBOUND_MESSAGE",
            priority="P2",
            project_id=thread.project_id,
            order_id=thread.order_id,
            payload={"draft_id": str(draft.id), "category_id": body.category_id},
        )
        db.add(task)
        await db.flush()

        log = GiraffeJPMessageDeliveryLog(
            tenant_id=tenant_id,
            draft_id=draft.id,
            channel=body.channel,
            delivery_status="PENDING_HUMAN_CONFIRMATION",
        )
        db.add(log)
        await db.flush()

        await emit_event(
            db=db,
            event_type=OUTBOUND_MESSAGE_PENDING_APPROVAL,
            payload={
                "draft_id": str(draft.id),
                "category_id": body.category_id,
                "task_id": str(task.id),
            },
            tenant_id=tenant_id,
            project_id=thread.project_id,
            order_id=thread.order_id,
            triggered_by_user_id=user_id,
        )

    await emit_event(
        db=db,
        event_type=OUTBOUND_DRAFT_CREATED,
        payload={
            "draft_id": str(draft.id),
            "category_id": body.category_id,
            "auto_send_allowed": auto_send,
            "status": draft.status,
        },
        tenant_id=tenant_id,
        project_id=thread.project_id,
        order_id=thread.order_id,
        triggered_by_user_id=user_id,
    )
    return draft


async def list_outbound_drafts(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[GiraffeJPOutboundMessageDraft]:
    result = await db.execute(
        select(GiraffeJPOutboundMessageDraft)
        .where(GiraffeJPOutboundMessageDraft.tenant_id == tenant_id)
        .order_by(GiraffeJPOutboundMessageDraft.created_at.desc())
    )
    return result.scalars().all()


async def get_outbound_draft(
    db: AsyncSession,
    draft_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> GiraffeJPOutboundMessageDraft:
    draft = await db.get(GiraffeJPOutboundMessageDraft, draft_id)
    if not draft or draft.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Outbound draft not found")
    return draft


async def approve_outbound_draft(
    db: AsyncSession,
    draft_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPOutboundMessageDraft:
    draft = await get_outbound_draft(db, draft_id, tenant_id)
    if draft.status not in ("PENDING_HUMAN_CONFIRMATION", "DRAFT"):
        raise HTTPException(
            status_code=409,
            detail=f"Draft in status '{draft.status}' cannot be approved",
        )
    thread = await _get_thread(db, draft.thread_id, tenant_id)

    now = datetime.now(timezone.utc)
    draft.approved_by_user_id = user_id
    draft.status = "APPROVED_SENT"
    draft.sent_at = now

    message = GiraffeJPMessage(
        tenant_id=tenant_id,
        thread_id=draft.thread_id,
        sender_type="CS_STAFF",
        sender_id=user_id,
        message_text=draft.message_text,
        category_id=draft.category_id,
        direction="OUTBOUND",
    )
    db.add(message)
    await db.flush()

    log = GiraffeJPMessageDeliveryLog(
        tenant_id=tenant_id,
        draft_id=draft.id,
        message_id=message.id,
        channel=draft.channel,
        delivery_status="MOCK_SENT",
    )
    db.add(log)
    await db.flush()

    await emit_event(
        db=db,
        event_type=OUTBOUND_MESSAGE_APPROVED_SENT,
        payload={
            "draft_id": str(draft.id),
            "message_id": str(message.id),
            "approved_by": str(user_id),
        },
        tenant_id=tenant_id,
        project_id=thread.project_id,
        order_id=thread.order_id,
        triggered_by_user_id=user_id,
    )
    return draft


async def reject_outbound_draft(
    db: AsyncSession,
    draft_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPOutboundMessageDraft:
    draft = await get_outbound_draft(db, draft_id, tenant_id)
    thread = await _get_thread(db, draft.thread_id, tenant_id)
    draft.status = "REJECTED"
    await db.flush()
    await emit_event(
        db=db,
        event_type=OUTBOUND_MESSAGE_REJECTED,
        payload={"draft_id": str(draft.id), "rejected_by": str(user_id)},
        tenant_id=tenant_id,
        project_id=thread.project_id,
        order_id=thread.order_id,
        triggered_by_user_id=user_id,
    )
    return draft
