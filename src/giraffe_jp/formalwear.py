import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.giraffe_jp import (
    GiraffeJPFormalwearOrderProfile,
    GiraffeJPC2B2MRoleEdge,
)
from src.db.models.project import Project
from src.execution_graph.event_types import (
    C2B2M_DEFAULT_EDGES_INITIALIZED,
    C2B2M_ROLE_EDGE_CREATED,
    FORMALWEAR_ORDER_PROFILE_CREATED,
    FORMALWEAR_ORDER_PROFILE_UPDATED,
)
from src.execution_graph.writer import emit_event
from src.giraffe_jp.schemas import (
    C2B2MRoleEdgeCreate,
    FormalwearOrderProfileCreate,
    FormalwearOrderProfileUpdate,
    HOLLOW_TO_HEM_CATEGORIES,
)


async def _validate_project_tenant(
    db: AsyncSession,
    project_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Project:
    project = await db.get(Project, project_id)
    if not project or project.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def create_formalwear_order_profile(
    db: AsyncSession,
    body: FormalwearOrderProfileCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPFormalwearOrderProfile:
    await _validate_project_tenant(db, body.project_id, tenant_id)

    data = body.model_dump()

    # Apply hollow_to_hem_required default for dress/bridalwear categories
    if data.get("product_category") in HOLLOW_TO_HEM_CATEGORIES:
        if data.get("hollow_to_hem_required") is None:
            data["hollow_to_hem_required"] = True
    if data.get("hollow_to_hem_required") is None:
        data["hollow_to_hem_required"] = False

    profile = GiraffeJPFormalwearOrderProfile(tenant_id=tenant_id, **data)
    db.add(profile)
    await db.flush()
    await emit_event(
        db=db,
        event_type=FORMALWEAR_ORDER_PROFILE_CREATED,
        payload={
            "profile_id": str(profile.id),
            "product_category": profile.product_category,
            "project_id": str(profile.project_id),
        },
        tenant_id=tenant_id,
        project_id=profile.project_id,
        order_id=profile.order_id,
        triggered_by_user_id=user_id,
    )
    return profile


async def list_formalwear_order_profiles(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[GiraffeJPFormalwearOrderProfile]:
    result = await db.execute(
        select(GiraffeJPFormalwearOrderProfile)
        .where(GiraffeJPFormalwearOrderProfile.tenant_id == tenant_id)
        .order_by(GiraffeJPFormalwearOrderProfile.created_at.desc())
    )
    return result.scalars().all()


async def get_formalwear_order_profile(
    db: AsyncSession,
    profile_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> GiraffeJPFormalwearOrderProfile:
    profile = await db.get(GiraffeJPFormalwearOrderProfile, profile_id)
    if not profile or profile.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Formalwear order profile not found")
    return profile


async def update_formalwear_order_profile(
    db: AsyncSession,
    profile_id: uuid.UUID,
    body: FormalwearOrderProfileUpdate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPFormalwearOrderProfile:
    profile = await get_formalwear_order_profile(db, profile_id, tenant_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.flush()
    await emit_event(
        db=db,
        event_type=FORMALWEAR_ORDER_PROFILE_UPDATED,
        payload={"profile_id": str(profile.id), "status": profile.status},
        tenant_id=tenant_id,
        project_id=profile.project_id,
        order_id=profile.order_id,
        triggered_by_user_id=user_id,
    )
    return profile


async def create_c2b2m_role_edge(
    db: AsyncSession,
    body: C2B2MRoleEdgeCreate,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> GiraffeJPC2B2MRoleEdge:
    await _validate_project_tenant(db, body.project_id, tenant_id)
    data = body.model_dump()
    edge = GiraffeJPC2B2MRoleEdge(tenant_id=tenant_id, **data)
    db.add(edge)
    await db.flush()
    await emit_event(
        db=db,
        event_type=C2B2M_ROLE_EDGE_CREATED,
        payload={
            "edge_id": str(edge.id),
            "from_actor_type": edge.from_actor_type,
            "to_actor_type": edge.to_actor_type,
            "edge_type": edge.edge_type,
        },
        tenant_id=tenant_id,
        project_id=edge.project_id,
        order_id=edge.order_id,
        triggered_by_user_id=user_id,
    )
    return edge


async def list_c2b2m_role_edges(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    project_id: uuid.UUID | None = None,
) -> list[GiraffeJPC2B2MRoleEdge]:
    query = select(GiraffeJPC2B2MRoleEdge).where(GiraffeJPC2B2MRoleEdge.tenant_id == tenant_id)
    if project_id:
        query = query.where(GiraffeJPC2B2MRoleEdge.project_id == project_id)
    result = await db.execute(query.order_by(GiraffeJPC2B2MRoleEdge.created_at))
    return result.scalars().all()


async def get_c2b2m_role_edge(
    db: AsyncSession,
    edge_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> GiraffeJPC2B2MRoleEdge:
    edge = await db.get(GiraffeJPC2B2MRoleEdge, edge_id)
    if not edge or edge.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="C2B2M role edge not found")
    return edge


async def _edge_exists(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    project_id: uuid.UUID,
    from_actor_type: str,
    to_actor_type: str,
    to_actor_id: uuid.UUID | None,
    edge_type: str,
) -> bool:
    query = select(GiraffeJPC2B2MRoleEdge).where(
        GiraffeJPC2B2MRoleEdge.tenant_id == tenant_id,
        GiraffeJPC2B2MRoleEdge.project_id == project_id,
        GiraffeJPC2B2MRoleEdge.from_actor_type == from_actor_type,
        GiraffeJPC2B2MRoleEdge.to_actor_type == to_actor_type,
        GiraffeJPC2B2MRoleEdge.edge_type == edge_type,
    )
    if to_actor_id is not None:
        query = query.where(GiraffeJPC2B2MRoleEdge.to_actor_id == to_actor_id)
    result = await db.execute(query)
    return result.scalars().first() is not None


async def initialize_default_c2b2m_edges_for_project(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    project_id: uuid.UUID,
    order_id: uuid.UUID | None = None,
    customer_id: uuid.UUID | None = None,
    supplier_id: uuid.UUID | None = None,
) -> list[GiraffeJPC2B2MRoleEdge]:
    await _validate_project_tenant(db, project_id, tenant_id)
    created = []

    if not await _edge_exists(db, tenant_id, project_id, "JP_CUSTOMER", "GIRAFFE_JP", None, "DEFAULT"):
        edge = GiraffeJPC2B2MRoleEdge(
            tenant_id=tenant_id,
            project_id=project_id,
            order_id=order_id,
            from_actor_type="JP_CUSTOMER",
            from_actor_id=customer_id,
            from_role="B_SIDE",
            to_actor_type="GIRAFFE_JP",
            to_actor_id=None,
            to_role="MAIN_M_SIDE",
            edge_type="DEFAULT",
        )
        db.add(edge)
        await db.flush()
        created.append(edge)

    if supplier_id and not await _edge_exists(
        db, tenant_id, project_id, "GIRAFFE_JP", "SUPPLIER", supplier_id, "DEFAULT"
    ):
        edge = GiraffeJPC2B2MRoleEdge(
            tenant_id=tenant_id,
            project_id=project_id,
            order_id=order_id,
            from_actor_type="GIRAFFE_JP",
            from_actor_id=None,
            from_role="UPSTREAM_B_SIDE",
            to_actor_type="SUPPLIER",
            to_actor_id=supplier_id,
            to_role="UPSTREAM_M_SIDE",
            edge_type="DEFAULT",
        )
        db.add(edge)
        await db.flush()
        created.append(edge)

    await emit_event(
        db=db,
        event_type=C2B2M_DEFAULT_EDGES_INITIALIZED,
        payload={
            "project_id": str(project_id),
            "edges_created": len(created),
            "supplier_included": supplier_id is not None,
        },
        tenant_id=tenant_id,
        project_id=project_id,
        order_id=order_id,
    )
    return created
