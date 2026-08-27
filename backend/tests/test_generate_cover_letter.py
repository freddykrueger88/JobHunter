"""
Tests fuer POST /api/ai/generate-cover-letter.

CoverLetter.tsx (die KI-Anschreiben-Generierung, Kernfunktion laut
Produktvision) war im Frontend komplett ungeroutet und wurde erst
nachtraeglich (Bugfix-Sweep 2026-08-27) in Kanban.tsx eingebunden.
Dabei aufgefallen: die Komponente sendete nie application_id mit,
wodurch das generierte Anschreiben nie mit der Bewerbung verknuepft
wurde - CoverLetterQualityPanel, der ZIP-Export (auto_apply.py) und
das DIN-5008-PDF (das Firma/Titel aus cl.application_id herleitet)
fanden dadurch nie ein Anschreiben. Ausserdem nutzte der Endpoint ohne
explizites cv_id keinen Lebenslauf (anderes als skill_gap/job_analyzer/
ats_scorer, die alle automatisch den zuletzt hochgeladenen CV nutzen) -
beide Luecken hier durch Regressionstests abgesichert.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.cover_letter import CoverLetter
from backend.models.cv import CVData
from backend.models.job import Job

pytestmark = pytest.mark.asyncio


def _mock_ollama_response(response_text: str):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"response": response_text}
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestGenerateCoverLetter:
    async def test_links_cover_letter_to_application(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python gesucht")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        with patch("httpx.AsyncClient", return_value=_mock_ollama_response("Sehr geehrte Damen und Herren...")):
            res = await client.post("/api/ai/generate-cover-letter", json={
                "job_id": job.id,
                "application_id": app_id,
                "tone": "formell",
            })

        assert res.status_code == 200, res.text
        cl_id = res.json()["id"]
        cl = await db.get(CoverLetter, cl_id)
        assert cl.application_id == app_id

    async def test_uses_latest_cv_when_no_cv_id_given(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python gesucht")
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann", skills=["Python", "FastAPI"]))
        await db.commit()
        await db.refresh(job)

        mock_client = _mock_ollama_response("Sehr geehrte Damen und Herren...")
        with patch("httpx.AsyncClient", return_value=mock_client):
            res = await client.post("/api/ai/generate-cover-letter", json={
                "job_id": job.id,
                "tone": "formell",
            })

        assert res.status_code == 200, res.text
        sent_prompt = mock_client.post.call_args.kwargs["json"]["prompt"]
        assert "Max Mustermann" in sent_prompt
        assert "Python" in sent_prompt

    async def test_job_not_found_returns_404(self, client: httpx.AsyncClient):
        res = await client.post("/api/ai/generate-cover-letter", json={"job_id": 999999})
        assert res.status_code == 404
