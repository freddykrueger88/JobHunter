"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("contact_person", sa.String(255), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("source_portal", sa.String(50), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=True, index=True),
        sa.Column("job_type", sa.String(50), nullable=True),
        sa.Column("is_hidden", sa.Boolean, default=False),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("distance_km", sa.Float, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # applications
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("job_id", sa.Integer, sa.ForeignKey("jobs.id", ondelete="CASCADE"), index=True),
        sa.Column("status", sa.String(50), default="interessant"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("interview_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("kanban_position", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # settings
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("theme", sa.String(20), default="dark"),
        sa.Column("language", sa.String(5), default="de"),
        sa.Column("ai_model", sa.String(100), default="mistral"),
        sa.Column("ai_tone", sa.String(50), default="formell"),
        sa.Column("default_location", sa.String(255), nullable=True),
        sa.Column("default_radius_km", sa.Integer, default=25),
        sa.Column("hide_ausbildung", sa.Boolean, default=True),
        sa.Column("reminder_default_days", sa.Integer, default=7),
        sa.Column("adzuna_app_id_enc", sa.Text, nullable=True),
        sa.Column("adzuna_api_key_enc", sa.Text, nullable=True),
        sa.Column("linkedin_api_key_enc", sa.Text, nullable=True),
        sa.Column("arbeitsagentur_client_id_enc", sa.Text, nullable=True),
        sa.Column("arbeitsagentur_client_secret_enc", sa.Text, nullable=True),
    )

    # cv_data
    op.create_table(
        "cv_data",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("skills", JSON, nullable=True),
        sa.Column("work_experience", JSON, nullable=True),
        sa.Column("education", JSON, nullable=True),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # cover_letters
    op.create_table(
        "cover_letters",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("application_id", sa.Integer, sa.ForeignKey("applications.id", ondelete="SET NULL"), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tone_used", sa.String(50), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("template_filename", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # reminders
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("application_id", sa.Integer, sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=True),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("is_done", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # history
    op.create_table(
        "history",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("event_type", sa.String(50), index=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("meta", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )

    # Default-Settings-Eintrag (immer id=1)
    op.execute("""
        INSERT INTO settings (id, theme, language, ai_model, ai_tone, default_radius_km, hide_ausbildung, reminder_default_days)
        VALUES (1, 'dark', 'de', 'mistral', 'formell', 25, true, 7)
    """)


def downgrade() -> None:
    op.drop_table("history")
    op.drop_table("reminders")
    op.drop_table("cover_letters")
    op.drop_table("cv_data")
    op.drop_table("settings")
    op.drop_table("applications")
    op.drop_table("jobs")
