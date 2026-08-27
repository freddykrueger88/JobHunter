"""
Tests fuer backend/services/reminder_mailer.py.

Kritischer Fund: UserSettings.smtp_host/smtp_port/smtp_user/
smtp_recipient/smtp_password_enc und Reminder.mail_sent existierten
auf keinem der beiden Modelle. Die Fruehausstiegs-Pruefung nutzte
getattr(s, "smtp_host", None), wodurch die Funktion nie crashte, aber
auch niemals ueber den Guard hinauskam - die SMTP-Konfiguration galt
technisch IMMER als fehlend, unabhaengig vom tatsaechlichen Zustand.
Migration 0014 ergaenzt beide Modelle, dieser Test faengt die
Funktion end-to-end ab (mit gemocktem aiosmtplib.send).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.crypto import encrypt
from backend.models.reminder import Reminder
from backend.models.settings import UserSettings
from backend.services.reminder_mailer import send_due_reminders

pytestmark = pytest.mark.asyncio


class TestSendDueReminders:
    async def test_skips_silently_when_smtp_not_configured(self, db: AsyncSession, monkeypatch):
        due = Reminder(remind_at=datetime.now(timezone.utc) - timedelta(minutes=5), message="Test")
        db.add(due)
        await db.commit()

        monkeypatch.setattr("backend.services.reminder_mailer.async_session_factory", lambda: _FakeCtx(db))

        with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            await send_due_reminders()
            mock_send.assert_not_called()

        await db.refresh(due)
        assert due.mail_sent is False

    async def test_sends_and_marks_due_reminder(self, db: AsyncSession, monkeypatch):
        db.add(UserSettings(
            id=1, smtp_host="smtp.example.com", smtp_port=587,
            smtp_user="bot@example.com", smtp_recipient="me@example.com",
            smtp_password_enc=encrypt("hunter2"),
        ))
        due = Reminder(remind_at=datetime.now(timezone.utc) - timedelta(minutes=5), message="Vorstellungsgespraech")
        not_due = Reminder(remind_at=datetime.now(timezone.utc) + timedelta(days=1), message="Zukunft")
        db.add_all([due, not_due])
        await db.commit()

        monkeypatch.setattr("backend.services.reminder_mailer.async_session_factory", lambda: _FakeCtx(db))

        with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            await send_due_reminders()
            mock_send.assert_called_once()

        result = await db.execute(select(Reminder).order_by(Reminder.id))
        reminders = {r.message: r.mail_sent for r in result.scalars().all()}
        assert reminders["Vorstellungsgespraech"] is True
        assert reminders["Zukunft"] is False


class _FakeCtx:
    """Ersetzt async_session_factory() - liefert die Test-DB-Session statt
    einer neuen Verbindung zum separaten, tabellenlosen globalen engine."""
    def __init__(self, db: AsyncSession):
        self._db = db

    async def __aenter__(self):
        return self._db

    async def __aexit__(self, *args):
        return False
