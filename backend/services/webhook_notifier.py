"""Webhook-Benachrichtigungen (Slack/Discord/ntfy) bei neuen Treffern
oder Statusaenderungen (#82, G.3.4).

Alle drei Dienste nehmen einen simplen POST-Request entgegen, nur das
Payload-Format unterscheidet sich:
- Slack: JSON {"text": "..."} an die Incoming-Webhook-URL
- Discord: JSON {"content": "..."} an die Webhook-URL
- ntfy: reiner Text-Body (kein JSON) an die Topic-URL
  (https://ntfy.sh/<topic> oder eine selbstgehostete Instanz)
"""
from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

WEBHOOK_TYPES = ("slack", "discord", "ntfy")


async def send_webhook(url: str, webhook_type: str, message: str) -> bool:
    if not url:
        return False

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if webhook_type == "slack":
                r = await client.post(url, json={"text": message})
            elif webhook_type == "discord":
                r = await client.post(url, json={"content": message})
            elif webhook_type == "ntfy":
                r = await client.post(url, content=message.encode("utf-8"), headers={"Content-Type": "text/plain; charset=utf-8"})
            else:
                logger.error("send_webhook: unbekannter webhook_type '%s'", webhook_type)
                return False
            r.raise_for_status()
        return True
    except Exception as e:
        logger.error("send_webhook: Senden fehlgeschlagen (%s): %s", webhook_type, e)
        return False


async def notify_new_jobs(settings_row, profile_name: str, count: int) -> None:
    if not getattr(settings_row, "webhook_url_enc", None) or not settings_row.webhook_notify_new_jobs:
        return
    from backend.core.crypto import decrypt

    url = decrypt(settings_row.webhook_url_enc)
    message = f"🔍 JobHunter: Suchprofil \"{profile_name}\" hat {count} neue Stelle(n) gefunden."
    await send_webhook(url, settings_row.webhook_type or "slack", message)


async def notify_status_change(settings_row, job_title: str, company: str, old_status: str, new_status: str) -> None:
    if not getattr(settings_row, "webhook_url_enc", None) or not settings_row.webhook_notify_status_change:
        return
    from backend.core.crypto import decrypt

    url = decrypt(settings_row.webhook_url_enc)
    message = f"📋 JobHunter: \"{job_title}\" bei {company}: {old_status} → {new_status}"
    await send_webhook(url, settings_row.webhook_type or "slack", message)


async def send_test_webhook(settings_row) -> dict:
    if not settings_row.webhook_url_enc:
        return {"success": False, "error": "Webhook nicht konfiguriert"}
    from backend.core.crypto import decrypt

    url = decrypt(settings_row.webhook_url_enc)
    ok = await send_webhook(url, settings_row.webhook_type or "slack", "✅ JobHunter Test-Benachrichtigung")
    return {"success": ok, "error": None if ok else "Senden fehlgeschlagen – Webhook-URL prüfen"}
