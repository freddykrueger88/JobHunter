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
    # Onboarding-Wizard beim ersten Start bereits durchlaufen?
    onboarding_done: Mapped[bool] = mapped_column(Boolean, default=False)
    # API-Keys (Fernet-verschlüsselt)
    adzuna_app_id_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    adzuna_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_api_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    arbeitsagentur_client_id_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    arbeitsagentur_client_secret_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
