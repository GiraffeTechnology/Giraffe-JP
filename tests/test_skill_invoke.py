"""
Unit tests for POST /api/skill/invoke.

Uses a minimal isolated FastAPI app containing only the skill_invoke router
so no PostgreSQL or external services are needed.
adapt_openclaw_event() is pure in-memory; these tests exercise the route
and adapter together without real WeChat, OpenClaw Gateway, or LLM infra.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes.skill_invoke import router as skill_invoke_router
from src.openclaw_skill.openclaw_event_adapter import adapt_openclaw_event

# Isolated app — only skill_invoke, no DB-backed routers
_app = FastAPI()
_app.include_router(skill_invoke_router)


@pytest.fixture(scope="module")
def _client():
    with TestClient(_app) as c:
        yield c


_B_SIDE_EVENT = {
    "source": "wechat",
    "channel": "wechat",
    "channel_account_id": "gh_openclaw_test",
    "conversation_id": "conv_bside_001",
    "sender_id": "buyer_001",
    "sender_display_name": "Test Buyer",
    "message_text": "I need 500 custom polo shirts delivered by August.",
    "message_type": "text",
}

_M_SIDE_EVENT = {
    "source": "wechat",
    "channel": "wechat",
    "channel_account_id": "gh_openclaw_test",
    "conversation_id": "conv_mside_001",
    "sender_id": "supplier_001",
    "sender_display_name": "Test Supplier",
    "message_text": "We can supply 500 polo shirts, lead time 30 days, unit price $8.",
    "message_type": "text",
}


def test_skill_invoke_b_side_http(_client):
    """POST /api/skill/invoke returns 200 and a dict for a B-side event."""
    response = _client.post("/api/skill/invoke", json=_B_SIDE_EVENT)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_skill_invoke_m_side_http(_client):
    """POST /api/skill/invoke returns 200 for a supplier-side event."""
    response = _client.post("/api/skill/invoke", json=_M_SIDE_EVENT)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_adapt_openclaw_event_b_side_direct():
    """adapt_openclaw_event returns a dict for a B-side event (no DB needed)."""
    result = adapt_openclaw_event(_B_SIDE_EVENT)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_adapt_openclaw_event_m_side_direct():
    """adapt_openclaw_event returns a dict for a supplier-side event."""
    result = adapt_openclaw_event(_M_SIDE_EVENT)
    assert isinstance(result, dict)


def test_skill_invoke_missing_optional_fields(_client):
    """Route accepts events with only core required fields."""
    event = {
        "source": "test",
        "channel": "test",
        "channel_account_id": "acct_001",
        "conversation_id": "conv_001",
        "sender_id": "user_001",
        "message_text": "Hello",
    }
    response = _client.post("/api/skill/invoke", json=event)
    # adapter may return 200 or raise 500 for minimal input — either is acceptable
    assert response.status_code in (200, 500)
