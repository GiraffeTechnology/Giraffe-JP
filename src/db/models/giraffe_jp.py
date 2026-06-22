import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base
from src.db.json_type import PortableJSON as JSONB


# ── Service Core ────────────────────────────────────────────────────────────────────────────────

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


# ── Iteration 02: Message Category Auto-Send Permissions ─────────────────────────────

class GiraffeJPMessageCategoryPermission(Base):
    __tablename__ = "giraffe_jp_message_category_permissions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "category_id", name="uq_gjp_tenant_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    category_id: Mapped[str] = mapped_column(String(128), nullable=False)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    party_type: Mapped[str] = mapped_column(String(64), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    auto_send: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ── Iteration 03: Web Dialog and Email Communication Layer ───────────────────────────

class GiraffeJPConversationThread(Base):
    __tablename__ = "giraffe_jp_conversation_threads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    party_type: Mapped[str] = mapped_column(String(64), nullable=False)
    party_ref_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    thread_type: Mapped[str] = mapped_column(String(64), nullable=False, default="GENERAL")
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GiraffeJPMessage(Base):
    __tablename__ = "giraffe_jp_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    thread_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("giraffe_jp_conversation_threads.id"), nullable=False)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sender_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GiraffeJPOutboundMessageDraft(Base):
    __tablename__ = "giraffe_jp_outbound_message_drafts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    thread_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("giraffe_jp_conversation_threads.id"), nullable=False)
    category_id: Mapped[str] = mapped_column(String(128), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING_HUMAN_CONFIRMATION")
    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GiraffeJPMessageDeliveryLog(Base):
    __tablename__ = "giraffe_jp_message_delivery_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    draft_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("giraffe_jp_outbound_message_drafts.id"), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(32), nullable=False, default="SIMULATED")
    delivery_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


# ── Iteration 04: Formalwear C2B2M Order Extension ───────────────────────────────────────

class GiraffeJPFormalwearOrderProfile(Base):
    __tablename__ = "giraffe_jp_formalwear_order_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    garment_category: Mapped[str] = mapped_column(String(64), nullable=False)
    hollow_to_hem_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    hollow_to_hem_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    model_try_on_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    local_alteration_possible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    custom_measurements: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GiraffeJPC2B2MRoleEdge(Base):
    __tablename__ = "giraffe_jp_c2b2m_role_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    role_from: Mapped[str] = mapped_column(String(64), nullable=False)
    role_to: Mapped[str] = mapped_column(String(64), nullable=False)
    edge_label: Mapped[str] = mapped_column(String(128), nullable=False)
    edge_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
