import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServiceNodeCreate(BaseModel):
    project_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    node_type: str
    status: str = "PENDING"
    priority: str = "P2"
    scheduled_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    payload: Optional[dict] = None


class ServiceNodeUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    payload: Optional[dict] = None


class ServiceNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: Optional[uuid.UUID]
    order_id: Optional[uuid.UUID]
    node_type: str
    status: str
    priority: str
    scheduled_at: Optional[datetime]
    due_at: Optional[datetime]
    completed_at: Optional[datetime]
    payload: Optional[dict]
    created_at: datetime
    updated_at: datetime


class ConfirmationRequestCreate(BaseModel):
    service_node_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    target_party_type: str
    target_party_id: Optional[uuid.UUID] = None
    confirmation_type: str
    required_fields: Optional[dict] = None
    priority: str = "P2"
    blocking_next_node: bool = False
    channel: str = "WEB_DIALOG"
    due_at: Optional[datetime] = None


class ConfirmationResponseBody(BaseModel):
    response_payload: Optional[dict] = None


class ConfirmationRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    service_node_id: uuid.UUID
    project_id: Optional[uuid.UUID]
    order_id: Optional[uuid.UUID]
    target_party_type: str
    target_party_id: Optional[uuid.UUID]
    confirmation_type: str
    required_fields: Optional[dict]
    priority: str
    blocking_next_node: bool
    channel: str
    status: str
    due_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    response_payload: Optional[dict]
    created_at: datetime
    updated_at: datetime


class CustomerServiceTaskCreate(BaseModel):
    service_node_id: Optional[uuid.UUID] = None
    confirmation_request_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    task_type: str
    priority: str = "P2"
    assigned_to_user_id: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None
    payload: Optional[dict] = None


class CustomerServiceTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    service_node_id: Optional[uuid.UUID]
    confirmation_request_id: Optional[uuid.UUID]
    order_id: Optional[uuid.UUID]
    project_id: Optional[uuid.UUID]
    task_type: str
    priority: str
    assigned_to_user_id: Optional[uuid.UUID]
    status: str
    due_at: Optional[datetime]
    payload: Optional[dict]
    created_at: datetime
    updated_at: datetime
