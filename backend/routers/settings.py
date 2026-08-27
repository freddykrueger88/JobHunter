from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.settings import UserSettings
from backend.schemas.settings import SettingsRead, SettingsUpdate
from backend.core.crypto import encrypt

router = APIRouter(prefix="/api/settings", tags=["Einstellungen"])


async def get_or_create_settings(db: AsyncSession) -> UserSettings:
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = UserSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


def _to_read(s: UserSettings) -> SettingsRead:
    """Einzige Stelle, die UserSettings -> SettingsRead abbildet - GET und
    PATCH bauten das frueher beide manuell und getrennt zusammen, wodurch
    ein neues Pflichtfeld (weekly_goal) an einer der beiden Stellen vergessen
    wurde und GET /api/settings/ mit einem Pydantic-ValidationError crashte."""
    return SettingsRead(
        theme=s.theme,
        language=s.language,
        ai_model=s.ai_model,
        ai_tone=s.ai_tone,
        default_location=s.default_location,
        default_radius_km=s.default_radius_km,
        hide_ausbildung=s.hide_ausbildung,
        reminder_default_days=s.reminder_default_days,
        weekly_goal=s.weekly_goal,
        burnout_threshold_count=s.burnout_threshold_count,
        burnout_threshold_days=s.burnout_threshold_days,
        onboarding_done=s.onboarding_done,
        has_adzuna_key=bool(s.adzuna_api_key_enc),
        has_linkedin_key=bool(s.linkedin_api_key_enc),
        has_arbeitsagentur_key=bool(s.arbeitsagentur_client_id_enc),
        has_francetravail_key=bool(s.francetravail_client_id_enc),
        smtp_host=s.smtp_host,
        smtp_port=s.smtp_port,
        smtp_user=s.smtp_user,
        smtp_recipient=s.smtp_recipient,
        has_smtp_password=bool(s.smtp_password_enc),
        webhook_type=s.webhook_type,
        webhook_notify_new_jobs=s.webhook_notify_new_jobs,
        webhook_notify_status_change=s.webhook_notify_status_change,
        has_webhook_url=bool(s.webhook_url_enc),
    )


@router.get("/", response_model=SettingsRead)
async def get_settings(db: AsyncSession = Depends(get_db)):
    s = await get_or_create_settings(db)
    return _to_read(s)


@router.patch("/", response_model=SettingsRead)
async def update_settings(data: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    s = await get_or_create_settings(db)
    simple_fields = [
        "theme", "language", "ai_model", "ai_tone", "default_location",
        "default_radius_km", "hide_ausbildung", "reminder_default_days",
        "weekly_goal", "burnout_threshold_count", "burnout_threshold_days",
        "color_blind_mode", "onboarding_done",
        "smtp_host", "smtp_port", "smtp_user", "smtp_recipient",
        "webhook_type", "webhook_notify_new_jobs", "webhook_notify_status_change",
    ]
    for field in simple_fields:
        value = getattr(data, field)
        if value is not None:
            setattr(s, field, value)
    # API-Keys/Passwoerter verschlüsselt speichern
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
    if data.francetravail_client_id:
        s.francetravail_client_id_enc = encrypt(data.francetravail_client_id)
    if data.francetravail_client_secret:
        s.francetravail_client_secret_enc = encrypt(data.francetravail_client_secret)
    if data.smtp_password:
        s.smtp_password_enc = encrypt(data.smtp_password)
    if data.webhook_url:
        s.webhook_url_enc = encrypt(data.webhook_url)
    await db.commit()
    await db.refresh(s)
    return _to_read(s)


@router.post("/test-mail")
async def send_test_mail_endpoint(db: AsyncSession = Depends(get_db)):
    """Sendet eine Test-Mail mit den gespeicherten SMTP-Einstellungen."""
    from backend.services.mail import send_test_mail

    s = await get_or_create_settings(db)
    return await send_test_mail(s)


@router.post("/test-webhook")
async def send_test_webhook_endpoint(db: AsyncSession = Depends(get_db)):
    """Sendet eine Test-Benachrichtigung mit der gespeicherten Webhook-URL (#82, G.3.4)."""
    from backend.services.webhook_notifier import send_test_webhook

    s = await get_or_create_settings(db)
    return await send_test_webhook(s)
