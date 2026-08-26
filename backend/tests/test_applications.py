"""
Tests fuer backend/routers/applications.py (Backlog Phase B.6).

Regressionsschutz fuer einen kritischen, beim manuellen Testen gefundenen
Bug: list_applications/get_application griffen auf job.location zu - ein
Feld, das auf dem Job-Modell nie existierte (dort heisst es city). Jeder
Aufruf von GET /api/applications/ crashte mit 500, sobald eine Bewerbung
zu einem existierenden Job vorlag - das betrifft direkt das Kanban-Board,
den Kernbestandteil der App. Derselbe Copy-Paste-Bug steckte auch in
backend/services/auto_apply.py und backend/routers/export.py (dort per
manuellem End-to-End-Test verifiziert, siehe BACKLOG.md Phase B.6).
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


async def _create_job_and_application(client: httpx.AsyncClient, db: AsyncSession) -> tuple[int, int]:
    job = Job(title="Backend Engineer", company="Beispiel GmbH", city="Bremen")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    res = await client.post("/api/applications/", json={"job_id": job.id})
    assert res.status_code == 200, res.text
    return job.id, res.json()["id"]


class TestListAndGet:
    async def test_list_applications_does_not_crash_with_existing_job(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Regression: 500 durch job.location (existiert nicht, korrekt: job.city)."""
        job_id, _ = await _create_job_and_application(client, db)

        res = await client.get("/api/applications/")

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) == 1
        assert body[0]["job"] == {"title": "Backend Engineer", "company": "Beispiel GmbH", "city": "Bremen"}

    async def test_get_application_does_not_crash_with_existing_job(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job_id, app_id = await _create_job_and_application(client, db)

        res = await client.get(f"/api/applications/{app_id}")

        assert res.status_code == 200, res.text
        assert res.json()["job"]["city"] == "Bremen"

    async def test_list_applications_handles_job_without_city(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Remote Job", company="Remote GmbH", city=None)
        db.add(job)
        await db.commit()
        await db.refresh(job)
        await client.post("/api/applications/", json={"job_id": job.id})

        res = await client.get("/api/applications/")

        assert res.status_code == 200, res.text
        assert res.json()[0]["job"]["city"] is None


class TestCreateAndUpdate:
    async def test_create_application(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Job", company="Firma")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        res = await client.post("/api/applications/", json={"job_id": job.id, "status": "interessant"})

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["job_id"] == job.id
        assert body["status"] == "interessant"
        assert "job" not in body  # ApplicationBase, keine Job-Relation im create-Response

    async def test_update_application_status(self, client: httpx.AsyncClient, db: AsyncSession):
        _, app_id = await _create_job_and_application(client, db)

        res = await client.patch(f"/api/applications/{app_id}", json={"status": "beworben"})

        assert res.status_code == 200, res.text
        assert res.json()["status"] == "beworben"

    async def test_get_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/applications/999999")
        assert res.status_code == 404
