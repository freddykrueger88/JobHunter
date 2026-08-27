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
        assert "has_francetravail_key" in body
        assert "has_webhook_url" in body


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

    async def test_encrypts_francetravail_credentials(self, client: httpx.AsyncClient):
        res = await client.patch("/api/settings/", json={
            "francetravail_client_id": "ft-client-id-xyz",
            "francetravail_client_secret": "ft-secret-abc",
        })

        assert res.status_code == 200, res.text
        assert res.json()["has_francetravail_key"] is True
        assert "ft-client-id-xyz" not in res.text
        assert "ft-secret-abc" not in res.text

        res2 = await client.get("/api/settings/")
        assert res2.json()["has_francetravail_key"] is True

    async def test_encrypts_webhook_url_and_saves_type_and_toggles(self, client: httpx.AsyncClient):
        res = await client.patch("/api/settings/", json={
            "webhook_url": "https://hooks.slack.com/services/super-secret",
            "webhook_type": "slack",
            "webhook_notify_new_jobs": True,
            "webhook_notify_status_change": True,
        })

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["has_webhook_url"] is True
        assert body["webhook_type"] == "slack"
        assert body["webhook_notify_new_jobs"] is True
        assert body["webhook_notify_status_change"] is True
        assert "super-secret" not in res.text

        res2 = await client.get("/api/settings/")
        assert res2.json()["has_webhook_url"] is True
