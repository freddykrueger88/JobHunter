"""Cron-Job: Fällige Erinnerungen per E-Mail versenden."""
from datetime import datetime, timezone
from sqlalchemy import select
from backend.core.database import async_session_factory
from backend.models.reminder import Reminder
from backend.models.settings import UserSettings
from backend.services.mail import send_reminder_email
from backend.core.crypto import decrypt
import logging

logger = logging.getLogger(__name__)


async def send_due_reminders():
    async with async_session_factory() as db:
        # Settings laden
        res = await db.execute(select(UserSettings).where(UserSettings.id == 1))
        s = res.scalar_one_or_none()
        if not s or not getattr(s, "smtp_host", None) or not getattr(s, "smtp_recipient", None):
            return  # SMTP nicht konfiguriert

        password = decrypt(s.smtp_password_enc) if s.smtp_password_enc else ""

        # Fällige, nicht erledigte, noch nicht gemailte Erinnerungen
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Reminder).where(
                Reminder.is_done == False,  # noqa
                Reminder.remind_at <= now,
                Reminder.mail_sent == False,  # noqa
            ).limit(20)
        )
        reminders = result.scalars().all()

        for r in reminders:
            subject = f"🔔 JobHunter Erinnerung: {r.message or 'Fällige Erinnerung'}"
            body = (
                f"Hallo!\n\nDiese Erinnerung ist fällig:\n\n"
                f"📌 {r.message or 'Keine Nachricht'}\n"
                f"🗓️  Fällig: {r.remind_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"JobHunter 🎯"
            )
            ok = await send_reminder_email(
                smtp_host=s.smtp_host, smtp_port=s.smtp_port or 587,
                smtp_user=s.smtp_user or "", smtp_password=password,
                recipient=s.smtp_recipient, subject=subject, body_text=body,
            )
            if ok:
                r.mail_sent = True
                logger.info(f"Erinnerung #{r.id} per Mail gesendet")

        await db.commit()
