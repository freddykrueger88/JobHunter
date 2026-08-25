"""Add blocklist, user_badges, backup_logs, text_snippets tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-24

Hintergrund: Diese Modelle existierten nur in der veralteten, ungenutzten
backend/models.py (wurde vom backend/models/-Package ueberschattet) und
hatten nie eine Migration. Jetzt im Package nachgezogen (siehe
backend/models/blocklist.py, user_badge.py, backup_log.py,
text_snippet.py) - hier die zugehoerigen Tabellen.

cover_letter_templates -> text_snippets umbenannt (2026-08-25): echte
Namenskollision mit PR #91 (Issue #89, DOCX-Anschreiben-Vorlagen), das
ebenfalls eine cover_letter_templates-Tabelle einfuehrt, aber inhaltlich
komplett anders. Revisionsnummer bleibt vorerst 0004 (PR #91 ist lokal
noch nicht gemerged) - MUSS beim Mergen von PR #91 auf 0006 mit
down_revision=0005 verschoben werden (0005 ist bereits die separate
Rename-Migration text_snippets, siehe 0005_rename_...py), sonst
Revision-ID-Kollision.
Siehe docs/analysis/BACKLOG.md Phase F.2.
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blocklist",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("firma", sa.String, nullable=True),
        sa.Column("recruiter_name", sa.String, nullable=True),
        sa.Column("grund", sa.Text, nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "user_badges",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("badge_key", sa.String, unique=True),
        sa.Column("freigeschaltet_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "backup_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("dateiname", sa.String, nullable=True),
        sa.Column("groesse_bytes", sa.Integer, nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("erfolgreich", sa.Boolean, server_default=sa.true()),
    )

    op.create_table(
        "text_snippets",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("category", sa.String, server_default="allgemein"),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("is_custom", sa.Boolean, server_default=sa.false()),
        sa.Column("sprache", sa.String, server_default="de"),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("text_snippets")
    op.drop_table("backup_logs")
    op.drop_table("user_badges")
    op.drop_table("blocklist")
