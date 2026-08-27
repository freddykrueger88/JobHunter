"""
Tests fuer backend/services/badges.py + GET /api/badges/.

Bugfix-Sweep 2026-08-27: der Service existierte fertig, aber ohne
Router (BadgesPanel.tsx rief /api/badges/ auf, das es nirgends gab).
Ausserdem pruefte check_and_award auf Application.status == 'eingeladen'/
'zusage' - Status-Strings, die im aktuellen Schema nie existierten
(korrekt: 'interview'/'angenommen'), wodurch 2 der 10 Abzeichen nie
erreichbar gewesen waeren. streak_3/streak_7/ki_anschreiben/
lebenslauf_upload/foto_upload waren im urspruenglichen conditions-Array
komplett uebersprungen - jetzt ergaenzt.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.cover_letter import CoverLetter
from backend.models.cv import CVData
from backend.models.job import Job

pytestmark = pytest.mark.asyncio


class TestBadgesEndpoint:
    async def test_no_applications_returns_all_locked(self, client: httpx.AsyncClient):
        res = await client.get("/api/badges/")

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) == 10
        assert all(b["freigeschaltet"] is False for b in body)

    async def test_first_application_unlocks_erste_bewerbung(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        await client.post("/api/applications/", json={"job_id": job.id})

        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "erste_bewerbung")
        assert badge["freigeschaltet"] is True

    async def test_interview_status_unlocks_erste_einladung(self, client: httpx.AsyncClient, db: AsyncSession):
        """Regression: Bedingung war frueher status == 'eingeladen' (existiert nicht)."""
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]
        await client.patch(f"/api/applications/{app_id}", json={"status": "interview"})

        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "erste_einladung")
        assert badge["freigeschaltet"] is True

    async def test_angenommen_status_unlocks_erste_zusage(self, client: httpx.AsyncClient, db: AsyncSession):
        """Regression: Bedingung war frueher status == 'zusage' (existiert nicht)."""
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]
        await client.patch(f"/api/applications/{app_id}", json={"status": "angenommen"})

        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "erste_zusage")
        assert badge["freigeschaltet"] is True

    async def test_cv_upload_unlocks_lebenslauf_upload(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann"))
        await db.commit()

        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "lebenslauf_upload")
        assert badge["freigeschaltet"] is True

    async def test_cover_letter_unlocks_ki_anschreiben(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        db.add(CoverLetter(application_id=app_res.json()["id"], content="Sehr geehrte..."))
        await db.commit()

        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "ki_anschreiben")
        assert badge["freigeschaltet"] is True

    async def test_foto_upload_job_unlocks_foto_upload_badge(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(Job(title="Backend Engineer", company="Beispiel GmbH", source_portal="foto-upload"))
        await db.commit()

        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "foto_upload")
        assert badge["freigeschaltet"] is True

    async def test_three_consecutive_days_unlocks_streak_3(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for i in range(3):
            db.add(Application(job_id=job.id, status="interessant", created_at=base + timedelta(days=i)))
        await db.commit()

        res = await client.get("/api/badges/")

        badges = {b["key"]: b["freigeschaltet"] for b in res.json()}
        assert badges["streak_3"] is True
        assert badges["streak_7"] is False

    async def test_badge_stays_unlocked_once_awarded_even_if_condition_no_longer_holds(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]
        await client.get("/api/badges/")  # erste_bewerbung freigeschaltet

        await client.delete(f"/api/applications/{app_id}")
        res = await client.get("/api/badges/")

        badge = next(b for b in res.json() if b["key"] == "erste_bewerbung")
        assert badge["freigeschaltet"] is True
