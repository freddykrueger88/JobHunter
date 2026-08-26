"""
Tests fuer backend/services/skill_gap.py + POST /api/jobs/{id}/skill-gap.

Regressionsschutz: der Service schrieb auf Job.skill_gap_score/
skill_gap_json (existierten nicht, Migration 0010 ergaenzt sie) und
importierte das nie existierende ai_client-Modul.
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


class TestSkillGap:
    async def test_skill_gap_without_cv_returns_400(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python gesucht")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        res = await client.post(f"/api/jobs/{job.id}/skill-gap")

        assert res.status_code == 400

    async def test_skill_gap_with_cv_persists_score(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Python + FastAPI gesucht")
        db.add(job)
        db.add(CVData(filename="cv.pdf", full_name="Max Mustermann", raw_text="Python-Entwickler, 3 Jahre Erfahrung"))
        await db.commit()
        await db.refresh(job)

        raw = '{"match_score": 78, "existing_skills": ["Python"], "missing_skills": ["FastAPI"], "learning_recommendations": ["FastAPI-Kurs"]}'
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(f"/api/jobs/{job.id}/skill-gap")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["match_score"] == 78

        await db.refresh(job)
        assert job.skill_gap_score == 78
