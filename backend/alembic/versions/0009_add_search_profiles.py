"""Add search_profiles table

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-26

Das SearchProfile-Modell (backend/models/search_profile.py) und der
zugehoerige Router (backend/api/search_profiles.py, gespeicherte
Suchprofile mit automatischer Wiederholung via apscheduler) existierten
bereits, aber nie eine Migration die die Tabelle tatsaechlich anlegt -
jeder Aufruf von /api/search-profiles/* crashte mit
"relation search_profiles does not exist". Siehe docs/analysis/BACKLOG.md.
"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("keywords", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("radius_km", sa.Integer(), server_default="25"),
        sa.Column("schedule", sa.String(), server_default="daily"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("last_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_result_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("search_profiles")
