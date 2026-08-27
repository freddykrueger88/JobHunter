"""Tests fuer GET /api/cover-letter-templates/defaults.

Bugfix-Sweep 2026-08-27: default_templates.py (vorgefertigte Anschreiben-
Vorlagen nach Branche) existierte fertig, wurde aber nirgends
exponiert. Jetzt als Startpunkt-Bibliothek im Vorlage-Feld der KI-
Anschreiben-Generierung (CoverLetter.tsx) nutzbar.
"""
from __future__ import annotations

import httpx
import pytest

pytestmark = pytest.mark.asyncio


class TestDefaultTemplates:
    async def test_returns_templates_with_placeholders(self, client: httpx.AsyncClient):
        res = await client.get("/api/cover-letter-templates/defaults")

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) >= 5
        assert all({"name", "category", "sprache", "body"} <= set(t.keys()) for t in body)
        assert any("{stelle}" in t["body"] for t in body)
