from pydantic import BaseModel


class SettingsRead(BaseModel):
    theme: str
    language: str
    ai_model: str
    ai_tone: str
    default_location: str | None
    default_radius_km: int
    hide_ausbildung: bool
    reminder_default_days: int
    weekly_goal: int
    onboarding_done: bool
    # API-Keys werden NICHT im Klartext zurückgegeben
    has_adzuna_key: bool
    has_linkedin_key: bool
    has_arbeitsagentur_key: bool

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    ai_model: str | None = None
    ai_tone: str | None = None
    default_location: str | None = None
    default_radius_km: int | None = None
    hide_ausbildung: bool | None = None
    reminder_default_days: int | None = None
    weekly_goal: int | None = None
    color_blind_mode: str | None = None
    onboarding_done: bool | None = None
    # API-Keys im Klartext – werden beim Speichern verschlüsselt
    adzuna_app_id: str | None = None
    adzuna_api_key: str | None = None
    linkedin_api_key: str | None = None
    arbeitsagentur_client_id: str | None = None
    arbeitsagentur_client_secret: str | None = None
