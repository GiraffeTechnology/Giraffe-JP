"""API tests for message category permission endpoints."""
import uuid

from src.db.models.giraffe_jp import GiraffeJPMessageCategoryPermission
from src.db.models.tenant import Tenant


async def test_seed_defaults(auth_client):
    resp = await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 22  # 9 customer + 9 supplier + 4 model partner

    category_ids = {item["category_id"] for item in data}
    assert "CUSTOMER_ORDER_RECEIVED_UPDATE" in category_ids
    assert "CUSTOMER_PRICE_CONFIRMATION" in category_ids
    assert "SUPPLIER_ORDER_PLACEMENT" in category_ids
    assert "MODEL_PARTNER_AVAILABILITY_REQUEST" in category_ids


async def test_seed_defaults_is_idempotent(auth_client):
    resp1 = await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")
    assert resp1.status_code == 200
    resp2 = await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")
    assert resp2.status_code == 200
    # Both calls return the same 22 categories with no duplicates
    assert len(resp2.json()) == 22


async def test_list_defaults(auth_client):
    await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")
    resp = await auth_client.get("/api/giraffe-jp/message-category-permissions")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 22


async def test_get_category(auth_client):
    await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")
    resp = await auth_client.get(
        "/api/giraffe-jp/message-category-permissions/CUSTOMER_ORDER_RECEIVED_UPDATE"
    )
    assert resp.status_code == 200, resp.text
    perm = resp.json()
    assert perm["category_id"] == "CUSTOMER_ORDER_RECEIVED_UPDATE"
    assert perm["auto_send"] is True
    assert perm["is_active"] is True


async def test_get_category_not_found(auth_client):
    resp = await auth_client.get(
        "/api/giraffe-jp/message-category-permissions/DOES_NOT_EXIST"
    )
    assert resp.status_code == 404


async def test_update_auto_send(auth_client):
    await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")

    resp = await auth_client.patch(
        "/api/giraffe-jp/message-category-permissions/CUSTOMER_ORDER_RECEIVED_UPDATE",
        json={"auto_send": False},
    )
    assert resp.status_code == 200, resp.text
    updated = resp.json()
    assert updated["auto_send"] is False

    # Confirm persisted
    get_resp = await auth_client.get(
        "/api/giraffe-jp/message-category-permissions/CUSTOMER_ORDER_RECEIVED_UPDATE"
    )
    assert get_resp.json()["auto_send"] is False


async def test_unknown_category_defaults_to_false(auth_client, db):
    """Tenant has no seeded permissions → is_auto_send_allowed returns False."""
    # We test this indirectly via a unit test; API-level: get unknown returns 404
    resp = await auth_client.get(
        "/api/giraffe-jp/message-category-permissions/UNKNOWN_CAT"
    )
    assert resp.status_code == 404


async def test_inactive_category_is_retrievable_but_flagged(auth_client):
    await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")

    await auth_client.patch(
        "/api/giraffe-jp/message-category-permissions/CUSTOMER_LOGISTICS_UPDATE",
        json={"is_active": False},
    )
    resp = await auth_client.get(
        "/api/giraffe-jp/message-category-permissions/CUSTOMER_LOGISTICS_UPDATE"
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_tenant_isolation(auth_client, db):
    await auth_client.post("/api/giraffe-jp/message-category-permissions/seed-defaults")

    other_tenant = Tenant(name="Other Tenant", slug=f"other-{uuid.uuid4().hex[:8]}")
    db.add(other_tenant)
    await db.flush()

    other_perm = GiraffeJPMessageCategoryPermission(
        tenant_id=other_tenant.id,
        category_id="CUSTOMER_ORDER_RECEIVED_UPDATE",
        category_name="Other Tenant Category",
        direction="CUSTOMER",
        channel="ANY",
        auto_send=False,
        is_active=True,
    )
    db.add(other_perm)
    await db.commit()

    # Auth client's tenant should see their own permissions
    resp = await auth_client.get(
        "/api/giraffe-jp/message-category-permissions/CUSTOMER_ORDER_RECEIVED_UPDATE"
    )
    assert resp.status_code == 200
    # The auth client's tenant has auto_send=True (from seed)
    assert resp.json()["auto_send"] is True
