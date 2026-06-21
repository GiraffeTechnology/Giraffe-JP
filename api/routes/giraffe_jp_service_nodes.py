import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from src.giraffe_jp.schemas import ServiceNodeCreate, ServiceNodeOut, ServiceNodeUpdate
from src.giraffe_jp.service import (
    create_service_node,
    get_service_node,
    list_service_nodes,
    update_service_node,
)

router = APIRouter()


@router.post("/service-nodes", status_code=status.HTTP_201_CREATED, response_model=ServiceNodeOut)
async def create_service_node_route(
    body: ServiceNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    node = await create_service_node(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(node)
    return node


@router.get("/service-nodes", response_model=list[ServiceNodeOut])
async def list_service_nodes_route(
    project_id: Optional[uuid.UUID] = None,
    order_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_service_nodes(db, current_user.tenant_id, project_id, order_id, status)


@router.get("/service-nodes/{node_id}", response_model=ServiceNodeOut)
async def get_service_node_route(
    node_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_service_node(db, node_id, current_user.tenant_id)


@router.patch("/service-nodes/{node_id}", response_model=ServiceNodeOut)
async def update_service_node_route(
    node_id: uuid.UUID,
    body: ServiceNodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    node = await update_service_node(db, node_id, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(node)
    return node
