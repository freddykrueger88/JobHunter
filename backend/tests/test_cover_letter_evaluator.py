"""
Tests fuer backend/services/cover_letter_evaluator.py + POST
/api/applications/{id}/evaluate-cover-letter.

Regressionsschutz: der Service ging von app.anschreiben (Feld auf
Application) aus - Anschreiben liegen tatsaechlich in einer eigenen
Tabelle (cover_letters, per application_id verknuepft). Ausserdem
importierte er ein nie existierendes Modul (backend.services.ai_client)
- beides behoben.
"""
from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.cover_letter import CoverLetter
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


class TestEvaluateCoverLetterEndpoint:
    async def test_no_cover_letter_returns_404(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Test", company="TestCo")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.post(f"/api/applications/{app_id}/evaluate-cover-letter")

        assert res.status_code == 404

    async def test_evaluates_cover_letter_from_cover_letters_table(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Backend Engineer", company="Beispiel GmbH",
                   description="Wir suchen einen Python-Entwickler.")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        db.add(CoverLetter(
            application_id=app_id,
            content="Sehr geehrte Damen und Herren, ...",
            tone_used="formell",
            model_used="mistral",
        ))
        await db.commit()

        raw = '{"overall_score": 82, "relevance": 85, "tone": 80, "structure": 78, "strengths": ["klar"], "improvements": ["laenger"], "summary": "Guter Entwurf"}'
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(f"/api/applications/{app_id}/evaluate-cover-letter")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["overall_score"] == 82
        assert body["strengths"] == ["klar"]
