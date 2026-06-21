import uuid

from src.db.models.giraffe_jp import GiraffeJPServiceNode
from src.db.models.tenant import Tenant


async def test_create_service_node_confirmation_and_task(auth_client, seed_project):
    node_resp = await auth_client.post(
        "/api/giraffe-jp/service-nodes",
        json={
            "project_id": seed_project["id"],
            "node_type": "MEASUREMENT_REQUIRED",
            "priority": "P0",
            "payload": {"source": "api-test"},
        },
    )
    assert node_resp.status_code == 201, node_resp.text
    node = node_resp.json()
    assert node["node_type"] == "MEASUREMENT_REQUIRED"
    assert node["status"] == "PENDING"

    confirmation_resp = await auth_client.post(
        "/api/giraffe-jp/confirmation-requests",
        json={
            "service_node_id": node["id"],
            "target_party_type": "CUSTOMER",
            "confirmation_type": "MEASUREMENT_CONFIRMATION",
            "required_fields": {"fields": ["bust_cm", "waist_cm"]},
            "priority": "P0",
            "blocking_next_node": True,
        },
    )
    assert confirmation_resp.status_code == 201, confirmation_resp.text
    confirmation = confirmation_resp.json()
    assert confirmation["blocking_next_node"] is True
    assert confirmation["project_id"] == seed_project["id"]

    blocked_resp = await auth_client.patch(
        f"/api/giraffe-jp/service-nodes/{node['id']}",
        json={"status": "COMPLETED"},
    )
    assert blocked_resp.status_code == 409

    confirm_resp = await auth_client.post(
        f"/api/giraffe-jp/confirmation-requests/{confirmation['id']}/confirm",
        json={"response_payload": {"confirmed": True}},
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    assert confirm_resp.json()["status"] == "CONFIRMED"

    complete_node_resp = await auth_client.patch(
        f"/api/giraffe-jp/service-nodes/{node['id']}",
        json={"status": "COMPLETED"},
    )
    assert complete_node_resp.status_code == 200, complete_node_resp.text
    assert complete_node_resp.json()["completed_at"] is not None

    task_resp = await auth_client.post(
        "/api/giraffe-jp/customer-service/tasks",
        json={
            "confirmation_request_id": confirmation["id"],
            "task_type": "REVIEW_MEASUREMENT_CONFIRMATION",
            "priority": "P1",
        },
    )
    assert task_resp.status_code == 201, task_resp.text
    task = task_resp.json()
    assert task["status"] == "OPEN"
    assert task["project_id"] == seed_project["id"]

    start_resp = await auth_client.post(f"/api/giraffe-jp/customer-service/tasks/{task['id']}/start")
    assert start_resp.status_code == 200, start_resp.text
    assert start_resp.json()["status"] == "IN_PROGRESS"

    done_resp = await auth_client.post(f"/api/giraffe-jp/customer-service/tasks/{task['id']}/complete")
    assert done_resp.status_code == 200, done_resp.text
    assert done_resp.json()["status"] == "DONE"


async def test_service_nodes_are_tenant_isolated(auth_client, db):
    other_tenant = Tenant(name="Other Tenant", slug=f"other-{uuid.uuid4().hex[:8]}")
    db.add(other_tenant)
    await db.flush()
    other_node = GiraffeJPServiceNode(
        tenant_id=other_tenant.id,
        node_type="SUPPLIER_SEARCH_STARTED",
        status="PENDING",
        priority="P2",
    )
    db.add(other_node)
    await db.commit()

    list_resp = await auth_client.get("/api/giraffe-jp/service-nodes")
    assert list_resp.status_code == 200, list_resp.text
    ids = {item["id"] for item in list_resp.json()}
    assert str(other_node.id) not in ids

    detail_resp = await auth_client.get(f"/api/giraffe-jp/service-nodes/{other_node.id}")
    assert detail_resp.status_code == 404
