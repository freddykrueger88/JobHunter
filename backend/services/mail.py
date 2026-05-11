"""E-Mail-Service via aiosmtplib."""
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from backend.core.crypto import decrypt
import logging

logger = logging.getLogger(__name__)


async def send_reminder_email(
    smtp_host: str, smtp_port: int,
    smtp_user: str, smtp_password: str,
    recipient: str, subject: str, body_text: str,
) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(
        f"<html><body><p>{body_text.replace(chr(10), '<br>')}</p>"
        "<p style='color:#666;font-size:12px'>JobHunter 🎯</p></body></html>",
        "html", "utf-8"
    ))
    try:
        await aiosmtplib.send(
            msg, hostname=smtp_host, port=smtp_port,
            username=smtp_user, password=smtp_password,
            start_tls=True,
        )
        return True
    except Exception as e:
        logger.error(f"Mail-Fehler: {e}")
        return False


async def send_test_mail(settings_row) -> dict:
    """Sendet eine Test-Mail mit den gespeicherten SMTP-Einstellungen."""
    if not getattr(settings_row, "smtp_host", None):
        return {"success": False, "error": "SMTP nicht konfiguriert"}
    password = decrypt(settings_row.smtp_password_enc) if settings_row.smtp_password_enc else ""
    ok = await send_reminder_email(
        smtp_host=settings_row.smtp_host,
        smtp_port=settings_row.smtp_port or 587,
        smtp_user=settings_row.smtp_user or "",
        smtp_password=password,
        recipient=settings_row.smtp_recipient or settings_row.smtp_user or "",
        subject="✅ JobHunter Test-Mail",
        body_text="Diese Test-Mail bestätigt, dass deine SMTP-Konfiguration funktioniert.",
    )
    return {"success": ok, "error": None if ok else "Senden fehlgeschlagen – SMTP-Einstellungen prüfen"}
