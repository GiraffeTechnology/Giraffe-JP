import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── Service Core ────────────────────────────────────────────────────────────────────────────────

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


# ── Iteration 02: Message Category Auto-Send Permissions ─────────────────────────────

class MessageCategoryPermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    category_id: str
    category_name: str
    party_type: str
    channel: str | None
    auto_send: bool
    created_at: datetime
    updated_at: datetime


class MessageCategoryPermissionUpdate(BaseModel):
    auto_send: bool


# ── Iteration 03: Web Dialog and Email Communication Layer ───────────────────────────

class ConversationThreadCreate(BaseModel):
    party_type: str
    project_id: uuid.UUID | None = None
    party_ref_id: str | None = None
    thread_type: str = "GENERAL"
    subject: str | None = None


class ConversationThreadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID | None
    party_type: str
    party_ref_id: str | None
    thread_type: str
    subject: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class InboundMessageCreate(BaseModel):
    body: str
    sender_ref: str | None = None
    message_metadata: dict | None = None


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    thread_id: uuid.UUID
    direction: str
    body: str
    sender_ref: str | None
    message_metadata: dict | None
    created_at: datetime


class OutboundDraftCreate(BaseModel):
    category_id: str
    body: str


class OutboundDraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    thread_id: uuid.UUID
    category_id: str
    body: str
    approval_status: str
    reviewed_by_user_id: uuid.UUID | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


# ── Iteration 04: Formalwear C2B2M Order Extension ───────────────────────────────────────

class FormalwearProfileCreate(BaseModel):
    garment_category: str
    hollow_to_hem_cm: float | None = None
    model_try_on_required: bool = True
    local_alteration_possible: bool = True
    custom_measurements: dict | None = None


class FormalwearProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID
    garment_category: str
    hollow_to_hem_cm: float | None
    hollow_to_hem_required: bool
    model_try_on_required: bool
    local_alteration_possible: bool
    custom_measurements: dict | None
    created_at: datetime
    updated_at: datetime


class FormalwearProfileUpdate(BaseModel):
    hollow_to_hem_cm: float | None = None
    model_try_on_required: bool | None = None
    local_alteration_possible: bool | None = None
    custom_measurements: dict | None = None


class C2B2MEdgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID
    role_from: str
    role_to: str
    edge_label: str
    edge_metadata: dict | None
    created_at: datetime
