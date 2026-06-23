"""add_mside_actor_columns_to_projects

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add actor-based (M-side / GLTG) project identity columns that exist in
    # the Project ORM model but were absent from the initial schema migration.
    # FK references to actors.actor_id are intentionally omitted here: the
    # actors registry lives outside this migration chain and the columns are
    # stored as plain VARCHAR so inserts succeed without a live actors table.
    op.add_column("projects", sa.Column("project_id", sa.String(36), nullable=True))
    op.create_unique_constraint("uq_projects_project_id", "projects", ["project_id"])
    op.add_column("projects", sa.Column("original_buyer_actor_id", sa.String(36), nullable=True))
    op.add_column("projects", sa.Column("main_supplier_actor_id", sa.String(36), nullable=True))
    op.add_column("projects", sa.Column("category", sa.String(128), nullable=True))
    op.add_column("projects", sa.Column("product_summary", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("quantity", sa.Integer(), nullable=True))
    op.add_column("projects", sa.Column("product_tier", sa.String(32), nullable=True))
    op.add_column("projects", sa.Column("created_by_channel", sa.String(64), nullable=True))
    op.add_column("projects", sa.Column("metadata_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "metadata_json")
    op.drop_column("projects", "created_by_channel")
    op.drop_column("projects", "product_tier")
    op.drop_column("projects", "quantity")
    op.drop_column("projects", "product_summary")
    op.drop_column("projects", "category")
    op.drop_column("projects", "main_supplier_actor_id")
    op.drop_column("projects", "original_buyer_actor_id")
    op.drop_constraint("uq_projects_project_id", "projects", type_="unique")
    op.drop_column("projects", "project_id")
