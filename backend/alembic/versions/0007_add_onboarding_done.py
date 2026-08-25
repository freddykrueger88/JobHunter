"""Add onboarding_done to settings

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-25

Onboarding-Wizard (frontend/src/pages/Onboarding.tsx) existierte im
Frontend bereits seit v1.3 (#50), war aber nie in App.tsx eingebunden
und das dafuer benoetigte settings.onboarding_done-Feld fehlte im
Backend komplett. Beides jetzt nachgezogen (siehe
docs/analysis/BACKLOG.md Phase F.3-Entscheidung).
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "settings",
        sa.Column("onboarding_done", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("settings", "onboarding_done")
