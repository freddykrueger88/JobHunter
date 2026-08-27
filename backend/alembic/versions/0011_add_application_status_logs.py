"""Add application_status_logs table

Revision ID: 0011
Revises: 0010
Create Date: 2026-08-27

Bugfix-Sweep: das ApplicationStatusLog-Modell (backend/models/
application_status_log.py) existierte seit der urspruenglichen
Alembic-Einfuehrung (Commit 2d0db93), aber nie eine Migration die die
Tabelle anlegt - und nichts schrieb je hinein. Gleichzeitig ruft
Kanban.tsx im Detail-Modal seit jeher GET /api/applications/{id}/timeline
fuer die "Timeline"-Sektion auf, ein Endpoint der nirgends im Backend
existierte (404, still ignoriert da der Frontend-Query-Default ein
leeres Array ist - die Sektion verschwindet einfach statt zu crashen).
Modell-Felder (application_id, status, changed_at) passen exakt zum
Frontend-Interface TimelineEntry - naheliegend, dass beide urspruenglich
zusammengehoerten. Tabelle jetzt angelegt, Router schreibt bei jedem
Statuswechsel + Erstellung hinein und liefert sie ueber den neuen
Timeline-Endpoint aus.
"""
from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "application_status_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("application_id", sa.Integer(), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("application_status_logs")
