from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from src.giraffe_jp.message_permissions import (
    get_category_permission,
    list_category_permissions,
    seed_default_categories,
    update_category_permission,
)
from src.giraffe_jp.schemas import (
    MessageCategoryPermissionOut,
    MessageCategoryPermissionUpdate,
)

router = APIRouter()


@router.get(
    "/message-category-permissions",
    response_model=list[MessageCategoryPermissionOut],
)
async def list_message_category_permissions_route(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_category_permissions(db, current_user.tenant_id)


@router.get(
    "/message-category-permissions/{category_id}",
    response_model=MessageCategoryPermissionOut,
)
async def get_message_category_permission_route(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_category_permission(db, current_user.tenant_id, category_id)


@router.patch(
    "/message-category-permissions/{category_id}",
    response_model=MessageCategoryPermissionOut,
)
async def update_message_category_permission_route(
    category_id: str,
    body: MessageCategoryPermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    perm = await update_category_permission(
        db, current_user.tenant_id, category_id, body, current_user.id
    )
    await db.commit()
    await db.refresh(perm)
    return perm


@router.post(
    "/message-category-permissions/seed-defaults",
    response_model=list[MessageCategoryPermissionOut],
    status_code=status.HTTP_200_OK,
)
async def seed_default_message_category_permissions_route(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    perms = await seed_default_categories(db, current_user.tenant_id, current_user.id)
    await db.commit()
    for p in perms:
        await db.refresh(p)
    return perms
