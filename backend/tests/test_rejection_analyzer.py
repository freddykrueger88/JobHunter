"""
Tests fuer backend/services/rejection_analyzer.py + POST
/api/applications/{id}/analyze-rejection.

Regressionsschutz: der Service ging von app.anschreiben und app.absage_text
aus - beide existieren auf Application nicht (Anschreiben leben in der
eigenen cover_letters-Tabelle, ein Absage-Text-Feld gibt es im Datenmodell
gar nicht - deshalb jetzt als Request-Body-Parameter statt persistiertem
Feld). Ausserdem das ai_client-Problem wie bei den anderen Modulen.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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


class TestAnalyzeRejection:
    async def test_analyzes_rejection_without_cover_letter(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        raw = '{"strengths": ["klar"], "weaknesses": ["zu kurz"], "improvement_suggestions": ["mehr Details"], "summary": "Solide Basis"}'
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(
                f"/api/applications/{app_id}/analyze-rejection",
                json={"rejection_text": "Leider haben wir uns fuer einen anderen Kandidaten entschieden."},
            )

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["summary"] == "Solide Basis"
        assert body["weaknesses"] == ["zu kurz"]

    async def test_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.post(
            "/api/applications/999999/analyze-rejection",
            json={"rejection_text": "Absage-Text"},
        )
        assert res.status_code == 404
