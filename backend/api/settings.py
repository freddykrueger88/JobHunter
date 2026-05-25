from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.settings import UserSettings
from backend.schemas.settings import SettingsRead, SettingsUpdate
from backend.core.crypto import encrypt

router = APIRouter(prefix="/settings", tags=["Einstellungen"])


async def get_or_create_settings(db: AsyncSession) -> UserSettings:
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = UserSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("/", response_model=SettingsRead)
async def get_settings(db: AsyncSession = Depends(get_db)):
    s = await get_or_create_settings(db)
    return SettingsRead(
        theme=s.theme,
        language=s.language,
        ai_model=s.ai_model,
        ai_tone=s.ai_tone,
        default_location=s.default_location,
        default_radius_km=s.default_radius_km,
        hide_ausbildung=s.hide_ausbildung,
        reminder_default_days=s.reminder_default_days,
        has_adzuna_key=bool(s.adzuna_api_key_enc),
        has_linkedin_key=bool(s.linkedin_api_key_enc),
        has_arbeitsagentur_key=bool(s.arbeitsagentur_client_id_enc),
    )


@router.patch("/", response_model=SettingsRead)
async def update_settings(data: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    s = await get_or_create_settings(db)
    simple_fields = [
        "theme", "language", "ai_model", "ai_tone", "default_location",
        "default_radius_km", "hide_ausbildung", "reminder_default_days",
        "color_blind_mode",
    ]
    for field in simple_fields:
        value = getattr(data, field)
        if value is not None:
            setattr(s, field, value)
    # API-Keys verschlüsselt speichern
    if data.adzuna_app_id:
        s.adzuna_app_id_enc = encrypt(data.adzuna_app_id)
    if data.adzuna_api_key:
        s.adzuna_api_key_enc = encrypt(data.adzuna_api_key)
    if data.linkedin_api_key:
        s.linkedin_api_key_enc = encrypt(data.linkedin_api_key)
    if data.arbeitsagentur_client_id:
        s.arbeitsagentur_client_id_enc = encrypt(data.arbeitsagentur_client_id)
    if data.arbeitsagentur_client_secret:
        s.arbeitsagentur_client_secret_enc = encrypt(data.arbeitsagentur_client_secret)
    await db.commit()
    await db.refresh(s)
    return SettingsRead(
        theme=s.theme, language=s.language, ai_model=s.ai_model, ai_tone=s.ai_tone,
        default_location=s.default_location, default_radius_km=s.default_radius_km,
        hide_ausbildung=s.hide_ausbildung, reminder_default_days=s.reminder_default_days,
        has_adzuna_key=bool(s.adzuna_api_key_enc),
        has_linkedin_key=bool(s.linkedin_api_key_enc),
        has_arbeitsagentur_key=bool(s.arbeitsagentur_client_id_enc),
    )
