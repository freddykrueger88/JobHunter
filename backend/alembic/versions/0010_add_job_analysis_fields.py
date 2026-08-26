"""Add job analysis fields (salary/work model/tags/skill gap)

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-26

job_analyzer.py und skill_gap.py (backend/services/) existierten bereits,
schrieben aber auf Job-Spalten, die nie angelegt wurden (gehalt_min/
gehalt_max/ist_remote/ist_hybrid/tags/sprache/skill_gap_score/
skill_gap_json) - siehe docs/analysis/BACKLOG.md. Ergaenzt die fehlenden
Spalten, damit beide KI-Analyse-Features tatsaechlich nutzbar sind.
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("salary_min", sa.Integer(), nullable=True))
    op.add_column("jobs", sa.Column("salary_max", sa.Integer(), nullable=True))
    op.add_column("jobs", sa.Column("work_model", sa.String(20), nullable=True))
    op.add_column("jobs", sa.Column("tags", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("skill_gap_score", sa.Integer(), nullable=True))
    op.add_column("jobs", sa.Column("skill_gap_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "skill_gap_json")
    op.drop_column("jobs", "skill_gap_score")
    op.drop_column("jobs", "tags")
    op.drop_column("jobs", "work_model")
    op.drop_column("jobs", "salary_max")
    op.drop_column("jobs", "salary_min")
