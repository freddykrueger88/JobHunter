"""Add followups table (Wiedervorlagen-System, Issue #64)

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "followups",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "application_id",
            sa.Integer,
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("faellig_am", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notiz", sa.Text, nullable=True),
        sa.Column("erledigt", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("erledigt_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "erstellt_am",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "aktualisiert_am",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Index fuer effiziente Ampel-Abfragen:
    # WHERE erledigt = false ORDER BY faellig_am
    op.create_index(
        "ix_followups_erledigt_faellig_am",
        "followups",
        ["erledigt", "faellig_am"],
    )


def downgrade() -> None:
    op.drop_index("ix_followups_erledigt_faellig_am", table_name="followups")
    op.drop_table("followups")
