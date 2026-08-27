"""Add weekly_goal to settings

Revision ID: 0012
Revises: 0011
Create Date: 2026-08-27

Bugfix-Sweep: WeeklyGoalWidget.tsx (GET /api/stats/weekly-goal) und
StatsChart.tsx (GET /api/stats/, GET /api/stats/weekly) waren fertig
gebaute, aber nie erreichbare Dashboard-Widgets - kein /api/stats-Router
existierte. Fuer den Fortschrittsbalken braucht es ein konfigurierbares
Wochenziel; bisher gab es dafuer kein Feld.
"""
from alembic import op
import sqlalchemy as sa

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("settings", sa.Column("weekly_goal", sa.Integer(), nullable=False, server_default="5"))


def downgrade() -> None:
    op.drop_column("settings", "weekly_goal")
