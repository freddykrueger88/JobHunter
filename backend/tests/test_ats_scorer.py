"""
Tests fuer backend/services/ats_scorer.py + POST
/api/applications/{id}/ats-check.

AtsScorePanel.tsx + ats_scorer.py waren fertig gebaut, aber nirgends
verdrahtet: kein Router-Endpoint, keine Einbindung im Kanban-Detail-Modal
(siehe BACKLOG.md, Funktionsfaehigkeits-Audit 2026-08-27).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.cv import CVData
from backend.models.job import Job

pytestmark = pytest.mark.asyncio


class TestAtsCheckEndpoint:
    async def test_no_job_description_returns_400(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.post(f"/api/applications/{app_id}/ats-check")

        assert res.status_code == 400

    async def test_no_cv_returns_400(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python und FastAPI gesucht")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.post(f"/api/applications/{app_id}/ats-check")

        assert res.status_code == 400

    async def test_scores_latest_cv_against_job_description(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(
            title="Backend Engineer",
            company="Beispiel GmbH",
            description="Wir suchen einen erfahrenen Python Entwickler mit FastAPI Kenntnissen und Docker Erfahrung.",
        )
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann", raw_text="Erfahrener Python Entwickler mit FastAPI Kenntnissen."))
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.post(f"/api/applications/{app_id}/ats-check")

        assert res.status_code == 200, res.text
        body = res.json()
        assert "score" in body
        assert body["ampel"] in ("gruen", "gelb", "rot")
        assert "docker" in [kw.lower() for kw in body["missing_keywords"]]

    async def test_ai_suggestions_used_only_below_threshold(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python Rust Go Java C++ Kubernetes Terraform")
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann", raw_text="Ich kann kochen."))
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"response": '["Python erwaehnen", "Kubernetes-Erfahrung ergaenzen", "Rust hinzufuegen"]'}
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            res = await client.post(f"/api/applications/{app_id}/ats-check")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["score"] < 70
        assert body["ki_vorschlaege"] == ["Python erwaehnen", "Kubernetes-Erfahrung ergaenzen", "Rust hinzufuegen"]
