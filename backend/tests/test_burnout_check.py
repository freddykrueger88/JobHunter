"""
Tests fuer GET /api/stats/burnout-check (#81, G.3.5 - Burnout-Fruehwarner).

"Ohne Erfolg" zaehlt bewusst nur Bewerbungen mit Status "beworben"
(noch offen) oder "absage" (abgelehnt) - "interessant" ist noch keine
abgeschickte Bewerbung und "interview"/"angenommen" sind ein Erfolg,
beide zaehlen nicht mit.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.job import Job
from backend.models.settings import UserSettings

pytestmark = pytest.mark.asyncio


async def _make_application(db: AsyncSession, status: str, created_at: datetime) -> None:
    job = Job(title="Testjob", company="Testfirma")
    db.add(job)
    await db.flush()
    db.add(Application(job_id=job.id, status=status, created_at=created_at))
    await db.commit()


class TestBurnoutCheck:
    async def test_no_warning_below_threshold(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=5, burnout_threshold_days=14))
        await db.commit()
        now = datetime.now(timezone.utc)
        for _ in range(4):
            await _make_application(db, "beworben", now)

        res = await client.get("/api/stats/burnout-check")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["warnung"] is False
        assert body["anzahl"] == 4

    async def test_warning_at_threshold(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=5, burnout_threshold_days=14))
        await db.commit()
        now = datetime.now(timezone.utc)
        for _ in range(5):
            await _make_application(db, "beworben", now)

        res = await client.get("/api/stats/burnout-check")

        body = res.json()
        assert body["warnung"] is True
        assert body["anzahl"] == 5

    async def test_rejected_applications_count_as_unsuccessful(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=2, burnout_threshold_days=14))
        await db.commit()
        now = datetime.now(timezone.utc)
        await _make_application(db, "beworben", now)
        await _make_application(db, "absage", now)

        res = await client.get("/api/stats/burnout-check")

        assert res.json()["warnung"] is True

    async def test_interview_and_angenommen_do_not_count(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=2, burnout_threshold_days=14))
        await db.commit()
        now = datetime.now(timezone.utc)
        await _make_application(db, "interview", now)
        await _make_application(db, "angenommen", now)

        res = await client.get("/api/stats/burnout-check")

        body = res.json()
        assert body["anzahl"] == 0
        assert body["warnung"] is False

    async def test_interessant_does_not_count(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=1, burnout_threshold_days=14))
        await db.commit()
        now = datetime.now(timezone.utc)
        await _make_application(db, "interessant", now)

        res = await client.get("/api/stats/burnout-check")

        body = res.json()
        assert body["anzahl"] == 0
        assert body["warnung"] is False

    async def test_applications_outside_window_do_not_count(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=1, burnout_threshold_days=14))
        await db.commit()
        old = datetime.now(timezone.utc) - timedelta(days=30)
        await _make_application(db, "beworben", old)

        res = await client.get("/api/stats/burnout-check")

        body = res.json()
        assert body["anzahl"] == 0
        assert body["warnung"] is False

    async def test_uses_default_threshold_without_settings_row(self, client: httpx.AsyncClient, db: AsyncSession):
        res = await client.get("/api/stats/burnout-check")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["schwellenwert"] == 10
        assert body["tage"] == 14

    async def test_custom_threshold_from_settings_is_respected(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, burnout_threshold_count=3, burnout_threshold_days=7))
        await db.commit()

        res = await client.get("/api/stats/burnout-check")

        body = res.json()
        assert body["schwellenwert"] == 3
        assert body["tage"] == 7
