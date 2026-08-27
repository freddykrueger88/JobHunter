from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class UserSettings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Theme: dark, light, boys, girls
    theme: Mapped[str] = mapped_column(String(20), default="dark")
    language: Mapped[str] = mapped_column(String(5), default="de")
    # Barrierefreiheit: none, protanopia, deuteranopia, tritanopia
    color_blind_mode: Mapped[str] = mapped_column(String(20), default="none")
    # KI
    ai_model: Mapped[str] = mapped_column(String(100), default="mistral")
    # KI-Laune: formell, direkt, modern, kreativ
    ai_tone: Mapped[str] = mapped_column(String(50), default="formell")
    # Suche
    default_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    default_radius_km: Mapped[int] = mapped_column(default=25)
    hide_ausbildung: Mapped[bool] = mapped_column(Boolean, default=True)
    # Erinnerungen
    reminder_default_days: Mapped[int] = mapped_column(default=7)
    # Wochenziel fuer WeeklyGoalWidget (Anzahl Bewerbungen/Woche)
    weekly_goal: Mapped[int] = mapped_column(default=5)
    # Burnout-Fruehwarner (#81, G.3.5): Warnung, wenn in
    # burnout_threshold_days Tagen burnout_threshold_count Bewerbungen
    # ohne Erfolg (kein Interview/keine Zusage) abgeschickt wurden.
    burnout_threshold_count: Mapped[int] = mapped_column(default=10)
    burnout_threshold_days: Mapped[int] = mapped_column(default=14)
    # Onboarding-Wizard beim ersten Start bereits durchlaufen?
    onboarding_done: Mapped[bool] = mapped_column(Boolean, default=False)
    # API-Keys (Fernet-verschlüsselt)
    adzuna_app_id_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    adzuna_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    arbeitsagentur_client_id_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    arbeitsagentur_client_secret_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    # France Travail (FR-Jobboerse, Phase I.1) - eigene OAuth2-Zugangsdaten
    # noetig, kein oeffentlicher Fest-Key wie bei Arbeitsagentur.
    francetravail_client_id_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    francetravail_client_secret_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    # SMTP fuer Erinnerungs-Mails (backend/services/reminder_mailer.py) -
    # Passwort verschluesselt wie die anderen Zugangsdaten oben.
    smtp_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smtp_port: Mapped[int | None] = mapped_column(nullable=True)
    smtp_user: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smtp_recipient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smtp_password_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Webhook-Benachrichtigungen (#82, G.3.4) - Slack/Discord/ntfy bei
    # neuen Suchprofil-Treffern und/oder Bewerbungs-Statusaenderungen.
    # URL verschluesselt wie SMTP-Passwort (Discord/Slack-Webhook-URLs
    # erlauben direktes Posten, wenn sie geleakt werden).
    webhook_url_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    webhook_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # slack, discord, ntfy
    webhook_notify_new_jobs: Mapped[bool] = mapped_column(Boolean, default=False)
    webhook_notify_status_change: Mapped[bool] = mapped_column(Boolean, default=False)
