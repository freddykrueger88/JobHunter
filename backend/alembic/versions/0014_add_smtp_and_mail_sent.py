"""Add SMTP settings + reminders.mail_sent

Revision ID: 0014
Revises: 0013
Create Date: 2026-08-27

Bugfix-Sweep: reminder_mailer.py (Cron-Job fuer Erinnerungs-E-Mails)
und mail.py (SMTP-Versand + Testmail) referenzierten
UserSettings.smtp_host/smtp_port/smtp_user/smtp_recipient/
smtp_password_enc und Reminder.mail_sent - keines davon existierte auf
den Modellen. Da die Felder in reminder_mailer.py nur ueber getattr()
mit Default None abgefragt wurden, crashte das nicht sofort, sondern
sorgte still dafuer, dass die Funktion die Fruehausstiegs-Bedingung
("SMTP nicht konfiguriert") immer traf - das Feature konnte technisch
nie funktionieren, unabhaengig von der tatsaechlichen Konfiguration.
"""
from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("settings", sa.Column("smtp_host", sa.String(length=255), nullable=True))
    op.add_column("settings", sa.Column("smtp_port", sa.Integer(), nullable=True))
    op.add_column("settings", sa.Column("smtp_user", sa.String(length=255), nullable=True))
    op.add_column("settings", sa.Column("smtp_recipient", sa.String(length=255), nullable=True))
    op.add_column("settings", sa.Column("smtp_password_enc", sa.Text(), nullable=True))
    op.add_column("reminders", sa.Column("mail_sent", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("reminders", "mail_sent")
    op.drop_column("settings", "smtp_password_enc")
    op.drop_column("settings", "smtp_recipient")
    op.drop_column("settings", "smtp_user")
    op.drop_column("settings", "smtp_port")
    op.drop_column("settings", "smtp_host")
