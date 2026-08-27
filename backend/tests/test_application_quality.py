"""
Tests fuer backend/services/application_quality.py + GET /api/applications/
{id}/quality-score.

Bugfix-Sweep 2026-08-27: QualityScoreCard.tsx war fertig gebaut, aber
ohne Router. Der Service griff ausserdem auf Application.anschreiben/
anschreiben_score/cv_pfad/ats_score zu - keines davon existierte je
(Anschreiben liegen in einer eigenen Tabelle, CVs sind global, Scores
wurden nirgends zwischengespeichert). cover_letter_evaluator.py und der
ats-check-Endpoint schreiben ihre Scores jetzt in neue Cache-Spalten
(CoverLetter.quality_score, Application.ats_score).
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.cover_letter import CoverLetter
from backend.models.cv import CVData
from backend.models.job import Job

pytestmark = pytest.mark.asyncio


class TestQualityScore:
    async def test_nothing_done_yet_gives_zero_score(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.get(f"/api/applications/{app_id}/quality-score")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["gesamt_score"] == 0
        assert body["ampel"] == "rot"
        assert body["vollstaendig"] is False
        assert body["naechster_schritt"]["key"] == "anschreiben"

    async def test_all_components_present_gives_full_score(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", skill_gap_score=80)
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann"))
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        db.add(CoverLetter(application_id=app_id, content="Sehr geehrte...", quality_score=90))
        # ats_score direkt setzen (der echte Endpoint braucht Ollama)
        from backend.models.application import Application
        app = await db.get(Application, app_id)
        app.ats_score = 70
        await db.commit()

        res = await client.get(f"/api/applications/{app_id}/quality-score")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["vollstaendig"] is True
        assert body["naechster_schritt"] is None
        assert body["gesamt_score"] > 70

    async def test_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/applications/999999/quality-score")
        assert res.status_code == 404

    async def test_no_link_in_checklist_items(self, client: httpx.AsyncClient, db: AsyncSession):
        """Regression: die urspruenglichen Links (/bewerbung/{id}/...)
        zeigten auf eine Route, die es im Frontend nie gab."""
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.get(f"/api/applications/{app_id}/quality-score")

        assert all(item["link"] is None for item in res.json()["checklist"])
