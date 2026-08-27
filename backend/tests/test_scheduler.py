"""
Tests fuer backend/services/scheduler.py.

Kritischster Fund im Bugfix-Sweep: init_scheduler() (der einzige Ort,
der scheduler.start() aufruft) wurde nirgends im Backend aufgerufen -
weder in main.py noch sonstwo. schedule_profile() registrierte bei
jedem Anlegen/Aktivieren eines Suchprofils zwar einen APScheduler-Job,
aber ohne .start() feuert APScheduler keinen einzigen davon. Die
komplette automatische Stellensuche (SearchProfile) lief dadurch trotz
funktionierender CRUD-API nie automatisch - nur manuelles "Jetzt
ausfuehren" funktionierte. Jetzt in main.py's Startup-Event aufgerufen,
zusaetzlich mit reminder_mailer (alle 15 Min) und backup (taeglich)
verdrahtet.

init_scheduler() nutzt scheduler.py's eigene async_session_factory
(nicht die get_db-Dependency) - fuer den Test durch die Test-DB-Session
ersetzt, sonst griffe es auf die separate, tabellenlose In-Memory-DB
des globalen engine-Objekts zu.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.scheduler import init_scheduler, scheduler

pytestmark = pytest.mark.asyncio


class TestInitScheduler:
    async def test_starts_scheduler_and_registers_recurring_jobs(self, db: AsyncSession, monkeypatch):
        @asynccontextmanager
        async def fake_session_factory():
            yield db

        monkeypatch.setattr("backend.services.scheduler.async_session_factory", fake_session_factory)

        try:
            await init_scheduler()

            assert scheduler.running is True
            job_ids = {j.id for j in scheduler.get_jobs()}
            assert "reminder_mailer" in job_ids
            assert "daily_backup" in job_ids
        finally:
            if scheduler.running:
                scheduler.shutdown(wait=False)
