"""Add quality-score caches (cover_letters.quality_score, applications.ats_score)

Revision ID: 0013
Revises: 0012
Create Date: 2026-08-27

Bugfix-Sweep: application_quality.py (QualityScoreCard.tsx) griff auf
Application.anschreiben_score/ats_score zu - nie existierende Felder,
die AI-Tools in diesem Projekt (cover_letter_evaluator, ats_scorer)
sind zustandslos und persistieren ihre Scores nirgends. Beide
schreiben ihr Ergebnis jetzt hier rein, damit der Qualitaetsscore
nicht bei jedem Aufruf alle Tools neu (und teuer, Ollama-gestuetzt)
ausfuehren muss.
"""
from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cover_letters", sa.Column("quality_score", sa.Integer(), nullable=True))
    op.add_column("applications", sa.Column("ats_score", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("applications", "ats_score")
    op.drop_column("cover_letters", "quality_score")
