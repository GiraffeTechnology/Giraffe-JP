import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from src.giraffe_jp.formalwear import (
    create_c2b2m_role_edge,
    create_formalwear_order_profile,
    get_c2b2m_role_edge,
    get_formalwear_order_profile,
    initialize_default_c2b2m_edges_for_project,
    list_c2b2m_role_edges,
    list_formalwear_order_profiles,
    update_formalwear_order_profile,
)
from src.giraffe_jp.schemas import (
    C2B2MRoleEdgeCreate,
    C2B2MRoleEdgeOut,
    FormalwearOrderProfileCreate,
    FormalwearOrderProfileOut,
    FormalwearOrderProfileUpdate,
    InitializeDefaultEdgesBody,
)

router = APIRouter()


@router.post(
    "/formalwear/order-profiles",
    response_model=FormalwearOrderProfileOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_formalwear_order_profile_route(
    body: FormalwearOrderProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = await create_formalwear_order_profile(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/formalwear/order-profiles", response_model=list[FormalwearOrderProfileOut])
async def list_formalwear_order_profiles_route(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_formalwear_order_profiles(db, current_user.tenant_id)


@router.get("/formalwear/order-profiles/{profile_id}", response_model=FormalwearOrderProfileOut)
async def get_formalwear_order_profile_route(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_formalwear_order_profile(db, profile_id, current_user.tenant_id)


@router.patch("/formalwear/order-profiles/{profile_id}", response_model=FormalwearOrderProfileOut)
async def update_formalwear_order_profile_route(
    profile_id: uuid.UUID,
    body: FormalwearOrderProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = await update_formalwear_order_profile(
        db, profile_id, body, current_user.tenant_id, current_user.id
    )
    await db.commit()
    await db.refresh(profile)
    return profile


@router.post(
    "/c2b2m/role-edges",
    response_model=C2B2MRoleEdgeOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_c2b2m_role_edge_route(
    body: C2B2MRoleEdgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    edge = await create_c2b2m_role_edge(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(edge)
    return edge


@router.get("/c2b2m/role-edges", response_model=list[C2B2MRoleEdgeOut])
async def list_c2b2m_role_edges_route(
    project_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_c2b2m_role_edges(db, current_user.tenant_id, project_id)


@router.get("/c2b2m/role-edges/{edge_id}", response_model=C2B2MRoleEdgeOut)
async def get_c2b2m_role_edge_route(
    edge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_c2b2m_role_edge(db, edge_id, current_user.tenant_id)


@router.post(
    "/c2b2m/projects/{project_id}/initialize-default-edges",
    response_model=list[C2B2MRoleEdgeOut],
)
async def initialize_default_c2b2m_edges_route(
    project_id: uuid.UUID,
    body: InitializeDefaultEdgesBody,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    edges = await initialize_default_c2b2m_edges_for_project(
        db,
        tenant_id=current_user.tenant_id,
        project_id=project_id,
        order_id=body.order_id,
        customer_id=body.customer_id,
        supplier_id=body.supplier_id,
    )
    await db.commit()
    for e in edges:
        await db.refresh(e)
    return edges
