"""
Tests fuer backend/services/duplicate_detection.py + GET /api/jobs/{id}/duplicates.

Regressionsschutz: der Service griff auf job.titel/firma/ort/erstellt_am
zu (existieren auf dem Job-Modell nicht, korrekt: title/company/city/
created_at) und filterte zusaetzlich auf other.status, ein Feld, das auf
Job ueberhaupt nicht existiert (Status lebt auf Application, nicht Job) -
jeder Aufruf crashte mit AttributeError. Siehe BACKLOG.md.
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


class TestDuplicateDetection:
    async def test_finds_similar_job(self, client: httpx.AsyncClient, db: AsyncSession):
        job1 = Job(title="Backend Entwickler (m/w/d)", company="Beispiel GmbH", city="Bremen")
        job2 = Job(title="Backend-Entwickler mwd", company="Beispiel GmbH", city="Bremen")
        job3 = Job(title="Koch", company="Restaurant XY", city="Hamburg")
        db.add_all([job1, job2, job3])
        await db.commit()
        for j in (job1, job2, job3):
            await db.refresh(j)

        res = await client.get(f"/api/jobs/{job1.id}/duplicates")

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) == 1
        assert body[0]["id"] == job2.id
        assert body[0]["similarity_score"] >= 0.75

    async def test_no_duplicates_returns_empty_list(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Einzigartige Stelle", company="Solo GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        res = await client.get(f"/api/jobs/{job.id}/duplicates")

        assert res.status_code == 200
        assert res.json() == []

    async def test_nonexistent_job_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/jobs/999999/duplicates")
        assert res.status_code == 404
