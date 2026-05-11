"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('city', sa.String()),
        sa.Column('postal_code', sa.String()),
        sa.Column('address', sa.String()),
        sa.Column('contact_person', sa.String()),
        sa.Column('description', sa.Text()),
        sa.Column('url', sa.String()),
        sa.Column('job_type', sa.String()),
        sa.Column('source_portal', sa.String()),
        sa.Column('external_id', sa.String()),
        sa.Column('is_hidden', sa.Boolean(), default=False),
        sa.Column('published_at', sa.DateTime(timezone=True)),
        sa.Column('latitude', sa.Float()),
        sa.Column('longitude', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('applications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(), default='interessant'),
        sa.Column('notes', sa.Text()),
        sa.Column('kanban_position', sa.Integer(), default=0),
        sa.Column('applied_at', sa.DateTime(timezone=True)),
        sa.Column('interview_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('application_status_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('cv_data',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('raw_text', sa.Text()),
        sa.Column('full_name', sa.String()),
        sa.Column('email', sa.String()),
        sa.Column('phone', sa.String()),
        sa.Column('address', sa.String()),
        sa.Column('skills', JSONB),
        sa.Column('work_experience', JSONB),
        sa.Column('education', JSONB),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('history_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('meta', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('reminders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='SET NULL')),
        sa.Column('remind_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('message', sa.String()),
        sa.Column('is_done', sa.Boolean(), default=False),
        sa.Column('mail_sent', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('theme', sa.String(), default='dark'),
        sa.Column('language', sa.String(), default='de'),
        sa.Column('ai_model', sa.String(), default='mistral'),
        sa.Column('ai_tone', sa.String(), default='formell'),
        sa.Column('default_location', sa.String()),
        sa.Column('default_radius_km', sa.Integer(), default=25),
        sa.Column('hide_ausbildung', sa.Boolean(), default=True),
        sa.Column('reminder_default_days', sa.Integer(), default=7),
        sa.Column('adzuna_app_id_enc', sa.String()),
        sa.Column('adzuna_api_key_enc', sa.String()),
        sa.Column('linkedin_api_key_enc', sa.String()),
        sa.Column('arbeitsagentur_client_id_enc', sa.String()),
        sa.Column('arbeitsagentur_client_secret_enc', sa.String()),
        sa.Column('smtp_host', sa.String()),
        sa.Column('smtp_port', sa.Integer(), default=587),
        sa.Column('smtp_user', sa.String()),
        sa.Column('smtp_password_enc', sa.String()),
        sa.Column('smtp_recipient', sa.String()),
    )
    op.create_table('search_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('keywords', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('radius_km', sa.Integer(), default=25),
        sa.Column('schedule', sa.String(), default='daily'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_run', sa.DateTime(timezone=True)),
        sa.Column('last_result_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('cover_letters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='SET NULL')),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tone_used', sa.String()),
        sa.Column('model_used', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in ['cover_letters','users','search_profiles','user_settings','reminders',
                  'history_entries','cv_data','application_status_logs','applications','jobs']:
        op.drop_table(table)
