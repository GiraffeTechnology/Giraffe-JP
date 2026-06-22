"""add_giraffe_jp_iterations_02_03_04

Revision ID: d4e5f6a7b8c9
Revises: b2c3d4e5f6a7
Create Date: 2026-06-22 10:00:00.000000

Adds tables for Giraffe JP Iterations 02, 03, and 04. The service-core
tables (giraffe_jp_service_nodes, giraffe_jp_confirmation_requests,
giraffe_jp_customer_service_tasks) were created by migration b2c3d4e5f6a7
and are not touched here.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Iteration 02: Message Category Auto-Send Permissions ────────────────────
    op.create_table(
        'giraffe_jp_message_category_permissions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('category_id', sa.String(length=128), nullable=False),
        sa.Column('category_name', sa.String(length=255), nullable=False),
        sa.Column('party_type', sa.String(length=64), nullable=False),
        sa.Column('channel', sa.String(length=64), nullable=True),
        sa.Column('auto_send', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'category_id', name='uq_gjp_tenant_category'),
    )
    op.create_index('ix_gjp_msg_perms_tenant_id', 'giraffe_jp_message_category_permissions', ['tenant_id'])

    # ── Iteration 03: Web Dialog and Email Communication Layer ────────────
    op.create_table(
        'giraffe_jp_conversation_threads',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=True),
        sa.Column('party_type', sa.String(length=64), nullable=False),
        sa.Column('party_ref_id', sa.String(length=255), nullable=True),
        sa.Column('thread_type', sa.String(length=64), nullable=False),
        sa.Column('subject', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gjp_conv_threads_tenant_id', 'giraffe_jp_conversation_threads', ['tenant_id'])
    op.create_index('ix_gjp_conv_threads_project_id', 'giraffe_jp_conversation_threads', ['project_id'])
    op.create_index('ix_gjp_conv_threads_status', 'giraffe_jp_conversation_threads', ['status'])

    op.create_table(
        'giraffe_jp_messages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('thread_id', sa.Uuid(), nullable=False),
        sa.Column('direction', sa.String(length=16), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('sender_ref', sa.String(length=255), nullable=True),
        sa.Column('message_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['thread_id'], ['giraffe_jp_conversation_threads.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gjp_messages_tenant_id', 'giraffe_jp_messages', ['tenant_id'])
    op.create_index('ix_gjp_messages_thread_id', 'giraffe_jp_messages', ['thread_id'])

    op.create_table(
        'giraffe_jp_outbound_message_drafts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('thread_id', sa.Uuid(), nullable=False),
        sa.Column('category_id', sa.String(length=128), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('approval_status', sa.String(length=32), nullable=False),
        sa.Column('reviewed_by_user_id', sa.Uuid(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['thread_id'], ['giraffe_jp_conversation_threads.id']),
        sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gjp_drafts_tenant_id', 'giraffe_jp_outbound_message_drafts', ['tenant_id'])
    op.create_index('ix_gjp_drafts_thread_id', 'giraffe_jp_outbound_message_drafts', ['thread_id'])
    op.create_index('ix_gjp_drafts_approval_status', 'giraffe_jp_outbound_message_drafts', ['approval_status'])

    op.create_table(
        'giraffe_jp_message_delivery_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('draft_id', sa.Uuid(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('channel', sa.String(length=64), nullable=False),
        sa.Column('delivery_status', sa.String(length=32), nullable=False),
        sa.Column('delivery_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['draft_id'], ['giraffe_jp_outbound_message_drafts.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gjp_delivery_logs_tenant_id', 'giraffe_jp_message_delivery_logs', ['tenant_id'])
    op.create_index('ix_gjp_delivery_logs_draft_id', 'giraffe_jp_message_delivery_logs', ['draft_id'])

    # ── Iteration 04: Formalwear C2B2M Order Extension ──────────────────
    op.create_table(
        'giraffe_jp_formalwear_order_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('garment_category', sa.String(length=64), nullable=False),
        sa.Column('hollow_to_hem_cm', sa.Float(), nullable=True),
        sa.Column('hollow_to_hem_required', sa.Boolean(), nullable=False),
        sa.Column('model_try_on_required', sa.Boolean(), nullable=False),
        sa.Column('local_alteration_possible', sa.Boolean(), nullable=False),
        sa.Column('custom_measurements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gjp_formalwear_tenant_id', 'giraffe_jp_formalwear_order_profiles', ['tenant_id'])
    op.create_index('ix_gjp_formalwear_project_id', 'giraffe_jp_formalwear_order_profiles', ['project_id'])

    op.create_table(
        'giraffe_jp_c2b2m_role_edges',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tenant_id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('role_from', sa.String(length=64), nullable=False),
        sa.Column('role_to', sa.String(length=64), nullable=False),
        sa.Column('edge_label', sa.String(length=128), nullable=False),
        sa.Column('edge_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gjp_c2b2m_edges_tenant_id', 'giraffe_jp_c2b2m_role_edges', ['tenant_id'])
    op.create_index('ix_gjp_c2b2m_edges_project_id', 'giraffe_jp_c2b2m_role_edges', ['project_id'])


def downgrade() -> None:
    op.drop_index('ix_gjp_c2b2m_edges_project_id', table_name='giraffe_jp_c2b2m_role_edges')
    op.drop_index('ix_gjp_c2b2m_edges_tenant_id', table_name='giraffe_jp_c2b2m_role_edges')
    op.drop_table('giraffe_jp_c2b2m_role_edges')

    op.drop_index('ix_gjp_formalwear_project_id', table_name='giraffe_jp_formalwear_order_profiles')
    op.drop_index('ix_gjp_formalwear_tenant_id', table_name='giraffe_jp_formalwear_order_profiles')
    op.drop_table('giraffe_jp_formalwear_order_profiles')

    op.drop_index('ix_gjp_delivery_logs_draft_id', table_name='giraffe_jp_message_delivery_logs')
    op.drop_index('ix_gjp_delivery_logs_tenant_id', table_name='giraffe_jp_message_delivery_logs')
    op.drop_table('giraffe_jp_message_delivery_logs')

    op.drop_index('ix_gjp_drafts_approval_status', table_name='giraffe_jp_outbound_message_drafts')
    op.drop_index('ix_gjp_drafts_thread_id', table_name='giraffe_jp_outbound_message_drafts')
    op.drop_index('ix_gjp_drafts_tenant_id', table_name='giraffe_jp_outbound_message_drafts')
    op.drop_table('giraffe_jp_outbound_message_drafts')

    op.drop_index('ix_gjp_messages_thread_id', table_name='giraffe_jp_messages')
    op.drop_index('ix_gjp_messages_tenant_id', table_name='giraffe_jp_messages')
    op.drop_table('giraffe_jp_messages')

    op.drop_index('ix_gjp_conv_threads_status', table_name='giraffe_jp_conversation_threads')
    op.drop_index('ix_gjp_conv_threads_project_id', table_name='giraffe_jp_conversation_threads')
    op.drop_index('ix_gjp_conv_threads_tenant_id', table_name='giraffe_jp_conversation_threads')
    op.drop_table('giraffe_jp_conversation_threads')

    op.drop_index('ix_gjp_msg_perms_tenant_id', table_name='giraffe_jp_message_category_permissions')
    op.drop_table('giraffe_jp_message_category_permissions')
