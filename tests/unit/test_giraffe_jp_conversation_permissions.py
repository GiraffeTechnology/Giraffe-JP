"""Unit tests for outbound draft permission enforcement using mocks."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_thread(tenant_id, project_id=None, order_id=None):
    thread = MagicMock()
    thread.id = uuid.uuid4()
    thread.tenant_id = tenant_id
    thread.project_id = project_id
    thread.order_id = order_id
    return thread


@pytest.mark.asyncio
async def test_auto_send_category_creates_message_and_delivery_log():
    from src.giraffe_jp.conversations import create_outbound_draft
    from src.giraffe_jp.schemas import OutboundMessageDraftCreate

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()

    body = OutboundMessageDraftCreate(
        thread_id=thread_id,
        category_id="CUSTOMER_ORDER_RECEIVED_UPDATE",
        message_text="Your order has been received.",
        channel="WEB_DIALOG",
    )

    db = AsyncMock()
    added_objects = []

    def capture_add(obj):
        added_objects.append(obj)

    db.add = capture_add
    db.flush = AsyncMock()

    thread = _make_thread(tenant_id)

    with (
        patch("src.giraffe_jp.conversations._get_thread", AsyncMock(return_value=thread)),
        patch("src.giraffe_jp.conversations.is_auto_send_allowed", AsyncMock(return_value=True)),
        patch("src.giraffe_jp.conversations.emit_event", AsyncMock()),
    ):
        draft = await create_outbound_draft(db, body, tenant_id, user_id)

    assert draft.status == "AUTO_SENT"
    assert draft.sent_at is not None
    assert draft.auto_send_allowed is True

    from src.db.models.giraffe_jp import GiraffeJPMessage, GiraffeJPMessageDeliveryLog
    message_objs = [o for o in added_objects if isinstance(o, GiraffeJPMessage)]
    log_objs = [o for o in added_objects if isinstance(o, GiraffeJPMessageDeliveryLog)]
    assert len(message_objs) == 1
    assert len(log_objs) == 1
    assert log_objs[0].delivery_status == "MOCK_SENT"


@pytest.mark.asyncio
async def test_manual_category_creates_pending_task():
    from src.giraffe_jp.conversations import create_outbound_draft
    from src.giraffe_jp.schemas import OutboundMessageDraftCreate

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()

    body = OutboundMessageDraftCreate(
        thread_id=thread_id,
        category_id="CUSTOMER_PRICE_CONFIRMATION",
        message_text="Please confirm the price.",
        channel="WEB_DIALOG",
    )

    db = AsyncMock()
    added_objects = []

    def capture_add(obj):
        added_objects.append(obj)

    db.add = capture_add
    db.flush = AsyncMock()

    thread = _make_thread(tenant_id)

    with (
        patch("src.giraffe_jp.conversations._get_thread", AsyncMock(return_value=thread)),
        patch("src.giraffe_jp.conversations.is_auto_send_allowed", AsyncMock(return_value=False)),
        patch("src.giraffe_jp.conversations.emit_event", AsyncMock()),
    ):
        draft = await create_outbound_draft(db, body, tenant_id, user_id)

    assert draft.status == "PENDING_HUMAN_CONFIRMATION"
    assert draft.auto_send_allowed is False

    from src.db.models.giraffe_jp import GiraffeJPCustomerServiceTask, GiraffeJPMessageDeliveryLog
    task_objs = [o for o in added_objects if isinstance(o, GiraffeJPCustomerServiceTask)]
    log_objs = [o for o in added_objects if isinstance(o, GiraffeJPMessageDeliveryLog)]
    assert len(task_objs) == 1
    assert task_objs[0].task_type == "REVIEW_OUTBOUND_MESSAGE"
    assert len(log_objs) == 1
    assert log_objs[0].delivery_status == "PENDING_HUMAN_CONFIRMATION"


@pytest.mark.asyncio
async def test_unknown_category_creates_pending_task():
    """Unknown category → is_auto_send_allowed returns False → pending task."""
    from src.giraffe_jp.conversations import create_outbound_draft
    from src.giraffe_jp.schemas import OutboundMessageDraftCreate

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    thread_id = uuid.uuid4()

    body = OutboundMessageDraftCreate(
        thread_id=thread_id,
        category_id="TOTALLY_UNKNOWN_CATEGORY_XYZ",
        message_text="Some message.",
        channel="EMAIL",
    )

    db = AsyncMock()
    added_objects = []
    db.add = lambda obj: added_objects.append(obj)
    db.flush = AsyncMock()

    thread = _make_thread(tenant_id)

    with (
        patch("src.giraffe_jp.conversations._get_thread", AsyncMock(return_value=thread)),
        patch("src.giraffe_jp.conversations.is_auto_send_allowed", AsyncMock(return_value=False)),
        patch("src.giraffe_jp.conversations.emit_event", AsyncMock()),
    ):
        draft = await create_outbound_draft(db, body, tenant_id, user_id)

    assert draft.status == "PENDING_HUMAN_CONFIRMATION"

    from src.db.models.giraffe_jp import GiraffeJPCustomerServiceTask
    task_objs = [o for o in added_objects if isinstance(o, GiraffeJPCustomerServiceTask)]
    assert len(task_objs) == 1
