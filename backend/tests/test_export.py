"""
Tests fuer backend/routers/export.py (Backlog Phase B.6 - Nebenbefund).

Regressionsschutz fuer denselben job.location-Bug wie in
test_applications.py: CSV- und XLSX-Export crashten mit 500, sobald eine
Bewerbung zu einem existierenden Job exportiert wurde.
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


async def _create_job_and_application(client: httpx.AsyncClient, db: AsyncSession) -> None:
    job = Job(title="Backend Engineer", company="Beispiel GmbH", city="Bremen")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    res = await client.post("/api/applications/", json={"job_id": job.id})
    assert res.status_code == 200, res.text


class TestExportDoesNotCrash:
    async def test_csv_export_with_existing_job(self, client: httpx.AsyncClient, db: AsyncSession):
        await _create_job_and_application(client, db)

        res = await client.get("/api/export/csv")

        assert res.status_code == 200, res.text
        assert "Bremen" in res.text

    async def test_xlsx_export_with_existing_job(self, client: httpx.AsyncClient, db: AsyncSession):
        await _create_job_and_application(client, db)

        res = await client.get("/api/export/xlsx")

        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert len(res.content) > 0
