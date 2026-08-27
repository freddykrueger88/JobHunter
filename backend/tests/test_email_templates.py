"""
Tests fuer backend/services/email_templates.py + GET /api/applications/
{id}/email-template/{template_type}.

Bugfix-Sweep 2026-08-27: EmailTemplatePanel.tsx existierte nicht, der
Service war fertig aber ohne Router. Dabei gefixt: fill_template()
nutzte .format_map({**kwargs}) - fehlt auch nur einer der template-
spezifischen Platzhalter (z.B. {uhrzeit} bei termin_bestaetigen ohne
gesetzten Interview-Termin), crasht das mit KeyError. Jetzt ueber ein
SafeDict abgefangen, fehlende Platzhalter bleiben sichtbar stehen statt
zu crashen.
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.cv import CVData
from backend.models.job import Job
from backend.services.email_templates import fill_template

pytestmark = pytest.mark.asyncio


class TestFillTemplateSafety:
    async def test_missing_placeholder_does_not_crash(self):
        """Regression: termin_bestaetigen braucht {datum}/{uhrzeit}, die
        hier bewusst fehlen."""
        result = fill_template("termin_bestaetigen", stelle="Backend Engineer")
        assert "{datum}" in result["body"]
        assert "{uhrzeit}" in result["body"]

    async def test_unknown_template_type_returns_empty(self):
        result = fill_template("does_not_exist")
        assert result == {"betreff": "", "body": ""}


class TestEmailTemplateEndpoint:
    async def test_fills_stelle_and_firma(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.get(f"/api/applications/{app_id}/email-template/nachfrage")

        assert res.status_code == 200, res.text
        body = res.json()
        assert "Backend Engineer" in body["body"]
        assert "Beispiel GmbH" in body["body"]

    async def test_fills_name_from_latest_cv(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann"))
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.get(f"/api/applications/{app_id}/email-template/followup")

        assert "Max" in res.json()["body"]
        assert "Mustermann" in res.json()["body"]

    async def test_interview_date_template_without_interview_at_does_not_crash(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.get(f"/api/applications/{app_id}/email-template/termin_bestaetigen")

        assert res.status_code == 200, res.text

    async def test_unknown_template_type_returns_400(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.get(f"/api/applications/{app_id}/email-template/unbekannt")

        assert res.status_code == 400

    async def test_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/applications/999999/email-template/nachfrage")
        assert res.status_code == 404
