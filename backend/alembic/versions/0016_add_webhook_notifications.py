"""Add webhook notification settings

Revision ID: 0016
Revises: 0015
Create Date: 2026-08-27

#82/G.3.4: Slack/Discord/ntfy-Webhook-Benachrichtigungen bei neuen
Suchprofil-Treffern und/oder Bewerbungs-Statusaenderungen. URL
verschluesselt wie das SMTP-Passwort, gleiches Muster wie die
bestehenden Zugangsdaten-Spalten.
"""
from alembic import op
import sqlalchemy as sa

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("settings", sa.Column("webhook_url_enc", sa.Text(), nullable=True))
    op.add_column("settings", sa.Column("webhook_type", sa.String(length=20), nullable=True))
    op.add_column("settings", sa.Column("webhook_notify_new_jobs", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("settings", sa.Column("webhook_notify_status_change", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("settings", "webhook_notify_status_change")
    op.drop_column("settings", "webhook_notify_new_jobs")
    op.drop_column("settings", "webhook_type")
    op.drop_column("settings", "webhook_url_enc")
