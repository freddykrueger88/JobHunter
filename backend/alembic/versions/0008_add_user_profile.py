"""Add user_profile table (Phase H - KI-Hintergrundprofil)

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-25

Strukturiertes Nutzerprofil (Kernkompetenzen, Wunschrolle, Soft Skills,
Arbeitsstil, Werte) fuer bessere KI-Anschreiben - bisher bekam die KI
nur eine aus dem CV extrahierte Kurzfassung. Siehe
docs/analysis/BACKLOG.md Phase H.
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profile",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ueber_mich", sa.Text(), nullable=True),
        sa.Column("kernkompetenzen", sa.Text(), nullable=True),
        sa.Column("wunschrolle", sa.String(255), nullable=True),
        sa.Column("erfahrungsjahre", sa.Integer(), nullable=True),
        sa.Column("soft_skills", sa.Text(), nullable=True),
        sa.Column("arbeitsstil", sa.String(20), nullable=True),
        sa.Column("werte", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_profile")
