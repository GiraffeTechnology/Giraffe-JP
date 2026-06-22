import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.db.json_type import PortableJSON as JSONB


class GiraffeJPServiceNode(Base):
    __tablename__ = "giraffe_jp_service_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    node_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(10), default="P2", nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class GiraffeJPConfirmationRequest(Base):
    __tablename__ = "giraffe_jp_confirmation_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    service_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("giraffe_jp_service_nodes.id"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    target_party_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_party_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    confirmation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    required_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    priority: Mapped[str] = mapped_column(String(10), default="P2", nullable=False)
    blocking_next_node: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="WEB_DIALOG", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class GiraffeJPMessageCategoryPermission(Base):
    __tablename__ = "giraffe_jp_message_category_permissions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "category_id", name="uq_giraffe_jp_msg_cat_perm_tenant_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    category_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, default="ANY", index=True)
    auto_send: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class GiraffeJPConversationThread(Base):
    __tablename__ = "giraffe_jp_conversation_threads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    participant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("participants.id"), nullable=True, index=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    thread_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class GiraffeJPMessage(Base):
    __tablename__ = "giraffe_jp_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("giraffe_jp_conversation_threads.id"), nullable=False, index=True
    )
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    message_text: Mapped[str] = mapped_column(String, nullable=False)
    message_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    direction: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GiraffeJPOutboundMessageDraft(Base):
    __tablename__ = "giraffe_jp_outbound_message_drafts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("giraffe_jp_conversation_threads.id"), nullable=False, index=True
    )
    service_node_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("giraffe_jp_service_nodes.id"), nullable=True
    )
    confirmation_request_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("giraffe_jp_confirmation_requests.id"), nullable=True
    )
    category_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message_text: Mapped[str] = mapped_column(String, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    auto_send_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False, default="SYSTEM")
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class GiraffeJPMessageDeliveryLog(Base):
    __tablename__ = "giraffe_jp_message_delivery_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    draft_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("giraffe_jp_outbound_message_drafts.id"), nullable=True, index=True
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("giraffe_jp_messages.id"), nullable=True
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GiraffeJPFormalwearOrderProfile(Base):
    __tablename__ = "giraffe_jp_formalwear_order_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    product_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    occasion: Mapped[str] = mapped_column(String(200), nullable=False)
    use_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    budget_min_jpy: Mapped[Decimal | None] = mapped_column(Numeric(12, 0), nullable=True)
    budget_max_jpy: Mapped[Decimal | None] = mapped_column(Numeric(12, 0), nullable=True)
    color_preference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    style_reference_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    coverage_preference: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    fit_preference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    heel_height_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 1), nullable=True)
    hollow_to_hem_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    model_try_on_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    local_alteration_possible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class GiraffeJPC2B2MRoleEdge(Base):
    __tablename__ = "giraffe_jp_c2b2m_role_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    from_actor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    from_actor_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    from_role: Mapped[str] = mapped_column(String(50), nullable=False)
    to_actor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    to_actor_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    to_role: Mapped[str] = mapped_column(String(50), nullable=False)
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GiraffeJPCustomerServiceTask(Base):
    __tablename__ = "giraffe_jp_customer_service_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    service_node_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("giraffe_jp_service_nodes.id"),
        nullable=True,
        index=True,
    )
    confirmation_request_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("giraffe_jp_confirmation_requests.id"),
        nullable=True,
        index=True,
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String(10), default="P2", nullable=False)
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False, index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
