import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.giraffe_jp import (
    GiraffeJPConfirmationRequest,
    GiraffeJPCustomerServiceTask,
    GiraffeJPServiceNode,
)
from src.db.models.order import Order
from src.db.models.project import Project
from src.execution_graph.event_types import (
    CONFIRMATION_CONFIRMED,
    CONFIRMATION_ESCALATED,
    CONFIRMATION_REJECTED,
    CONFIRMATION_REQUEST_CREATED,
    CUSTOMER_SERVICE_TASK_COMPLETED,
    CUSTOMER_SERVICE_TASK_CREATED,
    CUSTOMER_SERVICE_TASK_ESCALATED,
    CUSTOMER_SERVICE_TASK_STARTED,
    SERVICE_NODE_CREATED,
    SERVICE_NODE_UPDATED,
)
from src.execution_graph.writer import emit_event
from src.giraffe_jp.schemas import (
    ConfirmationRequestCreate,
    CustomerServiceTaskCreate,
    ServiceNodeCreate,
    ServiceNodeUpdate,
)


async def _get_tenant_scoped(db: AsyncSession, model, resource_id: uuid.UUID, tenant_id: uuid.UUID):
    item = await db.get(model, resource_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Resource not found")
    return item


async def _validate_project_and_order_scope(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    project_id: uuid.UUID | None,
    order_id: uuid.UUID | None,
) -> tuple[uuid.UUID | None, uuid.UUID | None]:
    if project_id:
        project = await db.get(Project, project_id)
        if not project or project.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Project not found")

    if order_id:
        order = await db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        order_project = await db.get(Project, order.project_id)
        if not order_project or order_project.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Order not found")
        if project_id and order.project_id != project_id:
            raise HTTPException(status_code=409, detail="Order does not belong to project")
        project_id = order.project_id

    return project_id, order_id


async def create_service_node(
    db: AsyncSession,
    body: ServiceNodeCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPServiceNode:
    data = body.model_dump()
    data["project_id"], data["order_id"] = await _validate_project_and_order_scope(
        db,
        tenant_id,
        data["project_id"],
        data["order_id"],
    )
    node = GiraffeJPServiceNode(tenant_id=tenant_id, **data)
    db.add(node)
    await db.flush()
    await emit_event(
        db=db,
        event_type=SERVICE_NODE_CREATED,
        payload={"service_node_id": str(node.id), "node_type": node.node_type, "status": node.status},
        tenant_id=tenant_id,
        project_id=node.project_id,
        order_id=node.order_id,
        triggered_by_user_id=user_id,
    )
    return node


async def list_service_nodes(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    project_id: uuid.UUID | None = None,
    order_id: uuid.UUID | None = None,
    status: str | None = None,
) -> list[GiraffeJPServiceNode]:
    query = select(GiraffeJPServiceNode).where(GiraffeJPServiceNode.tenant_id == tenant_id)
    if project_id:
        query = query.where(GiraffeJPServiceNode.project_id == project_id)
    if order_id:
        query = query.where(GiraffeJPServiceNode.order_id == order_id)
    if status:
        query = query.where(GiraffeJPServiceNode.status == status)
    result = await db.execute(query.order_by(GiraffeJPServiceNode.created_at.desc()))
    return result.scalars().all()


async def get_service_node(
    db: AsyncSession,
    node_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> GiraffeJPServiceNode:
    return await _get_tenant_scoped(db, GiraffeJPServiceNode, node_id, tenant_id)


async def update_service_node(
    db: AsyncSession,
    node_id: uuid.UUID,
    body: ServiceNodeUpdate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPServiceNode:
    node = await get_service_node(db, node_id, tenant_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(node, field, value)
    if node.status == "COMPLETED" and node.completed_at is None:
        result = await db.execute(
            select(GiraffeJPConfirmationRequest).where(
                GiraffeJPConfirmationRequest.tenant_id == tenant_id,
                GiraffeJPConfirmationRequest.service_node_id == node_id,
                GiraffeJPConfirmationRequest.priority == "P0",
                GiraffeJPConfirmationRequest.blocking_next_node.is_(True),
                GiraffeJPConfirmationRequest.status != "CONFIRMED",
            )
        )
        blocking = result.scalars().first()
        if blocking:
            raise HTTPException(
                status_code=409,
                detail="P0 blocking confirmation must be confirmed before completing service node",
            )
        node.completed_at = datetime.now(timezone.utc)
    await db.flush()
    await emit_event(
        db=db,
        event_type=SERVICE_NODE_UPDATED,
        payload={"service_node_id": str(node.id), "node_type": node.node_type, "status": node.status},
        tenant_id=tenant_id,
        project_id=node.project_id,
        order_id=node.order_id,
        triggered_by_user_id=user_id,
    )
    return node


async def create_confirmation_request(
    db: AsyncSession,
    body: ConfirmationRequestCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPConfirmationRequest:
    node = await get_service_node(db, body.service_node_id, tenant_id)
    data = body.model_dump()
    data["project_id"] = data["project_id"] or node.project_id
    data["order_id"] = data["order_id"] or node.order_id
    data["project_id"], data["order_id"] = await _validate_project_and_order_scope(
        db,
        tenant_id,
        data["project_id"],
        data["order_id"],
    )
    if data["project_id"] != node.project_id or data["order_id"] != node.order_id:
        raise HTTPException(status_code=409, detail="Confirmation scope must match service node")
    confirmation = GiraffeJPConfirmationRequest(tenant_id=tenant_id, **data)
    db.add(confirmation)
    await db.flush()
    await emit_event(
        db=db,
        event_type=CONFIRMATION_REQUEST_CREATED,
        payload={
            "confirmation_request_id": str(confirmation.id),
            "service_node_id": str(confirmation.service_node_id),
            "confirmation_type": confirmation.confirmation_type,
            "blocking_next_node": confirmation.blocking_next_node,
        },
        tenant_id=tenant_id,
        project_id=confirmation.project_id,
        order_id=confirmation.order_id,
        triggered_by_user_id=user_id,
    )
    return confirmation


async def list_confirmation_requests(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    service_node_id: uuid.UUID | None = None,
    status: str | None = None,
) -> list[GiraffeJPConfirmationRequest]:
    query = select(GiraffeJPConfirmationRequest).where(GiraffeJPConfirmationRequest.tenant_id == tenant_id)
    if service_node_id:
        query = query.where(GiraffeJPConfirmationRequest.service_node_id == service_node_id)
    if status:
        query = query.where(GiraffeJPConfirmationRequest.status == status)
    result = await db.execute(query.order_by(GiraffeJPConfirmationRequest.created_at.desc()))
    return result.scalars().all()


async def get_confirmation_request(
    db: AsyncSession,
    confirmation_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> GiraffeJPConfirmationRequest:
    return await _get_tenant_scoped(db, GiraffeJPConfirmationRequest, confirmation_id, tenant_id)


async def _transition_confirmation(
    db: AsyncSession,
    confirmation_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    status: str,
    event_type: str,
    response_payload: dict | None = None,
) -> GiraffeJPConfirmationRequest:
    confirmation = await get_confirmation_request(db, confirmation_id, tenant_id)
    confirmation.status = status
    confirmation.response_payload = response_payload
    if status == "CONFIRMED":
        confirmation.confirmed_at = datetime.now(timezone.utc)
    await db.flush()
    await emit_event(
        db=db,
        event_type=event_type,
        payload={"confirmation_request_id": str(confirmation.id), "status": confirmation.status},
        tenant_id=tenant_id,
        project_id=confirmation.project_id,
        order_id=confirmation.order_id,
        triggered_by_user_id=user_id,
    )
    return confirmation


async def confirm_confirmation_request(
    db: AsyncSession,
    confirmation_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    response_payload: dict | None = None,
) -> GiraffeJPConfirmationRequest:
    return await _transition_confirmation(
        db, confirmation_id, tenant_id, user_id, "CONFIRMED", CONFIRMATION_CONFIRMED, response_payload
    )


async def reject_confirmation_request(
    db: AsyncSession,
    confirmation_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    response_payload: dict | None = None,
) -> GiraffeJPConfirmationRequest:
    return await _transition_confirmation(
        db, confirmation_id, tenant_id, user_id, "REJECTED", CONFIRMATION_REJECTED, response_payload
    )


async def escalate_confirmation_request(
    db: AsyncSession,
    confirmation_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    response_payload: dict | None = None,
) -> GiraffeJPConfirmationRequest:
    return await _transition_confirmation(
        db, confirmation_id, tenant_id, user_id, "ESCALATED", CONFIRMATION_ESCALATED, response_payload
    )


async def create_customer_service_task(
    db: AsyncSession,
    body: CustomerServiceTaskCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPCustomerServiceTask:
    data = body.model_dump()
    if body.service_node_id:
        node = await get_service_node(db, body.service_node_id, tenant_id)
        data["project_id"] = data["project_id"] or node.project_id
        data["order_id"] = data["order_id"] or node.order_id
    if body.confirmation_request_id:
        confirmation = await get_confirmation_request(db, body.confirmation_request_id, tenant_id)
        if data["service_node_id"] and data["service_node_id"] != confirmation.service_node_id:
            raise HTTPException(status_code=409, detail="Task service node must match confirmation request")
        data["service_node_id"] = data["service_node_id"] or confirmation.service_node_id
        data["project_id"] = data["project_id"] or confirmation.project_id
        data["order_id"] = data["order_id"] or confirmation.order_id
    data["project_id"], data["order_id"] = await _validate_project_and_order_scope(
        db,
        tenant_id,
        data["project_id"],
        data["order_id"],
    )
    task = GiraffeJPCustomerServiceTask(tenant_id=tenant_id, **data)
    db.add(task)
    await db.flush()
    await emit_event(
        db=db,
        event_type=CUSTOMER_SERVICE_TASK_CREATED,
        payload={"customer_service_task_id": str(task.id), "task_type": task.task_type, "status": task.status},
        tenant_id=tenant_id,
        project_id=task.project_id,
        order_id=task.order_id,
        triggered_by_user_id=user_id,
    )
    return task


async def list_customer_service_tasks(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    status: str | None = None,
) -> list[GiraffeJPCustomerServiceTask]:
    query = select(GiraffeJPCustomerServiceTask).where(GiraffeJPCustomerServiceTask.tenant_id == tenant_id)
    if status:
        query = query.where(GiraffeJPCustomerServiceTask.status == status)
    result = await db.execute(query.order_by(GiraffeJPCustomerServiceTask.created_at.desc()))
    return result.scalars().all()


async def _transition_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    status: str,
    event_type: str,
) -> GiraffeJPCustomerServiceTask:
    task = await _get_tenant_scoped(db, GiraffeJPCustomerServiceTask, task_id, tenant_id)
    task.status = status
    await db.flush()
    await emit_event(
        db=db,
        event_type=event_type,
        payload={"customer_service_task_id": str(task.id), "status": task.status},
        tenant_id=tenant_id,
        project_id=task.project_id,
        order_id=task.order_id,
        triggered_by_user_id=user_id,
    )
    return task


async def start_customer_service_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPCustomerServiceTask:
    return await _transition_task(db, task_id, tenant_id, user_id, "IN_PROGRESS", CUSTOMER_SERVICE_TASK_STARTED)


async def complete_customer_service_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPCustomerServiceTask:
    return await _transition_task(db, task_id, tenant_id, user_id, "DONE", CUSTOMER_SERVICE_TASK_COMPLETED)


async def escalate_customer_service_task(
    db: AsyncSession,
    task_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPCustomerServiceTask:
    return await _transition_task(db, task_id, tenant_id, user_id, "ESCALATED", CUSTOMER_SERVICE_TASK_ESCALATED)
