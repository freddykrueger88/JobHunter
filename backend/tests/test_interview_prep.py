"""
Tests fuer backend/services/interview_prep.py + POST /api/interview/prep/{job_id}.

Regressionsschutz: der Service nahm application_id + persistierte
Job/Application-Felder (job.titel/beschreibung, urspruenglich sogar
application-zentriert) an - jetzt konsistent mit dem bereits bestehenden
Uebungsmodus (/api/interview/questions/{job_id}) auf job_id umgestellt,
korrekte Feldnamen (title/description), ai_client-Fix wie bei den
anderen Modulen.
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


class TestInterviewPrep:
    async def test_generates_prep_questions(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH",
                   description="Python-Entwickler mit FastAPI-Kenntnissen gesucht.")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        raw = '{"technical": [{"question": "Was ist FastAPI?", "sample_answer": "Ein Python-Webframework."}], "personal": [], "salary": []}'
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(f"/api/interview/prep/{job.id}")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["technical"][0]["question"] == "Was ist FastAPI?"

    async def test_nonexistent_job_returns_404(self, client: httpx.AsyncClient):
        res = await client.post("/api/interview/prep/999999")
        assert res.status_code == 404
