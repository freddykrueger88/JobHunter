"""Add burnout early-warning threshold settings

Revision ID: 0017
Revises: 0016
Create Date: 2026-08-27

#81/G.3.5: konfigurierbarer Schwellenwert fuer den Burnout-Fruehwarner
(Warnung bei zu vielen Bewerbungen ohne Erfolg in kurzer Zeit).
"""
from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("settings", sa.Column("burnout_threshold_count", sa.Integer(), nullable=False, server_default="10"))
    op.add_column("settings", sa.Column("burnout_threshold_days", sa.Integer(), nullable=False, server_default="14"))


def downgrade() -> None:
    op.drop_column("settings", "burnout_threshold_days")
    op.drop_column("settings", "burnout_threshold_count")
