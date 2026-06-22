"""add_actor_columns_to_projects

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-22 13:00:00.000000

Adds the actor-based identity columns to the projects table that are present in the
Project ORM model but were omitted from the initial migration.

The original_buyer_actor_id and main_supplier_actor_id columns reference actors.actor_id
in the model but the actors table is not yet present — those columns are added without
FK constraints here and can be constrained once actors is introduced.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("project_id", sa.String(length=36), nullable=True))
    op.add_column("projects", sa.Column("original_buyer_actor_id", sa.String(length=36), nullable=True))
    op.add_column("projects", sa.Column("main_supplier_actor_id", sa.String(length=36), nullable=True))
    op.add_column("projects", sa.Column("category", sa.String(length=128), nullable=True))
    op.add_column("projects", sa.Column("product_summary", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("quantity", sa.Integer(), nullable=True))
    op.add_column("projects", sa.Column("product_tier", sa.String(length=32), nullable=True))
    op.add_column("projects", sa.Column("created_by_channel", sa.String(length=64), nullable=True))
    op.add_column("projects", sa.Column("metadata_json", sa.JSON(), nullable=True))
    op.create_unique_constraint("uq_projects_project_id", "projects", ["project_id"])


def downgrade() -> None:
    op.drop_constraint("uq_projects_project_id", "projects", type_="unique")
    op.drop_column("projects", "metadata_json")
    op.drop_column("projects", "created_by_channel")
    op.drop_column("projects", "product_tier")
    op.drop_column("projects", "quantity")
    op.drop_column("projects", "product_summary")
    op.drop_column("projects", "category")
    op.drop_column("projects", "main_supplier_actor_id")
    op.drop_column("projects", "original_buyer_actor_id")
    op.drop_column("projects", "project_id")
