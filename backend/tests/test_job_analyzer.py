"""
Tests fuer backend/services/job_analyzer.py + POST /api/jobs/{id}/analyze.

Regressionsschutz: der Service schrieb auf Job.tags/gehalt_min/gehalt_max/
ist_remote/ist_hybrid/sprache - keine dieser Spalten existierte (Migration
0010 ergaenzt salary_min/salary_max/work_model/tags/skill_gap_*). Ausserdem
das ai_client-Problem wie bei den anderen Modulen, und unterschiedliche
JSON-Antwortschluessel je nach Sprache (jetzt immer englisch).
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


class TestAnalyzeJob:
    async def test_analyze_persists_extracted_fields(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH",
                   description="Python-Entwickler gesucht, Remote moeglich, 55000-70000 EUR.")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        raw = '{"must_haves": ["Python"], "nice_to_haves": [], "salary_min": 55000, "salary_max": 70000, "work_model": "remote", "tags": ["python", "backend"]}'
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(f"/api/jobs/{job.id}/analyze")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["salary_min"] == 55000
        assert body["salary_max"] == 70000
        assert body["work_model"] == "remote"
        assert body["tags"] == ["python", "backend"]

    async def test_analyze_without_description_returns_422(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        res = await client.post(f"/api/jobs/{job.id}/analyze")

        assert res.status_code == 422
