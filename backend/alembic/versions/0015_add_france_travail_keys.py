"""Add France Travail OAuth2 credentials

Revision ID: 0015
Revises: 0014
Create Date: 2026-08-27

Phase I.1 (EU-weite Jobboersen): France Travail (ex-Pole Emploi) ist die
franzoesische Entsprechung der deutschen Arbeitsagentur-Quelle, benoetigt
aber - anders als Arbeitsagentur/EURES/Karriere.NRW/service.bund.de -
vom Nutzer selbst kostenlos registrierte OAuth2-Zugangsdaten
(https://francetravail.io/inscription), gespeichert nach demselben
Muster wie die bestehenden adzuna_*_enc/linkedin_api_key_enc-Spalten.
"""
from alembic import op
import sqlalchemy as sa

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("settings", sa.Column("francetravail_client_id_enc", sa.Text(), nullable=True))
    op.add_column("settings", sa.Column("francetravail_client_secret_enc", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("settings", "francetravail_client_secret_enc")
    op.drop_column("settings", "francetravail_client_id_enc")
