"""
Tests fuer backend/services/pdf_overview.py + GET /api/export/pdf-overview.

Regressionsschutz: der Service griff auf Application.bewerbungsdatum/notiz
und Job.firma/titel/bewerbungsfrist zu - keines dieser Felder existiert
auf den echten Modellen (korrekt: applied_at/notes, company/title; eine
Bewerbungsfrist wird in JobHunter ueberhaupt nicht getrackt). Ausserdem
war urspruenglich weasyprint als PDF-Engine vorgesehen, aber nie
installiert - auf reportlab umgestellt (im Projekt bereits vorhanden).
"""
from __future__ import annotations

import io

import httpx
import pytest
from pdfminer.high_level import extract_text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


class TestPdfOverview:
    async def test_pdf_overview_with_application(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", city="Bremen")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]
        await client.patch(f"/api/applications/{app_id}", json={"notes": "Testnotiz"})

        res = await client.get("/api/export/pdf-overview")

        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/pdf"
        assert res.content[:4] == b"%PDF"

    async def test_pdf_overview_empty(self, client: httpx.AsyncClient):
        res = await client.get("/api/export/pdf-overview")

        assert res.status_code == 200
        assert res.content[:4] == b"%PDF"

    async def test_exclude_status_omits_matching_applications(self, client: httpx.AsyncClient, db: AsyncSession):
        """Backlog L.1: Nachweis fuer die Agentur fuer Arbeit soll nur
        tatsaechlich abgeschickte Bewerbungen zeigen, nicht nur vorgemerkte."""
        interested_job = Job(title="Nur vorgemerkt", company="Vorgemerkt GmbH")
        applied_job = Job(title="Wirklich beworben", company="Beworben GmbH")
        db.add_all([interested_job, applied_job])
        await db.commit()
        await db.refresh(interested_job)
        await db.refresh(applied_job)

        await client.post("/api/applications/", json={"job_id": interested_job.id, "status": "interessant"})
        await client.post("/api/applications/", json={"job_id": applied_job.id, "status": "beworben"})

        res = await client.get("/api/export/pdf-overview", params={"exclude_status": "interessant"})

        assert res.status_code == 200, res.text
        text = extract_text(io.BytesIO(res.content))
        assert "Beworben GmbH" in text
        assert "Vorgemerkt GmbH" not in text
