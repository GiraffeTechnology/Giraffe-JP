"""add_giraffe_jp_iter02_03_04

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Iteration 02: Message Category Auto-Send Permissions
    op.create_table(
        "giraffe_jp_message_category_permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.String(length=100), nullable=False),
        sa.Column("category_name", sa.String(length=200), nullable=False),
        sa.Column("direction", sa.String(length=50), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("auto_send", sa.Boolean(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("updated_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "category_id", name="uq_giraffe_jp_msg_cat_perm_tenant_category"),
    )
    op.create_index(op.f("ix_giraffe_jp_message_category_permissions_tenant_id"), "giraffe_jp_message_category_permissions", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_message_category_permissions_category_id"), "giraffe_jp_message_category_permissions", ["category_id"])
    op.create_index(op.f("ix_giraffe_jp_message_category_permissions_direction"), "giraffe_jp_message_category_permissions", ["direction"])
    op.create_index(op.f("ix_giraffe_jp_message_category_permissions_channel"), "giraffe_jp_message_category_permissions", ["channel"])
    op.create_index(op.f("ix_giraffe_jp_message_category_permissions_is_active"), "giraffe_jp_message_category_permissions", ["is_active"])

    # Iteration 03: Conversation Threads
    op.create_table(
        "giraffe_jp_conversation_threads",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("participant_id", sa.Uuid(), nullable=True),
        sa.Column("customer_id", sa.Uuid(), nullable=True),
        sa.Column("thread_type", sa.String(length=50), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_conversation_threads_tenant_id"), "giraffe_jp_conversation_threads", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_conversation_threads_project_id"), "giraffe_jp_conversation_threads", ["project_id"])
    op.create_index(op.f("ix_giraffe_jp_conversation_threads_order_id"), "giraffe_jp_conversation_threads", ["order_id"])
    op.create_index(op.f("ix_giraffe_jp_conversation_threads_participant_id"), "giraffe_jp_conversation_threads", ["participant_id"])
    op.create_index(op.f("ix_giraffe_jp_conversation_threads_thread_type"), "giraffe_jp_conversation_threads", ["thread_type"])
    op.create_index(op.f("ix_giraffe_jp_conversation_threads_status"), "giraffe_jp_conversation_threads", ["status"])

    # Iteration 03: Messages
    op.create_table(
        "giraffe_jp_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("sender_type", sa.String(length=50), nullable=False),
        sa.Column("sender_id", sa.Uuid(), nullable=True),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("message_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("category_id", sa.String(length=100), nullable=True),
        sa.Column("direction", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["giraffe_jp_conversation_threads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_messages_tenant_id"), "giraffe_jp_messages", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_messages_thread_id"), "giraffe_jp_messages", ["thread_id"])
    op.create_index(op.f("ix_giraffe_jp_messages_category_id"), "giraffe_jp_messages", ["category_id"])
    op.create_index(op.f("ix_giraffe_jp_messages_direction"), "giraffe_jp_messages", ["direction"])

    # Iteration 03: Outbound Message Drafts
    op.create_table(
        "giraffe_jp_outbound_message_drafts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column("service_node_id", sa.Uuid(), nullable=True),
        sa.Column("confirmation_request_id", sa.Uuid(), nullable=True),
        sa.Column("category_id", sa.String(length=100), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("auto_send_allowed", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.String(length=50), nullable=False),
        sa.Column("approved_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["confirmation_request_id"], ["giraffe_jp_confirmation_requests.id"]),
        sa.ForeignKeyConstraint(["service_node_id"], ["giraffe_jp_service_nodes.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["thread_id"], ["giraffe_jp_conversation_threads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_outbound_message_drafts_tenant_id"), "giraffe_jp_outbound_message_drafts", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_outbound_message_drafts_thread_id"), "giraffe_jp_outbound_message_drafts", ["thread_id"])
    op.create_index(op.f("ix_giraffe_jp_outbound_message_drafts_category_id"), "giraffe_jp_outbound_message_drafts", ["category_id"])
    op.create_index(op.f("ix_giraffe_jp_outbound_message_drafts_status"), "giraffe_jp_outbound_message_drafts", ["status"])

    # Iteration 03: Message Delivery Logs
    op.create_table(
        "giraffe_jp_message_delivery_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("draft_id", sa.Uuid(), nullable=True),
        sa.Column("message_id", sa.Uuid(), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("delivery_status", sa.String(length=50), nullable=False),
        sa.Column("provider_message_id", sa.String(length=200), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["draft_id"], ["giraffe_jp_outbound_message_drafts.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["giraffe_jp_messages.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_message_delivery_logs_tenant_id"), "giraffe_jp_message_delivery_logs", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_message_delivery_logs_draft_id"), "giraffe_jp_message_delivery_logs", ["draft_id"])
    op.create_index(op.f("ix_giraffe_jp_message_delivery_logs_delivery_status"), "giraffe_jp_message_delivery_logs", ["delivery_status"])

    # Iteration 04: Formalwear Order Profiles
    op.create_table(
        "giraffe_jp_formalwear_order_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("customer_id", sa.Uuid(), nullable=True),
        sa.Column("product_category", sa.String(length=50), nullable=False),
        sa.Column("occasion", sa.String(length=200), nullable=False),
        sa.Column("use_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("budget_min_jpy", sa.Numeric(precision=12, scale=0), nullable=True),
        sa.Column("budget_max_jpy", sa.Numeric(precision=12, scale=0), nullable=True),
        sa.Column("color_preference", sa.String(length=200), nullable=True),
        sa.Column("style_reference_notes", sa.String(length=1000), nullable=True),
        sa.Column("coverage_preference", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("fit_preference", sa.String(length=100), nullable=True),
        sa.Column("heel_height_cm", sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column("hollow_to_hem_required", sa.Boolean(), nullable=False),
        sa.Column("model_try_on_required", sa.Boolean(), nullable=False),
        sa.Column("local_alteration_possible", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_formalwear_order_profiles_tenant_id"), "giraffe_jp_formalwear_order_profiles", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_formalwear_order_profiles_project_id"), "giraffe_jp_formalwear_order_profiles", ["project_id"])
    op.create_index(op.f("ix_giraffe_jp_formalwear_order_profiles_order_id"), "giraffe_jp_formalwear_order_profiles", ["order_id"])
    op.create_index(op.f("ix_giraffe_jp_formalwear_order_profiles_product_category"), "giraffe_jp_formalwear_order_profiles", ["product_category"])
    op.create_index(op.f("ix_giraffe_jp_formalwear_order_profiles_status"), "giraffe_jp_formalwear_order_profiles", ["status"])

    # Iteration 04: C2B2M Role Edges
    op.create_table(
        "giraffe_jp_c2b2m_role_edges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("from_actor_type", sa.String(length=50), nullable=False),
        sa.Column("from_actor_id", sa.Uuid(), nullable=True),
        sa.Column("from_role", sa.String(length=50), nullable=False),
        sa.Column("to_actor_type", sa.String(length=50), nullable=False),
        sa.Column("to_actor_id", sa.Uuid(), nullable=True),
        sa.Column("to_role", sa.String(length=50), nullable=False),
        sa.Column("edge_type", sa.String(length=50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_c2b2m_role_edges_tenant_id"), "giraffe_jp_c2b2m_role_edges", ["tenant_id"])
    op.create_index(op.f("ix_giraffe_jp_c2b2m_role_edges_project_id"), "giraffe_jp_c2b2m_role_edges", ["project_id"])
    op.create_index(op.f("ix_giraffe_jp_c2b2m_role_edges_order_id"), "giraffe_jp_c2b2m_role_edges", ["order_id"])
    op.create_index(op.f("ix_giraffe_jp_c2b2m_role_edges_from_actor_type"), "giraffe_jp_c2b2m_role_edges", ["from_actor_type"])
    op.create_index(op.f("ix_giraffe_jp_c2b2m_role_edges_to_actor_type"), "giraffe_jp_c2b2m_role_edges", ["to_actor_type"])
    op.create_index(op.f("ix_giraffe_jp_c2b2m_role_edges_edge_type"), "giraffe_jp_c2b2m_role_edges", ["edge_type"])


def downgrade() -> None:
    op.drop_index(op.f("ix_giraffe_jp_c2b2m_role_edges_edge_type"), table_name="giraffe_jp_c2b2m_role_edges")
    op.drop_index(op.f("ix_giraffe_jp_c2b2m_role_edges_to_actor_type"), table_name="giraffe_jp_c2b2m_role_edges")
    op.drop_index(op.f("ix_giraffe_jp_c2b2m_role_edges_from_actor_type"), table_name="giraffe_jp_c2b2m_role_edges")
    op.drop_index(op.f("ix_giraffe_jp_c2b2m_role_edges_order_id"), table_name="giraffe_jp_c2b2m_role_edges")
    op.drop_index(op.f("ix_giraffe_jp_c2b2m_role_edges_project_id"), table_name="giraffe_jp_c2b2m_role_edges")
    op.drop_index(op.f("ix_giraffe_jp_c2b2m_role_edges_tenant_id"), table_name="giraffe_jp_c2b2m_role_edges")
    op.drop_table("giraffe_jp_c2b2m_role_edges")

    op.drop_index(op.f("ix_giraffe_jp_formalwear_order_profiles_status"), table_name="giraffe_jp_formalwear_order_profiles")
    op.drop_index(op.f("ix_giraffe_jp_formalwear_order_profiles_product_category"), table_name="giraffe_jp_formalwear_order_profiles")
    op.drop_index(op.f("ix_giraffe_jp_formalwear_order_profiles_order_id"), table_name="giraffe_jp_formalwear_order_profiles")
    op.drop_index(op.f("ix_giraffe_jp_formalwear_order_profiles_project_id"), table_name="giraffe_jp_formalwear_order_profiles")
    op.drop_index(op.f("ix_giraffe_jp_formalwear_order_profiles_tenant_id"), table_name="giraffe_jp_formalwear_order_profiles")
    op.drop_table("giraffe_jp_formalwear_order_profiles")

    op.drop_index(op.f("ix_giraffe_jp_message_delivery_logs_delivery_status"), table_name="giraffe_jp_message_delivery_logs")
    op.drop_index(op.f("ix_giraffe_jp_message_delivery_logs_draft_id"), table_name="giraffe_jp_message_delivery_logs")
    op.drop_index(op.f("ix_giraffe_jp_message_delivery_logs_tenant_id"), table_name="giraffe_jp_message_delivery_logs")
    op.drop_table("giraffe_jp_message_delivery_logs")

    op.drop_index(op.f("ix_giraffe_jp_outbound_message_drafts_status"), table_name="giraffe_jp_outbound_message_drafts")
    op.drop_index(op.f("ix_giraffe_jp_outbound_message_drafts_category_id"), table_name="giraffe_jp_outbound_message_drafts")
    op.drop_index(op.f("ix_giraffe_jp_outbound_message_drafts_thread_id"), table_name="giraffe_jp_outbound_message_drafts")
    op.drop_index(op.f("ix_giraffe_jp_outbound_message_drafts_tenant_id"), table_name="giraffe_jp_outbound_message_drafts")
    op.drop_table("giraffe_jp_outbound_message_drafts")

    op.drop_index(op.f("ix_giraffe_jp_messages_direction"), table_name="giraffe_jp_messages")
    op.drop_index(op.f("ix_giraffe_jp_messages_category_id"), table_name="giraffe_jp_messages")
    op.drop_index(op.f("ix_giraffe_jp_messages_thread_id"), table_name="giraffe_jp_messages")
    op.drop_index(op.f("ix_giraffe_jp_messages_tenant_id"), table_name="giraffe_jp_messages")
    op.drop_table("giraffe_jp_messages")

    op.drop_index(op.f("ix_giraffe_jp_conversation_threads_status"), table_name="giraffe_jp_conversation_threads")
    op.drop_index(op.f("ix_giraffe_jp_conversation_threads_thread_type"), table_name="giraffe_jp_conversation_threads")
    op.drop_index(op.f("ix_giraffe_jp_conversation_threads_participant_id"), table_name="giraffe_jp_conversation_threads")
    op.drop_index(op.f("ix_giraffe_jp_conversation_threads_order_id"), table_name="giraffe_jp_conversation_threads")
    op.drop_index(op.f("ix_giraffe_jp_conversation_threads_project_id"), table_name="giraffe_jp_conversation_threads")
    op.drop_index(op.f("ix_giraffe_jp_conversation_threads_tenant_id"), table_name="giraffe_jp_conversation_threads")
    op.drop_table("giraffe_jp_conversation_threads")

    op.drop_index(op.f("ix_giraffe_jp_message_category_permissions_is_active"), table_name="giraffe_jp_message_category_permissions")
    op.drop_index(op.f("ix_giraffe_jp_message_category_permissions_channel"), table_name="giraffe_jp_message_category_permissions")
    op.drop_index(op.f("ix_giraffe_jp_message_category_permissions_direction"), table_name="giraffe_jp_message_category_permissions")
    op.drop_index(op.f("ix_giraffe_jp_message_category_permissions_category_id"), table_name="giraffe_jp_message_category_permissions")
    op.drop_index(op.f("ix_giraffe_jp_message_category_permissions_tenant_id"), table_name="giraffe_jp_message_category_permissions")
    op.drop_table("giraffe_jp_message_category_permissions")
