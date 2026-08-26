"""
Tests fuer backend/api/search_profiles.py.

Regressionsschutz: der Router und das SearchProfile-Modell existierten
bereits, aber keine Alembic-Migration legte die search_profiles-Tabelle
jemals an - in der echten (Postgres-)Datenbank crashte jeder Aufruf mit
"relation search_profiles does not exist" (siehe Migration 0009). Der
hiesige SQLite-Test-DB-Aufbau (Base.metadata.create_all) haette diesen
konkreten Fehler nie aufgedeckt, da er direkt aus den ORM-Modellen erzeugt
wird statt aus der Alembic-Kette - deshalb wurde der Live-Bug zusaetzlich
per echtem End-to-End-Test gegen die laufende Postgres-Instanz verifiziert
(siehe BACKLOG.md). Diese Tests decken die Endpunkt-Logik selbst ab.
"""
from __future__ import annotations

import httpx
import pytest

pytestmark = pytest.mark.asyncio


class TestSearchProfilesCrud:
    async def test_create_and_list(self, client: httpx.AsyncClient):
        res = await client.post("/api/search-profiles/", json={
            "name": "IT-Support Bremen",
            "keywords": "IT-Support",
            "location": "Bremen",
            "radius_km": 25,
            "schedule": "daily",
        })
        assert res.status_code == 201, res.text
        created = res.json()
        assert created["name"] == "IT-Support Bremen"
        assert created["is_active"] is True

        res = await client.get("/api/search-profiles/")
        assert res.status_code == 200
        assert len(res.json()) == 1

    async def test_toggle(self, client: httpx.AsyncClient):
        create_res = await client.post("/api/search-profiles/", json={
            "name": "Test", "keywords": "Test", "location": "Bremen",
        })
        pid = create_res.json()["id"]

        res = await client.patch(f"/api/search-profiles/{pid}/toggle")

        assert res.status_code == 200, res.text
        assert res.json()["is_active"] is False

    async def test_delete(self, client: httpx.AsyncClient):
        create_res = await client.post("/api/search-profiles/", json={
            "name": "Test", "keywords": "Test", "location": "Bremen",
        })
        pid = create_res.json()["id"]

        res = await client.delete(f"/api/search-profiles/{pid}")

        assert res.status_code == 204
        list_res = await client.get("/api/search-profiles/")
        assert list_res.json() == []

    async def test_toggle_nonexistent_returns_404(self, client: httpx.AsyncClient):
        res = await client.patch("/api/search-profiles/999999/toggle")
        assert res.status_code == 404
