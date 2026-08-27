"""Add diary_entries table

Revision ID: 0018
Revises: 0017
Create Date: 2026-08-28

#80/G.3.6: Bewerbungs-Tagebuch - freies Notiz-Textfeld, durchsuchbar,
PDF-exportierbar. Nicht an eine bestimmte Bewerbung gebunden (dafuer
gibt es bereits Application.notes) - ein allgemeines Journal.
"""
from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "diary_entries",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("diary_entries")
