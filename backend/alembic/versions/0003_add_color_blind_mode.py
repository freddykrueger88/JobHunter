"""Add color_blind_mode to settings table

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-25

Hintergrund: Das Frontend sendet color_blind_mode beim Auto-Save mit.
Da die Spalte in der DB fehlte, schlug jeder PATCH /settings/ mit
422 Validation Error fehl – auch das Speichern von API-Keys.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "settings",
        sa.Column(
            "color_blind_mode",
            sa.String(20),
            nullable=False,
            server_default="none",
        ),
    )


def downgrade() -> None:
    op.drop_column("settings", "color_blind_mode")
