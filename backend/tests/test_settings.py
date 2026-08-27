"""
Tests fuer backend/routers/settings.py.

Bugfix-Sweep 2026-08-27: es gab bisher ueberhaupt keine Tests fuer
diesen Router - dadurch fiel eine selbst eingefuehrte Regression aus
der gleichen Session nicht auf: SettingsRead bekam ein neues
Pflichtfeld (weekly_goal, fuer WeeklyGoalWidget) und der Router baute
SettingsRead(...) an zwei Stellen manuell zusammen, ohne das Feld zu
uebergeben - GET /api/settings/ crashte mit einem Pydantic-
ValidationError, live auf der echten Instanz verifiziert und sofort
gefixt.
"""
from __future__ import annotations

import httpx
import pytest

pytestmark = pytest.mark.asyncio


class TestGetSettings:
    async def test_returns_all_fields_including_weekly_goal(self, client: httpx.AsyncClient):
        res = await client.get("/api/settings/")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["weekly_goal"] == 5
        assert "theme" in body
        assert "has_adzuna_key" in body


class TestUpdateSettings:
    async def test_updates_weekly_goal(self, client: httpx.AsyncClient):
        res = await client.patch("/api/settings/", json={"weekly_goal": 8})

        assert res.status_code == 200, res.text
        assert res.json()["weekly_goal"] == 8

        # Persistiert - ein zweiter GET sieht denselben Wert
        res2 = await client.get("/api/settings/")
        assert res2.json()["weekly_goal"] == 8

    async def test_updates_simple_field(self, client: httpx.AsyncClient):
        res = await client.patch("/api/settings/", json={"theme": "light"})

        assert res.status_code == 200, res.text
        assert res.json()["theme"] == "light"

    async def test_encrypts_api_key_and_never_returns_plaintext(self, client: httpx.AsyncClient):
        res = await client.patch("/api/settings/", json={"adzuna_api_key": "secret-key-123"})

        assert res.status_code == 200, res.text
        assert res.json()["has_adzuna_key"] is True
        assert "secret-key-123" not in res.text
