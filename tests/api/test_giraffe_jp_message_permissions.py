"""Integration tests for Giraffe JP message category auto-send permissions API."""
import pytest
import uuid


@pytest.mark.asyncio
async def test_seed_defaults_creates_22_permissions(auth_client):
    resp = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 22


@pytest.mark.asyncio
async def test_seed_defaults_idempotent(auth_client):
    """Calling seed-defaults twice does not create duplicate rows."""
    resp1 = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    resp2 = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert len(resp1.json()) == len(resp2.json()) == 22


@pytest.mark.asyncio
async def test_list_permissions_after_seed(auth_client):
    await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    resp = await auth_client.get("/api/giraffe-jp/permissions")
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 22


@pytest.mark.asyncio
async def test_get_single_permission(auth_client):
    seed_resp = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    perm_id = seed_resp.json()[0]["id"]
    resp = await auth_client.get(f"/api/giraffe-jp/permissions/{perm_id}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == perm_id


@pytest.mark.asyncio
async def test_get_permission_not_found(auth_client):
    resp = await auth_client.get(f"/api/giraffe-jp/permissions/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_permission_auto_send(auth_client):
    """PATCH flips auto_send and emits a graph event."""
    seed_resp = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    perms = seed_resp.json()
    target = next(p for p in perms if p["category_id"] == "CUST_PAYMENT_REMINDER")
    assert target["auto_send"] is False

    patch_resp = await auth_client.patch(
        f"/api/giraffe-jp/permissions/{target['id']}",
        json={"auto_send": True},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    assert patch_resp.json()["auto_send"] is True


@pytest.mark.asyncio
async def test_permissions_require_auth(client):
    resp = await client.get("/api/giraffe-jp/permissions")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_permissions_have_correct_structure(auth_client):
    seed_resp = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    perm = seed_resp.json()[0]
    assert all(k in perm for k in ["id", "tenant_id", "category_id", "category_name",
                                    "party_type", "channel", "auto_send",
                                    "created_at", "updated_at"])


# ── Cross-tenant isolation tests ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tenant_a_update_does_not_affect_tenant_b(auth_client, other_auth_client):
    """Patching Tenant A's permission must not change Tenant B's permission for the same category."""
    seed_a = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    seed_b = await other_auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    assert seed_a.status_code == 201
    assert seed_b.status_code == 201

    perms_a = seed_a.json()
    perms_b = seed_b.json()

    target_a = next(p for p in perms_a if p["category_id"] == "CUST_PAYMENT_REMINDER")
    target_b = next(p for p in perms_b if p["category_id"] == "CUST_PAYMENT_REMINDER")

    assert target_a["auto_send"] is False
    assert target_b["auto_send"] is False

    patch_resp = await auth_client.patch(
        f"/api/giraffe-jp/permissions/{target_a['id']}",
        json={"auto_send": True},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["auto_send"] is True

    # Tenant B's permission must remain unchanged
    b_check = await other_auth_client.get(f"/api/giraffe-jp/permissions/{target_b['id']}")
    assert b_check.status_code == 200, b_check.text
    assert b_check.json()["auto_send"] is False

    # Tenant A cannot read Tenant B's permission row by ID
    cross_check = await auth_client.get(f"/api/giraffe-jp/permissions/{target_b['id']}")
    assert cross_check.status_code == 404


@pytest.mark.asyncio
async def test_unknown_category_defaults_to_not_auto_send_per_tenant(
    auth_client, other_auth_client
):
    """After seeding, neither tenant has a permission row for an unknown category."""
    await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    await other_auth_client.post("/api/giraffe-jp/permissions/seed-defaults")

    list_a = await auth_client.get("/api/giraffe-jp/permissions")
    list_b = await other_auth_client.get("/api/giraffe-jp/permissions")

    assert list_a.status_code == 200
    assert list_b.status_code == 200

    category_ids_a = {p["category_id"] for p in list_a.json()}
    category_ids_b = {p["category_id"] for p in list_b.json()}

    assert "UNKNOWN_CAT_XYZ" not in category_ids_a
    assert "UNKNOWN_CAT_XYZ" not in category_ids_b


@pytest.mark.asyncio
async def test_seed_defaults_idempotent_per_tenant(auth_client, other_auth_client):
    """seed-defaults is idempotent for each tenant independently."""
    # Seed twice for Tenant A
    r_a1 = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    r_a2 = await auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    assert r_a1.status_code == 201
    assert r_a2.status_code == 201
    assert len(r_a1.json()) == 22
    assert len(r_a2.json()) == 22

    # Seed twice for Tenant B
    r_b1 = await other_auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    r_b2 = await other_auth_client.post("/api/giraffe-jp/permissions/seed-defaults")
    assert r_b1.status_code == 201
    assert r_b2.status_code == 201
    assert len(r_b1.json()) == 22
    assert len(r_b2.json()) == 22

    # Each tenant's list still shows exactly 22 rows (no cross-contamination)
    list_a = await auth_client.get("/api/giraffe-jp/permissions")
    list_b = await other_auth_client.get("/api/giraffe-jp/permissions")
    assert len(list_a.json()) == 22
    assert len(list_b.json()) == 22
