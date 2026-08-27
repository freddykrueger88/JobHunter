"""
Tests fuer backend/routers/blocklist.py (#84, G.3.2 - Firmen-Blacklist).

Der Router (CRUD + is_blocked()-Hilfsfunktion) existierte bereits vor
dieser Session, war aber nirgends tatsaechlich wirksam: is_blocked()
wurde nie aufgerufen, es gab keine Frontend-Seite, und blockierte
Firmen tauchten trotzdem ganz normal in der Stellenliste auf. Diese
Tests decken sowohl die (schon vorhandene) CRUD-Basis als auch die neu
hinzugekommenen Teile ab: Bulk-Import mit Duplikat-Erkennung und die
tatsaechliche Filterwirkung in GET /api/jobs/ und GET /api/jobs/search.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.blocklist import Blocklist
from backend.models.job import Job
from backend.services.job_search.base import RawJob

pytestmark = pytest.mark.asyncio


class TestCrud:
    async def test_create_and_list(self, client: httpx.AsyncClient):
        res = await client.post("/api/blocklist/", json={"firma": "Acme GmbH", "grund": "Ghosting"})
        assert res.status_code == 201, res.text
        assert res.json()["firma"] == "Acme GmbH"

        res2 = await client.get("/api/blocklist/")
        assert len(res2.json()) == 1

    async def test_delete(self, client: httpx.AsyncClient):
        created = await client.post("/api/blocklist/", json={"firma": "Acme GmbH"})
        entry_id = created.json()["id"]

        res = await client.delete(f"/api/blocklist/{entry_id}")
        assert res.status_code == 204

        res2 = await client.get("/api/blocklist/")
        assert res2.json() == []

    async def test_delete_nonexistent_returns_404(self, client: httpx.AsyncClient):
        res = await client.delete("/api/blocklist/999")
        assert res.status_code == 404


class TestImport:
    async def test_imports_new_entries(self, client: httpx.AsyncClient):
        res = await client.post("/api/blocklist/import", json=[
            {"firma": "Firma A", "grund": "x"},
            {"firma": "Firma B"},
        ])

        assert res.status_code == 200, res.text
        assert res.json() == {"imported": 2, "skipped": 0}

    async def test_skips_case_insensitive_duplicates(self, client: httpx.AsyncClient):
        await client.post("/api/blocklist/", json={"firma": "Acme GmbH"})

        res = await client.post("/api/blocklist/import", json=[
            {"firma": "acme gmbh"},  # gleiche Firma, andere Schreibweise
            {"firma": "Neue Firma"},
        ])

        assert res.json() == {"imported": 1, "skipped": 1}

    async def test_skips_duplicates_within_same_import_batch(self, client: httpx.AsyncClient):
        res = await client.post("/api/blocklist/import", json=[
            {"firma": "Doppelt AG"},
            {"firma": "Doppelt AG"},
        ])

        assert res.json() == {"imported": 1, "skipped": 1}


class TestJobListFiltering:
    async def test_blocked_company_excluded_from_list(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(Job(title="Job A", company="Blockierte Firma GmbH"))
        db.add(Job(title="Job B", company="Andere Firma AG"))
        db.add(Blocklist(firma="Blockierte Firma"))
        await db.commit()

        res = await client.get("/api/jobs/")

        titles = [j["title"] for j in res.json()]
        assert titles == ["Job B"]

    async def test_no_blocklist_entries_returns_all(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(Job(title="Job A", company="Firma X"))
        await db.commit()

        res = await client.get("/api/jobs/")

        assert len(res.json()) == 1


class TestSearchEndpointSkipsSaving:
    async def test_does_not_persist_jobs_from_blocked_companies(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(Blocklist(firma="Blockierte Firma"))
        await db.commit()

        raw_jobs = [
            RawJob(title="Job A", company="Blockierte Firma GmbH", source_portal="test", external_id="1"),
            RawJob(title="Job B", company="Andere Firma AG", source_portal="test", external_id="2"),
        ]
        with patch("backend.routers.jobs.search_all_sources", new=AsyncMock(return_value=raw_jobs)):
            res = await client.get("/api/jobs/search", params={
                "keywords": "x", "location": "Bremen", "save": True,
            })

        assert res.status_code == 200, res.text

        saved = await client.get("/api/jobs/")
        titles = [j["title"] for j in saved.json()]
        assert titles == ["Job B"]
