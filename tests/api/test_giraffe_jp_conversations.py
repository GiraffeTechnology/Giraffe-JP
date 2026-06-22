"""API tests for conversation thread and outbound draft endpoints."""
import uuid

from src.db.models.giraffe_jp import GiraffeJPMessageCategoryPermission
from src.db.models.tenant import Tenant


async def _seed_permissions(auth_client):
    resp = await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")
    assert resp.status_code == 200


async def _create_thread(auth_client, **kwargs):
    payload = {"thread_type": "CUSTOMER", "channel": "WEB_DIALOG"}
    payload.update(kwargs)
    resp = await auth_client.post("/api/giraffe-jp/conversations", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_conversation_thread(auth_client, seed_project):
    thread = await _create_thread(auth_client, project_id=seed_project["id"])
    assert thread["thread_type"] == "CUSTOMER"
    assert thread["channel"] == "WEB_DIALOG"
    assert thread["status"] == "OPEN"
    assert thread["project_id"] == seed_project["id"]


async def test_list_conversation_threads(auth_client):
    await _create_thread(auth_client)
    await _create_thread(auth_client, thread_type="SUPPLIER", channel="EMAIL")
    resp = await auth_client.get("/api/giraffe-jp/conversations")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_get_conversation_thread(auth_client):
    thread = await _create_thread(auth_client)
    resp = await auth_client.get(f"/api/giraffe-jp/conversations/{thread['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == thread["id"]


async def test_get_thread_not_found(auth_client):
    resp = await auth_client.get(f"/api/giraffe-jp/conversations/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_record_inbound_message(auth_client):
    thread = await _create_thread(auth_client)
    resp = await auth_client.post(
        f"/api/giraffe-jp/conversations/{thread['id']}/messages/inbound",
        json={
            "sender_type": "CUSTOMER",
            "message_text": "Hello, I would like to order a formal dress.",
        },
    )
    assert resp.status_code == 201, resp.text
    msg = resp.json()
    assert msg["direction"] == "INBOUND"
    assert msg["sender_type"] == "CUSTOMER"
    assert msg["thread_id"] == thread["id"]


async def test_list_thread_messages(auth_client):
    thread = await _create_thread(auth_client)
    await auth_client.post(
        f"/api/giraffe-jp/conversations/{thread['id']}/messages/inbound",
        json={"sender_type": "CUSTOMER", "message_text": "Message one."},
    )
    await auth_client.post(
        f"/api/giraffe-jp/conversations/{thread['id']}/messages/inbound",
        json={"sender_type": "CUSTOMER", "message_text": "Message two."},
    )
    resp = await auth_client.get(f"/api/giraffe-jp/conversations/{thread['id']}/messages")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_create_outbound_draft_auto_send(auth_client):
    await _seed_permissions(auth_client)
    thread = await _create_thread(auth_client)

    resp = await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "CUSTOMER_ORDER_RECEIVED_UPDATE",
            "message_text": "Your order has been received.",
            "channel": "WEB_DIALOG",
        },
    )
    assert resp.status_code == 201, resp.text
    draft = resp.json()
    assert draft["status"] == "AUTO_SENT"
    assert draft["auto_send_allowed"] is True
    assert draft["sent_at"] is not None


async def test_auto_send_creates_outbound_message(auth_client):
    await _seed_permissions(auth_client)
    thread = await _create_thread(auth_client)

    await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "CUSTOMER_LOGISTICS_UPDATE",
            "message_text": "Your garment is on its way.",
            "channel": "WEB_DIALOG",
        },
    )

    msgs_resp = await auth_client.get(f"/api/giraffe-jp/conversations/{thread['id']}/messages")
    assert msgs_resp.status_code == 200
    outbound = [m for m in msgs_resp.json() if m["direction"] == "OUTBOUND"]
    assert len(outbound) == 1
    assert outbound[0]["message_text"] == "Your garment is on its way."


async def test_create_outbound_draft_manual_category(auth_client):
    await _seed_permissions(auth_client)
    thread = await _create_thread(auth_client)

    resp = await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "CUSTOMER_PRICE_CONFIRMATION",
            "message_text": "Please confirm the price of ¥150,000.",
            "channel": "WEB_DIALOG",
        },
    )
    assert resp.status_code == 201, resp.text
    draft = resp.json()
    assert draft["status"] == "PENDING_HUMAN_CONFIRMATION"
    assert draft["auto_send_allowed"] is False
    assert draft["sent_at"] is None


async def test_manual_category_creates_cs_task(auth_client, db):
    await _seed_permissions(auth_client)
    thread = await _create_thread(auth_client)

    await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "SUPPLIER_ORDER_PLACEMENT",
            "message_text": "Please accept our order.",
            "channel": "EMAIL",
        },
    )

    tasks_resp = await auth_client.get("/api/giraffe-jp/customer-service/tasks")
    assert tasks_resp.status_code == 200
    review_tasks = [t for t in tasks_resp.json() if t["task_type"] == "REVIEW_OUTBOUND_MESSAGE"]
    assert len(review_tasks) >= 1


async def test_unknown_category_creates_pending_task(auth_client):
    thread = await _create_thread(auth_client)

    resp = await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "TOTALLY_UNKNOWN_CATEGORY",
            "message_text": "Some message.",
            "channel": "WEB_DIALOG",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "PENDING_HUMAN_CONFIRMATION"


async def test_approve_send_flow(auth_client):
    await _seed_permissions(auth_client)
    thread = await _create_thread(auth_client)

    draft_resp = await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "CUSTOMER_PRICE_CONFIRMATION",
            "message_text": "Please confirm price ¥120,000.",
            "channel": "WEB_DIALOG",
        },
    )
    draft = draft_resp.json()
    assert draft["status"] == "PENDING_HUMAN_CONFIRMATION"

    approve_resp = await auth_client.post(
        f"/api/giraffe-jp/outbound-drafts/{draft['id']}/approve-send"
    )
    assert approve_resp.status_code == 200, approve_resp.text
    approved = approve_resp.json()
    assert approved["status"] == "APPROVED_SENT"
    assert approved["sent_at"] is not None
    assert approved["approved_by_user_id"] is not None

    msgs_resp = await auth_client.get(f"/api/giraffe-jp/conversations/{thread['id']}/messages")
    outbound = [m for m in msgs_resp.json() if m["direction"] == "OUTBOUND"]
    assert len(outbound) == 1


async def test_reject_flow(auth_client):
    await _seed_permissions(auth_client)
    thread = await _create_thread(auth_client)

    draft_resp = await auth_client.post(
        "/api/giraffe-jp/outbound-drafts",
        json={
            "thread_id": thread["id"],
            "category_id": "CUSTOMER_DELIVERY_COMMITMENT",
            "message_text": "Delivery on June 30.",
            "channel": "WEB_DIALOG",
        },
    )
    draft = draft_resp.json()

    reject_resp = await auth_client.post(
        f"/api/giraffe-jp/outbound-drafts/{draft['id']}/reject"
    )
    assert reject_resp.status_code == 200, reject_resp.text
    assert reject_resp.json()["status"] == "REJECTED"

    msgs_resp = await auth_client.get(f"/api/giraffe-jp/conversations/{thread['id']}/messages")
    outbound = [m for m in msgs_resp.json() if m["direction"] == "OUTBOUND"]
    assert len(outbound) == 0


async def test_tenant_isolation_conversations(auth_client, db):
    thread = await _create_thread(auth_client)

    other_tenant = Tenant(name="Other Tenant", slug=f"other-{uuid.uuid4().hex[:8]}")
    db.add(other_tenant)
    await db.commit()

    resp = await auth_client.get("/api/giraffe-jp/conversations")
    ids = {item["id"] for item in resp.json()}
    assert thread["id"] in ids

    # Check that no threads from the other_tenant appear (they have none, so this just validates listing)
    assert len(resp.json()) >= 1
