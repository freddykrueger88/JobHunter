"""
Tests fuer backend/api/calendar.py + backend/services/calendar_export.py (#77).

Regressionsschutz fuer zwei Bugs, die beim manuellen Testen gefunden
wurden: build_ical_event griff auf job.titel/job.firma zu (existieren auf
dem Job-Modell nicht, korrekt: title/company) und get_all_ical filterte
auf Application.gespraechstermin (existiert nicht, korrekt: interview_at).
Beide Endpunkte crashten dadurch mit 500 - siehe BACKLOG.md.
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


async def _create_job_application_with_interview(client: httpx.AsyncClient, db: AsyncSession) -> int:
    job = Job(title="Backend Engineer", company="Beispiel GmbH", city="Bremen")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    res = await client.post("/api/applications/", json={"job_id": job.id})
    app_id = res.json()["id"]

    res = await client.patch(f"/api/applications/{app_id}", json={"interview_at": "2026-09-01T10:00:00"})
    assert res.status_code == 200, res.text
    return app_id


class TestCalendarExport:
    async def test_single_ics_does_not_crash_and_contains_job_info(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        app_id = await _create_job_application_with_interview(client, db)

        res = await client.get(f"/api/calendar/{app_id}/ics")

        assert res.status_code == 200, res.text
        assert "Backend Engineer" in res.text
        assert "Beispiel GmbH" in res.text
        assert "DTSTART:20260901T100000Z" in res.text

    async def test_feed_ics_includes_scheduled_interviews(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        await _create_job_application_with_interview(client, db)

        res = await client.get("/api/calendar/feed.ics")

        assert res.status_code == 200, res.text
        assert "BEGIN:VEVENT" in res.text
        assert "Backend Engineer" in res.text

    async def test_feed_ics_empty_without_interviews(self, client: httpx.AsyncClient):
        res = await client.get("/api/calendar/feed.ics")

        assert res.status_code == 200, res.text
        assert "BEGIN:VEVENT" not in res.text

    async def test_single_ics_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/calendar/999999/ics")
        assert res.status_code == 404
