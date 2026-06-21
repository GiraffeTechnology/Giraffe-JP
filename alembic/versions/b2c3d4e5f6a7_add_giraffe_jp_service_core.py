"""add_giraffe_jp_service_core

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-22 02:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "giraffe_jp_service_nodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("node_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_giraffe_jp_service_nodes_due_at"), "giraffe_jp_service_nodes", ["due_at"])
    op.create_index(op.f("ix_giraffe_jp_service_nodes_node_type"), "giraffe_jp_service_nodes", ["node_type"])
    op.create_index(op.f("ix_giraffe_jp_service_nodes_order_id"), "giraffe_jp_service_nodes", ["order_id"])
    op.create_index(op.f("ix_giraffe_jp_service_nodes_project_id"), "giraffe_jp_service_nodes", ["project_id"])
    op.create_index(op.f("ix_giraffe_jp_service_nodes_status"), "giraffe_jp_service_nodes", ["status"])
    op.create_index(op.f("ix_giraffe_jp_service_nodes_tenant_id"), "giraffe_jp_service_nodes", ["tenant_id"])

    op.create_table(
        "giraffe_jp_confirmation_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("service_node_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("target_party_type", sa.String(length=50), nullable=False),
        sa.Column("target_party_id", sa.Uuid(), nullable=True),
        sa.Column("confirmation_type", sa.String(length=100), nullable=False),
        sa.Column("required_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("blocking_next_node", sa.Boolean(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["service_node_id"], ["giraffe_jp_service_nodes.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_giraffe_jp_confirmation_requests_due_at"),
        "giraffe_jp_confirmation_requests",
        ["due_at"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_confirmation_requests_order_id"),
        "giraffe_jp_confirmation_requests",
        ["order_id"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_confirmation_requests_project_id"),
        "giraffe_jp_confirmation_requests",
        ["project_id"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_confirmation_requests_service_node_id"),
        "giraffe_jp_confirmation_requests",
        ["service_node_id"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_confirmation_requests_status"),
        "giraffe_jp_confirmation_requests",
        ["status"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_confirmation_requests_tenant_id"),
        "giraffe_jp_confirmation_requests",
        ["tenant_id"],
    )

    op.create_table(
        "giraffe_jp_customer_service_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("service_node_id", sa.Uuid(), nullable=True),
        sa.Column("confirmation_request_id", sa.Uuid(), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("task_type", sa.String(length=100), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("assigned_to_user_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["confirmation_request_id"], ["giraffe_jp_confirmation_requests.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["service_node_id"], ["giraffe_jp_service_nodes.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_giraffe_jp_customer_service_tasks_confirmation_request_id"),
        "giraffe_jp_customer_service_tasks",
        ["confirmation_request_id"],
    )
    op.create_index(op.f("ix_giraffe_jp_customer_service_tasks_due_at"), "giraffe_jp_customer_service_tasks", ["due_at"])
    op.create_index(
        op.f("ix_giraffe_jp_customer_service_tasks_order_id"),
        "giraffe_jp_customer_service_tasks",
        ["order_id"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_customer_service_tasks_project_id"),
        "giraffe_jp_customer_service_tasks",
        ["project_id"],
    )
    op.create_index(
        op.f("ix_giraffe_jp_customer_service_tasks_service_node_id"),
        "giraffe_jp_customer_service_tasks",
        ["service_node_id"],
    )
    op.create_index(op.f("ix_giraffe_jp_customer_service_tasks_status"), "giraffe_jp_customer_service_tasks", ["status"])
    op.create_index(
        op.f("ix_giraffe_jp_customer_service_tasks_tenant_id"),
        "giraffe_jp_customer_service_tasks",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_giraffe_jp_customer_service_tasks_tenant_id"), table_name="giraffe_jp_customer_service_tasks")
    op.drop_index(op.f("ix_giraffe_jp_customer_service_tasks_status"), table_name="giraffe_jp_customer_service_tasks")
    op.drop_index(op.f("ix_giraffe_jp_customer_service_tasks_service_node_id"), table_name="giraffe_jp_customer_service_tasks")
    op.drop_index(op.f("ix_giraffe_jp_customer_service_tasks_project_id"), table_name="giraffe_jp_customer_service_tasks")
    op.drop_index(op.f("ix_giraffe_jp_customer_service_tasks_order_id"), table_name="giraffe_jp_customer_service_tasks")
    op.drop_index(op.f("ix_giraffe_jp_customer_service_tasks_due_at"), table_name="giraffe_jp_customer_service_tasks")
    op.drop_index(
        op.f("ix_giraffe_jp_customer_service_tasks_confirmation_request_id"),
        table_name="giraffe_jp_customer_service_tasks",
    )
    op.drop_table("giraffe_jp_customer_service_tasks")

    op.drop_index(op.f("ix_giraffe_jp_confirmation_requests_tenant_id"), table_name="giraffe_jp_confirmation_requests")
    op.drop_index(op.f("ix_giraffe_jp_confirmation_requests_status"), table_name="giraffe_jp_confirmation_requests")
    op.drop_index(
        op.f("ix_giraffe_jp_confirmation_requests_service_node_id"),
        table_name="giraffe_jp_confirmation_requests",
    )
    op.drop_index(op.f("ix_giraffe_jp_confirmation_requests_project_id"), table_name="giraffe_jp_confirmation_requests")
    op.drop_index(op.f("ix_giraffe_jp_confirmation_requests_order_id"), table_name="giraffe_jp_confirmation_requests")
    op.drop_index(op.f("ix_giraffe_jp_confirmation_requests_due_at"), table_name="giraffe_jp_confirmation_requests")
    op.drop_table("giraffe_jp_confirmation_requests")

    op.drop_index(op.f("ix_giraffe_jp_service_nodes_tenant_id"), table_name="giraffe_jp_service_nodes")
    op.drop_index(op.f("ix_giraffe_jp_service_nodes_status"), table_name="giraffe_jp_service_nodes")
    op.drop_index(op.f("ix_giraffe_jp_service_nodes_project_id"), table_name="giraffe_jp_service_nodes")
    op.drop_index(op.f("ix_giraffe_jp_service_nodes_order_id"), table_name="giraffe_jp_service_nodes")
    op.drop_index(op.f("ix_giraffe_jp_service_nodes_node_type"), table_name="giraffe_jp_service_nodes")
    op.drop_index(op.f("ix_giraffe_jp_service_nodes_due_at"), table_name="giraffe_jp_service_nodes")
    op.drop_table("giraffe_jp_service_nodes")
