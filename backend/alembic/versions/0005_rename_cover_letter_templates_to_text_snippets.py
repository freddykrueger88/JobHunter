"""Rename cover_letter_templates to text_snippets

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-25

Hintergrund: Tabelle text_snippets hiess in der bereits angewendeten
Migration 0004 noch cover_letter_templates. Umbenannt wegen echter
Namenskollision mit PR #91 (Issue #89, DOCX-Anschreiben-Vorlagen), das
eine inhaltlich komplett andere, ebenfalls cover_letter_templates
genannte Tabelle einfuehrt. Tabelle war zum Zeitpunkt der Umbenennung
leer (0 Zeilen), kein Datenverlust. Siehe docs/analysis/BACKLOG.md
Phase F.2.
"""
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("cover_letter_templates", "text_snippets")


def downgrade() -> None:
    op.rename_table("text_snippets", "cover_letter_templates")
