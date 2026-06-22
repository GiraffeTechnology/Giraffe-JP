import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


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


# ── Iteration 02: Message Category Permissions ────────────────────────────────

class MessageCategoryPermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    category_id: str
    category_name: str
    direction: str
    channel: str
    auto_send: bool
    description: Optional[str]
    is_active: bool
    updated_by_user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class MessageCategoryPermissionUpdate(BaseModel):
    auto_send: Optional[bool] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


# ── Iteration 03: Conversations & Outbound Drafts ─────────────────────────────

class ConversationThreadCreate(BaseModel):
    project_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    participant_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    thread_type: str
    channel: str


class ConversationThreadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: Optional[uuid.UUID]
    order_id: Optional[uuid.UUID]
    participant_id: Optional[uuid.UUID]
    customer_id: Optional[uuid.UUID]
    thread_type: str
    channel: str
    status: str
    created_at: datetime
    updated_at: datetime


class InboundMessageCreate(BaseModel):
    sender_type: str
    sender_id: Optional[uuid.UUID] = None
    message_text: str
    message_payload: Optional[dict] = None
    category_id: Optional[str] = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    thread_id: uuid.UUID
    sender_type: str
    sender_id: Optional[uuid.UUID]
    message_text: str
    message_payload: Optional[dict]
    category_id: Optional[str]
    direction: str
    created_at: datetime


class OutboundMessageDraftCreate(BaseModel):
    thread_id: uuid.UUID
    service_node_id: Optional[uuid.UUID] = None
    confirmation_request_id: Optional[uuid.UUID] = None
    category_id: str
    message_text: str
    channel: str
    created_by: str = "SYSTEM"


class OutboundMessageDraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    thread_id: uuid.UUID
    service_node_id: Optional[uuid.UUID]
    confirmation_request_id: Optional[uuid.UUID]
    category_id: str
    message_text: str
    channel: str
    auto_send_allowed: bool
    status: str
    created_by: str
    approved_by_user_id: Optional[uuid.UUID]
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# ── Iteration 04: Formalwear Order Profiles & C2B2M Role Edges ───────────────

VALID_PRODUCT_CATEGORIES = {
    "FORMAL_DRESS",
    "WOMENS_SUIT",
    "BRIDALWEAR",
    "LIGHT_WEDDING_DRESS",
    "RECEPTION_DRESS",
}

HOLLOW_TO_HEM_CATEGORIES = {"FORMAL_DRESS", "BRIDALWEAR", "LIGHT_WEDDING_DRESS"}


class FormalwearOrderProfileCreate(BaseModel):
    project_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    product_category: str
    occasion: str
    use_date: Optional[datetime] = None
    budget_min_jpy: Optional[Decimal] = None
    budget_max_jpy: Optional[Decimal] = None
    color_preference: Optional[str] = None
    style_reference_notes: Optional[str] = None
    coverage_preference: Optional[dict] = None
    fit_preference: Optional[str] = None
    heel_height_cm: Optional[Decimal] = None
    hollow_to_hem_required: Optional[bool] = None
    model_try_on_required: bool = True
    local_alteration_possible: bool = True

    @field_validator("product_category")
    @classmethod
    def validate_product_category(cls, v: str) -> str:
        if v not in VALID_PRODUCT_CATEGORIES:
            raise ValueError(f"product_category must be one of {sorted(VALID_PRODUCT_CATEGORIES)}")
        return v


class FormalwearOrderProfileUpdate(BaseModel):
    order_id: Optional[uuid.UUID] = None
    occasion: Optional[str] = None
    use_date: Optional[datetime] = None
    budget_min_jpy: Optional[Decimal] = None
    budget_max_jpy: Optional[Decimal] = None
    color_preference: Optional[str] = None
    style_reference_notes: Optional[str] = None
    coverage_preference: Optional[dict] = None
    fit_preference: Optional[str] = None
    heel_height_cm: Optional[Decimal] = None
    hollow_to_hem_required: Optional[bool] = None
    model_try_on_required: Optional[bool] = None
    local_alteration_possible: Optional[bool] = None
    status: Optional[str] = None


class FormalwearOrderProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID
    order_id: Optional[uuid.UUID]
    customer_id: Optional[uuid.UUID]
    product_category: str
    occasion: str
    use_date: Optional[datetime]
    budget_min_jpy: Optional[Decimal]
    budget_max_jpy: Optional[Decimal]
    color_preference: Optional[str]
    style_reference_notes: Optional[str]
    coverage_preference: Optional[dict]
    fit_preference: Optional[str]
    heel_height_cm: Optional[Decimal]
    hollow_to_hem_required: bool
    model_try_on_required: bool
    local_alteration_possible: bool
    status: str
    created_at: datetime
    updated_at: datetime


class C2B2MRoleEdgeCreate(BaseModel):
    project_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    from_actor_type: str
    from_actor_id: Optional[uuid.UUID] = None
    from_role: str
    to_actor_type: str
    to_actor_id: Optional[uuid.UUID] = None
    to_role: str
    edge_type: str
    payload: Optional[dict] = None


class C2B2MRoleEdgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID
    order_id: Optional[uuid.UUID]
    from_actor_type: str
    from_actor_id: Optional[uuid.UUID]
    from_role: str
    to_actor_type: str
    to_actor_id: Optional[uuid.UUID]
    to_role: str
    edge_type: str
    payload: Optional[dict]
    created_at: datetime


class InitializeDefaultEdgesBody(BaseModel):
    order_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    supplier_id: Optional[uuid.UUID] = None
