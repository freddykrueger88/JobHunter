"""
Tests fuer backend/routers/diary.py + backend/services/diary_pdf.py
(#80, G.3.6 - Bewerbungs-Tagebuch).
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import DiaryEntry

pytestmark = pytest.mark.asyncio


class TestCrud:
    async def test_create_and_list(self, client: httpx.AsyncClient):
        res = await client.post("/api/diary/", json={"content": "Heute drei Bewerbungen geschrieben."})
        assert res.status_code == 201, res.text
        assert res.json()["content"] == "Heute drei Bewerbungen geschrieben."

        res2 = await client.get("/api/diary/")
        assert len(res2.json()) == 1

    async def test_list_orders_newest_first(self, client: httpx.AsyncClient):
        await client.post("/api/diary/", json={"content": "Erster Eintrag"})
        await client.post("/api/diary/", json={"content": "Zweiter Eintrag"})

        res = await client.get("/api/diary/")

        contents = [e["content"] for e in res.json()]
        assert contents == ["Zweiter Eintrag", "Erster Eintrag"]

    async def test_update(self, client: httpx.AsyncClient):
        created = await client.post("/api/diary/", json={"content": "Alter Text"})
        entry_id = created.json()["id"]

        res = await client.patch(f"/api/diary/{entry_id}", json={"content": "Neuer Text"})

        assert res.status_code == 200, res.text
        assert res.json()["content"] == "Neuer Text"

    async def test_update_nonexistent_returns_404(self, client: httpx.AsyncClient):
        res = await client.patch("/api/diary/999", json={"content": "x"})
        assert res.status_code == 404

    async def test_delete(self, client: httpx.AsyncClient):
        created = await client.post("/api/diary/", json={"content": "Zu löschen"})
        entry_id = created.json()["id"]

        res = await client.delete(f"/api/diary/{entry_id}")
        assert res.status_code == 204

        res2 = await client.get("/api/diary/")
        assert res2.json() == []

    async def test_delete_nonexistent_returns_404(self, client: httpx.AsyncClient):
        res = await client.delete("/api/diary/999")
        assert res.status_code == 404


class TestSearch:
    async def test_search_filters_by_content_substring(self, client: httpx.AsyncClient):
        await client.post("/api/diary/", json={"content": "Absage von Acme GmbH bekommen, frustrierend."})
        await client.post("/api/diary/", json={"content": "Gutes Gespräch mit einem Recruiter gehabt."})

        res = await client.get("/api/diary/", params={"search": "Absage"})

        entries = res.json()
        assert len(entries) == 1
        assert "Acme" in entries[0]["content"]

    async def test_search_is_case_insensitive(self, client: httpx.AsyncClient):
        await client.post("/api/diary/", json={"content": "Frustrierender Tag heute."})

        res = await client.get("/api/diary/", params={"search": "FRUSTRIERENDER"})

        assert len(res.json()) == 1

    async def test_no_search_returns_all(self, client: httpx.AsyncClient):
        await client.post("/api/diary/", json={"content": "A"})
        await client.post("/api/diary/", json={"content": "B"})

        res = await client.get("/api/diary/")

        assert len(res.json()) == 2


class TestPdfExport:
    async def test_returns_pdf_content_type(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(DiaryEntry(content="Ein Testeintrag für den PDF-Export."))
        await db.commit()

        res = await client.get("/api/diary/pdf")

        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF")

    async def test_pdf_export_works_with_no_entries(self, client: httpx.AsyncClient):
        res = await client.get("/api/diary/pdf")

        assert res.status_code == 200, res.text
        assert res.content.startswith(b"%PDF")

    async def test_pdf_export_respects_search_filter(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(DiaryEntry(content="Absage bekommen."))
        db.add(DiaryEntry(content="Gutes Gespräch gehabt."))
        await db.commit()

        res = await client.get("/api/diary/pdf", params={"search": "Absage"})

        assert res.status_code == 200, res.text
        assert res.content.startswith(b"%PDF")
