"""Unit tests for is_auto_send_allowed() logic using mocks."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.giraffe_jp.message_permissions import is_auto_send_allowed


def _make_perm(auto_send: bool, is_active: bool = True, channel: str = "ANY"):
    perm = MagicMock()
    perm.auto_send = auto_send
    perm.is_active = is_active
    perm.channel = channel
    return perm


def _mock_db_with_perm(perm):
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = perm
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.mark.asyncio
async def test_is_auto_send_allowed_missing_category():
    db = _mock_db_with_perm(None)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "UNKNOWN_CATEGORY")
    assert result is False


@pytest.mark.asyncio
async def test_is_auto_send_allowed_inactive_category():
    perm = _make_perm(auto_send=True, is_active=False)
    db = _mock_db_with_perm(perm)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_ORDER_RECEIVED_UPDATE")
    assert result is False


@pytest.mark.asyncio
async def test_is_auto_send_allowed_auto_send_true():
    perm = _make_perm(auto_send=True, is_active=True, channel="ANY")
    db = _mock_db_with_perm(perm)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_ORDER_RECEIVED_UPDATE")
    assert result is True


@pytest.mark.asyncio
async def test_is_auto_send_allowed_auto_send_false():
    perm = _make_perm(auto_send=False, is_active=True, channel="ANY")
    db = _mock_db_with_perm(perm)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_PRICE_CONFIRMATION")
    assert result is False


@pytest.mark.asyncio
async def test_is_auto_send_allowed_channel_any_matches_any_channel():
    perm = _make_perm(auto_send=True, is_active=True, channel="ANY")
    db = _mock_db_with_perm(perm)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_ORDER_RECEIVED_UPDATE", channel="EMAIL")
    assert result is True


@pytest.mark.asyncio
async def test_is_auto_send_allowed_channel_mismatch():
    perm = _make_perm(auto_send=True, is_active=True, channel="WEB_DIALOG")
    db = _mock_db_with_perm(perm)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_ORDER_RECEIVED_UPDATE", channel="EMAIL")
    assert result is False


@pytest.mark.asyncio
async def test_is_auto_send_allowed_channel_exact_match():
    perm = _make_perm(auto_send=True, is_active=True, channel="EMAIL")
    db = _mock_db_with_perm(perm)
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_ORDER_RECEIVED_UPDATE", channel="EMAIL")
    assert result is True


@pytest.mark.asyncio
async def test_is_auto_send_allowed_no_channel_supplied():
    perm = _make_perm(auto_send=True, is_active=True, channel="WEB_DIALOG")
    db = _mock_db_with_perm(perm)
    # No channel supplied — channel filter is skipped
    result = await is_auto_send_allowed(db, uuid.uuid4(), "CUSTOMER_ORDER_RECEIVED_UPDATE")
    assert result is True
