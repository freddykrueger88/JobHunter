"""
Tests fuer backend/services/cv_optimizer.py + POST /api/applications/{id}/
cv-optimize.

Bugfix-Sweep 2026-08-27: CvOptimizerPanel.tsx existierte nicht (weder
Backend-Router noch Frontend-Komponente) - der Service war fertig,
gab aber je nach erkannter Sprache unterschiedliche JSON-Schluessel
zurueck (staerken/schwaechen/vorschlaege vs. strengths/weaknesses/
suggestions), was das Frontend gezwungen haette, zwei Response-Formen
zu behandeln (gleiches Problem wie bei cover_letter_evaluator.py vor
dessen Fix). Auf durchgehend englische Schluessel normalisiert.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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


class TestCvOptimize:
    async def test_no_cv_returns_400(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        res = await client.post(f"/api/applications/{app_id}/cv-optimize")

        assert res.status_code == 400

    async def test_uses_latest_cv_and_returns_english_keys_for_german_input(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python gesucht")
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann", raw_text="Erfahrener Python-Entwickler mit 5 Jahren Berufserfahrung."))
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        raw = '{"score": 68, "strengths": ["Klare Struktur"], "weaknesses": ["Zu kurz"], "suggestions": [{"section": "Skills", "suggestion": "Mehr Details"}]}'
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(f"/api/applications/{app_id}/cv-optimize")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["score"] == 68
        assert body["strengths"] == ["Klare Struktur"]
        assert body["suggestions"][0]["section"] == "Skills"

    async def test_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.post("/api/applications/999999/cv-optimize")
        assert res.status_code == 404
