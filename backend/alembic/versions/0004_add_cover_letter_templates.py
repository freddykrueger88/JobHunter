"""Add cover_letter_templates table for DOCX template upload (Issue #89)

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-02

Nutzer können eigene DOCX-Anschreiben-Vorlagen mit Platzhaltern hochladen.
Die KI befüllt die Platzhalter stellenspezifisch und generiert ein fertiges DOCX.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cover_letter_templates",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("placeholders", ARRAY(sa.String()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("cover_letter_templates")
