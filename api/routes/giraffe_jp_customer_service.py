import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from src.giraffe_jp.schemas import CustomerServiceTaskCreate, CustomerServiceTaskOut
from src.giraffe_jp.service import (
    complete_customer_service_task,
    create_customer_service_task,
    escalate_customer_service_task,
    list_customer_service_tasks,
    start_customer_service_task,
)

router = APIRouter()


@router.get("/customer-service/tasks", response_model=list[CustomerServiceTaskOut])
async def list_customer_service_tasks_route(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_customer_service_tasks(db, current_user.tenant_id, status)


@router.post("/customer-service/tasks", status_code=status.HTTP_201_CREATED, response_model=CustomerServiceTaskOut)
async def create_customer_service_task_route(
    body: CustomerServiceTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = await create_customer_service_task(db, body, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/customer-service/tasks/{task_id}/start", response_model=CustomerServiceTaskOut)
async def start_customer_service_task_route(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = await start_customer_service_task(db, task_id, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/customer-service/tasks/{task_id}/complete", response_model=CustomerServiceTaskOut)
async def complete_customer_service_task_route(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = await complete_customer_service_task(db, task_id, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/customer-service/tasks/{task_id}/escalate", response_model=CustomerServiceTaskOut)
async def escalate_customer_service_task_route(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = await escalate_customer_service_task(db, task_id, current_user.tenant_id, current_user.id)
    await db.commit()
    await db.refresh(task)
    return task
