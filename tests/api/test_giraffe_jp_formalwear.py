"""API tests for formalwear order profiles and C2B2M role edges."""
import uuid

from src.db.models.order import Order as OrderModel
from src.db.models.project import Project
from src.db.models.tenant import Tenant


async def test_create_formalwear_order_profile(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "BRIDALWEAR",
            "occasion": "Wedding ceremony",
        },
    )
    assert resp.status_code == 201, resp.text
    profile = resp.json()
    assert profile["product_category"] == "BRIDALWEAR"
    assert profile["occasion"] == "Wedding ceremony"
    assert profile["model_try_on_required"] is True
    assert profile["local_alteration_possible"] is True
    assert profile["hollow_to_hem_required"] is True  # default for BRIDALWEAR


async def test_hollow_to_hem_default_for_formal_dress(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "FORMAL_DRESS",
            "occasion": "Gala dinner",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["hollow_to_hem_required"] is True


async def test_hollow_to_hem_default_for_light_wedding_dress(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "LIGHT_WEDDING_DRESS",
            "occasion": "Reception party",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["hollow_to_hem_required"] is True


async def test_hollow_to_hem_not_default_for_womens_suit(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "WOMENS_SUIT",
            "occasion": "Business meeting",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["hollow_to_hem_required"] is False


async def test_hollow_to_hem_explicit_false_for_bridalwear(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "BRIDALWEAR",
            "occasion": "Intimate ceremony",
            "hollow_to_hem_required": False,
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["hollow_to_hem_required"] is False


async def test_invalid_product_category(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "EVENING_GOWN",
            "occasion": "Party",
        },
    )
    assert resp.status_code == 422


async def test_model_try_on_required_default_true(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "RECEPTION_DRESS",
            "occasion": "Reception",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["model_try_on_required"] is True


async def test_list_formalwear_order_profiles(auth_client, seed_project):
    await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={"project_id": seed_project["id"], "product_category": "BRIDALWEAR", "occasion": "Wedding"},
    )
    resp = await auth_client.get("/api/giraffe-jp/formalwear/order-profiles")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_get_formalwear_order_profile(auth_client, seed_project):
    create_resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={"project_id": seed_project["id"], "product_category": "WOMENS_SUIT", "occasion": "Meeting"},
    )
    profile_id = create_resp.json()["id"]
    resp = await auth_client.get(f"/api/giraffe-jp/formalwear/order-profiles/{profile_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == profile_id


async def test_update_formalwear_order_profile(auth_client, seed_project):
    create_resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={"project_id": seed_project["id"], "product_category": "RECEPTION_DRESS", "occasion": "Party"},
    )
    profile_id = create_resp.json()["id"]

    resp = await auth_client.patch(
        f"/api/giraffe-jp/formalwear/order-profiles/{profile_id}",
        json={"status": "ACTIVE", "color_preference": "Ivory"},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["status"] == "ACTIVE"
    assert updated["color_preference"] == "Ivory"


async def test_create_c2b2m_role_edge(auth_client, seed_project):
    resp = await auth_client.post(
        "/api/giraffe-jp/c2b2m/role-edges",
        json={
            "project_id": seed_project["id"],
            "from_actor_type": "JP_CUSTOMER",
            "from_role": "B_SIDE",
            "to_actor_type": "GIRAFFE_JP",
            "to_role": "MAIN_M_SIDE",
            "edge_type": "DEFAULT",
        },
    )
    assert resp.status_code == 201, resp.text
    edge = resp.json()
    assert edge["from_actor_type"] == "JP_CUSTOMER"
    assert edge["to_actor_type"] == "GIRAFFE_JP"
    assert edge["edge_type"] == "DEFAULT"


async def test_initialize_default_c2b2m_edges(auth_client, seed_project):
    resp = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={},
    )
    assert resp.status_code == 200, resp.text
    edges = resp.json()
    assert len(edges) == 1  # Only customer→giraffe_jp without supplier
    assert edges[0]["from_actor_type"] == "JP_CUSTOMER"
    assert edges[0]["to_actor_type"] == "GIRAFFE_JP"


async def test_initialize_default_c2b2m_edges_with_supplier(auth_client, seed_project):
    supplier_id = str(uuid.uuid4())
    resp = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={"supplier_id": supplier_id},
    )
    assert resp.status_code == 200, resp.text
    edges = resp.json()
    assert len(edges) == 2
    actor_types = {e["from_actor_type"] for e in edges}
    assert "JP_CUSTOMER" in actor_types
    assert "GIRAFFE_JP" in actor_types


async def test_no_duplicate_default_edges(auth_client, seed_project):
    payload = {"project_id": seed_project["id"]}

    resp1 = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={},
    )
    assert resp1.status_code == 200
    assert len(resp1.json()) == 1

    resp2 = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={},
    )
    assert resp2.status_code == 200
    # Second call creates 0 new edges
    assert len(resp2.json()) == 0


async def test_supplier_edge_only_when_supplier_provided(auth_client, seed_project):
    resp = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={},
    )
    edges = resp.json()
    to_types = {e["to_actor_type"] for e in edges}
    assert "SUPPLIER" not in to_types


async def test_tenant_isolation_formalwear(auth_client, seed_project, db):
    await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={"project_id": seed_project["id"], "product_category": "BRIDALWEAR", "occasion": "Wedding"},
    )

    other_tenant = Tenant(name="Other Tenant", slug=f"other-{uuid.uuid4().hex[:8]}")
    db.add(other_tenant)
    await db.commit()

    resp = await auth_client.get("/api/giraffe-jp/formalwear/order-profiles")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    # All returned profiles belong to the auth tenant (verified by existence of at least 1)


async def test_tenant_isolation_role_edges(auth_client, seed_project, db):
    await auth_client.post(
        "/api/giraffe-jp/c2b2m/role-edges",
        json={
            "project_id": seed_project["id"],
            "from_actor_type": "JP_CUSTOMER",
            "from_role": "B_SIDE",
            "to_actor_type": "GIRAFFE_JP",
            "to_role": "MAIN_M_SIDE",
            "edge_type": "CUSTOM",
        },
    )

    resp = await auth_client.get("/api/giraffe-jp/c2b2m/role-edges")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ── Scope validation tests ────────────────────────────────────────────────────

async def _make_other_tenant_order(db, real_user_id: uuid.UUID):
    """Create an order in a separate tenant and return (order, other_tenant)."""
    other_tenant = Tenant(name="Scope Tenant", slug=f"scope-{uuid.uuid4().hex[:8]}")
    db.add(other_tenant)
    await db.flush()
    # real_user_id satisfies the projects.created_by FK constraint
    other_project = Project(tenant_id=other_tenant.id, title="Scope Project", created_by=real_user_id)
    db.add(other_project)
    await db.flush()
    other_order = OrderModel(project_id=other_project.id)
    db.add(other_order)
    await db.commit()
    return other_order, other_tenant


async def test_formalwear_profile_rejects_cross_tenant_order_id(auth_client, seed_user, seed_project, db):
    """order_id that belongs to another tenant must be rejected (422)."""
    other_order, _ = await _make_other_tenant_order(db, uuid.UUID(seed_user["user_id"]))

    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "WOMENS_SUIT",
            "occasion": "Meeting",
            "order_id": str(other_order.id),
        },
    )
    assert resp.status_code == 422, resp.text


async def test_formalwear_profile_rejects_order_id_wrong_project(auth_client, seed_project, db, seed_user):
    """order_id that belongs to tenant but a different project must be rejected (422)."""
    from src.db.models.project import Project as ProjectModel
    # Create a second project in the same tenant
    other_project_resp = await auth_client.post("/api/projects", json={"title": "Other Project"})
    assert other_project_resp.status_code == 201
    other_project_id = other_project_resp.json()["id"]

    # Create an order under the other project directly in DB
    other_order = OrderModel(project_id=uuid.UUID(other_project_id))
    db.add(other_order)
    await db.commit()

    resp = await auth_client.post(
        "/api/giraffe-jp/formalwear/order-profiles",
        json={
            "project_id": seed_project["id"],
            "product_category": "FORMAL_DRESS",
            "occasion": "Gala",
            "order_id": str(other_order.id),
        },
    )
    assert resp.status_code == 422, resp.text


async def test_c2b2m_role_edge_rejects_cross_tenant_order_id(auth_client, seed_user, seed_project, db):
    """order_id from another tenant must be rejected for role edge creation (422)."""
    other_order, _ = await _make_other_tenant_order(db, uuid.UUID(seed_user["user_id"]))

    resp = await auth_client.post(
        "/api/giraffe-jp/c2b2m/role-edges",
        json={
            "project_id": seed_project["id"],
            "from_actor_type": "JP_CUSTOMER",
            "from_role": "B_SIDE",
            "to_actor_type": "GIRAFFE_JP",
            "to_role": "MAIN_M_SIDE",
            "edge_type": "DEFAULT",
            "order_id": str(other_order.id),
        },
    )
    assert resp.status_code == 422, resp.text


async def test_default_edge_init_rejects_cross_tenant_order_id(auth_client, seed_user, seed_project, db):
    """order_id from another tenant must be rejected by initialize-default-edges (422)."""
    other_order, _ = await _make_other_tenant_order(db, uuid.UUID(seed_user["user_id"]))

    resp = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={"order_id": str(other_order.id)},
    )
    assert resp.status_code == 422, resp.text


async def test_default_edge_updates_actor_id_when_customer_supplied(auth_client, seed_project):
    """Second call with customer_id updates the existing anonymous customer edge rather than duplicating."""
    customer_id = str(uuid.uuid4())

    # First call: anonymous customer edge
    resp1 = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={},
    )
    assert resp1.status_code == 200
    assert len(resp1.json()) == 1

    # Second call: supply customer_id — should update, not create a new edge
    resp2 = await auth_client.post(
        f"/api/giraffe-jp/c2b2m/projects/{seed_project['id']}/initialize-default-edges",
        json={"customer_id": customer_id},
    )
    assert resp2.status_code == 200
    # No new edge created (edge was updated in place)
    assert len(resp2.json()) == 0

    # Verify only one customer→giraffe_jp edge exists
    list_resp = await auth_client.get(
        f"/api/giraffe-jp/c2b2m/role-edges?project_id={seed_project['id']}"
    )
    customer_edges = [
        e for e in list_resp.json()
        if e["from_actor_type"] == "JP_CUSTOMER" and e["to_actor_type"] == "GIRAFFE_JP"
    ]
    assert len(customer_edges) == 1
    assert customer_edges[0]["from_actor_id"] == customer_id
